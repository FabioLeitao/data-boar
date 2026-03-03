# How to Use the LGPD Audit Application

This guide covers **command-line arguments and outcomes**, **deploying and using the web API**, **configuration (targets and credentials)**, and **downloading reports** (current and previous sessions).

**Português (Brasil):** [USAGE.pt_BR.md](USAGE.pt_BR.md)

---


## 1. Command-line interface (CLI)

The main entry point is `main.py`. Prefer it over `run.py`.

### Arguments

| Argument | Default | Description |
|----------|---------|-------------|
| `--config` | `config.yaml` | Path to the configuration file (YAML or JSON). Used for both one-shot audit and to resolve `api.port` when starting the web server. |
| `--web` | *(flag)* | Start the REST API server instead of running a one-shot audit. |
| `--port` | `8088` | Port for the API when `--web` is set. Can be overridden by `api.port` in config. Ignored in one-shot mode. |
| `--reset-data` | *(flag)* | Dangerous maintenance operation: wipe all scan sessions, findings and failures from SQLite, delete generated reports/heatmaps under `report.output_dir`, and record the wipe in `data_wipe_log`. Does not start a scan. |
| `--tenant` | *(none)* | Optional customer/tenant name for the scan in CLI mode. Stored on the session and surfaced on dashboard and reports. |
| `--technician` | *(none)* | Optional technician/operator responsible for the scan in CLI mode. Stored on the session and surfaced on dashboard and reports. |

### Outcomes

**One-shot audit (no `--web`):**

```bash
# Minimal run
python main.py --config config.yaml

# Tag scan with tenant and technician metadata
python main.py --config config.yaml --tenant "Acme Corp" --technician "Alice Silva"
```

- Loads config, runs a full audit of all targets (databases, filesystems, APIs, shares as configured).
- Creates a new session (UUID + timestamp), writes findings to the local SQLite DB (including optional `tenant_name` and `technician_name`), then generates the Excel report (and heatmap) for that session.
- **Output:** Console prints `Scan session: <session_id>` and `Report written: <path>` (or "No findings to report.").
- Report path is under `report.output_dir` from config (default: current directory). File name: `Relatorio_Auditoria_<session_id>.xlsx` (and `heatmap_<session_id>.png`).

**REST API server (`--web`):**

```bash
python main.py --config config.yaml --web --port 8088
```

- Loads config and starts the FastAPI server on `0.0.0.0:<port>` (listens on all interfaces).
- **Outcome:** Server runs until interrupted. No scan runs automatically; you trigger scans and download reports via the API (see below).
- **Note:** The API process loads its own config at startup from the **`CONFIG_PATH`** environment variable, or `config.yaml` in the current working directory. To use a different file when running the server, set `CONFIG_PATH`:

  ```bash
  set CONFIG_PATH=production.yaml   # Windows
  export CONFIG_PATH=production.yaml   # Linux/macOS
  python main.py --web --port 8088
  ```

---

## 2. Deploying and accessing the web API

### Deploying the server

