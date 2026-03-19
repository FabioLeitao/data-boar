# Consolidated plans – sequential to-dos

Plan files are kept in **English only** for history and progress tracking. Operator-facing documentation (how to use, config, deploy, etc.) exists in both EN and pt-BR; see [README.md](README.md) ([pt-BR](README.pt_BR.md)).

This document is the **single source of truth** for the project's plan status and remains in **`docs/plans/`** at all times. It lists **incomplete goals** from active plans and the **recommended sequential to-dos** to achieve them. Completed plan documents are archived in **`docs/plans/completed/`** for reference; links below point to those files.

**Token-aware work:** When context or token limits apply (e.g. after an initial Pro+ burst), prefer **one plan or one to-do per session**; open only the files needed for that step. See **[TOKEN_AWARE_USAGE.md](TOKEN_AWARE_USAGE.md)** for short vs long-term goals, artifact references (Docker Hub, `docs/private/`), and one-session workflow.

**Safety / IP / profitability burst:** When protecting revenue or reducing public exposure matters more than token savings for a short period, use **Priority band A** below first, then return to the token-aware table. See **[CODE_PROTECTION_OPERATOR_PLAYBOOK.md](../CODE_PROTECTION_OPERATOR_PLAYBOOK.md)** for phased steps and copy-paste prompts for the agent.

**Policy:** When implementing a plan step, **update documentation** (USAGE, TECH_GUIDE, SECURITY, or dedicated docs) and **add or run tests** as the feature is implemented. After completing or adding to-dos, **update this file and the plan file** so progress is tracked in one place. All steps are intended to be **non-destructive**, **non-regression**, and **tested** before marking done.

## Status taxonomy (horizon + urgency)

Use these tags in headings to keep priorities explicit and machine-countable:

