# python3-lgpd-crawler

Application for auditing personal and sensitive data across databases and filesystems, aligned with **LGPD**, **GDPR**, **CCPA**, **HIPAA**, and **GLBA**. It discovers and maps possible PII/sensitive data via regex and ML, stores metadata in a local SQLite database, and produces Excel reports with heatmaps and recommendations.

## Features

- **Multi-target scanning**: Configure multiple databases, filesystems, APIs, remote shares, **Power BI**, and **Power Apps (Dataverse)** in a single YAML/JSON config.
- **SQL databases**: PostgreSQL, MySQL, MariaDB, SQLite, Microsoft SQL Server, Oracle (via SQLAlchemy drivers).
- **Power BI (optional)**: Discover workspaces, datasets, and tables via Power BI REST API; sample with DAX. Azure AD OAuth2 (client credentials). Findings in **Database findings** sheet.
- **Power Apps / Dataverse (optional)**: Discover entities and attributes via Dataverse Web API; sample rows. Azure AD OAuth2 (client credentials). Findings in **Database findings** sheet.
- **Remote shares (optional)**: SharePoint, WebDAV, SMB/CIFS, NFS — by FQDN or IP with credentials in config; install `.[shares]`.
- **NoSQL (optional)**: MongoDB, Redis — install optional deps: `uv pip install -e ".[nosql]"`.
- **Filesystem**: Recursive scan of local (or mounted) directories; permission check before reading. Supports many extensions: text (`.txt`, `.csv`, `.json`, `.xml`, `.html`, `.md`, `.yml`, `.log`, `.ini`, `.sql`, `.rtf`, etc.), documents (`.pdf`, `.doc`, `.docx`, `.odt`, `.ods`, `.odp`, `.xls`, `.xlsx`, `.xlsm`, `.ppt`, `.pptx`), email (`.eml`, `.msg`), and data (`.sqlite`, `.db`). **SQLite files** (`.sqlite`, `.sqlite3`, `.db`) found on disk are opened and scanned as databases (discover tables/columns, sample and detect); set `file_scan.scan_sqlite_as_db: false` to skip. Set `file_scan.extensions` to a list of suffixes, or `"*"` / `"all"` for all supported types.
- **Sensitivity detection**: Regex patterns (configurable) + ML classifier (TF-IDF + RandomForest) on column names and sampled content; no raw data is stored. **Lyrics and music tablature** are detected via heuristics so that date-like or digit sequences in song lyrics and guitar tabs are downgraded to MEDIUM/LOW to reduce false positives; strong PII (CPF, email, etc.) still reports HIGH.
- **Single SQLite**: All findings and failures per session (UUID + timestamp); separate tables for database findings, filesystem findings, and scan failures.
- **Reporting**: Excel with sheets "Database findings", "Filesystem findings", "Scan failures", "Recommendations", "Praise / existing controls" (indications of encryption/hashing/tokenization), **"Trends - Session comparison"** (vs previous run: improvements or new/increased findings for DPO and security team), and sensitivity/risk heatmap (PNG).
- **CLI and REST API**: Run one-shot audit from command line or start API (default port 8088) for `/scan`, `/start`, `/scan_database`, `/status`, `/report`, `/list`, `/reports/{session_id}`.

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

Use a single config file in **YAML** or **JSON**. The API loads it from `CONFIG_PATH` or `config.yaml` in the working directory. For detailed **targets and credentials** (databases, filesystems, APIs with basic/bearer/OAuth2, and shared content), see **[docs/USAGE.md](docs/USAGE.md)**. Example `config.yaml`:

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
  scan_sqlite_as_db: true   # open .sqlite/.db files as DBs and scan tables/columns
  sample_limit: 5

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

### Learned patterns (optional)

At the end of each run (when a report is generated), the engine can write **learned patterns**: terms that were classified as sensitive in this scan, so you can merge them into `ml_patterns_file` for the next run. This improves future detection while limiting false positives (only HIGH sensitivity by default, minimum confidence, and exclusion of generic terms like `id`, `name`).

Enable in config:

```yaml
learned_patterns:
  enabled: true
  output_file: learned_patterns.yaml
  min_sensitivity: HIGH      # or MEDIUM to also capture borderline cases
  min_confidence: 70
  min_term_length: 3
  require_pattern: true      # only learn when a pattern was actually detected
  append: true               # merge with existing file
  exclude_if_in_ml_patterns: true   # skip terms already in ml_patterns_file
```

