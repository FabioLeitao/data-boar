# Sensitivity detection: ML and DL training terms

The application uses a **hybrid** pipeline to classify column names and sampled content as sensitive or not:

1. **Regex** – Built-in patterns (CPF, CNPJ, email, phone, SSN, credit card, dates) plus optional overrides from a config file.
2. **ML** – TF-IDF + RandomForest trained on a list of **(text, label)** terms (sensitive vs non-sensitive). Terms come from a file or from inline config.
3. **DL (optional)** – Sentence embeddings + a small classifier trained on your terms. Used when the optional dependency `sentence-transformers` is installed and you provide DL terms (file or inline). Confidence is combined with ML (e.g. `max(ml_confidence, dl_confidence)`).

You can **set the training words for both ML and DL** in the main config file (inline) or in separate YAML/JSON files.

**Português (Brasil):** [sensitivity-detection.pt_BR.md](sensitivity-detection.pt_BR.md)

**Minor data detection:** The application can flag possible data of minors (DOB/age columns) and apply differential treatment in reports (LGPD Art. 14, GDPR Art. 8). The age threshold (default 18) is configurable in the external config file. See [minor-detection.md](minor-detection.md) for configuration and fine-tuning.

**Aggregated / cross-referenced identification risk:** When multiple quasi-identifier categories (e.g. gender, job position, health, address, phone) appear in the **same table or file**, the report generator flags this as a **special case** for DPO and compliance (LGPD Art. 5, GDPR Recital 26 – identifiability from a combination of data). The Excel report includes a sheet **"Cross-ref data – ident. risk"** listing each case (target, table/file, columns involved, categories, explanation) and a high-priority recommendation. This is optional and configurable via `detection.aggregated_identification_enabled`, `aggregated_min_categories`, and `quasi_identifier_mapping`. See [PLAN_AGGREGATED_IDENTIFICATION.md](PLAN_AGGREGATED_IDENTIFICATION.md) for design and config details.

---

## Config keys

| Key | Description |
|-----|-------------|
| `ml_patterns_file` | Path to a YAML/JSON file with ML training terms (list of `{ text, label }`). Used when `sensitivity_detection.ml_terms` is not set. |
| `dl_patterns_file` | Path to a YAML/JSON file with DL training terms (same format). Used when `sensitivity_detection.dl_terms` is not set. |
| `sensitivity_detection` | Optional section with inline terms (no separate file needed). |
| `sensitivity_detection.ml_terms` | List of `{ text: string, label: "sensitive" \| "non_sensitive" }`. Overrides/supplements `ml_patterns_file` when non-empty. |
| `sensitivity_detection.dl_terms` | List of `{ text: string, label: "sensitive" \| "non_sensitive" }`. Overrides/supplements `dl_patterns_file` when non-empty. |

**Label values:** `sensitive` or `1` = sensitive (PII/personal data); `non_sensitive` or `0` = not sensitive.

---

## File format (YAML or JSON)

Both `ml_patterns_file` and `dl_patterns_file` use the same structure. You can point both to the same file if you want ML and DL to use the same terms.

**YAML example:**

```yaml
# List of terms; each has "text" and "label"
- text: "cpf"
  label: sensitive
- text: "email"
  label: sensitive
- text: "data de nascimento"
  label: sensitive
- text: "senha"
  label: sensitive
- text: "item_count"
  label: non_sensitive
- text: "config_file"
  label: non_sensitive
```

**Alternative key:** some configs use `patterns` or `terms` as the root key:

```yaml
patterns:
  - text: "cpf"
    label: sensitive
  - text: "email"
    label: sensitive
  - text: "system_log"
    label: non_sensitive
```

**JSON example:**

```json
[
  { "text": "cpf", "label": "sensitive" },
  { "text": "email", "label": "sensitive" },
  { "text": "item_count", "label": "non_sensitive" }
]
```

---

## Inline terms in main config

You can define ML and DL training terms directly in your main `config.yaml` (or JSON) under `sensitivity_detection`, without separate files.

**Example: inline ML and DL terms**

```yaml
# config.yaml
targets: []
file_scan:
  extensions: [.txt, .csv, .pdf]
  recursive: true
report:
  output_dir: .

# Training terms for sensitivity (ML = TF-IDF + RandomForest; DL = sentence embeddings + classifier when .[dl] installed)
sensitivity_detection:
  ml_terms:
    - { text: "cpf", label: sensitive }
    - { text: "email", label: sensitive }
    - { text: "senha", label: sensitive }
    - { text: "data de nascimento", label: sensitive }
    - { text: "item_count", label: non_sensitive }
    - { text: "system_log", label: non_sensitive }
  dl_terms:
    - { text: "customer name", label: sensitive }
    - { text: "health record", label: sensitive }
    - { text: "salary", label: sensitive }
    - { text: "internal id", label: non_sensitive }
    - { text: "cache key", label: non_sensitive }
```

