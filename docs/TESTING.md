# Testing

**Português (Brasil):** [TESTING.pt_BR.md](TESTING.pt_BR.md)

This document describes how to run the test suite and what each test module covers. All tests must pass with **no errors or warnings** (`-W error`). CI runs the same command on every push and pull request.

## Running tests

From the project root:

```bash
# Full suite (recommended; uses pyproject.toml addopts including -W error)
uv run pytest -v -W error

# Or rely on addopts only
uv run pytest -v

# Run a single test file
uv run pytest tests/test_routes_responses.py -v -W error

# Run tests matching a keyword
uv run pytest -v -W error -k "session_id"
```

**Requirements:** Python 3.12+, dependencies installed (`uv sync` or `pip install -e .`). No external services are required; tests use temporary configs and in-memory or temporary SQLite where needed.

## Test modules overview

| Module                                | Purpose                                                                                                                                                                                                                                                          |
| --------                              | --------                                                                                                                                                                                                                                                         |
| **test_aggregated_identification.py** | Category mapping, aggregation rules, and report output for quasi-identifier aggregation (LGPD/compliance).                                                                                                                                                       |
| **test_api_key.py**                   | Optional API key: when `api.require_api_key` is true, X-API-Key or Bearer required; GET /health remains public.                                                                                                                                                  |
| **test_api_scan.py**                  | POST /scan triggers a full audit using the loaded config; session and background behaviour.                                                                                                                                                                      |
| **test_audit.py**                     | Sensitivity detection: CPF, email, religion, political affiliation, low-sensitivity classification.                                                                                                                                                              |
| **test_csp_headers.py**               | Security headers and Content-Security-Policy on dashboard and help pages (no `unsafe-inline` in script-src).                                                                                                                                                     |
| **test_data_scanner.py**              | Connector registry: filesystem, database (Postgres), API, unknown target resolution.                                                                                                                                                                             |
| **test_database.py**                  | Config normalization (empty, legacy, rate_limit, scan.max_workers), LocalDBManager, sessions, wipe.                                                                                                                                                              |
| **test_docs_markdown.py**             | Documentation quality: README and docs/USAGE exist, have a title and key content; relative links resolve; SECURITY.md has content.                                                                                                                               |
| **test_learned_patterns.py**          | Learned patterns: collect (sensitivity, pattern, filesystem), write YAML, exclusions.                                                                                                                                                                            |
| **test_logic.py**                     | Audit logic: CPF in content, lyrics/tablature downgrade, backward compatibility of scan results.                                                                                                                                                                 |
| **test_minor_detection.py**           | Minor detection: age/DOB heuristics, possible_minor flag, config wiring, report prioritization.                                                                                                                                                                  |
| **test_markdown_lint.py**             | SonarQube/markdownlint-style rules on project .md files: MD009, MD012, MD024, MD036, MD051, MD060, MD031 (blanks around fences), MD034 (no bare URLs), table pipe spacing. Excludes .venv, .cursor, .git.                                                        |
| **test_ml_engine.py**                 | MLSensitivityScanner: random_state seed (S6709), hyperparameters (S6973), local variable naming (S117), predict behaviour.                                                                                                                                       |
| **test_rate_limit_api.py**            | Rate limiting: 429 when max concurrent scans or min_interval exceeded; disabled by default for legacy configs.                                                                                                                                                   |
| **test_report_recommendations.py**    | Report recommendations, overrides, executive summary, min_sensitivity, possible_minor row/priority, config_scope_hash.                                                                                                                                           |
| **test_report_trends.py**             | Trends sheet and report info (tenant, technician) in generated reports.                                                                                                                                                                                          |
| **test_routes_responses.py**          | API contract and OpenAPI: invalid session_id → 400; 429/400/404 documented in OpenAPI; config page uses template constant.                                                                                                                                       |
| **test_scripts.py**                   | Shell/PowerShell script checks: `prep_audit.sh` bash syntax (`bash -n`, non-Windows), shebang and explicit `exit 1`; `scripts/commit-or-pr.ps1` PowerShell parse (Parser::ParseFile) and param block / ValidateSet. See [Script testing](#script-testing) below. |
| **test_security.py**                  | SQL injection resistance (identifier escaping), path traversal (session_id validation), ORM-only session_id use, YAML safe_load.                                                                                                                                 |
| **test_sonarqube_python.py**          | SonarQube-style guards: session_id regex (\\w + re.ASCII), response constants, report constants, connector/sql refactor helpers, no bare except in key modules.                                                                                                  |
| **test_sql_connector.py**             | SQL connector: skip schemas (Oracle vs default), should_skip_schema, discover (SQLite fallback), _discover_fallback_no_schemas.                                                                                                                                  |

## Quality and security-related tests

These tests encode **SonarQube** or **API contract** rules so that regressions are caught in CI:

- **test_routes_responses.py** – Ensures HTTP status codes (400, 404, 429) are both implemented and declared in the OpenAPI schema (SonarQube S8415). Validates invalid `session_id` returns 400 and that the config page responds correctly.
- **test_sonarqube_python.py** – Ensures constants are used instead of duplicated literals (S1192), session_id pattern uses `\w` with `re.ASCII` (S5856), refactored helpers exist in connector_registry and sql_connector (S3776), and key modules do not use bare `except:` (S5706).
- **test_ml_engine.py** – Ensures ML scanner has random_state seed (S6709), required hyperparameters (S6973), and local variable naming (S117).
- **test_docs_markdown.py** – Ensures key docs exist, have minimal structure, and internal links in README and docs/USAGE resolve (no broken links).
- **test_markdown_lint.py** – Ensures all project Markdown files pass MD009, MD012, MD024, MD036, MD051, MD060 (trailing spaces, consecutive blank lines, duplicate headings, emphasis-as-heading, link fragments, code fence consistency). See [Markdown lint](#markdown-lint) below.
- **test_security.py** – Ensures SQL identifier escaping prevents second-statement execution (SQL injection), session_id pattern rejects path traversal and SQL-like payloads, database layer uses ORM for session_id (no raw interpolation), and YAML config uses safe_load (no code execution). See [SECURITY.md](../SECURITY.md#resistance-to-common-vulnerabilities).

When adding or changing API behaviour, config schema, or quality rules, update the relevant test module and keep this document in sync.

### Script testing

Scripts are validated for **syntax and structure** only; no root or network is required:

- **prep_audit.sh** – On non-Windows: `bash -n prep_audit.sh` (syntax check). On all platforms: tests assert shebang and use of explicit `exit 1` when not root (Sonar-style best practice). The script is intended to run as root and install packages; tests do not execute it.
- **scripts/commit-or-pr.ps1** – PowerShell parse via `Parser::ParseFile` (no execution, no git calls). Tests also assert a `param` block with `ValidateSet('Preview','Commit','PR')`. Sonar-style fixes in the script: `git add -- $f`, `git commit -m "$Title" -m "$Body"` (quoted arguments).

### Markdown lint

Project `.md` files (excluding `.venv`, `.cursor`, `.git`, etc.) are checked for SonarQube/markdownlint-style rules so CI catches regressions:

- **MD009** – No trailing spaces at end of line.
- **MD012** – No multiple consecutive blank lines (max one).
- **MD024** – No duplicate heading text in the same file (headings inside fenced code blocks are ignored).
- **MD036** – No standalone emphasis-only line used as a heading (use `##` instead of `**Bold**`; labels with colons and long sentences are ignored).
- **MD051** – Link fragments (anchors) must not contain spaces.
- **MD060** – Fenced code blocks use consistent markers (all ` ``` ` or all `~~~`).
- **MD031** – Blanks around fences: a blank line is required before and after each fenced code block.
- **MD034** – No bare URLs: wrap in angle brackets (`<url>`) or use `[text](url)`; URLs inside backticks or code blocks are ignored.
- **MD060 (table)** – Table column style “aligned” (pipes align with header). Apply `uv run python scripts/fix_markdown_sonar.py` to fix MD007, MD009, MD012, MD029, MD032, MD036, MD047, and MD060 across all project `.md` files.

Run the check as part of the full suite: `uv run pytest tests/test_markdown_lint.py -v -W error`.

## CI

GitHub Actions (`.github/workflows/ci.yml`) runs:

1. **Test** – `uv run pytest -v -W error` on Ubuntu with Python 3.12.
1. **Dependency audit** – `uv run pip-audit` after `uv sync`.
1. **SonarQube / SonarCloud** – Code quality and security analysis (Python, scripts, etc.) when `SONAR_TOKEN` is set in repo secrets. See [SonarQube / SonarCloud](#sonarqube--sonarcloud) below.

Code scanning (CodeQL) is in `.github/workflows/codeql.yml` and analyzes Python for security and quality findings. See the repository **Security** tab for CodeQL alerts.

### SonarQube / SonarCloud

Analysis is driven by [`sonar-project.properties`](../sonar-project.properties) at the repo root. **The same file is used in two places:**

- **Locally (Cursor / VS Code):** The SonarQube extension in your IDE uses this config when you run analysis from the editor (e.g. “Run SonarQube analysis”). That’s how code quality is checked on your machine. The extension talks to your SonarQube server or SonarCloud and shows issues in the editor.
- **In CI:** GitHub Actions has no Cursor or IDE extensions. The workflow runs the SonarScanner (same tool, same config) so every push/PR is analyzed and the quality gate applies. So CI does not “use” the Cursor extension; it runs the scanner directly using this same `sonar-project.properties`.

Keeping one `sonar-project.properties` in the repo keeps local (extension) and CI in sync. To enable the CI step:

- **SonarCloud:** Add a secret `SONAR_TOKEN` (create a token at [sonarcloud.io](https://sonarcloud.io)). Ensure `sonar.projectKey` and `sonar.organization` in `sonar-project.properties` match the project you create in SonarCloud (project key is often `organization_repo`).
- **SonarQube Server:** Add secrets `SONAR_TOKEN` and `SONAR_HOST_URL` (e.g. `<https://sonarqube.your-company.co>m`).

The pipeline is intended to be followed for all reported issues (bugs, vulnerabilities, code smells, and security hotspots). Fix or justify findings; add or adjust tests where rules are encoded in the repo (e.g. `test_sonarqube_python.py`, `test_markdown_lint.py`, `test_scripts.py`) so that the same issues do not reappear. New findings from SonarQube should be addressed the same way: fix, add tests if the rule is in scope, and document in [TESTING.md](TESTING.md) or [CONTRIBUTING.md](../CONTRIBUTING.md) where relevant.

### Using extension issues to fix and prevent (automation)

The **same issues** the Cursor SonarQube extension shows come from the SonarQube/SonarCloud server. You can use them to fix code and prevent reintroduction in an automated way:

1. **Understand and fix**
   - **In the IDE:** Use the extension to see issues (file, line, rule, message). Fix them by hand or with the help of an agent that reads the same list.
   - **Machine-readable list:** Run `scripts/sonar_issues.py` (see below) to fetch the current issues from the API. The script prints one line per issue: `file:line:rule:severity:message`. Use this output to drive fixes (e.g. feed it to a script or an agent that applies fixes for known rule types).

1. **Prevent reintroduction (already automated)**
   - **CI:** The Sonar job in `.github/workflows/ci.yml` runs the same analysis on every push/PR. The quality gate fails if new issues appear or the gate condition is not met, so problematic changes are blocked before merge.
   - **Tests:** Critical rules are encoded in pytest (`test_sonarqube_python.py`, `test_markdown_lint.py`, `test_scripts.py`, etc.). Even without running Sonar, CI runs these tests, so regressions for those rules are caught even if Sonar is not configured.

1. **Fetching the issue list (script)**
   - From the repo root, with `SONAR_TOKEN` set (and optionally `SONAR_HOST_URL` for a SonarQube server):
     - `uv run python scripts/sonar_issues.py` — prints one line per issue; exit code 1 if there are issues (so you can `scripts/sonar_issues.py || true` to just list, or fail a script when issues exist).
     - `uv run python scripts/sonar_issues.py --json` — prints the full API JSON.
   - The script reads `sonar.projectKey` from `sonar-project.properties`, so it stays in sync with the extension and CI. Use this list to fix issues and to feed automation (e.g. an agent that “fix all issues from this list”).

## See also

- [CONTRIBUTING.md](../CONTRIBUTING.md) – Local setup and workflow; run tests before opening a PR.
- [SECURITY.md](../SECURITY.md) – Supported versions and dependency audit.
- [docs/USAGE.md](USAGE.md) – API and config behaviour covered by the tests.
