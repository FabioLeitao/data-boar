"""
feature_gate.py
================
Unified runtime feature-gate facade for Data Boar (open-core boundary).

Why this module exists
----------------------
Before this facade, three things lived in three places:

* :mod:`core.licensing.tier_features` — the **registry** (feature -> minimum
  :class:`~core.licensing.tier_features.Tier`).
* :mod:`core.licensing.runtime_feature_tier` — **how** to resolve the effective
  :class:`Tier` for the running process (JWT ``dbtier`` vs YAML
  ``licensing.effective_tier`` vs default ``OPEN``).
* :mod:`core.licensing.guard` — the **license state machine** (``OPEN`` /
  ``VALID`` / ``GRACE`` / ``EXPIRED`` / ``REVOKED`` / …).

Callers that wanted to gate a code path had to wire all three by hand, which
made the open-core boundary easy to forget. This module is the single line
new code should call when it asks "may I do this?".

Doctrinal alignment
-------------------
* **Defensive scanning manifesto** (`docs/ops/inspirations/DEFENSIVE_SCANNING_MANIFESTO.md`):
  this gate **never** changes sampling caps, statement timeouts, or
  ``WITH (NOLOCK)`` posture. It only decides whether the *more expensive*
  ingredient (e.g. high-frequency sampling profile) is offered to the operator.
  Hard ceilings in :mod:`connectors.sql_sampling` still clamp every read.
* **The art of the fallback** (`docs/ops/inspirations/THE_ART_OF_THE_FALLBACK.md`):
  every denial returns a structured :class:`FeatureGateDecision` with a
  factual ``reason`` (e.g. ``"tier_below_required"``,
  ``"license_state_invalid"``). Callers are expected to surface that reason
  through :mod:`core.scan_audit_log`, not swallow it.

Default posture
---------------
When :class:`~core.licensing.tier_features.Tier.OPEN` is resolved (lab /
unlicensed development — the **community default**) every registered feature
is **allowed**. Enforcement only kicks in once an operator opts into
``licensing.mode: enforced`` *and* presents a JWT with a non-empty ``dbtier``
claim, or sets ``licensing.effective_tier`` in YAML. This preserves the
"forks and academic use keep working" contract from
``docs/LICENSING_OPEN_CORE_AND_COMMERCIAL.md``.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from core.licensing.guard import get_license_guard
from core.licensing.runtime_feature_tier import get_runtime_tier_for_features
from core.licensing.tier_features import (
    FEATURE_TIER_MAP,
    Tier,
    get_required_tier,
    is_feature_available,
)

__all__ = [
    "FeatureGateDecision",
    "FeatureNotAvailableError",
    "evaluate_feature",
    "is_feature_enabled",
    "require_feature",
    "snapshot_gate_state",
]


# License states under which feature gating is meaningful. ``OPEN`` is the
# explicit "enforcement off" state and is treated as allow-all elsewhere.
_ALLOWED_LICENSE_STATES_FOR_GATING: frozenset[str] = frozenset(
    {"OPEN", "VALID", "GRACE"}
)


@dataclass(frozen=True)
class FeatureGateDecision:
    """
    Structured result of a gate evaluation.

    ``allowed`` is the only field callers should branch on. The other fields
    exist so audit logs and dashboards can explain *why* without re-deriving
    the answer (manifesto §3 of THE_ART_OF_THE_FALLBACK).
    """

    feature: str
    allowed: bool
    current_tier: Tier
    required_tier: Tier
    license_state: str
    reason: str

    def to_audit_dict(self) -> dict[str, Any]:
        """JSON-friendly shape for ``core/scan_audit_log.py`` consumers."""
        return {
            "feature": self.feature,
            "allowed": self.allowed,
            "current_tier": self.current_tier.value,
            "required_tier": self.required_tier.value,
            "license_state": self.license_state,
            "reason": self.reason,
        }


class FeatureNotAvailableError(RuntimeError):
    """
    Raised by :func:`require_feature` when a gated capability is requested but
    the resolved tier or license state forbids it.

    Carries the structured :class:`FeatureGateDecision` for callers that want
    to surface it through their own error path (API response, CLI exit code).
    """

    def __init__(self, decision: FeatureGateDecision) -> None:
        self.decision = decision
        msg = (
            f"feature '{decision.feature}' requires tier "
            f"'{decision.required_tier.value}', current tier is "
            f"'{decision.current_tier.value}' "
            f"(license_state={decision.license_state}, reason={decision.reason})"
        )
        super().__init__(msg)


def _coerce_config(config: dict[str, Any] | None) -> dict[str, Any]:
    return config if isinstance(config, dict) else {}


def evaluate_feature(
    feature: str,
    config: dict[str, Any] | None = None,
) -> FeatureGateDecision:
    """
    Resolve the effective :class:`Tier` and license state and decide whether
    ``feature`` is currently enabled.

    The function is **pure with respect to side effects**: it does not log,
    raise, or mutate state. Logging is a caller responsibility so the gate
    can be evaluated from low-noise paths (e.g. ``/status`` snapshots, UI
    bootstrap) without flooding the audit trail.
    """
    cfg = _coerce_config(config)
    current_tier = get_runtime_tier_for_features(cfg)
    required_tier = get_required_tier(feature)

    license_state = "UNKNOWN"
    try:
        guard = get_license_guard(cfg)
        license_state = guard.context.state or "UNKNOWN"
    except Exception:
        # Singleton init must not break gate evaluation; degrade to UNKNOWN
        # and let the OPEN-tier branch below decide. This matches the
        # "do not silently fail" rule: callers see ``UNKNOWN`` in the audit
        # snapshot and can investigate.
        license_state = "UNKNOWN"

    # OPEN tier is the community default; enforcement off => allow all.
    if current_tier == Tier.OPEN:
        return FeatureGateDecision(
            feature=feature,
            allowed=True,
            current_tier=current_tier,
            required_tier=required_tier,
            license_state=license_state,
            reason="open_mode_enforcement_disabled",
        )

    # An unknown / not-registered feature is treated as COMMUNITY by the
    # registry (see ``tier_features.get_required_tier``). The decision below
    # still goes through the same checks, so unregistered features end up
    # allowed for COMMUNITY+ and denied for hypothetical sub-community tiers
    # (none today).
    if feature not in FEATURE_TIER_MAP:
        # Be explicit so audit consumers can flag unknown feature names.
        unregistered_decision_reason = "feature_not_registered_default_community"
    else:
        unregistered_decision_reason = ""

    if license_state not in _ALLOWED_LICENSE_STATES_FOR_GATING:
        return FeatureGateDecision(
            feature=feature,
            allowed=False,
            current_tier=current_tier,
            required_tier=required_tier,
            license_state=license_state,
            reason="license_state_not_allowed",
        )

    allowed = is_feature_available(feature, current_tier)
    if allowed:
        reason = unregistered_decision_reason or "tier_meets_requirement"
    else:
        reason = "tier_below_required"

    return FeatureGateDecision(
        feature=feature,
        allowed=allowed,
        current_tier=current_tier,
        required_tier=required_tier,
        license_state=license_state,
        reason=reason,
    )


def is_feature_enabled(
    feature: str,
    config: dict[str, Any] | None = None,
) -> bool:
    """Boolean shortcut for callers that only need the yes/no decision."""
    return evaluate_feature(feature, config).allowed


def require_feature(
    feature: str,
    config: dict[str, Any] | None = None,
) -> FeatureGateDecision:
    """
    Assert that ``feature`` is enabled or raise :class:`FeatureNotAvailableError`.

    Use this from code paths where execution **must not** continue when the
    capability is gated (e.g. instantiating an Enterprise-only connector).
    Returns the :class:`FeatureGateDecision` on success so callers can still
    log the allowed path for completeness.
    """
    decision = evaluate_feature(feature, config)
    if not decision.allowed:
        raise FeatureNotAvailableError(decision)
    return decision


def snapshot_gate_state(
    config: dict[str, Any] | None = None,
    features: list[str] | None = None,
) -> dict[str, Any]:
    """
    Return a JSON-friendly snapshot of the gate for ``/status`` / dashboards.

    Mirrors the shape used by :mod:`core.enterprise_surface_posture`: a single
    object that pairs license state, resolved tier, and per-feature decisions
    for the requested feature list. When ``features`` is ``None``, all
    registered feature names are evaluated.
    """
    cfg = _coerce_config(config)
    feature_names = list(features) if features else sorted(FEATURE_TIER_MAP.keys())
    current_tier = get_runtime_tier_for_features(cfg)
    license_state = "UNKNOWN"
    try:
        guard = get_license_guard(cfg)
        license_state = guard.context.state or "UNKNOWN"
    except Exception:
        license_state = "UNKNOWN"

    decisions = [evaluate_feature(name, cfg).to_audit_dict() for name in feature_names]
    return {
        "current_tier": current_tier.value,
        "license_state": license_state,
        "open_mode": current_tier == Tier.OPEN,
        "feature_count": len(decisions),
        "features": decisions,
    }