**Option: run from Docker (no Git clone)**  
A pre-built image is available on Docker Hub: `fabioleitao/python3-lgpd-crawler:latest` ([hub.docker.com/r/fabioleitao/python3-lgpd-crawler](https://hub.docker.com/r/fabioleitao/python3-lgpd-crawler)). Pull it and run with a mounted config at `/data/config.yaml` (see README “Deploy with Docker” and `deploy/DEPLOY.md`). You can use this instanced container instead of installing from source.

1. **Install** the application and optional dependencies (e.g. `.[nosql]`, `.[shares]`) as in the README.
2. **Prepare** a config file (e.g. `config.yaml`) with `targets`, `file_scan`, `report`, and optionally `api.port`.
3. **Set config path** (optional):  
   `CONFIG_PATH=/etc/lgpd-audit/config.yaml` (or your path) so the API loads that file regardless of working directory.
4. **Run the server:**

   ```bash
   python main.py --config config.yaml --web --port 8088
   ```

   Or with uvicorn directly (config is still read from `CONFIG_PATH` or `config.yaml` in the process working directory):

   ```bash
   uvicorn api.routes:app --host 0.0.0.0 --port 8088
   ```

5. **Binding:** Default `0.0.0.0` means the server accepts connections from any interface. Restrict by using `--host 127.0.0.1` if only local access is needed.
6. **Production:** Run behind a reverse proxy (nginx, Traefik, Caddy, or similar), use a process manager (systemd, supervisord), or a container; ensure `CONFIG_PATH` and `report.output_dir` are set appropriately and that the process can write to the output directory and the SQLite path. The application behaves correctly behind NAT, load balancers, and reverse proxies: when TLS is terminated at the proxy, set **X-Forwarded-Proto: https** so security headers (e.g. HSTS) and scheme detection work. See [SECURITY.md](../SECURITY.md) for HTTP security headers.

### Base URL and accessing the API

- **Base URL:** `http://<host>:<port>/`  
  Example: `http://localhost:8088/` or `http://your-server:8088/`
- **OpenAPI docs (interactive):**  
  - Swagger UI: `http://localhost:8088/docs`  
  - ReDoc: `http://localhost:8088/redoc`
- **No built-in authentication:** The API does not implement auth. Secure it at the reverse proxy or network level if exposed.

### Web dashboard

When the API server is running, a **simple web dashboard** is available in the browser:

| Page | URL | Description |
|------|-----|--------------|
| **Dashboard** | `http://<host>:<port>/` | Scan status (running/idle, current session, findings count), quantity/quality summary (DB findings, FS findings, failures, total), **“Progress over time” chart** (total findings + risk score per session), form inputs for **tenant/customer** and **technician/operator** before starting a scan, and a “Start scan” button. Recent sessions table shows session ID, started date, tenant, technician, findings, failures, and a download link. |
| **Reports** | `http://<host>:<port>/reports` | List of all scan sessions (session ID, started/finished, status, tenant, technician, DB/FS/failures counts) with a “Download” link per session (regenerates and downloads the Excel report). |
| **Configuration** | `http://<host>:<port>/config` | Edit the scan configuration (YAML) in the browser. “Save configuration” writes to the config file (see `CONFIG_PATH` or `config.yaml`). Changes apply to the next scan. |

| **Help** | `http://<host>:<port>/help` | Quickstart, config examples, and links to README/USAGE. |
| **About** | `http://<host>:<port>/about` | Application name, version, author, and license (same as repository LICENSE). |

The **Start scan** button sends `POST /scan` and triggers a **full audit of all targets** in the current configuration (the same databases, filesystems, APIs, and options defined in your config file). Saving the Configuration page updates the config used for the next scan. The dashboard uses the same API under the hood (`/status`, `/scan`, `/list`, `/reports/{session_id}`). Status polls automatically when a scan is running. No separate frontend build (Python + Jinja2 + minimal CSS/JS).

### API endpoints (summary)

| Method | Endpoint | Purpose |
|--------|----------|---------|
| `POST` | `/scan` or `/start` | Start a full audit in the background. Returns `session_id`. Optional JSON body: `{ "tenant": "Acme Corp", "technician": "Alice" }` to tag the session. |
| `POST` | `/scan_database` | One-off scan of a single database (body: name, host, port, user, password, database, driver, optional tenant/technician). Returns `session_id`. |
| `GET`  | `/status` | Current run state: `running`, `current_session_id`, `findings_count`. |
| `GET`  | `/report` | Download the **last generated** Excel report (or generate from last session if none). |
| `GET`  | `/heatmap` | Download the **last generated** heatmap PNG (sensitivity/risk heatmap for the most recent session). |
| `GET`  | `/logs` | Download the most recent `audit_YYYYMMDD.log` file with connection/finding entries. |
| `GET`  | `/list` or `/reports` | List past sessions (for choosing which report to download). Each entry includes tenant/technician when set. |
| `GET`  | `/reports/{session_id}` | **Regenerate** and download the Excel report for that session. |
| `GET`  | `/heatmap/{session_id}` | **Regenerate** the report (if needed) and download the heatmap PNG for that session. |
| `GET`  | `/logs/{session_id}` | Download the first audit log file that contains that `session_id`, for session-level trace analysis. |
| `PATCH` | `/sessions/{session_id}` | Set or clear tenant/customer name for an existing session. Body: `{ "tenant": "..." }`. |
| `PATCH` | `/sessions/{session_id}/technician` | Set or clear technician/operator name for an existing session. Body: `{ "technician": "..." }`. |
| `GET`  | `/about` | About page (HTML): application name, version, author, license. |
| `GET`  | `/about/json` | Machine-readable about info (name, version, author, license, copyright). |
| `GET`  | `/health` | Liveness/readiness for Docker and Kubernetes. |

---

## 3. Using the API (examples)

### Start a full audit

```bash
# Minimal: start a scan with default metadata
curl -X POST http://localhost:8088/scan

# Start a scan tagged with tenant/customer and technician/operator
curl -X POST http://localhost:8088/scan \
  -H "Content-Type: application/json" \
  -d '{ "tenant": "Acme Corp", "technician": "Alice Silva" }'
```

**Response (200):**

```json
{
  "status": "started",
  "session_id": "a1b2c3d4-20250301_143022"
}
```

- Use `session_id` to download that session’s report later (see “Download reports” below).

### Check status

```bash
curl http://localhost:8088/status
```

**Response (200):**

```json
{
  "running": true,
  "current_session_id": "a1b2c3d4-20250301_143022",
  "findings_count": 42
}
```

- When `running` is `false`, the audit for `current_session_id` has finished.

### One-off database scan

```bash
curl -X POST http://localhost:8088/scan_database \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Ad-hoc Postgres",
    "host": "db.example.com",
    "port": 5432,
    "user": "audit",
    "password": "secret",
    "database": "mydb",
    "driver": "postgresql+psycopg2",
    "tenant": "Acme Corp",
    "technician": "Alice Silva"
  }'
```

**Response (200):** Same as `/scan`: `{"status": "started", "session_id": "..."}`.

### List past sessions (to choose a report)

```bash
curl http://localhost:8088/list
```

**Response (200):**

```json
{
  "sessions": [
    {
      "session_id": "a1b2c3d4-20250301_143022",
      "started_at": "2025-03-01T14:30:22",
      "finished_at": "2025-03-01T14:35:10",
      "status": "completed",
      "tenant_name": "Acme Corp",
      "technician_name": "Alice Silva",
      "database_findings": 12,
      "filesystem_findings": 30,
      "scan_failures": 0
    }
  ]
}
```

Use any `session_id` to download that session’s report (see below).

### Download current (last) report

```bash
curl -o report.xlsx http://localhost:8088/report
```

- Returns the **last generated** Excel file.
- If no report exists, the server may try to generate one from the current or most recent session; if none exists, you get **404** with body like: `{"detail": "Report not available. Run a scan first."}`.

### Download current (last) audit log

```bash
curl -o audit.log http://localhost:8088/logs
```

- Returns the most recent `audit_YYYYMMDD.log` file written by the application.
- If no log file is found, you get **404** with `{"detail": "No log files found."}`.

### Download current (last) heatmap PNG

```bash
curl -o heatmap.png http://localhost:8088/heatmap
```

- Returns the **last generated** heatmap PNG for the most recent session (creating it along with the report if needed).
- If no suitable session exists, you get **404** with a message like `{"detail": "Heatmap not available. Run a scan first."}`.

### Download report for a specific (previous) session

```bash
curl -o report_20250301.xlsx "http://localhost:8088/reports/a1b2c3d4-20250301_143022"
```

- **Regenerates** the Excel (and heatmap) for that `session_id` and returns the file.
- If the session has no data or generation fails, you get **404** with `{"detail": "No data for session ... or report generation failed."}`.

### Download heatmap for a specific (previous) session

```bash
curl -o heatmap_20250301.png "http://localhost:8088/heatmap/a1b2c3d4-20250301_143022"
```

- Regenerates the report (and heatmap) for that `session_id` if needed and returns the PNG.
- If no heatmap is available for that session (e.g. no findings), you get **404** with `{"detail": "Heatmap not available for session ..."`}.

### Download audit log that contains a specific session

```bash
curl -o audit_20250301.log "http://localhost:8088/logs/a1b2c3d4-20250301_143022"
```

- Scans available `audit_YYYYMMDD.log` files (newest first) and returns the first one whose content contains that `session_id`.
- If no such log file is found, you get **404** with `{"detail": "No log file contains session_id ..."`}.

