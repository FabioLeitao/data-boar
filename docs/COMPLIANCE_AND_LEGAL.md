# Compliance and legal — summary for legal and compliance leaders

**Português (Brasil):** [COMPLIANCE_AND_LEGAL.pt_BR.md](COMPLIANCE_AND_LEGAL.pt_BR.md)

**Primary audience:** **Legal**, **compliance leadership**, and **DPOs** assessing fit, risk, and evidence—not day-to-day IT configuration. For **YAML, API limits, encodings, and timeouts**, see [COMPLIANCE_TECHNICAL_REFERENCE.md](COMPLIANCE_TECHNICAL_REFERENCE.md); for **full config and commands**, see [USAGE.md](USAGE.md).

This page states **what Data Boar reveals**, **what it does not do**, **which regulatory framings** you can align with, **what artifacts** support audits, and how **professional services** can help map your **data soup** before the product **ingests and digests** it.

---

## What we surface (and under which provisions)

- **Personal and sensitive data:** Detection of common PII (e.g. CPF, email, phone) and **special categories** in the sense of **LGPD Art. 5 II** and **GDPR Art. 9** (health, religion, political opinion, biometric, genetic, and related).
- **Quasi-identifiers and re-identification risk:** Combinations that can contribute to identifying individuals, consistent with **LGPD Art. 5** and **GDPR Recital 26**.
- **Possible minor-related data:** Indicators aligned with **LGPD Art. 14** and **GDPR Art. 8** (human review may still be required).
- **Regional and ambiguous identifiers:** Region-specific document labels and ambiguous fields flagged for **manual confirmation** where automation cannot assert certainty.
- **Multi-source visibility:** One coherent view across the **data soup** your organisation configures—databases, files, APIs, business-intelligence and collaboration systems, and other **connector** types described at a high level in [COMPLIANCE_FRAMEWORKS.md](COMPLIANCE_FRAMEWORKS.md) and [TECH_GUIDE.md](TECH_GUIDE.md)—without claiming completeness of every legacy system until targets are in scope.
- **Filesystem and rich-media triage:** The engine can **sample enough context** from text-like files to apply judgment—reducing alert fatigue where content looks like **entertainment or boilerplate** while **strong pattern matches** remain prominent for remediation. For file targets, **optional** rich-media handling includes **metadata** (e.g. EXIF, ID3, container tags), **optional OCR** on images, and **subtitle** sidecar text where configured—within sampling limits and optional dependencies (see [USAGE.md](USAGE.md) and [COMPLIANCE_TECHNICAL_REFERENCE.md](COMPLIANCE_TECHNICAL_REFERENCE.md)). **Steganography**, full-frame media analytics, **embedded tracker / web-bug** heuristics (including social/ad network patterns discussed in security education media), and systematic detection of **document-layer concealment** (e.g. microscopic or low-contrast text, hidden structure, Unicode cloaking, deeply nested embedded objects) are **not** represented as exhaustive today; they are phased as **future opt-in** capabilities—see the **Tier 3b** and **Tier 4** taxonomy in [PLAN_ADDITIONAL_DATA_SOUP_FORMATS.md](plans/PLAN_ADDITIONAL_DATA_SOUP_FORMATS.md)—so reporting stays proportionate, limits sensitive-data copying, and avoids unbounded CPU/I/O.

---

## What we do not do

- **We do not store or exfiltrate PII content** for reporting: the tool retains **metadata** (location, pattern type, sensitivity level, framework tags) so teams gain **visibility for maturity and remediation** without copying personal data into a second datastore. Excel outputs describe **findings and recommendations**, not raw personal fields.

---

## Regulatory alignment: built-in and configuration-led

- **Built into reports and detection language today:** **LGPD**, **GDPR**, **CCPA**, **HIPAA**, **GLBA** (norm references and recommendation text).
- **Additional jurisdictions and internal policies:** Many further frameworks (e.g. UK GDPR, PIPEDA, POPIA, APPI, PCI-DSS, and regional profiles) can be reflected through **configuration profiles**—adjusting pattern sets, labels, and report wording—**without forking the product**. What “small change” means in practice (files, merge steps) is documented for implementation teams in [COMPLIANCE_FRAMEWORKS.md](COMPLIANCE_FRAMEWORKS.md). **Roadmap** items continue to extend coverage over time.

