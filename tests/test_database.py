"""Tests for config loader and database layer (no live DB required)."""
import pytest
from pathlib import Path

from config.loader import load_config, normalize_config
from core.database import LocalDBManager, ScanSession, DatabaseFinding


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


def test_local_db_manager(tmp_path):
    db_path = str(tmp_path / "test_audit.db")
    mgr = LocalDBManager(db_path)
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


def test_get_previous_session(tmp_path):
    db_path = str(tmp_path / "test_prev.db")
    mgr = LocalDBManager(db_path)
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


def test_load_config_file(config_path=None):
    path = Path("config.yaml")
    if not path.exists():
        path = Path("config/config.json")
    if not path.exists():
        pytest.skip("No config.yaml or config/config.json")
    config = load_config(path)
    assert "targets" in config
    assert "file_scan" in config
