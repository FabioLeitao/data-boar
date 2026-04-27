"""
Resolve effective product tier for feature gating (YAML ``licensing.effective_tier``, JWT ``dbtier``).

Shared by API routes, RBAC, and maturity POC so tier logic stays in one place.
"""

from __future__ import annotations

from typing import Any

from core.licensing.tier_features import Tier


def map_dbtier_string_to_tier(raw: str) -> Tier:
    """Map JWT ``dbtier`` / lab ``effective_tier`` strings to :class:`Tier`."""
    r = raw.strip().lower()
    if not r:
        return Tier.OPEN
    if r in ("enterprise", "ent"):
        return Tier.ENTERPRISE
    if r in ("pro", "professional", "consultant", "partner", "trial"):
        return Tier.PRO
    if r in ("community", "standard", "oss", "open_core"):
        return Tier.COMMUNITY
    return Tier.COMMUNITY


def get_runtime_tier_for_features(cfg: dict[str, Any]) -> Tier:
    """
    Resolve tier for ``is_feature_available``: JWT ``dbtier`` when enforced and VALID/GRACE wins over
    ``licensing.effective_tier``; otherwise lab YAML; default OPEN (all features on).
    """
    dbtier_claim = ""
    try:
        from core.licensing.guard import get_license_guard

        g = get_license_guard(cfg)
        c = g.context
        if c.state in ("VALID", "GRACE"):
            dbtier_claim = str(getattr(c, "dbtier", "") or "").strip().lower()
    # Optional license claim parsing; missing field falls back to default tier.
    except Exception:
        pass  # nosec B110
    lc = cfg.get("licensing") if isinstance(cfg.get("licensing"), dict) else {}
    yaml_tier = str(lc.get("effective_tier") or "").strip().lower()
    if dbtier_claim:
        return map_dbtier_string_to_tier(dbtier_claim)
    if yaml_tier:
        return map_dbtier_string_to_tier(yaml_tier)
    return Tier.OPEN
