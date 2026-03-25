# Compliance frameworks and extensibility

The application helps DPO, security, and compliance teams discover and map personal or sensitive data in line with multiple regulations. This document describes which frameworks are explicitly referenced today, where to find sample configuration, and how to extend support to others (e.g. UK GDPR, PIPEDA, APPI, POPIA) without code changes.

**Decision-makers (legal / compliance leadership):** start with the non-technical summary [COMPLIANCE_AND_LEGAL.md](COMPLIANCE_AND_LEGAL.md) ([pt-BR](COMPLIANCE_AND_LEGAL.pt_BR.md)); return here for **files, samples, and merge steps**.

**Português (Brasil):** [COMPLIANCE_FRAMEWORKS.pt_BR.md](COMPLIANCE_FRAMEWORKS.pt_BR.md)

---

## Regulations we support today (built-in and config examples)

**Built-in (out of the box):** The detector and reports explicitly reference **LGPD** (Brazil), **GDPR** (EU), **CCPA** (California), **HIPAA** (US health), and **GLBA** (US financial). Findings use these norm tags and recommendation text by default.

**Sample configuration and examples:** We provide config-file examples so you can align with more regulations without changing code:

- **[regex_overrides.example.yaml](regex_overrides.example.yaml)** – custom regex patterns with `norm_tag` (e.g. LGPD Art. 5, CCPA). Copy and extend for other identifiers (e.g. UK NIN, Canadian SIN) and set `norm_tag` to your framework.
- **Recommendation overrides** – in [USAGE.md](USAGE.md) (report section) you will find `report.recommendation_overrides`: list of `norm_tag_pattern`, `base_legal`, `risk`, `recommendation`, `priority`, `relevant_for`. Use this to tailor report text for any regulation (UK GDPR, PIPEDA, POPIA, APPI, PCI-DSS, or internal norms).
- **ML/DL terms** – [SENSITIVITY_DETECTION.md](SENSITIVITY_DETECTION.md) and the main config support `ml_patterns_file`, `dl_patterns_file`, or inline `sensitivity_detection.ml_terms` / `dl_terms` so you can add framework-specific terms (e.g. “personal information”, “data subject”, “responsible party”) for better detection and labelling.