- Horizons: `[H0]` must-do-now, `[H1]` short-term, `[H2]` medium-term, `[H3]` long-term/production-ready milestone, `[H4]` far horizon (post-lato/master's scenario), `[H5]` dream horizon (PhD thesis scenario).
- Urgency: `[U0]` security/safety now, `[U1]` low-AI/high-gain soon, `[U2]` not critical next, `[U3]` backlog/catalogue.

<!-- PLANS_STATUS_DASHBOARD:START -->
## Status dashboard (auto-generated)

Do not edit this block manually; refresh with `python scripts/plans-stats.py --write`.

- **Status rows counted:** 87  (Done: 43 | Incomplete: 44)
- **Incomplete breakdown:** Pending `⬜`=42, Tracked `🔄`=2, Under consideration=0, Backlog-marked rows=1

| Horizon | Total rows | Done | Incomplete |
| ------- | ----------: | ----: | ----------: |
| `H0` | 19 | 16 | 3 |
| `H1` | 0 | 0 | 0 |
| `H2` | 0 | 0 | 0 |
| `H3` | 68 | 27 | 41 |
| `H4` | 0 | 0 | 0 |
| `H5` | 0 | 0 | 0 |
| `UNSPECIFIED` | 0 | 0 | 0 |
<!-- PLANS_STATUS_DASHBOARD:END -->

**Plan status:** Corporate compliance ✅ · Minor data detection ✅ · Aggregated identification ✅ · Sensitive categories ML/DL ✅ · Rate limiting ✅ · Web hardening ✅ · Logo and naming ✅ · **Security hardening** ✅ Done (Tier 1) · **Secrets/vault** ✅ Phase A done (Tier 1) · **Configurable timeouts** ✅ Done · **Commercial licensing (runtime + docs + issuer bootstrap)** ✅ Phase 1 in repo (see `docs/LICENSING_SPEC.md`, `core/licensing/`); operational hardening ⬜ Priority band A · **Version check & self-upgrade** ⬜ Not started · **Additional compliance samples** ✅ Done · **Compliance standards alignment (ISO/IEC 27701, FELCA)** ✅ Done (doc only) · **Additional detection techniques & FN reduction** 🔄 Slices 1–3 done (+ optional `fuzzy_column_match` / `FUZZY_COLUMN_MATCH`); next: plan §4 format hints / aggregated wording, etc. · **Compressed files** ✅ Done (steps 1–12; follow-ups 13–14 optional) · **Content type & cloaking detection** ✅ Core plan done (optional: man pages / OpenAPI examples) · **Data source versions & hardening** ⬜ Not started · **Strong crypto & controls validation** ⬜ Not started · **CNPJ alphanumeric format validation** ✅ Phase 4 done (Phase 5 checksum future) · **Selenium QA test suite** ⬜ Not started · **Synthetic data & confidence validation** ⬜ Not started · **Notifications (off-band + scan-complete)** ⬜ Not started · **Dashboard i18n** ⬜ Under consideration · **SAP connector** ⬜ Not started · **Additional data soup formats** ⬜ Backlog (catalogue)

### Commercial licensing — future reminder (partner / tiered SKUs)

When revising **license terms** for IP, commerciality, and profitability, explicitly design **multiple SKUs** (e.g. **direct end-user commercial** vs **partner / pro / enterprise**—names TBD) so **consulting partners** can deliver to **their customers** under a **partner-appropriate** subscription and price point, with different objectives and cost-to-serve (analogous to tiered DB licensing: Express / Standard / Enterprise / options). **Legal + pricing first;** then JWT claims and runtime enforcement. Documented in [LICENSING_OPEN_CORE_AND_COMMERCIAL.md](../LICENSING_OPEN_CORE_AND_COMMERCIAL.md) and [LICENSING_SPEC.md](../LICENSING_SPEC.md) (future extensions).

**Brand and experience IP (same pass):** Include **mascot**, **Data Boar / dashBOARd** naming, **data soup** metaphor and connector narrative, **UI/report appearance**, documented **operation** (CLI/API/Docker story), and **companion artifacts** (Docker image branding, website, related repos) in trademark and commercial-license review — see [LICENSING_OPEN_CORE_AND_COMMERCIAL.md § Brand, narrative, and experience IP](../LICENSING_OPEN_CORE_AND_COMMERCIAL.md#brand-narrative-and-experience-ip-inventory-for-counsel-and-commercial-policy) and [COPYRIGHT_AND_TRADEMARK.md](../COPYRIGHT_AND_TRADEMARK.md#6-brand-narrative-and-product-experience-inventory).

---

## Conflict and dependency analysis

| Plan                                     | Depends on                      | Conflicts with | Notes                                                                                                                         |
| ----                                     | ----------                      | -------------- | -----                                                                                                                         |
| Security hardening                       | —                               | None           | Additive (validation, docs, audit). Do first to strengthen base.                                                              |
| Secrets vault                            | —                               | None           | Phase A (redact, env) improves config safety before vault.                                                                    |
| Version check / self-upgrade             | —                               | None           | Backup excludes secrets (manifest); compatible with Secrets A. Optional Phase 9: .deb, apt repo, signing, bytecode-only (see plan §9). |
| Additional compliance samples            | —                               | None           | Config-only; samples and docs additive.                                                                                       |
| Compressed files                         | Config loader (new keys)        | None           | Additive feature; optional dependency py7zr.                                                                                  |
| Content type & cloaking detection        | —                               | None           | Opt-in magic-byte/MIME detection for renamed/cloaked files; more I/O/CPU; steganography out of scope for v1.                   |
| Dashboard i18n                           | Approach decided                | None           | No concrete to-dos until routing/translation approach chosen.                                                                 |
| Data source versions & hardening         | —                               | None           | Additive: new table data_source_inventory, new report sheets; optional CVE lookup.                                            |
| Strong crypto & controls validation      | —                               | None           | Optional flag (CLI + dashboard); new table or extend inventory; report sheet "Crypto & controls"; inference best-effort.      |
| CNPJ alphanumeric format validation      | —                               | None           | Format spec + regex/override; optional built-in or config flag; compatibility report; no change to legacy LGPD_CNPJ.          |
| Selenium QA test suite                   | —                               | None           | On-demand; optional [qa] deps; tests_qa/; report + recommendations; exclude from default pytest.                              |
| Synthetic data & confidence validation   | —                               | None           | Fixtures (files, SQL, NoSQL, shares); FP/FN + ground truth; confidence bands + operator guidance; timeouts/connectivity docs. |
| Configurable timeouts                    | —                               | None           | Global + per-target connect/read timeouts; sane defaults; connector wiring; recommendations (avoid DoS, too-fast).            |
| Notifications (off-band + scan-complete) | Optional: Secrets Phase A       | None           | Webhook notifier; scan-complete brief to operator/tenant (Slack, Teams, Telegram, etc.); recommendations.                     |
| SAP connector                            | Optional: Configurable timeouts | None           | Add SAP (HANA/OData/RFC) to data soup; same discovery/sample/finding flow; optional [sap] extra. See PLAN_SAP_CONNECTOR.      |
| Additional data soup formats             | Optional: Compressed, content-type | None        | Catalogue: epub, parquet, avro, dbf; rich media (images, audio, video) as stego containers; metadata-only or stego phase. See PLAN_ADDITIONAL_DATA_SOUP_FORMATS. |
| Additional detection techniques & FN reduction | Optional: Synthetic data (for validation) | None        | Additive: optional engines (fuzzy, stemming, format hint, embedding prototype); config thresholds; “suggested review”; reduce false negatives. See PLAN_ADDITIONAL_DETECTION_TECHNIQUES_AND_FN_REDUCTION. |
| Home lab validation (production-readiness)   | Optional: –1/–1b maintenance in acceptable state | None | Manual second-machine smoke per [HOMELAB_VALIDATION.md](../HOMELAB_VALIDATION.md); proves deploy + ≥1 connector path before demo/customer confidence; low token. |
| Compliance standards alignment           | —                               | None           | Doc only: ISO/IEC 27701 (PIMS), FELCA (minor data); COMPLIANCE_FRAMEWORKS + roadmap sentence; no code. See PLAN_COMPLIANCE_STANDARDS_ALIGNMENT. |

**Regression and tests:** No plan modifies wipe behaviour, SQLite schema (except Self-upgrade adds optional upgrade_log, Data source versions adds data_source_inventory, Strong crypto adds optional crypto_controls_audit or extends inventory), or existing config keys in a breaking way. New tests per plan must pass together with the full suite (`uv run pytest -v -W error`). Document each new feature in the relevant docs (EN + pt-BR where applicable).

---

## Review and sequence rationale

The recommended order below is chosen to:

- **Strengthen the base first:** Security hardening and Configurable timeouts reduce risk and improve robustness for all later work. **Both are already completed.**
- **Respect dependencies:** Secrets Phase A (redact, env) before Phase B (vault); Notifications can optionally use Secrets A for webhook URLs. **Phase A is completed; Phase B is deferred to a later billing cycle unless extra capacity is available.**
- **Batch additive features:** Compliance samples, Compressed files, Data source versions, and Strong crypto add config/report/sheets without breaking existing flows. **Near-term focus is on small, high-leverage slices of these plans.**
- **Defer optional or heavy work:** Version check, Selenium QA, Synthetic data, Notifications (later phases), SAP connector, Dashboard i18n, and Additional data soup formats come after core security and scan/report features or when more usage budget is available.

## Tier summary (for planning):

- **Priority band A – Safety, IP exposure, profitability guardrails (do before resuming heavy token-aware feature slices when critical):** See table **“Priority band A”** below — Dependabot/Scout, Docker Hub tag hygiene, private issuer repo, partner access, optional `license-smoke` CI, legal/license boundary review. Does not replace cryptographic licensing; complements it.
- **Tier 1 – Foundation (completed):** Security hardening, Configurable timeouts, Secrets Phase A.
- **Tier 2 – Scan and report (in progress, token-efficient slices first):** Compressed files, Content type & cloaking detection, Data source versions & hardening, Strong crypto & controls, Compliance samples (completed), SAP connector (later).
- **Tier 3 – Secrets and upgrade (deferred unless extra capacity):** Secrets Phase B, Version check & self-upgrade.
- **Tier 4 – Validation and ops (partial, high-value slices first):** CNPJ alphanumeric, Additional detection techniques & FN reduction, **Home lab smoke** (order **–1L**, after maintenance), Notifications (early phases), Selenium QA, Synthetic data & confidence, Dashboard i18n.

Plans without dependencies can be run in parallel within a tier (e.g. 4 and 5). Within a plan, execute phases in order.

---

## Recommended sequence (aggregated, token-aware)

The list below is ordered for the current billing cycle, with a focus on:

- **Near-term, high-value work** that fits in the remaining Pro usage.
- **AI-heavy** tasks where the agent’s help is most valuable.
- **Manual-friendly** tasks that you can do largely by hand or with existing tooling.

### H0/U0 Priority band A — Safety, security, IP exposure, profitability (sequence when critical)

Complete **in order** when you need to reduce public artifact exposure or tighten commercial posture **before** burning tokens on large feature work. Most steps are **manual on GitHub/Docker Hub** + short doc updates; use the agent for checklists, scripts, and repo docs.

| Step | Task | Owner | Done when |
| ---- | ---- | ----- | ---------- |
| **A1** | **Dependabot / dependency alerts** | You + agent (PRs) | Alerts triaged; safe merges; `pyproject.toml` + lockfiles + `requirements.txt` aligned; `.\scripts\check-all.ps1` green. Same as order **–1** in the table below. |
| **A2** | **Docker Scout / image CVEs** | You + agent (Dockerfile) | `docker scout quickview` acceptable or documented exceptions; image rebuilt; smoke test. Same as **–1b**. |
| **A3** | **Docker Hub tag hygiene** | **You (manual Hub UI)** | Obsolete tags deleted or documented; only supported tags documented in [DEPLOY.md](../deploy/DEPLOY.md) §8; CI/partners confirmed not pinning removed tags. |
| **A4** | **Private repo for issuer tooling** | **You** | `tools/license-studio` copied to a **private** GitHub/GitLab repo; no signing keys in any public remote; README/runbook only in private or `docs/private/`. |
| **A5** | **Partner access (e.g. Ivan)** | **You** | Collaborator role on private repos as needed; no shared personal secrets via chat. |
| **A6** | **Licensing smoke automation** | Agent | `scripts/license-smoke.ps1` (or pytest slice) documented; optional CI job — token-aware single session. |
| **A7** | **Legal / license boundary** | **You + counsel** | Open-core vs commercial terms documented; no repo change required for first call. |

After **A1–A3** (minimum), you can **resume token-aware pace** on Tier 2 features (e.g. content-type Step 4) unless A4–A7 are blocking revenue.

**Reference:** [CODE_PROTECTION_OPERATOR_PLAYBOOK.md](../CODE_PROTECTION_OPERATOR_PLAYBOOK.md), [LICENSING_SPEC.md](../LICENSING_SPEC.md), [HOSTING_AND_WEBSITE_OPTIONS.md](../HOSTING_AND_WEBSITE_OPTIONS.md).

**Home lab (production-readiness gate):** Sequenced as **order –1L** in the table below—run **after –1/–1b** when deps/image are in an acceptable state, **before** treating a build as demo/customer-ready without a second environment. Playbook: [HOMELAB_VALIDATION.md](../HOMELAB_VALIDATION.md) ([pt-BR](../HOMELAB_VALIDATION.pt_BR.md)). Manual on your hardware; does not replace pytest/CI.

### What to start next (by recommended execution under token constraints)

**Order = smallest-scope, high-value first.** Pick one when you're ready to implement; each can be done in one or a few sessions.

| Order | Plan | Why this order (scope / value) |
| ----- | ---- | ------------------------------ |
| –1 | **Dependabot & GH bots (security/maintenance)** | **Do early:** Review [Security → Dependabot alerts](https://github.com/FabioLeitao/data-boar/security/dependabot) and open Dependabot PRs. Apply only safe updates: edit `pyproject.toml` (or accept Dependabot PR), then `uv lock`, `uv export --no-emit-package pyproject.toml -o requirements.txt`, commit all three, run `.\scripts\check-all.ps1`. Merge only after CI green. See SECURITY.md (Dependabot SLAs, dependency policy). |
| –1b | **Docker Hub Scout (image CVEs)** | **Do early, after Dependabot:** Run `docker scout quickview fabioleitao/data_boar:latest` (or `:1.6.2`) locally, or use [Docker Hub → data_boar → Tags → Scout](https://hub.docker.com/r/fabioleitao/data_boar) for the image. Fix by: bump base image in Dockerfile (e.g. `python:3.12-slim` to a digest or newer tag), and/or apply dependency updates (Dependabot); rebuild, re-scan with Scout, run `.\scripts\check-all.ps1` and a quick container smoke test. Merge only when tests pass and Scout findings are acceptable or resolved. Token-aware: one session for Scout review + one round of fixes. |
| –1L | **Home lab — production-readiness smoke** | **When:** After –1/–1b are acceptable (or exceptions documented)—you are **ready to invest half a day on a second machine** (VM/container host), not before. **What:** Run [HOMELAB_VALIDATION.md](../HOMELAB_VALIDATION.md) §1 baseline (clone, tests, `docker build`, config, run, idle scan) **plus** at least one connector slice (e.g. §2 synthetic filesystem or §3 SQLite). **Why:** Catches deploy/config gaps CI cannot see; high gain for production confidence; **manual, low AI tokens** (agent only for doc fixes if you find gaps). |
| 0 | **Compliance standards alignment (ISO/IEC 27701, FELCA)** | Doc only: COMPLIANCE_FRAMEWORKS + roadmap; no code; smallest scope; supports pitch and audit narrative. ✅ Done |
| 1 | **CNPJ alphanumeric format validation** | Research + regex + doc (Phase 1); focused, no schema change; high value for BR compliance. ✅ Phase 4 done |
| 2 | **Content type & cloaking detection** | Steps 1–6 done (CLI `--content-type-check`, `POST /scan` `content_type_check`, dashboard checkbox, tests, USAGE/TECH_GUIDE). Optional follow-ups: man pages, OpenAPI examples. |
| 3 | **Additional detection techniques & FN reduction** | ✅ Slices 1–3 + **aggregated cross-ref sample note** (Excel + recommendation text). **Next (token-aware):** plan priority 4 — format/length hints from connectors. |
| 4 | **Strong crypto & controls validation** | Phase 1: CLI flag, config, API/dashboard checkbox, engine wiring (no criteria yet); then Phase 2 adds criteria. |
| 5 | **Data source versions & hardening** | Phase 1: `data_source_inventory` schema + save + one connector (e.g. SQL) + report sheet; one clear slice. |
| 6 | **Notifications (off-band + scan-complete)** | Phase 1: config shape + notifier module + one channel (e.g. webhook); docs and examples; medium scope. |

**Deferred (larger or later):** Secrets Phase B, Version check & self-upgrade (incl. optional Phase 9: .deb/apt repo, signed packages, bytecode-only install, winget-like), Selenium QA, Synthetic data, SAP connector, Dashboard i18n. **Backlog:** Additional data soup formats.

#### Resume next session (security/maintenance first, then feature work)

**If you have an open PR** with the latest plan edits (Dependabot/Scout to-dos, self-upgrade §9 .deb/apt/bytecode, **deb name availability and deps for easy deployment**): merge when ready, then continue below.

**If IP / Docker / profitability is urgent:** run **Priority band A** (table above) through at least **A3** before deep feature work; say *“Priority band A, step Ax”* to the agent (see playbook).

1. **Dependabot (order –1):** On GitHub go to **Security → Dependabot**. There are open alerts (e.g. pyOpenSSL, PyJWT, pypdf, SonarQube action). For each: either merge an existing Dependabot PR after local `check-all` and CI pass, or update `pyproject.toml` (and Actions in `.github/workflows` if needed), then `uv lock`, `uv export --no-emit-package pyproject.toml -o requirements.txt`, commit `pyproject.toml` + `uv.lock` + `requirements.txt`, run `.\scripts\check-all.ps1`, push and merge. One PR per ecosystem (pip vs github-actions) is enough; batch non-security updates if desired.
2. **Docker Hub Scout (order –1b):** Run **`docker scout quickview fabioleitao/data_boar:latest`** locally (or open Docker Hub → repo **data_boar** → Tags → Scout for the image). If there are CVEs: update Dockerfile base image (e.g. `python:3.12-slim` to a digest or newer tag) and/or rely on Dependabot dependency updates; rebuild image, run Scout again, then `.\scripts\check-all.ps1` and a quick container smoke test. Merge only when tests pass and Scout is acceptable. Do one Scout review + one round of fixes per session (token-aware).
3. **CodeQL:** Runs on push/PR to main; weekly schedule. No action unless **Security → Code scanning** shows new findings; then fix and re-run.
4. **After bots and Scout are green:** Either run **order –1L** (home lab) if you want second-environment proof before the next feature burst, or continue the table: **Content type** optional follow-ups, **FN reduction** plan §4 (format hints), **Strong crypto** Phase 1, or **Data source versions** Phase 1.
5. **Study (your task):** CWL paid courses are listed and prioritised in [PORTFOLIO_AND_EVIDENCE_SOURCES.md](PORTFOLIO_AND_EVIDENCE_SOURCES.md) §3.2 and in `docs/private/Learning_and_certs.md`. Recommended order: BTF → C3SA → MCBTA → PTF → …; one cert at a time. Slot fixed study blocks (e.g. 1–2 sessions/week) after one feature slice; don’t mix deep study with same-day agent-heavy coding (token-aware). **After lato sensu:** post-lato options (stricto sensu, Faculdade HUB MBA IA, Universidade do Intercâmbio) are in PORTFOLIO §4.2; choose one when ready – no need to open all academic plans in one session.

### Compliance standards alignment (ISO/IEC 27701, FELCA) – [PLAN_COMPLIANCE_STANDARDS_ALIGNMENT.md](PLAN_COMPLIANCE_STANDARDS_ALIGNMENT.md)

Doc-only; supports pitch and audit narrative. No code changes.

| # | To-do                                                                                                 | Status    |
| - | -----                                                                                                 | ------    |
| 1 | Add subsection "Auditable and management standards" in COMPLIANCE_FRAMEWORKS.md (EN); link to plan.  | ✅ Done   |
| 2 | Add equivalent subsection in COMPLIANCE_FRAMEWORKS.pt_BR.md.                                         | ✅ Done   |
| 3 | Update roadmap sentence in README.md (ISO/IEC 27701, FELCA, auditable/regional standards).                 | ✅ Done   |
| 4 | Update roadmap sentence in README.pt_BR.md equivalently.                                              | ✅ Done   |
| 5 | PLANS_TODO: plan status, dependency row, "What to start next" order 0, this to-do block.              | ✅ Done   |

### Wabbix 2026-03-18 — evolution review (9.1/10) and follow-ups

External review PDF (local): `docs/feedbacks, reviews, comments and criticism/analise_evolucao_data_boar_2026-03-18.pdf`. **In-repo tracking:** [WABBIX_ANALISE_2026-03-18.md](WABBIX_ANALISE_2026-03-18.md).

| Follow-up | Status | Notes |
| --------- | ------ | ----- |
| KPI panel (release / CI / security ops) | ⬜ Backlog (**W-KPI**) | GitHub Insights / manual dashboard; low AI, ops cadence. |
| Contract tests (reports + critical APIs) | ✅ Done (**W-CONTRACT**) | Report/heatmap artifacts regression: `tests/test_report_trends.py`; API/OpenAPI contract responses: `tests/test_routes_responses.py`. |
| Decouple detector/report rules | 🔄 Incremental (**W-DECOUPLE**) | Small modules (e.g. fuzzy helper); Sonar complexity gates. |
| Doc snapshot per release | ✅ Baseline | `docs/releases/X.Y.Z.md` per version; optional “frozen bundle” → backlog. |
| Security vuln triage routine | 🔄 Tracked | Priority band **A1–A3**, `scripts/maintenance-check.ps1`, `SECURITY.md`. |
| Aggregated “incomplete sample” wording | ✅ Done | Cross-ref sheet note row + recommendation text. |
| Staging fuzzy config | ✅ Example | `deploy/config.staging.example.yaml`, `deploy/STAGING_CONFIG.md`. |

### Secure default host binding (Wabix P0/P1 follow-up)

Tighten runtime defaults for the API host. Implemented: default `127.0.0.1`, opt-in `0.0.0.0` via `api.host`, docs and tests.

| # | To-do                                                                                                                                                | Status    |
| - | -----                                                                                                                                                | ------    |
| 1 | Default host loopback for desktop: make the API bind to `127.0.0.1` by default when running as a normal process (CLI/desktop).                      | ✅ Done   |
| 2 | Explicit opt-in for `0.0.0.0`: only bind to all interfaces when explicitly requested in config/CLI, or in container entrypoints where it is fenced. | ✅ Done   |
| 3 | Docs: add a short note in `USAGE.md` / `USAGE.pt_BR.md` and `deploy/DEPLOY*.md` explaining the difference and safer recommended host settings.      | ✅ Done   |
| 4 | Tests: add 1–2 small tests around API startup config (host value chosen from config vs CLI) to avoid regressions in future releases.               | ✅ Done   |

### Documentation and sync reminders

- **pt-BR translation review:** When syncing EN → pt-BR, review for **naturalness** and meaning-equivalent wording; avoid overly literal transposition that can sound artificial. Schedule a pass over key docs (README.pt_BR, USAGE.pt_BR, DEPLOY.pt_BR, SENSITIVITY_DETECTION.pt_BR, etc.) when capacity allows.
- **Legacy branches cleanup reminder:** When we have maintenance time, tidy `python2-lgpd-crawler-legacy-and-history-only` branches (verify no active work depends on them, then delete/close/retire them).

### H1/U1 A. Near-term focus (current billing cycle)

0. **Home lab validation (order –1L)** *(manual, high gain for prod readiness)* — After Dependabot/Scout are under control, execute [HOMELAB_VALIDATION.md](../HOMELAB_VALIDATION.md) on a second machine; no feature code unless you document a gap. Prefer this **before** staking reputation on “it runs anywhere” demos.

1. **CNPJ alphanumeric format validation** *(AI-assisted research + manual wiring)*
   - Use AI for: research/spec for alphanumeric format, regex proposal, EN + pt-BR doc wording.
   - Do manually: integrate regex/overrides, wire to existing detection/reporting, add tests.

2. **Content type & cloaking detection – Step 1** *(small slice)*
   - Magic-byte table + read_magic / infer_content_type for supported formats; no connector change yet.

3. **Data source versions & hardening – schema and report design** *(AI-heavy design, light implementation)*
   - Use AI for: `data_source_inventory` schema, inventory/report sheet layout, design for one reference connector.
   - Do manually: implement that connector incrementally; add others in later cycles.

4. **Strong crypto & controls validation – criteria + wording** *(AI-heavy criteria/report, manual plumbing)*
   - Use AI for: strong-crypto matrix per connector type, “Crypto & controls” sheet layout, disclaimers.
   - Do manually: add CLI/config flag, implement persistence for one connector, basic tests.

5. **Additional detection techniques & FN reduction – next slices** *(mixed)*
   - Done in repo: MEDIUM threshold, suggested review, `column_name_normalize_for_ml`, multi-connector persist LOW ID-like.
   - Use AI for: fuzzy-match design (plan §3), aggregation wording, optional format hints.
   - Do manually: config + detector wiring, tests, docs (EN + pt-BR).

6. **Notifications (off-band + scan-complete) – Phase 1 only** *(AI for schema/templates, manual implementation)*
   - Use AI for: notifications config shape, notifier interface, initial message templates for CI/script usage.
   - Do manually: notifier module, config parsing, basic docs and examples; later phases after reset.

### H2/U2 B. Deferred to after billing reset (or if on-demand spend is enabled)

0. **Wabbix backlog (token-aware, non-blocking)** — **W-KPI:** release/CI KPI view. (W-CONTRACT already covered by existing contract tests for reports + OpenAPI responses.) Pick one small slice when maintenance is green.
1. **Secrets vault – Phase B** – full vault implementation, re-import CLI/web, optional remove-from-config, and key management docs.
2. **Version check & self-upgrade** – version fetch, CLI/API, backup/restore, container detection, audit log.
3. **Selenium QA test suite** – full UI automation suite, stress tests, QA reports.
4. **Synthetic data & confidence validation** – fixtures across all formats, precision/recall tooling, confidence bands in reports (feeds **W-CONTRACT**).
5. **SAP connector** – research, connector module for HANA/OData/RFC, docs and tests.
6. **Dashboard i18n** – routing and translation strategy decision, then implementation.

### H3/U3 C. Backlog (catalogue)

**Additional data soup formats:** [PLAN_ADDITIONAL_DATA_SOUP_FORMATS.md](PLAN_ADDITIONAL_DATA_SOUP_FORMATS.md) – additional formats (epub, parquet, avro, dbf) and rich media / steganography containers (images, audio, video). Prioritise after compressed + content-type; stego as optional future phase.

**Brand micro-copy reminder (dashBOARd):** Revisit whether/how to label the **web dashboard** with the recommended sub-brand nickname `dashBOARd` (while keeping the decision-maker pitch unchanged). Keep changes low-noise and professional: prefer page title/header parenthetical (and minimal doc mentions in technical overview / USAGE / TECH_GUIDE). If we apply it, also update version bump / release notes accordingly. Status: ✅ Implemented (nav + About); revisit on next minor bump if needed.

- **H4/U3 far horizon (post-lato / master's scenario):** Master's degree path and related portfolio milestones can be tracked here when activated. Status: ⬜ Backlog.
- **H5/U3 dream horizon (PhD thesis scenario):** PhD thesis-aligned research/roadmap items can be tracked here when activated. Status: ⬜ Backlog.

---

## Open plans and to-dos (summary)

### Additional detection techniques & false-negative reduction – [PLAN_ADDITIONAL_DETECTION_TECHNIQUES_AND_FN_REDUCTION.md](PLAN_ADDITIONAL_DETECTION_TECHNIQUES_AND_FN_REDUCTION.md)

| Priority | To-do                                                                                                                       | Status    |
| -------- | --------------------------------------------------------------------------------------------------------------------------- | ------    |
| 1        | Configurable MEDIUM threshold; “suggested review” in report for ID-like columns classified LOW                               | ✅ Done (MEDIUM via `sensitivity_detection.medium_confidence_threshold`; `detection.persist_low_id_like_for_review` on SQL, Snowflake, MongoDB, Redis, Dataverse, Power BI, REST + sheet **Suggested review (LOW)**; see SENSITIVITY_DETECTION.md) |
| 2        | Stemming/normalisation for column names in ML/term matching                                                                 | ✅ Done (`sensitivity_detection.column_name_normalize_for_ml`: accent + separators for ML/DL only; see SENSITIVITY_DETECTION.md, `tests/test_column_name_ml_normalize.py`) |
| 3        | Optional fuzzy column name match (e.g. rapidfuzz) in confidence band 25–45 → MEDIUM + FUZZY_COLUMN_MATCH                   | ✅ Done (`sensitivity_detection.fuzzy_column_match`, extra `detection-fuzzy`, `FUZZY_COLUMN_MATCH`; see SENSITIVITY_DETECTION.md) |
| 4        | Data type/length hint from connectors → optional format hint in detector; MEDIUM suggestion when format suggests ID        | ✅ Done (initial slice: `connector_format_id_hint`, `FORMAT_LENGTH_HINT_ID`, `tests/test_format_length_hint.py`; extend INT/email/REST later) |
| 5        | Embedding prototype similarity (reuse DL embedder) as optional semantic hint                                               | ⬜ Pending |
| 6        | Region-specific column dictionaries (config); FK/table context where connector exposes schema                              | ⬜ Pending |
| 7        | Validation: ground-truth fixtures, baseline recall; per-technique FN/FP metrics; docs                                       | ⬜ Pending |
| 8        | Aggregated/incomplete: report wording – state results based on sampled data, human confirmation recommended               | ✅ Done (first row on **Cross-ref data – ident. risk** + `AGGREGATED_IDENTIFICATION` recommendation text; `report/generator.py`) |
| 9        | Aggregated/incomplete: verify MEDIUM and PII_AMBIGUOUS contribute to aggregation; document                                 | ✅ Done (`PII_AMBIGUOUS` → `other` in `DEFAULT_PATTERN_CATEGORY_MAP`; documented in [WABBIX_ANALISE_2026-03-18.md](WABBIX_ANALISE_2026-03-18.md)) |
| 10       | Aggregated/incomplete: optional "incomplete data" mode (lower min_categories, report note)                                 | ⬜ Pending |
| 11       | Aggregated/incomplete: optional single high-risk category "suggested review"                                                | ⬜ Pending |

---

### Notifications (off-band + scan-complete) – [PLAN_NOTIFICATIONS_OFFBAND_AND_SCAN_COMPLETE.md](PLAN_NOTIFICATIONS_OFFBAND_AND_SCAN_COMPLETE.md)

| Phase   | To-do                                                                                                                                    | Status    |
| -----   | -----                                                                                                                                    | ------    |
| 1.1–1.3 | notifications config; notifier module (webhook, Slack, Teams, Telegram); doc Part A (task/milestone from CI or script)                   | ⬜ Pending |
| 2.1–2.4 | Scan-complete summary (totals, HIGH/MEDIUM/LOW, DOB minor, failures); trigger after report gen (CLI + web); “how to download” in message | ⬜ Pending |
| 3.1–3.3 | Tenant notification; multi-channel; retry and rate limit                                                                                 | ⬜ Pending |
| 4.1–4.4 | USAGE/SECURITY docs; optional audit log; recommendations; tests                                                                          | ⬜ Pending |

---

### Secrets and password protection (vault) – [PLAN_SECRETS_VAULT.md](PLAN_SECRETS_VAULT.md)

| Phase | To-do                                                                                                  | Status    |
| ----- | -----                                                                                                  | ------    |
| A1    | pass_from_env / password_from_env (all connectors); document                                           | ✅ Done    |
| A2    | Redact secrets in GET /config; POST merge/refs                                                         | ✅ Done    |
| A3    | Config permissions, .gitignore, release checklist                                                      | ✅ Done    |
| B1–B6 | Vault schema, local vault, loader @vault/@env, CLI reimport, web reimport, optional remove-from-config | ⬜ Pending |
| C1–C2 | Vault key management docs; release checklist                                                           | ⬜ Pending |

---

### Version check and self-upgrade – [PLAN_SELF_UPGRADE_AND_VERSION_CHECK.md](PLAN_SELF_UPGRADE_AND_VERSION_CHECK.md)

Core flow first (sections 1–7); then optional Phase 9 (complexity/gain: high complexity, high gain for Linux/enterprise).

| #       | To-do                                                                              | Status    |
| -       | -----                                                                              | ------    |
| 1.1–1.3 | Repo URL, version fetch (GitHub API), expose current/latest/notes                  | ⬜ Pending |
| 2.1–2.5 | CLI --check-update, --upgrade; API GET /check-update, POST /upgrade; schedule docs | ⬜ Pending |
| 3.1–3.5 | Backup, upgrade method, restore, upgrade_log, restart docs                         | ⬜ Pending |
| 4.1–4.4 | Container detection; message; Docker/Kubernetes commands                           | ⬜ Pending |
| 5.1–5.2 | No downgrade; --force flag                                                         | ⬜ Pending |
| 6.1–6.3 | No data loss; config/overrides backup; audit trail                                 | ⬜ Pending |
| 7.1–7.3 | Tests; USAGE/DEPLOY docs; release notes                                            | ⬜ Pending |
| 9.1–9.5 | **Optional (after 1–7):** .deb package (ensure package name available; include/bundle deps for easy deployment), own apt repo, GPG signing, bytecode-only install (no raw .py), winget-like UX; see plan §9. | ⬜ Pending |

---

### Compressed files (scan inside archives) – [PLAN_COMPRESSED_FILES.md](PLAN_COMPRESSED_FILES.md)

| #    | To-do                                                                    | Status    |           |
| -    | -----                                                                    | ------    |           |
| 1    | Config: file_scan.scan_compressed, max_inner_size, compressed_extensions | ✅ Done   |           |
| 2    | CLI --scan-compressed                                                    | ✅ Done   |           |
| 3    | Archive detection (magic bytes: zip, gz, 7z, tar, bz2, xz)               | ✅ Done   |           |
| 4    | Open-archive helper (zipfile, tarfile, py7zr optional)                   | ✅ Done   |           |
| 5    | FilesystemConnector: scan inside archives; path like archive\            | inner     | ✅ Done   |
| 6    | Optional [compressed] extra; graceful skip if py7zr missing              | ✅ Done   |           |
| 7–11 | Engine/API/dashboard; share connectors; tests; docs (EN + pt-BR)         | ✅ Done   |           |
| 12   | Resource exhaustion: max_inner_size, temp caps; user warning when enabling (disk, I/O, run time) | ✅ Done   |           |
| 13   | Follow-up: password-protected archive sample (or programmatic test) to validate file_passwords for ZIP/7z | ⬜ Pending |           |
| 14   | Follow-up: optional max members per archive (e.g. 1000) as extra guard | ⬜ Pending |           |

---

### Content type & cloaking detection – [PLAN_CONTENT_TYPE_AND_CLOAKING_DETECTION.md](PLAN_CONTENT_TYPE_AND_CLOAKING_DETECTION.md)

| #   | To-do                                                                                                                       | Status    |
| --- | ---------------------------------------------------------------------------------------------------------------------------- | ------    |
| 1   | Magic-byte table + read_magic / infer_content_type for supported formats                                                     | ✅ Done   |
| 2   | Config file_scan.use_content_type (default false); engine/connectors                                                        | ✅ Done   |
| 3   | FilesystemConnector (and shares): use inferred type when option on; fallback to extension                                   | ✅ Done   |
| 4   | CLI --content-type-check; API/dashboard checkbox + user warning (may increase I/O and run time)                             | ✅ Done   |
| 5   | Tests: default unchanged; with option on, renamed PDF scanned by content; no regressions                                     | ✅ Done   |
| 6   | Docs: option, benefit (renamed/cloaking), resource impact; steganography out of scope for v1                                 | ✅ Done   |

---

### Data source versions & hardening – [PLAN_DATA_SOURCE_VERSIONS_AND_HARDENING.md](PLAN_DATA_SOURCE_VERSIONS_AND_HARDENING.md)

| Phase   | To-do                                                                                                                                                            | Status    |
| -----   | -----                                                                                                                                                            | ------    |
| 1.1–1.9 | Data model (data_source_inventory), save method; SQL/MongoDB/Redis/Power BI/Dataverse/REST version collection; Report "Data source inventory" sheet; tests; docs | ⬜ Pending |
| 2.1–2.5 | Snowflake, SMB, SharePoint, WebDAV, NFS version/protocol collection; tests; docs                                                                                 | ⬜ Pending |
| 3.1–3.6 | CVE/hardening rules, hardening engine, "Hardening recommendations" sheet, mitigation from public docs only; tests; docs                                          | ⬜ Pending |
| 4.1–4.4 | Hardening summary in report; optional standalone guide; docs/hardening-guide.md; full regression                                                                 | ⬜ Pending |

---

### Strong crypto & controls validation – [PLAN_OPTIONAL_STRONG_CRYPTO_AND_CONTROLS_VALIDATION.md](PLAN_OPTIONAL_STRONG_CRYPTO_AND_CONTROLS_VALIDATION.md)

| Phase   | To-do                                                                                                                                 | Status    |
| -----   | -----                                                                                                                                 | ------    |
| 1.1–1.7 | CLI --validate-crypto; optional config scan.validate_crypto; API body validate_crypto; dashboard checkbox; engine wiring; tests; docs | ⬜ Pending |
| 2.1–2.8 | Strong-crypto criteria; SQL/Mongo/Redis/REST/SMB validation; persist results; "Crypto & controls" sheet; tests; docs                  | ⬜ Pending |
| 3.1–3.6 | Anonymisation/controls heuristics (column/field names, metadata); store summary; disclaimer in report; tests; docs                    | ⬜ Pending |
| 4.1–4.3 | Crypto failures do not fail scan; full regression; optional link to Data source inventory                                             | ⬜ Pending |

---

### CNPJ alphanumeric format validation – [PLAN_CNPJ_ALPHANUMERIC_FORMAT_VALIDATION.md](PLAN_CNPJ_ALPHANUMERIC_FORMAT_VALIDATION.md)

| Phase   | To-do                                                                                                                 | Status    |
| -----   | -----                                                                                                                 | ------    |
| 1.1–1.4 | Research and specify alphanumeric CNPJ format (IN RFB 2.229/2024); propose regex; document in SENSITIVITY_DETECTION (EN + pt_BR) | ✅ Done   |
| 2.1–2.3 | Example regex_overrides + ML term; verify scan detects both legacy and alphanumeric; USAGE docs                       | ✅ Done   |
| 3.1–3.4 | Decide built-in vs flag vs override-only; optional built-in/flag; optional "CNPJ format compatibility" report summary | ✅ Done   |
| 4.1–4.3 | "How to get there" in plan; sync PLANS_TODO and plan; full regression                                                 | ✅ Done   |

---

### Selenium QA test suite – [PLAN_SELENIUM_QA_TEST_SUITE.md](PLAN_SELENIUM_QA_TEST_SUITE.md)

| Phase   | To-do                                                                                                               | Status    |
| -----   | -----                                                                                                               | ------    |
| 1.1–1.6 | Optional [qa] deps (Selenium, webdriver-manager); tests_qa/ conftest + navigation + API baseline; runner stub; docs | ⬜ Pending |
| 2.1–2.5 | Buttons/forms; reports list; report/heatmap downloads; optional /logs; include in runner and report                 | ⬜ Pending |
| 3.1–3.4 | Report generator (pass/fail, duration, recommendations); configurable output dir; docs                              | ⬜ Pending |
| 4.1–4.3 | Optional stress tests; exclude QA from default pytest; final docs and PLANS_TODO                                    | ⬜ Pending |

---

### Synthetic data & confidence validation – [PLAN_SYNTHETIC_DATA_AND_CONFIDENCE_VALIDATION.md](PLAN_SYNTHETIC_DATA_AND_CONFIDENCE_VALIDATION.md)

| Phase   | To-do                                                                                        | Status    |
| -----   | -----                                                                                        | ------    |
| 1.1–1.5 | Fixture root; file-format coverage + ground-truth manifest; doc and optional tests           | ⬜ Pending |
| 2.1–2.4 | SQL/NoSQL fixtures (Docker or in-memory); manifest; doc and optional precision/recall script | ⬜ Pending |
| 3.1–3.3 | Shares fixtures or doc; Troubleshooting (timeouts, connectivity); optional timeout fixture   | ⬜ Pending |
| 4.1–4.5 | Confidence bands + operator guidance; report column/section; docs EN + pt_BR; tests          | ⬜ Pending |
| 5.1–5.3 | Optional validation scoring script; tune doc; PLANS_TODO update                              | ⬜ Pending |

---

### SAP connector – [PLAN_SAP_CONNECTOR.md](PLAN_SAP_CONNECTOR.md)

| Phase   | To-do                                                                                             | Status    |
| -----   | -----                                                                                             | ------    |
| 1.1–1.3 | Research SAP access (HANA/OData/RFC); decide primary path; define config shape                    | ⬜ Pending |
| 2.1–2.3 | Connector module (discovery, sampling, scan_column, save_finding); register; optional [sap] extra | ⬜ Pending |
| 3.1–3.3 | USAGE/TECH_GUIDE (EN + pt-BR); tests; pitch/roadmap update in README                              | ⬜ Pending |

---

### Dashboard i18n – [PLAN_DASHBOARD_I18N.md](PLAN_DASHBOARD_I18N.md)

**Status:** Under consideration. No to-do list until routing (path prefix vs query/cookie) and translation storage (JSON vs gettext) are decided. After decision, add concrete steps to this plan and to [PLAN_DASHBOARD_I18N.md](PLAN_DASHBOARD_I18N.md).

---

## Completed plans (reference)

- **Corporate compliance** – [.cursor/plans/](.cursor/plans/) (reference)
- **Minor data detection** – [completed/PLAN_MINOR_DATA_DETECTION.md](completed/PLAN_MINOR_DATA_DETECTION.md)
- **Aggregated identification** – [completed/PLAN_AGGREGATED_IDENTIFICATION.md](completed/PLAN_AGGREGATED_IDENTIFICATION.md)
- **Sensitive categories ML/DL** – [completed/PLAN_SENSITIVE_CATEGORIES_ML_DL.md](completed/PLAN_SENSITIVE_CATEGORIES_ML_DL.md)
- **Rate limiting** – [completed/PLAN_RATE_LIMIT_SCANS.md](completed/PLAN_RATE_LIMIT_SCANS.md)
- **Web hardening** – [completed/PLAN_WEB_HARDENING_SECURITY.md](completed/PLAN_WEB_HARDENING_SECURITY.md)
- **Logo and naming** – [completed/PLAN_LOGO_AND_NAMING.md](completed/PLAN_LOGO_AND_NAMING.md)
- **Security hardening** – [completed/PLAN_SECURITY_HARDENING.md](completed/PLAN_SECURITY_HARDENING.md)
- **Configurable timeouts** – [completed/PLAN_CONFIGURABLE_TIMEOUTS_AND_RATE_GUIDANCE.md](completed/PLAN_CONFIGURABLE_TIMEOUTS_AND_RATE_GUIDANCE.md)
- **Additional compliance samples** – [completed/PLAN_ADDITIONAL_COMPLIANCE_SAMPLES.md](completed/PLAN_ADDITIONAL_COMPLIANCE_SAMPLES.md)

---

## Readiness and operations (meta)

Goal categories (so we don’t forget). **Full prioritised checklist and to-dos:** [PLAN_READINESS_AND_OPERATIONS.md](PLAN_READINESS_AND_OPERATIONS.md). Status is updated only there.

| Category                | One-line summary                                                        | Status      |
| ----------              | ------------------                                                      | --------    |
| **Release**             | Checklist in CONTRIBUTING; history = git + `docs/releases/`.            | Done        |
| **Security response**   | Vulnerability and Dependabot security PR SLAs in SECURITY.md.           | Done        |
| **Runbooks**            | Operator runbook one-pager; backup and restore in USAGE/deploy.         | Not started |
| **Compliance evidence** | “Compliance and evidence” in SECURITY or doc; data retention mention.   | Not started |
| **Onboarding**          | Short onboarding checklist in CONTRIBUTING.                             | Not started |
| **Dependency policy**   | Python/platform support sentence; optional lockfile refresh policy.     | Not started |
| **Check-all script**    | One command (uv sync, ruff, pytest, pip-audit) approximates CI locally. | Not started |

See PLAN_READINESS for MCP recommendation, workflow automation, and when to revisit (release, onboarding, audit).

---

## Artifacts and portfolio (for thesis, evidence mapping, pitch)

**Full checklist (Docker Hub, Dockerfiles, GitHub, certifications, Ubuntu, private docs):** [PORTFOLIO_AND_EVIDENCE_SOURCES.md](PORTFOLIO_AND_EVIDENCE_SOURCES.md). Authoritative Docker list: **`docs/private/From Docker hub list of repositories.md`**. CV, TCC, LinkedIn in `docs/private/` (git-ignored). See [TOKEN_AWARE_USAGE.md](TOKEN_AWARE_USAGE.md) §3.

---

## How to use this list

1. **Execute to-dos** in the recommended sequence (or in dependency order within a plan).
1. **Mark done** in both this file and the plan file when a step is implemented, tested, and documented.
1. **After each step:** run `uv run pytest -v -W error` to ensure no regression.
1. **Documentation:** Update USAGE, TECH_GUIDE, SECURITY, or dedicated docs (EN + pt-BR) as features land; add new doc files to docs/README index and, if needed, to test_docs_markdown.
1. **New to-dos:** When adding a new to-do to any plan, add it here under the corresponding plan section so this remains the source of truth.

---

## Last synced with plan files. Update this doc when completing steps or when plans change.
