# Security Policy

**Português (Brasil):** [SECURITY.pt_BR.md](SECURITY.pt_BR.md)

This document describes which versions of the application are supported, which dependency baseline is expected, and how to report security vulnerabilities to the maintainers. For copyright and license: [NOTICE](NOTICE); for making copyright and trademark official: [docs/COPYRIGHT_AND_TRADEMARK.md](docs/COPYRIGHT_AND_TRADEMARK.md) ([pt-BR](docs/COPYRIGHT_AND_TRADEMARK.pt_BR.md)).

## Supported versions

- **Application:** `python3-lgpd-crawler` – current development targets **Python 3.12+**.
- We aim to support the latest stable minor versions of Python 3.12 and 3.13 on Linux, macOS and Windows.
- Older Python versions (< 3.12) are not tested and should be considered unsupported.

## Dependencies and environment

**`pyproject.toml`** is the source of truth for the **uv** toolchain; **pip** and **`requirements.txt`** are derivative (requirements.txt is generated from pyproject.toml for pip-based or legacy environments). Dependencies are declared in **`pyproject.toml`** and managed primarily via **uv**:

- To install in a fresh environment:

  ```bash
  uv sync
  ```

- To generate a locked `requirements.txt` for legacy environments that use plain `pip`:

  ```bash
  uv pip compile pyproject.toml -o requirements.txt
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

- Dependencies in **`pyproject.toml`** use minimum versions (`>=`) so security patches are allowed; **Dependabot** (see `.github/dependabot.yml`) opens weekly PRs for pip and GitHub Actions. When applying a pip dependency update (from Dependabot or elsewhere), update **`pyproject.toml`** first (raise the minimum version for that package), then run `uv pip compile pyproject.toml -o requirements.txt` and commit both files; do not merge a change that only edits `requirements.txt`. Prefer merging dependency PRs after CI (tests and audit) pass.

- Locally, install and run a dependency audit:

  ```bash
  uv sync
  uv pip install pip-audit
  uv run pip-audit
  ```

  CI runs the same audit on every push/PR.

- Whenever you change dependencies (including when applying Dependabot or automation recommendations), edit **`pyproject.toml`** first, then regenerate `requirements.txt` with `uv pip compile pyproject.toml -o requirements.txt` so both files stay in sync.

## Resistance to common vulnerabilities

- **SQL injection:** Table and column names used in dynamic SQL (connectors) come from the database inspector (discover), not from user input. Identifiers are escaped per dialect: double-quote for SQLite/Postgres/Oracle (`"` → `""`), backtick for MySQL (`` ` `` → ` `` `). The local audit database (SQLite) uses SQLAlchemy ORM and parameterized queries only; `session_id` and other user-supplied values are never concatenated into raw SQL. See **`tests/test_security.py`** for regression tests.
- **Path traversal:** `session_id` in API paths is validated with a strict pattern (alphanumeric and underscore, 12–64 chars) before use in file paths or lookups; invalid values return HTTP 400. See **`api/routes.py`** `_validate_session_id` and **`tests/test_security.py`**.
- **Credential injection in connection URLs:** User and password are URL-encoded when building database connection URLs (SQL connector, MongoDB connector) so that special characters (`@`, `:`, `/`, `#`) in credentials do not break URL parsing or be misinterpreted as host/path. See **`connectors/sql_connector.py`** `_quote_userinfo` / `_build_url`, **`connectors/mongodb_connector.py`** `connect()`, and **`tests/test_security.py`** (e.g. `test_sql_connector_build_url_encodes_password_special_chars`, `test_mongodb_connector_uri_encodes_password_special_chars`).
- **Config and serialization:** YAML config is loaded with `yaml.safe_load` (no arbitrary Python object deserialization). See **`tests/test_security.py`** for a test that unsafe YAML tags are rejected.
- **Config endpoint exposure:** When `api.require_api_key` is true, GET `/config` returns 401 without a valid API key, so raw config (which may contain secrets) is not exposed. See **`tests/test_security.py`** `test_config_endpoint_requires_api_key_when_required`.

For a **technician-oriented summary** (what to watch for, regression tests, recommendations), see **`docs/security.md`** (EN) and **`docs/security.pt_BR.md`** (pt-BR).

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

Security headers (including CSP) are implemented in **`api/routes.py`** (middleware applied to web and API responses). To harden container and cluster deployments:

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
