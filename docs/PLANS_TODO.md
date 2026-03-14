# Consolidated plans – sequential to-dos

Plan files are kept in **English only** for history and progress tracking. Operator-facing documentation (how to use, config, deploy, etc.) exists in both EN and pt-BR; see [README.md](README.md) ([pt-BR](README.pt_BR.md)).

This document is the **single source of truth** for the project’s plan status and remains in **`docs/`** at all times. It lists **incomplete goals** from active plans and the **recommended sequential to-dos** to achieve them. Completed plan documents (design and to-do details) are archived in **`docs/completed/`** for reference; links below point to those files.

All steps are intended to be **non-destructive**, **non-regression**, and **non-performance impacting**; each step should be **tested** and **safe** before marking done.

**Plan status:** Corporate compliance improvements ✅ Complete · Minor data detection ✅ Complete · Aggregated identification ✅ Complete · Sensitive categories ML/DL ✅ Complete · Rate limiting & concurrency ✅ Complete · Web hardening & security ✅ Complete · Logo and naming ⬜ In progress · **Dashboard i18n (multi-language web UI)** ⬜ Under consideration

---

## Plan: Dashboard i18n (multi-language web UI) ⬜ **Under consideration**

**Source:** [docs/PLAN_DASHBOARD_I18N.md](PLAN_DASHBOARD_I18N.md)

**Status:** No approach decided yet. The plan document sets out **options and recommendations** (path-prefix vs query/cookie, JSON vs gettext, complexity). **There is no to-do list here until we choose an approach;** after that, concrete steps will be added to this section and to the plan file.

---

## Plan: Logo and naming recommendations ⬜ **In progress**

**Source:** [docs/PLAN_LOGO_AND_NAMING.md](PLAN_LOGO_AND_NAMING.md)

**Progress:** Mark each to-do done here and in the plan file when actually completed.

Goal: Copyright-safe logo (web, favicon, optional report), integration in the app, and naming recommendations (e.g. compliance_crawler). User decides which options to apply.

| #   | To-do                                                                                                                             | Status    | Notes                                                                                                       |
| --- | ---                                                                                                                               | ---       | ---                                                                                                         |
| 1   | Decide logo concept (A–D) and colors; produce master logo (SVG) and export web PNG (32/64 px) and favicon (ICO or 16/32 PNG)      | ✅ Done    | **Data Boar mascot** as logo; master SVG + PNG in `api/static/mascot/`; favicon derived (build_favicon.py). |
| 2   | Place assets in `api/static/`: favicon.ico (and/or favicon-32.png), logo.svg, logo-64.png                                         | ✅ Done    | Mascot in `api/static/mascot/`; favicon.ico from script; former logo.svg retired.                           |
| 3   | Add favicon link(s) in `api/templates/base.html` (`<link rel="icon">`)                                                            | ✅ Done    | base.html uses mascot as favicon.                                                                           |
| 4   | (Optional) Add logo to About page and optionally Dashboard/Reports header                                                         | ✅ Done    | About, Dashboard, Reports, Config, Help: mascot in header + attribution.                                    |
| 5   | Check PyPI and web for chosen name (e.g. compliance_crawler) availability                                                         | ⬜ Pending | Avoid clashes with existing products                                                                        |
| 6   | Decide display name and/or package rename; if changing, update `core/about.py` and/or `pyproject.toml` and docs per VERSIONING.md | ✅ Done    | Display name **Data Boar**; package remains `python3-lgpd-crawler`.                                         |
| 7   | (Optional) Embed logo in Excel Report info sheet via `report/generator.py`                                                        | ✅ Done    | Small mascot (48×48) in Report info at D1.                                                                  |
| 8   | (Optional) Add logo to heatmap PNG footer in `_create_heatmap`                                                                    | ✅ Done    | Small mascot in lower-right inset (8% size).                                                                |

---

## Plan: Corporate compliance improvements ✅ **Complete**

**Source:** `.cursor/plans/corporate_compliance_improvements_plan_b209453a.plan.md`

**Progress:** All to-dos below are complete. This plan is **closed** for implementation; use this section only for reference to the current state of the application.

### To-dos (all complete)