**Merge into ML patterns:** Copy or merge entries from `learned_patterns.yaml` into your `ml_patterns_file`. Each entry has `text` and `label: sensitive`; optional `pattern_detected` and `norm_tag` help you review. Use the same format as the ML patterns file (list of `text` + `label`). After merging, the next run will use the expanded set for the classifier.

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
# Report written to report.output_dir, e.g. Relatorio_Auditoria_<session_id>.xlsx
```

**REST API (default port 8088):**

```bash
python main.py --config config.yaml --web --port 8088
# Or: uvicorn api.routes:app --host 0.0.0.0 --port 8088
```

**Arguments:** `--config` (path to YAML/JSON, default `config.yaml`), `--web` (start API instead of one-shot), `--port` (default 8088). When using the API, the server loads config from the `CONFIG_PATH` environment variable or `config.yaml` in the working directory.

**API routes (summary):**

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/scan` or `/start` | Start full audit in background; returns `session_id` |
| `POST` | `/scan_database` | One-off scan of one database (JSON body); returns `session_id` |
| `GET` | `/status` | `running`, `current_session_id`, `findings_count` |
| `GET` | `/report` | Download **last generated** Excel report |
| `GET` | `/list` or `/reports` | List past sessions (to pick a report) |
| `GET` | `/reports/{session_id}` | Regenerate and download report for that session |

For **deployment**, **using the web API** (with request/response examples), **configuration and credentials** (databases, filesystems, APIs with basic/bearer/OAuth2/custom auth, and shared content), and **downloading current and previous reports**, see **[docs/USAGE.md](docs/USAGE.md)**.

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

## REST/API targets and authentication

You can scan remote HTTP(S) APIs for personal or sensitive data by adding targets with `type: api` or `type: rest`. The connector calls the configured endpoints (GET), parses JSON, and runs the same sensitivity detection on field names and sample values. **Authentication** is configurable so you can use static credentials, bearer tokens (e.g. negotiated or issued by an IdP), or OAuth2 client credentials.

**Required:** `name`, `base_url` (or `url`). **Optional:** `paths` or `endpoints` (list of path strings, e.g. `["/users", "/orders"]`), `discover_url` (GET returns a list of paths to scan), `timeout`, `headers`, and an `auth` block.

### Auth types

| Type | Use case | Config |
|------|----------|--------|
| **basic** | Static username and password | `auth: { type: basic, username: "...", password: "..." }` |
| **bearer** | Static or negotiated token (e.g. from Kerberos/AD, or API key) | `auth: { type: bearer, token: "..." }` or `token_from_env: "MY_TOKEN_VAR"` |
| **oauth2_client** | OAuth2 client credentials (machine-to-machine) | `auth: { type: oauth2_client, token_url: "https://...", client_id: "...", client_secret: "..." }` (or `client_secret: "${ENV_VAR}"` to read from environment) |
| **custom** | Custom headers (e.g. `Authorization: Negotiate ...`, API key header) | `auth: { type: custom, headers: { "Authorization": "Bearer ...", "X-API-Key": "..." } }` |

If you omit `auth` but set `user`/`username` and `pass`/`password` on the target, **basic** auth is used.

**Example config (YAML):**

```yaml
targets:
  - name: "Internal Users API"
    type: api
    base_url: "https://api.example.com"
    paths: ["/users", "/profiles"]
    auth:
      type: oauth2_client
      token_url: "https://auth.example.com/oauth/token"
      client_id: "audit-client"
      client_secret: "${API_OAUTH_SECRET}"
      scope: "read:users"
  - name: "Legacy API (basic)"
    type: rest
    base_url: "https://legacy.example.com"
    paths: ["/v1/contacts"]
    auth:
      type: basic
      username: "audit_user"
      password: "***"
  - name: "API with bearer token (e.g. negotiated)"
    type: api
    base_url: "https://api.example.com"
    paths: ["/data"]
    auth:
      type: bearer
      token_from_env: "NEGOTIATED_TOKEN"   # or use "token" for static value
  - name: "API with custom header"
    type: api
    base_url: "https://api.example.com"
    paths: ["/export"]
    auth:
      type: custom
      headers:
        Authorization: "Bearer ..."
        X-Requested-By: "lgpd-audit"
```

Findings from API targets appear in the **Filesystem findings** sheet with `file_name` like `GET /users | email` (endpoint and field). The project uses **httpx** (already a dependency) for HTTP; no extra install is required for the REST connector.

## Power BI and Power Apps (Dataverse)

You can scan **Power BI** (datasets and tables) and **Power Apps / Dataverse** (entities and columns) as data sources. Both use **Azure AD OAuth2 client credentials** (app registration with a client secret). No extra install is required (httpx is already a dependency).

### Power BI

- **Type:** `powerbi`
- **Auth:** Azure AD app with Power BI permissions (`Dataset.Read.All` or `Dataset.ReadWrite.All`). Enable “Allow service principals to use Power BI APIs” in the Power BI admin portal if using a service principal.
- **Config:** `tenant_id`, `client_id`, `client_secret` (or under `auth:`). Optional: `workspace_ids` or `group_ids` to limit to specific workspaces; omit to use “My workspace” and all workspaces the app can see.

The connector lists datasets and tables (push datasets expose table schema; for others it samples via DAX), runs sensitivity detection on column names and sample values, and writes **Database findings** (schema = dataset name, table = table name, column = column).

**Example config (YAML):**

