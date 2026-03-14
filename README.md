# Data Boar

![Data Boar mascot](api/static/mascot/data_boar_mascote_color.svg)

**Português (Brasil):** [README.pt_BR.md](README.pt_BR.md) · [docs/USAGE.pt_BR.md](docs/USAGE.pt_BR.md)

---

## For decision-makers and compliance leads

Your organization needs to know **where** personal and sensitive data lives—to comply with **LGPD**, **GDPR**, **CCPA**, **HIPAA**, **GLBA** and to avoid costly surprises. But full-scale audits and endless war rooms are expensive and disruptive. **Data Boar** helps you build **compliance awareness** and find **possible violations** without out-of-control costs: a single, configurable engine that roots through your data and reports what it finds, so your IT, cybersecurity, and compliance teams—together with DPOs—can take informed action and reduce the risk of penalties.

Like a **boar**, it is **hungry and tenacious**: it keeps searching, digs into many sources, and doesn’t stop at the surface. It’s tough enough for heterogeneous environments. Data Boar is ready to **ingest and digest your “data soup”**—whatever the ingredients. When properly configured and authorized, it can scan **local and remote files**, **SQL databases** (PostgreSQL, MySQL, SQL Server, Oracle, Snowflake, and more), **NoSQL** (MongoDB, Redis), **APIs**, **dashboards**, **Power BI**, **Dataverse**, **SharePoint**, **WebDAV**, **SMB/NFS**, and other sources. It **does not store or exfiltrate** personal or sensitive content—only **metadata** (where something was found, pattern type, sensitivity level). So you get **visibility for maturity and remediation** without moving or copying PII.

Reporting covers **multiple scan sessions** with **trends** (this run vs previous runs), **recommendations** based on findings, **heatmaps**, and evolution over time. You can **schedule scans** via scripts or orchestrators that call its **internal API**, so continuous compliance monitoring is possible. The tool is **flexible**: you can tune it to other compliance checks by changing **configuration** (regex, ML/DL terms, norm tags, recommendation overrides)—no code change required for many scenarios. It helps **IT, cybersecurity, compliance, and DPOs** work together to understand exposure and take proper action under the regulations you care about.

**We invite you to get in touch** to see how Data Boar can support your compliance journey.

**Typical scenarios:** Preparing for an audit or regulator request; mapping data before a migration or DLP rollout; raising compliance awareness without a full war room.

> **Current release:** 1.5.2. Release notes: [docs/releases/](docs/releases/) and the [GitHub Releases page](https://github.com/FabioLeitao/data-boar/releases).
> **Documentation note:** This README and `docs/USAGE.md` are the canonical English references. When features or options change, update **both** languages to keep them in sync.

---

## Technical overview

Data Boar runs as a **one-shot CLI** audit or as a **REST API** (default port 8088) with a web dashboard. You configure **targets** (databases, filesystems, APIs, shares, Power BI, Dataverse) and **sensitivity detection** (regex + ML, optional DL) in a single **YAML or JSON** config file. It writes findings and session metadata to a local **SQLite** database and produces **Excel reports** and a **heatmap PNG** per session.

| If you need…                                        | See                                                                                                                               |
| -------------                                       | ---                                                                                                                               |
| Install, run, CLI/API reference, connectors, deploy | [Technical guide (EN)](docs/TECH_GUIDE.md) · [Guia técnico (pt-BR)](docs/TECH_GUIDE.pt_BR.md)                                     |
| Configuration schema, credentials, examples         | [USAGE.md](docs/USAGE.md) · [USAGE.pt_BR.md](docs/USAGE.pt_BR.md)                                                                 |
| Deploy (Docker, Compose, Kubernetes)                | [deploy/DEPLOY.md](docs/deploy/DEPLOY.md) · [deploy/DEPLOY.pt_BR.md](docs/deploy/DEPLOY.pt_BR.md)                                 |
| Sensitivity detection (ML/DL terms)                 | [sensitivity-detection.md](docs/sensitivity-detection.md) · [sensitivity-detection.pt_BR.md](docs/sensitivity-detection.pt_BR.md) |
| Testing, security, contributing                     | [docs/TESTING.md](docs/TESTING.md) · [SECURITY.md](SECURITY.md) · [CONTRIBUTING.md](CONTRIBUTING.md)                              |

**Quick start (from repo root):** `uv sync` → prepare `config.yaml` (see `deploy/config.example.yaml` and [USAGE](docs/USAGE.md)) → `uv run python main.py --config config.yaml` for one-shot, or `uv run python main.py --config config.yaml --web` for the API and dashboard at <http://localhost:8088/>.

**Full documentation index** (browse all topics and languages): [docs/README.md](docs/README.md) · [docs/README.pt_BR.md](docs/README.pt_BR.md).

**License and copyright:** [LICENSE](LICENSE) · [NOTICE](NOTICE) · [docs/COPYRIGHT_AND_TRADEMARK.md](docs/COPYRIGHT_AND_TRADEMARK.md) ([pt-BR](docs/COPYRIGHT_AND_TRADEMARK.pt_BR.md)).
