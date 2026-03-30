# Plans hub — navigation for collaborators

**Português (Brasil):** [PLANS_HUB.pt_BR.md](PLANS_HUB.pt_BR.md)

**Purpose:** Give **new collaborators, candidates, and reviewers** a single map of every **`PLAN_*.md`** in this tree (open and completed), with a short **intent** line and optional **cross-references**. It does **not** replace **[PLANS_TODO.md](PLANS_TODO.md)** (sequential work and status) or **[SPRINTS_AND_MILESTONES.md](SPRINTS_AND_MILESTONES.md)** (time-boxed themes); it **complements** them for orientation.

**When to refresh:** After adding, renaming, or archiving a `PLAN_*.md` file, run:

```bash
python scripts/plans_hub_sync.py --write
```

Then commit the updated hub. **CI / pre-commit** runs `python scripts/plans_hub_sync.py --check` so the table cannot drift silently.

**Optional hints inside a plan file** (English comments, anywhere in the body):

```html
<!-- plans-hub-summary: One line for humans (shown in the hub table). -->
<!-- plans-hub-related: PLAN_OTHER.md, completed/PLAN_OLD.md -->
```

---

## Meta documents (read these first)

| Document                                                               | Role                                                                                                                     |
| --------                                                               | ----                                                                                                                     |
| [PLANS_TODO.md](PLANS_TODO.md)                                         | **Single source of truth** for open-plan to-dos, dependency order, and the auto **status dashboard** (`plans-stats.py`). |
| [SPRINTS_AND_MILESTONES.md](SPRINTS_AND_MILESTONES.md)                 | Sprint themes, milestones, Kanban/Gantt-style traceability (bilingual with `.pt_BR.md`).                                 |
| [TOKEN_AWARE_USAGE.md](TOKEN_AWARE_USAGE.md)                           | Token-aware slices and one-session discipline.                                                                           |
| [PORTFOLIO_AND_EVIDENCE_SOURCES.md](PORTFOLIO_AND_EVIDENCE_SOURCES.md) | Study cadence, evidence, portfolio alignment.                                                                            |
| [MAINTENANCE_FRONT_OF_WORK.md](MAINTENANCE_FRONT_OF_WORK.md)           | Post-burst maintenance and CI matrix hygiene.                                                                            |
| [PYTHON_UPGRADE_PLAYBOOK.md](PYTHON_UPGRADE_PLAYBOOK.md)               | Runtime upgrade sequencing (EN; pt-BR companion available).                                                              |
| [completed/NEXT_STEPS.md](completed/NEXT_STEPS.md)                     | Archived implementation checklist pointer (not a `PLAN_` file).                                                          |

---

## All `PLAN_*.md` files (auto-generated)

Do **not** edit the table manually; refresh with `python scripts/plans_hub_sync.py --write`.

