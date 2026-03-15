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

Additional **compliance sample configs** (one profile per regulation: UK GDPR, PIPEDA, POPIA, APPI, PCI-DSS) are planned and will be documented in the same way. Until then, you can combine the examples above to achieve compatibility with those or other frameworks.

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
