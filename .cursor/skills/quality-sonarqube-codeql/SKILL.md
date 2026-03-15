---
name: quality-sonarqube-codeql
description: Apply when implementing or reviewing Python/markdown for quality and security. Ensures SonarQube-style rules (S3981, S3776, S4423, S5706, S1192) and CodeQL-relevant patterns are followed, and that the project quality tests are run and pass.
---

# Quality: SonarQube and CodeQL (enforcement and tests)

Use this skill when implementing or reviewing **Python** or **markdown** changes that can affect static analysis (SonarQube) or code scanning (CodeQL). The project encodes quality rules in **tests**; this skill ensures we follow them and run the right tests after edits.

## When to apply

- Implementing or refactoring Python (api, core, config, connectors, report, tests).
- Adding or changing markdown (README, docs, SECURITY, CONTRIBUTING).
- Code review or PR preparation for quality/security.
- After any change that might introduce S3981, S3776, bare except, weak TLS, or CodeQL findings.

## What to do

### 1. Avoid SonarQube violations (tests enforce these)

| Rule      | Avoid                                                       | Use instead                                                                             |
| --------  | --------                                                    | -------------                                                                           |
| **S3981** | `len(...) >= 0`                                             | `len(...) == 0` or `len(...) > 0` (or drop redundant check)                             |
| **S3776** | High cognitive complexity in a single function              | Extract helpers; keep functions in `tests/test_sonarqube_python.py` under complexity 15 |
| **S4423** | `ssl.create_default_context()` without minimum TLS          | Set `ctx.minimum_version = ssl.TLSVersion.TLSv1_2` (or stronger)                        |
| **S5706** | Bare `except:`                                              | `except Exception:` or specific exception types                                         |
| **S1192** | Repeated string literals for routes/response/template names | Named constants (see api/routes, report code)                                           |
| **S5856** | Session_id regex without `re.ASCII`                         | Use `re.ASCII` (or equivalent) when using `\w`                                          |

### 2. Avoid CodeQL-relevant patterns

- **Secrets:** Do not log API keys, passwords, or connection strings (see SECURITY.md, docs/security.md).
- **Injection:** Use parameterized queries and safe APIs; never concatenate user input into SQL or shell commands.
- **Crypto:** Prefer TLS 1.2+ and standard libraries; avoid weak or deprecated algorithms.

### 3. Markdown: points of attention

When adding or editing markdown, avoid common lint issues that the test or SonarQube report:

- **MD022:** Blank line before and after each heading.
- **MD026:** No trailing punctuation (`.` `:` `;` `!` `?`) in `#` headings.
- **MD032:** Blank lines around lists (fix script applies this).
- **MD041:** File must start with a top-level heading (`# Title`), not a blank line or front matter only.
- **MD024:** No duplicate heading text in the same file; use unique text per section (e.g. "What to do (Ruff):" not repeated "What to do:").
- **MD060:** Tables aligned (run fix script); use consistent fenced code markers (all ``` or all ~~~).

After `fix_markdown_sonar.py`, restore **semantic numbering** (1. 2. 3.) in step lists by hand when the list is a real sequence.

### 4. Run Ruff and quality tests after edits

After changing Python or markdown:

```bash
# Lint (CI runs this; extend-exclude in pyproject.toml skips legacy dirs)
uv run ruff check .

# SonarQube-style + security (Python)
uv run pytest tests/test_sonarqube_python.py tests/test_security.py -v -W error

# Markdown (if .md changed)
uv run python scripts/fix_markdown_sonar.py
uv run pytest tests/test_markdown_lint.py -v -W error
```

Before opening a PR, run the full suite:

```bash
uv run pytest -v -W error
```

Fix any failure; do not commit with failing quality tests. CodeQL runs in CI (`.github/workflows/codeql.yml`); address findings in the Security tab.

### 5. When adding new SonarQube or CodeQL rules

Keep adding tests so we avoid regressions without breaking the app:

1. **Add a test** that enforces the new rule (in the appropriate test module).
1. **Update the rule** (`.cursor/rules/quality-sonarqube-codeql.mdc`) and this skill with the rule id and guidance.
1. **Update docs/TESTING.md** so the new rule is listed in the quality section.

The full suite runs with `-W error` (pyproject.toml addopts and CI); all tests must stay green and warning-free during development so behaviour stays correct.

## Alignment with project

- **Rule:** `.cursor/rules/quality-sonarqube-codeql.mdc` – same scope (Python + markdown); apply that rule when editing those files.
- **Tests:** `tests/test_sonarqube_python.py`, `tests/test_security.py`, `tests/test_markdown_lint.py`; see **docs/TESTING.md** for the full list.
- **CI:** GitHub Actions run pytest and pip-audit; CodeQL runs on push/PR. Keeping tests green and fixing CodeQL findings is required for merge.
