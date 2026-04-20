# PLAN: Organizational maturity self-assessment (GRC-style questionnaire)

<!-- plans-hub-summary: Deferred exploration: optional LGPD/compliance maturity questionnaire + scoring—companion to technical scans; not legal audit. -->
<!-- plans-hub-related: PLAN_DASHBOARD_REPORTS_ACCESS_CONTROL.md, LICENSING_OPEN_CORE_AND_COMMERCIAL.md (future tier features), PLAN_SCOPE_IMPORT_FROM_EXPORTS.md (inventory bootstrap narrative) -->

**Status:** Exploration / backlog — **no implementation commitment** until product/legal review and operator import of source questionnaire content.

**Horizon / urgency:** `[H3]` or `[H4]` · `[U3]` catalogue (revisit after higher-priority scanner/dashboard/security work).

**Synced with:** [PLANS_TODO.md](PLANS_TODO.md) (Backlog catalogue entry).

### Operator sequencing (2026-04) — architecture options A–D

**Are we on option A in code right now?** **No.** There is **no** GRC/maturity route shipped yet; the plan only compares **A / B / C / D**. The **next agreed `feature` session** is **[M-LOCALE-V1](PLAN_DASHBOARD_I18N.md)** (path-prefixed HTML + `en` / `pt-BR`) **before** [#86](https://github.com/FabioLeitao/data-boar/issues/86) Phase 1 — see Integration / WIP in [PLANS_TODO.md](PLANS_TODO.md).

**When GRC POC work starts (after M-LOCALE-V1 unless reprioritised):**

| Step | Architecture | Intent |
| --- | --- | --- |
| **1** | **A** — New dashBOARd routes (`/…/assessment` once locale prefix exists) + SQLite persistence | **First** in-app spike: single app, same audit story; align with RBAC/#86 later. |
| **2** | **B** — Excel sheet + formula scoring | Fast tabular path; compare UX vs A for consultant workflows. |
| **3** | **C** — Companion app + API/SSO | Separation / white-label; evaluate **after** A/B learnings. |
| **4** | **D** — PDF/export-only narrative | Simplicity vs interactivity; last in the **comparison Colleague-Nn**, not “never”. |

**POC scaffolding (minimal, when scheduled):** feature-flag or **`dbtier`**-gated **placeholder** route + empty state + pointer to this plan — **no** proprietary questionnaire text in public repo; YAML pack under private or licensed pack later. Prefer **`/{locale}/…/assessment`** once **M-LOCALE-V1** lands so paths are not rewritten twice.

**Operator deferral (confirmed):** GRC scaffolding is **not** part of the **M-LOCALE-V1** slice — schedule as the **next `feature` session after** [M-LOCALE-V1](PLAN_DASHBOARD_I18N.md) merges, unless the operator reprioritises.

**Remember:** proceed **A → B → C → D** as **evaluation spikes**, not four full products—pick one shipping path after spikes unless counsel/commercial demands otherwise.

## Problem statement

Operators and consultants need **organizational** visibility (roles, processes, awareness) alongside **technical** inventory from Data Boar. A structured **self-assessment** (not audit, not legal advice) can raise maturity and align teams (DPO, IT, cyber, compliance, HR, contracts, customer-facing) with preparation for LGPD and related frameworks—**if** answers are sincere and the instrument is clearly framed as **consciousness-raising** only.

**Source material:** Maintainer-authored questionnaire (historically a **DOCX** in an LGPD working folder, plus spreadsheet “gabarito” / scoring logic). **Not** in the public repo until curated; expect **`docs/private/`** or a licensed commercial content pack for paid tiers.

**Operator workspace (confirmed — not public Git):** `docs/private/raw_pastes/general/LGPD_DOCS/` contains the working **DOCX** (diagnóstico / índice de adequação à LGPD, level bands), **XLSX** metric/scoring example, and additional **inventory / mapping** spreadsheets usable as **design inspiration** for future report shapes and scope hints—**do not** paste proprietary wording into tracked files. For agent ingestion in future sessions: keep files in that folder or export **structured** excerpts (YAML/CSV of questions + weights) to the same tree; **DOCX/XLSX** are readable via tools/scripts on the workstation even when Cursor’s file **glob** skips gitignored paths.

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

**Recommendation for first spike (when promoted):** prototype **C** or **A** behind **feature flag + license claim**; keep question YAML/JSON in a **content pack** repo or private submodule so **LGPD vs ISO 27701 vs hybrid** = different packs without forking the engine.

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

1. Import and normalize questionnaire from DOCX → structured YAML (sections, weights, help text).
2. Legal/commercial one-pager: positioning vs audit; consent for storing responses.
3. Choose architecture **A vs C**; if **A**, align with [PLAN_DASHBOARD_REPORTS_ACCESS_CONTROL.md](PLAN_DASHBOARD_REPORTS_ACCESS_CONTROL.md) and API key / future SSO.
4. MVP: save responses + single **text/Markdown annex** in report bundle (similar narrative slot to “vulnerability-style” long-form report plans).

## Relationship to other plans

- **[PLAN_SCOPE_IMPORT_FROM_EXPORTS.md](PLAN_SCOPE_IMPORT_FROM_EXPORTS.md)** — complementary “bootstrap from existing tools” story; assessment is **people/process**, scope import is **technical inventory**.
- **Dashboard RBAC / #86** — required if multi-user tenants fill forms.

---

*Created for operator recall after exploration in chat; revise or archive when superseded.*
