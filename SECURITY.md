# Security Policy

**Português (Brasil):** [SECURITY.pt_BR.md](SECURITY.pt_BR.md)

This document describes which versions of the application are supported, which dependency baseline is expected, and how to report security vulnerabilities to the maintainers. For copyright and license: [NOTICE](NOTICE); for making copyright and trademark official: [docs/COPYRIGHT_AND_TRADEMARK.md](docs/COPYRIGHT_AND_TRADEMARK.md) ([pt-BR](docs/COPYRIGHT_AND_TRADEMARK.pt_BR.md)).

## Supported versions

- **Application:** `python3-lgpd-crawler` – current development targets **Python 3.12+**.
- We aim to support the latest stable minor versions of Python 3.12 and 3.13 on Linux, macOS and Windows.
- Older Python versions (< 3.12) are not tested and should be considered unsupported.

## Dependencies and environment

**`pyproject.toml`** is the source of truth for the **uv** toolchain. The **`uv.lock`** file pins the exact resolved dependency tree so that installs are reproducible and users are protected from accidental breakage when a dependency updates (“it worked yesterday”). **pip** and **`requirements.txt`** are derivative (requirements.txt is exported from the lockfile for pip-based or legacy environments). Dependencies are declared in **`pyproject.toml`** and managed via **uv**:

- To install in a fresh environment (uses **uv.lock** for reproducible versions):

  ```bash
  uv sync
  ```

- To export a locked **requirements.txt** for environments that use plain **pip** (same versions as **uv.lock**):

  ```bash
  uv export --no-emit-package pyproject.toml -o requirements.txt
  ```

### Runtime prerequisites (Linux example)

On Ubuntu/Debian you should have at least:

```bash
sudo apt update
sudo apt install -y \
  python3.12 python3.12-venv python3.12-dev build-essential \
  libpq-dev libssl-dev libffi-dev unixodbc-dev
```

Additional client libraries may be required depending on which connectors you use (e.g. Oracle, SQL Server, Snowflake); see the main `README.md` for connector-specific notes.

## Keeping dependencies up to date

- Dependencies in **`pyproject.toml`** use **minimum versions (`>=`)** so security patches are allowed; pin exact versions (`==`) only where necessary. The **lockfile (`uv.lock`)** is committed so that everyone (and CI) installs the same tree; it is refreshed when dependencies change or before a stable release so the app stays updated, compatible, and safe. **Dependabot** (see `.github/dependabot.yml`) opens weekly PRs for pip and GitHub Actions and helps signal when to act: when you apply an update (or before a release), update **`pyproject.toml`** first, then run `uv lock` and `uv export --no-emit-package pyproject.toml -o requirements.txt`, and commit **pyproject.toml**, **uv.lock**, and **requirements.txt**. Do not merge a change that only edits `requirements.txt` or `uv.lock` without updating the other. Merge dependency PRs only after CI (tests and audit) pass.

- Locally, install and run a dependency audit (CI does the same on every push/PR):

  ```bash
  uv sync
  uv pip install pip-audit
  uv run pip-audit
  ```

- Whenever you change dependencies (including when applying Dependabot or automation), edit **`pyproject.toml`** first, then run `uv lock` and `uv export --no-emit-package pyproject.toml -o requirements.txt` so **uv.lock** and **requirements.txt** stay in sync with the lockfile.

This approach is part of the project’s security baseline. For the full list of hardening measures and status, see **`docs/plans/completed/PLAN_SECURITY_HARDENING.md`**.

## Resistance to common vulnerabilities

