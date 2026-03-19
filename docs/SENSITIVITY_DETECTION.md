# Sensitivity detection: ML and DL training terms

The application uses a **hybrid** pipeline to classify column names and sampled content as sensitive or not:

1. **Regex** – Built-in patterns (CPF, CNPJ, email, phone, SSN, credit card, dates) plus optional overrides from a config file.
1. **ML** – TF-IDF + RandomForest trained on a list of **(text, label)** terms (sensitive vs non-sensitive). Terms come from a file or from inline config. The forest uses a **fixed `random_state`** so confidence scores are reproducible across runs and detector instances.
1. **DL (optional)** – Sentence embeddings + a small classifier trained on your terms. Used when the optional dependency `sentence-transformers` is installed and you provide DL terms (file or inline). Confidence is combined with ML (e.g. `max(ml_confidence, dl_confidence)`).

You can **set the training words for both ML and DL** in the main config file (inline) or in separate YAML/JSON files.

**Português (Brasil):** [SENSITIVITY_DETECTION.pt_BR.md](SENSITIVITY_DETECTION.pt_BR.md)

**Minor data detection:** The application can flag possible data of minors (DOB/age columns) and apply differential treatment in reports (LGPD Art. 14, GDPR Art. 8). The age threshold (default 18) is configurable in the external config file. See [MINOR_DETECTION.md](MINOR_DETECTION.md) for configuration and fine-tuning.

**Aggregated / cross-referenced identification risk:** When multiple quasi-identifier categories (e.g. gender, job position, health, address, phone) appear in the **same table or file**, the report generator flags this as a **special case** for DPO and compliance (LGPD Art. 5, GDPR Recital 26 – identifiability from a combination of data). The Excel report includes a sheet **"Cross-ref data – ident. risk"** listing each case (target, table/file, columns involved, categories, explanation) and a high-priority recommendation. This is optional and configurable via `detection.aggregated_identification_enabled`, `aggregated_min_categories`, and `quasi_identifier_mapping`. See [PLAN_AGGREGATED_IDENTIFICATION.md](plans/completed/PLAN_AGGREGATED_IDENTIFICATION.md) for design and config details.

---

## CNPJ formats (Brazil): legacy numeric and alphanumeric

Brazilian **CNPJ** (Cadastro Nacional da Pessoa Jurídica) is the company tax identifier. Two formats are relevant:

**Legacy (numeric only):**

- 14 digits, optionally formatted as `XX.XXX.XXX/XXXX-XX` (dots, slash, hyphen). Still valid; no mandatory migration.

**Alphanumeric (current official format):**

- Defined by **Instrução Normativa RFB nº 2.229/2024** (Receita Federal). Same 14-character length; display punctuation unchanged (`XX.XXX.XXX/XXXX-XX`).
- **Positions 1–8 (root):** alphanumeric `0–9`, `A–Z` (uppercase).
- **Positions 9–12 (registration order):** alphanumeric `0–9`, `A–Z`.
- **Positions 13–14 (verification digits):** numeric only `0–9`.
- New company registrations will receive alphanumeric CNPJs from **July 2026** onward; existing numeric CNPJs remain valid.

The project supports both formats. Alphanumeric detection is **opt-in** so existing behaviour is unchanged:

- `LGPD_CNPJ` – legacy numeric format only (always active).
- `LGPD_CNPJ_ALNUM` – alphanumeric format per IN RFB 2.229/2024 (first 12 positions `[0-9A-Z]`, last two digits). Active when either:
  - `detection.cnpj_alphanumeric: true` is set in config, or
  - an override for `LGPD_CNPJ_ALNUM` is added via `regex_overrides_file`.

Both patterns share the same `norm_tag` (`LGPD Art. 5`). The detector performs **format compatibility only** (regex match); **checksum validation** (e.g. Module 11 for alphanumeric) is left to a future detector phase. If your sector uses a variant (e.g. lowercase letters), adjust the regex in your override accordingly.

---

## Content type & cloaking detection (future)

The project has a **plan** for optional **content-based type detection** to help with **renamed files** and **simple cloaking** (e.g. PDF saved as `.txt`). As of version 1.6.0:

- **Step 1 (helper) is implemented:** a small internal helper `infer_content_type(path_or_bytes)` uses **magic bytes and simple heuristics** to infer a coarse file type label (for example: `pdf`, `zip`, `text`) from the first bytes of a file or bytes buffer.
- **No wiring to connectors yet:** filesystem and share connectors still decide what to scan based on **extensions** and existing rules; the helper is not called in production flows.
- **Future phase (opt-in):** a later phase will add an **opt-in toggle** (config/CLI/dashboard) so connectors can consult this helper before deciding how to extract and scan content, improving resistance to renamed/cloaked files at the cost of a small extra read per file.

