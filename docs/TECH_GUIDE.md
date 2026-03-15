# Technical guide (Data Boar)

**Português (Brasil):** [TECH_GUIDE.pt_BR.md](TECH_GUIDE.pt_BR.md)

This guide covers installation, configuration, CLI and API reference, supported connectors, and deployment. For a high-level introduction and why Data Boar exists, see the [root README](../README.md).

## Features

- **Multi-target scanning**: Configure multiple databases, filesystems, APIs, remote shares, **Power BI**, and **Power Apps (Dataverse)** in a single YAML/JSON config.
- **SQL databases**: PostgreSQL, MySQL, MariaDB, SQLite, Microsoft SQL Server, Oracle (via SQLAlchemy drivers).
- **Power BI (optional)**: Discover workspaces, datasets, and tables via Power BI REST API; sample with DAX. Azure AD OAuth2 (client credentials). Findings in **Database findings** sheet.
- **Power Apps / Dataverse (optional)**: Discover entities and attributes via Dataverse Web API; sample rows. Azure AD OAuth2 (client credentials). Findings in **Database findings** sheet.
- **Remote shares (optional)**: SharePoint, WebDAV, SMB/CIFS, NFS — by FQDN or IP with credentials in config; install `.[shares]`.
- **NoSQL (optional)**: MongoDB, Redis — install optional deps: `uv pip install -e ".[nosql]"`.
- **Filesystem**: Recursive scan of local (or mounted) directories; permission check before reading. Supports many extensions: text (`.txt`, `.csv`, `.json`, `.xml`, `.html`, `.md`, `.yml`, `.log`, `.ini`, `.sql`, `.rtf`, etc.), documents (`.pdf`, `.doc`, `.docx`, `.odt`, `.ods`, `.odp`, `.xls`, `.xlsx`, `.xlsm`, `.ppt`, `.pptx`), email (`.eml`, `.msg`), and data (`.sqlite`, `.db`). **SQLite files** (`.sqlite`, `.sqlite3`, `.db`) found on disk are opened and scanned as databases (discover tables/columns, sample and detect); set `file_scan.scan_sqlite_as_db: false` to skip. Set `file_scan.extensions` to a list of suffixes, or `"*"` / `"all"` for all supported types.
- **Sensitivity detection**: Regex (configurable) + **ML** (TF-IDF + RandomForest) + optional **DL** (sentence embeddings + classifier) on column names and sampled content; no raw data is stored. You can set **ML and DL training terms** in the config (inline or via `ml_patterns_file` / `dl_patterns_file`). See [SENSITIVITY_DETECTION.md](SENSITIVITY_DETECTION.md) (English) or [SENSITIVITY_DETECTION.pt_BR.md](SENSITIVITY_DETECTION.pt_BR.md) (Português – Brasil) for examples. **Lyrics and music tablature** are detected via heuristics so that date-like or digit sequences in song lyrics and guitar tabs are downgraded to MEDIUM/LOW to reduce false positives; strong PII (CPF, email, etc.) still reports HIGH.
- **Multi-language, multi-encoding, and multi-regional**: Config and pattern files support **UTF-8** (recommended), UTF-8 BOM, and legacy encodings (cp1252, Latin-1); the main config is read with **auto-detection**. Compliance samples and reports support **Unicode** and terms in the language of your region (e.g. EN+FR for Canada, PT-BR+EN for Brazil). **Sample configs for UK GDPR, EU GDPR, Benelux, PIPEDA, POPIA, APPI, PCI-DSS, and other regions** are in [compliance-samples/](compliance-samples/); see [COMPLIANCE_FRAMEWORKS.md – Compliance samples](COMPLIANCE_FRAMEWORKS.md#compliance-samples) ([pt-BR](COMPLIANCE_FRAMEWORKS.pt_BR.md#amostras-de-conformidade)) for the list and how to use. Set **`pattern_files_encoding`** when using non-UTF-8 pattern files. See [USAGE – File encoding](USAGE.md#file-encoding-config-and-pattern-files) and [COMPLIANCE_FRAMEWORKS – Multi-language and regional operation](COMPLIANCE_FRAMEWORKS.md#multi-language-multi-encoding-and-multi-regional-operation).
- **Single SQLite**: All findings and failures per session (UUID + timestamp); metadata per scan includes optional **tenant_name** (customer/tenant) and **technician_name** (operator responsible). Separate tables for database findings, filesystem findings, and scan failures.
- **Reporting**: Excel with sheets **"Report info"** (Session ID, Started at, Tenant/Customer, Technician/Operator, Application, Version, Author, License, Copyright), "Database findings", "Filesystem findings", "Scan failures", "Recommendations", "Praise / existing controls" (indications of encryption/hashing/tokenization), **"Trends - Session comparison"** (this run vs up to 3 previous runs; aggregate notes), **"Heatmap data"** (table plus embedded heatmap image, fit-to-one-page when printed), and a standalone sensitivity/risk heatmap PNG. Report info and heatmap include optional Data Boar mascot branding; dashboard/reports pages show application and author attribution.
- **CLI and REST API**: Run one-shot audit from command line or start API (default port 8088) for `/scan`, `/start`, `/scan_database`, `/status`, `/report`, `/heatmap`, `/list`, `/reports/{session_id}`, `/logs`, `/about`, and `PATCH /sessions/{session_id}` for tenant/technician metadata. Both modes allow tagging scans with optional **tenant/customer** and **technician/operator** information. **Optional API key** and **rate limiting** (see [USAGE.md](USAGE.md)) protect the API when exposed. The web dashboard includes **Help**, **About** (author and license), and security headers (see [SECURITY.md](../SECURITY.md)). The application works behind NAT, load balancers, and reverse proxies (nginx, Traefik, Caddy); set `X-Forwarded-Proto: https` when TLS is terminated at the proxy.

## Requirements and environment preparation

- **Operating system**: Ubuntu 24.04 LTS / Debian 13 (recommended) or a recent Linux/macOS/Windows.
- **Python**: 3.12+.
- **Package manager**: [uv](https://github.com/astral-sh/uv) (recommended) or `pip`.

### Install Python and system libraries (Linux example)

On Debian/Ubuntu:

```bash
sudo apt update
sudo apt install -y python3.12 python3.12-venv python3.12-dev build-essential \
  libpq-dev libssl-dev libffi-dev unixodbc-dev
```

- `python3.12[-dev]` and `build-essential` are required to build some drivers (e.g. database clients).
- `libpq-dev`, `unixodbc-dev` and SSL/FFI headers help when using PostgreSQL, SQL Server, Oracle, or other SQLAlchemy drivers.

On Windows:

- Install **Python 3.12** from `python.org` and ensure "Add Python to PATH" is checked.
- Install database client tools as needed (e.g. Oracle Instant Client, SQL Server ODBC driver) following their vendor docs.

### Install uv

`uv` is a fast Python package/dependency manager:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh          # Linux/macOS
py -m pip install uv                                    # Windows (fallback if installer not used)
```

After installation, ensure `uv` is on your `PATH`:

```bash
uv --version
```

You can always fall back to plain `pip` + virtualenv if you prefer.

## Install the application

```bash
# With uv (recommended) – creates a virtualenv and installs deps
uv sync

# Or with pip (inside an activated virtualenv)
pip install -e .
```

### Running the app with uv

`uv` can also run the application directly with all dependencies:

```bash
# One-shot CLI scan
uv run python main.py --config config.yaml

# Start the API server (equivalent to python main.py --web)
uv run python main.py --config config.yaml --web --port 8088
```

Optional NoSQL support (MongoDB, Redis):

```bash
uv pip install -e ".[nosql]"
# or: pip install -e ".[nosql]"
```

## Configuration

Use a single config file in **YAML** or **JSON**. The API loads it from `CONFIG_PATH` or `config.yaml` in the working directory. For detailed **targets and credentials** (databases, filesystems, APIs with basic/bearer/OAuth2, and shared content), see **[USAGE.md](USAGE.md)**. For **multi-language and multi-regional** use (encoding, compliance samples per region), see [USAGE – File encoding](USAGE.md#file-encoding-config-and-pattern-files) and [COMPLIANCE_FRAMEWORKS](COMPLIANCE_FRAMEWORKS.md#multi-language-multi-encoding-and-multi-regional-operation). Example `config.yaml`:

```yaml
targets:

- name: "Producao_Postgres"

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

### Rate limiting and safety (optional)

To prevent accidental overload (several scans in a row or too many in parallel when called via API/dashboard), you can enable a `rate_limit` block in the main config:

```yaml
rate_limit:
  enabled: true
  max_concurrent_scans: 1
  min_interval_seconds: 0
  grace_for_running_status: 0
```

When `enabled` is true, API endpoints that start scans (`POST /scan`, `/start`, `/scan_database`) may respond with **HTTP 429** and a JSON payload describing the reason (e.g. too many running scans or minimum interval not elapsed). The CLI only prints warnings using the same logic, so existing scripts keep working. See [USAGE.md](USAGE.md) and [lgpd_crawler.5](lgpd_crawler.5) for full configuration details and examples.

## Run

### CLI (one-shot audit)

```bash
# Minimal run with default options
python main.py --config config.yaml

# Change report/API port via config (no --web here; one-shot mode ignores --port)
python main.py --config config_prod.yaml

# Tag run with tenant/customer and technician/operator
python main.py --config config.yaml --tenant "Acme Corp" --technician "Alice Silva"

# Report written to report.output_dir, e.g. Relatorio_Auditoria_<session_id>.xlsx
```

### REST API (default port 8088)

```bash
# Start API with default port 8088
python main.py --config config.yaml --web

# Start API on a custom port
python main.py --config config.yaml --web --port 9090

# Equivalent (bypassing main.py CLI)
uvicorn api.routes:app --host 0.0.0.0 --port 8088
```

## CLI arguments (reference)

| Argument            | Mode                   | Description                                                                                                                                                                                                                  | Examples                                             |
| ---------           | ------                 | -------------                                                                                                                                                                                                                | ----------                                           |
| `--config PATH`     | CLI & API              | Path to YAML/JSON config file. Defaults to `config.yaml` if omitted.                                                                                                                                                         | `--config config.yaml`, `--config configs/prod.yaml` |
| `--web`             | API only               | Start the REST API instead of running a one-shot scan.                                                                                                                                                                       | `--web`                                              |
| `--port N`          | API only               | Port for the REST API when `--web` is set. Defaults to `8088`. Ignored in one-shot CLI mode.                                                                                                                                 | `--web --port 9090`                                  |
| `--reset-data`      | CLI only (maintenance) | **Dangerous**: wipe all scan sessions, findings and failures from SQLite, delete generated reports/heatmaps under `report.output_dir`, and record the wipe event in `data_wipe_log` for auditability. Does not start a scan. | `--reset-data`                                       |
| `--tenant NAME`     | CLI only (one-shot)    | Optional customer / tenant name for this scan. Stored in `scan_sessions.tenant_name`, shown on dashboard and in the **Report info** sheet.                                                                                   | `--tenant "Acme Corp"`                               |
| `--technician NAME` | CLI only (one-shot)    | Optional technician / operator responsible for this scan. Stored in `scan_sessions.technician_name`, shown on dashboard and in the **Report info** sheet.                                                                    | `--technician "Alice Silva"`                         |

When using the API (`--web`), the server loads config from **`CONFIG_PATH`** (environment variable) or `config.yaml` in the working directory if `--config` is not provided on the CLI.

**Web dashboard:** With the server running, open <http://localhost:8088/> for a simple dashboard: scan status, quantity/quality of discovered data (DB/FS findings, failures), **progress graph over time** (total findings and a risk score per session), optional inputs for **tenant/customer** and **technician/operator** before starting a scan, recent sessions (including tenant/technician columns), and links to **Reports** (list and download) and **Configuration** (edit YAML in the browser).

## API routes (summary)

| Method   | Endpoint                            | Description                                                                                                                                      |
| -------- | ----------                          | -------------                                                                                                                                    |
| `POST`   | `/scan` or `/start`                 | Start full audit in background; returns `session_id`. Optional JSON body: `{ "tenant": "Acme Corp", "technician": "Alice" }` to tag the session. |
| `POST`   | `/scan_database`                    | One-off scan of one database (JSON body); returns `session_id`                                                                                   |
| `GET`    | `/status`                           | `running`, `current_session_id`, `findings_count`                                                                                                |
| `GET`    | `/report`                           | Download **last generated** Excel report                                                                                                         |
| `GET`    | `/heatmap`                          | Download **last generated** heatmap PNG (sensitivity/risk heatmap for most recent session)                                                       |
| `GET`    | `/list` or `/reports`               | List past sessions (to pick a report); includes `tenant_name`, `technician_name`, counts, and status.                                            |
| `GET`    | `/reports/{session_id}`             | Regenerate and download report for that session                                                                                                  |
| `GET`    | `/heatmap/{session_id}`             | Regenerate report (if needed) and download heatmap PNG for that session                                                                          |
| `PATCH`  | `/sessions/{session_id}`            | Set or clear tenant/customer name for an existing session. Body: `{ "tenant": "..." }`.                                                          |
| `PATCH`  | `/sessions/{session_id}/technician` | Set or clear technician/operator name for an existing session. Body: `{ "technician": "..." }`.                                                  |

For **deployment**, **using the web API** (with request/response examples), **configuration and credentials** (databases, filesystems, APIs with basic/bearer/OAuth2/custom auth, and shared content), and **downloading current and previous reports**, see **[USAGE.md](USAGE.md)**.

## Supported databases and drivers

| Engine           | Driver (config)             | Note                                                                                                                                   |
| -----------      | --------------------------- | -------------------------                                                                                                              |
| PostgreSQL       | `postgresql+psycopg2`       | psycopg2-binary                                                                                                                        |
| MySQL            | `mysql+pymysql`             | pymysql                                                                                                                                |
| MariaDB          | `mysql+pymysql`             | same as MySQL                                                                                                                          |
| SQLite           | `sqlite`                    | database = path                                                                                                                        |
| SQL Server       | `mssql+pyodbc`              | pyodbc                                                                                                                                 |
| Oracle (19+ RAC) | `oracle+oracledb`           | oracledb (thin mode; no Oracle Client). Config `database` = service name (e.g. customers_db or ORCL).                                  |
| Snowflake        | `snowflake`                 | optional: `uv pip install -e ".[bigdata]"`; config uses `account`, `user`, `pass`, `database`, `schema`, `warehouse`, optional `role`. |
| MongoDB          | `mongodb`                   | optional: pymongo                                                                                                                      |
| Redis            | `redis`                     | optional: redis                                                                                                                        |

For MongoDB/Redis, add a target with `type: database` and `driver: mongodb` or `redis` (host, port, database/password as needed). Install optional deps: `uv pip install -e ".[nosql]"`. For Snowflake, add a target with `type: database` and `driver: snowflake` and install the `.[bigdata]` extra.

## REST/API targets and authentication

You can scan remote HTTP(S) APIs for personal or sensitive data by adding targets with `type: api` or `type: rest`. The connector calls the configured endpoints (GET), parses JSON, and runs the same sensitivity detection on field names and sample values. **Authentication** is configurable so you can use static credentials, bearer tokens (e.g. negotiated or issued by an IdP), or OAuth2 client credentials.

**Required:** `name`, `base_url` (or `url`). **Optional:** `paths` or `endpoints` (list of path strings, e.g. `["/users", "/orders"]`), `discover_url` (GET returns a list of paths to scan), `timeout`, `headers`, and an `auth` block.

### Auth types

| Type              | Use case                                                             | Config                                                                                                                                                          |
| ------            | ----------                                                           | --------                                                                                                                                                        |
| **basic**         | Static username and password                                         | `auth: { type: basic, username: "...", password: "..." }`                                                                                                       |
| **bearer**        | Static or negotiated token (e.g. from Kerberos/AD, or API key)       | `auth: { type: bearer, token: "..." }` or `token_from_env: "MY_TOKEN_VAR"`                                                                                      |
| **oauth2_client** | OAuth2 client credentials (machine-to-machine)                       | `auth: { type: oauth2_client, token_url: "<https://...",> client_id: "...", client_secret: "..." }` (or `client_secret: "${ENV_VAR}"` to read from environment) |
| **custom**        | Custom headers (e.g. `Authorization: Negotiate ...`, API key header) | `auth: { type: custom, headers: { "Authorization": "Bearer ...", "X-API-Key": "..." } }`                                                                        |

If you omit `auth` but set `user`/`username` and `pass`/`password` on the target, **basic** auth is used.

## Example config (YAML) — API/REST

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
- **Auth:** Azure AD app with Power BI permissions (`Dataset.Read.All` or `Dataset.ReadWrite.All`). Enable "Allow service principals to use Power BI APIs" in the Power BI admin portal if using a service principal.
- **Config:** `tenant_id`, `client_id`, `client_secret` (or under `auth:`). Optional: `workspace_ids` or `group_ids` to limit to specific workspaces; omit to use "My workspace" and all workspaces the app can see.

The connector lists datasets and tables (push datasets expose table schema; for others it samples via DAX), runs sensitivity detection on column names and sample values, and writes **Database findings** (schema = dataset name, table = table name, column = column).

### Example config (YAML) — Power BI

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
- **Auth:** Azure AD app with application permission to Dataverse (e.g. "Common Data Service" / `user_impersonation` or env-specific application permission). Admin consent required.
- **Config:** `org_url` (or `environment_url`), e.g. `<https://myorg.crm.dynamics.co>m`, plus `tenant_id`, `client_id`, `client_secret` (or under `auth:`).

The connector lists entities (tables), their attributes, samples rows, runs sensitivity detection, and writes **Database findings** (schema = entity logical name, table = entity set, column = attribute).

### Example config (YAML) — Dataverse

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

| Type               | Host / URL                                                         | Credentials                       | Notes                                                                   |
| ------             | ------------                                                       | -------------                     | --------                                                                |
| **sharepoint**     | `site_url`: `<https://host/sites/sitenam>e`                        | `user`, `pass`; NTLM or basic     | On-prem or URL; path = server-relative folder (e.g. `Shared Documents`) |
| **webdav**         | `base_url`: `<https://host/pat>h`                                  | `user`, `pass`                    | Recursive list and download                                             |
| **smb** / **cifs** | `host`: FQDN or IP, `share`: share name, `path`: path inside share | `user`, `pass`, optional `domain` | Port 445 default                                                        |
| **nfs**            | `path`: **local mount point** (NFS must be mounted first)          | —                                 | `host` / `export_path` for reporting only                               |

### Example config (YAML) — File shares

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

To support a new data source (e.g. another database driver or API), see **[ADDING_CONNECTORS.md](ADDING_CONNECTORS.md)** (English) or **[ADDING_CONNECTORS.pt_BR.md](ADDING_CONNECTORS.pt_BR.md)** (Português – Brasil). The guide describes the connector contract, how to register a new type (or driver), optional dependencies, and includes step-by-step instructions plus examples (database-style and API-style).

## Logging and alerts

- Log file: `audit_YYYYMMDD.log` (and console).
- On each finding (possible personal/sensitive data), the app logs and prints an `[ALERT]` to the console so the operator is notified on the fly.

## Dependencies and security

- **Source of truth:** For the **uv** toolchain, **`pyproject.toml`** is the single source of truth for declared dependencies; **`uv.lock`** pins the resolved tree for reproducible installs (avoids “it worked yesterday” breakage). **pip** and **`requirements.txt`** are derivative (requirements.txt is exported from the lockfile for pip-based environments). Do not edit **`uv.lock`** or **`requirements.txt`** by hand for version changes. When you add, remove, or change a dependency, edit **`pyproject.toml`** only, then run `uv lock` and export.

- **Regenerate lockfile and requirements.txt after any dependency change:**

  ```bash
  # From project root: resolve and lock, then export for pip
  uv lock
  uv export --no-emit-package pyproject.toml -o requirements.txt
  ```

  Commit **pyproject.toml**, **uv.lock**, and **requirements.txt**. This keeps installs reproducible and aligned so `pip install -r requirements.txt` matches `uv sync`.

- **Dependabot / automation:** If a PR (e.g. from Dependabot) suggests updating only `requirements.txt` or `uv.lock`, apply the change to the **source of truth** first: update the corresponding minimum version in **`pyproject.toml`**, then run `uv lock` and `uv export --no-emit-package pyproject.toml -o requirements.txt` and commit all three files. Do not merge a dependency update that only edits `requirements.txt` or `uv.lock`.

- **Check for known CVEs:** Run `uv pip audit` (or `pip audit` if available) before deployment; fix or pin any vulnerable packages.
- See also **Security and compliance** below.

## Man pages

For systems that use the traditional `man` interface, two manual pages are provided:

- **Section 1 (command):** [lgpd_crawler.1](lgpd_crawler.1) — describes the program, its options, the web API, and curl examples. View with `man data_boar` or `man lgpd_crawler` (or `man 1 data_boar`, `man 1 lgpd_crawler`).
- **Section 5 (file formats):** [lgpd_crawler.5](lgpd_crawler.5) — describes the main config file topology and optional files (regex overrides, ML/DL pattern files, learned patterns), with examples. View with `man 5 data_boar` or `man 5 lgpd_crawler`.

On Linux/BSD, section 1 is for executable commands; section 5 is for configuration and file format conventions. Install both pages and add symlinks (see below) so that both **data_boar** and **lgpd_crawler** work: `man data_boar` / `man lgpd_crawler` for the command, `man 5 data_boar` / `man 5 lgpd_crawler` for config and file formats.

**Install both pages** (create the target directories first so the copy does not fail if they are missing). Right after creating the directories, run `chmod 755` on them so that all users can access the man pages; depending on your default umask, new directories may otherwise be 750 and only root could traverse them. After copying, run `chmod 644` on the installed files so that all users can read the pages (copied files may otherwise be 640).

```bash
sudo mkdir -p /usr/local/share/man/man1/
sudo mkdir -p /usr/local/share/man/man5/
sudo chmod 755 /usr/local/share/man/man1/ /usr/local/share/man/man5/
sudo cp docs/lgpd_crawler.1 /usr/local/share/man/man1/
sudo cp docs/lgpd_crawler.5 /usr/local/share/man/man5/
sudo chmod 644 /usr/local/share/man/man1/lgpd_crawler.1 /usr/local/share/man/man5/lgpd_crawler.5
sudo ln -sf lgpd_crawler.1 /usr/local/share/man/man1/data_boar.1
sudo ln -sf lgpd_crawler.5 /usr/local/share/man/man5/data_boar.5
sudo mandb    # or: sudo makewhatis   # depends on distro
```

The symlinks make both **data_boar** and **lgpd_crawler** resolve to the same pages. After that:

```bash
man data_boar        # or: man lgpd_crawler     # command and options (section 1)
man 5 data_boar      # or: man 5 lgpd_crawler   # config and file formats (section 5)
```

When adding new CLI options or API capabilities, update [lgpd_crawler.1](lgpd_crawler.1); when adding or changing config keys or pattern file formats, update [lgpd_crawler.5](lgpd_crawler.5) and the root [README](../README.md) so the man pages continue to reflect the current behaviour. The same files are viewed as both `man data_boar` and `man lgpd_crawler` (section 1 and 5) via symlinks at install time. For **version bumps** (major.minor.build convention and where to update the version number), see [VERSIONING.md](VERSIONING.md).

## Deploy with Docker

You can run the API as a **single container** (`docker run`), with **Docker Compose**, **Docker Swarm**, or **Kubernetes**. You may either **pull the pre-built image** from Docker Hub or **build from source** after cloning the repo.

### Pre-built image (Docker Hub)

Docker images are available on **Docker Hub** so you can run the application without cloning the repository:

- **Branded (Data Boar):** [hub.docker.com/r/fabioleitao/data_boar](https://hub.docker.com/r/fabioleitao/data_boar) — `fabioleitao/data_boar:latest` and `fabioleitao/data_boar:1.5.4`
- **Legacy:** [hub.docker.com/r/fabioleitao/python3-lgpd-crawler](https://hub.docker.com/r/fabioleitao/python3-lgpd-crawler) — `fabioleitao/python3-lgpd-crawler:latest` (same image may be published under both names)

The image includes regex + ML + optional DL sensitivity detection; you can set ML/DL training terms in config (see [SENSITIVITY_DETECTION.md](SENSITIVITY_DETECTION.md) and [deploy/config.example.yaml](../deploy/config.example.yaml)).

Example: run the web API with a local config directory:

```bash
docker pull fabioleitao/data_boar:latest
docker run -d -p 8088:8088 -v /path/to/your/data:/data -e CONFIG_PATH=/data/config.yaml fabioleitao/data_boar:latest
```

Prepare `/data/config.yaml` from `deploy/config.example.yaml` (see [deploy/DEPLOY.md](deploy/DEPLOY.md) ([pt-BR](deploy/DEPLOY.pt_BR.md))). You can decide to use this image as an instanced container instead of pulling the code from Git and building locally.

### Build from source

- **Build:** `docker build -t python3-lgpd-crawler:latest .`
- **Run:** Mount config at `/data/config.yaml` (see `deploy/config.example.yaml`). Expose port 8088.
- **Compose:** `docker compose -f deploy/docker-compose.yml -f deploy/docker-compose.override.yml up -d` (prepare `./data/config.yaml` first).
- **Swarm:** `docker stack deploy -c deploy/docker-compose.yml -c deploy/docker-compose.override.yml lgpd-audit`.
- **Kubernetes:** `kubectl apply -f deploy/kubernetes/` (see [deploy/kubernetes/README.md](deploy/kubernetes/README.md)).

Full steps (build, push, single container, Compose, Swarm, Kubernetes): **[deploy/DEPLOY.md](deploy/DEPLOY.md)** ([pt-BR](deploy/DEPLOY.pt_BR.md)). For MCP, build and push from source: [DOCKER_SETUP.md](DOCKER_SETUP.md) ([pt-BR](DOCKER_SETUP.pt_BR.md)).

## Compliance frameworks and extensibility

The application explicitly references **LGPD**, **GDPR**, **CCPA**, **HIPAA**, and **GLBA** in built-in patterns and report labels. We provide **sample configuration and config-file examples** (e.g. [regex_overrides.example.yaml](regex_overrides.example.yaml), recommendation overrides in [USAGE.md](USAGE.md)) so you can extend to **UK GDPR**, **PIPEDA**, **POPIA**, **APPI**, **PCI-DSS**, or custom norms without code changes: set **`norm_tag`** in [regex overrides](SENSITIVITY_DETECTION.md#custom-regex-patterns-detecting-new-personalsensitive-values) or custom connectors to any framework label, and use **`report.recommendation_overrides`** in config to tailor recommendation text. We can **assist with tuning** (tailored configs or slight code changes) for further compatibility when you reach out. See **[COMPLIANCE_FRAMEWORKS.md](COMPLIANCE_FRAMEWORKS.md)** ([pt-BR](COMPLIANCE_FRAMEWORKS.pt_BR.md)) for the full list of supported regulations, sample files, and extensibility.

## Security and compliance

- No raw sampled content is persisted; only metadata (location, pattern, sensitivity, norm tag).
- The web API adds security headers by default (X-Content-Type-Options, X-Frame-Options, Content-Security-Policy, Referrer-Policy, Permissions-Policy, and HSTS when served over HTTPS). See [SECURITY.md](../SECURITY.md).
- Use recent, CVE-patched versions of the interpreter and dependencies (`uv sync` / `pip install -e .`).
- Keep credentials in config files or environment; avoid committing secrets.
- **Behind a reverse proxy (nginx, Traefik, Caddy):** Set `X-Forwarded-Proto: https` for TLS-terminated traffic so HSTS and scheme detection work correctly.
- **Reporting vulnerabilities:** See [SECURITY.md](../SECURITY.md). **Testing:** See [TESTING.md](TESTING.md). **Contributing:** See [CONTRIBUTING.md](../CONTRIBUTING.md).

## Documentation (see also)

**Full index (all topics, EN and pt-BR):** [README.md](README.md) · [README.pt_BR.md](README.pt_BR.md). **Root intro:** [../README.md](../README.md) · [../README.pt_BR.md](../README.pt_BR.md). **Configuration and API usage:** [USAGE.md](USAGE.md) · [USAGE.pt_BR.md](USAGE.pt_BR.md). **Sensitivity (ML/DL):** [SENSITIVITY_DETECTION.md](SENSITIVITY_DETECTION.md) · [SENSITIVITY_DETECTION.pt_BR.md](SENSITIVITY_DETECTION.pt_BR.md). **Deploy:** [deploy/DEPLOY.md](deploy/DEPLOY.md) · [deploy/DEPLOY.pt_BR.md](deploy/DEPLOY.pt_BR.md). **Connectors:** [ADDING_CONNECTORS.md](ADDING_CONNECTORS.md) · [ADDING_CONNECTORS.pt_BR.md](ADDING_CONNECTORS.pt_BR.md). **Compliance:** [COMPLIANCE_FRAMEWORKS.md](COMPLIANCE_FRAMEWORKS.md) · [COMPLIANCE_FRAMEWORKS.pt_BR.md](COMPLIANCE_FRAMEWORKS.pt_BR.md). **Testing, security, contributing:** [TESTING.md](TESTING.md) · [TESTING.pt_BR.md](TESTING.pt_BR.md), [SECURITY.md](../SECURITY.md) · [SECURITY.pt_BR.md](../SECURITY.pt_BR.md), [CONTRIBUTING.md](../CONTRIBUTING.md) · [CONTRIBUTING.pt_BR.md](../CONTRIBUTING.pt_BR.md). **Copyright/trademark:** [COPYRIGHT_AND_TRADEMARK.md](COPYRIGHT_AND_TRADEMARK.md) · [COPYRIGHT_AND_TRADEMARK.pt_BR.md](COPYRIGHT_AND_TRADEMARK.pt_BR.md).

## License and copyright

See [LICENSE](../LICENSE). Project and copyright notice: [NOTICE](../NOTICE). For making copyright and trademark official (registration, registries): [COPYRIGHT_AND_TRADEMARK.md](COPYRIGHT_AND_TRADEMARK.md) ([pt-BR](COPYRIGHT_AND_TRADEMARK.pt_BR.md)).
