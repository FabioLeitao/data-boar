"""
Resilience primitives — exponential backoff with jitter + per-target Circuit Breaker.

Why this module exists
======================

Data Boar is a **guest** on customer databases (see
``docs/ops/inspirations/DEFENSIVE_SCANNING_MANIFESTO.md``). When a target DB
(Snowflake, Oracle, MSSQL, PostgreSQL, Mongo, …) becomes unresponsive, we
must **never**:

1. hammer it with tight retries (the host is already on fire),
2. block the whole scan because **one** target is a zombie,
3. swallow the failure silently (no audit row, no blast-radius signal).

This module provides two small, dependency-free building blocks that the
engine and connectors can wire in without rewriting their flow:

* :func:`compute_backoff_delay` — exponential backoff **with full jitter**
  (AWS Architecture Blog, Marc Brooker), clamped to a configurable ceiling.
  Default ladder for 3 attempts: ~1 s, ~4 s, ~10 s.

* :class:`CircuitBreaker` — per-target circuit breaker with the three
  canonical states (CLOSED → OPEN → HALF_OPEN). After ``failure_threshold``
  consecutive failures the breaker **trips**; subsequent calls short-circuit
  with :class:`CircuitOpenError` for ``cooldown_seconds`` (default **15 min**)
  before a single probe call is allowed (HALF_OPEN). One success closes the
  circuit; one more failure re-opens it.

The breaker is *per target* (e.g. one Snowflake DSN, one Oracle service
name). A faulty target is **skipped**, not the entire run — the engine logs
a structured ``circuit_open`` failure row, includes blast-radius metadata
(target name + failure count + cooldown), and continues with the others.

The fallback / observability posture follows
``docs/ops/inspirations/THE_ART_OF_THE_FALLBACK.md`` — every demotion
("retry → trip → skip") emits a diagnostic with a factual reason.
"""

from __future__ import annotations

import logging
import os
import random
import threading
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, TypeVar

T = TypeVar("T")

_logger = logging.getLogger("data_boar.resilience")


# ---------------------------------------------------------------------------
# Backoff
# ---------------------------------------------------------------------------

# Defaults — match the ladder agreed in the engineering mission:
#   1st fail (1 s), 2nd fail (4 s), 3rd fail (10 s), then trip the circuit.
DEFAULT_RETRY_BASE_SECONDS: float = 1.0
DEFAULT_RETRY_MAX_SECONDS: float = 10.0
DEFAULT_RETRY_ATTEMPTS: int = 3
DEFAULT_RETRY_LADDER_SECONDS: tuple[float, ...] = (1.0, 4.0, 10.0)


def compute_backoff_delay(
    attempt: int,
    *,
    base_seconds: float = DEFAULT_RETRY_BASE_SECONDS,
    max_seconds: float = DEFAULT_RETRY_MAX_SECONDS,
    jitter: bool = True,
    rng: random.Random | None = None,
    ladder_seconds: tuple[float, ...] | None = DEFAULT_RETRY_LADDER_SECONDS,
) -> float:
    """Return the sleep delay (seconds) before the **next** retry.

    ``attempt`` is 1-based: ``attempt=1`` is the delay after the *first* failure.

    With ``ladder_seconds`` (the default), the deterministic targets are
    ``1 s → 4 s → 10 s``; for ``attempt`` past the ladder length we fall back
    to ``base * 2 ** (attempt - 1)`` clamped to ``max_seconds``.

    With ``jitter=True`` (default) we apply **full jitter** —
    ``random.uniform(0, target)`` — which spreads thundering-herd retries
    coming from many workers without ever exceeding the deterministic cap.
    """
    if attempt < 1:
        return 0.0
    if ladder_seconds and attempt <= len(ladder_seconds):
        target = float(ladder_seconds[attempt - 1])
    else:
        # Classic exponential: 1, 2, 4, 8, … * base.
        target = float(base_seconds) * (2 ** (attempt - 1))
    target = max(0.0, min(target, float(max_seconds)))
    if not jitter or target <= 0.0:
        return target
    r = rng if rng is not None else random
    return r.uniform(0.0, target)


# ---------------------------------------------------------------------------
# Circuit breaker
# ---------------------------------------------------------------------------


class CircuitState(str, Enum):
    """Canonical breaker states.

    * ``CLOSED`` — normal traffic; failures are counted.
    * ``OPEN`` — short-circuiting; calls fail fast with :class:`CircuitOpenError`
      until ``cooldown_seconds`` elapsed.
    * ``HALF_OPEN`` — exactly one probe call is allowed through. Success closes
      the circuit; failure re-opens it for another cooldown window.
    """

    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"


