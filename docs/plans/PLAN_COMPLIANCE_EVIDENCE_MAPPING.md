# Plan: Compliance evidence mapping – regulations to app features and reports

**Status:** Not started (structure only)
**Synced with:** `long-term-product-and-academic-roadmap`, [COMPLIANCE_FRAMEWORKS.md](../COMPLIANCE_FRAMEWORKS.md), [PLAN_LATO_SENSU_THESIS.md](PLAN_LATO_SENSU_THESIS.md)

This plan keeps a **structured mapping** between regulations/standards (LGPD, GDPR, FELCA, ISO/IEC 27701/27001/27002/27005, SOC 2, etc.) and **concrete app features and reports**. It is for internal and academic use—**not** for the public README roadmap.

---

## 1. Scope and structure

**Goal:** Decide which norms to include and how to represent the mapping.

### To-dos

| # | To-do | Status |
| - | ----- | ------ |
| 1.1 | List the primary norms to track in this mapping (LGPD, GDPR, FELCA, ISO/IEC 27701, ISO/IEC 27001/27002/27005, SOC 2; optionally sector norms like HIPAA/GLBA). | ⬜ Pending |
| 1.2 | Choose a simple representation: e.g. one table per norm (control/requirement → app feature/report/plan), plus short explanatory notes. | ⬜ Pending |

---

## 2. LGPD and GDPR mapping

**Goal:** Link LGPD/GDPR obligations to features/reports in a way you can reuse in product docs and academic work.

### 2.1 LGPD – example slice

| LGPD reference / tema                    | App feature / report                                           | Notes |
| ---------------------------------------- | -------------------------------------------------------------- | ----- |
| Art. 5, I (dados pessoais)              | Core detector (regex + ML/DL), norm tags `LGPD Art. 5`         | Detection and labelling of personal/sensitive data in “data soup”. |
| Art. 37 (registro das operações)        | Session reports (Excel), findings tables, run history          | Each scan acts as evidence of where data was found and under which norms. |
| Art. 14 (dados de crianças e adolescentes) | Minor data detection (DOB/age inference, minors flags) and corresponding report fields | Helps map processing of minors’ data for FELCA/LGPD obligations. |

### 2.2 GDPR – example slice

| GDPR reference / theme                  | App feature / report                                           | Notes |
| --------------------------------------- | -------------------------------------------------------------- | ----- |
| Art. 4(1) (personal data)              | Core detector (regex + ML/DL), norm tags `GDPR Art. 4(1)`      | Same detection engine; different norm tags and recommendation overrides. |
| Records of processing (Art. 30, Rec. 82) | Session inventory across connectors + Excel reports             | Inputs for RoPA and data-mapping exercises, not a full RoPA tool. |

### To-dos

| # | To-do | Status |
| - | ----- | ------ |
| 2.1 | Derive a concise LGPD → feature/report table from `COMPLIANCE_FRAMEWORKS*` and existing plans (e.g. minors’ data, cross-ref risk, inventory, crypto & controls). | ⬜ Pending |
| 2.2 | Do the same for GDPR (focus on data subject rights, records of processing, security of processing, and accountability). | ⬜ Pending |

---

## 3. ISO/IEC 27xxx and SOC 2 mapping

**Goal:** Clarify how the app **supports** (but does not replace) ISMS and trust-services controls.

### To-dos

| # | To-do | Status |
| - | ----- | ------ |
| 3.1 | For ISO/IEC 27701, identify which controls are primarily supported (e.g. records of processing, data mapping, evidence for DPIAs and cross-border flows) and link them to reports and configurations. | ⬜ Pending |
| 3.2 | For ISO/IEC 27001/27002/27005, map relevant control families (asset management, cryptography, logging/monitoring, communications security, risk treatment) to app outputs. | ⬜ Pending |
| 3.3 | For SOC 2 (Security/Availability/Confidentiality), note how discovery, inventory, and crypto/controls sheets act as evidence inputs for specific trust criteria. | ⬜ Pending |

---

## 4. FELCA and child-protection/platform norms

**Goal:** Capture how minors’ data detection and related features support FELCA and similar laws.

### To-dos

| # | To-do | Status |
| - | ----- | ------ |
| 4.1 | Map FELCA obligations (age-related, parental controls, privacy-by-default, transparency) to minors’ data detection and reporting in the app. | ⬜ Pending |
| 4.2 | Add a brief note on how the same capabilities could support other regional child-protection/platform norms (without over-claiming). | ⬜ Pending |

---

## 5. Integration with docs and academic work

**Goal:** Reuse this mapping in product docs and thesis material without duplication.

### To-dos

| # | To-do | Status |
| - | ----- | ------ |
| 5.1 | Decide where to surface high-level summaries (e.g. small excerpts in `COMPLIANCE_FRAMEWORKS*`, more detailed tables only in this plan or thesis notes). | ⬜ Pending |
| 5.2 | When a major feature/report is added (e.g. crypto & controls sheet, data-source inventory), update this mapping and note which norms/control families it strengthens. | ⬜ Pending |

---

## 6. Sync notes

- Use this plan as your **single source of truth** for detailed mappings; product docs should only expose what is needed for operators and decision-makers.
- Keep the tone careful: always “supports” or “provides evidence for”, never “fully complies” or “certifies”.

