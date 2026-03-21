# Compliance and legal — summary for legal and compliance teams

**Português (Brasil):** [COMPLIANCE_AND_LEGAL.pt_BR.md](COMPLIANCE_AND_LEGAL.pt_BR.md)

This document gives a short, factual summary for **legal**, **compliance**, and **DPO** audiences: what the application surfaces, what it does not do, which frameworks are supported, where evidence lives, and where to find detailed technical and security information.

---

## What we surface (and under which provisions)

- **Personal and sensitive data:** Detection of PII (e.g. CPF, email, phone) and of **sensitive categories** under **LGPD Art. 5 II** and **GDPR Art. 9** (health, religion, political opinion, biometric, genetic, and related).
- **Quasi-identifiers and re-identification risk:** Combinations that can re-identify individuals, in line with **LGPD Art. 5** and **GDPR Recital 26**.
- **Possible minor data:** Indicators of data relating to minors, in line with **LGPD Art. 14** and **GDPR Art. 8**.
- **Regional and ambiguous identifiers:** Regional document names (e.g. French carte bleue, carte vitale) and ambiguous identifiers (e.g. doc_id) flagged for manual confirmation.
- **Multi-source visibility:** Exposure across legacy columns, exports, dashboards, and multiple data sources in one view; support for files, SQL, NoSQL, APIs, Power BI, Dataverse, SharePoint, SMB/NFS, and other connectors (see [TECH_GUIDE](TECH_GUIDE.md)).

---

## What we do not do

- **No storage or exfiltration of PII:** The application does not store or exfiltrate personal or sensitive *content*. It retains only **metadata** (where something was found, pattern type, sensitivity level) so you get visibility for maturity and remediation without moving or copying PII. Reports and heatmaps contain findings and recommendations, not raw personal data.

---

## Supported frameworks and sample configuration

- **Built-in (out of the box):** LGPD, GDPR, CCPA, HIPAA, GLBA (norm tags and recommendation text in reports).
- **Sample configs (ready to use):** UK GDPR, EU GDPR, Benelux, PIPEDA, POPIA, APPI, PCI-DSS, and additional regional frameworks (e.g. Philippines, Australia, Singapore, UAE, Argentina, Kenya, India, Turkey) are available as configuration files in [compliance-samples/](compliance-samples/). Each sample is a single YAML file (regex patterns, ML terms, recommendation overrides) so you can align with a framework without code changes. Full list and usage: [COMPLIANCE_FRAMEWORKS.md](COMPLIANCE_FRAMEWORKS.md).

---

## Evidence and outputs

- **Excel reports** per scan session: findings by target, column, pattern type, sensitivity level, and framework-specific recommendation text (base legal, risk, recommendation, priority).
- **Heatmaps** and **trends** across sessions (this run vs previous runs) for evolution over time.
- **Schedulable** scans via internal API so continuous compliance monitoring can be automated; reports and heatmaps are the audit trail.

---

## Security, encodings, and operations

- **Security:** Validation of inputs (e.g. tenant/technician), request body size limit (API), and logging policy (no API keys, passwords, or connection strings in logs). See [SECURITY.md](SECURITY.md) ([pt-BR](SECURITY.pt_BR.md)).
- **Encodings and languages:** Config and pattern files support UTF-8 (recommended), UTF-8 with BOM, or legacy encodings (e.g. Windows ANSI, Latin-1); main config is read with auto-detection. Terms and reports can follow the language of your region (e.g. EN+FR for Canada, PT-BR+EN for Brazil). See [USAGE.md](USAGE.md#file-encoding-config-and-pattern-files) ([pt-BR](USAGE.pt_BR.md)).
- **Timeouts:** Configurable timeouts (global and per target) so one slow source does not block the run.

---

## Tailored tuning and support

If your regulation or compliance scope needs specific tuning (e.g. custom norm tags, recommendation text, or pattern sets), we can assist with tailored config files or small code-side adjustments. Reach out to discuss.

---

## Where to go next

| Need                                        | Document                                                                                                                |
| ------                                      | ----------                                                                                                              |
| Configuration schema, credentials, examples | [USAGE.md](USAGE.md) · [USAGE.pt_BR.md](USAGE.pt_BR.md)                                                                 |
| List of frameworks and how to use samples   | [COMPLIANCE_FRAMEWORKS.md](COMPLIANCE_FRAMEWORKS.md) · [COMPLIANCE_FRAMEWORKS.pt_BR.md](COMPLIANCE_FRAMEWORKS.pt_BR.md) |
| Security (fixes, logging, body limit)       | [SECURITY.md](SECURITY.md) · [SECURITY.pt_BR.md](SECURITY.pt_BR.md)                                                     |
| Install, run, connectors, deploy            | [TECH_GUIDE.md](TECH_GUIDE.md) · [TECH_GUIDE.pt_BR.md](TECH_GUIDE.pt_BR.md)                                             |
| Full documentation index                    | [README.md](README.md) · [README.pt_BR.md](README.pt_BR.md)                                                             |