```yaml
targets:
  - name: "Power BI Compliance"
    type: powerbi
    tenant_id: "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
    client_id: "yyyyyyyy-yyyy-yyyy-yyyy-yyyyyyyyyyyy"
    client_secret: "${POWERBI_CLIENT_SECRET}"   # or literal
    # optional: limit to specific workspaces
    # workspace_ids: ["group-guid-1", "group-guid-2"]
```

### Power Apps / Dataverse

- **Type:** `dataverse` or `powerapps`
- **Auth:** Azure AD app with application permission to Dataverse (e.g. “Common Data Service” / `user_impersonation` or env-specific application permission). Admin consent required.
- **Config:** `org_url` (or `environment_url`), e.g. `https://myorg.crm.dynamics.com`, plus `tenant_id`, `client_id`, `client_secret` (or under `auth:`).

The connector lists entities (tables), their attributes, samples rows, runs sensitivity detection, and writes **Database findings** (schema = entity logical name, table = entity set, column = attribute).

**Example config (YAML):**

```yaml
targets:
  - name: "Dataverse HR"
    type: dataverse
    org_url: "https://myorg.crm.dynamics.com"
    tenant_id: "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
    client_id: "yyyyyyyy-yyyy-yyyy-yyyy-yyyyyyyyyyyy"
    client_secret: "${DATAVERSE_CLIENT_SECRET}"
```

Use the same `file_scan.sample_limit` (default 5) to control how many rows are sampled per table/entity for Power BI and Dataverse.

## SharePoint, WebDAV, SMB/CIFS, and NFS shares

You can scan remote file shares by **FQDN or IP** with credentials in config. Install optional deps:  
`uv pip install -e ".[shares]"`  
(installs `smbprotocol`, `webdavclient3`, `requests_ntlm`).

| Type | Host / URL | Credentials | Notes |
|------|------------|-------------|--------|
| **sharepoint** | `site_url`: `https://host/sites/sitename` | `user`, `pass`; NTLM or basic | On-prem or URL; path = server-relative folder (e.g. `Shared Documents`) |
| **webdav** | `base_url`: `https://host/path` | `user`, `pass` | Recursive list and download |
| **smb** / **cifs** | `host`: FQDN or IP, `share`: share name, `path`: path inside share | `user`, `pass`, optional `domain` | Port 445 default |
| **nfs** | `path`: **local mount point** (NFS must be mounted first) | — | `host` / `export_path` for reporting only |

**Example config (YAML):**

```yaml
targets:
  # SMB/CIFS (Windows or Samba)
  - name: "FileServer HR"
    type: smb
    host: "fileserver.company.local"   # or 10.0.0.10
    share: "HR"
    path: "Documents"
    user: "audit_user"
    pass: "***"
    domain: "COMPANY"                 # optional
    port: 445
    recursive: true

  # WebDAV
  - name: "WebDAV Storage"
    type: webdav
    base_url: "https://webdav.company.com/dav"
    user: "audit"
    pass: "***"
    path: "archive"
    recursive: true
    verify_ssl: true

  # SharePoint (on-prem or URL; NTLM or basic)
  - name: "SharePoint HR"
    type: sharepoint
    site_url: "https://sharepoint.company.com/sites/hr"
    path: "Shared Documents"
    user: "audit@company.com"
    pass: "***"

  # NFS (path = local mount point; mount NFS first)
  - name: "NFS Export"
    type: nfs
    host: "nfs.company.local"
    export_path: "/export/data"
    path: "/mnt/nfs_data"             # local mount point
```

All share types use the same **file_scan** settings (extensions, recursive, scan_sqlite_as_db, sample_limit) from config. Findings appear in the **Filesystem findings** sheet.

## Adding new connectors

To support a new data source (e.g. another database driver or API), see **[docs/ADDING_CONNECTORS.md](docs/ADDING_CONNECTORS.md)**. It describes the connector contract, how to register a new type (or driver), optional dependencies, and includes step-by-step instructions plus examples (database-style and API-style).

## Logging and alerts

- Log file: `audit_YYYYMMDD.log` (and console).
- On each finding (possible personal/sensitive data), the app logs and prints an `[ALERT]` to the console so the operator is notified on the fly.

## Dependencies and security

- **Sync locked deps:** From project root, generate a locked `requirements.txt` from `pyproject.toml` with:  
  `uv pip compile pyproject.toml -o requirements.txt`  
  (or keep `requirements.txt` in sync manually with `pyproject.toml`.)
- **Check for known CVEs:** Run `uv pip audit` (or `pip audit` if available) before deployment; fix or pin any vulnerable packages.
- See also **Security and compliance** below.

## Security and compliance

- No raw sampled content is persisted; only metadata (location, pattern, sensitivity, norm tag).
- Use recent, CVE-patched versions of the interpreter and dependencies (`uv sync` / `pip install -e .`).
- Keep credentials in config files or environment; avoid committing secrets.

## License

See [LICENSE](LICENSE).