**U.S. — children’s and minors’ privacy (technical mapping only):** Optional YAML samples support **technical** and **operational** inventory work (e.g. DPO review, audit preparation, or scoping under counsel)—including framings sometimes associated with **federal COPPA (FTC Rule)**, **California AB 2273**, and **Colorado CPA** rules affecting consumers under 18. This is **not legal advice**, **not** age verification or parental-consent proof, and **not** a determination that any law applies. Use [COMPLIANCE_FRAMEWORKS.md](COMPLIANCE_FRAMEWORKS.md) and [compliance-samples/](compliance-samples/) for file names and merge steps.

---

## Evidence and outputs (for audits and governance)

- **Excel reports** per scan **session**: findings by source, field/path, pattern type, sensitivity, and framework-oriented recommendation text (legal basis, risk, suggested action, priority where configured).
- **Heatmaps** and **trend views** across sessions to show **evolution**, not only a point-in-time snapshot.
- **Repeatable runs** (including automation via API) so monitoring can match your **operating model**; technical detail of scheduling and limits: [COMPLIANCE_TECHNICAL_REFERENCE.md](COMPLIANCE_TECHNICAL_REFERENCE.md).
- **Optional operator signals (webhooks):** When `notifications` is enabled, the app can POST a short scan-completion summary (e.g. Slack, Teams, Telegram, or a generic URL), including **multiple operator channels** or an optional **tenant copy** when configured — **default off**; this is operational convenience and **does not replace** Excel outputs or constitute legal evidence by itself. See [USAGE.md — Operator notifications](USAGE.md#51-operator-notifications-optional).
- **Build identity and runtime posture (operators):** Reports record **application version** in “Report info”; a planned enhancement will expose **release vs development** builds and optional **integrity** signals for enterprises (no change to legal scope until implemented). For **operational** deployment checks (not legal evidence by itself), the API **`GET /status`** includes a **`runtime_trust`** snapshot summarising whether the running configuration/environment matches expectations (e.g. unexpected local overrides).

---

## Professional services: mapping the data soup

Organisations rarely have a single, tidy inventory of every **ingredient** in their **data soup**—shadow copies, legacy exports, BI models, and ad hoc shares are common. **Data Boar** is built to **ingest and digest** what you point it at; **discovering and prioritising** those sources, **tuning** norm tags and recommendation language, and **bridging** legal expectations with technical scope is often a **joint** exercise.

**Contracted services** (consulting and fine-tuning) are available to help: scoping targets, aligning configuration to your **regulatory mix**, and shortening time-to-trust—without replacing your **DPO** or **counsel**. For licensing and commercial boundaries, see [LICENSING_OPEN_CORE_AND_COMMERCIAL.md](LICENSING_OPEN_CORE_AND_COMMERCIAL.md). **Get in touch** via the channels you already use with the maintainer (e.g. GitHub, professional email)—no obligation.

---

## Where to go next

| Need                                                | Document                                                                                                                  |
| ----                                                | --------                                                                                                                  |
| **Legal / compliance summary (this page)**          | You are here                                                                                                              |
| **IT: encodings, API limits, timeouts, automation** | [COMPLIANCE_TECHNICAL_REFERENCE.md](COMPLIANCE_TECHNICAL_REFERENCE.md) ([pt-BR](COMPLIANCE_TECHNICAL_REFERENCE.pt_BR.md)) |
| **Framework list and sample profiles**              | [COMPLIANCE_FRAMEWORKS.md](COMPLIANCE_FRAMEWORKS.md) · [COMPLIANCE_FRAMEWORKS.pt_BR.md](COMPLIANCE_FRAMEWORKS.pt_BR.md)   |
| **Config schema, credentials, CLI/API**             | [USAGE.md](USAGE.md) · [USAGE.pt_BR.md](USAGE.pt_BR.md)                                                                   |
| **Security policy**                                 | [SECURITY.md](SECURITY.md) · [SECURITY.pt_BR.md](SECURITY.pt_BR.md)                                                       |
| **Install, connectors, deploy**                     | [TECH_GUIDE.md](TECH_GUIDE.md) · [TECH_GUIDE.pt_BR.md](TECH_GUIDE.pt_BR.md)                                               |
| **Glossary**                                        | [GLOSSARY.md](GLOSSARY.md) · [GLOSSARY.pt_BR.md](GLOSSARY.pt_BR.md)                                                       |
| **Full documentation index**                        | [README.md](README.md) · [README.pt_BR.md](README.pt_BR.md)                                                               |