| #   | To-do                                                                                                                                                                                             | Status | Notes                                                                                          |
| --- | ---                                                                                                                                                                                               | ---    | ---                                                                                            |
| 1   | **Phase 6 – Config:** Normalize `api.require_api_key`, `api.api_key`, `api.api_key_from_env` in `config/loader.py`                                                                                | ✅ Done | Optional API key for enterprise                                                                |
| 2   | **Phase 6 – API:** Add middleware/dependency in `api/routes.py` to check `X-API-Key` or `Authorization: Bearer <key>` when `require_api_key` is true; 401 if wrong/missing; **exclude `/health`** | ✅ Done | Load balancers keep 200 on /health                                                             |
| 3   | **Phase 6 – Tests:** New test: with `require_api_key: true` and valid key → 200; wrong/missing key → 401; `/health` without key → 200                                                             | ✅ Done | Existing API test still passes when option off                                                 |
| 4   | **Phase 6 – Docs:** Update SECURITY.md to mention optional API key; document key in USAGE (EN and PT-BR)                                                                                          | ✅ Done | Key in env; do not log                                                                         |
| 5   | **Validate Phase 6:** Run `pytest -W error`; call API with/without key when `require_api_key` true                                                                                                | ✅ Done | 42 tests pass                                                                                  |
| 6   | **Final:** Run full `pytest -W error`; optional docker build and smoke test                                                                                                                       | ✅ Done | 42 tests pass                                                                                  |
| 7   | **Publish:** Validate documentation reflects current state; bump minor version if needed; republish Docker image to hub; keep EN and PT-BR docs in sync                                           | ✅ Done | Version 1.5.1; docs validated; branded image fabioleitao/data_boar (see docs/deploy/DEPLOY.md) |

**Current state of the application (for later reference):** Phases 0–5 (baseline, docs/frameworks, recommendation overrides, executive summary, min_sensitivity, config_scope_hash) and Phase 6 (optional API key) are implemented and tested. App version **1.5.1**; display name **Data Boar** (mascot branding, favicon, report/heatmap branding); Trends sheet shows up to 3 previous runs; heatmap PNG embedded in Excel Heatmap data sheet; config supports `api.require_api_key`, `api.api_key`, `api.api_key_from_env`; API middleware enforces X-API-Key or Bearer when required; GET /health is always public; SECURITY.md and USAGE (EN/PT-BR) document the option. Branded Docker image: fabioleitao/data_boar:latest and :1.5.1 (see docs/deploy/DEPLOY.md).

---

## Plan: Detection and differential treatment of possible minor data ✅ **Complete**

**Source:** [docs/completed/PLAN_MINOR_DATA_DETECTION.md](completed/PLAN_MINOR_DATA_DETECTION.md)

**Progress:** All to-dos below are complete. This plan is **closed** for implementation; use this section only for reference to the current state of the application.

Goal: Detect when data may relate to minors (e.g. age from DOB), treat as highest sensitivity, cross-reference with name/official docs/health, optionally full-scan related columns, and surface in report with differential treatment (LGPD Art. 14, GDPR Art. 8).

| #   | To-do                                                                                                                    | Status                               |
| --- | ---                                                                                                                      | ---                                  |
| 1   | Design & doc: finalize approach (age inference, flag vs level, cross-ref, full-scan); minimal schema impact              | ✅ Done                               |
| 2   | Detector: DOB/age parsing + age < threshold → possible_minor; keep HIGH/MED/LOW for others                               | ✅ Done                               |
| 3   | Schema: optional column possible_minor or encode via pattern/norm_tag; migration                                         | ✅ Done (encode via pattern/norm_tag) |
| 4   | Scanner: pass possible_minor from detector into saved findings                                                           | ✅ Done                               |
| 5   | Cross-reference: DOB/minor with name, CPF/RG/SSN, health in same row; confidence                                         | ✅ Done                               |
| 6   | Full scan (optional): when DOB suggests minor + config, full-scan column and adjacent                                    | ✅ Done                               |
| 7   | Report: highest-priority recommendation/section for possible minors (LGPD 14, GDPR 8)                                    | ✅ Done                               |
| 8   | Config: minor_age_threshold, minor_full_scan, minor_cross_reference in loader; wire loader → engine → scanner → detector | ✅ Done                               |
| 9   | Tests: age inference, possible_minor, report, config wiring; no regression                                               | ✅ Done                               |
| 10  | Docs: sensitivity & compliance (EN/PT-BR) for minor detection                                                            | ✅ Done                               |

