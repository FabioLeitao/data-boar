"""
Tests for optional API key: when api.require_api_key is true, requests must provide
X-API-Key or Authorization: Bearer <key>; /health is always allowed without key.
"""

from fastapi.testclient import TestClient


def test_health_allowed_without_key_when_api_key_required(tmp_path):
    """GET /health must return 200 without API key even when require_api_key is true."""
    config_yaml = f"""targets: []
report:
  output_dir: {tmp_path}
api:
  port: 8088
  require_api_key: true
  api_key: "secret123"
sqlite_path: {tmp_path}/audit.db
"""
    config_path = tmp_path / "config.yaml"
    config_path.write_text(config_yaml, encoding="utf-8")

    import api.routes as routes

    orig_path = routes._config_path
    orig_cfg = routes._config
    orig_engine = routes._audit_engine
    try:
        routes._config_path = str(config_path)
        routes._config = None
        routes._audit_engine = None
        client = TestClient(routes.app)
        resp = client.get("/health")
        assert resp.status_code == 200
        assert resp.json().get("status") == "ok"
    finally:
        routes._config_path = orig_path
        routes._config = orig_cfg
        routes._audit_engine = orig_engine


def test_required_api_key_rejects_missing_key(tmp_path):
    """When require_api_key true, GET /status without key returns 401."""
    config_yaml = f"""targets: []
report:
  output_dir: {tmp_path}
api:
  port: 8088
  require_api_key: true
  api_key: "secret123"
sqlite_path: {tmp_path}/audit.db
"""
    config_path = tmp_path / "config.yaml"
    config_path.write_text(config_yaml, encoding="utf-8")

    import api.routes as routes

    orig_path = routes._config_path
    orig_cfg = routes._config
    orig_engine = routes._audit_engine
    try:
        routes._config_path = str(config_path)
        routes._config = None
        routes._audit_engine = None
        client = TestClient(routes.app)
        resp = client.get("/status")
        assert resp.status_code == 401
        assert "detail" in resp.json()
    finally:
        routes._config_path = orig_path
        routes._config = orig_cfg
        routes._audit_engine = orig_engine


def test_required_api_key_accepts_x_api_key_header(tmp_path):
    """When require_api_key true, GET /status with X-API-Key returns 200."""
    config_yaml = f"""targets: []
report:
  output_dir: {tmp_path}
api:
  port: 8088
  require_api_key: true
  api_key: "secret123"
sqlite_path: {tmp_path}/audit.db
"""
    config_path = tmp_path / "config.yaml"
    config_path.write_text(config_yaml, encoding="utf-8")

    import api.routes as routes

    orig_path = routes._config_path
    orig_cfg = routes._config
    orig_engine = routes._audit_engine
    try:
        routes._config_path = str(config_path)
        routes._config = None
        routes._audit_engine = None
        client = TestClient(routes.app)
        resp = client.get("/status", headers={"X-API-Key": "secret123"})
        assert resp.status_code == 200
    finally:
        routes._config_path = orig_path
        routes._config = orig_cfg
        routes._audit_engine = orig_engine


def test_required_api_key_accepts_bearer(tmp_path):
    """When require_api_key true, GET /status with Authorization: Bearer <key> returns 200."""
    config_yaml = f"""targets: []
report:
  output_dir: {tmp_path}
api:
  port: 8088
  require_api_key: true
  api_key: "secret123"
sqlite_path: {tmp_path}/audit.db
"""
    config_path = tmp_path / "config.yaml"
    config_path.write_text(config_yaml, encoding="utf-8")

    import api.routes as routes

    orig_path = routes._config_path
    orig_cfg = routes._config
    orig_engine = routes._audit_engine
    try:
        routes._config_path = str(config_path)
        routes._config = None
        routes._audit_engine = None
        client = TestClient(routes.app)
        resp = client.get("/status", headers={"Authorization": "Bearer secret123"})
        assert resp.status_code == 200
    finally:
        routes._config_path = orig_path
        routes._config = orig_cfg
        routes._audit_engine = orig_engine


def test_required_api_key_rejects_wrong_key(tmp_path):
    """When require_api_key true, wrong key returns 401."""
    config_yaml = f"""targets: []
report:
  output_dir: {tmp_path}
api:
  port: 8088
  require_api_key: true
  api_key: "secret123"
sqlite_path: {tmp_path}/audit.db
"""
    config_path = tmp_path / "config.yaml"
    config_path.write_text(config_yaml, encoding="utf-8")

    import api.routes as routes

    orig_path = routes._config_path
    orig_cfg = routes._config
    orig_engine = routes._audit_engine
    try:
        routes._config_path = str(config_path)
        routes._config = None
        routes._audit_engine = None
        client = TestClient(routes.app)
        resp = client.get("/status", headers={"X-API-Key": "wrong"})
        assert resp.status_code == 401
    finally:
        routes._config_path = orig_path
        routes._config = orig_cfg
        routes._audit_engine = orig_engine


def test_api_works_without_key_when_require_api_key_false(tmp_path):
    """When require_api_key is false/unset, /status works without any key (existing behaviour)."""
    config_yaml = f"""targets: []
report:
  output_dir: {tmp_path}
api:
  port: 8088
sqlite_path: {tmp_path}/audit.db
"""
    config_path = tmp_path / "config.yaml"
    config_path.write_text(config_yaml, encoding="utf-8")

    import api.routes as routes

    orig_path = routes._config_path
    orig_cfg = routes._config
    orig_engine = routes._audit_engine
    try:
        routes._config_path = str(config_path)
        routes._config = None
        routes._audit_engine = None
        client = TestClient(routes.app)
        resp = client.get("/status")
        assert resp.status_code == 200
    finally:
        routes._config_path = orig_path
        routes._config = orig_cfg
        routes._audit_engine = orig_engine
