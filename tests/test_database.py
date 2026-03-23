"""Tests for config loader and database layer (no live DB required)."""

import os
import pytest
from pathlib import Path

from config.loader import load_config, normalize_config
from core.database import DataSourceInventory, DataWipeLog, LocalDBManager, failure_hint


def test_normalize_config_empty():
    out = normalize_config({"targets": []})
    assert out["targets"] == []
    assert "file_scan" in out
    assert out["api"].get("port") == 8088


def test_normalize_config_legacy_databases():
    # Use placeholder for password field; test only verifies normalization (no real credentials).
    out = normalize_config(
        {
            "databases": [
                {
                    "name": "x",
                    "host": "h",
                    "port": 5432,
                    "user": "u",
                    "password": os.environ.get("TEST_DB_PASSWORD", "test-placeholder"),
                    "database": "d",
                }
            ],
            "file_scan": {"directories": [], "extensions": [".txt"]},
        }
    )
    assert len(out["targets"]) >= 1
    db_target = next(t for t in out["targets"] if t.get("type") == "database")
    assert db_target["name"] == "x"
    assert db_target["host"] == "h"
    assert db_target["database"] == "d"


def test_normalize_config_detection_aggregated_identification():
    """Config loader normalizes detection.aggregated_identification_enabled, aggregated_min_categories, quasi_identifier_mapping."""
    out = normalize_config(
        {
            "targets": [],
            "detection": {
                "aggregated_identification_enabled": False,
                "aggregated_min_categories": 3,
                "quasi_identifier_mapping": [
                    {"column_pattern": "cargo", "category": "job_position"},
                    {"pattern_detected": "PHONE_BR", "category": "phone"},
                ],
            },
        }
    )
    det = out.get("detection", {})
    assert det.get("aggregated_identification_enabled") is False
    assert det.get("aggregated_min_categories") == 3
    assert len(det.get("quasi_identifier_mapping", [])) == 2
    assert det["quasi_identifier_mapping"][0]["category"] == "job_position"
    assert det["quasi_identifier_mapping"][1]["category"] == "phone"

    # Defaults when detection section is missing or empty
    out2 = normalize_config({"targets": []})
    det2 = out2.get("detection", {})
    assert det2.get("aggregated_identification_enabled") is True
    assert det2.get("aggregated_min_categories") == 2
    assert det2.get("quasi_identifier_mapping") == []


def test_normalize_config_rate_limit_and_scan_max_workers(monkeypatch):
    """Config loader normalizes rate_limit block and clamps scan.max_workers."""
    # No env overrides
    cfg = normalize_config(
        {
            "targets": [],
            "scan": {"max_workers": 100},
            "rate_limit": {
                "enabled": True,
                "max_concurrent_scans": 0,  # should be clamped to >= 1
                "min_interval_seconds": -10,  # should be clamped to >= 0
                "grace_for_running_status": -5,  # should be clamped to >= 0
            },
        }
    )
    rl = cfg.get("rate_limit", {})
    assert rl.get("enabled") is True
    assert rl.get("max_concurrent_scans") >= 1
    assert rl.get("min_interval_seconds") >= 0
    assert rl.get("grace_for_running_status") >= 0
    # max_workers capped to a safe upper bound
    assert cfg.get("scan", {}).get("max_workers") <= 32


