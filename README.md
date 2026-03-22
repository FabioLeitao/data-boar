# Data Boar

**Data Boar — based on lgpd_crawler technology.** Compliance-aware discovery and mapping of personal and sensitive data across your data soup.

![Data Boar mascot](api/static/mascot/data_boar_mascote_color.svg)

**Português (Brasil):** [README.pt_BR.md](README.pt_BR.md) · [docs/USAGE.pt_BR.md](docs/USAGE.pt_BR.md)

---

## For decision-makers and compliance leads

Your organization needs to know **where** personal and sensitive data lives—to comply with **LGPD**, **GDPR**, **CCPA**, **HIPAA**, **GLBA** and to avoid costly surprises. **Data Boar** helps you build **compliance awareness** and surface **possible violations** without out-of-control cost: one configurable engine that scans your data and reports what it finds, so IT, cybersecurity, compliance, and DPOs can take informed action.

**What we surface:** Beyond obvious PII (CPF, CNPJ – including the new alphanumeric format, email, phone), we use **AI** (ML and optional DL) to detect **sensitive categories** (health, religion, political opinion, biometric, genetic—LGPD Art. 5 II, GDPR Art. 9), **quasi-identifier combinations** (LGPD Art. 5, GDPR Recital 26), and **possible minor data** (LGPD Art. 14, GDPR Art. 8). We recognise regional document names and flag ambiguous identifiers for manual confirmation, and reveal exposure across **legacy columns**, **exports**, **dashboards**, and **multiple sources** in one view—so you see gaps that manual checks or rule-only tools often miss.

The real risk—**shadow IT** and beyond—often hides in parallel spreadsheets, forgotten folders, legacy databases, lack of standardization, tangled flows, poorly documented applications, exceptions, and excessive data collection. Data Boar keeps sniffing through your data soup to uncover those hidden ingredients—including renamed or cloaked files and weaker transport or storage—so compliance and legal teams see what’s really there, not just how it’s presented.

**Hungry for your data soup:** Like a **boar**, we dig into many sources and don't stop at the surface. Whatever the ingredients—**files**, **SQL**, **NoSQL**, **APIs**, **Power BI**, **Dataverse**, **SharePoint**, **SMB/NFS**, and more—we're built to ingest and digest it. We **do not store or exfiltrate** PII, only **metadata** (where found, pattern type, sensitivity), so you get visibility for remediation without moving data. For a concise summary for legal and compliance teams, see [Compliance and legal](docs/COMPLIANCE_AND_LEGAL.md).

**Why it holds up:** One engine, **config-driven** (regex, ML/DL terms, norm tags, recommendation overrides)—no code changes to align with different frameworks. **Excel reports**, **heatmaps**, and **trends** across sessions; **schedulable** scans via API. We support **LGPD**, **GDPR**, **CCPA**, **HIPAA**, **GLBA** out of the box; **sample configs** for **UK GDPR**, **EU GDPR**, **Benelux**, **PIPEDA**, **POPIA**, **APPI**, **PCI-DSS**, and other regions are in [docs/compliance-samples](docs/compliance-samples/) ([compliance frameworks](docs/COMPLIANCE_FRAMEWORKS.md)). Multilingual and legacy encodings are supported; **configurable timeouts** and **security hardening** (validation, headers, audit) are in place. **Compressed files:** You can scan inside archives (zip, tar, gz, 7z with optional extra) via **config** (`file_scan.scan_compressed`), **CLI** (`--scan-compressed`), or the **dashboard** checkbox; see [USAGE](docs/USAGE.md) and the warning about run time and I/O. Optional **content-type** detection helps find renamed or cloaked files (e.g. PDFs disguised as .txt); early **crypto/transport** visibility (e.g. TLS vs plaintext) is collected for database and API targets. **Sniffing with judgment on the file trail:** Plain-text reads use a **configurable character budget** so the engine sees real structure—not a useless nib—before it decides; **entertainment-shaped** content (e.g. chord sheets, lyrics, typical open-source README chunks) routes **noisy ML hints** into a **review band** instead of crowding the report with spurious “certain” alerts, while **hard pattern hits** (IDs, payment data, strong PII) stay decisive for triage. **Roadmap:** **Richer soup ingredients**—optional **image metadata** and **OCR**, **audio/video** tags, and **subtitle** sidecars—so camera rolls, voicemail, and media libraries fit the same audit metaphor ([PLAN_ADDITIONAL_DATA_SOUP_FORMATS.md](docs/plans/PLAN_ADDITIONAL_DATA_SOUP_FORMATS.md), [USAGE](docs/USAGE.md)); **enterprise back-office** expansion (**SAP**, HR/SST, ERP/CRM-style ecosystems—[PLAN_SAP_CONNECTOR.md](docs/plans/PLAN_SAP_CONNECTOR.md), [PLAN_ENTERPRISE_HR_SST_ERP_CONNECTORS.md](docs/plans/PLAN_ENTERPRISE_HR_SST_ERP_CONNECTORS.md)); fuller **crypto/controls** validation; further **detection** refinement; **scan-complete / out-of-band notifications** ([PLAN_NOTIFICATIONS_OFFBAND_AND_SCAN_COMPLETE.md](docs/plans/PLAN_NOTIFICATIONS_OFFBAND_AND_SCAN_COMPLETE.md)); **dashboard and API access** patterns for subscription- or shared-network deploys (**M-ACCESS**, [SPRINTS_AND_MILESTONES.md](docs/plans/SPRINTS_AND_MILESTONES.md)). Alignment with **ISO/IEC 27701** (PIMS), **SOC 2**, and **FELCA** (minor-data mapping) is documented; we continue to extend support for auditable and regional standards.

