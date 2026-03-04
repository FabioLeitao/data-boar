"""Tests for config loader and database layer (no live DB required)."""
import pytest
from pathlib import Path

from config.loader import load_config, normalize_config
from core.database import LocalDBManager, ScanSession, DatabaseFinding, DataWipeLog


def test_normalize_config_empty():
    out = normalize_config({"targets": []})
    assert out["targets"] == []
    assert "file_scan" in out
    assert out["api"].get("port") == 8088


def test_normalize_config_legacy_databases():
    out = normalize_config({
        "databases": [{"name": "x", "host": "h", "port": 5432, "user": "u", "password": "p", "database": "d"}],
        "file_scan": {"directories": [], "extensions": [".txt"]},
    })
    assert len(out["targets"]) >= 1
    db_target = next(t for t in out["targets"] if t.get("type") == "database")
    assert db_target["name"] == "x"
    assert db_target["host"] == "h"
    assert db_target["database"] == "d"


def test_normalize_config_detection_aggregated_identification():
    """Config loader normalizes detection.aggregated_identification_enabled, aggregated_min_categories, quasi_identifier_mapping."""
    out = normalize_config({
        "targets": [],
        "detection": {
            "aggregated_identification_enabled": False,
            "aggregated_min_categories": 3,
            "quasi_identifier_mapping": [
                {"column_pattern": "cargo", "category": "job_position"},
                {"pattern_detected": "PHONE_BR", "category": "phone"},
            ],
        },
    })
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


def test_local_db_manager(tmp_path):
    db_path = str(tmp_path / "test_audit.db")
    mgr = LocalDBManager(db_path)
    try:
        mgr.set_current_session_id("test-session-123")
        mgr.create_session_record("test-session-123")
        mgr.save_finding("database", target_name="T", server_ip="127.0.0.1", schema_name="s", table_name="t", column_name="c", data_type="VARCHAR", sensitivity_level="HIGH", pattern_detected="CPF", norm_tag="LGPD", ml_confidence=90)
        db_findings, fs_findings, failures = mgr.get_findings("test-session-123")
        assert len(db_findings) == 1
        assert db_findings[0]["column_name"] == "c"
        mgr.finish_session("test-session-123")
        sessions = mgr.list_sessions()
        assert any(s["session_id"] == "test-session-123" for s in sessions)
        assert "scan_failures" in sessions[0]
    finally:
        mgr.dispose()


def test_get_previous_session(tmp_path):
    db_path = str(tmp_path / "test_prev.db")
    mgr = LocalDBManager(db_path)
    try:
        mgr.set_current_session_id("session-first")
        mgr.create_session_record("session-first")
        mgr.save_finding("database", target_name="T", session_id="session-first", column_name="c1", sensitivity_level="HIGH", pattern_detected="CPF", norm_tag="LGPD", ml_confidence=80)
        mgr.finish_session("session-first")
        mgr.set_current_session_id("session-second")
        mgr.create_session_record("session-second")
        mgr.save_finding("database", target_name="T", session_id="session-second", column_name="c2", sensitivity_level="HIGH", pattern_detected="EMAIL", norm_tag="GDPR", ml_confidence=85)
        mgr.finish_session("session-second")
        prev = mgr.get_previous_session("session-second")
        assert prev is not None
        assert prev["session_id"] == "session-first"
        assert prev["database_findings"] == 1
        assert mgr.get_previous_session("session-first") is None
    finally:
        mgr.dispose()


def test_wipe_all_data_logs_and_clears(tmp_path):
    db_path = str(tmp_path / "test_wipe.db")
    mgr = LocalDBManager(db_path)
    try:
        # Create two sessions with findings
        mgr.set_current_session_id("s1")
        mgr.create_session_record("s1")
        mgr.save_finding("database", target_name="T1", schema_name="s", table_name="t", column_name="c1", data_type="VARCHAR", sensitivity_level="HIGH", pattern_detected="CPF", norm_tag="LGPD", ml_confidence=90)
        mgr.finish_session("s1")

        mgr.set_current_session_id("s2")
        mgr.create_session_record("s2")
        mgr.save_finding("database", target_name="T2", schema_name="s", table_name="t", column_name="c2", data_type="VARCHAR", sensitivity_level="HIGH", pattern_detected="EMAIL", norm_tag="GDPR", ml_confidence=85)
        mgr.finish_session("s2")

        # Sanity check: we have sessions and findings
        assert mgr.list_sessions()
        db_rows, fs_rows, fail_rows = mgr.get_findings("s1")
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