class CircuitOpenError(RuntimeError):
    """Raised when a call is short-circuited because the breaker is open.

    Carries the breaker name and the seconds left until a HALF_OPEN probe is
    allowed; engine code uses these to write a structured failure row.
    """

    def __init__(
        self,
        breaker_name: str,
        retry_after_seconds: float,
        consecutive_failures: int,
    ) -> None:
        self.breaker_name = breaker_name
        self.retry_after_seconds = max(0.0, float(retry_after_seconds))
        self.consecutive_failures = int(consecutive_failures)
        super().__init__(
            f"Circuit '{breaker_name}' is OPEN "
            f"(retry_after={self.retry_after_seconds:.0f}s, "
            f"failures={self.consecutive_failures})"
        )


@dataclass
class CircuitBreakerConfig:
    """Per-target breaker tuning.

    Defaults match the engineering mission: 3 fails to trip, 15-minute cooldown,
    full-jitter backoff with the 1/4/10 ladder.
    """

    failure_threshold: int = 3
    cooldown_seconds: float = 15 * 60.0
    retry_attempts: int = DEFAULT_RETRY_ATTEMPTS
    retry_base_seconds: float = DEFAULT_RETRY_BASE_SECONDS
    retry_max_seconds: float = DEFAULT_RETRY_MAX_SECONDS
    retry_ladder_seconds: tuple[float, ...] | None = DEFAULT_RETRY_LADDER_SECONDS
    jitter: bool = True


@dataclass
class CircuitTelemetry:
    """Lightweight, JSON-serializable snapshot of breaker state.

    Used by the engine to record a structured ``save_failure`` row when a
    target is skipped and to feed the scan audit log.
    """

    name: str
    state: str
    consecutive_failures: int
    total_failures: int
    total_successes: int
    total_short_circuits: int
    last_failure_reason: str | None
    last_failure_class: str | None
    cooldown_seconds: float
    retry_after_seconds: float
    opened_at_epoch: float | None


