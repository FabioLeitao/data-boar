# Data Boar

![Data Boar mascot](api/static/mascot/data_boar_mascote_color.svg)

**Português (Brasil):** [README.pt_BR.md](README.pt_BR.md) · [docs/USAGE.pt_BR.md](docs/USAGE.pt_BR.md)

---

## For decision-makers and compliance leads

Your organization needs to know **where** personal and sensitive data lives—to comply with **LGPD**, **GDPR**, **CCPA**, **HIPAA**, **GLBA** and to avoid costly surprises. Full-scale audits and manual discovery are often **expensive and time-consuming**. **Data Boar** helps you build **compliance awareness** and surface **possible violations**—including ones that are easy to miss—without out-of-control cost: a single, configurable engine that roots through your data and reports what it finds, so your IT, cybersecurity, and compliance teams, together with DPOs, can take informed action and reduce the risk of penalties.

**What we surface:** Beyond obvious PII (CPF, email, phone, etc.), Data Boar uses **AI** (machine learning and optional deep learning) to detect **sensitive categories** (health, religion, political opinion, biometric, genetic, and others under LGPD Art. 5 II and GDPR Art. 9), **quasi-identifier combinations** that can re-identify individuals (LGPD Art. 5, GDPR Recital 26), and **possible minor data** (LGPD Art. 14, GDPR Art. 8). It recognises **regional document names** (e.g. French carte bleue, carte vitale) and flags **ambiguous identifiers** (e.g. doc_id) for manual confirmation. It can reveal exposure in **legacy columns**, **exports**, **dashboards**, and **multiple sources** in one view—so you see gaps that manual checks or rule-only tools often miss.

Like a **boar**, it is **hungry and tenacious**: it keeps searching, digs into many sources, and doesn’t stop at the surface. It’s tough enough for heterogeneous environments. Data Boar is ready to **ingest and digest your “data soup”**—whatever the ingredients, from **many sources** (files, SQL, NoSQL, APIs, shares, and the like) to **many languages, encodings, and regions** across your estate. When properly configured and authorized, it can scan **local and remote files**, **SQL databases** (PostgreSQL, MySQL, SQL Server, Oracle, Snowflake, and more), **NoSQL** (MongoDB, Redis), **APIs**, **dashboards**, **Power BI**, **Dataverse**, **SharePoint**, **WebDAV**, **SMB/NFS**, and other sources. When you supply optional passwords in config, **even locked files in the soup** (password-protected PDFs, ZIP-based documents) can be opened and scanned so nothing is left unturned. It **does not store or exfiltrate** personal or sensitive content—only **metadata** (where something was found, pattern type, sensitivity level). So you get **visibility for maturity and remediation** without moving or copying PII.

**Why it holds up:** One engine for many sources; **config-driven** tuning (regex, ML/DL terms, norm tags, recommendation overrides) so you can align with different frameworks without code changes; **Excel reports** and **heatmaps** with trends across sessions; **schedulable** scans via API for continuous monitoring. We already support **LGPD**, **GDPR**, **CCPA**, **HIPAA**, and **GLBA** out of the box and provide **sample configuration and config-file examples** (e.g. [regex overrides](docs/regex_overrides.example.yaml), recommendation overrides in [USAGE](docs/USAGE.md)) so you can extend to **UK GDPR**, **EU GDPR**, **Benelux**, **PIPEDA**, **POPIA**, **APPI**, **PCI-DSS**, or custom norms. **Sample configs for UK GDPR, EU GDPR, Benelux, PIPEDA, POPIA, APPI, and PCI-DSS** are in [docs/compliance-samples](docs/compliance-samples/) (see [compliance frameworks](docs/COMPLIANCE_FRAMEWORKS.md)); additional regional samples (e.g. Philippines, Australia, Singapore, UAE, Argentina, Kenya, India, Turkey) are in the same folder. **Whatever the language, encoding, or region of your data soup**, the boar is built for it: config and pattern files can use **UTF-8** (recommended), UTF-8 with BOM, or legacy encodings (Windows ANSI, Latin-1), with the main config read by **auto-detection** so mixed environments don’t break. Terms and reports can follow the language of your region (e.g. EN+FR for Canada, PT-BR+EN for Brazil, Japanese or Arabic for APAC/MENA). Set **`pattern_files_encoding`** when using non-UTF-8 pattern files—see [USAGE](docs/USAGE.md#file-encoding-config-and-pattern-files). If your regulation or compliance scope needs specific tuning, **we can assist**—tailored config files or small code-side adjustments—when you reach out. **Configurable timeouts** (global and per-target) keep one slow source from blocking the run. **Security hardening** (validation, headers, audit) is in place so deployments can meet auditor expectations. **Roadmap** priorities include more compliance samples (EU GDPR, Benelux, PIPEDA, POPIA, APPI, PCI-DSS, and optional regional ones), optional scanning inside compressed archives, stronger crypto and controls validation, detection improvements and false-negative reduction (optional techniques and inference on aggregated data), and SAP and other enterprise sources—so the product keeps evolving toward the controls your auditors expect.

Reporting covers **multiple scan sessions** with **trends** (this run vs previous runs), **recommendations** based on findings, **heatmaps**, and evolution over time. You can **schedule scans** via scripts or orchestrators that call its **internal API**, so continuous compliance monitoring is possible. The tool is **flexible**: tune it to other compliance checks by changing **configuration** (regex, ML/DL terms, norm tags, recommendation overrides)—no code change for many scenarios. It helps **IT, cybersecurity, compliance, and DPOs** work together to understand exposure and take action under the regulations you care about, **no matter what’s in the soup**.

**We invite you to get in touch** to see how Data Boar can support your compliance journey.

**Typical scenarios:** Preparing for an audit or regulator request; mapping data before a migration or DLP rollout; raising compliance awareness without a full war room.

> **Current release:** 1.5.4. Release notes: [docs/releases/](docs/releases/) and the [GitHub Releases page](https://github.com/FabioLeitao/data-boar/releases).
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

**Quick start (from repo root):** `uv sync` → prepare `config.yaml` (see `deploy/config.example.yaml` and [USAGE](docs/USAGE.md)) → `uv run python main.py --config config.yaml` for one-shot, or `uv run python main.py --config config.yaml --web` for the API and dashboard at <http://localhost:8088/>.

**Full documentation index** (browse all topics and languages): [docs/README.md](docs/README.md) · [docs/README.pt_BR.md](docs/README.pt_BR.md).

**License and copyright:** [LICENSE](LICENSE) · [NOTICE](NOTICE) · [docs/COPYRIGHT_AND_TRADEMARK.md](docs/COPYRIGHT_AND_TRADEMARK.md) ([pt-BR](docs/COPYRIGHT_AND_TRADEMARK.pt_BR.md)).
