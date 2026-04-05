# Plan: Quasi-identification composite risk (IP + geolocation + breadcrumbs)

<!-- plans-hub-summary: Add configurable composite-risk detection for quasi-identification in logs/proxy traces (IP+geo+breadcrumbs), with LGPD-first guardrails and safe default behavior. -->
<!-- plans-hub-related: PLAN_ADDITIONAL_DETECTION_TECHNIQUES_AND_FN_REDUCTION.md, PLAN_READINESS_AND_OPERATIONS.md, PLAN_COMPLIANCE_STANDARDS_ALIGNMENT.md -->

## Status

Proposed (implementation-ready specification).

## Why this exists

Isolated fields like CEP, IP, municipality, user-agent, and route path can look "generic". Combined, they may become identifying or strongly re-identifying in operational logs (reverse proxy + app access + query breadcrumbs). This plan defines a safe, configurable detection path for this composite risk.

## Scope

In scope:

- Composite-risk scoring for quasi-identification signals in logs and sampled text.
- LGPD-oriented guardrails (minimization, purpose limitation, controlled enrichment).
- Report output for "possible deanonymization risk" with explainable factors.
- Optional runtime enrichment controls (off by default).

Out of scope:

- Full SIEM replacement.
- Automated punitive actions or user blocking.
- Persistent storage of enriched personal data beyond current retention policy.

## Threat model (practical)

Risk pattern:

1. Public/semi-public log fields are collected (`ip`, `x-forwarded-for`, URL/query, headers, timestamp).
2. Location breadcrumbs appear (`cep`, municipality, neighborhood, state).
3. Extra context appears (path suggests residential context, route purpose, repeated session behavior).
4. Combined entropy becomes high enough to point to a household or individual.

## Detection model (composite score)

### Signals and base weights

Each detected signal contributes points to a per-record or per-group score:

| Signal | Weight |
| --- | ---: |
| Raw IP present (IPv4/IPv6) | 20 |
| IP + precise timestamp pair | 10 |
| CEP detected | 15 |
| Municipality detected | 10 |
| Neighborhood detected | 10 |
| Street/logradouro token | 15 |
| House/building number token | 10 |
| High-entropy user-agent/device hint | 10 |
| Sensitive route breadcrumb (auth/account/profile/report-download) | 10 |
| Cross-source correlation present (proxy + app log/session id) | 15 |

### Synergy boosts (when combinations occur)

| Combination | Extra points |
| --- | ---: |
| IP + CEP | +10 |
| CEP + municipality + neighborhood | +15 |
| Address tokens + route breadcrumb | +10 |
| Cross-source correlation + any location trio | +10 |

### Thresholds

| Final score | Risk label | Action |
| ---: | --- | --- |
| 0-34 | LOW | Keep normal handling; no enrichment. |
| 35-64 | MEDIUM | Flag "suggested review"; redact output fields in report preview. |
| 65-100 | HIGH | Flag "possible deanonymization risk"; enforce strict redaction and operator review cue. |

Notes:

- Scores are explainable (store which signals fired).
- Thresholds must be configurable to adapt to deployment risk appetite.

## Proposed config keys

Add under detection/config namespace (default-safe):

- `sensitivity_detection.quasi_identification.enabled: true`
- `sensitivity_detection.quasi_identification.score_medium_threshold: 35`
- `sensitivity_detection.quasi_identification.score_high_threshold: 65`
- `sensitivity_detection.quasi_identification.enable_online_enrichment: false`
- `sensitivity_detection.quasi_identification.online_enrichment_provider: ""`
- `sensitivity_detection.quasi_identification.persist_enrichment: false`
- `sensitivity_detection.quasi_identification.max_enrichment_lookups_per_run: 10`
- `sensitivity_detection.quasi_identification.redact_ip_to_prefix: true`
- `sensitivity_detection.quasi_identification.ipv4_prefix_mask: 24`
- `sensitivity_detection.quasi_identification.ipv6_prefix_mask: 48`

## LGPD guardrails (non-negotiable defaults)

1. **Data minimization first:** store masked IP prefixes by default in reports, not full IP.
2. **Local-first inference:** run regex/correlation locally before any outbound lookup.
3. **External enrichment opt-in only:** disabled by default; explicit config required.
4. **Purpose limitation:** enrichment only for compliance-risk analysis path, never for profiling users.
5. **No silent persistence:** enriched fields are ephemeral unless explicit retention policy allows.
6. **Auditability:** log enrichment attempts as metadata (count/provider/outcome), not full queried payload.
7. **Bounded lookups:** hard cap per run to prevent data exfiltration patterns.
8. **Human confirmation for HIGH:** output "possible" language and require operator review.

