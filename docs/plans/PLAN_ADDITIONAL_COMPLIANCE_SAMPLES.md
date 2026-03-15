# Plan: Additional compliance scans and sample configs (UK GDPR, EU GDPR, Benelux, PIPEDA, POPIA, APPI, PCI-DSS)

**Status:** Not started
**Synced with:** [PLANS_TODO.md](PLANS_TODO.md) (central to-do list)

## When implementing steps: update docs and tests; then update PLANS_TODO.md and this file.

This plan adds **sample configuration files** and documentation so the application can be used out-of-the-box for **additional compliance frameworks** (UK GDPR, EU GDPR, Benelux, PIPEDA, POPIA, APPI, PCI-DSS) with the same scan-and-report flow already used for LGPD, GDPR, CCPA, HIPAA, and GLBA. It ensures **flexibility** and **sellability** for future contracts (e.g. scanning company data for UK, Canadian, South African, Japanese, or payment-card compliance) while keeping **complexity low** (config-only; no code changes required for detection and reporting). The plan covers **what to put in which file**, **how the samples achieve each compliance**, **pitch** (short, professional mention in README) and **technical depth** (dedicated doc and links from USAGE/TECH_GUIDE), plus **tests** and **new doc files** where needed.

---

## Goals

- **Extend “default” compliance coverage** with 3–5 additional regulations via **sample configs** (regex overrides, ML/DL terms, recommendation overrides) so users can enable a given framework by pointing the main config at those samples (or merging them).
- **Document clearly** what goes in `regex_overrides_file`, `ml_patterns_file` / `dl_patterns_file` (or inline `sensitivity_detection`), and `report.recommendation_overrides` for each framework, and how combining them makes the app report violations and recommendations for that regulation.
- **Pitch:** Add a short, professional line in the README (and pt-BR) that sample configs for UK GDPR, EU GDPR, Benelux, PIPEDA, POPIA, APPI, and PCI-DSS are available and where to find them.
- **Technical depth:** Detail in a dedicated section (new doc or extended [COMPLIANCE_FRAMEWORKS.md](COMPLIANCE_FRAMEWORKS.md)) how to achieve each compliance: which files to use, how to merge or reference them, and how to interpret the report (Base legal, Risco, Recomendação, Prioridade, Relevante para).
- **Tests:** Add tests (or doc checks) that validate each sample file (structure, valid YAML, correct keys) so samples do not regress.
- **Balance:** Choose regulations that offer good **market penetration** and **useful flexibility** without excessive **complexity** (config-only; minimal new concepts).

---

## Recommended regulations (3–5) and rationale

| Regulation  | Scope                                                 | Why include                                                                                                                                                                               | Complexity vs benefit                                                                                             |
| ----------  | -----                                                 | -----------                                                                                                                                                                               | ----------------------                                                                                            |
| **UK GDPR** | UK (post-Brexit) + EU-like                            | High sellability (UK companies, adequacy, ICO); same concepts as EU GDPR; norm_tag and overrides map directly.                                                                            | **Low** – same patterns as GDPR; add UK-specific norm_tag and recommendation text.                                |
| **EU GDPR** | EEA (EU 27 + EEA states)                              | Explicit EEA scope; many contracts require EU (not UK) alignment; EDPB and member-state DPAs; distinct from UK post-Brexit/DPDI.                                                           | **Low** – norm_tag "EU GDPR"/"GDPR", Art. 4(1), Recitals, EDPB; optional EN + DE/FR terms.                           |
| **Benelux** | Belgium, Netherlands, Luxembourg                      | EU GDPR applies; national IDs (Dutch BSN, Belgian NISS/INS, Luxembourg matricule) and national DPAs (APD/GBA, Autoriteit Persoonsgegevens, CNPD); useful for Benelux-focused deployments. | **Low–medium** – EU GDPR base + regex for BSN, NISS, LU ID; recommendation_overrides for national DPAs; EN + NL/FR terms. |
| **PIPEDA**  | Canada – federal private sector                       | North American market; many enterprises need Canadian privacy; “personal information” definition and consent/limitation align with existing detection.                                    | **Low–medium** – add Canadian identifiers (e.g. SIN), terms, and recommendation_overrides for PIPEDA.             |
| **POPIA**   | South Africa                                          | Growing African market; “personal information” and “responsible party” concepts similar to GDPR/LGPD; good for contracts in SA and pan-African expansion.                                 | **Low–medium** – add SA identifiers if needed, terms, and overrides for POPIA.                                    |
| **APPI**    | Japan – Act on the Protection of Personal Information | Asia-Pacific market; “personal information” and “retained personal data”; different terminology but same config mechanism (regex + ML terms + overrides).                                 | **Medium** – add Japanese column-name/term examples and overrides; doc in EN/pt-BR can still describe APPI.       |
| **PCI-DSS** | Payment card data (global)                            | Already partially covered (credit card regex, financial risk); explicit **sample** ties patterns and recommendations to PCI-DSS so reports speak the language of merchants and assessors. | **Low** – bundle existing financial patterns + dedicated recommendation_overrides and optional regex refinements. |