<!-- PLANS_HUB_TABLE:START -->
| Status | Document | Title | Summary | Related plans |
| ------ | -------- | ----- | ------- | -------------- |
| **Open** | [PLAN_ADDITIONAL_DATA_SOUP_FORMATS.md](PLAN_ADDITIONAL_DATA_SOUP_FORMATS.md) | Plan: Additional "data soup" formats and rich media | **Status:** Tier 3 **metadata + subtitles + magic-byte cloaking** — **merged to `main` when shipped** (see [PLANS_TODO.md](PLANS_TODO.md) **Integration / WIP** until then); Tier 1 formats and **stego** remain backlog (se | — |
| **Open** | [PLAN_ADDITIONAL_DETECTION_TECHNIQUES_AND_FN_REDUCTION.md](PLAN_ADDITIONAL_DETECTION_TECHNIQUES_AND_FN_REDUCTION.md) | Plan: Additional detection techniques and false-negative reduction | **Status:** In progress (priorities 1–3 implemented; priority 4 initial slice: `connector_format_id_hint` + `FORMAT_LENGTH_HINT_ID`) **Goal:** Explore techniques, frameworks, and libraries (beyond Regex, ML, and DL) to i | — |
| **Open** | [PLAN_BANDIT_SECURITY_LINTER.md](PLAN_BANDIT_SECURITY_LINTER.md) | Plan: Bandit (Python security linter) | **Status:** Phase 1–2 done (dev dependency, `pyproject` config, optional CI gate **medium+**). **Phase 3** = tighten skips / per-line `# nosec`, expand paths, or fail on **low** when triaged. | — |
| **Open** | [PLAN_BUILD_IDENTITY_RELEASE_INTEGRITY.md](PLAN_BUILD_IDENTITY_RELEASE_INTEGRITY.md) | Plan: Build identity, runtime version display, and release integrity | **Status:** Not started **Related:** [PLAN_SELF_UPGRADE_AND_VERSION_CHECK.md](PLAN_SELF_UPGRADE_AND_VERSION_CHECK.md) (remote “latest” vs current; upgrade paths) | — |
| **Open** | [PLAN_CNPJ_ALPHANUMERIC_FORMAT_VALIDATION.md](PLAN_CNPJ_ALPHANUMERIC_FORMAT_VALIDATION.md) | Plan: CNPJ alphanumeric format – understanding, validation, and compatibility | **Status:** Phase 4 done; Phase 5 (checksum validation) future. Phases 1–4 complete. | — |
| **Open** | [PLAN_COMPLIANCE_EVIDENCE_MAPPING.md](PLAN_COMPLIANCE_EVIDENCE_MAPPING.md) | Plan: Compliance evidence mapping – regulations to app features and reports | **Status:** Not started (structure only) | — |
| **Open** | [PLAN_COMPLIANCE_STANDARDS_ALIGNMENT.md](PLAN_COMPLIANCE_STANDARDS_ALIGNMENT.md) | Plan: Compliance standards alignment (ISO/IEC 27701, FELCA, auditable norms) | **Status:** Done (documentation) | — |
| **Open** | [PLAN_COMPRESSED_FILES.md](PLAN_COMPRESSED_FILES.md) | Plan: Optional scan inside compressed files (archives) | **Status:** Not started | — |
| **Open** | [PLAN_CONTENT_TYPE_AND_CLOAKING_DETECTION.md](PLAN_CONTENT_TYPE_AND_CLOAKING_DETECTION.md) | Plan: Content-based type detection and cloaking resistance | **Status:** Steps 1–4 implemented (config, connectors, CLI, API/dashboard); tests and doc polish tracked below | — |
| **Open** | [PLAN_DASHBOARD_HTTPS_BY_DEFAULT_AND_HTTP_EXPLICIT_RISK.md](PLAN_DASHBOARD_HTTPS_BY_DEFAULT_AND_HTTP_EXPLICIT_RISK.md) | Plan: Dashboard HTTPS-by-default with explicit HTTP risk mode | **Status:** Core phases shipped (TLS + explicit HTTP + status/banner); audit-export / tamper phases still open | — |
| **Open** | [PLAN_DASHBOARD_I18N.md](PLAN_DASHBOARD_I18N.md) | Dashboard i18n and multi-language web UI | **Status:** **Target architecture agreed** — implementation **deferred** until higher-priority product slices ship; milestones and sequencing below are **planning only** until scheduled. | — |
| **Open** | [PLAN_DASHBOARD_REPORTS_ACCESS_CONTROL.md](PLAN_DASHBOARD_REPORTS_ACCESS_CONTROL.md) | Plan: Dashboard / reports access control (roles & permissions) | **Status:** Not started (backlog — tracked from GitHub) | — |
| **Open** | [PLAN_DATA_SOURCE_VERSIONS_AND_HARDENING.md](PLAN_DATA_SOURCE_VERSIONS_AND_HARDENING.md) | Plan: Data source version and protocol detection with CVE awareness and hardening guidance | **Status:** Not started | — |
| **Open** | [PLAN_ENTERPRISE_HR_SST_ERP_CONNECTORS.md](PLAN_ENTERPRISE_HR_SST_ERP_CONNECTORS.md) | Plan: Enterprise back-office connectors (SST, HR, ERP, CRM, folha, helpdesk, URM) | **Status:** Not started (planning / backlog catalogue) | — |
| **Open** | [PLAN_GEMINI_FEEDBACK_TRIAGE.md](PLAN_GEMINI_FEEDBACK_TRIAGE.md) | Plan: Gemini feedback triage (non-authoritative) | Gemini triage from 2026-03-26 local bundle (WRB folder): P0/P1/P2 rows with IDs—non-authoritative until verified and promoted. | [TOKEN_AWARE_USAGE.md](TOKEN_AWARE_USAGE.md) [PLANS_TODO.md](PLANS_TODO.md) [PORTFOLIO_AND_EVIDENCE_SOURCES.md](PORTFOLIO_AND_EVIDENCE_SOURCES.md) [PYTHON_UPGRADE_PLAYBOOK.md](PYTHON_UPGRADE_PLAYBOOK.md) |
| **Open** | [PLAN_GRC_INSPIRED_ENTERPRISE_TRUST_ACCELERATORS.md](PLAN_GRC_INSPIRED_ENTERPRISE_TRUST_ACCELERATORS.md) | Plan: GRC-inspired trust accelerators for enterprise recognition | **Status:** Proposed **Audience:** Internal product planning (operator + maintainers) | — |
| **Open** | [PLAN_LAB_FIREWALL_ACCESS_AND_OBSERVABILITY.md](PLAN_LAB_FIREWALL_ACCESS_AND_OBSERVABILITY.md) | Lab-op — firewall / L3 baseline, assistant access, security posture, observability (sequenced) | One **ordered spine** for homelab work that started with **UniFi / firewall tuning**: align **L3 + DHCP + DNS** per VLAN, enable **safe Cursor/assistant automation** on the operator PC, capture **security posture** (Cybe | — |
| **Open** | [PLAN_LAB_FIREWALL_ACCESS_AND_OBSERVABILITY.pt_BR.md](PLAN_LAB_FIREWALL_ACCESS_AND_OBSERVABILITY.pt_BR.md) | Lab-op — firewall / L3, acesso ao assistente, postura de segurança, observabilidade (sequenciado) | **Finalidade:** Uma **espinha dorsal ordenada** para o trabalho de homelab que começou com **ajuste de UniFi / firewall**: alinhar **L3 + DHCP + DNS** por VLAN, permitir **automação segura com Cursor** no PC do operador, | — |
| **Open** | [PLAN_LAB_OP_OBSERVABILITY_STACK.md](PLAN_LAB_OP_OBSERVABILITY_STACK.md) | Lab-op observability stack — metrics, logs, dashboards (plan only) | Sequence **optional** homelab instrumentation—**Grafana**, time-series DBs, **centralized logs**—without blocking Data Boar development or **–1L** validation. **No** implementation in this repo; operator deploys via Comp | — |
| **Open** | [PLAN_LAB_OP_OBSERVABILITY_STACK.pt_BR.md](PLAN_LAB_OP_OBSERVABILITY_STACK.pt_BR.md) | Stack de observabilidade no lab-op — métricas, logs, dashboards (só plano) | **Objetivo:** Ordenar instrumentação **opcional** do homelab — **Grafana**, bases de séries temporais, **centralização de logs** — sem bloquear desenvolvimento do Data Boar nem a validação **–1L**. **Sem** implementação  | — |
| **Open** | [PLAN_LATO_SENSU_THESIS.md](PLAN_LATO_SENSU_THESIS.md) | Plan: Lato sensu thesis – Data Boar as applied artifact | **Status:** Not started (structure only) | — |
| **Open** | [PLAN_MARKET_ALIGNMENT_AND_WABBIX_REVIEW_TIMING.md](PLAN_MARKET_ALIGNMENT_AND_WABBIX_REVIEW_TIMING.md) | Plan: Market alignment checkpoint and Wabbix review timing | **Status:** Proposed (checkpoint note) | — |
| **Open** | [PLAN_NOTIFICATIONS_OFFBAND_AND_SCAN_COMPLETE.md](PLAN_NOTIFICATIONS_OFFBAND_AND_SCAN_COMPLETE.md) | Plan: Off-band notifications and scan-completion notifications | **Status:** Phase 1–2 baseline implemented (config + notifier + scan-complete trigger + docs); Phase 3+ backlog. | — |
| **Open** | [PLAN_OBJECT_STORAGE_CLOUD_CONNECTORS.md](PLAN_OBJECT_STORAGE_CLOUD_CONNECTORS.md) | Plan: Object storage connectors (S3-class, Azure Blob, GCS) | **Status:** Not started (planning only). **Synced with:** [PLANS_TODO.md](PLANS_TODO.md). | — |
| **Open** | [PLAN_OPERATOR_API_KEY_FIRST_AUTH_UX.md](PLAN_OPERATOR_API_KEY_FIRST_AUTH_UX.md) | Plan: Operator API key–first auth UX (reduce JWT / manual Bearer toil) | **Status:** Exploratory spike (not implementing product IdP) | — |
| **Open** | [PLAN_OPT_IN_NETWORK_PORT_SERVICE_HINTS.md](PLAN_OPT_IN_NETWORK_PORT_SERVICE_HINTS.md) | Plan: Opt-in network port / service hints (“hidden ingredients” adjacent) | **Status:** Proposal (not implemented) | — |
| **Open** | [PLAN_OPTIONAL_STRONG_CRYPTO_AND_CONTROLS_VALIDATION.md](PLAN_OPTIONAL_STRONG_CRYPTO_AND_CONTROLS_VALIDATION.md) | Plan: Optional strong-crypto validation and inference of anonymisation/controls | **Status:** Not started | — |
| **Open** | [PLAN_PRIORITY_MATRIX_ADJUSTMENTS_2026-03-25.md](PLAN_PRIORITY_MATRIX_ADJUSTMENTS_2026-03-25.md) | Plan checkpoint: priority matrix adjustments (2026-03-25) | **Status:** Applied updates in planning docs **Goal context:** faster commercialization readiness without regressions, with trust-first sequencing. | — |
| **Open** | [PLAN_READINESS_AND_OPERATIONS.md](PLAN_READINESS_AND_OPERATIONS.md) | Plan: Readiness and operations (meta / “see the forest”) | Capture aspects that are easy to miss when focused on feature plans—so you can decide what to formalise, automate, or document next. No obligation to implement everything; use as a prioritised checklist. | — |
| **Open** | [PLAN_SAP_CONNECTOR.md](PLAN_SAP_CONNECTOR.md) | Plan: SAP connector – add SAP to the "data soup" | **Status:** Not started | — |
| **Open** | [PLAN_SECRETS_VAULT.md](PLAN_SECRETS_VAULT.md) | Plan: Secrets and password protection (vault and alternatives) | **Status:** Phase A done; Phase B and C pending | — |
| **Open** | [PLAN_SELENIUM_QA_TEST_SUITE.md](PLAN_SELENIUM_QA_TEST_SUITE.md) | Plan: Selenium-based QA test suite (on-demand, report and recommendations) | **Status:** Not started | — |
| **Open** | [PLAN_SELF_UPGRADE_AND_VERSION_CHECK.md](PLAN_SELF_UPGRADE_AND_VERSION_CHECK.md) | Plan: Version check and self-upgrade (with container-aware behaviour) | **Related:** [PLAN_BUILD_IDENTITY_RELEASE_INTEGRITY.md](PLAN_BUILD_IDENTITY_RELEASE_INTEGRITY.md) — **local** build string (`release` vs `dev`, optional manifest) shown at startup and in the dashboard; this plan focuses  | — |
| **Open** | [PLAN_SEMGREP_CI.md](PLAN_SEMGREP_CI.md) | Plan: Semgrep in CI (OSS ruleset) | **Status:** ✅ **Complete** (workflow on `main`, tests, docs, Wabbix baseline). **Slack:** failure notify watches **`Semgrep`** when **`SLACK_WEBHOOK_URL`** is set — optional operator smoke: see § below. **Synced with:**  | — |
| **Open** | [PLAN_STRICTO_SENSU_RESEARCH_PATH.md](PLAN_STRICTO_SENSU_RESEARCH_PATH.md) | Plan: Stricto sensu research path (M.Sc. and PhD) on top of Data Boar | **Status:** Not started (structure only) | — |
| **Open** | [PLAN_SYNTHETIC_DATA_AND_CONFIDENCE_VALIDATION.md](PLAN_SYNTHETIC_DATA_AND_CONFIDENCE_VALIDATION.md) | Plan: Synthetic and true-like data sources, confidence scoring, and operator guidance | **Status:** Not started | — |
| **Open** | [PLAN_TWO_WEEK_EXECUTION_NO_REGRESSION.md](PLAN_TWO_WEEK_EXECUTION_NO_REGRESSION.md) | Plan: Two-week execution sprint (no regressions, low toil, fast delivery) | **Status:** Proposed (ready to execute) | — |
| **Open** | [PLAN_US_CHILD_PRIVACY_TECHNICAL_ALIGNMENT.md](PLAN_US_CHILD_PRIVACY_TECHNICAL_ALIGNMENT.md) | Plan: U.S. child and minor privacy — technical mapping (samples + docs) | **Status:** Phase 1 complete (config samples + EN/pt-BR product docs + README mentions) | — |
| **Open** | [PLAN_WEBSITE_AND_DOCS_I18N_FUTURE.md](PLAN_WEBSITE_AND_DOCS_I18N_FUTURE.md) | Plan (future): public website, marketing depth, and extra doc languages | Capture intent so we do not forget: a **stronger public surface** (site + optional extra languages) aligned with **branding** (Data Boar / dashBOARd, data soup narrative) and **trust** (releases, docs, use cases). | — |
| **Completed** | [PLAN_ADDITIONAL_COMPLIANCE_SAMPLES.md](completed/PLAN_ADDITIONAL_COMPLIANCE_SAMPLES.md) | Plan: Additional compliance scans and sample configs (UK GDPR, EU GDPR, Benelux, PIPEDA, POPIA, APPI, PCI-DSS) | **Status:** All samples and docs done; tests 3.1–3.2 and regression 4.1 done | — |
| **Completed** | [PLAN_AGGREGATED_IDENTIFICATION.md](completed/PLAN_AGGREGATED_IDENTIFICATION.md) | Plan: Cross-referenced and aggregated data – identification risk | — | — |
| **Completed** | [PLAN_CONFIGURABLE_TIMEOUTS_AND_RATE_GUIDANCE.md](completed/PLAN_CONFIGURABLE_TIMEOUTS_AND_RATE_GUIDANCE.md) | Plan: Configurable timeouts for data soup access (sane defaults and recommendations) | **Status:** Done (Phases 1–4 complete) | — |
| **Completed** | [PLAN_LOGO_AND_NAMING.md](completed/PLAN_LOGO_AND_NAMING.md) | Logo, favicon, and application naming recommendations | **Status:** Complete (all to-dos done; plan archived in `docs/plans/completed/`) | — |
| **Completed** | [PLAN_MINOR_DATA_DETECTION.md](completed/PLAN_MINOR_DATA_DETECTION.md) | Plan: Detection and differential treatment of possible minor data | — | — |
| **Completed** | [PLAN_RATE_LIMIT_SCANS.md](completed/PLAN_RATE_LIMIT_SCANS.md) | Plan: Rate limiting and concurrency safeguards | Goal: Add configurable rate limiting and concurrency safeguards so the LGPD audit scanner cannot accidentally DoS customer networks while keeping existing behaviour and docs in sync. | — |
| **Completed** | [PLAN_SECURITY_HARDENING.md](completed/PLAN_SECURITY_HARDENING.md) | Plan: Security hardening and vulnerability closure | **Status:** Done (Tier 1 foundation). All steps 1.1–1.3, 2.1–2.4, 3.1–3.4, 5.1–5.3, 6.1–6.3, 7.1–7.3 complete. | — |
| **Completed** | [PLAN_SENSITIVE_CATEGORIES_ML_DL.md](completed/PLAN_SENSITIVE_CATEGORIES_ML_DL.md) | Plan: ML/DL detection of additional sensitive categories | — | — |
| **Completed** | [PLAN_WEB_HARDENING_SECURITY.md](completed/PLAN_WEB_HARDENING_SECURITY.md) | Plan: Web hardening and security improvements | Goal: Harden the web surface of the LGPD crawler (CSP, headers, and deploy guidance) without regressing current behaviour, keeping docs and man pages in sync and tests green. | — |

<!-- PLANS_HUB_TABLE:END -->

---

## Cross-cutting themes (manual)

Use this section for **narrative** ties that are awkward to express per row. Keep it short; prefer `plans-hub-related` in the plan file when possible.

- **Detection & reporting:** sensitivity, FN reduction, content-type, aggregated identification, minors, notifications — see hub rows and **PLANS_TODO** detection cluster.
- **Security & supply chain:** **PyPI path:** **`uv.lock`** + CI **`pip-audit`** + **Dependabot**; **GitHub Actions** pinned to **commit SHAs** in CI/CodeQL/Semgrep/slack-ops-digest (bump via Dependabot). Plus Semgrep, Bandit, secrets/vault, HTTPS/dashboard risk, release integrity, **SBOM** roadmap (**ADR 0003**) — align with **Priority band A** in **PLANS_TODO**.
- **Connectors & data soup:** object storage, SAP, HR/ERP, compressed files, additional formats — often sequenced after core stability; check **PLANS_TODO** order.

**See also:** [README.md](../README.md) documentation index (**Internal and reference**), [CONTRIBUTING.md](../../CONTRIBUTING.md), [AGENTS.md](../../AGENTS.md).