If you set **only** `ml_terms` (or only `dl_terms`), the other still uses its file or built-in defaults: ML falls back to `ml_patterns_file` or built-in terms when `ml_terms` is empty; DL is used only when `dl_terms` or `dl_patterns_file` is provided and the optional `sentence-transformers` package is installed.

---

## Using only files (no inline)

```yaml
# config.yaml
ml_patterns_file: config/ml_terms.yaml
dl_patterns_file: config/dl_terms.yaml
# ... rest of config
```

Or use the same file for both:

```yaml
ml_patterns_file: config/sensitivity_terms.yaml
dl_patterns_file: config/sensitivity_terms.yaml
```

---

## Enabling the DL backend

The DL step uses **sentence embeddings** (e.g. `sentence-transformers/all-MiniLM-L6-v2`) and trains a small classifier on your DL terms at startup. Install the optional dependency:

```bash
uv pip install -e ".[dl]"
# or
pip install -e ".[dl]"
```

This installs `sentence-transformers` (and its dependencies). If `.[dl]` is not installed, the pipeline still runs with **regex + ML**; the DL step is skipped and confidence comes only from ML.

---

## Example: shared terms file

Create e.g. `config/sensitivity_terms.yaml` (or copy from [sensitivity_terms.example.yaml](sensitivity_terms.example.yaml)):

```yaml
- text: "cpf"
  label: sensitive
- text: "cnpj"
  label: sensitive
- text: "email"
  label: sensitive
- text: "telefone"
  label: sensitive
- text: "data de nascimento"
  label: sensitive
- text: "nome completo"
  label: sensitive
- text: "senha"
  label: sensitive
- text: "salário"
  label: sensitive
- text: "health record"
  label: sensitive
- text: "item_count"
  label: non_sensitive
- text: "config_file"
  label: non_sensitive
- text: "temp_data"
  label: non_sensitive
- text: "lyrics"
  label: non_sensitive
- text: "tablature"
  label: non_sensitive
```

Reference in config:

```yaml
ml_patterns_file: config/sensitivity_terms.yaml
dl_patterns_file: config/sensitivity_terms.yaml
```

---

## Sensitive categories (health, religion, political, etc.)

To detect **additional sensitive personal data** (LGPD Art. 5 II, 11; GDPR Art. 9)—such as CID/ICD (diagnosis codes), gender, religion, political affiliation, PEP, race/skin color, union affiliation, genetic/biometric data, sex life, health/disability—add training terms for those categories to your ML/DL term list.

- **Plan and table of categories:** [PLAN_SENSITIVE_CATEGORIES_ML_DL.md](PLAN_SENSITIVE_CATEGORIES_ML_DL.md)
- **Ready-to-use example file:** [sensitivity_terms_sensitive_categories.example.yaml](sensitivity_terms_sensitive_categories.example.yaml)

Copy that file (or merge its entries) into your `ml_patterns_file` / `dl_patterns_file`, or into `sensitivity_detection.ml_terms` / `sensitivity_detection.dl_terms`. You can use `report.recommendation_overrides` so findings in these categories get the right Base legal, Risk, and Priority in the report (see the plan for examples).

---

## Custom regex patterns (detecting new personal/sensitive values)

The detector matches **regex patterns** against the combined text (column name + sample content). Built-in patterns cover CPF, CNPJ, email, phone, SSN, credit card, and dates. To make the application pay attention to **new possibly personal or sensitive values** (e.g. RG, license plate, health plan number, other country IDs), you add **custom patterns** via a file and point the config to it.

### Where to configure

In your main config file (`config.yaml` or JSON), set the key **`regex_overrides_file`** to the path of a YAML or JSON file that lists your patterns. The path can be absolute or relative to the process working directory. The application loads this file at startup and **merges** your patterns with the built-in ones (your names override built-in ones if they match).

```yaml
# config.yaml
regex_overrides_file: config/regex_overrides.yaml
# ... rest of config (targets, file_scan, report, etc.)
```

If `regex_overrides_file` is omitted or the file is missing, only the built-in patterns are used.

### File format

The file must contain a **list of objects**, each with:

| Field | Required | Description |
|-------|----------|-------------|
| `name` | Yes | Short identifier for the pattern (e.g. `RG_BR`, `PLATE_BR`). Appears in reports as `pattern_detected`. |
| `pattern` | Yes | Regular expression (Python `re` syntax). Matched against column name + sample text. Use raw strings; prefer `\b` for word boundaries to avoid partial matches. |
| `norm_tag` | No | Label for compliance/reporting (e.g. `LGPD Art. 5`, `Custom`). Default: `"Custom"`. You can set this to any framework label (e.g. `"UK GDPR"`, `"PIPEDA s. 2"`, `"APPI"`, `"POPIA"`) so findings appear under that norm in reports and recommendations; see [Compliance frameworks and extensibility](compliance-frameworks.md). |

