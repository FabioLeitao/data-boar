"""Tests for the engine ↔ circuit breaker integration.

The "blast radius" property the engineering mission asked for: when **one**
target keeps failing, the breaker trips, that target is **skipped**, and the
rest of the scan keeps going. We verify that with two synthetic targets:

* ``zombie`` — a connector whose ``run()`` always raises a transient error.
* ``healthy`` — a connector whose ``run()`` succeeds.

After the first run for ``zombie`` exhausts its retries and trips the
breaker, a second run for the same target must short-circuit (no
``connector.run()`` invocation) and emit a ``circuit_open`` failure row.
The healthy target must still be processed.
"""

from __future__ import annotations

from typing import Any

import pytest

from core.engine import AuditEngine
from core.resilience import (
    CircuitOpenError,
    CircuitState,
    get_circuit_breaker,
    reset_all_breakers,
)


# ---------------------------------------------------------------------------
# Synthetic connector
# ---------------------------------------------------------------------------


class _ScriptedConnector:
    """A test double matching the connector contract used by the engine.

    The engine instantiates connectors via ``connector_for_target`` -> class
    lookup. We sidestep that by patching ``connector_for_target`` to return
    this scripted class for the duration of the test.
    """

    behavior: str = "ok"
    runs: list[str] = []

    def __init__(
        self,
        target_config: dict[str, Any],
        scanner: Any,
        db_manager: Any,
        sample_limit: int = 5,
        detection_config: dict[str, Any] | None = None,
        sampling_policy: Any = None,
    ) -> None:
        self.config = target_config
        self.scanner = scanner
        self.db_manager = db_manager
        self.sample_limit = sample_limit

    def run(self) -> None:
        target_name = self.config.get("name", "unknown")
        type(self).runs.append(target_name)
        if target_name == "zombie":
            # Drive the breaker through the retry ladder by calling it
            # directly here — that mirrors what real connectors do during
            # connect() (they wrap the I/O call in breaker.call).
            from core.resilience import (
                get_circuit_breaker as _get,
                load_breaker_config_from_target,
            )

            breaker = _get(
                f"target:{target_name}",
                config=load_breaker_config_from_target(self.config),
            )

            def _always_fail() -> Any:
                raise TimeoutError("zombie target")

            breaker.call(_always_fail)
        elif target_name == "healthy":
            self.db_manager.save_finding(
                source_type="database",
                target_name=target_name,
                server_ip="localhost",
                engine_details="test",
                schema_name="",
                table_name="t",
                column_name="c",
                data_type="text",
                sensitivity_level="MEDIUM",
                pattern_detected="DUMMY",
                norm_tag="",
                ml_confidence=0,
            )
        else:
            raise RuntimeError(f"unscripted target: {target_name}")


@pytest.fixture(autouse=True)
def _isolate_breakers() -> None:
    reset_all_breakers()
    _ScriptedConnector.runs = []
    yield
    reset_all_breakers()


def _make_config() -> dict[str, Any]:
    return {
        "targets": [
            {
                "name": "zombie",
                "type": "database",
                "driver": "test",
                "circuit_breaker": {
                    "failure_threshold": 3,
                    "cooldown_seconds": 900,
                    "retry_attempts": 3,
                    "retry_max_seconds": 0,
                    "jitter": False,
                },
            },
            {
                "name": "healthy",
                "type": "database",
                "driver": "test",
            },
        ],
        "scan": {"max_workers": 1},
        "file_scan": {},
    }


def test_engine_skips_zombie_target_after_breaker_trips(tmp_path, monkeypatch) -> None:
    """First run trips the breaker; second run short-circuits without calling run()."""
    db_path = tmp_path / "audit.db"
    cfg = _make_config()
    engine = AuditEngine(cfg, db_path=str(db_path))

    # Patch the connector lookup to return our scripted connector for any target.
    monkeypatch.setattr(
        "core.engine.connector_for_target",
        lambda t: (_ScriptedConnector, "test"),
    )
    # Avoid any real backoff sleep regardless of jitter config.
    monkeypatch.setattr("core.resilience.time.sleep", lambda s: None)
    # Ensure the SQL connector branch in _run_target gets crypto signal stub
    # — but for this synthetic flow, summarize_crypto_from_connection_info
    # already accepts our shape and may return an empty set.
    sid = engine.start_audit()
    assert sid

    # Both targets attempted on the first run: zombie failed (3 retries),
    # healthy succeeded.
    assert "zombie" in _ScriptedConnector.runs
    assert "healthy" in _ScriptedConnector.runs

    # Breaker for the zombie target must now be OPEN.
    breaker = get_circuit_breaker("target:zombie")
    assert breaker.state is CircuitState.OPEN

    # A failure row exists for zombie with reason=error (raised TimeoutError
    # propagated out of run()) — and the audit log readback should reflect
    # the breaker telemetry.
    audit_log = engine.get_scan_audit_log()
    breakers_in_log = {b["name"]: b for b in audit_log.get("circuit_breakers", [])}
    assert "target:zombie" in breakers_in_log
    assert breakers_in_log["target:zombie"]["state"] == "open"

    # --- Second run on the same engine: zombie should be SKIPPED. ---
    _ScriptedConnector.runs.clear()
    sid_2 = engine.start_audit()
    # The zombie's run() must NOT have been invoked again.
    assert "zombie" not in _ScriptedConnector.runs
    # Healthy target still ran.
    assert "healthy" in _ScriptedConnector.runs
    # And a circuit_open failure row was written for the zombie target on
    # this fresh session.
    _db, _fs, failures = engine.db_manager.get_findings(session_id=sid_2)
    zombie_rows = [r for r in failures if r.get("target_name") == "zombie"]
    assert zombie_rows, "Expected a circuit_open failure row for zombie"
    assert zombie_rows[0]["reason"] == "circuit_open"


def test_circuit_open_error_inside_run_logs_circuit_open_reason(
    tmp_path, monkeypatch
) -> None:
    """When a connector itself raises CircuitOpenError mid-run, we record reason=circuit_open."""
    db_path = tmp_path / "audit.db"
    cfg = _make_config()
    cfg["targets"] = [cfg["targets"][0]]  # only zombie
    engine = AuditEngine(cfg, db_path=str(db_path))

    class _AlreadyOpenConnector(_ScriptedConnector):
        def run(self) -> None:  # type: ignore[override]
            raise CircuitOpenError(
                breaker_name="target:zombie",
                retry_after_seconds=300.0,
                consecutive_failures=4,
            )

    monkeypatch.setattr(
        "core.engine.connector_for_target",
        lambda t: (_AlreadyOpenConnector, "test"),
    )
    monkeypatch.setattr("core.resilience.time.sleep", lambda s: None)

    engine.start_audit()
    _db, _fs, failures = engine.db_manager.get_findings()
    rows = [r for r in failures if r.get("target_name") == "zombie"]
    assert rows, "Expected a failure row for the zombie target"
    assert rows[0]["reason"] == "circuit_open"
    assert "circuit_open" in (rows[0].get("details") or "")
