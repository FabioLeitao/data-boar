"""API report/heatmap path containment (aligned with CodeQL py/path-injection patterns)."""

import os
from pathlib import Path

import pytest
from fastapi.testclient import TestClient


def _write_minimal_config(
    config_path: Path, output_dir: Path, sqlite_path: Path
) -> None:
    config_path.write_text(
        f"""targets: []
report:
  output_dir: {output_dir}
api:
  port: 8088
sqlite_path: {sqlite_path}
scan:
  max_workers: 1
""",
        encoding="utf-8",
    )


def _set_routes_context(tmp_path: Path, output_dir: Path):
    import api.routes as routes

    config_path = tmp_path / "config.yaml"
    sqlite_path = tmp_path / "audit.db"
    _write_minimal_config(config_path, output_dir, sqlite_path)

    orig = (routes._config_path, routes._config, routes._audit_engine)
    routes._config_path = str(config_path)
    routes._config = None
    routes._audit_engine = None
    return routes, orig


def _restore_routes_context(routes, orig):
    routes._config_path, routes._config, routes._audit_engine = orig


class _FakeDBManager:
    current_session_id = None

    @staticmethod
    def list_sessions():
        return []


class _FakeEngine:
    def __init__(self, report_output_dir: Path, report_path: Path):
        self.config = {"report": {"output_dir": str(report_output_dir)}}
        self._report_path = str(report_path)
        self.db_manager = _FakeDBManager()

    def get_last_report_path(self):
        return self._report_path

    def generate_final_reports(self, _session_id):
        return self._report_path


def test_download_report_rejects_path_outside_configured_output_dir(tmp_path: Path):
    output_dir = tmp_path / "reports"
    output_dir.mkdir(parents=True, exist_ok=True)
    outside_report = tmp_path / "outside.xlsx"
    outside_report.write_text("dummy", encoding="utf-8")

    routes, orig = _set_routes_context(tmp_path, output_dir)
    try:
        routes._audit_engine = _FakeEngine(output_dir, outside_report)
        client = TestClient(routes.app)
        resp = client.get("/report")
        assert resp.status_code == 404
    finally:
        _restore_routes_context(routes, orig)


def test_download_report_rejects_non_report_filename_pattern(tmp_path: Path):
    """Basename must match Relatorio_Auditoria_*.xlsx even if file sits under output_dir."""
    output_dir = tmp_path / "reports"
    output_dir.mkdir(parents=True, exist_ok=True)
    bad_name = output_dir / "not_a_report.xlsx"
    bad_name.write_text("dummy", encoding="utf-8")

    routes, orig = _set_routes_context(tmp_path, output_dir)
    try:
        routes._audit_engine = _FakeEngine(output_dir, bad_name)
        client = TestClient(routes.app)
        resp = client.get("/report")
        assert resp.status_code == 404
    finally:
        _restore_routes_context(routes, orig)


def test_resolved_existing_file_under_out_dir_rejects_traversal(tmp_path: Path):
    """Join+normpath+realpath containment must reject escaping the base directory."""
    import api.routes as routes

    base = tmp_path / "out"
    base.mkdir(parents=True, exist_ok=True)
    (base / "good.png").write_bytes(b"x")
    assert routes._resolved_existing_file_under_out_dir(base, "good.png") is not None
    assert routes._resolved_existing_file_under_out_dir(base, "../out/good.png") is None
    assert routes._resolved_existing_file_under_out_dir(base, "..") is None
    assert routes._resolved_existing_file_under_out_dir(base, "nope.png") is None


def test_heatmap_png_path_for_download_matches_allowlist(tmp_path: Path):
    import api.routes as routes

    out = tmp_path / "reports"
    out.mkdir(parents=True, exist_ok=True)
    (out / "heatmap_abcdef123456.png").write_bytes(b"png")
    engine = _FakeEngine(out, out / "Relatorio_Auditoria_abcdef123456.xlsx")
    ok = routes._heatmap_png_path_for_download(engine, "abcdef1234567890")
    assert ok is not None and ok.name == "heatmap_abcdef123456.png"
    assert routes._heatmap_png_path_for_download(engine, "../../etc") is None


def test_download_heatmap_rejects_report_path_outside_configured_output_dir(
    tmp_path: Path,
):
    output_dir = tmp_path / "reports"
    output_dir.mkdir(parents=True, exist_ok=True)
    outside_report = tmp_path / "Relatorio_Auditoria_abcdef123456.xlsx"
    outside_report.write_text("dummy", encoding="utf-8")
    # Even if a matching heatmap exists beside the report, endpoint must reject the base report path.
    outside_heatmap = tmp_path / "heatmap_abcdef123456.png"
    outside_heatmap.write_bytes(b"png")

    routes, orig = _set_routes_context(tmp_path, output_dir)
    try:
        routes._audit_engine = _FakeEngine(output_dir, outside_report)
        client = TestClient(routes.app)
        resp = client.get("/heatmap")
        assert resp.status_code == 404
    finally:
        _restore_routes_context(routes, orig)


