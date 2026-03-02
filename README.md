# python3-lgpd-crawler

Application for auditing personal and sensitive data across databases and filesystems, aligned with **LGPD**, **GDPR**, **CCPA**, **HIPAA**, and **GLBA**. It discovers and maps possible PII/sensitive data via regex and ML, stores metadata in a local SQLite database, and produces Excel reports with heatmaps and recommendations.

## Features

- **Multi-target scanning**: Configure multiple databases and filesystem paths in a single YAML/JSON config.
- **SQL databases**: PostgreSQL, MySQL, MariaDB, SQLite, Microsoft SQL Server, Oracle (via SQLAlchemy drivers).
- **NoSQL (optional)**: MongoDB, Redis — install optional deps: ` uv pip install-e ".[nosql]"`.
- **Filesystem**: Recursive scan of local (or mounted) directories; permission check before reading. Supports many extensions: text (`.txt`, `.csv`, `.json`, `.xml`, `.html`, `.md`, `.yml`, `.log`, `.ini`, `.sql`, `.rtf`, etc.), documents (`.pdf`, `.doc`, `.docx`, `.odt`, `.ods`, `.odp`, `.xls`, `.xlsx`, `.xlsm`, `.ppt`, `.pptx`), email (`.eml`, `.msg`), and data (`.sqlite`, `.db`). Set `file_scan.extensions` in config to a list of suffixes, or use `"*"` / `"all"` to scan all supported types.
- **Sensitivity detection**: Regex patterns (configurable) + ML classifier (TF-IDF + RandomForest) on column names and sampled content; no raw data is stored.
- **Single SQLite**: All findings and failures per session (UUID + timestamp); separate tables for database findings, filesystem findings, and scan failures.
- **Reporting**: Excel with sheets "Database findings", "Filesystem findings", "Scan failures", "Recommendations", and sensitivity/risk heatmap (PNG).
- **CLI and REST API**: Run one-shot audit from command line or start API (default port 8088) for `/scan`, `/status`, `/report`, `/list`, `/reports/{session_id}`.

## Requirements

- Python 3.12+
- Ubuntu 24.04 LTS / Debian 13 (or recent Linux/macOS/Windows)  
- [uv](https://github.com/astral-sh/uv) (recommended) or pip

## Install

```bash
# With uv (recommended)
uv sync

# Or with pip
pip install -e .
```

Optional NoSQL support (MongoDB, Redis):

```bash
uv pip install -e ".[nosql]"
# or: pip install -e ".[nosql]"
```

## Configuration

Use a single config file in **YAML** or **JSON**. Example `config.yaml`:

```yaml
targets:
  - name: "Produção_Postgres"
    type: database
    driver: postgresql+psycopg2
    host: 10.0.0.50
    port: 5432
    user: audit_user
    pass: secure_password
    database: customers_db

  - name: "Documentos_LGPD"
    type: filesystem
    path: /home/user/Documents/LGPD
    recursive: true

file_scan:
  extensions: [.txt, .csv, .pdf, .docx, .xlsx]
  recursive: true

report:
  output_dir: .

api:
  port: 8088

sqlite_path: audit_results.db
scan:
  max_workers: 1   # 1 = sequential; >1 = parallel

# Optional: external pattern files (no code change)
ml_patterns_file: ml_patterns.yaml
regex_overrides_file: regex_overrides.yaml
```

Legacy `config/config.json` with `databases` and `file_scan.directories` is normalized automatically.

### ML patterns file (optional)

YAML/JSON list of `text` + `label` (sensitive / non_sensitive) to train or extend the classifier:

```yaml
- text: "cpf"
  label: sensitive
- text: "system_log"
  label: non_sensitive
```

### Regex overrides (optional)

YAML/JSON list of `name`, `pattern`, optional `norm_tag`:

```yaml
- name: LGPD_CPF
  pattern: "\b\d{3}\.?\d{3}\.?\d{3}-?\d{2}\b"
  norm_tag: "LGPD Art. 5"
```

## Run

**CLI (one-shot audit):**

```bash
python main.py --config config.yaml
# Report written to report output_dir, e.g. Relatorio_Auditoria_<session_id>.xlsx
```

**REST API (default port 8088):**

```bash
python main.py --config config.yaml --web --port 8088
# Or: uvicorn api.routes:app --host 0.0.0.0 --port 8088
```

API routes:

- `POST /scan` or `POST /start` — start audit in background; returns `session_id`
- `GET /status` — `running`, `current_session_id`, `findings_count`
- `GET /report` — download last generated Excel report
- `GET /list` or `GET /reports` — list past sessions (session_id, timestamp, counts)
- `GET /reports/{session_id}` — regenerate and download report for that session

## Supported databases and drivers

| Engine    | Driver (config)           | Note                    |
|-----------|---------------------------|-------------------------|
| PostgreSQL| `postgresql+psycopg2`     | psycopg2-binary         |
| MySQL     | `mysql+pymysql`           | pymysql                 |
| MariaDB   | `mysql+pymysql`           | same as MySQL           |
| SQLite    | `sqlite`                  | database = path         |
| SQL Server| `mssql+pyodbc`            | pyodbc                  |
| Oracle (19+ RAC) | `oracle+oracledb` | oracledb (thin mode; no Oracle Client). Config `database` = service name (e.g. customers_db or ORCL). |
| MongoDB   | `mongodb`                 | optional: pymongo       |
| Redis     | `redis`                   | optional: redis         |

For MongoDB/Redis, add a target with `type: database` and `driver: mongodb` or `redis` (host, port, database/password as needed). Install optional deps: `uv pip install -e ".[nosql]"`.

## Logging and alerts

- Log file: `audit_YYYYMMDD.log` (and console).
- On each finding (possible personal/sensitive data), the app logs and prints an `[ALERT]` to the console so the operator is notified on the fly.

## Security and compliance

- No raw sampled content is persisted; only metadata (location, pattern, sensitivity, norm tag).
- Use recent, CVE-patched versions of the interpreter and dependencies (`uv sync` / `pip install -e .`).
- Keep credentials in config files or environment; avoid committing secrets.

## License

See [LICENSE](LICENSE).
