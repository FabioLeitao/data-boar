# PLAN: Organizational maturity self-assessment (GRC-style questionnaire)

<!-- plans-hub-summary: POC on main: gated /{locale}/assessment + YAML pack + SQLite + HMAC + post-submit HTML summary; scoring/export/RBAC still backlog—companion to technical scans; not legal audit. -->
<!-- plans-hub-related: PLAN_DASHBOARD_REPORTS_ACCESS_CONTROL.md, LICENSING_OPEN_CORE_AND_COMMERCIAL.md (future tier features), PLAN_SCOPE_IMPORT_FROM_EXPORTS.md (inventory bootstrap narrative) -->

**Status:** **POC A in progress on `main`** — gated `GET`/`POST /{locale}/assessment`, optional **`api.maturity_assessment_pack_path`** (YAML), **SQLite** table `maturity_assessment_answers`, optional **HMAC-SHA256 per row** (`row_hmac`) when **`DATA_BOAR_MATURITY_INTEGRITY_SECRET`** (or **`api.maturity_integrity_secret_from_env`**) is set at write time. **`GET /status`** and **`python main.py --export-audit-trail`** include **`maturity_assessment_integrity`** (counts: ok / mismatch / unsealed / unknown_sealed). **Not** encryption; deters casual DB edits and supports demo narrative. **Still backlog:** scoring, consultant UX, legal one-pager, RBAC (#86), report bundle export.

**Horizon / urgency:** `[H3]` or `[H4]` · `[U3]` for the **complete** product slice; next code slices: **scoring / export**, then **tenant model** when clear.

**Synced with:** [PLANS_TODO.md](PLANS_TODO.md) (Backlog catalogue entry).

### Operator sequencing — prerequisites done; POC **A** in progress (SQLite + HMAC shipped; scoring next)

**M-LOCALE-V1 (dashboard i18n):** ✅ **shipped on `main`** (**2026-04**) — path-prefixed HTML, `en` + `pt-BR` catalogs, negotiation. See [PLAN_DASHBOARD_I18N.md](completed/PLAN_DASHBOARD_I18N.md) and [PLANS_TODO.md](PLANS_TODO.md) (Dashboard i18n section).

**Version signal for testers (do not rely on git inference alone):** in-repo semver is **`1.7.1-beta`** ([VERSIONING.md](../VERSIONING.md) `-beta`); **last stable** published story remains **1.7.0** (Hub / GitHub Release). Callouts: [CHANGELOG.md](../../CHANGELOG.md), [docs/releases/1.7.1-beta.md](../releases/1.7.1-beta.md), README **Latest stable** vs **`main` pre-release**. Anyone pulling `main` for **formal** beta testing should use those files—not only `git log`.

**Are we on option A in code right now?** **Yes (POC):** `GET`/`POST /{locale}/assessment` when **`api.maturity_self_assessment_poc_enabled`** is on and tier allows it (`core/licensing/tier_features.py`); otherwise **404**. Optional YAML pack drives questions; answers persist to SQLite; optional **HMAC** seals rows when a secret is configured. **Scoring**, **RBAC**, and **report narrative export** are still **not** implemented — the plan still compares full **A / B / C / D** product shapes for later evaluation.

**POC architecture A — progress:**

| Step | Architecture | Intent |
| --- | --- | --- |
| **1** | **A** — Routes under **`/{locale}/…/assessment`** + optional YAML pack ✅; **SQLite persistence + answers** ✅; **optional HMAC row integrity** ✅ (`GET /status`, **`--export-audit-trail`**) | **First** in-app spike: single app, same audit story; align with RBAC [#86](https://github.com/FabioLeitao/data-boar/issues/86) later. |
| **2** | **B** — Excel sheet + formula scoring | Fast tabular path; compare UX vs A for consultant workflows. |
| **3** | **C** — Companion app + API/SSO | Separation / white-label; evaluate **after** A/B learnings. |
| **4** | **D** — PDF/export-only narrative | Simplicity vs interactivity; last in the **comparison Colleague-Nn**, not “never”. |

**POC scaffolding (ongoing):** feature-flag + tier / JWT gates; optional YAML pack from **`api.maturity_assessment_pack_path`** — **no** proprietary questionnaire text in the **public** repo (curate privately; see `tests/fixtures/maturity_assessment/sample_pack.yaml` for shape). Routes use the same **`/{locale_slug}/…`** pattern as the rest of the dashboard HTML ([PLAN_DASHBOARD_I18N.md](completed/PLAN_DASHBOARD_I18N.md)).

**Remember:** proceed **A → B → C → D** as **evaluation spikes**, not four full products—pick one shipping path after spikes unless counsel/commercial demands otherwise.

### After this track (operator sequencing — do not lose the thread)

1. **[PLAN_PRODUCT_TIERS_AND_OPEN_CORE.md](PLAN_PRODUCT_TIERS_AND_OPEN_CORE.md)** — **Technical enforcement roadmap:** only **Phase 0** is done (claims sketched in **LICENSING_SPEC**, JWT path exists). **Phases 1–6** ( **`dbtier` / `dbfeatures` in tokens**, `check_feature()`, gates in connectors/reports, Partner/Enterprise rules) are **not started** — depends on **legal review** and issuer work; promote when GRC/maturity and commercial packaging need real entitlements (not just `licensing.effective_tier` lab simulation).
2. **[PLAN_PDF_GRC_REPORT.md](PLAN_PDF_GRC_REPORT.md)** — **Different artefact:** PDF “em prosa” for **technical scan findings** (exec summary, priority matrix like a **cyber/GRC vulnerability-style** report). **Not** the org questionnaire; it complements technical evidence. Priority band **B** in that plan; still **planned** (Phases 1–2 unchecked).
3. **[PLAN_SCOPE_IMPORT_FROM_EXPORTS.md](PLAN_SCOPE_IMPORT_FROM_EXPORTS.md)** — **After** maturity/DOCX is under control: bootstrap **customer asset inventory** from **exports** — **minimum** acceptable is a **manual CSV** (“everything the client remembers”: hosts, paths, tags) mapped to the **canonical schema** → merge-safe config fragments. Live ITSM APIs are **not** required for v1.
4. **Dashboard RBAC — [GitHub #86](https://github.com/FabioLeitao/data-boar/issues/86)** (still **OPEN** as of plan updates): **Phase 1** = browser **session** + **Bitwarden Passwordless.dev** (minimum viable human auth) on the same **`/{locale}/…`** paths as i18n; then role/group gates for `/reports` and downloads per [PLAN_DASHBOARD_REPORTS_ACCESS_CONTROL.md](PLAN_DASHBOARD_REPORTS_ACCESS_CONTROL.md). **Order locked in product docs:** **M-LOCALE-V1** ✅ → **maturity POC track** (this file) → **scope import** → **#86** implementation — adjust only if a **security exception** forces early guards (then budget a migration slice).

## Problem statement

Operators and consultants need **organizational** visibility (roles, processes, awareness) alongside **technical** inventory from Data Boar. A structured **self-assessment** (not audit, not legal advice) can raise maturity and align teams (DPO, IT, cyber, compliance, HR, contracts, customer-facing) with preparation for LGPD and related frameworks—**if** answers are sincere and the instrument is clearly framed as **consciousness-raising** only.

**Source material:** Maintainer-authored questionnaire (historically a **DOCX** in an LGPD working folder, plus spreadsheet “gabarito” / scoring logic). **Not** in the public repo until curated; expect **`docs/private/`** or a licensed commercial content pack for paid tiers.

**Operator workspace (confirmed — not public Git):** `docs/private/raw_pastes/general/LGPD_DOCS/` contains the working **DOCX** (diagnóstico / índice de adequação à LGPD, level bands), **XLSX** metric/scoring example, and additional **inventory / mapping** spreadsheets usable as **design inspiration** for future report shapes and scope hints—**do not** paste proprietary wording into tracked files. For agent ingestion in future sessions: keep files in that folder or export **structured** excerpts (YAML/CSV of questions + weights) to the same tree; **DOCX/XLSX** are readable via tools/scripts on the workstation even when Cursor’s file **glob** skips gitignored paths.

**DOCX → YAML workflow (architecture A):** curate sections/questions **privately**, then author a **`maturity_assessment_pack_path`** YAML file matching `core/maturity_assessment/pack.py` (see `tests/fixtures/maturity_assessment/sample_pack.yaml` for shape). Point `api.maturity_assessment_pack_path` at that file; no proprietary strings belong in the public GitHub tree.

## Fit with Data Boar mission

- **Aligned:** Same “evidence and governance” story: technical scan shows **where** data lives; maturity form shows **how prepared** the organization claims to be—both feed the DPO/consultant narrative in sales and delivery.
- **Not aligned with open core:** This is **process/GRC content**, heavy UX, and ongoing content maintenance—natural fit for **commercial / partner** tier or a **separate product**, not the BSD AGPL community baseline.

**Branding:** Can share **Data Boar** / **dashBOARd** chrome if embedded; must not blur **legal conclusions**—copy must repeat that output is **self-reported maturity signal**, not certification (see [ADR 0025](../adr/0025-compliance-positioning-evidence-inventory-not-legal-conclusion-engine.md) posture).

## Architecture options (decision later)

| Option | Pros | Cons |
| --- | --- | --- |
| **A. New dashBOARd routes** (`/assessment` or similar), store in SQLite per tenant/session | Single login, same audit trail story, export to report | Couples release cadence to core app; RBAC/auth (#86) becomes more critical |
| **B. Extra Excel sheet + formula scoring** | Fast to ship if schema is tabular; familiar to Excel users | Weak for long text, branching logic, versioning of questions |
| **C. Companion web app** (“Boar Assess” or partner OEM) with API/SSO link to Data Boar | Clear separation; independent roadmap; optional white-label for partners | Two deployables, identity integration cost |
| **D. PDF/export-only** from a filled form (server generates narrative) | Simple | Less interactive; trend history needs storage anyway |

**Recommendation for first spike (when promoted):** prototype **A** (per **Operator sequencing** above) behind **feature flag + license claim**; keep question YAML/JSON in a **content pack** repo or private submodule so **LGPD vs ISO 27701 vs hybrid** = different packs without forking the engine. Revisit **C** after A/B learnings.

## Multi-“norm” adaptation

Feasible: treat **question banks** and **weights** as data (like **compliance samples**), keyed by `norm_tag` / selected **compliance profile** for the tenant. Scoring must stay **transparent** (documented weights, “fair if honest” disclaimer). **Not** mirabolante if scoped as **config-driven questionnaire + rubric**, not bespoke law engine.

## Tamper-evidence (POC) — HMAC on stored answers

- **What:** Each stored answer row can carry **`row_hmac`** = HMAC-SHA256 (hex) over a **canonical UTF-8 payload** (`core/maturity_assessment/integrity.py`, version prefix `maturity-answer-hmac-v1`). The **secret** is read from env (**`DATA_BOAR_MATURITY_INTEGRITY_SECRET`** by default, or the env var named by **`api.maturity_integrity_secret_from_env`**). If no secret is set at submit time, rows are stored **unsealed** (empty MAC).
- **Where to read:** **`GET /status`** → **`maturity_assessment_integrity`**; **`python main.py --export-audit-trail`** includes the **same** object for offline governance snapshots.
- **What it is not:** Not **encryption**; not proof against an attacker with the secret, the app process, or full disk control (“evil maid”). It **does** help demos and operators detect **casual SQLite edits** without updating the MAC.
- **Regression tests:** `tests/test_maturity_assessment_integrity.py` (golden HMAC vector, verify counts, DB tamper); `tests/test_api_assessment_poc.py`; `tests/test_audit_export.py` (export parity with `verify_maturity_assessment_integrity`).

## Risks and guardrails

- **Honesty / gaming:** Scores are only as good as inputs; position as **trend and conversation starter**, not compliance scorecard.
- **Scope creep:** Full GRC platforms are a product category—stay **thin**: questionnaire + export + optional history, not workflow replacement.
- **Legal:** Every surface: “not legal advice; not audit; not ANPD filing.”

## Open core vs commercial

- **Open core:** **No** — keep scanner/dashboard baseline OSS; ship assessment as **source-available / subscription** module, **or** separate paid app.
- **Subscription value:** Periodic re-assessment, trend charts, consultant “tenant” view—matches **partner SKUs** in [LICENSING_OPEN_CORE_AND_COMMERCIAL.md](../LICENSING_OPEN_CORE_AND_COMMERCIAL.md).

## Next steps (ordered; POC-first)

1. **POC A — done for persistence + integrity demo:** SQLite + YAML pack + HMAC + `/status` + audit export ✅; **post-submit summary** on `GET /{locale}/assessment?saved=1&batch=…` (row count + HMAC counts for that batch) ✅. **Next:** lightweight **scoring** or richer **read-only summary** in-dashboard (product decision); **import** questionnaire from private DOCX → YAML **without** pasting proprietary wording into public Git.
2. Legal/commercial one-pager: positioning vs audit; consent for storing responses.
3. **Architecture lock:** spike **A** remains default; revisit **C** only after A/B learnings — align with [PLAN_DASHBOARD_REPORTS_ACCESS_CONTROL.md](PLAN_DASHBOARD_REPORTS_ACCESS_CONTROL.md) and API key / future SSO (#86).
4. MVP: **export** org answers into report bundle or annex (distinct from technical **[PLAN_PDF_GRC_REPORT.md](PLAN_PDF_GRC_REPORT.md)** PDF stream).

## Relationship to other plans

- **[PLAN_PRODUCT_TIERS_AND_OPEN_CORE.md](PLAN_PRODUCT_TIERS_AND_OPEN_CORE.md)** — subscription / partner tier boundaries; maturity assessment is **not** open core — enforcement phases **1+** apply when moving past POC/lab gates.
- **[PLAN_PDF_GRC_REPORT.md](PLAN_PDF_GRC_REPORT.md)** — **Scan output** PDF (exec + detailed + priority matrix); **not** the org self-assessment form — cross-sell in GRC narratives only.
- **[PLAN_SCOPE_IMPORT_FROM_EXPORTS.md](PLAN_SCOPE_IMPORT_FROM_EXPORTS.md)** — complementary “bootstrap from existing tools” story; assessment is **people/process**, scope import is **technical inventory**.
- **Dashboard RBAC / #86** — required if multi-user tenants fill forms.

---

*Created for operator recall after exploration in chat; revise or archive when superseded.*
