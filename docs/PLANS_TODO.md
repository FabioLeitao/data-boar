# Consolidated plans – sequential to-dos

This document lists **incomplete goals** from active plans and the **recommended sequential to-dos** to achieve them. All steps are intended to be **non-destructive**, **non-regression**, and **non-performance impacting**; each step should be **tested** and **safe** before marking done.

---

## Plan: Corporate compliance improvements ✅ **Complete**

**Source:** `.cursor/plans/corporate_compliance_improvements_plan_b209453a.plan.md`

**Progress:** All to-dos below are complete. This plan is **closed** for implementation; use this section only for reference to the current state of the application.

### To-dos (all complete)

| # | To-do | Status | Notes |
|---|--------|--------|--------|
| 1 | **Phase 6 – Config:** Normalize `api.require_api_key`, `api.api_key`, `api.api_key_from_env` in `config/loader.py` | ✅ Done | Optional API key for enterprise |
| 2 | **Phase 6 – API:** Add middleware/dependency in `api/routes.py` to check `X-API-Key` or `Authorization: Bearer <key>` when `require_api_key` is true; 401 if wrong/missing; **exclude `/health`** | ✅ Done | Load balancers keep 200 on /health |
| 3 | **Phase 6 – Tests:** New test: with `require_api_key: true` and valid key → 200; wrong/missing key → 401; `/health` without key → 200 | ✅ Done | Existing API test still passes when option off |
| 4 | **Phase 6 – Docs:** Update SECURITY.md to mention optional API key; document key in USAGE (EN and PT-BR) | ✅ Done | Key in env; do not log |
| 5 | **Validate Phase 6:** Run `pytest -W error`; call API with/without key when `require_api_key` true | ✅ Done | 42 tests pass |
| 6 | **Final:** Run full `pytest -W error`; optional docker build and smoke test | ✅ Done | 42 tests pass |
| 7 | **Publish:** Validate documentation reflects current state; bump minor version if needed; republish Docker image to hub; keep EN and PT-BR docs in sync | ✅ Done | Version 1.1.0; docs validated; Docker build/push remains manual (see deploy/DEPLOY.md) |

**Current state of the application (for later reference):** Phases 0–5 (baseline, docs/frameworks, recommendation overrides, executive summary, min_sensitivity, config_scope_hash) and Phase 6 (optional API key) are implemented and tested. App version **1.1.0**; config supports `api.require_api_key`, `api.api_key`, `api.api_key_from_env`; API middleware enforces X-API-Key or Bearer when required; GET /health is always public; SECURITY.md and USAGE (EN/PT-BR) document the option. Docker image tag/push is manual (see deploy/DEPLOY.md).

---

## Plan: Detection and differential treatment of possible minor data

**Source:** [docs/PLAN_MINOR_DATA_DETECTION.md](PLAN_MINOR_DATA_DETECTION.md)

Goal: Detect when data may relate to minors (e.g. age from DOB), treat as highest sensitivity, cross-reference with name/official docs/health, optionally full-scan related columns, and surface in report with differential treatment (LGPD Art. 14, GDPR Art. 8).

| # | To-do | Status |
|---|--------|--------|
| 1 | Design & doc: finalize approach (age inference, flag vs level, cross-ref, full-scan); minimal schema impact | ✅ Done |
| 2 | Detector: DOB/age parsing + age < threshold → possible_minor; keep HIGH/MED/LOW for others | ✅ Done |
| 3 | Schema: optional column possible_minor or encode via pattern/norm_tag; migration | ✅ Done (encode via pattern/norm_tag) |
| 4 | Scanner: pass possible_minor from detector into saved findings | ✅ Done |
| 5 | Cross-reference: DOB/minor with name, CPF/RG/SSN, health in same row; confidence | ✅ Done |
| 6 | Full scan (optional): when DOB suggests minor + config, full-scan column and adjacent | ✅ Done |
| 7 | Report: highest-priority recommendation/section for possible minors (LGPD 14, GDPR 8) | ✅ Done |
| 8 | Config: minor_age_threshold, minor_full_scan, minor_cross_reference in loader; wire loader → engine → scanner → detector | ✅ Done |
| 9 | Tests: age inference, possible_minor, report, config wiring; no regression | ✅ Done |
| 10 | Docs: sensitivity & compliance (EN/PT-BR) for minor detection | ✅ Done |

---

## Plan: Cross-referenced / aggregated data – identification risk

