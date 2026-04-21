"""RBAC (GitHub #86 Phase 2): opt-in api.rbac + Pro tier gate."""

from __future__ import annotations

from pathlib import Path

import pytest
import yaml
from fastapi.testclient import TestClient

from core.rbac_settings import rbac_enforcement_active
from core.webauthn_rp.session_cookie import sign_session
from core.webauthn_rp.settings import user_id_bytes, webauthn_block


@pytest.fixture
def rbac_pro_client(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv(
        "DATA_BOAR_WEBAUTHN_TOKEN_SECRET", "unit-test-webauthn-secret-min-16"
    )
    cfg = tmp_path / "config.yaml"
    db = tmp_path / "audit.db"
    cfg.write_text(
        f"""targets: []
report:
  output_dir: {tmp_path}
sqlite_path: {db}
licensing:
  effective_tier: pro
api:
  port: 8088
  api_key: test-secret-key
  webauthn:
    enabled: true
    rp_id: localhost
    rp_name: Data Boar Test
    origin: http://testserver
    user_display_name: tester
  rbac:
    enabled: true
    api_key_roles:
      - dashboard
    default_roles:
      - dashboard
      - scanner
      - reports_reader
      - config_admin
scan:
  max_workers: 1
""",
        encoding="utf-8",
    )
    import api.routes as routes

    prev_path = routes._config_path
    prev_cfg = routes._config
    prev_eng = routes._audit_engine
    routes._config_path = str(cfg)
    routes._config = None
    routes._audit_engine = None
    client = TestClient(routes.app)
    yield client, routes
    routes._config_path = prev_path
    routes._config = prev_cfg
    routes._audit_engine = prev_eng
    monkeypatch.delenv("DATA_BOAR_WEBAUTHN_TOKEN_SECRET", raising=False)


def test_rbac_enforcement_active_requires_tier_and_flag():
    assert not rbac_enforcement_active(
        {
            "api": {"rbac": {"enabled": True}},
            "licensing": {"effective_tier": "community"},
        }
    )
    assert rbac_enforcement_active(
        {"api": {"rbac": {"enabled": True}}, "licensing": {"effective_tier": "pro"}}
    )


def test_rbac_401_without_principal_on_protected_route(rbac_pro_client):
    client, _ = rbac_pro_client
    r = client.get("/status")
    assert r.status_code == 401


def test_rbac_api_key_dashboard_allows_status_forbids_report(rbac_pro_client):
    client, _ = rbac_pro_client
    h = {"X-API-Key": "test-secret-key"}
    assert client.get("/status", headers=h).status_code == 200
    assert client.get("/report", headers=h).status_code == 403


def test_rbac_community_yaml_enabled_does_not_enforce(tmp_path: Path, monkeypatch):
    """Tier blocks dashboard_rbac: middleware is a no-op (OPEN behaviour without RBAC)."""
    monkeypatch.setenv(
        "DATA_BOAR_WEBAUTHN_TOKEN_SECRET", "unit-test-webauthn-secret-min-16"
    )
    cfg = tmp_path / "config.yaml"
    db = tmp_path / "audit.db"
    cfg.write_text(
        f"""targets: []
report:
  output_dir: {tmp_path}
sqlite_path: {db}
licensing:
  effective_tier: community
api:
  port: 8088
  rbac:
    enabled: true
scan:
  max_workers: 1
""",
        encoding="utf-8",
    )
    import api.routes as routes

    prev_path = routes._config_path
    prev_cfg = routes._config
    prev_eng = routes._audit_engine
    routes._config_path = str(cfg)
    routes._config = None
    routes._audit_engine = None
    client = TestClient(routes.app)
    try:
        assert client.get("/status").status_code == 200
    finally:
        routes._config_path = prev_path
        routes._config = prev_cfg
        routes._audit_engine = prev_eng


def test_rbac_webauthn_session_roles_json_reports_only(rbac_pro_client):
    client, routes_mod = rbac_pro_client
    cfg = yaml.safe_load(Path(routes_mod._config_path).read_text(encoding="utf-8"))
    wa = webauthn_block(cfg)
    assert wa is not None
    uid = user_id_bytes(wa)
    dbm = routes_mod._get_engine().db_manager
    dbm.webauthn_save_credential(
        user_id=uid,
        credential_id=b"unit-test-credential-id-32bytes!!",
        public_key=b"k" * 64,
        sign_count=0,
    )
    from core.database import WebAuthnCredential

    sess = dbm._session_factory()
    try:
        row = (
            sess.query(WebAuthnCredential)
            .filter(WebAuthnCredential.user_id == uid[:64])
            .one()
        )
        row.roles_json = '["reports_reader"]'
        sess.commit()
    finally:
        sess.close()

    secret = "unit-test-webauthn-secret-min-16"
    cookie = sign_session(secret, uid)
    client.cookies.set("db_webauthn", cookie)

    assert client.get("/en/reports").status_code == 200
    assert client.get("/en/").status_code == 403
