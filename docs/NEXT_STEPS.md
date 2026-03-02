# Next Steps – LGPD Audit Solution

Plan of next steps based on the [implementation plan](.cursor/plans/lgpd_audit_solution_full_implementation_4a673b9e.plan.md) and current codebase.

---

## 1. Status vs plan

| Plan item | Status | Notes |
|-----------|--------|------|
| config/loader.py | Done | Unified YAML/JSON, normalized schema |
| core/session.py | Done | UUID + timestamp |
| core/database.py | Done | Single SQLite, 4 tables, LocalDBManager |
| core/detector.py | Done | Regex + ML from config |
| core/scanner.py | Done | Uses detector only |
| core/connector_registry.py | Done | Registry + connector_for_target |
| core/engine.py | Done | start_audit, generate_final_reports, parallel/sequential |
| connectors/sql_connector.py | Done | Discover + sample, Oracle/MSSQL/MySQL/Postgres/etc. |
| connectors/filesystem_connector.py | Done | Permission check, recursive, many extensions |
| connectors/mongodb_connector.py | Done | Optional, pymongo |
| connectors/redis_connector.py | Done | Optional, redis |
| report/generator.py | Done | Excel + heatmap, DB/FS/failures/recommendations |
| api/routes.py | Done | /scan, /start, /status, /report, /list, /reports/{id} |
| main.py | Done | --config, --web, --port 8088 |
| utils/logger.py | Done | Unified logger, log_finding, notify_violation |
| README.md | Done | Install, config, run, DBs, file types |
| TOPOLOGY.md | Done | Module/class/function topology |
| config.yaml | Done | Unified shape, DB targets (commented), file_scan |
| pyproject.toml | Done | requires-python 3.12+, optional nosql/bigdata |
| requirements.txt | In place | Keep in sync with pyproject.toml |

---

## 2. Recommended next steps (in order)

### 2.1 Consolidate legacy code and tests

