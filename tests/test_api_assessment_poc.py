"""Gated dashboard route: organizational self-assessment POC placeholder (PLAN_MATURITY_*)."""

from __future__ import annotations

import re
from pathlib import Path

from fastapi.testclient import TestClient

from core.database import LocalDBManager


def _setup_routes(tmp_path: Path, api_extra: str = "", licensing_block: str = ""):
    """Point api.routes at a temp config.yaml. Avoid duplicate YAML ``api:`` keys (merge bugs)."""
    out_dir = str(tmp_path).replace("\\", "/")
    config_yaml = f"""targets: []
report:
  output_dir: {out_dir}
api:
  port: 8088
{api_extra}sqlite_path: {out_dir}/audit_results.db
scan:
  max_workers: 1
{licensing_block}"""
    config_path = tmp_path / "config.yaml"
    config_path.write_text(config_yaml, encoding="utf-8")

    import api.routes as routes

    original_config_path = routes._config_path
    original_config = routes._config
    original_engine = routes._audit_engine
    routes._config_path = str(config_path)
    routes._config = None
    routes._audit_engine = None
    client = TestClient(routes.app)
    return routes, client, original_config_path, original_config, original_engine


def _teardown_routes(routes, original_config_path, original_config, original_engine):
    routes._config_path = original_config_path
    routes._config = original_config
    routes._audit_engine = original_engine
    routes._maturity_pack_cache = None


def test_assessment_placeholder_404_when_flag_off(tmp_path):
    routes, client, orig_path, orig_cfg, orig_engine = _setup_routes(tmp_path)
    try:
        r = client.get("/en/assessment")
        assert r.status_code == 404
    finally:
        _teardown_routes(routes, orig_path, orig_cfg, orig_engine)


def test_assessment_placeholder_200_when_flag_on_open_tier(tmp_path):
    routes, client, orig_path, orig_cfg, orig_engine = _setup_routes(
        tmp_path,
        api_extra="  maturity_self_assessment_poc_enabled: true\n",
    )
    try:
        r = client.get("/en/assessment")
        assert r.status_code == 200
        assert "PLAN_MATURITY_SELF_ASSESSMENT_GRC_QUESTIONNAIRE" in r.text
        r2 = client.get("/pt-br/assessment")
        assert r2.status_code == 200
    finally:
        _teardown_routes(routes, orig_path, orig_cfg, orig_engine)


def test_assessment_placeholder_404_when_community_tier_with_flag(tmp_path):
    routes, client, orig_path, orig_cfg, orig_engine = _setup_routes(
        tmp_path,
        api_extra="  maturity_self_assessment_poc_enabled: true\n",
        licensing_block="licensing:\n  effective_tier: community\n",
    )
    try:
        r = client.get("/en/assessment")
        assert r.status_code == 404
    finally:
        _teardown_routes(routes, orig_path, orig_cfg, orig_engine)


def test_assessment_placeholder_200_when_pro_tier_with_flag(tmp_path):
    routes, client, orig_path, orig_cfg, orig_engine = _setup_routes(
        tmp_path,
        api_extra="  maturity_self_assessment_poc_enabled: true\n",
        licensing_block="licensing:\n  effective_tier: pro\n",
    )
    try:
        r = client.get("/en/assessment")
        assert r.status_code == 200
    finally:
        _teardown_routes(routes, orig_path, orig_cfg, orig_engine)


def test_assessment_post_400_without_pack(tmp_path):
    routes, client, orig_path, orig_cfg, orig_engine = _setup_routes(
        tmp_path,
        api_extra="  maturity_self_assessment_poc_enabled: true\n",
        licensing_block="licensing:\n  effective_tier: pro\n",
    )
    try:
        r = client.post(
            "/en/assessment",
            data={
                "assessment_batch_id": "a" * 32,
                "pack_version": "1",
            },
        )
        assert r.status_code == 400
    finally:
        _teardown_routes(routes, orig_path, orig_cfg, orig_engine)


def test_assessment_post_404_when_community_tier(tmp_path):
    routes, client, orig_path, orig_cfg, orig_engine = _setup_routes(
        tmp_path,
        api_extra="  maturity_self_assessment_poc_enabled: true\n",
        licensing_block="licensing:\n  effective_tier: community\n",
    )
    try:
        r = client.post(
            "/en/assessment",
            data={"assessment_batch_id": "b" * 32},
        )
        assert r.status_code == 404
    finally:
        _teardown_routes(routes, orig_path, orig_cfg, orig_engine)


