"""Tests for ``core.resilience`` — backoff and per-target Circuit Breaker.

These tests live close to the unit and never sleep with the real wall clock:
we inject ``clock`` and ``sleep`` so the ladder, trip, cooldown, and
half-open transitions are exercised deterministically.
"""

from __future__ import annotations

import os
import random
from typing import Any
from unittest import mock

import pytest

from core.resilience import (
    CircuitBreaker,
    CircuitBreakerConfig,
    CircuitOpenError,
    CircuitState,
    DEFAULT_RETRY_LADDER_SECONDS,
    all_circuit_telemetry,
    compute_backoff_delay,
    get_circuit_breaker,
    is_transient_error,
    load_breaker_config_from_target,
    reset_all_breakers,
)


# ---------------------------------------------------------------------------
# Backoff ladder
# ---------------------------------------------------------------------------


def test_backoff_ladder_no_jitter_returns_canonical_1_4_10() -> None:
    """Without jitter, the ladder must be 1s -> 4s -> 10s — the agreed contract."""
    no_jitter = [compute_backoff_delay(a, jitter=False) for a in (1, 2, 3)]
    assert no_jitter == list(DEFAULT_RETRY_LADDER_SECONDS)


def test_backoff_attempt_zero_or_negative_is_zero() -> None:
    assert compute_backoff_delay(0, jitter=False) == 0.0
    assert compute_backoff_delay(-3, jitter=False) == 0.0


def test_backoff_clamped_to_max_seconds() -> None:
    """Past the ladder, exponential growth is clamped."""
    # No ladder -> 1 * 2 ** (5-1) = 16, capped to 10.
    assert (
        compute_backoff_delay(
            5, jitter=False, ladder_seconds=None, max_seconds=10.0, base_seconds=1.0
        )
        == 10.0
    )


def test_backoff_full_jitter_within_target_window() -> None:
    """With full jitter, every sample stays inside [0, target]."""
    rng = random.Random(1234)
    for attempt, target in enumerate(DEFAULT_RETRY_LADDER_SECONDS, start=1):
        for _ in range(50):
            sample = compute_backoff_delay(attempt, jitter=True, rng=rng)
            assert 0.0 <= sample <= target


# ---------------------------------------------------------------------------
# Circuit breaker — happy path
# ---------------------------------------------------------------------------


class _FakeClock:
    """Monotonic-style clock the tests can advance manually."""

    def __init__(self) -> None:
        self.t = 0.0

    def now(self) -> float:
        return self.t

    def advance(self, seconds: float) -> None:
        self.t += seconds


@pytest.fixture
def fake_clock() -> _FakeClock:
    return _FakeClock()


@pytest.fixture(autouse=True)
def _reset_breaker_registry() -> None:
    """Each test gets a clean global registry."""
    reset_all_breakers()
    yield
    reset_all_breakers()


def test_breaker_passes_through_when_func_succeeds(fake_clock: _FakeClock) -> None:
    breaker = CircuitBreaker(
        "ok", config=CircuitBreakerConfig(retry_attempts=1), clock=fake_clock.now
    )
    assert breaker.call(lambda: "value") == "value"
    assert breaker.state is CircuitState.CLOSED
    tel = breaker.telemetry()
    assert tel.total_successes == 1
    assert tel.total_failures == 0


def test_breaker_retries_then_succeeds_on_third_call(fake_clock: _FakeClock) -> None:
    """1st + 2nd call raise transient errors; the 3rd succeeds without tripping."""
    sleeps: list[float] = []
    breaker = CircuitBreaker(
        "flaky",
        config=CircuitBreakerConfig(
            retry_attempts=3,
            failure_threshold=3,
            jitter=False,
            retry_ladder_seconds=(0.1, 0.2, 0.3),
        ),
        clock=fake_clock.now,
        sleep=sleeps.append,
    )
    calls = {"n": 0}

    def func() -> str:
        calls["n"] += 1
        if calls["n"] < 3:
            raise TimeoutError("transient")
        return "ok"

    assert breaker.call(func) == "ok"
    assert calls["n"] == 3
    # Two delays consumed (between attempt 1->2 and 2->3).
    assert sleeps == [0.1, 0.2]
    assert breaker.state is CircuitState.CLOSED
    # Successful call after retries resets consecutive_failures.
    assert breaker.telemetry().consecutive_failures == 0