**Out of scope for this plan (can be later):** SOC 2, ISO 27001 (control frameworks; different “violation” model), state-level US laws beyond CCPA (e.g. VCDPA, CPA), ePrivacy (cookies/comms) – can be added as more samples once the pattern is established.

---

## File layout and what goes where

The app already supports:

- **`regex_overrides_file`** – list of `{ name, pattern, norm_tag }`; match in column name or sample → finding with that norm_tag.
- **`ml_patterns_file`** / **`dl_patterns_file`** (or **`sensitivity_detection.ml_terms`** / **`dl_terms`**) – list of `{ text, label: sensitive | non_sensitive }` for ML/DL; column names and sample text classified by these terms; detector assigns norm_tag from built-in or pattern name.
- **`report.recommendation_overrides`** – list of `{ norm_tag_pattern, base_legal, risk, recommendation, priority, relevant_for }`; first match (substring or exact) on `norm_tag` sets the recommendation row in the Excel report.

To add a **new compliance** (e.g. UK GDPR, PIPEDA):

1. **Regex:** Add patterns (e.g. UK NIN, Canadian SIN, SA ID) and set `norm_tag` to e.g. `"UK GDPR"`, `"PIPEDA"`, `"POPIA"`, `"APPI"`, `"PCI-DSS"` so findings get that tag.
1. **ML/DL terms:** Add terms (column-name and value hints) that are typical for that regulation (e.g. “personal information”, “data subject”, “responsible party” for POPIA; “retained personal data” for APPI) with label `sensitive` so the classifier can tag columns; ensure detector uses or maps to the same norm_tag where applicable.
1. **Recommendation overrides:** Add entries with `norm_tag_pattern` matching those norm_tags and framework-specific `base_legal`, `risk`, `recommendation`, `priority`, `relevant_for`.

**Proposed location for samples:** `docs/compliance-samples/` (or `deploy/compliance-samples/` so they sit next to deploy configs). Each regulation can have:

- **`<regulation>_regex.yaml`** – regex overrides (and norm_tag) for that regulation.
- **`<regulation>_ml_terms.yaml`** – ML (and optionally DL) terms for column/sample classification.
- **`<regulation>_recommendation_overrides.yaml`** – snippet (list of overrides) to be merged into `report.recommendation_overrides`.

Alternatively, **one file per regulation** that contains all three (e.g. `uk_gdpr.yaml` with sections or top-level keys that the user copies into main config or that we document as “include these in your config”). Prefer **one combined sample per regulation** (single file with comments) so the user has a single “UK GDPR profile” to point to or paste from.

**Naming convention:** `compliance-sample-uk_gdpr.yaml`, `compliance-sample-eu_gdpr.yaml`, `compliance-sample-benelux.yaml`, `compliance-sample-pipeda.yaml`, `compliance-sample-popia.yaml`, `compliance-sample-appi.yaml`, `compliance-sample-pci_dss.yaml`. Each file is self-contained (or references only standard paths) and documented at the top with “Copy into your config or set regex_overrides_file / ml_patterns_file and merge report.recommendation_overrides”.

---

## To-dos (concise)

