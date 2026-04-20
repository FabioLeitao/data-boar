# PLAN: Organizational maturity self-assessment (GRC-style questionnaire)

<!-- plans-hub-summary: POC on main: gated /{locale}/assessment + optional YAML pack; SQLite/scoring/product commitment still backlog—companion to technical scans; not legal audit. -->
<!-- plans-hub-related: PLAN_DASHBOARD_REPORTS_ACCESS_CONTROL.md, LICENSING_OPEN_CORE_AND_COMMERCIAL.md (future tier features), PLAN_SCOPE_IMPORT_FROM_EXPORTS.md (inventory bootstrap narrative) -->

**Status:** **POC scaffolding in repo** (gated route, optional `maturity_assessment_pack_path`, tier/JWT hooks) — **full** questionnaire UX, scoring, persistence, and legal positioning remain **exploration / backlog** until product/legal review and private content import.

**Horizon / urgency:** `[H3]` or `[H4]` · `[U3]` for the **complete** product slice; active **feature** track for the **next code slice** (SQLite + responses) when scheduled.

**Synced with:** [PLANS_TODO.md](PLANS_TODO.md) (Backlog catalogue entry).

### Operator sequencing — prerequisites done; POC **A** in progress (code), **SQLite next**

**M-LOCALE-V1 (dashboard i18n):** ✅ **shipped on `main`** (**2026-04**) — path-prefixed HTML, `en` + `pt-BR` catalogs, negotiation. See [PLAN_DASHBOARD_I18N.md](completed/PLAN_DASHBOARD_I18N.md) and [PLANS_TODO.md](PLANS_TODO.md) (Dashboard i18n section).

**Version signal for testers (do not rely on git inference alone):** in-repo semver is **`1.7.1-beta`** ([VERSIONING.md](../VERSIONING.md) `-beta`); **last stable** published story remains **1.7.0** (Hub / GitHub Release). Callouts: [CHANGELOG.md](../../CHANGELOG.md), [docs/releases/1.7.1-beta.md](../releases/1.7.1-beta.md), README **Latest stable** vs **`main` pre-release**. Anyone pulling `main` for **formal** beta testing should use those files—not only `git log`.

**Are we on option A in code right now?** **Minimal scaffolding only:** `GET /{locale}/assessment` exists when **`api.maturity_self_assessment_poc_enabled`** is on and tier allows it (see `core/licensing/tier_features.py`); otherwise **404**. No questionnaire items, scoring, or persistence yet — the plan still compares full **A / B / C / D** product shapes.

**Next `feature` slice (when scheduled): POC architecture A** — first spike after the above prerequisites:

| Step | Architecture | Intent |
| --- | --- | --- |
| **1** | **A** — Routes under **`/{locale}/…/assessment`** + optional YAML pack ✅; **SQLite persistence + answers** ⬜ | **First** in-app spike: single app, same audit story; align with RBAC [#86](https://github.com/FabioLeitao/data-boar/issues/86) later. |
| **2** | **B** — Excel sheet + formula scoring | Fast tabular path; compare UX vs A for consultant workflows. |
| **3** | **C** — Companion app + API/SSO | Separation / white-label; evaluate **after** A/B learnings. |
| **4** | **D** — PDF/export-only narrative | Simplicity vs interactivity; last in the **comparison Colleague-Nn**, not “never”. |

**POC scaffolding (minimal, first PR for A):** feature-flag or **`dbtier`**-gated **placeholder** route + empty state + pointer to this plan — **no** proprietary questionnaire text in public repo; YAML pack under private or licensed pack later. Routes **must** use the same **`/{locale_slug}/…`** pattern as the rest of the dashboard HTML ([PLAN_DASHBOARD_I18N.md](completed/PLAN_DASHBOARD_I18N.md)).

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

## Risks and guardrails

- **Honesty / gaming:** Scores are only as good as inputs; position as **trend and conversation starter**, not compliance scorecard.
- **Scope creep:** Full GRC platforms are a product category—stay **thin**: questionnaire + export + optional history, not workflow replacement.
- **Legal:** Every surface: “not legal advice; not audit; not ANPD filing.”

## Open core vs commercial

- **Open core:** **No** — keep scanner/dashboard baseline OSS; ship assessment as **source-available / subscription** module, **or** separate paid app.
- **Subscription value:** Periodic re-assessment, trend charts, consultant “tenant” view—matches **partner SKUs** in [LICENSING_OPEN_CORE_AND_COMMERCIAL.md](../LICENSING_OPEN_CORE_AND_COMMERCIAL.md).

## Next steps (when revisiting — e.g. after token refill / calmer sprint)

1. **POC A (in progress):** gated `GET /{locale}/assessment` placeholder ✅ — next: **SQLite persistence** for responses (per session/tenant when model is clear), then **import** questionnaire from private DOCX → structured YAML (sections, weights, help text) **without** pasting proprietary wording into public Git.
2. Legal/commercial one-pager: positioning vs audit; consent for storing responses.
3. **Architecture lock:** spike **A** is the default path; revisit **C** only after A/B learnings — align with [PLAN_DASHBOARD_REPORTS_ACCESS_CONTROL.md](PLAN_DASHBOARD_REPORTS_ACCESS_CONTROL.md) and API key / future SSO (#86).
4. MVP: save responses + single **text/Markdown annex** in report bundle (narrative slot aligned with long-form / **[PLAN_PDF_GRC_REPORT.md](PLAN_PDF_GRC_REPORT.md)**-style reporting for **technical** findings — keep org vs technical streams distinct).

## Relationship to other plans

- **[PLAN_PRODUCT_TIERS_AND_OPEN_CORE.md](PLAN_PRODUCT_TIERS_AND_OPEN_CORE.md)** — subscription / partner tier boundaries; maturity assessment is **not** open core — enforcement phases **1+** apply when moving past POC/lab gates.
- **[PLAN_PDF_GRC_REPORT.md](PLAN_PDF_GRC_REPORT.md)** — **Scan output** PDF (exec + detailed + priority matrix); **not** the org self-assessment form — cross-sell in GRC narratives only.
- **[PLAN_SCOPE_IMPORT_FROM_EXPORTS.md](PLAN_SCOPE_IMPORT_FROM_EXPORTS.md)** — complementary “bootstrap from existing tools” story; assessment is **people/process**, scope import is **technical inventory**.
- **Dashboard RBAC / #86** — required if multi-user tenants fill forms.

---

*Created for operator recall after exploration in chat; revise or archive when superseded.*