class CircuitBreaker:
    """Simple, thread-safe circuit breaker with exponential backoff retries.

    Usage::

        breaker = CircuitBreaker("snowflake:warehouse_lgpd")
        breaker.call(lambda: connector.connect())

    On ``call``, the breaker:

    1. If OPEN and the cooldown has not elapsed, raises :class:`CircuitOpenError`
       (no I/O, no retry — this is the "skip the zombie" path).
    2. Otherwise runs ``func`` with up to ``retry_attempts`` retries using
       :func:`compute_backoff_delay`. Each retry logs a structured line so a
       reader can reconstruct the demotion ladder.
    3. On success → resets to CLOSED.
    4. On exhausted retries → trips the circuit (OPEN) and re-raises the last
       exception so the caller can record a ``save_failure`` row.

    The breaker only counts **transient** errors as failures. Caller-side
    bugs (``ValueError``, ``TypeError``, ``KeyError``) are re-raised
    immediately and do **not** trip the circuit — see
    :func:`is_transient_error`.
    """

    def __init__(
        self,
        name: str,
        config: CircuitBreakerConfig | None = None,
        *,
        clock: Callable[[], float] = time.monotonic,
        sleep: Callable[[float], None] = time.sleep,
        is_transient: Callable[[BaseException], bool] | None = None,
    ) -> None:
        self.name = name
        self.config = config or CircuitBreakerConfig()
        self._clock = clock
        self._sleep = sleep
        self._is_transient = is_transient or is_transient_error
        self._lock = threading.Lock()
        self._state: CircuitState = CircuitState.CLOSED
        self._consecutive_failures: int = 0
        self._opened_at: float | None = None
        self._last_failure_reason: str | None = None
        self._last_failure_class: str | None = None
        self._total_failures: int = 0
        self._total_successes: int = 0
        self._total_short_circuits: int = 0

    # ---- public introspection -------------------------------------------------

    @property
    def state(self) -> CircuitState:
        with self._lock:
            self._maybe_transition_to_half_open_locked()
            return self._state

    def telemetry(self) -> CircuitTelemetry:
        """Return a JSON-serializable snapshot for audit logs / API."""
        with self._lock:
            self._maybe_transition_to_half_open_locked()
            return CircuitTelemetry(
                name=self.name,
                state=self._state.value,
                consecutive_failures=self._consecutive_failures,
                total_failures=self._total_failures,
                total_successes=self._total_successes,
                total_short_circuits=self._total_short_circuits,
                last_failure_reason=self._last_failure_reason,
                last_failure_class=self._last_failure_class,
                cooldown_seconds=self.config.cooldown_seconds,
                retry_after_seconds=self._retry_after_seconds_locked(),
                opened_at_epoch=self._opened_at,
            )

    # ---- main API -------------------------------------------------------------

    def call(self, func: Callable[..., T], *args: Any, **kwargs: Any) -> T:
        """Run ``func`` under the breaker, with retry+backoff, returning its result.

        Raises :class:`CircuitOpenError` when the breaker is open and the
        cooldown is still active (no call is attempted).
        """
        self._raise_if_short_circuited()

        last_exc: BaseException | None = None
        attempts = max(1, int(self.config.retry_attempts))
        for attempt in range(1, attempts + 1):
            try:
                result = func(*args, **kwargs)
            except Exception as exc:
                if not self._is_transient(exc):
                    # Non-transient (e.g. programmer errors) bubble up untouched.
                    raise
                last_exc = exc
                # Every transient attempt counts toward the breaker — that is
                # the contract from the engineering mission ("after 3 fails,
                # trip the circuit"). The breaker may flip to OPEN mid-loop;
                # we still let the surrounding retry logic re-raise the last
                # exception so the caller sees the underlying error class.
                self._record_failure(exc)
                if attempt >= attempts:
                    break
                delay = compute_backoff_delay(
                    attempt,
                    base_seconds=self.config.retry_base_seconds,
                    max_seconds=self.config.retry_max_seconds,
                    jitter=self.config.jitter,
                    ladder_seconds=self.config.retry_ladder_seconds,
                )
                _logger.warning(
                    "[resilience] retry breaker=%s attempt=%d/%d "
                    "delay=%.2fs reason=%s err_class=%s",
                    self.name,
                    attempt,
                    attempts,
                    delay,
                    _short_reason(exc),
                    type(exc).__name__,
                )
                if delay > 0:
                    self._sleep(delay)
                continue
            else:
                self._record_success()
                return result

        # Exhausted: re-raise the last seen exception so callers can record it.
        assert last_exc is not None  # for type-checkers; loop guarantees this
        raise last_exc

    # ---- helpers --------------------------------------------------------------

    def _raise_if_short_circuited(self) -> None:
        with self._lock:
            self._maybe_transition_to_half_open_locked()
            if self._state is CircuitState.OPEN:
                self._total_short_circuits += 1
                retry_after = self._retry_after_seconds_locked()
                _logger.error(
                    "[resilience] short_circuit breaker=%s state=open "
                    "retry_after=%.0fs failures=%d last_reason=%s",
                    self.name,
                    retry_after,
                    self._consecutive_failures,
                    self._last_failure_reason,
                )
                raise CircuitOpenError(
                    breaker_name=self.name,
                    retry_after_seconds=retry_after,
                    consecutive_failures=self._consecutive_failures,
                )

    def _record_success(self) -> None:
        with self._lock:
            self._total_successes += 1
            self._consecutive_failures = 0
            if self._state is not CircuitState.CLOSED:
                _logger.info(
                    "[resilience] circuit_closed breaker=%s prev_state=%s",
                    self.name,
                    self._state.value,
                )
            self._state = CircuitState.CLOSED
            self._opened_at = None

    def _record_failure(self, exc: BaseException) -> None:
        with self._lock:
            self._total_failures += 1
            self._consecutive_failures += 1
            self._last_failure_reason = _short_reason(exc)
            self._last_failure_class = type(exc).__name__
            should_open = (
                self._state is CircuitState.HALF_OPEN
                or self._consecutive_failures >= self.config.failure_threshold
            )
            if should_open and self._state is not CircuitState.OPEN:
                self._state = CircuitState.OPEN
                self._opened_at = self._clock()
                _logger.error(
                    "[resilience] circuit_tripped breaker=%s "
                    "failures=%d threshold=%d cooldown_s=%.0f "
                    "last_reason=%s err_class=%s",
                    self.name,
                    self._consecutive_failures,
                    self.config.failure_threshold,
                    self.config.cooldown_seconds,
                    self._last_failure_reason,
                    self._last_failure_class,
                )

    def _maybe_transition_to_half_open_locked(self) -> None:
        if self._state is not CircuitState.OPEN:
            return
        if self._opened_at is None:
            return
        elapsed = self._clock() - self._opened_at
        if elapsed >= self.config.cooldown_seconds:
            _logger.info(
                "[resilience] circuit_half_open breaker=%s elapsed=%.0fs",
                self.name,
                elapsed,
            )
            self._state = CircuitState.HALF_OPEN

    def _retry_after_seconds_locked(self) -> float:
        if self._state is not CircuitState.OPEN or self._opened_at is None:
            return 0.0
        remaining = self.config.cooldown_seconds - (self._clock() - self._opened_at)
        return max(0.0, remaining)

    # Test hooks -------------------------------------------------------------

    def force_open(self) -> None:
        """Manually trip the breaker (test / operator override)."""
        with self._lock:
            self._state = CircuitState.OPEN
            self._opened_at = self._clock()
            self._consecutive_failures = max(
                self._consecutive_failures, self.config.failure_threshold
            )

    def reset(self) -> None:
        """Manually close the breaker (test / operator override)."""
        with self._lock:
            self._state = CircuitState.CLOSED
            self._consecutive_failures = 0
            self._opened_at = None
            self._last_failure_reason = None
            self._last_failure_class = None