**Typical workflow:**

1. `POST /scan` → get `session_id`.
2. Poll `GET /status` until `running` is `false`.
3. Download last report: `GET /report` → save as Excel.
4. Or list sessions: `GET /list`, then download a specific one: `GET /reports/<session_id>`.

---

## 4. Configuration: targets and credentials

The application uses a **single** config file (YAML or JSON). The API loads it from:

- Environment variable **`CONFIG_PATH`**, or
- **`config.yaml`** in the process working directory.

CLI uses the path you pass with `--config` (e.g. `config.yaml`). For the **web server**, ensure the process either has `CONFIG_PATH` set or is started in a directory that contains `config.yaml` (or the path you use).

### Config file location and shape

- **Location:** Any path; typical names: `config.yaml`, `config/config.json`. Legacy `config/config.json` with `databases` and `file_scan.directories` is normalized automatically.
- **Root keys:** `targets`, `file_scan`, `report`, `api`, `sqlite_path`, `scan`, optional `ml_patterns_file`, `dl_patterns_file`, `regex_overrides_file`, `sensitivity_detection`, `learned_patterns`.

### Sensitivity detection: ML and DL training terms

You can set the **training words for ML and DL** in the main config (inline) or in separate YAML/JSON files. The pipeline is **hybrid**: regex → ML (TF-IDF + RandomForest) → optional DL (sentence embeddings + classifier). ML/DL terms use the same format: a list of `{ text, label }` with `label` = `sensitive` or `non_sensitive`.

