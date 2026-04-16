# Plan: Compliance evidence mapping – regulations to app features and reports

**Status:** Not started (structure only)
**Synced with:** `long-term-product-and-academic-roadmap`, [COMPLIANCE_FRAMEWORKS.md](../COMPLIANCE_FRAMEWORKS.md), [PLAN_LATO_SENSU_THESIS.md](PLAN_LATO_SENSU_THESIS.md)

This plan keeps a **structured mapping** between regulations/standards (LGPD, GDPR, FELCA, ISO/IEC 27701/27001/27002/27005, SOC 2, etc.) and **concrete app features and reports**. It is for internal and academic use—**not** for the public README roadmap.

---

## 1. Scope and structure

**Goal:** Decide which norms to include and how to represent the mapping.

### To-dos (Scope and structure)

| #   | To-do                                                                                                                                                          | Status    |
| -   | -----                                                                                                                                                          | ------    |
| 1.1 | List the primary norms to track in this mapping (LGPD, GDPR, FELCA, ISO/IEC 27701, ISO/IEC 27001/27002/27005, SOC 2; sector norms like HIPAA/GLBA; **backlog** of BR sector regulators and programme types in section 8). | ⬜ Pending |
| 1.2 | Choose a simple representation: e.g. one table per norm (control/requirement → app feature/report/plan), plus short explanatory notes.                         | ⬜ Pending |

---

## 2. LGPD and GDPR mapping

**Goal:** Link LGPD/GDPR obligations to features/reports in a way you can reuse in product docs and academic work.

### 2.1 LGPD – example slice

| LGPD reference / tema                      | App feature / report                                                                   | Notes                                                                     |
| ----------------------------------------   | --------------------------------------------------------------                         | -----                                                                     |
| Art. 5, I (dados pessoais)                 | Core detector (regex + ML/DL), norm tags `LGPD Art. 5`                                 | Detection and labelling of personal/sensitive data in “data soup”.        |
| Art. 37 (registro das operações)           | Session reports (Excel), findings tables, run history                                  | Each scan acts as evidence of where data was found and under which norms. |
| Art. 14 (dados de crianças e adolescentes) | Minor data detection (DOB/age inference, minors flags) and corresponding report fields | Helps map processing of minors’ data for FELCA/LGPD obligations.          |

### 2.2 GDPR – example slice

| GDPR reference / theme                   | App feature / report                                           | Notes                                                                    |
| ---------------------------------------  | -------------------------------------------------------------- | -----                                                                    |
| Art. 4(1) (personal data)                | Core detector (regex + ML/DL), norm tags `GDPR Art. 4(1)`      | Same detection engine; different norm tags and recommendation overrides. |
| Records of processing (Art. 30, Rec. 82) | Session inventory across connectors + Excel reports            | Inputs for RoPA and data-mapping exercises, not a full RoPA tool.        |

### To-dos (LGPD and GDPR mapping)

| #   | To-do                                                                                                                                                            | Status    |
| -   | -----                                                                                                                                                            | ------    |
| 2.1 | Derive a concise LGPD → feature/report table from `COMPLIANCE_FRAMEWORKS*` and existing plans (e.g. minors’ data, cross-ref risk, inventory, crypto & controls). | ⬜ Pending |
| 2.2 | Do the same for GDPR (focus on data subject rights, records of processing, security of processing, and accountability).                                          | ⬜ Pending |

---

## 3. ISO/IEC 27xxx and SOC 2 mapping

**Goal:** Clarify how the app **supports** (but does not replace) ISMS and trust-services controls.

### To-dos (ISO/IEC 27xxx and SOC 2)

| #   | To-do                                                                                                                                                                                                 | Status    |
| -   | -----                                                                                                                                                                                                 | ------    |
| 3.1 | For ISO/IEC 27701, identify which controls are primarily supported (e.g. records of processing, data mapping, evidence for DPIAs and cross-border flows) and link them to reports and configurations. | ⬜ Pending |
| 3.2 | For ISO/IEC 27001/27002/27005, map relevant control families (asset management, cryptography, logging/monitoring, communications security, risk treatment) to app outputs.                            | ⬜ Pending |
| 3.3 | For SOC 2 (Security/Availability/Confidentiality), note how discovery, inventory, and crypto/controls sheets act as evidence inputs for specific trust criteria.                                      | ⬜ Pending |

---

## 4. FELCA and child-protection/platform norms

**Goal:** Capture how minors’ data detection and related features support FELCA and similar laws.

### To-dos (FELCA and child-protection)

| #   | To-do                                                                                                                                        | Status    |
| -   | -----                                                                                                                                        | ------    |
| 4.1 | Map FELCA obligations (age-related, parental controls, privacy-by-default, transparency) to minors’ data detection and reporting in the app. | ⬜ Pending |
| 4.2 | Add a brief note on how the same capabilities could support other regional child-protection/platform norms (without over-claiming).          | ⬜ Pending |

---

## 5. Integration with docs and academic work

**Goal:** Reuse this mapping in product docs and thesis material without duplication.

### To-dos (Integration with docs and academic work)

| #   | To-do                                                                                                                                                                 | Status    |
| -   | -----                                                                                                                                                                 | ------    |
| 5.1 | Decide where to surface high-level summaries (e.g. small excerpts in `COMPLIANCE_FRAMEWORKS*`, more detailed tables only in this plan or thesis notes).               | ⬜ Pending |
| 5.2 | When a major feature/report is added (e.g. crypto & controls sheet, data-source inventory), update this mapping and note which norms/control families it strengthens. | ⬜ Pending |

