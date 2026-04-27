"""
Unit tests for ``core.licensing.feature_gate``.

The facade is the single entry point new code should use to ask "is this
capability allowed for the current process?". Tests here exercise:

* OPEN tier (community / lab default) — everything is allowed.
* Tier ladder — a Pro tier sees Pro features but not Enterprise ones.
* License state interaction — a tier resolved to non-OPEN, but with a
  ``LicenseGuard`` state outside ``OPEN/VALID/GRACE``, must deny.
* ``require_feature`` raises with the structured decision attached.
* ``snapshot_gate_state`` returns a JSON-friendly shape.

These tests deliberately avoid touching JWT signing, manifest verification,
or sampling SQL — they only confirm the wiring contract documented in
``feature_gate.py`` and ``DEFENSIVE_SCANNING_MANIFESTO.md`` (the gate must
not change sampling caps; it only chooses *which* ingredient is offered).
"""

from __future__ import annotations

import pytest

from core.licensing import (
    FeatureGateDecision,
    FeatureNotAvailableError,
    evaluate_feature,
    is_feature_enabled,
    require_feature,
    reset_license_guard_for_tests,
    snapshot_gate_state,
)
from core.licensing.tier_features import Tier


@pytest.fixture(autouse=True)
def _reset_license_guard_between_tests():
    reset_license_guard_for_tests()
    yield
    reset_license_guard_for_tests()


def _open_cfg() -> dict:
    return {"licensing": {"mode": "open", "effective_tier": ""}}


def _tier_cfg(tier: str) -> dict:
    return {"licensing": {"mode": "open", "effective_tier": tier}}


# ---------------------------------------------------------------------------
# OPEN tier — community default. Manifesto: forks and academic use must keep
# working until the operator explicitly opts into enforcement.
# ---------------------------------------------------------------------------


def test_open_mode_allows_every_registered_feature():
    cfg = _open_cfg()
    for feat in ("scan_filesystem", "report_pdf", "connector_mainframe", "siem_export"):
        decision = evaluate_feature(feat, cfg)
        assert decision.allowed is True
        assert decision.current_tier == Tier.OPEN
        assert decision.reason == "open_mode_enforcement_disabled"


def test_is_feature_enabled_open_mode_is_true():
    assert is_feature_enabled("connector_mainframe", _open_cfg()) is True


# ---------------------------------------------------------------------------
# Tier ladder — confirms the gate respects Community < Pro < Enterprise.
# ---------------------------------------------------------------------------


def test_pro_tier_allows_pro_feature_and_blocks_enterprise():
    cfg = _tier_cfg("pro")

    pro_decision = evaluate_feature("audit_log_advanced", cfg)
    assert pro_decision.allowed is True
    assert pro_decision.current_tier == Tier.PRO
    assert pro_decision.required_tier == Tier.PRO
    assert pro_decision.reason == "tier_meets_requirement"

    ent_decision = evaluate_feature("connector_mainframe", cfg)
    assert ent_decision.allowed is False
    assert ent_decision.current_tier == Tier.PRO
    assert ent_decision.required_tier == Tier.ENTERPRISE
    assert ent_decision.reason == "tier_below_required"


def test_community_tier_blocks_pro_and_enterprise_features():
    cfg = _tier_cfg("community")
    for feat in ("audit_log_advanced", "connector_mainframe", "siem_export"):
        decision = evaluate_feature(feat, cfg)
        assert decision.allowed is False
        assert decision.current_tier == Tier.COMMUNITY


def test_enterprise_tier_unlocks_enterprise_features():
    cfg = _tier_cfg("enterprise")
    for feat in ("connector_mainframe", "high_frequency_sampling", "siem_export"):
        decision = evaluate_feature(feat, cfg)
        assert decision.allowed is True
        assert decision.current_tier == Tier.ENTERPRISE


# ---------------------------------------------------------------------------
# Unregistered features fall back to community-tier requirement (registry
# default in ``tier_features.get_required_tier``). The gate still records an
# explicit reason so audit consumers can flag drift.
# ---------------------------------------------------------------------------


def test_unregistered_feature_in_pro_tier_is_allowed_with_explicit_reason():
    cfg = _tier_cfg("pro")
    decision = evaluate_feature("totally_made_up_feature", cfg)
    assert decision.allowed is True
    assert decision.required_tier == Tier.COMMUNITY
    assert decision.reason == "feature_not_registered_default_community"


# ---------------------------------------------------------------------------
# require_feature: error path must carry the structured decision so callers
# can re-emit it in API responses / CLI exit messages without re-evaluating.
# ---------------------------------------------------------------------------


def test_require_feature_raises_with_structured_decision():
    cfg = _tier_cfg("pro")
    with pytest.raises(FeatureNotAvailableError) as excinfo:
        require_feature("connector_mainframe", cfg)
    assert isinstance(excinfo.value.decision, FeatureGateDecision)
    assert excinfo.value.decision.feature == "connector_mainframe"
    assert excinfo.value.decision.allowed is False
    assert excinfo.value.decision.required_tier == Tier.ENTERPRISE


def test_require_feature_returns_decision_when_allowed():
    cfg = _tier_cfg("enterprise")
    decision = require_feature("high_frequency_sampling", cfg)
    assert decision.allowed is True
    assert decision.feature == "high_frequency_sampling"


# ---------------------------------------------------------------------------
# Snapshot shape — used by /status and dashboard banners.
# ---------------------------------------------------------------------------


def test_snapshot_gate_state_pro_tier_subset():
    cfg = _tier_cfg("pro")
    snap = snapshot_gate_state(
        cfg,
        features=["scan_filesystem", "audit_log_advanced", "connector_mainframe"],
    )
    assert snap["current_tier"] == "pro"
    assert snap["open_mode"] is False
    assert snap["feature_count"] == 3
    by_name = {entry["feature"]: entry for entry in snap["features"]}
    assert by_name["scan_filesystem"]["allowed"] is True
    assert by_name["audit_log_advanced"]["allowed"] is True
    assert by_name["connector_mainframe"]["allowed"] is False


def test_snapshot_gate_state_full_registry_in_open_mode_allows_all():
    snap = snapshot_gate_state(_open_cfg())
    assert snap["current_tier"] == "open"
    assert snap["open_mode"] is True
    assert all(entry["allowed"] for entry in snap["features"])


# ---------------------------------------------------------------------------
# Audit-friendly serialization: every decision must round-trip through
# ``to_audit_dict`` so log consumers (core/scan_audit_log.py) can store it.
# ---------------------------------------------------------------------------


def test_decision_to_audit_dict_is_json_friendly():
    cfg = _tier_cfg("pro")
    decision = evaluate_feature("connector_mainframe", cfg)
    payload = decision.to_audit_dict()
    assert payload == {
        "feature": "connector_mainframe",
        "allowed": False,
        "current_tier": "pro",
        "required_tier": "enterprise",
        "license_state": "OPEN",
        "reason": "tier_below_required",
    }