**Source:** [docs/PLAN_AGGREGATED_IDENTIFICATION.md](PLAN_AGGREGATED_IDENTIFICATION.md)

Goal: Cross information from multiple sources/columns (gender, job position, health, address, phone, etc.) that in **aggregate** can identify individuals; treat as personal/sensitive and report as a **special case** for DPO/compliance, explaining the cross-reference condition.

| # | To-do | Status |
|---|--------|--------|
| 1 | Design & doc: quasi-identifier categories, aggregation scope (per-table/per-file), storage | ⬜ Pending |
| 2 | Category mapping: column_name + pattern_detected → gender, job_position, health, address, phone (config + defaults) | ⬜ Pending |
| 3 | Schema: table or structure for aggregated identification risk (or synthetic finding with explanation) | ⬜ Pending |
| 4 | Post-scan aggregation: group by (session, target, table/file); if categories >= threshold, create aggregated record | ⬜ Pending |
| 5 | Report: sheet/section “Cross-referenced data – possible identification” with target, table/file, columns, explanation | ⬜ Pending |
| 6 | Report: recommendation row for aggregated case explaining multi-source condition for DPO/compliance | ⬜ Pending |
| 7 | Config: aggregated_identification_enabled, aggregated_min_categories, quasi_identifier_mapping | ⬜ Pending |
| 8 | Tests: category mapping, aggregation rule, report; no regression | ⬜ Pending |
| 9 | Docs: sensitivity & compliance (EN/PT-BR) for aggregated identification | ⬜ Pending |

---

## Plan: Sensitive categories ML/DL (CID, gender, religion, political, PEP, race, union, genetic, biometric, sex life)

**Source:** [docs/PLAN_SENSITIVE_CATEGORIES_ML_DL.md](PLAN_SENSITIVE_CATEGORIES_ML_DL.md)

Goal: Configure with examples so ML/DL can detect other sensitive personal data (CID/ICD, gender, religion, political affiliation, PEP, race/skin color, union, genetic/biometric, sex life, health/disability). Provide ready-to-use term lists and documentation; optional built-in defaults and report overrides.

| # | To-do | Status |
|---|--------|--------|
| 1 | **Example file:** Create `sensitivity_terms_sensitive_categories.example.yaml` with terms for all categories (EN and PT-BR oriented) | ✅ Done |
| 2 | **Docs EN:** In `sensitivity-detection.md`, add section "Sensitive categories (health, religion, political, etc.)" with link to plan and example file | ✅ Done |
| 3 | **Docs PT-BR:** In `sensitivity-detection.pt_BR.md`, add same section in Portuguese | ✅ Done |
| 4 | **Built-in defaults (optional):** Consider adding a subset of these terms to `DEFAULT_ML_TERMS` in `core/detector.py` so out-of-the-box detection includes e.g. religion, political, gender, biometric, genetic | ⬜ Pending |
| 5 | **Recommendation overrides example:** Add example in USAGE or in plan for `recommendation_overrides` covering health, religion, political, PEP, race, union, genetic, biometric, sex life | ⬜ Pending |
| 6 | **Tests:** Add test that when ML terms include e.g. "religion" and "political affiliation", columns/samples with those terms are classified as sensitive; existing tests pass | ⬜ Pending |

---

## Other plans (reference)

- **LGPD Audit Full Implementation** (`lgpd_audit_solution_full_implementation_*.plan.md`): No granular to-dos in plan; goals largely reflected in current codebase (unified config, SQLite, API 8088, report, etc.). No sequential to-do list to add here.
- **Privacy-audit-scanner** (`privacy-audit-scanner_*.plan.md`): Describes a different package layout (`dataguardian/`). Current repo is `python3-lgpd-crawler` with `core/`, `api/`, `report/`, `connectors/`. Those plans’ to-dos (db-scanners, file-scanners, etc.) map to existing components; consider them **reference only** unless you adopt that structure.

---

## How to use this list

1. **Execute to-dos in order** (1 → 2 → … → 7).
2. **Mark done** when the step is implemented, tests pass, and behaviour is verified (e.g. in plan file set `status: completed`, or tick in this table when you sync).
3. **After each step:** run `uv run pytest -W error` to ensure no regression.
4. **Publish step:** update README/USAGE/SECURITY and version as needed; build and push Docker image; keep EN/PT-BR aligned.

---

*Last synced with plan files and codebase. Update this doc when completing steps or when plans change.*