# ---------------------------------------------------------------------------
# Registry
# ---------------------------------------------------------------------------


@dataclass
class _Registry:
    breakers: dict[str, CircuitBreaker] = field(default_factory=dict)
    lock: threading.Lock = field(default_factory=threading.Lock)


_REGISTRY = _Registry()


def get_circuit_breaker(
    name: str, config: CircuitBreakerConfig | None = None
) -> CircuitBreaker:
    """Return (or create) the per-target breaker keyed by ``name``.

    Targets are identified by a stable label — typically the YAML ``name`` —
    so the breaker survives across one scan run and is shared between the
    connector and engine telemetry.
    """
    with _REGISTRY.lock:
        existing = _REGISTRY.breakers.get(name)
        if existing is not None:
            return existing
        breaker = CircuitBreaker(name=name, config=config)
        _REGISTRY.breakers[name] = breaker
        return breaker


def all_circuit_telemetry() -> list[CircuitTelemetry]:
    """Snapshot every breaker (used by audit logs and tests)."""
    with _REGISTRY.lock:
        breakers = list(_REGISTRY.breakers.values())
    return [b.telemetry() for b in breakers]


def reset_all_breakers() -> None:
    """Drop every breaker (used by tests)."""
    with _REGISTRY.lock:
        _REGISTRY.breakers.clear()


# ---------------------------------------------------------------------------
# Config loading
# ---------------------------------------------------------------------------


def load_breaker_config_from_target(
    target: dict[str, Any] | None, *, defaults: CircuitBreakerConfig | None = None
) -> CircuitBreakerConfig:
    """Build a :class:`CircuitBreakerConfig` from a target dict + env overrides.

    Per-target YAML keys (all optional)::

        circuit_breaker:
          failure_threshold: 3
          cooldown_seconds: 900
          retry_attempts: 3
          retry_max_seconds: 10
          jitter: true

    Environment overrides (apply globally; useful for "completão" smoke runs)::

        DATA_BOAR_CIRCUIT_FAILURE_THRESHOLD
        DATA_BOAR_CIRCUIT_COOLDOWN_SECONDS
        DATA_BOAR_RETRY_ATTEMPTS
        DATA_BOAR_RETRY_MAX_SECONDS
    """
    base = defaults or CircuitBreakerConfig()
    cfg = CircuitBreakerConfig(
        failure_threshold=base.failure_threshold,
        cooldown_seconds=base.cooldown_seconds,
        retry_attempts=base.retry_attempts,
        retry_base_seconds=base.retry_base_seconds,
        retry_max_seconds=base.retry_max_seconds,
        retry_ladder_seconds=base.retry_ladder_seconds,
        jitter=base.jitter,
    )

    yaml_block: dict[str, Any] = {}
    if isinstance(target, dict):
        raw = target.get("circuit_breaker")
        if isinstance(raw, dict):
            yaml_block = raw

    cfg.failure_threshold = _coerce_int(
        yaml_block.get("failure_threshold"),
        cfg.failure_threshold,
        minimum=1,
    )
    cfg.cooldown_seconds = _coerce_float(
        yaml_block.get("cooldown_seconds"),
        cfg.cooldown_seconds,
        minimum=1.0,
    )
    cfg.retry_attempts = _coerce_int(
        yaml_block.get("retry_attempts"),
        cfg.retry_attempts,
        minimum=1,
    )
    cfg.retry_max_seconds = _coerce_float(
        yaml_block.get("retry_max_seconds"),
        cfg.retry_max_seconds,
        minimum=0.0,
    )
    if "jitter" in yaml_block:
        cfg.jitter = bool(yaml_block.get("jitter"))

    cfg.failure_threshold = _coerce_int(
        os.environ.get("DATA_BOAR_CIRCUIT_FAILURE_THRESHOLD"),
        cfg.failure_threshold,
        minimum=1,
    )
    cfg.cooldown_seconds = _coerce_float(
        os.environ.get("DATA_BOAR_CIRCUIT_COOLDOWN_SECONDS"),
        cfg.cooldown_seconds,
        minimum=1.0,
    )
    cfg.retry_attempts = _coerce_int(
        os.environ.get("DATA_BOAR_RETRY_ATTEMPTS"),
        cfg.retry_attempts,
        minimum=1,
    )
    cfg.retry_max_seconds = _coerce_float(
        os.environ.get("DATA_BOAR_RETRY_MAX_SECONDS"),
        cfg.retry_max_seconds,
        minimum=0.0,
    )
    return cfg