- **Files:** `ml_patterns_file`, `dl_patterns_file` – paths to YAML/JSON with a list of `{ text, label }`.
- **Inline:** `sensitivity_detection.ml_terms`, `sensitivity_detection.dl_terms` – same structure; when non-empty they override the corresponding file.
- **DL backend:** Optional; install with `uv pip install -e ".[dl]"`. When installed and DL terms are provided, confidence is combined with ML for better semantic detection.

**Full description and examples:** [sensitivity-detection.md](sensitivity-detection.md) (English) · [sensitivity-detection.pt_BR.md](sensitivity-detection.pt_BR.md) (Português – Brasil).

### Custom regex patterns (new personal/sensitive values)

To detect **new possibly personal or sensitive values** (e.g. RG, vehicle plate, health plan ID), add custom regex patterns. In the main config set **`regex_overrides_file`** to the path of a YAML or JSON file with a list of `{ name, pattern, norm_tag }`. The detector matches each pattern against the column name and sample text; any match is reported with HIGH sensitivity. Your file adds to or overrides built-in patterns (CPF, CNPJ, email, phone, SSN, credit card, dates). **Format and examples:** [sensitivity-detection.md](sensitivity-detection.md#custom-regex-patterns-detecting-new-personalsensitive-values) (EN) · [sensitivity-detection.pt_BR.md](sensitivity-detection.pt_BR.md#padrões-regex-customizados-detectar-novos-dados-pessoaissensíveis) (pt-BR).

### Targets: databases

Each target is an object in `targets` with at least `name` and `type`. For SQL databases use `type: database` and the appropriate `driver`.

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
```

Credentials: `user`, `pass` (or `password`). Optional: `url` to pass a full SQLAlchemy URL instead of host/port/user/database.

**Snowflake (optional, .[bigdata]):**

```yaml
targets:
  - name: "Warehouse_LGPD"
    type: database
    driver: snowflake
    account: "xy12345.us-east-1"
    user: "AUDIT_USER"
    pass: "secret"
    database: "COMPLIANCE_DB"
    schema: "PUBLIC"
    warehouse: "AUDIT_WH"
    role: "ANALYST"   # optional
```

Install the optional dependency with:

```bash
uv pip install -e ".[bigdata]"
```

The Snowflake connector uses the same pattern as other SQL engines: discover tables/columns, sample rows (no raw storage), run sensitivity detection, and save findings as database metadata (schema, table, column, data type, sensitivity, pattern, norm tag, confidence).

### Targets: filesystem

```yaml
  - name: "Documentos_LGPD"
    type: filesystem
    path: /home/user/Documents/LGPD
    recursive: true
```

No credentials. Uses `file_scan` settings (extensions, recursive, scan_sqlite_as_db, sample_limit) from config.

### Targets: APIs (REST) – Basic, Bearer, OAuth2, custom

Use `type: api` or `type: rest`. Required: `name`, `base_url` (or `url`). Optional: `paths` or `endpoints`, `discover_url`, `timeout`, `headers`, and an `auth` block.

**Basic auth:**

```yaml
  - name: "Legacy API"
    type: api
    base_url: "https://api.example.com"
    paths: ["/users", "/contacts"]
    auth:
      type: basic
      username: "audit_user"
      password: "your_password"
```

**Bearer token (static or from environment):**

```yaml
  - name: "API with bearer"
    type: api
    base_url: "https://api.example.com"
    paths: ["/data"]
    auth:
      type: bearer
      token: "eyJhbGc..."   # or use token_from_env: "API_TOKEN" to read from env
```

**OAuth2 client credentials (machine-to-machine):**

```yaml
  - name: "Internal Users API"
    type: api
    base_url: "https://api.example.com"
    paths: ["/users", "/profiles"]
    auth:
      type: oauth2_client
      token_url: "https://auth.example.com/oauth/token"
      client_id: "audit-client"
      client_secret: "${API_OAUTH_SECRET}"   # or literal secret
      scope: "read:users"
```

Set the env var (e.g. `API_OAUTH_SECRET`) in the environment where the app runs.

**Custom headers (e.g. API key or Negotiate):**

```yaml
  - name: "API with custom header"
    type: api
    base_url: "https://api.example.com"
    paths: ["/export"]
    auth:
      type: custom
      headers:
        Authorization: "Bearer ..."
        X-API-Key: "your-api-key"
```

If you omit `auth` but set `user`/`username` and `pass`/`password` on the target, **basic** auth is applied.

### Targets: Power BI and Power Apps (Dataverse)

**Power BI** and **Dataverse (Power Apps)** use Azure AD OAuth2 client credentials. No extra package is required (httpx is already a dependency).

**Power BI (`type: powerbi`):**

- Required: `name`, `tenant_id`, `client_id`, `client_secret` (or under `auth:`).
- Optional: `workspace_ids` or `group_ids` (list of workspace GUIDs) to limit scan; omit to use “My workspace” and all workspaces.
- Azure AD app must have Power BI permission `Dataset.Read.All` or `Dataset.ReadWrite.All`. If using a service principal, enable “Allow service principals to use Power BI APIs” in the Power BI admin portal.

```yaml
  - name: "Power BI Compliance"
    type: powerbi
    tenant_id: "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
    client_id: "yyyyyyyy-yyyy-yyyy-yyyy-yyyyyyyyyyyy"
    client_secret: "${POWERBI_CLIENT_SECRET}"
    # workspace_ids: ["group-guid-1"]
```

**Dataverse / Power Apps (`type: dataverse` or `type: powerapps`):**

- Required: `name`, `org_url` (or `environment_url`, e.g. `https://myorg.crm.dynamics.com`), `tenant_id`, `client_id`, `client_secret` (or under `auth:`).
- Azure AD app needs application permission to Dataverse (admin consent). Scope is derived from `org_url`.

```yaml
  - name: "Dataverse HR"
    type: dataverse
    org_url: "https://myorg.crm.dynamics.com"
    tenant_id: "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
    client_id: "yyyyyyyy-yyyy-yyyy-yyyy-yyyyyyyyyyyy"
    client_secret: "${DATAVERSE_CLIENT_SECRET}"
```

Findings from Power BI and Dataverse appear in the **Database findings** sheet. Sampling uses `file_scan.sample_limit` (default 5).

### Targets: shared content (SMB, WebDAV, SharePoint, NFS)

Install optional deps: `uv pip install -e ".[shares]"`.

**SMB/CIFS:**

```yaml
  - name: "FileServer HR"
    type: smb
    host: "fileserver.company.local"
    share: "HR"
    path: "Documents"
    user: "audit_user"
    pass: "***"
    domain: "COMPANY"   # optional
    port: 445
    recursive: true
```

**WebDAV:**

```yaml
  - name: "WebDAV Storage"
    type: webdav
    base_url: "https://webdav.company.com/dav"
    user: "audit"
    pass: "***"
    path: "archive"
    recursive: true
    verify_ssl: true
```

**SharePoint:**

```yaml
  - name: "SharePoint HR"
    type: sharepoint
    site_url: "https://sharepoint.company.com/sites/hr"
    path: "Shared Documents"
    user: "audit@company.com"
    pass: "***"
```

**NFS (path = local mount point; mount NFS before scanning):**

```yaml
  - name: "NFS Export"
    type: nfs
    host: "nfs.company.local"
    export_path: "/export/data"
    path: "/mnt/nfs_data"   # local mount point
```

All share types use the same `file_scan` settings (extensions, recursive, scan_sqlite_as_db, sample_limit). Findings appear in the **Filesystem findings** sheet.

### Global options (excerpt)

```yaml
file_scan:
  extensions: [.txt, .csv, .pdf, .docx, .xlsx]
  recursive: true
  scan_sqlite_as_db: true
  sample_limit: 5

report:
  output_dir: .    # directory for Excel and heatmap PNG

api:
  port: 8088
  workers: 1       # uvicorn workers; 1 = minimal, 2+ for concurrent API traffic

sqlite_path: audit_results.db
scan:
  max_workers: 1   # 1 = sequential; >1 = parallel targets (I/O-bound)
```

---

## 5. Downloading reports (summary)

| Goal | How |
|------|-----|
| **Last generated report** | `GET /report` → save response as `.xlsx`. |
| **Report for a specific past session** | `GET /list` to get `session_id`s, then `GET /reports/<session_id>` → save as `.xlsx`. |
| **One-shot run (CLI)** | After `python main.py --config config.yaml`, the report path is printed; file is under `report.output_dir` as `Relatorio_Auditoria_<session_id>.xlsx`. |

- Reports are generated on demand for a given session (from SQLite findings). The heatmap PNG is written next to the Excel file when the report is generated.
- No built-in retention policy; reports are files on disk. Clean up or archive them as needed.

---

## 6. Quick reference

- **CLI one-shot:** `python main.py --config config.yaml`
- **CLI start API:** `python main.py --config config.yaml --web --port 8088`
- **Config for API:** Set `CONFIG_PATH` or place `config.yaml` in working directory.
- **Start scan:** `POST /scan` or `POST /start`
- **Status:** `GET /status`
- **List sessions:** `GET /list` or `GET /reports`
- **Download last report:** `GET /report`
- **Download report by session:** `GET /reports/{session_id}`
- **Interactive API docs:** `http://<host>:<port>/docs`

**Related documentation:** [sensitivity-detection.md](sensitivity-detection.md) (ML/DL training terms; [pt-BR](sensitivity-detection.pt_BR.md)). To add a new data-source connector (database, API, share), see [ADDING_CONNECTORS.md](ADDING_CONNECTORS.md).