# ---------------------------------------------------------------------------
# Circuit breaker — trip + cooldown + half-open
# ---------------------------------------------------------------------------


def test_breaker_trips_after_threshold(fake_clock: _FakeClock) -> None:
    """3 consecutive transient failures → state OPEN, last exception re-raised."""
    breaker = CircuitBreaker(
        "trip",
        config=CircuitBreakerConfig(
            retry_attempts=3,
            failure_threshold=3,
            cooldown_seconds=900.0,
            jitter=False,
            retry_ladder_seconds=(0.0, 0.0, 0.0),
        ),
        clock=fake_clock.now,
        sleep=lambda s: None,
    )

    def boom() -> Any:
        raise TimeoutError("network unreachable")

    with pytest.raises(TimeoutError):
        breaker.call(boom)

    assert breaker.state is CircuitState.OPEN
    tel = breaker.telemetry()
    assert tel.consecutive_failures >= 3
    assert tel.retry_after_seconds == pytest.approx(900.0, abs=1.0)


def test_breaker_short_circuits_while_open(fake_clock: _FakeClock) -> None:
    """While OPEN and within cooldown, calls fail fast with CircuitOpenError."""
    breaker = CircuitBreaker(
        "shortcut",
        config=CircuitBreakerConfig(
            retry_attempts=3,
            failure_threshold=3,
            cooldown_seconds=900.0,
            jitter=False,
            retry_ladder_seconds=(0.0, 0.0, 0.0),
        ),
        clock=fake_clock.now,
        sleep=lambda s: None,
    )

    def boom() -> Any:
        raise ConnectionError("drop")

    with pytest.raises(ConnectionError):
        breaker.call(boom)

    # Now any call should short-circuit without invoking the underlying func.
    invoked = {"n": 0}

    def should_not_run() -> Any:
        invoked["n"] += 1
        return "should-not-happen"

    with pytest.raises(CircuitOpenError) as ei:
        breaker.call(should_not_run)
    assert invoked["n"] == 0
    assert ei.value.breaker_name == "shortcut"
    assert ei.value.retry_after_seconds > 0.0
    assert breaker.telemetry().total_short_circuits >= 1


def test_breaker_half_open_allows_one_probe_then_closes_on_success(
    fake_clock: _FakeClock,
) -> None:
    breaker = CircuitBreaker(
        "halfopen",
        config=CircuitBreakerConfig(
            retry_attempts=3,
            failure_threshold=3,
            cooldown_seconds=60.0,
            jitter=False,
            retry_ladder_seconds=(0.0, 0.0, 0.0),
        ),
        clock=fake_clock.now,
        sleep=lambda s: None,
    )

    with pytest.raises(TimeoutError):
        breaker.call(lambda: (_ for _ in ()).throw(TimeoutError("x")))
    assert breaker.state is CircuitState.OPEN

    # Cooldown elapsed -> next read transitions to HALF_OPEN automatically.
    fake_clock.advance(60.5)
    assert breaker.state is CircuitState.HALF_OPEN

    # Successful probe closes the circuit.
    assert breaker.call(lambda: "ok") == "ok"
    assert breaker.state is CircuitState.CLOSED


def test_breaker_half_open_failure_reopens_circuit(fake_clock: _FakeClock) -> None:
    breaker = CircuitBreaker(
        "halfopen-fail",
        config=CircuitBreakerConfig(
            retry_attempts=1,
            failure_threshold=3,
            cooldown_seconds=30.0,
            jitter=False,
            retry_ladder_seconds=(0.0,),
        ),
        clock=fake_clock.now,
        sleep=lambda s: None,
    )
    breaker.force_open()
    fake_clock.advance(31.0)
    assert breaker.state is CircuitState.HALF_OPEN

    with pytest.raises(TimeoutError):
        breaker.call(lambda: (_ for _ in ()).throw(TimeoutError("again")))
    # A single failure in HALF_OPEN re-opens the circuit immediately.
    assert breaker.state is CircuitState.OPEN


