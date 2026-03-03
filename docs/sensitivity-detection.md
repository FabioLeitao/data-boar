# Sensitivity detection: ML and DL training terms

The application uses a **hybrid** pipeline to classify column names and sampled content as sensitive or not:

1. **Regex** – Built-in patterns (CPF, CNPJ, email, phone, SSN, credit card, dates) plus optional overrides from a config file.
2. **ML** – TF-IDF + RandomForest trained on a list of **(text, label)** terms (sensitive vs non-sensitive). Terms come from a file or from inline config.
3. **DL (optional)** – Sentence embeddings + a small classifier trained on your terms. Used when the optional dependency `sentence-transformers` is installed and you provide DL terms (file or inline). Confidence is combined with ML (e.g. `max(ml_confidence, dl_confidence)`).

You can **set the training words for both ML and DL** in the main config file (inline) or in separate YAML/JSON files.

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

## Summary

- **ML terms:** From `sensitivity_detection.ml_terms` (inline) or `ml_patterns_file`. Used by the TF-IDF + RandomForest classifier.
- **DL terms:** From `sensitivity_detection.dl_terms` (inline) or `dl_patterns_file`. Used by the optional sentence-embedding + classifier when `.[dl]` is installed.
- **Same format:** Both use a list of `{ text, label }` with `label` = `sensitive` or `non_sensitive` (or `1` / `0`).
- **Inline overrides file:** When `ml_terms` or `dl_terms` are non-empty in config, they are used instead of loading from the corresponding file.

For regex overrides (custom patterns for value matching), see `regex_overrides_file` in the main configuration and [USAGE.md](USAGE.md).
