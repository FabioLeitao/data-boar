# Application topology

Textual description of modules, classes, and main functions and how they connect.

---

## Entry points

- **main.py** — CLI: `main()` parses `--config`, `--web`, `--port`; loads config via `config.loader.load_config`; if not `--web`, creates `AuditEngine(config)`, runs `start_audit()`, then `generate_final_reports()`; if `--web`, runs uvicorn with `api.routes.app` on given port.
- **api/routes.py** — FastAPI app: startup loads config and creates `AuditEngine`. Routes: POST `/scan`, `/start`; GET `/status`, `/report`, `/list`, `/reports`; GET `/reports/{session_id}`.

---

## Config

- **config/loader.py**
  - `load_config(path)` — Load YAML or JSON from path; return dict.
  - `normalize_config(data)` — Normalize to unified schema: `targets[]`, `file_scan`, `report`, `api`, `ml_patterns_file`, `regex_overrides_file`, `sqlite_path`, `scan.max_workers`. Legacy `databases` + `file_scan.directories` converted to `targets`.

---

## Core

- **core/session.py**
  - `new_session_id()` — Return UUID4 hex (12 chars) + timestamp string for scan session.

- **core/database.py**
  - **ScanSession** — SQLAlchemy model: id, session_id, started_at, finished_at, status.
  - **DatabaseFinding** — session_id, target_name, server_ip, engine_details, schema_name, table_name, column_name, data_type, sensitivity_level, pattern_detected, norm_tag, ml_confidence, created_at.
  - **FilesystemFinding** — session_id, target_name, path, file_name, data_type, sensitivity_level, pattern_detected, norm_tag, ml_confidence, created_at.
  - **ScanFailure** — session_id, target_name, reason, details, created_at.
  - **LocalDBManager** — `__init__(db_path)`, `set_current_session_id(sid)`, `current_session_id`, `save_finding(source_type, **kwargs)`, `save_failure(target_name, reason, details)`, `get_findings(session_id)`, `list_sessions()`, `create_session_record(session_id)`, `finish_session(session_id, status)`, `get_current_findings_count()`.

- **core/detector.py**
  - **SensitivityDetector** — `__init__(regex_overrides_path, ml_patterns_path)`; loads regex (built-in + overrides) and ML patterns; `analyze(column_name, sample_text)` → (sensitivity_level, pattern_detected, norm_tag, confidence). Uses TF-IDF + RandomForest when ML file or defaults available.
  - Helpers: `_load_regex_overrides(path)`, `_load_ml_patterns(path)`.

- **core/scanner.py**
  - **DataScanner** — `__init__(regex_overrides_path, ml_patterns_path)`; wraps `SensitivityDetector`. `scan_column(column_name, sample_content)` → dict (sensitivity_level, pattern_detected, norm_tag, ml_confidence); `scan_file_content(content, file_path)` → same dict or None; `analyze_data(column_name, sample_content)` → (level, pattern) for backward compatibility.

- **core/connector_registry.py**
  - `register(connector_type, connector_class, required_keys)` — Register connector class.
  - `get_connector(connector_type)` — Return (class, required_keys).
  - `list_connector_types()` — List registered types.
  - `connector_for_target(target)` — From target type/driver resolve (connector_class, required_keys).

- **core/engine.py**
  - **AuditEngine** — `__init__(config, db_path)`; holds `db_manager` (LocalDBManager), `scanner` (DataScanner). `start_audit()` → session_id (creates session, runs `_run_audit_targets()`); `_run_audit_targets()` runs each target via registry (sequential or parallel); `_run_target(target)` resolves connector and calls `connector.run()`. `generate_final_reports(session_id)` → report path via `report.generator.generate_report`. Properties: `is_running`, `get_current_findings_count()`, `get_last_report_path()`.
  - Imports connectors so they register (sql_connector, filesystem_connector, optional mongodb_connector, redis_connector).

---

## Connectors