For design details and rollout steps, see [PLAN_CONTENT_TYPE_AND_CLOAKING_DETECTION.md](plans/PLAN_CONTENT_TYPE_AND_CLOAKING_DETECTION.md).

## Config keys

| Key                              | Description                                                                                                                         |                                                                              |
| ---                              | ---                                                                                                                                 |                                                                              |
| `ml_patterns_file`               | Path to a YAML/JSON file with ML training terms (list of `{ text, label }`). Used when `sensitivity_detection.ml_terms` is not set. |                                                                              |
| `dl_patterns_file`               | Path to a YAML/JSON file with DL training terms (same format). Used when `sensitivity_detection.dl_terms` is not set.               |                                                                              |
| `sensitivity_detection`          | Optional section with inline terms (no separate file needed).                                                                       |                                                                              |
| `sensitivity_detection.ml_terms` | List of `{ text: string, label: "sensitive" \                                                                                       | "non_sensitive" }`. Overrides/supplements `ml_patterns_file` when non-empty. |
| `sensitivity_detection.dl_terms` | List of `{ text: string, label: "sensitive" \                                                                                       | "non_sensitive" }`. Overrides/supplements `dl_patterns_file` when non-empty. |
| `sensitivity_detection.medium_confidence_threshold` | Integer **1–69**, default **40**. Minimum combined ML/DL confidence (0–100) for **MEDIUM** when no strong regex match. **HIGH** remains at 70. Lower values surface more borderline columns for review (FN-first). |
| `sensitivity_detection.column_name_normalize_for_ml` | Boolean, default **false**. When **true**, **accent-folds** and **normalizes separators** on the column name **only for ML/DL input** (regex and minor heuristics still use the raw name). Reduces false negatives on names like `téléphone` vs training term `telefone`. |
| `sensitivity_detection.fuzzy_column_match` | Boolean, default **false**. When **true** and **`rapidfuzz`** is installed (`pip install .[detection-fuzzy]` or `uv sync --group dev`), compares the column name to **sensitive** ML/DL training terms. If there is **no regex match**, combined ML/DL confidence is in the configured band **strictly below** the MEDIUM threshold, and similarity ≥ `fuzzy_column_match_min_ratio`, returns **MEDIUM** with `pattern_detected` **`FUZZY_COLUMN_MATCH`**. **Off by default** — no change without the flag + library. |
| `sensitivity_detection.fuzzy_column_match_min_confidence` | Integer **0–100**, default **25**. Lower bound of the confidence band for fuzzy elevation (inclusive). |
| `sensitivity_detection.fuzzy_column_match_max_confidence` | Integer **0–100**, default **45**. Upper bound is `min(this, medium_confidence_threshold - 1)` so normal MEDIUM from ML/DL is unchanged. |
| `sensitivity_detection.fuzzy_column_match_min_ratio` | Integer **50–100**, default **85**. Minimum `rapidfuzz` score (max of ratio / partial_ratio / token_set_ratio) vs a sensitive term. |
| `sensitivity_detection.connector_format_id_hint` | Boolean, default **false**. When **true**, connectors pass declared SQL types (e.g. `VARCHAR(11)`) into the detector. If there is **no regex match**, combined ML/DL confidence is **below** the MEDIUM threshold, and the declared `CHAR`/`VARCHAR` length matches common ID sizes **with** an ID-like column name (e.g. `*_id` suffix, or `cpf` / `cnpj` / `ssn` in the name), classification becomes **MEDIUM** with `pattern_detected` **`FORMAT_LENGTH_HINT_ID`**. **Off by default.** See `tests/test_format_length_hint.py`, Plan §4 in `PLAN_ADDITIONAL_DETECTION_TECHNIQUES_AND_FN_REDUCTION.md`. |
| `detection.persist_low_id_like_for_review` | Boolean, default **false**. When **true**, **database-style connectors** (SQL, Snowflake, MongoDB, Redis, Dataverse, Power BI, REST/JSON field keys) may persist **LOW** columns whose names look like identifiers (`*_id`, `*_uuid`, `*_number`, etc.; see `core.suggested_review`) with pattern `SUGGESTED_REVIEW_ID_LIKE` for the Excel sheet **Suggested review (LOW)**. |
| `report.include_suggested_review_sheet` | Boolean, default **true**. When **true**, findings with `SUGGESTED_REVIEW_ID_LIKE` are listed on **Suggested review (LOW)** and **removed from** Database/Filesystem sheets to avoid duplication. Set **false** to keep them only on the main findings tabs. |

