"""WebAuthn HTML session gate and CSRF (Phase 1b, GitHub #86)."""

from __future__ import annotations

from pathlib import Path

import pytest
import yaml
from fastapi.testclient import TestClient

from core.webauthn_rp.session_cookie import COOKIE_NAME, sign_session
from core.webauthn_rp.settings import user_id_bytes, webauthn_block


@pytest.fixture
def webauthn_gate_client(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
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
api:
  port: 8088
  webauthn:
    enabled: true
    rp_id: localhost
    rp_name: Data Boar Test
    origin: http://testserver
    user_display_name: tester
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


def test_gate_off_when_no_credentials_allows_dashboard(webauthn_gate_client):
    client, _routes = webauthn_gate_client
    r = client.get("/en/", follow_redirects=False)
    assert r.status_code == 200


def test_gate_on_redirects_dashboard_to_login(webauthn_gate_client):
    client, routes_mod = webauthn_gate_client
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
    r = client.get("/en/", follow_redirects=False)
    assert r.status_code == 302
    assert r.headers["location"].startswith("/en/login?next=")


def test_gate_on_allows_help(webauthn_gate_client):
    client, routes_mod = webauthn_gate_client
    cfg = yaml.safe_load(Path(routes_mod._config_path).read_text(encoding="utf-8"))
    wa = webauthn_block(cfg)
    uid = user_id_bytes(wa)
    dbm = routes_mod._get_engine().db_manager
    dbm.webauthn_save_credential(
        user_id=uid,
        credential_id=b"unit-test-credential-id-32bytes!!",
        public_key=b"k" * 64,
        sign_count=0,
    )
    r = client.get("/en/help")
    assert r.status_code == 200


def test_gate_on_allows_login_page(webauthn_gate_client):
    client, routes_mod = webauthn_gate_client
    cfg = yaml.safe_load(Path(routes_mod._config_path).read_text(encoding="utf-8"))
    wa = webauthn_block(cfg)
    uid = user_id_bytes(wa)
    dbm = routes_mod._get_engine().db_manager
    dbm.webauthn_save_credential(
        user_id=uid,
        credential_id=b"unit-test-credential-id-32bytes!!",
        public_key=b"k" * 64,
        sign_count=0,
    )
    r = client.get("/en/login")
    assert r.status_code == 200


def test_gate_on_session_cookie_allows_dashboard(webauthn_gate_client):
    client, routes_mod = webauthn_gate_client
    cfg = yaml.safe_load(Path(routes_mod._config_path).read_text(encoding="utf-8"))
    wa = webauthn_block(cfg)
    uid = user_id_bytes(wa)
    secret = "unit-test-webauthn-secret-min-16"
    dbm = routes_mod._get_engine().db_manager
    dbm.webauthn_save_credential(
        user_id=uid,
        credential_id=b"unit-test-credential-id-32bytes!!",
        public_key=b"k" * 64,
        sign_count=0,
    )
    cookie_val = sign_session(secret, uid)
    client.cookies.set(COOKIE_NAME, cookie_val)
    r = client.get("/en/")
    assert r.status_code == 200


def test_csrf_required_on_config_post_when_gate_on(webauthn_gate_client):
    client, routes_mod = webauthn_gate_client
    cfg = yaml.safe_load(Path(routes_mod._config_path).read_text(encoding="utf-8"))
    wa = webauthn_block(cfg)
    uid = user_id_bytes(wa)
    secret = "unit-test-webauthn-secret-min-16"
    dbm = routes_mod._get_engine().db_manager
    dbm.webauthn_save_credential(
        user_id=uid,
        credential_id=b"unit-test-credential-id-32bytes!!",
        public_key=b"k" * 64,
        sign_count=0,
    )
    cookie_val = sign_session(secret, uid)
    client.cookies.set(COOKIE_NAME, cookie_val)
    r = client.post(
        "/en/config",
        data={"yaml": "targets: []\n"},
    )
    assert r.status_code == 403


# ---------------------------------------------------------------------------
# Regression: post-login open-redirect via ``next=`` (login_next is rendered
# verbatim into ``data-next`` on /static/webauthn-login.js, then assigned to
# ``window.location.href`` after a successful WebAuthn ceremony). Any value
# that the browser resolves to a cross-origin URL would phish the operator
# *after* they tapped their security key, so this gate must be strict.
# ---------------------------------------------------------------------------


def _safe_next_path():
    from api.webauthn_html_gate import safe_next_path

    return safe_next_path


@pytest.mark.parametrize(
    "evil",
    [
        # Protocol-relative URL: browsers resolve //evil.com against the page
        # scheme, so location.href = "//evil.com/x" navigates to https://evil.com/x.
        "//evil.com/x",
        "//attacker.example/admin",
        # Backslash-normalized authority: modern browsers normalize \ to /,
        # so /\evil.com behaves like //evil.com for navigation.
        "/\\evil.com/x",
        "/\\\\evil.com/admin",
        # Absolute URLs and dangerous schemes — covered by previous logic and
        # locked in here so the new code keeps rejecting them.
        "https://evil.com",
        "http://evil.com/",
        "javascript:alert(1)",
        # Embedded control characters can break a downstream URL parser or
        # get stripped by the browser, re-shaping the URL into //evil.com.
        "/\r//evil.com",
        "/\n//evil.com",
        "/\t//evil.com",
        "/\x00x",
    ],
)
def test_safe_next_path_rejects_cross_origin_and_control_chars(evil):
    safe_next_path = _safe_next_path()
    fallback = "/en/"
    assert safe_next_path(evil, fallback) == fallback


@pytest.mark.parametrize(
    "ok",
    [
        "/en/",
        "/en/reports",
        "/en/reports?sort=date_desc",
        "/pt-br/help",
        "/safe/path?with=query&and=fragment#hash",
    ],
)
def test_safe_next_path_allows_same_origin_paths(ok):
    safe_next_path = _safe_next_path()
    assert safe_next_path(ok, "/en/") == ok


def test_safe_next_path_empty_or_long_returns_fallback():
    safe_next_path = _safe_next_path()
    fallback = "/en/"
    assert safe_next_path(None, fallback) == fallback
    assert safe_next_path("", fallback) == fallback
    # Length cap — anything beyond 2048 chars collapses to fallback.
    assert safe_next_path("/" + "a" * 2050, fallback) == fallback
