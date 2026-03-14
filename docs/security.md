# Security: fixes, tests, and technician guidance

**Português (Brasil):** [security.pt_BR.md](security.pt_BR.md)

This document summarizes **critical and high-severity security measures** implemented in the application, the **regression tests** that guard them, and **recommendations for technicians** so you know what to keep an eye out for when configuring and operating the audit tool.

For full policy, supported versions, dependency audit, and how to report vulnerabilities, see **[SECURITY.md](../SECURITY.md)** ([pt-BR](../SECURITY.pt_BR.md)).

---

## What is protected (and how)

| Area                                        | Protection                                                                                                                                                                                                                     | Regression tests                                                                                                                                                                |
| ------                                      | ------------                                                                                                                                                                                                                   | ------------------                                                                                                                                                              |
| **Credential injection in connection URLs** | Database user and password are **URL-encoded** when building connection strings (SQL connector, MongoDB connector). Passwords containing `@`, `:`, `/`, or `#` no longer break URL parsing or get misinterpreted as host/path. | `test_sql_connector_build_url_encodes_password_special_chars`, `test_sql_connector_build_url_encodes_user_with_at`, `test_mongodb_connector_uri_encodes_password_special_chars` |
| **SQL injection**                           | Table/column names in dynamic SQL come from the database inspector (discover), not from user input. Identifiers are escaped per dialect (double-quote or backtick). `session_id` is only used via ORM/parameterized queries.   | `test_sqlite_identifier_escaping_prevents_second_statement`, `test_sql_connector_sample_uses_escaped_identifiers_sqlite`, `test_database_filters_use_orm_not_raw_sql`           |
| **Path traversal**                          | `session_id` in API paths is validated with a strict pattern (alphanumeric and underscore, 12–64 characters) before use in file paths. Invalid values return HTTP 400.                                                         | `test_session_id_validation_rejects_dangerous_patterns`                                                                                                                         |
| **Config / YAML**                           | Config is loaded with `yaml.safe_load` only (no arbitrary Python object deserialization). Malicious YAML tags (e.g. code execution) are rejected.                                                                              | `test_config_save_uses_safe_load`, `test_config_loader_uses_safe_load_not_load`                                                                                                 |
| **Config endpoint exposure**                | When `api.require_api_key` is true, GET `/config` returns **401** without a valid API key, so the raw config file (which may contain database passwords and secrets) is not exposed to unauthenticated users.                  | `test_config_endpoint_requires_api_key_when_required`                                                                                                                           |

All of the above tests live in **`tests/test_security.py`**. Running `pytest tests/test_security.py -v` regularly (e.g. in CI) helps ensure these protections are not accidentally removed.

---

## Recommendations for technicians

- **Passwords with special characters:** You can safely use database or MongoDB passwords that contain `@`, `:`, `/`, or `#`. The application encodes them when building connection URLs. No extra configuration is required.
- **Protecting the config in the UI:** The **Configuration** page (GET `/config`) shows and allows editing the main config file, which may contain credentials. If the API is exposed to untrusted users or networks, set **`api.require_api_key: true`** and provide a strong API key (or `api.api_key_from_env`). Then only requests that send a valid **X-API-Key** or **Authorization: Bearer** can access `/config`.
- **Where config is stored:** The config file path is set at startup (default `config.yaml` or `CONFIG_PATH`). Ensure the file and directory permissions restrict read/write to trusted users only.
- **Session IDs in URLs:** The API uses `session_id` in paths (e.g. `/reports/{session_id}`). Only values that match the allowed pattern (alphanumeric and underscore, 12–64 chars) are accepted; anything else returns 400. This prevents path traversal via crafted session IDs.
- **Deployment:** When the dashboard or API is exposed to the internet or untrusted networks, run behind a **reverse proxy** with **TLS** and proper authentication. Use the optional API key and rate limiting as an extra layer; see **SECURITY.md** and **docs/deploy/DEPLOY.md** (Security and hardening).

---

## Related documentation

- **SECURITY.md** ([pt-BR](../SECURITY.pt_BR.md)) — Security policy, headers, optional API key, reporting vulnerabilities.
- **docs/deploy/DEPLOY.md** ([pt-BR](deploy/DEPLOY.pt_BR.md)) — Deployment and hardening (Docker, Kubernetes, reverse proxy).
- **docs/USAGE.md** ([pt-BR](USAGE.pt_BR.md)) — CLI, API, and configuration (including `api.require_api_key`).
- **Man pages:** `man data_boar` or `man lgpd_crawler` (section 1), `man 5 data_boar` or `man 5 lgpd_crawler` (section 5) — include brief security and credential notes.