| #                     | To-do                                                                                                                                                                                                                                                                                                                                                                                                                                                     | Status                                    |
| ---                   | -----                                                                                                                                                                                                                                                                                                                                                                                                                                                     | ------                                    |
| **1. Samples**        |                                                                                                                                                                                                                                                                                                                                                                                                                                                           |                                           |
| 1.1                   | Create `docs/compliance-samples/` (or `deploy/compliance-samples/`). Add README in that folder listing the five samples and one-line purpose.                                                                                                                                                                                                                                                                                                             | Done                                      |
| 1.2                   | **UK GDPR:** Sample file with regex (e.g. UK NIN if desired), ML terms (UK/data subject terms), and recommendation_overrides (UK GDPR Art. 4(1), ICO, etc.). Document in sample header how to include in main config.                                                                                                                                                                                                                                     | Done                                      |
| 1.3                   | **PIPEDA (Canada):** Sample with regex (e.g. Canadian SIN), ML terms in **English and French** (e.g. personal information / renseignements personnels, consent / consentement) per compliance-samples-language rule, recommendation_overrides (PIPEDA s. 2, Privacy Commissioner). Create in next phase after UK GDPR.                                                                                                                                   | ⬜ Pending (next phase)                   |
| 1.4                   | **POPIA:** Sample with regex (SA ID if needed), ML terms (responsible party, personal information), recommendation_overrides (POPIA sections, Information Regulator).                                                                                                                                                                                                                                                                                     | ⬜ Pending                                 |
| 1.5                   | **APPI:** Sample with ML terms (Japanese or English equivalents for personal information, retained personal data), recommendation_overrides (APPI articles, PPC).                                                                                                                                                                                                                                                                                         | ⬜ Pending                                 |
| 1.6                   | **PCI-DSS:** Sample bundling existing financial/card patterns and recommendation_overrides (PCI-DSS requirements, tokenization, scope).                                                                                                                                                                                                                                                                                                                   | ⬜ Pending                                 |
| 1.7                   | **EU GDPR (EEA):** Sample with norm_tag "EU GDPR" (or "GDPR"), ML terms (data subject, personal data, Art. 4(1)), recommendation_overrides (EU 2016/679 Art. 4(1), Recitals, EDPB; member-state DPAs). Optional: EN + DE/FR terms for multilingual EU data.                                                                                                                                                                                                 | ⬜ Pending (next phase)                   |
| 1.8                   | **Benelux:** Sample extending EU GDPR with Benelux national identifiers (Dutch BSN, Belgian NISS/INS, Luxembourg national ID regex) and recommendation_overrides referencing national DPAs (BE: APD/GBA, NL: Autoriteit Persoonsgegevens, LU: CNPD). Terms in EN + NL/FR as relevant for BE/NL/LU data.                                                                                                                                                   | ⬜ Pending (next phase)                   |
| **2. Documentation**  |                                                                                                                                                                                                                                                                                                                                                                                                                                                           |                                           |
| 2.1                   | **Pitch (README):** In the “For decision-makers” or “Technical overview” section, add one short sentence: e.g. “Sample configs for **UK GDPR**, **EU GDPR**, **Benelux**, **PIPEDA**, **POPIA**, **APPI**, and **PCI-DSS** are available in [docs/compliance-samples](docs/compliance-samples/) (see [compliance-frameworks](docs/COMPLIANCE_FRAMEWORKS.md)).” Same in README.pt_BR.md.                                                                       | ⬜ Pending                                 |
| 2.2                   | **Technical depth:** In [COMPLIANCE_FRAMEWORKS.md](COMPLIANCE_FRAMEWORKS.md) (or a new **docs/compliance-samples.md**), add a section “Compliance samples” that (1) lists each regulation, (2) explains what to put in which file (regex_overrides_file, ml_patterns_file, recommendation_overrides), (3) describes how to use the sample (copy into config, or set paths and merge overrides), (4) links to each sample file. EN and pt-BR.              | Draft done (UK GDPR; complete in Phase 4) |
| 2.3                   | **USAGE / TECH_GUIDE:** In USAGE.md (and pt-BR), add a short subsection or link under “report” or “sensitivity” pointing to compliance-samples and compliance-frameworks for “other regulations”. In TECH_GUIDE, add a line under configuration or compliance pointing to the same.                                                                                                                                                                       | ⬜ Pending                                 |
| 2.4                   | **docs/README.md index:** Add a row (or cell) for “Compliance samples” linking to the new doc/section and the samples folder.                                                                                                                                                                                                                                                                                                                             | ⬜ Pending                                 |
| **3. Tests**          |                                                                                                                                                                                                                                                                                                                                                                                                                                                           |                                           |
| 3.1                   | Add a test that loads each sample YAML (compliance-sample-*.yaml) and asserts valid structure: if it contains a list of regex items, each has `name`, `pattern`, `norm_tag`; if it contains ml_terms, each has `text` and `label`; if it contains recommendation_overrides, each has `norm_tag_pattern` and the usual keys. Optional: run config loader with a minimal config that references the sample as regex_overrides_file and assert no exception. | Done (tests/test_compliance_samples.py)   |
| 3.2                   | If a new doc file is created (e.g. compliance-samples.md), add it to the docs existence test (test_docs_markdown or similar) so it is not forgotten.                                                                                                                                                                                                                                                                                                      | ⬜ Pending                                 |
| **4. No regressions** |                                                                                                                                                                                                                                                                                                                                                                                                                                                           |                                           |
| 4.1                   | Ensure existing behaviour unchanged: existing configs and reports still work; samples are additive. Run full test suite after adding samples and docs.                                                                                                                                                                                                                                                                                                    | ⬜ Pending                                 |