**Compliance samples (one profile per regulation):** Sample configs for **UK GDPR**, **EU GDPR**, **Benelux**, **PIPEDA**, **POPIA**, **APPI**, **PCI-DSS**, and other regions are in [compliance-samples/](compliance-samples/). Each sample is a single YAML file with regex patterns, ML terms, and recommendation overrides for that framework. See the [Compliance samples](#compliance-samples) section below for the full list, what goes in which file, and how to use them. For **language and target audience** (e.g. PIPEDA → EN + FR for Canada), see the [compliance-samples README](compliance-samples/README.md).

---

## Compliance samples

Sample configuration files for **UK GDPR**, **EU GDPR**, **Benelux**, **PIPEDA**, **POPIA**, **APPI**, **PCI-DSS**, and optional regional frameworks are in [compliance-samples/](compliance-samples/). Each file is self-contained (regex overrides, ML terms, recommendation overrides) so you can enable one framework by pointing your config at that file and merging its overrides.

### List of samples and links

| Regulation / region           | Sample file                                                                                                 | Purpose                                                                                        |
| -------------------           | -----------                                                                                                 | -------                                                                                        |
| **LGPD (Brazil)**             | [compliance-sample-lgpd.yaml](compliance-samples/compliance-sample-lgpd.yaml)                               | Bilingual PT-BR + EN terms; RG/CEP regex; Brazilian deployments.                               |
| **UK GDPR**                   | [compliance-sample-uk_gdpr.yaml](compliance-samples/compliance-sample-uk_gdpr.yaml)                         | UK post-Brexit, ICO-aligned; norm_tag and recommendation overrides.                            |
| **EU GDPR (EEA)**             | [compliance-sample-eu_gdpr.yaml](compliance-samples/compliance-sample-eu_gdpr.yaml)                         | EU 2016/679 Art. 4(1), EDPB, member-state DPAs; optional EN + DE/FR terms.                     |
| **Benelux (BE, NL, LU)**      | [compliance-sample-benelux.yaml](compliance-samples/compliance-sample-benelux.yaml)                         | EU GDPR base + national IDs (BSN, NISS, LU); national DPA overrides; EN + NL/FR.               |
| **PIPEDA (Canada)**           | [compliance-sample-pipeda.yaml](compliance-samples/compliance-sample-pipeda.yaml)                           | Personal information, consent; Canadian identifiers (e.g. SIN); EN + FR.                       |
| **POPIA (South Africa)**      | [compliance-sample-popia.yaml](compliance-samples/compliance-sample-popia.yaml)                             | Responsible party, personal information; SA identifiers.                                       |
| **APPI (Japan)**              | [compliance-sample-appi.yaml](compliance-samples/compliance-sample-appi.yaml)                               | Personal information, retained personal data; PPC alignment.                                   |
| **PCI-DSS**                   | [compliance-sample-pci_dss.yaml](compliance-samples/compliance-sample-pci_dss.yaml)                         | Payment card patterns and recommendation overrides for merchants/assessors.                    |
| **Philippines (DPA)**         | [compliance-sample-philippines_dpa.yaml](compliance-samples/compliance-sample-philippines_dpa.yaml)         | RA 10173, NPC; personal/sensitive personal information.                                        |
| **Australia (Privacy Act)**   | [compliance-sample-australia_privacy.yaml](compliance-samples/compliance-sample-australia_privacy.yaml)     | Privacy Act 1988, OAIC, APPs; optional TFN regex.                                              |
| **Singapore (PDPA)**          | [compliance-sample-singapore_pdpa.yaml](compliance-samples/compliance-sample-singapore_pdpa.yaml)           | PDPA 2012, PDPC; personal data, DNC; NRIC regex.                                               |
| **UAE (PDPL)**                | [compliance-sample-uae_pdpl.yaml](compliance-samples/compliance-sample-uae_pdpl.yaml)                       | Decree-Law 45/2021; personal/sensitive data; EN + optional AR.                                 |
| **Argentina (PDPA)**          | [compliance-sample-argentina_pdpa.yaml](compliance-samples/compliance-sample-argentina_pdpa.yaml)           | Ley 25.326, DNPDP; datos personales; ES + EN; CUIT/CUIL/DNI regex.                             |
| **Kenya (DPA)**               | [compliance-sample-kenya_dpa.yaml](compliance-samples/compliance-sample-kenya_dpa.yaml)                     | Data Protection Act 2019, ODPC; personal data, data controller.                                |
| **India (DPDP)**              | [compliance-sample-india_dpdp.yaml](compliance-samples/compliance-sample-india_dpdp.yaml)                   | DPDP Act 2023, DPBI; Aadhaar/PAN regex; EN.                                                    |
| **Turkey (KVKK)**             | [compliance-sample-turkey_kvkk.yaml](compliance-samples/compliance-sample-turkey_kvkk.yaml)                 | Law 6698, KVKK Board; kişisel veri; EN + TR; TC Kimlik regex.                                  |
| **New Zealand (Privacy Act)** | [compliance-sample-new_zealand_privacy.yaml](compliance-samples/compliance-sample-new_zealand_privacy.yaml) | Privacy Act 2020, OPC; personal information, IPPs.                                             |
| **Saudi (PDPL)**              | [compliance-sample-saudi_pdpl.yaml](compliance-samples/compliance-sample-saudi_pdpl.yaml)                   | Royal Decree M/19, SDAIA; personal/sensitive data.                                             |
| **Israel (PPL)**              | [compliance-sample-israel_ppl.yaml](compliance-samples/compliance-sample-israel_ppl.yaml)                   | Privacy Protection Law, PPA; personal information, database registrar.                         |
| **Colombia (Law 1581)**       | [compliance-sample-colombia_1581.yaml](compliance-samples/compliance-sample-colombia_1581.yaml)             | Ley 1581/2012, SIC; datos personales; ES + EN; CC/NIT regex.                                   |
| **Chile (Privacy)**           | [compliance-sample-chile_privacy.yaml](compliance-samples/compliance-sample-chile_privacy.yaml)             | Law 19.628; datos personales; ES + EN; RUT regex.                                              |
| **Nigeria (NDPR)**            | [compliance-sample-nigeria_ndpr.yaml](compliance-samples/compliance-sample-nigeria_ndpr.yaml)               | NDPR 2019, NITDA; personal data, data controller.                                              |
| **Morocco (Law 09-08)**       | [compliance-sample-morocco_09_08.yaml](compliance-samples/compliance-sample-morocco_09_08.yaml)             | Law 09-08, CNDP; données à caractère personnel; FR + EN; CIN regex.                            |
| **Switzerland (FADP)**        | [compliance-sample-switzerland_fadp.yaml](compliance-samples/compliance-sample-switzerland_fadp.yaml)       | Revised FADP, FDPIC; personal data; EN + optional DE/FR/IT; AHV/UID regex.                     |
| **U.S. (FTC COPPA)**          | [compliance-sample-us_ftc_coppa.yaml](compliance-samples/compliance-sample-us_ftc_coppa.yaml)               | Federal children's online privacy **technical mapping**; not age verification or legal advice. |
| **U.S. (CA AB 2273)**         | [compliance-sample-us_ca_ab2273_caadca.yaml](compliance-samples/compliance-sample-us_ca_ab2273_caadca.yaml) | California Age-Appropriate Design Code **labelling**; applicability varies—counsel required.   |
| **U.S. (CO CPA — minors)**    | [compliance-sample-us_co_cpa_minors.yaml](compliance-samples/compliance-sample-us_co_cpa_minors.yaml)       | Colorado Privacy Act / under-18 contexts **technical mapping**; not “known minor” detection.   |

### What goes in which file

Each sample can provide up to three kinds of content. Your **main config** references or merges them as follows:

| Config key / file                                             | Purpose                                                                                         | What the sample provides                                                                                                                                                 |
| -----------------                                             | -------                                                                                         | -------------------------                                                                                                                                                |
| **`regex_overrides_file`**                                    | Custom regex patterns; match → finding with HIGH and given `norm_tag`.                          | A list of `{ name, pattern, norm_tag }` (e.g. UK NIN, Canadian SIN, SA ID). Samples may use key `regex` or `patterns`.                                                   |
| **`ml_patterns_file`** / **`sensitivity_detection.ml_terms`** | ML (and DL) training terms; column names and sample text classified as sensitive/non_sensitive. | A list of `{ text, label }` with framework-specific terms (e.g. “data subject”, “personal information”, “responsible party”). Samples may use key `terms` or `ml_terms`. |
| **`report.recommendation_overrides`**                         | Override “Base legal”, “Risco”, “Recomendação”, “Prioridade”, “Relevante para” per `norm_tag`.  | A list of `{ norm_tag_pattern, base_legal, risk, recommendation, priority, relevant_for }` to merge into your config.                                                    |

The same YAML file can contain **regex**, **terms**, and **recommendation_overrides**; you set `regex_overrides_file` and `ml_patterns_file` to that file path, and copy the `recommendation_overrides` block into your main config under `report.recommendation_overrides`.

### How to use a sample

1. **Choose the sample** for your regulation from the table above (or from [compliance-samples/README.md](compliance-samples/README.md)).
1. **Set paths in your main config** (e.g. `config.yaml`):

   ```yaml
   regex_overrides_file: docs/compliance-samples/compliance-sample-pipeda.yaml
   ml_patterns_file: docs/compliance-samples/compliance-sample-pipeda.yaml
   ```

   Use the same file for both if the sample contains both `regex` and `terms`.

1. **Merge recommendation overrides:** Copy the `recommendation_overrides` list from the sample file into your config under `report.recommendation_overrides` (merge with any overrides you already have). See [USAGE.md](USAGE.md) (report section) for the structure.
1. **Run the scan** (CLI or API). Findings will use the norm tags and recommendation text from the sample; the Excel report will show the framework-specific Base legal, Risco, Recomendação, and Prioridade.

---

## Multi-language, multi-encoding, and multi-regional operation {#multi-language-multi-encoding-and-multi-regional-operation}

Whatever the **language**, **encoding**, or **region** of your data soup, the application is built to handle it: you can run compliance scans and reports in the language and encoding of your region without breaking in production.

### What is supported

- **Multiple languages in terms and reports:** Compliance samples can include terms in the language(s) of the target region (e.g. EN+FR for PIPEDA/Canada, PT-BR+EN for LGPD/Brazil, Japanese or Arabic for APAC/MENA). The Excel report and recommendation text support **Unicode** (e.g. base_legal and recommendation in Japanese, Arabic, or accented characters).
- **Multiple encodings for config and pattern files:** The **main config file** is read with **auto-detection** (UTF-8, UTF-8 with BOM, Windows ANSI/cp1252, Latin-1), so it loads even when saved in a legacy encoding. **Pattern files** (regex overrides, ML/DL terms) use the encoding set by **`pattern_files_encoding`** in your config (default **`utf-8`**). Set it to `cp1252` or `latin_1` only when your pattern or sample files are saved in that encoding.
- **Multiple regions:** Use the compliance sample that matches your region or regulation (LGPD, UK GDPR, EU GDPR, Benelux, PIPEDA, POPIA, APPI, PCI-DSS, or optional regional samples). Each sample is a single YAML file; you point your config at it and merge its recommendation overrides.

### How to enable and operate

1. **Choose the right sample for your region**

   See the [compliance-samples README](compliance-samples/README.md) table and the “Language and target audience” section. For example: Brazil → LGPD (PT-BR+EN); Canada → PIPEDA (EN+FR); UK → UK GDPR; EEA → EU GDPR; Benelux → Benelux sample; Japan → APPI; South Africa → POPIA.

1. **Save config and sample files in UTF-8 (recommended)**

   Saving everything in **UTF-8** avoids encoding issues with multilingual terms. The main config file will still load if it is in another encoding (auto-detection).

1. **Set paths and encoding in your config**

   In your main `config.yaml` (or `config.json`):

   ```yaml
   # Optional: only if your pattern/sample files are NOT in UTF-8 (e.g. legacy cp1252)
   pattern_files_encoding: utf-8

   regex_overrides_file: docs/compliance-samples/compliance-sample-pipeda.yaml
   ml_patterns_file: docs/compliance-samples/compliance-sample-pipeda.yaml
   ```

   Then merge the sample’s **`recommendation_overrides`** into your config under `report.recommendation_overrides` (see [USAGE](USAGE.md) report section).

1. **Run the scan**

   Use the CLI or API as usual. Findings will use the norm tags and recommendation text from the sample; the Excel report will show Unicode correctly.

For full encoding options and examples, see [USAGE – File encoding](USAGE.md#file-encoding-config-and-pattern-files) (EN) and [USAGE.pt_BR – Encoding de arquivos](USAGE.pt_BR.md#file-encoding-config-and-pattern-files) (pt-BR).

---

**Assistance with tuning:** If your organization needs **further or better compatibility** with a specific regulation or compliance scope (e.g. VCDPA, CPA, sector-specific rules), we can assist—by **creating tailored configuration files** or making **slight code-side adjustments**—when you reach out. This helps potential customers adopt the tool for their jurisdiction or auditor expectations without starting from scratch.

---

## Auditable and management standards (supporting role)

The application does **not** certify organisations. It provides **discovery and mapping** of personal and sensitive data and **metadata-only** reporting, which supports evidence-based accountability and audit preparation.

- **ISO/IEC 27701 (PIMS):** ISO/IEC 27701 requires PII controllers and processors to know where PII is and to document the scope of processing. Our scans and reports (findings, norm tags, Excel output) help you produce that evidence and align with the regulations you declare under ISO/IEC 27701 (e.g. LGPD, GDPR, CCPA). See [PLAN_COMPLIANCE_STANDARDS_ALIGNMENT.md](plans/PLAN_COMPLIANCE_STANDARDS_ALIGNMENT.md).
- **SOC 2:** A common pressure point for corporates; SOC 2 (Type I/II) expects documented controls over the security, availability, and confidentiality of systems that process sensitive data. We do not perform SOC 2 audits. Our **discovery and mapping** of where personal or sensitive data resides, plus metadata-only reporting, supports control design and audit preparation (e.g. evidence of data inventory and scope). Norm tags and recommendation overrides can be aligned to the trust principles and criteria you use. See [PLAN_COMPLIANCE_STANDARDS_ALIGNMENT.md](plans/PLAN_COMPLIANCE_STANDARDS_ALIGNMENT.md).
- **FELCA (Lei 15.211/2025 – Estatuto Digital da Criança e do Adolescente):** In force from 17 March 2026, FELCA applies to digital platforms directed at or accessible by minors in Brazil. We do not implement age verification or platform controls. Our **minor data detection** (e.g. date-of-birth and age-related columns, “possible minor” flags) and reports help you map where data relating to minors is processed and support transparency and accountability (e.g. toward ANPD). See [PLAN_COMPLIANCE_STANDARDS_ALIGNMENT.md](plans/PLAN_COMPLIANCE_STANDARDS_ALIGNMENT.md).

**Other compliance to watch:** Regional child-protection or platform laws (beyond FELCA), sector-specific rules (e.g. health, finance), and new data-localisation or cross-border requirements may affect your scope. We extend support via config and [compliance-samples](compliance-samples/) as norms become relevant; no code change is required to add new norm tags or recommendation text.

**U.S. child and minor privacy (technical only):** Optional samples ([FTC COPPA framing](compliance-samples/compliance-sample-us_ftc_coppa.yaml), [California AB 2273](compliance-samples/compliance-sample-us_ca_ab2273_caadca.yaml), [Colorado CPA minors context](compliance-samples/compliance-sample-us_co_cpa_minors.yaml)) add **norm tags and report wording** for audit prep, DPO review, and operational scoping. They do **not** provide legal advice, verify parental consent, or prove compliance. For plan scope and disclaimers: [PLAN_US_CHILD_PRIVACY_TECHNICAL_ALIGNMENT.md](plans/PLAN_US_CHILD_PRIVACY_TECHNICAL_ALIGNMENT.md).

Other auditable or regional norms can be addressed via our config-driven norm tags and [compliance-samples](compliance-samples/); we continue to extend documentation and samples as new standards become relevant.

---

## Explicitly referenced today (built-in labels)

The built-in regex patterns and report labels refer to these frameworks (with example `norm_tag` values):

| Framework | Scope                                   | Example norm_tag (in reports) |
| ---       | ---                                     | ---                           |
| **LGPD**  | Brazil – Lei Geral de Proteção de Dados | `LGPD Art. 5`                 |
| **GDPR**  | EU – General Data Protection Regulation | `GDPR Art. 4(1)`              |
| **CCPA**  | California – Consumer Privacy Act       | `CCPA`                        |
| **HIPAA** | US – Health data                        | Health/insurance context      |
| **GLBA**  | US – Financial services                 | `PCI/GLBA` (e.g. credit card) |

Findings are stored with a free-form **`norm_tag`** and **`pattern_detected`**; the Excel report uses them in the **Recommendations** sheet (Base legal, Risco, Recomendação, Prioridade, Relevante para).

---

## Extensibility

- **`norm_tag`** and **`pattern_detected`** are open: you can set them to any framework or internal label.
- **Regex overrides:** Use [regex_overrides_file](SENSITIVITY_DETECTION.md#custom-regex-patterns-detecting-new-personalsensitive-values) to add patterns and set `norm_tag` to e.g. `"UK GDPR"`, `"PIPEDA s. 2"`, `"APPI"`, `"POPIA"` so they appear in reports and recommendations.
- **Recommendation overrides (config):** Use `report.recommendation_overrides` in config to tailor "Base legal", "Relevante para", and other recommendation text per `norm_tag` pattern—so UK GDPR, PIPEDA, APPI, POPIA, or custom norms get the right labels and text without changing code. See [USAGE.md](USAGE.md) (report section) for an example.
- **Custom connectors:** New data sources can emit findings with any `norm_tag`; reporting and recommendations will use config overrides when provided, otherwise the built-in fallbacks.

No change to detector logic or thresholds is required; extensibility is via config and optional override files.

**Documentation index** (all topics, both languages): [README.md](README.md) · [README.pt_BR.md](README.pt_BR.md). For configuration schema and report options, see [USAGE.md](USAGE.md) ([pt-BR](USAGE.pt_BR.md)) and [TECH_GUIDE.md](TECH_GUIDE.md) ([pt-BR](TECH_GUIDE.pt_BR.md)).
