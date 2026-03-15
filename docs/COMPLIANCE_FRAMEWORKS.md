# Compliance frameworks and extensibility

The application helps DPO, security, and compliance teams discover and map personal or sensitive data in line with multiple regulations. This document describes which frameworks are explicitly referenced today, where to find sample configuration, and how to extend support to others (e.g. UK GDPR, PIPEDA, APPI, POPIA) without code changes.

**Português (Brasil):** [COMPLIANCE_FRAMEWORKS.pt_BR.md](COMPLIANCE_FRAMEWORKS.pt_BR.md)

---

## Regulations we support today (built-in and config examples)

**Built-in (out of the box):** The detector and reports explicitly reference **LGPD** (Brazil), **GDPR** (EU), **CCPA** (California), **HIPAA** (US health), and **GLBA** (US financial). Findings use these norm tags and recommendation text by default.

**Sample configuration and examples:** We provide config-file examples so you can align with more regulations without changing code:

- **[regex_overrides.example.yaml](regex_overrides.example.yaml)** – custom regex patterns with `norm_tag` (e.g. LGPD Art. 5, CCPA). Copy and extend for other identifiers (e.g. UK NIN, Canadian SIN) and set `norm_tag` to your framework.
- **Recommendation overrides** – in [USAGE.md](USAGE.md) (report section) you will find `report.recommendation_overrides`: list of `norm_tag_pattern`, `base_legal`, `risk`, `recommendation`, `priority`, `relevant_for`. Use this to tailor report text for any regulation (UK GDPR, PIPEDA, POPIA, APPI, PCI-DSS, or internal norms).
- **ML/DL terms** – [SENSITIVITY_DETECTION.md](SENSITIVITY_DETECTION.md) and the main config support `ml_patterns_file`, `dl_patterns_file`, or inline `sensitivity_detection.ml_terms` / `dl_terms` so you can add framework-specific terms (e.g. “personal information”, “data subject”, “responsible party”) for better detection and labelling.

**Compliance samples (one profile per regulation):** Sample configs for **LGPD** (Brazil), **UK GDPR**, **PIPEDA**, **POPIA**, **APPI**, and **PCI-DSS** are in [compliance-samples/](compliance-samples/). Each sample is a single YAML file with regex patterns, ML terms, and recommendation overrides for that framework. Use them as follows:

1. **Regex and ML terms:** Set `regex_overrides_file` and `ml_patterns_file` in your main config to the sample file path (the same file can be used for both; samples use keys `regex` and `terms`).
1. **Recommendation overrides:** Copy the `recommendation_overrides` list from the sample into your config under `report.recommendation_overrides` (merge with any existing overrides).

**Available samples:** [compliance-sample-lgpd.yaml](compliance-samples/compliance-sample-lgpd.yaml) – LGPD (Brazil); **bilingual PT-BR + EN** terms (e.g. "documento oficial" / "official document", "CNH" / "Driver License") for Brazilian deployments. [compliance-sample-uk_gdpr.yaml](compliance-samples/compliance-sample-uk_gdpr.yaml) – UK GDPR (UK post-Brexit, ICO-aligned). More samples (EU GDPR, Benelux, PIPEDA, POPIA, APPI, PCI-DSS, and optional regional ones) will be added in the same format. For **language and target audience** (e.g. PIPEDA → EN + FR for Canada), see the [compliance-samples README](compliance-samples/README.md).

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

2. **Save config and sample files in UTF-8 (recommended)**
   Saving everything in **UTF-8** avoids encoding issues with multilingual terms. The main config file will still load if it is in another encoding (auto-detection).

3. **Set paths and encoding in your config**
   In your main `config.yaml` (or `config.json`):

   ```yaml
   # Optional: only if your pattern/sample files are NOT in UTF-8 (e.g. legacy cp1252)
   pattern_files_encoding: utf-8

   regex_overrides_file: docs/compliance-samples/compliance-sample-pipeda.yaml
   ml_patterns_file: docs/compliance-samples/compliance-sample-pipeda.yaml
   ```

   Then merge the sample’s **`recommendation_overrides`** into your config under `report.recommendation_overrides` (see [USAGE](USAGE.md) report section).

4. **Run the scan**
   Use the CLI or API as usual. Findings will use the norm tags and recommendation text from the sample; the Excel report will show Unicode correctly.

For full encoding options and examples, see [USAGE – File encoding](USAGE.md#file-encoding-config-and-pattern-files) (EN) and [USAGE.pt_BR – Encoding de arquivos](USAGE.pt_BR.md#file-encoding-config-and-pattern-files) (pt-BR).

---

**Assistance with tuning:** If your organization needs **further or better compatibility** with a specific regulation or compliance scope (e.g. VCDPA, CPA, sector-specific rules), we can assist—by **creating tailored configuration files** or making **slight code-side adjustments**—when you reach out. This helps potential customers adopt the tool for their jurisdiction or auditor expectations without starting from scratch.

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