**Label values:** `sensitive` or `1` = sensitive (PII/personal data); `non_sensitive` or `0` = not sensitive.

### Suggested review (LOW) and MEDIUM threshold (FN reduction)

To catch more **possible** personal data without raising sensitivity, you can:

1. Lower `sensitivity_detection.medium_confidence_threshold` (e.g. **35**) so borderline ML/DL scores map to **MEDIUM** instead of **LOW**.
2. Set `detection.persist_low_id_like_for_review: true` on database targets so identifier-like column names that remain **LOW** are still stored and listed on **Suggested review (LOW)** in the Excel report for manual confirmation.

Details: [PLAN_ADDITIONAL_DETECTION_TECHNIQUES_AND_FN_REDUCTION.md](plans/PLAN_ADDITIONAL_DETECTION_TECHNIQUES_AND_FN_REDUCTION.md).

#### Why suggested-review rows need `persist_low_id_like_for_review: true` (or fixtures)

By default connectors **do not save** findings with sensitivity **LOW** (to keep the DB and reports smaller). **Suggested review** is still **LOW**; it only adds a distinct `pattern_detected` so the report can list those columns on **Suggested review (LOW)**. Therefore nothing appears on that sheet unless either:

- you set **`detection.persist_low_id_like_for_review: true`** so ID-like LOW columns are written with `SUGGESTED_REVIEW_ID_LIKE`, or
- tests / manual inserts add such rows (fixtures).

#### MEDIUM threshold **vs** persist flag (design fit for compliance scanning)

| Knob | Effect | Trade-off |
|------|--------|-----------|
| Lower **`medium_confidence_threshold`** (e.g. 35) | More borderline ML/DL scores become **MEDIUM** immediately; they are stored like any other non-LOW finding. | **More MEDIUM rows** everywhere (Database findings, recommendations). Good when you want **broad human review** without an extra flag. |
| **`persist_low_id_like_for_review: true`** | Only **LOW** columns whose **names** look like identifiers get a second chance to appear (still LOW) on **Suggested review (LOW)**. | **Targeted** extra rows; does not widen the MEDIUM band. Good when you mainly worry about **missed IDs** without flooding MEDIUM. |

**Recommendation (aligned with “bias to false positives / human verification”):** For **high-regret** environments, use a **slightly lower MEDIUM threshold** (e.g. 35–38) **and/or** enable **persist LOW ID-like** for scans where coverage matters. Start with one change, compare noise in reports, then add the second. Defaults stay conservative so existing deployments are unchanged.

---

## File format (YAML or JSON)

Both `ml_patterns_file` and `dl_patterns_file` use the same structure. You can point both to the same file if you want ML and DL to use the same terms.

## YAML example

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

## JSON example

```json
[
  { "text": "cpf", "label": "sensitive" },
  { "text": "email", "label": "sensitive" },
  { "text": "item_count", "label": "non_sensitive" }
]
```

---

## Aggregated identification: configuration and examples

When **aggregated identification** is enabled, the report generator groups findings by table (database) or file (filesystem) and flags cases where **multiple quasi-identifier categories** (e.g. gender, job position, health, address, phone) appear together, which can support re-identification (LGPD Art. 5, GDPR Recital 26). The Excel report gets a sheet **"Cross-ref data – ident. risk"** and a high-priority recommendation.

