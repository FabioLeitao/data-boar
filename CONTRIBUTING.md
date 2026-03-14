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
- **Pull requests:** Use the [PR template](.github/PULL_REQUEST_TEMPLATE.md). Ensure tests pass (`uv run pytest -v -W error`; see [docs/TESTING.md](docs/TESTING.md)) and that docs/README are updated when behaviour or setup changes.

### Reducing merge conflicts

- **Merge or rebase `main` into your branch before opening a PR.** Run `git fetch origin main` then `git merge origin/main` (or `git rebase origin/main`) and fix any conflicts locally. That way the PR stays mergeable and reviewers see a clean diff.
- **`report/generator.py`:** Sheet-writing logic lives in `_write_excel_sheets` and helpers (`_build_report_info`, `_build_executive_summary_rows`, etc.). When adding or changing Excel sheets, update those helpers rather than inlining logic in `generate_report`. That keeps the same structure as `main` and avoids the merge conflicts we had when main had inlined code and the branch had the refactor.

## Code and docs

- **Style:** The repo uses [EditorConfig](.editorconfig) (indent, charset, line endings). Keeping Python style consistent (e.g. with Ruff or Black) is encouraged.
- **Docs:** Keep [README.md](README.md) and [docs/USAGE.md](docs/USAGE.md) in sync with behaviour; update [README.pt_BR.md](README.pt_BR.md) and [docs/USAGE.pt_BR.md](docs/USAGE.pt_BR.md) for Portuguese. All **new** user-facing documentation must exist in **English (canonical)** and **Brazilian Portuguese**; **plan files** may be English-only. When you change docs to reflect application updates, **sync the other language** (EN first, then pt-BR). Use a language switcher at the top of each doc and cross-links that offer both languages (see [docs/README.md](docs/README.md) — Documentation policy). **After editing any .md file:** run `uv run python scripts/fix_markdown_sonar.py` and `uv run pytest tests/test_markdown_lint.py -v -W error` so SonarQube/markdownlint rules (e.g. MD060 table style) pass.
- **Secrets:** Never commit credentials or real PII. Use `.env` or `config.local.yaml` (both are in `.gitignore`) and redact in issues/PRs.

## CI and dependency hygiene

- **CI:** GitHub Actions run tests and `uv pip audit` on push/PR to `main` (or `master`). When SonarQube/SonarCloud is enabled (see [docs/TESTING.md](docs/TESTING.md)), address reported issues so the quality gate stays green.
- **Dependencies:** The source of truth for libraries is **`pyproject.toml`** (uv toolchain); pip and **`requirements.txt`** are derivative. Declare all runtime and dev dependencies in **`pyproject.toml`**. When you add or change deps, run `uv sync` and regenerate the lockfile with `uv pip compile pyproject.toml -o requirements.txt`. Do not edit `requirements.txt` by hand for version changes.
- **Dependabot / automation:** When applying a dependency update (e.g. from a Dependabot PR), update **`pyproject.toml`** first (bump the minimum version for that package), then run `uv pip compile pyproject.toml -o requirements.txt` and commit both files. Merge dependency PRs only after CI (tests and audit) pass.

## Deployment and production

- Use a dedicated config file (e.g. via `CONFIG_PATH`) and never commit it. Run `uv pip audit` before deploying.
- For public or multi-tenant use, put the API behind a reverse proxy (HTTPS, rate limiting, auth) as described in the README.

## See also

- **[docs/TESTING.md](docs/TESTING.md)** ([pt-BR](docs/TESTING.pt_BR.md)) — Test modules, CI, SonarQube.
- **[docs/TOPOLOGY.md](docs/TOPOLOGY.md)** ([pt-BR](docs/TOPOLOGY.pt_BR.md)) — Application topology (modules, classes, data flow).
- **[docs/COMMIT_AND_PR.md](docs/COMMIT_AND_PR.md)** ([pt-BR](docs/COMMIT_AND_PR.pt_BR.md)) — Commit and PR automation.
- **[docs/compliance-frameworks.md](docs/compliance-frameworks.md)** ([pt-BR](docs/compliance-frameworks.pt_BR.md)) — Compliance labels and extensibility.
- **[docs/COPYRIGHT_AND_TRADEMARK.md](docs/COPYRIGHT_AND_TRADEMARK.md)** ([pt-BR](docs/COPYRIGHT_AND_TRADEMARK.pt_BR.md)) — Copyright and trademark (making it official, registries). [NOTICE](NOTICE) for project notice.
- Full doc index: [docs/README.md](docs/README.md) ([pt-BR](docs/README.pt_BR.md)).

If you have questions, open a discussion or an issue. Thanks for contributing.
