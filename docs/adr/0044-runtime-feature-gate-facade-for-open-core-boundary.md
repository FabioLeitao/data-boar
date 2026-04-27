# ADR 0044: Runtime feature-gate facade for the open-core boundary

**Status:** Accepted
**Date:** 2026-04-27

## Context

The repository already had three pieces of the open-core boundary in place
(see [ADR 0027](0027-commercial-tier-boundaries-licensing-docs-and-future-jwt-claims.md)):

- [`core/licensing/tier_features.py`](../../core/licensing/tier_features.py) — the
  registry mapping each named feature to a minimum
  [`Tier`](../../core/licensing/tier_features.py).
- [`core/licensing/runtime_feature_tier.py`](../../core/licensing/runtime_feature_tier.py)
  — resolves the *effective* tier for the running process from the JWT
  `dbtier` claim or the YAML `licensing.effective_tier` fallback.
- [`core/licensing/guard.py`](../../core/licensing/guard.py) — the license state
  machine (`OPEN` / `VALID` / `GRACE` / `EXPIRED` / `REVOKED` / …).

Callers that wanted to gate a code path had to wire all three by hand. That
made the boundary easy to forget, and it pushed each call site to invent its
own "what reason do I log when access is denied?" answer. The
[Slack architectural-segregation mission](../ops/inspirations/INSPIRATIONS_HUB.md)
called out concrete premium capabilities that did not yet have a single,
auditable gate (mainframe / SAP HR connectors, high-frequency sampling,
advanced audit log, SIEM export).

## Decision

1. Add **`core/licensing/feature_gate.py`** as the single runtime entry point
   for "may I do this?" questions. It exposes:
   - `evaluate_feature(name, config) -> FeatureGateDecision`
   - `is_feature_enabled(name, config) -> bool`
   - `require_feature(name, config) -> FeatureGateDecision`
     (raises `FeatureNotAvailableError` carrying the structured decision)
   - `snapshot_gate_state(config, features=...)` for `/status` consumers.
2. Wire the facade through the existing `LicenseGuard` singleton so the
   default community / lab posture is preserved: `Tier.OPEN` allows every
   registered feature, exactly as the
   [LICENSING_OPEN_CORE_AND_COMMERCIAL.md](../LICENSING_OPEN_CORE_AND_COMMERCIAL.md)
   contract promises ("forks and academic use keep working").
3. Register the premium feature names called out by the architectural
   mission (`connector_mainframe`, `connector_sap_hr_totvs_rm`,
   `high_frequency_sampling`, `audit_log_advanced`, `siem_export`,
   `report_pdf_export`) in `tier_features.py` so the registry is the single
   source of truth.
4. Every denial returns a structured `FeatureGateDecision` with a factual
   `reason` (`tier_below_required`, `license_state_not_allowed`,
   `feature_not_registered_default_community`, …). Callers are expected to
   surface that reason through `core/scan_audit_log.py` instead of swallowing
   the decision — the same posture as
   [`THE_ART_OF_THE_FALLBACK.md`](../ops/inspirations/THE_ART_OF_THE_FALLBACK.md)
   §3 ("never falls through to a weaker level silently").

## Consequences

- **Positive:** New code that needs to gate an Enterprise / Pro capability
  has exactly one call to make (`require_feature`). The structured
  `FeatureGateDecision` is JSON-friendly so audit, API, and dashboard
  consumers share the same shape.
- **Positive (Defensive Scanning Manifesto):** the gate **never** changes
  sampling caps, statement timeouts, or the `WITH (NOLOCK)` posture in
  `connectors/sql_sampling.py`. It only decides whether the *more expensive*
  ingredient (e.g. the high-frequency sampling profile) is offered to the
  operator. Hard ceilings still clamp every read.
- **Negative:** Adding a new monetisable capability now requires an entry in
  the registry **and** a `require_feature` call site. That is the cost of
  having one auditable boundary instead of three.
- **Watch:** When JWT `dbfeatures` per-claim allowlists ship
  ([`LICENSING_SPEC.md`](../LICENSING_SPEC.md) future extensions), update
  the facade to consult them in addition to `dbtier` — the
  `FeatureGateDecision` shape was designed so the new reason
  (e.g. `feature_not_in_dbfeatures_claim`) drops in without breaking
  consumers.

## References

- [`core/licensing/feature_gate.py`](../../core/licensing/feature_gate.py)
- [`core/licensing/tier_features.py`](../../core/licensing/tier_features.py)
- [`core/licensing/runtime_feature_tier.py`](../../core/licensing/runtime_feature_tier.py)
- [`tests/test_feature_gate.py`](../../tests/test_feature_gate.py)
- [`docs/LICENSING_OPEN_CORE_AND_COMMERCIAL.md`](../LICENSING_OPEN_CORE_AND_COMMERCIAL.md)
- [`docs/LICENSING_SPEC.md`](../LICENSING_SPEC.md)
- [`docs/plans/PLAN_PRODUCT_TIERS_AND_OPEN_CORE.md`](../plans/PLAN_PRODUCT_TIERS_AND_OPEN_CORE.md)
- [`docs/ops/inspirations/DEFENSIVE_SCANNING_MANIFESTO.md`](../ops/inspirations/DEFENSIVE_SCANNING_MANIFESTO.md)
- [`docs/ops/inspirations/THE_ART_OF_THE_FALLBACK.md`](../ops/inspirations/THE_ART_OF_THE_FALLBACK.md)
- [ADR 0027 — Commercial tier boundaries (licensing docs and future JWT claims)](0027-commercial-tier-boundaries-licensing-docs-and-future-jwt-claims.md)