---

## 6. Artifacts and evidence sources

When extending the mapping or writing evidence-focused docs:

- **App and Docker:** This repo and image `fabioleitao/data_boar`; supporting artifacts in `docs/private/From Docker hub list of repositories.md` (wildfly_t1r, uptk for infra/observability narrative).
- **Private docs:** CV, TCC, LinkedIn in `docs/private/` (git-ignored). See [TOKEN_AWARE_USAGE.md](TOKEN_AWARE_USAGE.md) §3.

---

## 7. Sync notes

- Use this plan as your **single source of truth** for detailed mappings; product docs should only expose what is needed for operators and decision-makers.
- Keep the tone careful: always “supports” or “provides evidence for”, never “fully complies” or “certifies”.

---

## 8. Candidate sectors, regulators, and programme types (backlog — not product promises)

**Purpose:** Remember **where** the product can **honestly** help (inventory, metadata-only findings, config-led labels) versus **what** requires **specialist tools**, **certified cryptography**, or **legal/sector counsel**. This section is **internal** scoping for future doc rows, optional `compliance-samples` YAML, and **consulting** scoping—not a public compliance claim.

**Maintainer / operator intent (internal memory — not an exhaustive development promise):** This backlog exists for **long-term orientation**, **control**, and **remembering eventual client-specific scoping** when a real engagement appears—for example a **Brazilian health-plan broker** needing **LGPD** plus **ANS**-adjacent **lexicon** and **recommendation** text (partial alignment, not a substitute for ANS regulatory filings). Listing terms or regulators **here** is **not** a commitment to build every corresponding feature; the typical response remains **configuration**, **optional samples**, **recommendation overrides**, and **professional services**, **prioritized when** a named client need shows up.

**Brazil — health data and HIPAA analogy:** There is **no** statute that copies **HIPAA/HITECH/ePHI** as a single package. **LGPD** (e.g. sensitive personal data including **health**, **Art. 11**) applies broadly; **sector** layers include **ANS** (health plans), **CFM** (medical practice / records norms), **ANVISA** (products and regulated activities), and other **RDCs** and norms. **Alignment for clients:** same engine as elsewhere—**discovery and mapping** of health-related and identifier patterns with **LGPD** (and **HIPAA** where data crosses US contexts); **not** a substitute for **clinical system** validation or **ANS/CFM**-specific controls. **Samples today:** **`compliance-sample-lgpd.yaml`**; built-in **HIPAA** tags in the app for US-facing wording; **no** separate “BR HIPAA” YAML unless we later add an optional **health-sector lexicon** sample (doc-only / low-code).

**Brazil — financial / capital markets / public sector (examples, not exhaustive):** **BACEN** (including resolutions on cybersecurity and data), **CVM**, **SUSEP**, **B3** rules, **RFB** (tax/secrecy and ancillary obligations), **Dataprev**-related and other **public-sector** processing—all sit **on top of LGPD** and sector law. The product **does not** implement **PLD/Fiscal** transaction monitoring or **regulatory reporting**; it **can** support **data inventory** and **PII/sensitive-data visibility** for **governance** and **risk** programmes. **Samples today:** **`compliance-sample-pci_dss.yaml`** (card data patterns); **no** dedicated BACEN/SUSEP YAML yet—feasible later as **`recommendation_overrides`** + terms (with **counsel** review).

**PEP / KYC / CDD / EDD / AML adjacency:** Already positioned in [COMPLIANCE_AND_LEGAL.md](../COMPLIANCE_AND_LEGAL.md) (inventory vs list screening). Future work here is **lexicon** and **samples**, not **screening engines**.

**PCI DSS 4.x:** Existing sample targets **cardholder data** patterns; **version** evolution (3.x → 4.x) is a **periodic review** item for the sample file header and overrides—see [compliance-samples/README.md](../compliance-samples/README.md) *Sample maintenance*.

**FIPS 140-2 / 140-3:** Relevant to **deployment** (OS, OpenSSL, HSM, Python crypto stacks)—**not** something the scanner “certifies”. Mapping, if any, belongs under **operator deployment** and **environment** evidence, not detector features.

**Large enterprises and mixed programmes (e.g. energy, critical infrastructure):** Organisations often publish **internal** baselines (sometimes aligned to **NIST CSF**, **ISO 27001**, **CIS**). The product supports **technical inventory** and **policy-tagged** findings; it **does not** replace **vendor-specific** or **sector-specific** compliance programmes.

**Named companies (e.g. state-owned enterprises):** **Petrobras** and similar are **not** regulators; alignment is via **their** policies and **LGPD** plus sector safety/environment rules where applicable—same **inventory** story, **no** endorsement.

### To-dos (Sector and programme backlog)

| #   | To-do                                                                                                                                                       | Status    |
| --- | -----                                                                                                                                                       | --------- |
| 8.1 | Prioritise **one** BR-sector slice for a future optional sample or doc table (e.g. financial lexicon vs health lexicon)—token-aware; no scope creep.        | ⬜ Pending |
| 8.2 | Keep [COMPLIANCE_AND_LEGAL.md](../COMPLIANCE_AND_LEGAL.md) and [COMPLIANCE_FRAMEWORKS.md](../COMPLIANCE_FRAMEWORKS.md) as the **public** ceiling; deep regulator tables stay **here** or in **consulting** artefacts. | ⬜ Pending |