## Implementation slices (token-aware)

1. **Slice A - Schema + scoring core**
   - Add score calculator module with explainable factors.
   - Unit tests for score math, thresholds, and synergy rules.
2. **Slice B - Log extraction hooks**
   - Parse proxy/app breadcrumbs from existing scan inputs.
   - Normalize IP, CEP, municipality, neighborhood tokens.
3. **Slice C - Report integration**
   - Add row/section for composite quasi-identification risk.
   - Show factors + risk label + redacted output.
4. **Slice D - Guardrails and config**
   - Wire config flags and safe defaults.
   - Enforce max lookup limits and disabled-by-default enrichment.
5. **Slice E - Optional enrichment adapter**
   - Interface for external lookup provider (provider-agnostic).
   - Keep behind explicit opt-in and rate caps.
6. **Slice F - Docs + operator runbook**
   - Update `docs/SENSITIVITY_DETECTION.md` and relevant ops docs.
   - Include LGPD caveats and deployment-safe examples.

## Test strategy

- Unit tests: score calculation and threshold transitions.
- Fixture tests: synthetic log bundles with known low/medium/high cases.
- Regression tests: behavior unchanged when feature is disabled.
- Safety tests: no outbound enrichment calls when disabled.

## Sequencing recommendation

Near-term recommended order:

1. Slice A (core scoring)
2. Slice C (report visibility)
3. Slice D (guardrails + config)
4. Slice B (broader extraction)
5. Slice E (optional enrichment, only if justified)
6. Slice F (docs hardening and examples)

## Fit with Priority Matrix / PRINCE2 / Kanban

### Priority-matrix fit

- Fits current detection-depth lane (`What to start next` order **3a** in `PLANS_TODO`).
- Not a blocker for Priority band A unless an incident/regulatory request elevates urgency.
- Works as a focused vertical without forcing architecture churn in unrelated plans.

### PRINCE2-style stage control (scaled)

- **Time tolerance:** 1 daily slice (60-120 min) per session.
- **Scope tolerance:** one micro-deliverable only (e.g., score math OR report row OR one test cluster).
- **Quality tolerance:** tests green + docs delta for each merged slice.

### Kanban fit

- Keep one primary feature in `In progress` (this theme can occupy S2 detection depth).
- Move through: `Backlog -> Selected -> In progress -> Done` per slice.
- If interrupted by critical hygiene/security work, park this theme back in `Backlog` with next-step note.

## Daily-slice viability (example breakdown)

Each item below is intentionally small enough for one session:

1. Add score constants + score function skeleton.
2. Add 6-8 unit tests for thresholds/synergies.
3. Add factor-explanation payload (`fired_signals`) to score result.
4. Add report column/section for quasi-identification label.
5. Add redaction helper for IP prefixes and tests.
6. Wire config keys and default-safe behavior.
7. Add feature-off regression test.
8. Add docs snippet in `SENSITIVITY_DETECTION.md`.

## Subscription / licensing tier fit (open-core / pro / enterprise)

This section describes recommended packaging. Runtime claim enforcement remains governed by `LICENSING_SPEC.md`.

| Tier | Recommended quasi-identification capability |
| --- | --- |
| **Open-core** | Local composite scoring + LOW/MEDIUM/HIGH labels + explainable factors + redacted report output. No online enrichment. |
| **Pro** | Open-core + stronger cross-source correlation helpers and richer operator review cues (still local-first; enrichment off by default). |
| **Enterprise** | Pro + optional enrichment adapter under explicit opt-in + bounded lookup/audit controls + stricter policy knobs for governance teams. |

Guardrail remains for all tiers:

- Online enrichment must never be silently enabled.
- LGPD minimization and redaction defaults remain active by default.

## Advanced crossing ideas (future-ready)

Additional crossing vectors to raise recall for quasi-identification risk:

1. **Temporal fingerprinting**
   - Session windows, weekday/hour recurrence, route sequence timing.
2. **Device/browser fingerprint hints**
   - Normalized user-agent entropy, language/timezone mismatch, recurring header patterns.
