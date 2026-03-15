# Contributing to python3-lgpd-crawler

**Português (Brasil):** [CONTRIBUTING.pt_BR.md](CONTRIBUTING.pt_BR.md)

Thank you for considering contributing. This document covers local setup, workflow, and best practices so you can run the app, tests, and open changes safely.

## Quick start (development)

1. **Clone and enter the repo**

   ```bash
   git clone https://github.com/YOUR_ORG/python3-lgpd-crawler.git
   cd python3-lgpd-crawler
   ```

1. **Use Python 3.12+**

   The project targets Python 3.12 and 3.13. See [SECURITY.md](SECURITY.md) for supported versions.

1. **Install dependencies with uv (recommended)**

   ```bash
   uv sync
   ```

   Or with pip inside a virtualenv: `pip install -e .`

1. **Run tests**

   ```bash
   uv run pytest -v -W error
   ```

   All tests must pass with no errors or warnings. See [docs/TESTING.md](docs/TESTING.md) for what each test module covers and how to run subsets.

1. **Run the app**

   ```bash
   uv run python main.py --config config.yaml
   uv run python main.py --config config.yaml --web --port 8088
   ```

## Workflow

- **Bugs and features:** Open an issue using the [Bug report](.github/ISSUE_TEMPLATE/bug_report.md) or [Feature request](.github/ISSUE_TEMPLATE/feature_request.md) templates.
- **Security:** Do not post exploit details publicly. Use the [Security issue](.github/ISSUE_TEMPLATE/security.md) template (high-level only) or the process in [SECURITY.md](SECURITY.md).
- **Pull requests:** Use the [PR template](.github/PULL_REQUEST_TEMPLATE.md). Ensure tests pass (`uv run pytest -v -W error`; see [docs/TESTING.md](docs/TESTING.md)), the lint job passes (`uv run ruff check .`), and that docs/README are updated when behaviour or setup changes.

### Reducing merge conflicts

- **Merge or rebase `main` into your branch before opening a PR.** Run `git fetch origin main` then `git merge origin/main` (or `git rebase origin/main`) and fix any conflicts locally. That way the PR stays mergeable and reviewers see a clean diff.
- **`report/generator.py`:** Sheet-writing logic lives in `_write_excel_sheets` and helpers (`_build_report_info`, `_build_executive_summary_rows`, etc.). When adding or changing Excel sheets, update those helpers rather than inlining logic in `generate_report`. That keeps the same structure as `main` and avoids the merge conflicts we had when main had inlined code and the branch had the refactor.

## Code and docs