---

## Plan: Cross-referenced / aggregated data – identification risk ✅ **Complete**

**Source:** [docs/completed/PLAN_AGGREGATED_IDENTIFICATION.md](completed/PLAN_AGGREGATED_IDENTIFICATION.md)

**Progress:** All to-dos below are complete. This plan is **closed** for implementation; use this section only for reference to the current state of the application.

Goal: Cross information from multiple sources/columns (gender, job position, health, address, phone, etc.) that in **aggregate** can identify individuals; treat as personal/sensitive and report as a **special case** for DPO/compliance, explaining the cross-reference condition.

| #   | To-do                                                                                                                 | Status |
| --- | ---                                                                                                                   | ---    |
| 1   | Design & doc: quasi-identifier categories, aggregation scope (per-table/per-file), storage                            | ✅ Done |
| 2   | Category mapping: column_name + pattern_detected → gender, job_position, health, address, phone (config + defaults)   | ✅ Done |
| 3   | Schema: table or structure for aggregated identification risk (or synthetic finding with explanation)                 | ✅ Done |
| 4   | Post-scan aggregation: group by (session, target, table/file); if categories >= threshold, create aggregated record   | ✅ Done |
| 5   | Report: sheet/section “Cross-referenced data – possible identification” with target, table/file, columns, explanation | ✅ Done |
| 6   | Report: recommendation row for aggregated case explaining multi-source condition for DPO/compliance                   | ✅ Done |
| 7   | Config: aggregated_identification_enabled, aggregated_min_categories, quasi_identifier_mapping                        | ✅ Done |
| 8   | Tests: category mapping, aggregation rule, report; no regression                                                      | ✅ Done |
| 9   | Docs: sensitivity & compliance (EN/PT-BR) for aggregated identification                                               | ✅ Done |

---

## Plan: Sensitive categories ML/DL (CID, gender, religion, political, PEP, race, union, genetic, biometric, sex life) ✅ **Complete**

**Source:** [docs/completed/PLAN_SENSITIVE_CATEGORIES_ML_DL.md](completed/PLAN_SENSITIVE_CATEGORIES_ML_DL.md)

**Progress:** All to-dos below are complete. This plan is **closed** for implementation; use this section only for reference to the current state of the application.

Goal: Configure with examples so ML/DL can detect other sensitive personal data (CID/ICD, gender, religion, political affiliation, PEP, race/skin color, union, genetic/biometric, sex life, health/disability). Provide ready-to-use term lists and documentation; optional built-in defaults and report overrides.

| #   | To-do                                                                                                                                                                                                           | Status |
| --- | ---                                                                                                                                                                                                             | ---    |
| 1   | **Example file:** Create `sensitivity_terms_sensitive_categories.example.yaml` with terms for all categories (EN and PT-BR oriented)                                                                            | ✅ Done |
| 2   | **Docs EN:** In `sensitivity-detection.md`, add section "Sensitive categories (health, religion, political, etc.)" with link to plan and example file                                                           | ✅ Done |
| 3   | **Docs PT-BR:** In `sensitivity-detection.pt_BR.md`, add same section in Portuguese                                                                                                                             | ✅ Done |
| 4   | **Built-in defaults (optional):** Consider adding a subset of these terms to `DEFAULT_ML_TERMS` in `core/detector.py` so out-of-the-box detection includes e.g. religion, political, gender, biometric, genetic | ✅ Done |
| 5   | **Recommendation overrides example:** Add example in USAGE or in plan for `recommendation_overrides` covering health, religion, political, PEP, race, union, genetic, biometric, sex life                       | ✅ Done |
| 6   | **Tests:** Add test that when ML terms include e.g. "religion" and "political affiliation", columns/samples with those terms are classified as sensitive; existing tests pass                                   | ✅ Done |

---

## Plan: Rate limiting and concurrency safeguards ✅ **Complete**

**Source:** [docs/completed/PLAN_RATE_LIMIT_SCANS.md](completed/PLAN_RATE_LIMIT_SCANS.md)