**We invite you to get in touch** to see how Data Boar can support your compliance journey. Optional **professional services**—helping map your **data soup** and tune configuration for your regulatory mix—are summarised for legal and procurement readers in [Compliance and legal](docs/COMPLIANCE_AND_LEGAL.md) (see *Professional services*).

**Typical scenarios:** Preparing for an audit or regulator request; mapping data before a migration or DLP rollout; raising compliance awareness without a full war room.

> **Current release:** 1.6.4. Release notes: [docs/releases/](docs/releases/) and the [GitHub Releases page](https://github.com/FabioLeitao/data-boar/releases).
> **Documentation note:** This README and `docs/USAGE.md` are the canonical English references. When features or options change, update **both** languages to keep them in sync.

---

## Technical overview

Data Boar runs as a **one-shot CLI** audit or as a **REST API** (default port 8088) with a web dashboard. You configure **targets** (databases, filesystems, APIs, shares, Power BI, Dataverse) and **sensitivity detection** (regex + ML, optional DL) in a single **YAML or JSON** config file. It writes findings and session metadata to a local **SQLite** database and produces **Excel reports** and a **heatmap PNG** per session.

| If you need…                                        | See                                                                                                                               |
| -------------                                       | ---                                                                                                                               |
| Install, run, CLI/API reference, connectors, deploy | [Technical guide (EN)](docs/TECH_GUIDE.md) · [Guia técnico (pt-BR)](docs/TECH_GUIDE.pt_BR.md)                                     |
| Configuration schema, credentials, examples         | [USAGE.md](docs/USAGE.md) · [USAGE.pt_BR.md](docs/USAGE.pt_BR.md)                                                                 |
| Deploy (Docker, Compose, Kubernetes)                | [deploy/DEPLOY.md](docs/deploy/DEPLOY.md) · [deploy/DEPLOY.pt_BR.md](docs/deploy/DEPLOY.pt_BR.md)                                 |
| Sensitivity detection (ML/DL terms)                 | [SENSITIVITY_DETECTION.md](docs/SENSITIVITY_DETECTION.md) · [SENSITIVITY_DETECTION.pt_BR.md](docs/SENSITIVITY_DETECTION.pt_BR.md) |
| Testing, security, contributing                     | [docs/TESTING.md](docs/TESTING.md) · [SECURITY.md](SECURITY.md) · [CONTRIBUTING.md](CONTRIBUTING.md)                              |

**Quick start (from repo root):** `uv sync` → prepare `config.yaml` (see `deploy/config.example.yaml` and [USAGE](docs/USAGE.md)) → `uv run python main.py --config config.yaml` for one-shot, or `uv run python main.py --config config.yaml --web` for the API and dashboard (default bind `127.0.0.1`, e.g. <http://127.0.0.1:8088/>; use `--host 0.0.0.0` only with network controls). Full flags: `uv run python main.py --help`. **Do not commit** root `config.yaml` (`.gitignore`); it may contain LAN paths and secrets—see [CONTRIBUTING.md](CONTRIBUTING.md#public-repo-hygiene-lan-credentials).

**Full documentation index** (browse all topics and languages): [docs/README.md](docs/README.md) · [docs/README.pt_BR.md](docs/README.pt_BR.md).

**License and copyright:** [LICENSE](LICENSE) · [NOTICE](NOTICE) · [docs/COPYRIGHT_AND_TRADEMARK.md](docs/COPYRIGHT_AND_TRADEMARK.md) ([pt-BR](docs/COPYRIGHT_AND_TRADEMARK.pt_BR.md)).