def test_assessment_post_persists_answers_with_integrity_secret(tmp_path, monkeypatch):
    """When DATA_BOAR_MATURITY_INTEGRITY_SECRET is set, rows get HMAC and /status reports integrity."""
    monkeypatch.setenv("DATA_BOAR_MATURITY_INTEGRITY_SECRET", "poc-test-hmac-key")
    pack_src = (
        Path(__file__).resolve().parent
        / "fixtures"
        / "maturity_assessment"
        / "sample_pack.yaml"
    )
    pack_dst = tmp_path / "pack.yaml"
    pack_dst.write_text(pack_src.read_text(encoding="utf-8"), encoding="utf-8")
    pack_path = str(pack_dst).replace("\\", "/")
    extra = f"""  maturity_self_assessment_poc_enabled: true
  maturity_assessment_pack_path: {pack_path}
"""
    routes, client, orig_path, orig_cfg, orig_engine = _setup_routes(
        tmp_path,
        api_extra=extra,
        licensing_block="licensing:\n  effective_tier: pro\n",
    )
    try:
        r = client.get("/en/assessment")
        assert r.status_code == 200
        m = re.search(r'name="assessment_batch_id" value="([^"]+)"', r.text)
        assert m is not None
        bid = m.group(1)
        r2 = client.post(
            "/en/assessment",
            data={
                "assessment_batch_id": bid,
                "pack_version": "1",
                "answer__sample_dpo": "yes",
                "answer__sample_policy": "no",
            },
            follow_redirects=False,
        )
        assert r2.status_code == 303
        db = LocalDBManager(str(tmp_path / "audit_results.db"))
        try:
            rows = db.maturity_assessment_rows_for_integrity()
            assert len(rows) == 2
            assert all((row.get("row_hmac") or "").strip() for row in rows)
            st = client.get("/status")
            assert st.status_code == 200
            body = st.json()
            assert "maturity_assessment_integrity" in body
            mi = body["maturity_assessment_integrity"]
            assert mi.get("secret_configured") is True
            assert mi.get("rows_ok") == 2
            assert mi.get("rows_mismatch") == 0
        finally:
            db.dispose()
    finally:
        _teardown_routes(routes, orig_path, orig_cfg, orig_engine)


def test_assessment_post_persists_answers(tmp_path):
    pack_src = (
        Path(__file__).resolve().parent
        / "fixtures"
        / "maturity_assessment"
        / "sample_pack.yaml"
    )
    pack_dst = tmp_path / "pack.yaml"
    pack_dst.write_text(pack_src.read_text(encoding="utf-8"), encoding="utf-8")
    pack_path = str(pack_dst).replace("\\", "/")
    extra = f"""  maturity_self_assessment_poc_enabled: true
  maturity_assessment_pack_path: {pack_path}
"""
    routes, client, orig_path, orig_cfg, orig_engine = _setup_routes(
        tmp_path,
        api_extra=extra,
        licensing_block="licensing:\n  effective_tier: pro\n",
    )
    try:
        r = client.get("/en/assessment")
        assert r.status_code == 200
        m = re.search(r'name="assessment_batch_id" value="([^"]+)"', r.text)
        assert m is not None
        bid = m.group(1)
        r2 = client.post(
            "/en/assessment",
            data={
                "assessment_batch_id": bid,
                "pack_version": "1",
                "answer__sample_dpo": "yes",
                "answer__sample_policy": "no",
            },
            follow_redirects=False,
        )
        assert r2.status_code == 303
        assert "saved=1" in (r2.headers.get("location") or "")
        db = LocalDBManager(str(tmp_path / "audit_results.db"))
        try:
            assert db.count_maturity_assessment_answers() == 2
        finally:
            db.dispose()
    finally:
        _teardown_routes(routes, orig_path, orig_cfg, orig_engine)


def test_assessment_renders_yaml_pack_when_configured(tmp_path):
    pack_src = (
        Path(__file__).resolve().parent
        / "fixtures"
        / "maturity_assessment"
        / "sample_pack.yaml"
    )
    pack_dst = tmp_path / "pack.yaml"
    pack_dst.write_text(pack_src.read_text(encoding="utf-8"), encoding="utf-8")
    pack_path = str(pack_dst).replace("\\", "/")
    extra = f"""  maturity_self_assessment_poc_enabled: true
  maturity_assessment_pack_path: {pack_path}
"""
    routes, client, orig_path, orig_cfg, orig_engine = _setup_routes(
        tmp_path, api_extra=extra
    )
    try:
        r = client.get("/en/assessment")
        assert r.status_code == 200
        assert "Governance (sample)" in r.text
        assert "privacy governance" in r.text.lower()
    finally:
        _teardown_routes(routes, orig_path, orig_cfg, orig_engine)