**Progress:** All to-dos below are complete. This plan is **closed** for implementation; use this section only for reference to the current state of the application.

Goal: Add configurable rate limiting and concurrency safeguards so the LGPD audit scanner cannot accidentally DoS customer networks while keeping existing behaviour and docs in sync.

| #   | To-do                                                                                                                             | Status |
| --- | ---                                                                                                                               | ---    |
| 1   | Add `rate_limit` configuration support in `config/loader.py` (with env overrides) and document it.                                | ✅ Done |
| 2   | Implement DB-level helpers to query running/last sessions for rate limiting.                                                      | ✅ Done |
| 3   | Enforce rate limiting in `api/routes.py` for `/scan`, `/start`, `/scan_database` (no impact on read-only endpoints).              | ✅ Done |
| 4   | Decide and implement CLI interaction with rate limits (reject vs warn) and document the decision.                                 | ✅ Done |
| 5   | Add bounds and documentation for `scan.max_workers` to avoid extreme values when rate limiting is on.                             | ✅ Done |
| 6   | Write unit tests for the new rate-limit behaviour and ensure all existing tests still pass.                                       | ✅ Done |
| 7   | Update README (EN/PT-BR), USAGE (EN/PT-BR), man pages (1 and 5), and `help.html` to describe rate limiting and keep docs in sync. | ✅ Done |

---

## Plan: Web hardening and security improvements

**Source:** [docs/completed/PLAN_WEB_HARDENING_SECURITY.md](completed/PLAN_WEB_HARDENING_SECURITY.md)

Goal: Harden the web surface of the LGPD crawler (CSP, headers, and deploy guidance) without regressing current behaviour, keeping docs and man pages in sync and tests green.

| #   | To-do                                                                                                                                                                                  | Status |
| --- | ---                                                                                                                                                                                    | ---    |
| 1   | Refine CSP and security headers in `api/routes.py` (partial lockdown profile, optional stricter mode) and move dashboard JS into `/static/dashboard.js` to reduce inline code.         | ✅ Done |
| 2   | Confirm and, if needed, adjust Help page JS so it works under the refined CSP.                                                                                                         | ✅ Done |
| 3   | Extend `docs/deploy/DEPLOY.md` with Docker and Kubernetes hardening guidance (securityContext, NetworkPolicy, PDB, resource tuning) as **optional** examples.                          | ✅ Done |
| 4   | Update `SECURITY.md` with a short section covering CSP, security headers, and the new hardening examples.                                                                              | ✅ Done |
| 5   | Update docs (`docs/USAGE.md`, `docs/USAGE.pt_BR.md`) to mention CSP behaviour and how to enable stricter profiles, and update man(1)/(5) plus `help.html` to stay in sync.             | ✅ Done |
| 6   | Add/adjust tests (e.g. `tests/test_rate_limit_api.py`-style) to assert CSP header presence and default semantics, and re-run the full test suite (`uv run pytest tests/ -v -W error`). | ✅ Done |

---

## Other plans (reference)

- **LGPD Audit Full Implementation** (`lgpd_audit_solution_full_implementation_*.plan.md`): No granular to-dos in plan; goals largely reflected in current codebase (unified config, SQLite, API 8088, report, etc.). No sequential to-do list to add here.
- **Privacy-audit-scanner** (`privacy-audit-scanner_*.plan.md`): Describes a different package layout (`dataguardian/`). Current repo is `python3-lgpd-crawler` with `core/`, `api/`, `report/`, `connectors/`. Those plans’ to-dos (db-scanners, file-scanners, etc.) map to existing components; consider them **reference only** unless you adopt that structure.

---

## How to use this list

1. **Execute to-dos in order** (1 → 2 → … → 7).
1. **Mark done** when the step is implemented, tests pass, and behaviour is verified (e.g. in plan file set `status: completed`, or tick in this table when you sync).
1. **After each step:** run `uv run pytest -W error` to ensure no regression.
1. **Publish step:** update README/USAGE/SECURITY and version as needed; build and push Docker image; keep EN/PT-BR aligned.

---

*Last synced with plan files and codebase. Update this doc when completing steps or when plans change.*
