# Minor data detection: configuration and fine-tuning

The application can detect when gathered data may relate to **minors** (e.g. age or date of birth in columns) and treat it as **highest sensitivity**, with differential treatment in reports (LGPD Art. 14, GDPR Art. 8). This page describes how to **configure and fine-tune** the feature via the **external config file**, without changing application code.

**Português (Brasil):** [minor-detection.pt_BR.md](minor-detection.pt_BR.md)

---

## What is detected

- **Column names** that suggest date of birth or age, in **English and Brazilian Portuguese**, including acronyms (e.g. DOB, DDN, NASC, idade, age).
- **Sample values**: numeric ages (e.g. `17`) or dates that, when interpreted as date of birth, imply an age below the configurable **threshold** (default **18**). Those findings are flagged as **possible minor data** (`DOB_POSSIBLE_MINOR`) and get a dedicated high-priority recommendation in the report.

See [PLAN_MINOR_DATA_DETECTION.md](PLAN_MINOR_DATA_DETECTION.md) for the full design and list of column names/formats.

---

## Config file: where and what

The **minor/adult age threshold** is set in your **main config file** (e.g. `config.yaml` or the file pointed to by `CONFIG_PATH`). No code changes are required.

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| `detection.minor_age_threshold` | integer | **18** | Age below this value (inclusive) is treated as possible minor. Use e.g. 21 if your policy treats people under 21 as minors. |
| `detection.minor_full_scan` | boolean | false | Reserved for future use (full-scan of column when minor suggested). |
| `detection.minor_cross_reference` | boolean | true | Reserved for future use (cross-reference with name/doc/health in same row). |

If the **`detection`** section is **omitted**, the threshold defaults to **18** and the application behaves as before (no errors). Adding the section allows you to adjust the threshold without breaking existing runs.

---

## How to adjust and fine-tune

### 1. Use the default (18)

Do nothing: omit the `detection` section. Anyone under 18 (by age or inferred from DOB) is flagged as possible minor.

### 2. Raise the threshold (e.g. under-21 policy)

If your organisation treats people under 21 as minors, set the threshold to 21 in your config file:

```yaml
# config.yaml
targets: []
report:
  output_dir: .
sqlite_path: audit_results.db

detection:
  minor_age_threshold: 21
```

Then run the audit as usual. Columns that look like age/DOB with values indicating age under 21 will be flagged as possible minor.

### 3. Lower the threshold (e.g. only young children)

To flag only very young ages (e.g. under 14), set:

```yaml
detection:
  minor_age_threshold: 14
```

### 4. Full example with other options

```yaml
targets:
  - name: my-db
    type: database
    host: localhost
    database: app_db
file_scan:
  extensions: [.csv, .xlsx, .txt]
  recursive: true
report:
  output_dir: ./reports
  min_sensitivity: LOW

detection:
  minor_age_threshold: 18
  minor_full_scan: false
  minor_cross_reference: true

sqlite_path: audit_results.db
scan:
  max_workers: 1
```

---

## Column names and formats recognised

The detector looks for **DOB- or age-like** column names (and sample content). Recognised names include:

| Concept | English | Brazilian Portuguese | Acronyms |
|--------|---------|----------------------|----------|
| Date of birth | date of birth, birth date, birthdate | data de nascimento, nascimento, data de nasc. | DOB, DDN, DN, NASC, DTN |
| Age | age, person age | idade, idade_atual, idade_pessoa, faixa etária | AGE, IDD |

**Date formats** in sample text: `dd/mm/yyyy`, `yyyy-mm-dd`, `mm/dd/yyyy` (and common variants). **Numeric age**: integers in the sample (e.g. 0–120) when the column name suggests age.

If a column name does **not** suggest DOB or age, a value like `17` or a date in the sample will **not** by itself trigger possible-minor (avoids false positives on generic numeric/date columns).

---

## Report and recommendations

Findings flagged as possible minor get:

- **Sensitivity:** HIGH  
- **Pattern:** `DOB_POSSIBLE_MINOR` (possibly combined with other patterns)  
- **Norm tag:** LGPD Art. 14 – possible minor data; GDPR Art. 8  

In the Excel report, the **Recommendations** sheet includes a dedicated row for possible minor data with **highest priority** (CRÍTICA) and differential treatment text (consent, storage, use, sharing, parental responsibility). That row is listed **first** in the Recommendations sheet. See [PLAN_MINOR_DATA_DETECTION.md](PLAN_MINOR_DATA_DETECTION.md) and the report generator for the exact wording.

---

## Related documentation

- [PLAN_MINOR_DATA_DETECTION.md](PLAN_MINOR_DATA_DETECTION.md) – Plan, design, and to-do status.  
- [sensitivity-detection.md](sensitivity-detection.md) – ML/DL and regex sensitivity detection.  
- [USAGE.md](USAGE.md) – General configuration and API usage.
