# Quasi-identification operator playbook (token-aware)

**Português (Brasil):** [QUASI_IDENTIFICATION_OPERATOR_PLAYBOOK.pt_BR.md](QUASI_IDENTIFICATION_OPERATOR_PLAYBOOK.pt_BR.md)

Operational shorthand for the quasi-identification flow (`IP + geo + breadcrumbs`) with low cognitive load.

## Purpose

- Keep daily work small, safe, and auditable.
- Reduce accidental scope creep in detection-depth sprints.
- Preserve LGPD-safe defaults while enabling measurable progress.

## Daily slice checklist (10-120 min)

Use exactly one primary slice:

1. `score` - adjust or test risk/confidence scoring only.
2. `report` - adjust output fields or matrix action mapping.
3. `guardrail` - redaction, lookup caps, opt-in protections.
4. `fixture` - add synthetic case for FN/uncertainty coverage.
5. `docs` - update plan/playbook/schema references.

## Mandatory safety gates per slice

- No online enrichment by default.
- No persistence of enriched payload by default.
- Redaction remains on for report evidence.
- If behavior changes, add or update at least one test.

## Action mapping quick reference

| Risk x Confidence | Action |
| --- | --- |
| LOW x any | Informational or monitor only |
| MEDIUM x LOW | Suggested review with uncertainty note |
| MEDIUM x MEDIUM/HIGH | Priority review queue |
| HIGH x LOW | High-risk warning + gather safer evidence |
| HIGH x MEDIUM/HIGH | Mandatory operator review |

## Contract artifacts

- Schema: `docs/ops/schemas/quasi-identification-risk-record.schema.json`
- Example: `docs/ops/schemas/quasi-identification-risk-record.example.json`
- Plan: `docs/plans/PLAN_QUASI_IDENTIFICATION_COMPOSITE_RISK.md`

## Commit split guideline (local cadence)

Prefer small themed commits:

- `docs(plans):` plan updates and sequencing only.
- `test(detector):` fixture/contract tests only.
- `chore(workflow):` wrappers/playbook/ops guidance only.

Avoid mixing code + broad docs + workflow in one commit unless the change is truly atomic.