def test_normalize_config_timeouts_and_per_target():
    """Config loader adds global timeouts (defaults 25/90) and merges per-target overrides."""
    out = normalize_config(
        {
            "targets": [
                {
                    "name": "defaults",
                    "type": "database",
                    "driver": "postgresql",
                    "host": "h",
                    "database": "d",
                },
                {
                    "name": "overrides",
                    "type": "api",
                    "base_url": "http://x",
                    "connect_timeout": 10,
                    "read_timeout": 60,
                },
                {
                    "name": "single",
                    "type": "database",
                    "driver": "mysql",
                    "host": "h",
                    "database": "d",
                    "timeout": 45,
                },
            ],
            "timeouts": {"connect_seconds": 20, "read_seconds": 80},
        }
    )
    assert out.get("timeouts", {}).get("connect_seconds") == 20
    assert out.get("timeouts", {}).get("read_seconds") == 80
    targets = out["targets"]
    t0 = next(t for t in targets if t.get("name") == "defaults")
    assert (
        t0.get("connect_timeout_seconds") == 20 and t0.get("read_timeout_seconds") == 80
    )
    t1 = next(t for t in targets if t.get("name") == "overrides")
    assert (
        t1.get("connect_timeout_seconds") == 10 and t1.get("read_timeout_seconds") == 60
    )
    t2 = next(t for t in targets if t.get("name") == "single")
    assert (
        t2.get("connect_timeout_seconds") == 45 and t2.get("read_timeout_seconds") == 45
    )
    # Empty config: defaults 25/90
    out2 = normalize_config({"targets": []})
    assert out2.get("timeouts", {}).get("connect_seconds") == 25
    assert out2.get("timeouts", {}).get("read_seconds") == 90


def test_failure_hint_timeout_includes_config_guidance():
    """failure_hint('timeout') points operators to config timeouts and USAGE (Phase 4.2)."""
    hint = failure_hint("timeout")
    assert "timeout" in hint.lower()
    assert "USAGE" in hint or "timeouts" in hint
    assert "connect" in hint.lower() or "read" in hint.lower()


def test_failure_hint_other_reasons():
    """failure_hint returns sensible hints for unreachable, auth_failed, permission_denied."""
    assert (
        "connectivity" in failure_hint("unreachable").lower()
        or "network" in failure_hint("unreachable").lower()
    )
    assert "auth" in failure_hint("auth_failed").lower()
    assert "permission" in failure_hint("permission_denied").lower()
    assert (
        "unexpected" in failure_hint("unknown").lower()
        or "error" in failure_hint("unknown").lower()
    )


def test_local_db_manager(tmp_path):
    db_path = str(tmp_path / "test_audit.db")
    mgr = LocalDBManager(db_path)
    try:
        mgr.set_current_session_id("test-session-123")
        mgr.create_session_record("test-session-123")
        mgr.save_finding(
            "database",
            target_name="T",
            server_ip="127.0.0.1",
            schema_name="s",
            table_name="t",
            column_name="c",
            data_type="VARCHAR",
            sensitivity_level="HIGH",
            pattern_detected="CPF",
            norm_tag="LGPD",
            ml_confidence=90,
        )
        db_findings, _, _ = mgr.get_findings("test-session-123")
        assert len(db_findings) == 1
        assert db_findings[0]["column_name"] == "c"
        mgr.finish_session("test-session-123")
        sessions = mgr.list_sessions()
        assert any(s["session_id"] == "test-session-123" for s in sessions)
        assert "scan_failures" in sessions[0]
    finally:
        mgr.dispose()


def test_data_source_inventory_save_and_get(tmp_path):
    db_path = str(tmp_path / "test_inventory.db")
    mgr = LocalDBManager(db_path)
    try:
        mgr.set_current_session_id("inv-session-1")
        mgr.create_session_record("inv-session-1")
        mgr.save_data_source_inventory(
            target_name="pg-main",
            source_type="database",
            product="postgresql",
            product_version="PostgreSQL 16.2",
            protocol_or_api_version="postgresql",
            transport_security="sslmode=require",
            raw_details='{"driver":"postgresql"}',
        )
        rows = mgr.get_data_source_inventory("inv-session-1")
        assert len(rows) == 1
        assert rows[0]["target_name"] == "pg-main"
        assert rows[0]["product"] == "postgresql"
        assert rows[0]["transport_security"] == "sslmode=require"
    finally:
        mgr.dispose()