You can use a root-level list or a key `patterns` or `regex` containing the list. You can copy from [regex_overrides.example.yaml](regex_overrides.example.yaml) and edit.

**YAML example:**

```yaml
# config/regex_overrides.yaml
- name: "RG_BR"
  pattern: "\b\d{1,2}\.?\d{3}\.?\d{3}-?[0-9Xx]\b"
  norm_tag: "LGPD Art. 5"

- name: "PLATE_BR"
  pattern: "\b[A-Z]{3}-?\d{4}\b"
  norm_tag: "Personal data context"

- name: "HEALTH_PLAN_ID"
  pattern: "\b\d{6,14}\b"
  norm_tag: "Health/insurance context"
```

**JSON example:**

```json
[
  { "name": "RG_BR", "pattern": "\\b\\d{1,2}\\.?\\d{3}\\.?\\d{3}-?[0-9Xx]\\b", "norm_tag": "LGPD Art. 5" },
  { "name": "PLATE_BR", "pattern": "\\b[A-Z]{3}-?\\d{4}\\b", "norm_tag": "Personal data context" }
]
```

### Built-in patterns (reference)

The application already includes these patterns; you do not need to redefine them unless you want to change the regex or norm tag.

| Name | Description | Norm tag |
|------|-------------|----------|
| `LGPD_CPF` | Brazilian CPF (11 digits, optional dots/dash) | LGPD Art. 5 |
| `LGPD_CNPJ` | Brazilian CNPJ (14 digits, optional formatting) | LGPD Art. 5 |
| `EMAIL` | Email address | GDPR Art. 4(1) |
| `CREDIT_CARD` | 16-digit card (optional spaces/dashes) | PCI/GLBA |
| `PHONE_BR` | Brazilian phone (optional +55, area code) | LGPD Art. 5 |
| `CCPA_SSN` | US SSN (XXX-XX-XXXX) | CCPA |
| `DATE_DMY` | Date d/m/y (e.g. 31/12/2024) | Personal data context |

### Examples of useful additional patterns

- **RG (Brazil):** format varies by state; a common form is digits with optional dots and a trailing digit or X:  
  `\b\d{1,2}\.?\d{3}\.?\d{3}-?[0-9Xx]\b`
- **Brazilian vehicle plate (old):** `AAA-9999`:  
  `\b[A-Z]{3}-?\d{4}\b`
- **Brazilian vehicle plate (Mercosul):** `AAA9A99`:  
  `\b[A-Z]{3}\d[A-Z]\d{2}\b`
- **Generic numeric ID (e.g. health plan):** be careful with length to avoid too many false positives; e.g. 8–14 digits:  
  `\b\d{8,14}\b` (use only if context is appropriate; consider combining with ML/DL).
- **US phone:** `(XXX) XXX-XXXX` or `XXX-XXX-XXXX`:  
  `\b\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b`
- **Postal code (Brazil):** `99999-999`:  
  `\b\d{5}-?\d{3}\b`

When a custom pattern matches the column name or sample text, the finding is reported with **HIGH** sensitivity (or MEDIUM in lyrics/tabs context for weak patterns), with `pattern_detected` set to your `name` and `norm_tag` in the report.

### Summary

- **Configure:** Set `regex_overrides_file` in the main config to the path of your YAML/JSON file.
- **Format:** List of `{ name, pattern, norm_tag }`; `norm_tag` optional (default `"Custom"`).
- **Effect:** Your patterns are merged with built-in ones; any match in (column name + sample) is flagged. Use precise patterns and word boundaries to reduce false positives.
- **ML/DL:** For context (e.g. “this column name suggests PII”), use [ML/DL training terms](#config-keys) in addition to regex.

---

## Summary

- **ML terms:** From `sensitivity_detection.ml_terms` (inline) or `ml_patterns_file`. Used by the TF-IDF + RandomForest classifier.
- **DL terms:** From `sensitivity_detection.dl_terms` (inline) or `dl_patterns_file`. Used by the optional sentence-embedding + classifier when `.[dl]` is installed.
- **Same format:** Both use a list of `{ text, label }` with `label` = `sensitive` or `non_sensitive` (or `1` / `0`).
- **Inline overrides file:** When `ml_terms` or `dl_terms` are non-empty in config, they are used instead of loading from the corresponding file.
- **Regex patterns:** Use `regex_overrides_file` in the main config to add or override patterns for value-based detection (see [Custom regex patterns](#custom-regex-patterns-detecting-new-personalsensitive-values) above).
