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

- Use:

  ```bash
  uv sync
  uv pip audit
  ```

  regularly to ensure dependencies are installed as declared and checked against known CVEs.

- When you change dependencies in `pyproject.toml`, regenerate `requirements.txt` using the command above so both files stay in sync.

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
