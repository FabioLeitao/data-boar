"""
Resilience guardian for ``core.throttler.BoarThrottler``.

The throttler is a feedback controller that runs in **every** Pro scan loop
to keep customer DB latency bounded. Per the Defensive Scanning Manifesto
(``docs/ops/inspirations/DEFENSIVE_SCANNING_MANIFESTO.md`` §2 — relief
valves), the controller MUST behave deterministically under malformed
input rather than silently corrupting its moving-average window.

These tests are deterministic (no ``sleep``) and surgical: each one targets
a single silent zone the existing happy-path tests do not exercise.
"""

from __future__ import annotations

import logging

from core.throttler import BoarThrottler


def test_negative_latency_does_not_pollute_history() -> None:
    """A negative reading is ignored — must not enter the moving-average window."""
    t = BoarThrottler(target_latency_ms=200, max_workers=4, window_size=4)
    t.record_latency(-1.0)
    assert len(t.latency_history) == 0
    assert t.current_workers == 1


def test_negative_latency_does_not_advance_worker_count() -> None:
    """Hostile / clock-skew negatives must not be confused with 'fast' samples."""
    t = BoarThrottler(target_latency_ms=200, max_workers=4, window_size=4)
    for _ in range(10):
        t.record_latency(-0.05)
    assert t.current_workers == 1
    assert t.get_sleep_time() == 0.0


def test_zero_latency_is_a_valid_fast_sample() -> None:
    """Exactly ``0.0`` is permitted (cache hit / mocked driver) and must scale up."""
    t = BoarThrottler(target_latency_ms=200, max_workers=4, window_size=4)
    t.record_latency(0.0)
    t.record_latency(0.0)
    assert t.current_workers >= 2


def test_window_size_zero_is_floored_to_one() -> None:
    """A misconfigured ``window_size=0`` must not crash ``deque(maxlen=0)`` writes."""
    t = BoarThrottler(target_latency_ms=200, window_size=0)
    t.record_latency(0.05)
    t.record_latency(0.06)
    assert len(t.latency_history) == 1


def test_max_workers_one_never_scales_up() -> None:
    """Single-worker policy must remain single-worker no matter how fast."""
    t = BoarThrottler(target_latency_ms=200, max_workers=1, window_size=4)
    for _ in range(20):
        t.record_latency(0.001)
    assert t.current_workers == 1


def test_sustained_overload_halves_workers_repeatedly() -> None:
    """Manifesto §2: relief valve — high latency MUST trip the halving branch."""
    t = BoarThrottler(target_latency_ms=100, max_workers=16, window_size=2)
    t.current_workers = 16
    t.record_latency(1.0)
    t.record_latency(1.0)
    assert t.current_workers <= 8
    t.record_latency(1.0)
    assert t.current_workers <= 4


def test_get_sleep_time_with_empty_history_is_zero() -> None:
    """No samples seen yet → no cool-off."""
    t = BoarThrottler()
    assert t.get_sleep_time() == 0.0


def test_target_latency_zero_is_floored() -> None:
    """``target_latency_ms=0`` would divide-by-zero in the scaling math; must floor."""
    t = BoarThrottler(target_latency_ms=0, max_workers=4, window_size=4)
    t.record_latency(0.5)
    assert t.current_workers >= 1


def test_high_latency_emits_warning(caplog) -> None:
    """Operators rely on the WARNING line to spot a slow customer DB."""
    t = BoarThrottler(target_latency_ms=100, max_workers=8, window_size=2)
    t.current_workers = 8
    with caplog.at_level(logging.WARNING):
        t.record_latency(1.0)
        t.record_latency(1.0)
    assert any("BoarThrottler" in rec.message for rec in caplog.records)
