# Consolidated plans – sequential to-dos

Plan files are kept in **English only** for history and progress tracking. Operator-facing documentation (how to use, config, deploy, etc.) exists in both EN and pt-BR; see [README.md](README.md) ([pt-BR](README.pt_BR.md)).

This document is the **single source of truth** for the project's plan status and remains in **`docs/plans/`** at all times. It lists **incomplete goals** from active plans and the **recommended sequential to-dos** to achieve them. Completed plan documents are archived in **`docs/plans/completed/`** for reference; links below point to those files.

**Policy:** When implementing a plan step, **update documentation** (USAGE, TECH_GUIDE, SECURITY, or dedicated docs) and **add or run tests** as the feature is implemented. After completing or adding to-dos, **update this file and the plan file** so progress is tracked in one place. All steps are intended to be **non-destructive**, **non-regression**, and **tested** before marking done.

**Plan status:** Corporate compliance ✅ · Minor data detection ✅ · Aggregated identification ✅ · Sensitive categories ML/DL ✅ · Rate limiting ✅ · Web hardening ✅ · Logo and naming ✅ · **Security hardening** ✅ Done (Tier 1) · **Secrets/vault** ✅ Phase A done (Tier 1) · **Configurable timeouts** ✅ Done · **Version check & self-upgrade** ⬜ Not started · **Additional compliance samples** ⬜ Not started · **Compressed files** ⬜ Not started · **Data source versions & hardening** ⬜ Not started · **Strong crypto & controls validation** ⬜ Not started · **CNPJ alphanumeric format validation** ⬜ Not started · **Selenium QA test suite** ⬜ Not started · **Synthetic data & confidence validation** ⬜ Not started · **Notifications (off-band + scan-complete)** ⬜ Not started · **Dashboard i18n** ⬜ Under consideration · **SAP connector** ⬜ Not started

---

## Conflict and dependency analysis

| Plan                                     | Depends on                | Conflicts with | Notes                                                                                                                         |
| ----                                     | ----------                | -------------- | -----                                                                                                                         |
| Security hardening                       | —                         | None           | Additive (validation, docs, audit). Do first to strengthen base.                                                              |
| Secrets vault                            | —                         | None           | Phase A (redact, env) improves config safety before vault.                                                                    |
| Version check / self-upgrade             | —                         | None           | Backup excludes secrets (manifest); compatible with Secrets A.                                                                |
| Additional compliance samples            | —                         | None           | Config-only; samples and docs additive.                                                                                       |
| Compressed files                         | Config loader (new keys)  | None           | Additive feature; optional dependency py7zr.                                                                                  |
| Dashboard i18n                           | Approach decided          | None           | No concrete to-dos until routing/translation approach chosen.                                                                 |
| Data source versions & hardening         | —                         | None           | Additive: new table data_source_inventory, new report sheets; optional CVE lookup.                                            |
| Strong crypto & controls validation      | —                         | None           | Optional flag (CLI + dashboard); new table or extend inventory; report sheet "Crypto & controls"; inference best-effort.      |
| CNPJ alphanumeric format validation      | —                         | None           | Format spec + regex/override; optional built-in or config flag; compatibility report; no change to legacy LGPD_CNPJ.          |
| Selenium QA test suite                   | —                         | None           | On-demand; optional [qa] deps; tests_qa/; report + recommendations; exclude from default pytest.                              |
| Synthetic data & confidence validation   | —                         | None           | Fixtures (files, SQL, NoSQL, shares); FP/FN + ground truth; confidence bands + operator guidance; timeouts/connectivity docs. |
| Configurable timeouts                    | —                         | None           | Global + per-target connect/read timeouts; sane defaults; connector wiring; recommendations (avoid DoS, too-fast).            |
| Notifications (off-band + scan-complete) | Optional: Secrets Phase A | None           | Webhook notifier; scan-complete brief to operator/tenant (Slack, Teams, Telegram, etc.); recommendations.                     |
| SAP connector                            | Optional: Configurable timeouts | None    | Add SAP (HANA/OData/RFC) to data soup; same discovery/sample/finding flow; optional [sap] extra. See PLAN_SAP_CONNECTOR.     |

**Regression and tests:** No plan modifies wipe behaviour, SQLite schema (except Self-upgrade adds optional upgrade_log, Data source versions adds data_source_inventory, Strong crypto adds optional crypto_controls_audit or extends inventory), or existing config keys in a breaking way. New tests per plan must pass together with the full suite (`uv run pytest -v -W error`). Document each new feature in the relevant docs (EN + pt-BR where applicable).