| Key                                           | Type    | Default  | Description                                                                                                                                                                                                                                                                               |
| ---                                           | ---     | ---      | ---                                                                                                                                                                                                                                                                                       |
| `detection.aggregated_identification_enabled` | boolean | **true** | Set to `false` to disable aggregation and the Cross-ref sheet.                                                                                                                                                                                                                            |
| `detection.aggregated_min_categories`         | integer | **2**    | Minimum number of distinct quasi-identifier categories in a table/file to flag (e.g. 3 for stricter).                                                                                                                                                                                     |
| `detection.quasi_identifier_mapping`          | list    | **[]**   | Optional list of `{ column_pattern, category }` or `{ pattern_detected, category }` to map columns/patterns to `gender`, `job_position`, `health`, `address`, `phone`, `other`. Built-in defaults map common names (e.g. gender, sex, cargo, department, health, address), **phone** (phone, telefone, celular, home phone, téléphone, handynummer, etc.), **name/identifier** to `other` (first name, surname, nome, apellido, vorname, etc.), and **ID/document** to `other` (cpf, rg, passaporte, passport, ctps, documento oficial, pis, cartão cidadão, certidão, green card, cnh, driver license, identity document, id card, national id, document number, carte d'identité, etc.). |

## Example: enable with custom mapping and minimum 3 categories

```yaml
# config.yaml
targets: []
report:
  output_dir: ./reports
detection:
  aggregated_identification_enabled: true
  aggregated_min_categories: 3
  quasi_identifier_mapping:

    - { column_pattern: "cargo", category: job_position }
    - { column_pattern: "departamento", category: job_position }
    - { pattern_detected: "PHONE_BR", category: phone }
    - { pattern_detected: "EMAIL", category: other }

```

**How to operate:** Run a scan (CLI: `python main.py --config config.yaml` or API: start scan from the dashboard). Then generate the report (CLI: report is produced when the scan finishes; API: download from the session). If any table or file has at least `aggregated_min_categories` categories present, the report will include the **"Cross-ref data – ident. risk"** sheet and an **AGGREGATED_IDENTIFICATION** recommendation row.

**To disable:** Set `detection.aggregated_identification_enabled: false` in your config; the Cross-ref sheet and aggregated recommendation will not be generated.

---

## Inline terms in main config

You can define ML and DL training terms directly in your main `config.yaml` (or JSON) under `sensitivity_detection`, without separate files.

## Example: inline ML and DL terms

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

- **Plan and table of categories:** [PLAN_SENSITIVE_CATEGORIES_ML_DL.md](plans/completed/PLAN_SENSITIVE_CATEGORIES_ML_DL.md)
- **Ready-to-use example file:** [sensitivity_terms_sensitive_categories.example.yaml](sensitivity_terms_sensitive_categories.example.yaml)

Copy that file (or merge its entries) into your `ml_patterns_file` / `dl_patterns_file`, or into `sensitivity_detection.ml_terms` / `sensitivity_detection.dl_terms`. You can use `report.recommendation_overrides` so findings in these categories get the right Base legal, Risk, and Priority in the report. A full example (health, religion, political, PEP, race, union, genetic, biometric, sex life) is in [USAGE.md](USAGE.md) (Global options); [USAGE.pt_BR.md](USAGE.pt_BR.md) (Português).

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

| Field      | Required | Description                                                                                                                                                                                                                                                                                                                      |
| ---        | ---      | ---                                                                                                                                                                                                                                                                                                                              |
| `name`     | Yes      | Short identifier for the pattern (e.g. `RG_BR`, `PLATE_BR`). Appears in reports as `pattern_detected`.                                                                                                                                                                                                                           |
| `pattern`  | Yes      | Regular expression (Python `re` syntax). Matched against column name + sample text. Use raw strings; prefer `\b` for word boundaries to avoid partial matches.                                                                                                                                                                   |
| `norm_tag` | No       | Label for compliance/reporting (e.g. `LGPD Art. 5`, `Custom`). Default: `"Custom"`. You can set this to any framework label (e.g. `"UK GDPR"`, `"PIPEDA s. 2"`, `"APPI"`, `"POPIA"`) so findings appear under that norm in reports and recommendations; see [Compliance frameworks and extensibility](COMPLIANCE_FRAMEWORKS.md). |

You can use a root-level list or a key `patterns` or `regex` containing the list. You can copy from [regex_overrides.example.yaml](regex_overrides.example.yaml) and edit. Use **double-quoted** YAML for `pattern` values with **escaped backslashes** (e.g. `"\\b\\d{5}"`) so linters and loaders do not report invalid escape sequences; see `.cursor/rules/yaml-regex-patterns.mdc`. For **file encoding** (UTF-8, cp1252, etc.), see [USAGE.md](USAGE.md#file-encoding-config-and-pattern-files).

## YAML example (regex overrides)

```yaml
# config/regex_overrides.yaml
- name: "RG_BR"

  pattern: "\\b\\d{1,2}\\.?\\d{3}\\.?\\d{3}-?[0-9Xx]\\b"
  norm_tag: "LGPD Art. 5"

- name: "PLATE_BR"

  pattern: "\\b[A-Z]{3}-?\\d{4}\\b"
  norm_tag: "Personal data context"

- name: "HEALTH_PLAN_ID"

  pattern: "\\b\\d{6,14}\\b"
  norm_tag: "Health/insurance context"

# Example: alphanumeric CNPJ pattern (same structure as built-in LGPD_CNPJ_ALNUM).

- name: "LGPD_CNPJ_ALNUM"

  pattern: "\\b[A-Z0-9]{2}\\.?[A-Z0-9]{3}\\.?[A-Z0-9]{3}/?[A-Z0-9]{4}-?\\d{2}\\b"
  norm_tag: "LGPD Art. 5"
```

## JSON example (regex overrides)

```json
[
  { "name": "RG_BR", "pattern": "\\b\\d{1,2}\\.?\\d{3}\\.?\\d{3}-?[0-9Xx]\\b", "norm_tag": "LGPD Art. 5" },
  { "name": "PLATE_BR", "pattern": "\\b[A-Z]{3}-?\\d{4}\\b", "norm_tag": "Personal data context" }
]
```

### Built-in patterns (reference)

The application already includes these patterns; you do not need to redefine them unless you want to change the regex or norm tag.

| Name          | Description                                     | Norm tag              |
| ---           | ---                                             | ---                   |
| `LGPD_CPF`    | Brazilian CPF (11 digits, optional dots/dash)   | LGPD Art. 5           |
| `LGPD_CNPJ`   | Brazilian CNPJ (14 digits, optional formatting) | LGPD Art. 5           |
| `EMAIL`       | Email address                                   | GDPR Art. 4(1)        |
| `CREDIT_CARD` | 16-digit card (optional spaces/dashes)          | PCI/GLBA              |
| `PHONE_BR`    | Brazilian phone (optional +55, area code)       | LGPD Art. 5           |
| `CCPA_SSN`    | US SSN (XXX-XX-XXXX)                            | CCPA                  |
| `DATE_DMY`    | Date d/m/y (e.g. 31/12/2024)                    | Personal data context |

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

## Document summary

- **ML terms:** From `sensitivity_detection.ml_terms` (inline) or `ml_patterns_file`. Used by the TF-IDF + RandomForest classifier.
- **DL terms:** From `sensitivity_detection.dl_terms` (inline) or `dl_patterns_file`. Used by the optional sentence-embedding + classifier when `.[dl]` is installed.
- **Same format:** Both use a list of `{ text, label }` with `label` = `sensitive` or `non_sensitive` (or `1` / `0`).
- **Inline overrides file:** When `ml_terms` or `dl_terms` are non-empty in config, they are used instead of loading from the corresponding file.
- **Regex patterns:** Use `regex_overrides_file` in the main config to add or override patterns for value-based detection (see [Custom regex patterns](#custom-regex-patterns-detecting-new-personalsensitive-values) above).

### Generic/ambiguous identifiers (PII_AMBIGUOUS)

Column names such as **doc_id**, **document_id**, **id_number**, **doc_number**, **doc_ref**, **document_ref**, or **identifier** are ambiguous: they may hold PII (e.g. identity document number) or only an internal reference. The detector flags them as **sensitive** via ML terms but returns **MEDIUM** sensitivity and **pattern_detected** `PII_AMBIGUOUS` with norm_tag *"Generic identifier – confirm manually"*. The report recommendation then asks the **operator to confirm manually** whether the column contains personal data. Merge a recommendation override with `norm_tag_pattern: "PII_AMBIGUOUS"` (see EU GDPR or LGPD compliance samples) to get the "confirm manually" text in the report.

### Regional document nicknames and ID variations

Default ML terms and compliance samples include **regional naming** so column names in local language are recognised:

- **France:** *carte bleue*, *carte rose*, *carte vitale*, *titre de séjour*, *carte de séjour*, *numéro de sécurité sociale*, *carte d'identité*, *passeport*.
- **Germany:** *Personalausweis*, *Reisepass*, *Aufenthaltserlaubnis*, *Sozialversicherungsnummer*.
- **Spain:** *pasaporte*, *documento de identidad*, *libro de familia*, *carnet de conducir*, *NIE*.
- **Brazil (PT-BR):** *passaporte*, *CTPS*, *carteira de trabalho*, *certidão (nascimento/casamento/óbito)*, *título eleitoral*, *PIS*, *cartão cidadão*, *OAB*, *CRM*, *CRC*, *CREA*, *CRQ*, *registro profissional*, and the ID terms already listed.

Add or override terms in `ml_patterns_file` or `sensitivity_detection.ml_terms` for other locales.

**Documentation index** (all topics, both languages): [README.md](README.md) · [README.pt_BR.md](README.pt_BR.md).
