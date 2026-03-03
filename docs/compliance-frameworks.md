# Compliance frameworks and extensibility

The application helps DPO, security, and compliance teams discover and map personal or sensitive data in line with multiple regulations. This document describes which frameworks are explicitly referenced today and how to extend support to others (e.g. UK GDPR, PIPEDA, APPI, POPIA) without code changes.

**Português (Brasil):** [compliance-frameworks.pt_BR.md](compliance-frameworks.pt_BR.md)

---

## Explicitly referenced today

The built-in regex patterns and report labels refer to these frameworks (with example `norm_tag` values):

| Framework | Scope | Example norm_tag (in reports) |
|-----------|--------|------------------------------|
| **LGPD** | Brazil – Lei Geral de Proteção de Dados | `LGPD Art. 5` |
| **GDPR** | EU – General Data Protection Regulation | `GDPR Art. 4(1)` |
| **CCPA** | California – Consumer Privacy Act | `CCPA` |
| **HIPAA** | US – Health data | Health/insurance context |
| **GLBA** | US – Financial services | `PCI/GLBA` (e.g. credit card) |

Findings are stored with a free-form **`norm_tag`** and **`pattern_detected`**; the Excel report uses them in the **Recommendations** sheet (Base legal, Risco, Recomendação, Prioridade, Relevante para).

---

## Extensibility

- **`norm_tag`** and **`pattern_detected`** are open: you can set them to any framework or internal label.
- **Regex overrides:** Use [regex_overrides_file](sensitivity-detection.md#custom-regex-patterns-detecting-new-personalsensitive-values) to add patterns and set `norm_tag` to e.g. `"UK GDPR"`, `"PIPEDA s. 2"`, `"APPI"`, `"POPIA"` so they appear in reports and recommendations.
- **Recommendation overrides (config):** Use `report.recommendation_overrides` in config to tailor "Base legal", "Relevante para", and other recommendation text per `norm_tag` pattern—so UK GDPR, PIPEDA, APPI, POPIA, or custom norms get the right labels and text without changing code. See [USAGE.md](USAGE.md) (report section) for an example.
- **Custom connectors:** New data sources can emit findings with any `norm_tag`; reporting and recommendations will use config overrides when provided, otherwise the built-in fallbacks.

No change to detector logic or thresholds is required; extensibility is via config and optional override files.