---

## Review and sequence rationale

The recommended order below is chosen to:

- **Strengthen the base first:** Security hardening and Configurable timeouts reduce risk and improve robustness for all later work.
- **Respect dependencies:** Secrets Phase A (redact, env) before Phase B (vault); Notifications can optionally use Secrets A for webhook URLs.
- **Batch additive features:** Compliance samples, Compressed files, Data source versions, and Strong crypto add config/report/sheets without breaking existing flows.
- **Defer optional or heavy work:** Version check, CNPJ, Selenium QA, Synthetic data, Notifications, and Dashboard i18n come after core security and scan/report features.

## Tier summary (for planning):

- **Tier 1 – Foundation:** 1 Security hardening, 2 Configurable timeouts, 3 Secrets Phase A.
- **Tier 2 – Scan and report:** 4 Compliance samples, 5 Compressed files, 6 Data source versions & hardening, 7 Strong crypto & controls, 8 SAP connector.
- **Tier 3 – Secrets and upgrade:** 9 Secrets Phase B, 10 Version check & self-upgrade.
- **Tier 4 – Validation and ops:** 11 CNPJ alphanumeric, 12 Selenium QA, 13 Synthetic data & confidence, 14 Notifications, 15 Dashboard i18n.

Plans without dependencies can be run in parallel within a tier (e.g. 4 and 5). Within a plan, execute phases in order.

---

## Recommended sequence (aggregated)

1. **Security hardening** (docs + validation + audit) – low risk; improves base.
1. **Configurable timeouts** – global + per-target connect/read timeouts, sane defaults, connector wiring, recommendations.
1. **Secrets vault – Phase A** (env expansion, redact GET /config, docs) – config safety before more config surface.
1. **Additional compliance samples** – config-only; samples + docs + structure test.
1. **Compressed files** – new config, CLI, connector logic, tests, docs.
1. **Data source versions & hardening** – inventory table, connector version/protocol collection, CVE/hardening rules, report sheets, next-steps guide.
1. **Strong crypto & controls validation** – CLI/dashboard flag, strong-crypto validation per connection, anonymisation/controls inference, "Crypto & controls" report sheet.
1. **Secrets vault – Phase B** (vault impl, re-import CLI/web) – after Phase A.
1. **Version check & self-upgrade** – version source, container detection, CLI/API, backup/audit log.
1. **CNPJ alphanumeric format validation** – format spec, regex/override, optional built-in or flag, compatibility recommendations.
1. **Selenium QA test suite** – on-demand robot QA (navigation, functional, API, report/heatmap downloads, stress); short report and recommendations.
1. **Synthetic data & confidence validation** – fixtures (all formats, SQL, NoSQL, shares), FP/FN + ground truth, confidence bands + operator guidance, timeouts/connectivity docs.
1. **Notifications (off-band + scan-complete)** – webhook notifier, scan-complete brief to operator/tenant, how to download report; optional Part A (task/milestone) from CI or script.
1. **SAP connector** – add SAP (HANA/OData or RFC) to data soup; discovery, sampling, findings; optional [sap] extra; docs and tests. See [PLAN_SAP_CONNECTOR.md](PLAN_SAP_CONNECTOR.md).
1. **Dashboard i18n** – after approach is decided; add to-dos to this file and plan then.

---

## Open plans and to-dos (summary)

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
| A1    | pass_from_env / password_from_env (all connectors); document                                           | ✅ Done   |
| A2    | Redact secrets in GET /config; POST merge/refs                                                         | ✅ Done   |
| A3    | Config permissions, .gitignore, release checklist                                                      | ✅ Done   |
| B1–B6 | Vault schema, local vault, loader @vault/@env, CLI reimport, web reimport, optional remove-from-config | ⬜ Pending |
| C1–C2 | Vault key management docs; release checklist                                                           | ⬜ Pending |

---

### Version check and self-upgrade – [PLAN_SELF_UPGRADE_AND_VERSION_CHECK.md](PLAN_SELF_UPGRADE_AND_VERSION_CHECK.md)