# -- /logs and /logs/{session_id} containment (CodeQL py/path-injection on audit logs) --


@pytest.fixture
def _chdir(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """Run /logs handlers against ``tmp_path`` as runtime CWD (audit log dir)."""
    monkeypatch.chdir(tmp_path)
    return tmp_path


def test_audit_log_filename_pattern_only_accepts_dated_audit_logs():
    """Allowlist must be exactly ``audit_YYYYMMDD.log`` — no traversal sneakers."""
    import api.routes as routes

    pat = routes._AUDIT_LOG_FILENAME_PATTERN
    assert pat.fullmatch("audit_20260427.log")
    # Reject traversal, wrong extension, missing date, separator confusion.
    for bad in (
        "../audit_20260427.log",
        "audit_20260427.log.bak",
        "audit_2026-04-27.log",
        "audit_.log",
        "AUDIT_20260427.LOG",
        "config.yaml",
        "",
    ):
        assert pat.fullmatch(bad) is None, bad


def test_safe_audit_log_path_rejects_non_log_basename(_chdir: Path):
    import api.routes as routes

    (_chdir / "config.yaml").write_text("targets: []", encoding="utf-8")
    assert routes._safe_audit_log_path("config.yaml") is None
    assert routes._safe_audit_log_path("../etc/passwd") is None
    assert routes._safe_audit_log_path("") is None


def test_safe_audit_log_path_returns_existing_log_under_cwd(_chdir: Path):
    import api.routes as routes

    log = _chdir / "audit_20260427.log"
    log.write_text("session=abcdef abcdef\n", encoding="utf-8")
    safe = routes._safe_audit_log_path("audit_20260427.log")
    assert safe is not None
    assert os.path.basename(safe) == "audit_20260427.log"


def test_get_logs_returns_bytes_response_not_fileresponse(_chdir: Path):
    """``GET /logs`` must stream bytes (no ``FileResponse(path=...)`` sink)."""
    import api.routes as routes

    log = _chdir / "audit_20260427.log"
    log.write_text("hello world\n", encoding="utf-8")
    client = TestClient(routes.app)
    resp = client.get("/logs")
    assert resp.status_code == 200
    assert resp.headers["content-type"].startswith("text/plain")
    assert "audit_20260427.log" in resp.headers.get("content-disposition", "")
    assert resp.content == b"hello world\n"


def test_get_logs_skips_non_allowlisted_files(_chdir: Path):
    """A file matching ``audit_*.log`` glob but not the YYYYMMDD allowlist is skipped."""
    import api.routes as routes

    # glob("audit_*.log") would match this, but the allowlist must reject it.
    bogus = _chdir / "audit_evil.log"
    bogus.write_text("nope", encoding="utf-8")
    client = TestClient(routes.app)
    resp = client.get("/logs")
    assert resp.status_code == 404


def test_get_logs_session_id_search_skips_non_allowlisted_files(_chdir: Path):
    import api.routes as routes

    bogus = _chdir / "audit_evil.log"
    bogus.write_text("session=abcdef123456789\n", encoding="utf-8")
    client = TestClient(routes.app)
    resp = client.get("/logs/abcdef123456789")
    assert resp.status_code == 404


def test_get_logs_session_id_returns_bytes_for_matching_log(_chdir: Path):
    import api.routes as routes

    log = _chdir / "audit_20260427.log"
    log.write_text("session=abcdef123456789 finding=42\n", encoding="utf-8")
    client = TestClient(routes.app)
    resp = client.get("/logs/abcdef123456789")
    assert resp.status_code == 200
    assert resp.headers["content-type"].startswith("text/plain")
    assert b"abcdef123456789" in resp.content


def test_get_logs_invalid_session_id_returns_400(_chdir: Path):
    import api.routes as routes

    client = TestClient(routes.app)
    # Path traversal-shaped id is rejected by _validate_session_id before any file open.
    resp = client.get("/logs/..%2Fetc%2Fpasswd")
    assert resp.status_code in (400, 404)  # routing may collapse %2F to /


def test_audit_log_read_bound_caps_memory(
    _chdir: Path, monkeypatch: pytest.MonkeyPatch
):
    """A pathologically large audit log must not load fully into memory."""
    import api.routes as routes

    monkeypatch.setattr(routes, "_AUDIT_LOG_MAX_READ_BYTES", 16, raising=True)
    log = _chdir / "audit_20260427.log"
    log.write_bytes(b"A" * 4096)
    client = TestClient(routes.app)
    resp = client.get("/logs")
    assert resp.status_code == 200
    assert len(resp.content) == 16
    assert resp.headers.get("X-Data-Boar-Log-Truncated") == "1"
