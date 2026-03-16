"""
Test that the web API POST /scan (Start scan) triggers a full audit using the config's targets.
Ensures the dashboard Start scan button flow runs the audit engine with the current config.
"""

from fastapi.testclient import TestClient


def test_post_scan_triggers_audit_using_config(tmp_path):
    """
    POST /scan must start a background audit that uses targets from the config file.
    With a minimal config (targets: []), the scan completes immediately; we assert
    the session is created and appears in /list.
    """
    out_dir = str(tmp_path).replace("\\", "/")
    config_yaml = f"""targets: []
file_scan:
  extensions: [.txt, .csv]
  recursive: true
  scan_sqlite_as_db: false
  sample_limit: 2
report:
  output_dir: {out_dir}
api:
  port: 8088
sqlite_path: {out_dir}/audit_results.db
scan:
  max_workers: 1
"""
    config_path = tmp_path / "config.yaml"
    config_path.write_text(config_yaml, encoding="utf-8")

    # Patch the API module to use our temp config and DB path in normalized config
    import api.routes as routes

    original_config_path = routes._config_path
    original_config = routes._config
    original_engine = routes._audit_engine
    try:
        routes._config_path = str(config_path)
        routes._config = None
        routes._audit_engine = None

        app = routes.app
        client = TestClient(app)

        # Start scan (same as dashboard "Start scan" button: POST /scan)
        resp = client.post("/scan", json={})
        assert resp.status_code == 200, resp.text
        data = resp.json()
        assert data.get("status") == "started"
        session_id = data.get("session_id")
        assert session_id is not None and len(session_id) > 0

        # TestClient runs background tasks after response; session should be created and scan done
        list_resp = client.get("/list")
        assert list_resp.status_code == 200
        sessions = list_resp.json().get("sessions", [])
        assert any(s.get("session_id") == session_id for s in sessions), (
            f"Expected session {session_id} in {[s.get('session_id') for s in sessions]}"
        )

        # Status should be idle after scan completes (background task ran)
        status_resp = client.get("/status")
        assert status_resp.status_code == 200
        assert status_resp.json().get("running") is False
    finally:
        routes._config_path = original_config_path
        routes._config = original_config
        routes._audit_engine = original_engine