| #       | To-do                                                                              | Status    |
| -       | -----                                                                              | ------    |
| 1.1–1.3 | Repo URL, version fetch (GitHub API), expose current/latest/notes                  | ⬜ Pending |
| 2.1–2.5 | CLI --check-update, --upgrade; API GET /check-update, POST /upgrade; schedule docs | ⬜ Pending |
| 3.1–3.5 | Backup, upgrade method, restore, upgrade_log, restart docs                         | ⬜ Pending |
| 4.1–4.4 | Container detection; message; Docker/Kubernetes commands                           | ⬜ Pending |
| 5.1–5.2 | No downgrade; --force flag                                                         | ⬜ Pending |
| 6.1–6.3 | No data loss; config/overrides backup; audit trail                                 | ⬜ Pending |
| 7.1–7.3 | Tests; USAGE/DEPLOY docs; release notes                                            | ⬜ Pending |

---

### Additional compliance samples – [PLAN_ADDITIONAL_COMPLIANCE_SAMPLES.md](PLAN_ADDITIONAL_COMPLIANCE_SAMPLES.md)

| #       | To-do                                                                   | Status    |
| -       | -----                                                                   | ------    |
| 1.1     | Create docs/compliance-samples/ (or deploy/); README                    | ⬜ Pending |
| 1.2–1.6 | UK GDPR, PIPEDA, POPIA, APPI, PCI-DSS sample files                      | ⬜ Pending |
| 2.1–2.4 | README pitch; compliance-frameworks/samples doc; USAGE/TECH_GUIDE/index | ⬜ Pending |
| 3.1–3.2 | Test sample YAML structure; doc existence test                          | ⬜ Pending |
| 4.1     | No regressions; full test suite                                         | ⬜ Pending |

---

### Compressed files (scan inside archives) – [PLAN_COMPRESSED_FILES.md](PLAN_COMPRESSED_FILES.md)

| #    | To-do                                                                    | Status    |           |
| -    | -----                                                                    | ------    |           |
| 1    | Config: file_scan.scan_compressed, max_inner_size, compressed_extensions | ⬜ Pending |           |
| 2    | CLI --scan-compressed                                                    | ⬜ Pending |           |
| 3    | Archive detection (magic bytes: zip, gz, 7z, tar, bz2, xz)               | ⬜ Pending |           |
| 4    | Open-archive helper (zipfile, tarfile, py7zr optional)                   | ⬜ Pending |           |
| 5    | FilesystemConnector: scan inside archives; path like archive\            | inner     | ⬜ Pending |
| 6    | Optional [compressed] extra; graceful skip if py7zr missing              | ⬜ Pending |           |
| 7–11 | Engine/API/dashboard; share connectors; tests; docs (EN + pt-BR)         | ⬜ Pending |           |

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
| 1.1–1.4 | Research and specify alphanumeric CNPJ format; propose regex; document in SENSITIVITY_DETECTION (EN + pt_BR)          | ⬜ Pending |
| 2.1–2.3 | Example regex_overrides + ML term; verify scan detects both legacy and alphanumeric; USAGE docs                       | ⬜ Pending |
| 3.1–3.4 | Decide built-in vs flag vs override-only; optional built-in/flag; optional "CNPJ format compatibility" report summary | ⬜ Pending |
| 4.1–4.3 | "How to get there" recommendations; update PLANS_TODO and plan; full regression                                       | ⬜ Pending |

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

| Phase   | To-do                                                                                                                                    | Status    |
| -----   | -----                                                                                                                                    | ------    |
| 1.1–1.3 | Research SAP access (HANA/OData/RFC); decide primary path; define config shape                                                           | ⬜ Pending |
| 2.1–2.3 | Connector module (discovery, sampling, scan_column, save_finding); register; optional [sap] extra                                         | ⬜ Pending |
| 3.1–3.3 | USAGE/TECH_GUIDE (EN + pt-BR); tests; pitch/roadmap update in README                                                                     | ⬜ Pending |

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

---

## How to use this list

1. **Execute to-dos** in the recommended sequence (or in dependency order within a plan).
1. **Mark done** in both this file and the plan file when a step is implemented, tested, and documented.
1. **After each step:** run `uv run pytest -v -W error` to ensure no regression.
1. **Documentation:** Update USAGE, TECH_GUIDE, SECURITY, or dedicated docs (EN + pt-BR) as features land; add new doc files to docs/README index and, if needed, to test_docs_markdown.
1. **New to-dos:** When adding a new to-do to any plan, add it here under the corresponding plan section so this remains the source of truth.

---

## Last synced with plan files. Update this doc when completing steps or when plans change.
