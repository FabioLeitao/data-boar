# Security Policy

This document describes which versions of the application are supported, which dependency baseline is expected, and how to report security vulnerabilities to the maintainers.

## Supported versions

- **Application:** `python3-lgpd-crawler` – current development targets **Python 3.12+**.
- We aim to support the latest stable minor versions of Python 3.12 and 3.13 on Linux, macOS and Windows.
- Older Python versions (< 3.12) are not tested and should be considered unsupported.

## Dependencies and environment

Dependencies are declared in **`pyproject.toml`** and managed primarily via **uv**:

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

- Dependencies in **`pyproject.toml`** use minimum versions (`>=`) so security patches are allowed; **Dependabot** (see `.github/dependabot.yml`) opens weekly PRs for pip and GitHub Actions. Prefer merging those PRs after CI (tests and audit) pass.

- Locally, install and run a dependency audit:

  ```bash
  uv sync
  uv pip install pip-audit
  uv run pip-audit
  ```

  CI runs the same audit on every push/PR.

- When you change dependencies in `pyproject.toml`, regenerate `requirements.txt` using the command above so both files stay in sync.

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

## Reporting a vulnerability

If you believe you have found a security vulnerability in this project:

1. **Do not open a public issue with exploit details.**
2. Instead, please:
   - Open a new issue in the **Issues** tab with a short, high-level description (no sensitive PoC data), **or**
   - If GitHub security advisories or private reporting is available for this repo, prefer that channel.
3. Include at least:
   - Version/commit of the project you are using.
   - Python version and OS details.
   - A minimal description of the impact (e.g. information disclosure, privilege escalation, DoS).
4. The maintainers will:
   - Acknowledge receipt as soon as reasonably possible.
   - Investigate and, if confirmed, work on a fix and coordinate disclosure.

If you are unsure whether something is security-sensitive, err on the side of caution and use the private channel (or a minimal public issue) so we can triage it safely.