- **Style:** The repo uses [EditorConfig](.editorconfig) (indent, charset, line endings). Run `uv run ruff check .` and `uv run ruff format --check .` (or fix with `uv run ruff format .`) before PR so the CI lint job passes. **Recommended:** install [pre-commit](https://pre-commit.com/) hooks so Ruff (check + format) runs on every commit: `uv sync` then `uv run pre-commit install`; see `.pre-commit-config.yaml`.
- **Docs:** Keep [README.md](README.md) and [docs/USAGE.md](docs/USAGE.md) in sync with behaviour; update [README.pt_BR.md](README.pt_BR.md) and [docs/USAGE.pt_BR.md](docs/USAGE.pt_BR.md) for Portuguese. All **new** user-facing documentation must exist in **English (canonical)** and **Brazilian Portuguese**; **plan files** may be English-only. When you change docs to reflect application updates, **sync the other language** (EN first, then pt-BR). Use a language switcher at the top of each doc and cross-links that offer both languages (see [docs/README.md](docs/README.md) — Documentation policy). **After editing any .md file:** run `uv run python scripts/fix_markdown_sonar.py` and `uv run pytest tests/test_markdown_lint.py -v -W error` so SonarQube/markdownlint rules (e.g. MD060 table style) pass. The fix script applies MD029 (ordered list style 1/1/1); if a doc uses **semantic step numbers** (1. 2. 3.), restore them by hand after running the script so the list still reads correctly.
- **Secrets:** Never commit credentials or real PII. Use `.env` or `config.local.yaml` (both are in `.gitignore`) and redact in issues/PRs.

## CI and dependency hygiene

- **CI:** GitHub Actions run tests and **dependency audit** (`uv run pip-audit`) on every push/PR to `main` (or `master`). PRs must resolve any audit failures (fix or upgrade vulnerable dependencies) before merge. When SonarQube/SonarCloud is enabled (see [docs/TESTING.md](docs/TESTING.md)), address reported issues so the quality gate stays green.
- **Dependencies:** The source of truth for libraries is **`pyproject.toml`** (uv toolchain). The **`uv.lock`** file pins the exact resolved dependency tree so installs are reproducible and users are protected from “it worked yesterday” breakage when a dependency updates. Declare all runtime and dev dependencies in **`pyproject.toml`** (prefer **minimum versions `>=`**; pin `==` only when needed). When you add or change deps, run `uv lock`, then `uv export --no-emit-package pyproject.toml -o requirements.txt`, and commit **pyproject.toml**, **uv.lock**, and **requirements.txt**. Do not edit `uv.lock` or `requirements.txt` by hand for version changes. CI runs `uv sync` (which uses `uv.lock`) and then `pip-audit`, so the locked environment is what is tested and audited.
- **Dependabot / automation:** Dependabot opens weekly PRs for pip and GitHub Actions. When applying a dependency update (e.g. from a Dependabot PR), update **`pyproject.toml`** first (bump the minimum version), then run `uv lock` and `uv export --no-emit-package pyproject.toml -o requirements.txt`, and commit all three files. Merge dependency PRs only after CI (tests and audit) pass. Dependabot helps signal when to refresh dependencies; acting on those PRs (or before a stable release) keeps the lockfile updated, compatible, and safe. For **security** Dependabot PRs, we use the optional SLA in [SECURITY.md](SECURITY.md) (Security response).

## Release history and changelog

Release history is **git commit/PR history** plus **versioned release notes in `docs/releases/`** (e.g. one file per version). A separate CHANGELOG file in the repo is **not required**; use `docs/releases/` and tags for “where we are” and progress.

## Release checklist (Security)

Before tagging a **stable release**, maintainers should:

- **Lockfile and audit:** Run `uv lock` to refresh the lockfile from current `pyproject.toml`, then `uv sync` and `uv run pip-audit`. Fix or upgrade any high/critical findings, then run `uv export --no-emit-package pyproject.toml -o requirements.txt` and commit **uv.lock** and **requirements.txt** so the release is reproducible, compatible, and safe. This protects users from accidental breakage while keeping the release on audited dependencies.
- **Docs:** Ensure [SECURITY.md](SECURITY.md) and [docs/SECURITY.md](docs/SECURITY.md) reflect current behaviour (validation, headers, API key, logging policy).
- **Secrets and logging:** Confirm no API keys or passwords in logs; config file and env handling restrict access to trusted users (see [SECURITY.md](SECURITY.md)). Ensure **config file permissions** restrict read/write to trusted users and that **config.yaml** (and any file with secrets) is **not committed** (see .gitignore). When adding or changing log statements, do not log raw config, request bodies, or credentials; failure/exception text is redacted via `core.validation.redact_secrets_for_log` (regression: `test_redact_secrets_for_log_*` in `tests/test_security.py`).

## Deployment and production

- Use a dedicated config file (e.g. via `CONFIG_PATH`) and never commit it. Run `uv run pip-audit` before deploying.
- For public or multi-tenant use, put the API behind a reverse proxy (HTTPS, rate limiting, auth) as described in the README.

## See also

- **[docs/TESTING.md](docs/TESTING.md)** ([pt-BR](docs/TESTING.pt_BR.md)) — Test modules, CI, SonarQube.
- **[docs/TOPOLOGY.md](docs/TOPOLOGY.md)** ([pt-BR](docs/TOPOLOGY.pt_BR.md)) — Application topology (modules, classes, data flow).
- **[docs/COMMIT_AND_PR.md](docs/COMMIT_AND_PR.md)** ([pt-BR](docs/COMMIT_AND_PR.pt_BR.md)) — Commit and PR automation.
- **[docs/COMPLIANCE_FRAMEWORKS.md](docs/COMPLIANCE_FRAMEWORKS.md)** ([pt-BR](docs/COMPLIANCE_FRAMEWORKS.pt_BR.md)) — Compliance labels and extensibility.
- **[docs/COPYRIGHT_AND_TRADEMARK.md](docs/COPYRIGHT_AND_TRADEMARK.md)** ([pt-BR](docs/COPYRIGHT_AND_TRADEMARK.pt_BR.md)) — Copyright and trademark (making it official, registries). [NOTICE](NOTICE) for project notice.
- Full doc index: [docs/README.md](docs/README.md) ([pt-BR](docs/README.pt_BR.md)).

If you have questions, open a discussion or an issue. Thanks for contributing.