- **run.py** – Duplicate entry point (YAML, port 8080, own AuditEngine). Either remove and point users to `main.py`, or make it a thin wrapper that calls `config.loader` + `AuditEngine` and reuses `api.routes.app`.
- **api/app.py** – Second FastAPI app (`POST /scan_database`). Unify with `api/routes.py` (e.g. move route into routes and remove app.py) or document as legacy and deprecate.
- **scanners/** – `db_scanner.py`, `data_scanner.py`, `scanner_factory.py`, `report_generator.py`, `db_connector.py` reference `src.*` or old patterns. Either delete if unused or refactor to use `core.engine` + `connectors` + `report.generator` so there is a single scan/report path.
- **database/** – `connectors.py`, `scanner.py` used by old `main.py` flow. Current entry is `main.py` → `config.loader` → `core.engine` → `connectors.sql_connector`. Deprecate or remove `database/` if nothing else imports it.
- **file_scan/text_extractor.py** – Old detector. Replaced by `core.detector` + `connectors.filesystem_connector`. Remove or keep only as optional helper and document.
- **db/databasse.py** – Typo in name; alternate SQLite/audit models. Single source of truth is `core.database`. Remove or refactor to use `core.database` only.
- **report/sqlite_reporter.py** – Writes to `auditoria_dados.sqlite` with different schema. Single report path is `report.generator` + `core.database`. Remove or wire to LocalDBManager and same schema.
- **logging_custom/logger.py** – Superseded by `utils.logger`. Remove or make it import/alias `utils.logger`.
- **Tests** – `tests/test_audit.py`, `test_database.py`, `test_data_scanner.py`, `test_logic.py` likely import old modules. Update to use `config.loader`, `core.engine`, `core.database`, `connectors`, and run against the unified flow; add at least one CLI and one API smoke test.

**Deliverable:** Single entry (`main.py`), single engine, single report path; tests green and aligned with new topology.

---

### 2.2 Learned patterns (optional)

- Plan: “Append new terms classified sensitive to a ‘learned’ file; document how to merge into ml_patterns_file.”
- **Next step:** Add optional step in `AuditEngine` or report: at end of scan, write `learned_patterns.yaml` (or append to a file) with terms that were classified sensitive (e.g. column names that scored HIGH). Document in README: “Merge entries from `learned_patterns.yaml` into `ml_patterns_file` for the next run.”

**Deliverable:** Optional learned-patterns output + short README section.

---

### 2.3 Report “praise” for existing protections

- Original request: “Possible praise if there are clearly evidenced indications that data protection actions (pseudonymization, encryption, strong credentials) have already been applied.”
- **Next step:** In `report/generator.py`, add a “Praise / existing controls” section or sheet: e.g. when a finding has a norm_tag or pattern that suggests already protected (e.g. “encrypted”, “hash”, “tokenized” in column name or pattern_detected), add a positive line in the report. Can be a small heuristic (keyword in column name or in a new optional tag from the detector).

**Deliverable:** Report sheet or section that calls out possible existing protections.

---

### 2.4 Dependencies and security

- Run `uv pip compile` (or equivalent) and refresh pins in `pyproject.toml` for critical libs (e.g. cryptography, requests, fastapi, sqlalchemy, pyyaml).
- Regenerate or sync `requirements.txt` from pyproject.toml (e.g. `uv pip compile -o requirements.txt` or documented manual sync).
- Document in README: “Check dependencies for known CVEs (e.g. `uv pip audit` or safety).”

**Deliverable:** Updated pins, requirements.txt in sync, one-line CVE/audit note in README.

---

### 2.5 Optional connectors (BigData / APIs)

- Plan: “Snowflake, REST/SOAP, SharePoint, Datalake, Graylog/Grafana as optional connectors; document config and install.”
- **Next step:** Add optional connector modules (e.g. `connectors/snowflake_connector.py`, `connectors/rest_connector.py`) behind optional deps (`bigdata`, `api`), or at least document in README:
  - How to add a target (type, driver, URL/credentials).
  - Which packages to install (e.g. snowflake-connector-python, httpx/requests).
  - Example config snippets for Snowflake, a REST API, etc.

**Deliverable:** Docs and, if desired, one or two optional connector stubs (e.g. Snowflake, generic REST).

---

### 2.6 SQLite / .db files in filesystem scan

- Today: `.sqlite` / `.db` in file scan are path/name only (no content).
- **Next step:** Optionally treat them as DB targets: when scanning a file with extension `.sqlite` or `.db`, open with SQLAlchemy and run the same discover + sample + detect flow as for a database target, then save as filesystem_findings (or a dedicated flag) so the report still separates “from filesystem” vs “from database” but content is analyzed.

**Deliverable:** Design (config flag or auto-detect) and implementation for “scan SQLite files as DBs” in the file connector.

---

### 2.7 TOPOLOGY and README upkeep

- After any of the above, update TOPOLOGY.md (new modules, removed ones, data flow).
- README: keep supported DBs, file types, and optional connectors (including any new ones) in sync with the code.

**Deliverable:** TOPOLOGY.md and README accurate after each change.

---

## 3. File-level checklist (from plan)

| Path | Action | Status |
|------|--------|--------|
| pyproject.toml | Optional deps, CVE-safe pins | Done; refresh pins (2.4) |
| requirements.txt | Sync with pyproject | In place; formalize sync (2.4) |
| config/loader.py | Unified load | Done |
| core/session.py | UUID + timestamp | Done |
| core/database.py | Single schema | Done |
| core/detector.py | Regex + ML from config | Done |
| core/scanner.py | Use detector only | Done |
| core/connector_registry.py | Registry | Done |
| core/engine.py | Full engine + reports | Done |
| connectors/sql_connector.py | Discover + sample | Done |
| connectors/filesystem_connector.py | Permission, recursive, extensions | Done |
| connectors/mongodb_connector.py | Optional | Done |
| connectors/redis_connector.py | Optional | Done |
| report/generator.py | Single Excel + heatmap | Done; add praise (2.3) |
| api/routes.py | All routes | Done |
| main.py | CLI + API | Done |
| utils/logger.py | Unified logger | Done |
| README.md | Install, config, DBs, files | Done; keep updated (2.7) |
| TOPOLOGY.md | Full topology | Done; keep updated (2.7) |
| config.yaml | Unified shape | Done |
| run.py | Legacy | Consolidate or remove (2.1) |
| api/app.py | Legacy | Unify with routes (2.1) |
| scanners/* | Legacy | Remove or refactor (2.1) |
| database/* | Legacy | Deprecate/remove (2.1) |
| file_scan/*, db/*, report/sqlite_reporter.py | Legacy | Remove or align (2.1) |
| logging_custom/* | Legacy | Remove or alias (2.1) |
| tests/* | Update | Use new flow (2.1) |

---

## 4. Out of scope (per plan)

- No storage of raw DB/file content; only metadata (and optional anonymized example).
- No built-in SMB/NFS client; only local or OS-mounted paths.
- Deep learning is optional later; default remains regex + TF-IDF classifier.
- No WebSocket/streaming UI; REST API and file download only.

---

## 5. Suggested order of work

1. **2.1** – Consolidate legacy code and fix tests (removes confusion and prevents regressions).
2. **2.4** – Dependencies and security (low risk, high value).
3. **2.7** – TOPOLOGY + README after 2.1 and 2.4.
4. **2.3** – Report “praise” (small, visible improvement).
5. **2.2** – Learned patterns (optional, when ML tuning is a priority).
6. **2.6** – SQLite-as-DB in file scan (optional, when .sqlite/.db scanning is required).
7. **2.5** – Optional BigData/API connectors (when a specific integration is needed).