- **SQL injection:** Table and column names used in dynamic SQL (connectors) come from the database inspector (discover), not from user input. Identifiers are escaped per dialect: double-quote for SQLite/Postgres/Oracle (`"` → `""`), backtick for MySQL (`` ` `` → ` `` `). The local audit database (SQLite) uses SQLAlchemy ORM and parameterized queries only; `session_id` and other user-supplied values are never concatenated into raw SQL. See **`tests/test_security.py`** for regression tests.
- **Path traversal:** `session_id` in API paths is validated with a strict pattern (alphanumeric and underscore, 12–64 chars) before use in file paths or lookups; invalid values return HTTP 400. See **`api/routes.py`** `_validate_session_id` and **`tests/test_security.py`**.
- **Input validation (tenant/technician):** Tenant and technician values (scan start body, session PATCH, config-driven scan) are validated for length and allowed characters (printable, no control chars), then sanitized before storage so reports and the dashboard never display unsanitized input. See **`core/validation.py`** `sanitize_tenant_technician` and **`tests/test_security.py`**.
- **Credential injection in connection URLs:** User and password are URL-encoded when building database connection URLs (SQL connector, MongoDB connector) so that special characters (`@`, `:`, `/`, `#`) in credentials do not break URL parsing or be misinterpreted as host/path. See **`connectors/sql_connector.py`** `_quote_userinfo` / `_build_url`, **`connectors/mongodb_connector.py`** `connect()`, and **`tests/test_security.py`** (e.g. `test_sql_connector_build_url_encodes_password_special_chars`, `test_mongodb_connector_uri_encodes_password_special_chars`).
- **Config and serialization:** YAML config is loaded with `yaml.safe_load` (no arbitrary Python object deserialization). See **`tests/test_security.py`** for a test that unsafe YAML tags are rejected.
- **Config endpoint exposure:** When `api.require_api_key` is true, GET `/config` returns 401 without a valid API key, so raw config (which may contain secrets) is not exposed. **GET `/config` always redacts secret values** (passwords, API key, tokens, client_secret, etc.) before sending YAML to the browser, so the UI never displays or transmits plain secrets; on save, placeholders are merged with the current file so real secrets are not overwritten. See **`config/redact_config.py`** and **`tests/test_security.py`**.
- **Config file and secrets:** Restrict config file permissions (e.g. `chmod 600` on `config.yaml`) so only trusted users can read it. **Do not commit** `config.yaml` or any file containing credentials to version control; use **`config.example.yaml`** (or **`deploy/config.example.yaml`**) as a template and keep local config in **`.gitignore`** (the project ignores `config.yaml`, `config.local.yaml`, and `*.vault`). Prefer storing secrets in environment variables (e.g. `pass_from_env`, `api_key_from_env`) so the config file holds no plain secrets. See **`docs/USAGE.md`** (Configuration) and **`docs/plans/PLAN_SECRETS_VAULT.md`** (Phase A).
- **Request body size limit:** The API rejects requests whose **Content-Length** exceeds **1 MB** (e.g. POST `/config`, POST `/scan`, POST `/scan_database`) with **HTTP 413 Payload Too Large** to reduce DoS via huge JSON or form bodies. See **`api/routes.py`** `request_body_size_middleware` and **`tests/test_security.py`** for regression tests.
- **Logging policy:** API key, passwords, and connection strings must not appear in audit or application logs. Failure details and exception messages are passed through **`core.validation.redact_secrets_for_log`** before being written to the log; connection URLs and `password=` / `api_key=`-style values are masked. Do not log raw config, request bodies, or driver exception messages that might contain credentials. See **`core/database.py`** (save_failure) and **`tests/test_security.py`** (redact_secrets_for_log).
- **Report and heatmap access:** Report and heatmap endpoints validate `session_id` format before use; invalid IDs return 400, unknown or missing sessions return 404 (no session enumeration or 403/404 distinction for unknown IDs). See **`api/routes.py`** and **`docs/SECURITY.md`**.

For a **technician-oriented summary** (what to watch for, regression tests, recommendations), see **`docs/SECURITY.md`** (EN) and **`docs/SECURITY.pt_BR.md`** (pt-BR). For completed and planned hardening steps, see **`docs/plans/completed/PLAN_SECURITY_HARDENING.md`**.

## HTTP security headers (web and API)

The application adds the following headers to all web and API responses by default:

- **X-Content-Type-Options: nosniff** – prevents MIME-type sniffing.
- **X-Frame-Options: DENY** – prevents the app from being embedded in frames (clickjacking mitigation).
- **Content-Security-Policy** – restricts script, style, and resource origins to the app and the Chart.js CDN; allows inline scripts/styles required by the current dashboard.
- **Referrer-Policy: strict-origin-when-cross-origin** – limits referrer information sent on cross-origin requests.
- **Permissions-Policy** – disables browser features not needed by the app (camera, microphone, geolocation, etc.).
- **Strict-Transport-Security (HSTS)** – set only when the request is considered HTTPS (direct or via `X-Forwarded-Proto: https` from a trusted proxy), so HTTP-only deployments are not locked out. When present, it uses `max-age=31536000; includeSubDomains; preload`.

When the app is behind a reverse proxy (e.g. nginx, Caddy, load balancer), ensure the proxy sets **X-Forwarded-Proto: https** for TLS-terminated requests so HSTS is applied correctly. Do not enable HSTS at the app layer for plain HTTP; the proxy can add HSTS when serving over HTTPS.

## Optional API key (enterprise)

The API does not implement authentication by default; secure the app at the reverse proxy or network level when exposed. For enterprises that want a simple shared-secret gate without changing the “secure at proxy” model, the application supports an **optional API key**:

- In config, set `api.require_api_key: true` and either `api.api_key` (literal) or `api.api_key_from_env: "VAR"` (read key from environment). When enabled, every request except **GET /health** must include either the **X-API-Key** header or **Authorization: Bearer &lt;key&gt;**; otherwise the API returns **401**. The **/health** endpoint is never protected so load balancers and orchestrators can still get 200.
- **Good practice:** Use a strong, random key and store it in an environment variable (e.g. `api_key_from_env: "AUDIT_API_KEY"`). Do not log the key or commit it to version control. This is a simple gate only; for full authentication and authorization, continue to use the reverse proxy or an identity provider.

## Deployment hardening and reverse proxy

Security headers (including CSP) are implemented in **`api/routes.py`** (middleware applied to web and API responses). For **operator-facing hardening** (containers, reverse proxy, TLS, WAF), see **`docs/USAGE.md`** and **`docs/deploy/DEPLOY.md`** (Security and hardening). To harden container and cluster deployments:

- **Docker and Kubernetes:** See **`docs/deploy/DEPLOY.md`**, section **“Security and hardening (optional)”**, for:
- Running as non-root, resource limits, and healthchecks.
- Optional Kubernetes examples: **securityContext** (runAsNonRoot, readOnlyRootFilesystem, drop capabilities), **NetworkPolicy** (`deploy/kubernetes/network-policy.example.yaml`), and **PodDisruptionBudget** (`deploy/kubernetes/pdb.example.yaml`).

When the API or dashboard is **exposed to the internet or untrusted networks**, run it behind a **reverse proxy** with **TLS**, proper **authentication/authorization**, and consider a **WAF** (web application firewall). The app’s API key and rate limiting (see `docs/USAGE.md`) complement but do not replace proxy-level security.

## Reporting a vulnerability

If you believe you have found a security vulnerability in this project:

1. **Do not open a public issue with exploit details.**
1. Instead, please:
   - Open a new issue in the **Issues** tab with a short, high-level description (no sensitive PoC data), **or**
   - If GitHub security advisories or private reporting is available for this repo, prefer that channel.
1. Include at least:
   - Version/commit of the project you are using.
   - Python version and OS details.
   - A minimal description of the impact (e.g. information disclosure, privilege escalation, DoS).
1. The maintainers will:
   - Acknowledge receipt as soon as reasonably possible.
   - Investigate and, if confirmed, work on a fix and coordinate disclosure.

If you are unsure whether something is security-sensitive, err on the side of caution and use the private channel (or a minimal public issue) so we can triage it safely.

## Security response (optional SLAs)

These are **targets** for maintainers and reporters, not contractual obligations. Adjust to your capacity.

| Area | Optional target |
|------|-----------------|
| **Vulnerability reports** | We aim to **acknowledge** within **5 working days** and, for **high/critical** findings, to **fix or document** (e.g. advisory, mitigation, or “won’t fix” with rationale) within **30 days**. |
| **Dependabot security PRs** | We treat Dependabot **security** PRs as **P0**: aim to **merge or respond** (e.g. merge, close with comment, or defer with rationale) within **5 working days**. Non-security dependency PRs follow the usual review cycle. |

See **CONTRIBUTING** for how to apply dependency updates and run `pip-audit`; see **`.github/dependabot.yml`** for Dependabot configuration.