- **connectors/sql_connector.py**
  - **SQLConnector** — `__init__(target_config, scanner, db_manager, sample_limit)`; `connect()`, `close()`, `discover()` → list of {schema, table, columns}; `sample(schema, table, column_name)` → string (no persistence); `run()` — connect, discover, sample each column, run scanner, save_finding or save_failure. Registered for postgresql, mysql, mariadb, sqlite, mssql, oracle.

- **connectors/filesystem_connector.py**
  - **FilesystemConnector** — `__init__(target_config, scanner, db_manager, extensions)`; `run()` — walk path (recursive or not), check `os.access(path, R_OK)`, read text sample via `_read_text_sample()`, run scanner, save_finding or save_failure. Registered for filesystem.
  - `_read_text_sample(path, ext, max_chars)` — Extract text from txt/csv/pdf/docx/odt/xlsx (helpers from pypdf, docx, pandas, odfpy).

- **connectors/mongodb_connector.py** (optional)
  - **MongoDBConnector** — connect, list collections, sample documents, run scanner on field names + combined sample text, save_finding. Registered for mongodb when pymongo is installed.

- **connectors/redis_connector.py** (optional)
  - **RedisConnector** — connect, SCAN keys, run scanner on key names, save_finding. Registered for redis when redis package is installed.

---

## Report

- **report/generator.py**
  - `generate_report(db_manager, session_id, output_dir)` — Read `get_findings(session_id)` (database_findings, filesystem_findings, scan_failures); write Excel with sheets "Database findings", "Filesystem findings", "Scan failures", "Recommendations", "Heatmap data"; call `_create_heatmap()` to save PNG; return Excel path.
  - `_create_heatmap(db_rows, fs_rows, output_dir, session_id)` — Build pivot and seaborn heatmap, save PNG.
  - `_recommendations_rows(db_rows, fs_rows)` — Build list of recommendation dicts from unique pattern_detected/norm_tag.

---

## API

- **api/routes.py**
  - FastAPI `app`; startup loads config and creates AuditEngine (singleton).
  - `POST /scan`, `POST /start` — Create session_id, run `_run_audit_targets()` in background; return session_id.
  - `GET /status` — running, current_session_id, findings_count.
  - `GET /report` — Download last report file (or generate from last session).
  - `GET /list`, `GET /reports` — List sessions from SQLite.
  - `GET /reports/{session_id}` — Regenerate report for session and return file.

---

## Utils

- **utils/logger.py**
  - `get_logger()` — Return unified logger (file audit_YYYYMMDD.log + console).
  - `setup_live_logger()` — Alias for get_logger().
  - `log_connection(target_name, target_type, location)` — Log successful connection.
  - `log_finding(source_type, target_name, location, sensitivity, pattern)` — Log and call notify_violation.
  - `notify_violation(message)` — Log and print [ALERT] to console.

---

## Data flow (summary)

1. **Config** → config/loader → normalized dict with targets, file_scan, report, api, sqlite_path.
2. **Engine** → core/engine creates LocalDBManager, DataScanner; for each target, connector_for_target → connector.run().
3. **Connectors** → connect, discover (and sample for DB), call scanner.scan_column or scan_file_content, db_manager.save_finding or save_failure; logger.log_connection / log_finding.
4. **Report** → report/generator reads SQLite via db_manager.get_findings(session_id), writes Excel + heatmap, returns path.
5. **API** → routes use same AuditEngine; /scan starts background _run_audit_targets; /report and /reports/{id} call generate_final_reports.

---

## Dependency direction (no cycles)

- config.loader — no project imports.
- core.session — no project imports.
- core.database — no project imports.
- core.detector — optional yaml/json, sklearn, pandas.
- core.scanner — core.detector.
- core.connector_registry — none.
- connectors.* — core.connector_registry, core.database (via db_manager), core.scanner (or scanner), utils.logger.
- core.engine — core.connector_registry, core.database, core.scanner, core.session; imports connectors.
- report.generator — core.database (LocalDBManager usage), pandas, openpyxl, matplotlib/seaborn.
- api.routes — config.loader, core.engine.
- main — config.loader, core.engine, api.routes (for app), uvicorn.