3. **Network continuity**
   - Prefix stability over time, ASN/ISP hints, proxy-chain depth and shape.
4. **Cross-log graph correlation**
   - Shared `session_id`, request-id, download events, auth events across proxy/app logs.
5. **Metadata pivots**
   - Filename/EXIF/doc metadata ties to route-level breadcrumbs.
6. **Behavioral route-path motifs**
   - Repeated endpoint journeys that correlate with profile/account/address workflows.

All of the above remain "risk signals", not proof of identity.

## Confidence model (separate from risk score)

Use two outputs:

- `risk_score` (0-100): deanonymization potential.
- `confidence_score` (0-100): confidence in the inference quality.

Suggested confidence factors:

| Factor | Effect on confidence |
| --- | --- |
| Independent sources agree (proxy + app + report logs) | Increase |
| Temporal consistency across runs | Increase |
| Signal ambiguity high (generic tokens only) | Decrease |
| Data sparsity / missing breadcrumbs | Decrease |
| External enrichment unavailable or inconclusive | Decrease |

Reference confidence labels:

- `LOW`: `< 40`
- `MEDIUM`: `40-69`
- `HIGH`: `>= 70`

## Risk x confidence matrix (report-ready)

Recommended decision matrix:

| Risk \\ Confidence | LOW confidence | MEDIUM confidence | HIGH confidence |
| --- | --- | --- | --- |
| **LOW risk** | Keep as informational note; no action. | Keep as informational note; monitor trend. | Keep as informational note; monitor trend. |
| **MEDIUM risk** | Suggested review; request more evidence before escalation. | Suggested review with redacted evidence and operator checklist. | Escalate to priority review queue; preserve strict minimization. |
| **HIGH risk** | High-risk warning with explicit uncertainty note; gather more evidence safely. | High-risk warning + mandatory operator confirmation. | High-risk confirmed path: mandatory review, strict redaction, policy-triggered handling. |

Report fields (minimum):

- `risk_score`, `risk_label`
- `confidence_score`, `confidence_label`
- `fired_signals[]`
- `uncertainty_reasons[]`
- `redaction_applied: true/false`

Contract artifacts in repo:

- `docs/ops/schemas/quasi-identification-risk-record.schema.json`
- `docs/ops/schemas/quasi-identification-risk-record.example.json`
- `tests/test_quasi_identification_contract.py`
- `docs/ops/QUASI_IDENTIFICATION_OPERATOR_PLAYBOOK.md` (+ pt-BR)

## Backlog anticipations (FN, tree models, AI engines)

To anticipate next technical increments:

1. **FN fixtures expansion**
   - Add synthetic cases specifically for IP+geo+breadcrumb combinations.
2. **Tree-based confidence estimator**
   - Add optional tabular model (`xgboost`/`lightgbm`/`sklearn`) for `confidence_score`.
3. **Graph scoring prototype**
   - Optional graph-correlation module (`networkx`) for cross-log entity linkage.
4. **Fuzzy/entity helpers**
   - Optional `rapidfuzz` and light NER (`spaCy` or equivalent) for weak breadcrumbs.
5. **Explainability**
   - Keep factor-level explainability; optional SHAP only when model complexity increases.

## Sprint-ready implementation roadmap (S2/S3)

### S2-A (daily slices, low risk)

- Deliver `risk_score` engine + unit tests.
- Deliver `confidence_score` v0 (rule-based, explainable).
- Deliver report row with risk/confidence labels and redaction flag.

### S2-B (daily slices, medium risk)

- Add correlation features from multiple log sources.
- Add uncertainty reasons list and matrix-based action mapping.
- Add fixture pack for LOW/MEDIUM/HIGH x LOW/MEDIUM/HIGH confidence cases.

### S3-A (optional uplift)

- Add optional model-based confidence estimator (tree model), gated by config.
- Compare against rule-based baseline using FN-focused fixtures.
- Keep rule-based fallback as default-safe path.

### S3-B (enterprise optional, opt-in)

- Add enrichment adapter limits/audit metadata only (provider-agnostic).
- Keep external calls off by default and bounded when enabled.

## Success criteria

- Composite-risk labels appear in reports with explainable factors.
- Default mode adds no outbound data sharing.
- HIGH-risk combinations are surfaced with redacted evidence and review guidance.
- Thresholds and risk posture are configurable without code changes.