def test_get_previous_session(tmp_path):
    db_path = str(tmp_path / "test_prev.db")
    mgr = LocalDBManager(db_path)
    try:
        mgr.set_current_session_id("session-first")
        mgr.create_session_record("session-first")
        mgr.save_finding(
            "database",
            target_name="T",
            session_id="session-first",
            column_name="c1",
            sensitivity_level="HIGH",
            pattern_detected="CPF",
            norm_tag="LGPD",
            ml_confidence=80,
        )
        mgr.finish_session("session-first")
        mgr.set_current_session_id("session-second")
        mgr.create_session_record("session-second")
        mgr.save_finding(
            "database",
            target_name="T",
            session_id="session-second",
            column_name="c2",
            sensitivity_level="HIGH",
            pattern_detected="EMAIL",
            norm_tag="GDPR",
            ml_confidence=85,
        )
        mgr.finish_session("session-second")
        prev = mgr.get_previous_session("session-second")
        assert prev is not None
        assert prev["session_id"] == "session-first"
        assert prev["database_findings"] == 1
        assert mgr.get_previous_session("session-first") is None
    finally:
        mgr.dispose()


def test_running_sessions_count_and_last_session(tmp_path):
    """LocalDBManager helpers for rate limiting: running count and last session metadata."""
    db_path = str(tmp_path / "test_running.db")
    mgr = LocalDBManager(db_path)
    try:
        # No sessions yet
        assert mgr.get_running_sessions_count() == 0
        assert mgr.get_last_session() is None

        # First session: running
        mgr.set_current_session_id("s1")
        mgr.create_session_record("s1")
        running_count = mgr.get_running_sessions_count()
        assert running_count == 1
        last = mgr.get_last_session()
        assert last is not None
        assert last["session_id"] == "s1"
        assert last["status"] == "running"

        # Mark as completed and add a newer running session
        mgr.finish_session("s1")
        mgr.set_current_session_id("s2")
        mgr.create_session_record("s2")
        running_count2 = mgr.get_running_sessions_count()
        assert running_count2 == 1  # only s2 is running
        last2 = mgr.get_last_session()
        assert last2 is not None
        assert last2["session_id"] == "s2"
        assert last2["status"] == "running"
    finally:
        mgr.dispose()


def test_wipe_all_data_logs_and_clears(tmp_path):
    db_path = str(tmp_path / "test_wipe.db")
    mgr = LocalDBManager(db_path)
    try:
        # Create two sessions with findings
        mgr.set_current_session_id("s1")
        mgr.create_session_record("s1")
        mgr.save_finding(
            "database",
            target_name="T1",
            schema_name="s",
            table_name="t",
            column_name="c1",
            data_type="VARCHAR",
            sensitivity_level="HIGH",
            pattern_detected="CPF",
            norm_tag="LGPD",
            ml_confidence=90,
        )
        mgr.finish_session("s1")

        mgr.set_current_session_id("s2")
        mgr.create_session_record("s2")
        mgr.save_finding(
            "database",
            target_name="T2",
            schema_name="s",
            table_name="t",
            column_name="c2",
            data_type="VARCHAR",
            sensitivity_level="HIGH",
            pattern_detected="EMAIL",
            norm_tag="GDPR",
            ml_confidence=85,
        )
        mgr.finish_session("s2")
        mgr.save_data_source_inventory(
            target_name="db-host",
            source_type="database",
            product="sqlite",
            product_version="3.x",
        )

        # Sanity check: we have sessions and findings
        assert mgr.list_sessions()
        db_rows, _, _ = mgr.get_findings("s1")
        assert db_rows

        # Wipe everything and ensure sessions/findings are gone but a wipe log exists
        mgr.wipe_all_data("pytest wipe")

        sessions_after = mgr.list_sessions()
        assert sessions_after == []

        # Directly inspect DataWipeLog via a new session factory
        s = mgr._session_factory()
        try:
            wipes = s.query(DataWipeLog).all()
            assert len(wipes) == 1
            assert "pytest wipe" in wipes[0].reason
            inventories = s.query(DataSourceInventory).all()
            assert inventories == []
        finally:
            s.close()
    finally:
        mgr.dispose()


def test_load_config_file(config_path=None):
    path = Path("config.yaml")
    if not path.exists():
        path = Path("config/config.json")
    if not path.exists():
        pytest.skip("No config.yaml or config/config.json")
    config = load_config(path)
    assert "targets" in config
    assert "file_scan" in config