def _coerce_int(raw: Any, default: int, *, minimum: int) -> int:
    if raw is None or raw == "":
        return default
    try:
        return max(minimum, int(raw))
    except (TypeError, ValueError):
        return default


def _coerce_float(raw: Any, default: float, *, minimum: float) -> float:
    if raw is None or raw == "":
        return default
    try:
        return max(minimum, float(raw))
    except (TypeError, ValueError):
        return default


# ---------------------------------------------------------------------------
# Transient classification
# ---------------------------------------------------------------------------

# Module / class names that look like network / DB transport hiccups.
# We match by name to avoid importing optional drivers (snowflake, oracledb,
# pymongo, redis, …) just to know their exception classes.
_TRANSIENT_CLASS_KEYWORDS: tuple[str, ...] = (
    "Timeout",
    "TimeoutError",
    "OperationalError",  # SQLAlchemy / DBAPI generic
    "InterfaceError",
    "DisconnectionError",
    "ConnectionError",
    "ConnectionAbortedError",
    "ConnectionRefusedError",
    "ConnectionResetError",
    "BrokenPipeError",
    "HTTPError",
    "ReadTimeout",
    "ConnectTimeout",
    "ServerSelectionTimeoutError",  # pymongo
    "AutoReconnect",  # pymongo
    "NetworkTimeout",
    "SocketTimeout",
)


def is_transient_error(exc: BaseException) -> bool:
    """Heuristic: ``True`` when ``exc`` looks like a transport / DB hiccup.

    We inspect the class name (and base class names) rather than importing
    every optional driver; concrete drivers are loaded lazily by connectors.

    Programmer errors (``ValueError``, ``TypeError``, ``KeyError``,
    ``AttributeError``) are always non-transient — retrying a buggy call
    only burns CPU.
    """
    if isinstance(exc, (ValueError, TypeError, KeyError, AttributeError)):
        return False
    if isinstance(
        exc,
        (TimeoutError, ConnectionError, OSError),
    ):
        # OSError catches socket.gaierror, BrokenPipeError, etc.
        return True
    names = {type(exc).__name__}
    for cls in type(exc).__mro__:
        names.add(cls.__name__)
    return any(
        any(keyword in name for keyword in _TRANSIENT_CLASS_KEYWORDS) for name in names
    )


def _short_reason(exc: BaseException) -> str:
    msg = str(exc).strip().splitlines()[0] if str(exc).strip() else ""
    if len(msg) > 240:
        msg = msg[:237] + "..."
    return msg or type(exc).__name__


__all__ = [
    "CircuitBreaker",
    "CircuitBreakerConfig",
    "CircuitOpenError",
    "CircuitState",
    "CircuitTelemetry",
    "DEFAULT_RETRY_ATTEMPTS",
    "DEFAULT_RETRY_BASE_SECONDS",
    "DEFAULT_RETRY_LADDER_SECONDS",
    "DEFAULT_RETRY_MAX_SECONDS",
    "all_circuit_telemetry",
    "compute_backoff_delay",
    "get_circuit_breaker",
    "is_transient_error",
    "load_breaker_config_from_target",
    "reset_all_breakers",
]