# ---------------------------------------------------------------------------
# Transient classification
# ---------------------------------------------------------------------------


def test_non_transient_errors_bubble_up_without_counting(
    fake_clock: _FakeClock,
) -> None:
    breaker = CircuitBreaker(
        "non-transient",
        config=CircuitBreakerConfig(retry_attempts=3, failure_threshold=3),
        clock=fake_clock.now,
        sleep=lambda s: None,
    )
    with pytest.raises(ValueError):
        breaker.call(lambda: (_ for _ in ()).throw(ValueError("bug")))
    # Non-transient errors must NOT count against the breaker.
    assert breaker.state is CircuitState.CLOSED
    assert breaker.telemetry().total_failures == 0


def test_is_transient_error_identifies_drivers_by_name() -> None:
    class FakeOperationalError(Exception):
        pass

    class FakeServerSelectionTimeoutError(Exception):
        pass

    assert is_transient_error(FakeOperationalError("db down")) is True
    assert is_transient_error(FakeServerSelectionTimeoutError("mongo gone")) is True
    assert is_transient_error(TimeoutError()) is True
    assert is_transient_error(ConnectionError("reset")) is True
    assert is_transient_error(ValueError("bad arg")) is False
    assert is_transient_error(KeyError("missing")) is False


# ---------------------------------------------------------------------------
# Config loading
# ---------------------------------------------------------------------------


def test_load_breaker_config_from_yaml_overrides() -> None:
    cfg = load_breaker_config_from_target(
        {
            "name": "snow",
            "circuit_breaker": {
                "failure_threshold": 5,
                "cooldown_seconds": 120,
                "retry_attempts": 4,
                "retry_max_seconds": 8,
                "jitter": False,
            },
        }
    )
    assert cfg.failure_threshold == 5
    assert cfg.cooldown_seconds == 120.0
    assert cfg.retry_attempts == 4
    assert cfg.retry_max_seconds == 8.0
    assert cfg.jitter is False


def test_load_breaker_config_env_overrides_yaml() -> None:
    yaml_block = {"circuit_breaker": {"failure_threshold": 3, "cooldown_seconds": 60}}
    env = {
        "DATA_BOAR_CIRCUIT_FAILURE_THRESHOLD": "7",
        "DATA_BOAR_CIRCUIT_COOLDOWN_SECONDS": "1800",
        "DATA_BOAR_RETRY_ATTEMPTS": "2",
        "DATA_BOAR_RETRY_MAX_SECONDS": "5",
    }
    with mock.patch.dict(os.environ, env, clear=False):
        cfg = load_breaker_config_from_target(yaml_block)
    assert cfg.failure_threshold == 7
    assert cfg.cooldown_seconds == 1800.0
    assert cfg.retry_attempts == 2
    assert cfg.retry_max_seconds == 5.0


def test_load_breaker_config_invalid_falls_back_to_defaults() -> None:
    cfg = load_breaker_config_from_target(
        {"circuit_breaker": {"failure_threshold": "abc", "cooldown_seconds": "nope"}}
    )
    # Defaults preserved (failure_threshold=3, cooldown=900 == 15 min).
    assert cfg.failure_threshold == 3
    assert cfg.cooldown_seconds == 15 * 60.0


# ---------------------------------------------------------------------------
# Registry
# ---------------------------------------------------------------------------


def test_get_circuit_breaker_returns_same_instance_per_name() -> None:
    a = get_circuit_breaker("target:warehouse_lgpd")
    b = get_circuit_breaker("target:warehouse_lgpd")
    assert a is b
    c = get_circuit_breaker("target:other")
    assert c is not a


def test_all_circuit_telemetry_returns_each_breaker_once() -> None:
    a = get_circuit_breaker("target:one")
    a.force_open()
    get_circuit_breaker("target:two")
    snap = all_circuit_telemetry()
    names = {t.name for t in snap}
    assert names == {"target:one", "target:two"}
    by_name = {t.name: t for t in snap}
    assert by_name["target:one"].state == CircuitState.OPEN.value
    assert by_name["target:two"].state == CircuitState.CLOSED.value