---

## What goes in which file (reference for implementers)

| File / config key                                         | Purpose                                                                                                                                             | Per-regulation content                                                                                                                                                                                                                   |
| -----------------                                         | -------                                                                                                                                             | ----------------------                                                                                                                                                                                                                   |
| **regex_overrides_file**                                  | Custom regex patterns; match → finding with HIGH and given norm_tag.                                                                                | Add patterns for identifiers (e.g. UK NIN, SIN, SA ID) and set norm_tag to the regulation name (e.g. UK GDPR, PIPEDA, POPIA). PCI-DSS: card patterns with norm_tag PCI-DSS.                                                              |
| **ml_patterns_file** / **sensitivity_detection.ml_terms** | ML (and DL) training terms; column names and sample text classified as sensitive/non_sensitive; detector assigns norm_tag from pattern or defaults. | Add terms typical for that regulation (e.g. “data subject”, “personal information”, “responsible party”, “retained personal data”) so columns get classified and, where the detector maps to norm_tag, report shows the right framework. |
| **report.recommendation_overrides**                       | Override “Base legal”, “Risco”, “Recomendação”, “Prioridade”, “Relevante para” per norm_tag.                                                        | One or more entries with norm_tag_pattern matching the regulation (e.g. "UK GDPR", "PIPEDA") and framework-specific base_legal, risk, recommendation, priority, relevant_for.                                                            |

Samples can be **single-file** (one YAML with commented sections for regex, ml_terms, recommendation_overrides) that the user copies into their config, or **split** (regex file, ml file, overrides snippet) with a README in the folder explaining “set regex_overrides_file to … and merge this list into report.recommendation_overrides”. Prefer **one file per regulation** containing all three so “enable UK GDPR” = “include this file’s blocks in your config”.

---

## Order of execution

1. Create folder and README (1.1).
1. Add one sample (e.g. UK GDPR) end-to-end (1.2) and document it in compliance-frameworks or compliance-samples (2.2 draft).
1. Add remaining samples (1.3–1.8: PIPEDA, POPIA, APPI, PCI-DSS, EU GDPR, Benelux).
1. Pitch in README (2.1); technical depth and USAGE/TECH_GUIDE/index (2.2–2.4).
1. Tests (3.1, 3.2) and regression check (4.1).

---

## Why these compliances help the application

- **UK GDPR:** Strong demand in UK and post-Brexit adequacy; minimal extra work; improves positioning for UK and EU–UK dual scope.
- **EU GDPR:** Explicit EEA (EU 27 + EEA) scope; many RFPs and contracts require EU (not UK) alignment; EDPB and member-state DPA references; distinct from UK post-Brexit/DPDI.
- **Benelux:** Belgium, Netherlands, Luxembourg; EU GDPR plus national IDs (BSN, NISS, Luxembourg matricule) and national DPA references; useful for Benelux-focused or multilingual (NL/FR) deployments.
- **PIPEDA:** Opens Canadian market and RFPs that require Canadian privacy mapping.
- **POPIA:** Supports South African and pan-African engagements.
- **APPI:** Supports Japan and APAC clients with local compliance needs.
- **PCI-DSS:** Makes existing card/financial detection explicitly “PCI-DSS ready” in reports, improving sellability to merchants and assessors.

Together they show **flexibility** (one engine, many frameworks via config) and **readiness** for multi-jurisdiction and multi-framework contracts without code changes.

---

*Last updated: plan created. Update this doc when completing steps or when new regulations/samples are added.*
