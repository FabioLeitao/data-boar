# Quality workflow: recommendations and extra layers

This document suggests **additional layers** (tools, habits, and workflow) to keep the app working safely, readable, and to reduce toil, rework, and refactoring. Use it as a checklist; adopt incrementally. What you already have is in [TESTING.md](TESTING.md), [SECURITY.md](../SECURITY.md), and the Cursor rule/skill (`.cursor/rules/quality-sonarqube-codeql.mdc`, `.cursor/skills/quality-sonarqube-codeql/SKILL.md`).

**Already in place:** Ruff runs in CI (`uv run ruff check .`); `pyproject.toml` has `extend-exclude` for legacy dirs (`db`, `scanners`, `utils`, `logging_custom`). Run `uv run ruff check .` before PR. Optional: `uv run pre-commit install` so Ruff runs on commit (see `.pre-commit-config.yaml`).

## What you already have (baseline)

- **Tests:** Full pytest suite with `-W error`; SonarQube-style tests (S3981, S3776, S4423, S5706, S1192, etc.), security tests (SQL injection, path traversal, safe_load), markdown lint (including `.cursor/`).
- **CI:** Tests + `pip-audit` on every push/PR; optional SonarQube when `SONAR_TOKEN` is set; CodeQL in a separate workflow.
- **Cursor:** Rule and skill so the agent avoids SonarQube/CodeQL violations and runs quality tests after editing Python/markdown.
- **Docs:** CONTRIBUTING (release checklist, audit, min versions), SECURITY.md, TESTING.md, deploy hardening.

---

## Recommended layers (prioritised)

### 1. Run Ruff in CI (high value, low effort)

**Why:** Ruff catches style issues, unused imports, and many bug-prone patterns before they reach main. The PR template says "No new linter/format issues" but Ruff is not run in CI, so it's easy to forget.

## What to do (Ruff in CI):

- Add a **lint** job (or step) in `.github/workflows/ci.yml` that runs:
- `uv run ruff check .` (and optionally `uv run ruff format --check .`).
- Keep Ruff config in `pyproject.toml` (you already have `[tool.ruff.lint.per-file-ignores]`); add a `[tool.ruff]` section with `target-version`, `line-length`, and select rule sets if you want consistency.
- Update CONTRIBUTING and the quality rule/skill: "Before PR, run `uv run ruff check .` (and fix or adjust config)."

**Prevents:** Drift in style, unused code, many simple bugs; reduces review toil and post-merge fixes.

---

### 2. Pre-commit hooks (optional but strong)

**Why:** Catches issues **before** push so CI fails less often and you avoid "run after your own tail" on style/lint.

## What to do (pre-commit):

- Add [pre-commit](https://pre-commit.com/) (e.g. in dev dependency group) and a `.pre-commit-config.yaml` with:
- `ruff` (check + format),
- `markdownlint` or a hook that runs `scripts/fix_markdown_sonar.py` / `pytest tests/test_markdown_lint.py`,
- optionally a "fast" pytest subset (e.g. `test_markdown_lint`, `test_sonarqube_python`, `test_security`) if fast enough.
- Document in CONTRIBUTING: "Install hooks with `pre-commit install`; they run on commit."

**Prevents:** Pushing commits that will fail CI; keeps local and CI in sync.

---

### 3. Bandit (security linter) in CI or pre-commit

**Why:** Complements CodeQL and SonarQube with Python-specific checks: hardcoded passwords, `assert` in production, unsafe functions (e.g. `pickle`, `yaml.load`), etc.

## What to do (Bandit):

- Add `bandit` to dev dependencies; run `uv run bandit -r api core config connectors -ll` in CI (or in pre-commit). Exclude tests if too noisy; use a `bandit.yaml` or `[tool.bandit]` in `pyproject.toml` to skip false positives.
- Fix or explicitly allow findings; over time add Bandit to the quality rule/skill ("run bandit after security-sensitive changes").

**Prevents:** Common security anti-patterns that tests might not cover.

---

### 4. Semgrep (optional)

**Why:** Pattern-based SAST; custom and community rules for security and bug patterns. Overlaps with CodeQL and SonarQube but can catch project-specific patterns (e.g. "no raw SQL with f-strings").

## What to do (Semgrep):

- Add Semgrep to CI (or run locally before PR) with a config that enables relevant Python rules; add custom rules for your conventions (e.g. session_id, config keys). Free for open source.

**Prevents:** Custom bad patterns and some vulnerabilities CodeQL might not flag.

---

### 5. Type checking with mypy (gradual)

**Why:** Types make refactors safer and reduce "it worked until we changed X" regressions. Adopting gradually (e.g. `--no-error-summary` for a while, or only for `api/` and `core/`) keeps effort bounded.

## What to do (mypy):

- Add `mypy` to dev deps; add `[tool.mypy]` in `pyproject.toml` with a strictness level you can live with (e.g. `disallow_untyped_defs = false` at first). Run `uv run mypy api core` in CI (or a separate job that is allowed to fail initially). Tighten over time.

**Prevents:** Type-related bugs and makes refactoring less risky.

---

### 6. MD029 and the fix script (reduce rework)

**Why:** `scripts/fix_markdown_sonar.py` applies MD029 (ordered list style 1/1/1), which converts all list numbers to `1.`. That can break **semantic** numbering (e.g. "Step 1, 2, 3" becomes "1, 1, 1") and forces manual re-editing in many docs.

## What to do (MD029):

- Either: (a) disable MD029 in the fix script for lines that are clearly step lists (e.g. "1. … 2. … 3. …"), or (b) stop applying MD029 globally and rely on SonarQube reporting it only where you care, or (c) document "after running the fix script, restore semantic numbering in step lists" in CONTRIBUTING and in the markdown-lint rule.

**Prevents:** Repeated rework and confusion in docs after every markdown fix run.

---

### 7. Architecture / decision records (reduce wrong refactors)

**Why:** When "why" is written down, refactors are less likely to reintroduce the same mistakes or toil.

## What to do (ADRs):

- Keep a short **architecture** section in TECH_GUIDE or a dedicated `docs/architecture.md`: main components (API, engine, connectors, report), data flow, and where config/secrets live.
- For larger decisions, add one-page **ADRs** (Architecture Decision Records) under e.g. `docs/adr/` (e.g. "Why we use parameterized queries only", "Why session_id is validated with this regex"). Link from SECURITY.md or CONTRIBUTING where relevant.

**Prevents:** Refactoring that accidentally weakens security or duplicates past mistakes.

---

### 8. SBOM and supply chain (optional)

**Why:** pip-audit already addresses known vulnerabilities; a formal **Software Bill of Materials** helps with compliance and incident response.

## What to do (SBOM):

- Generate an SBOM (e.g. with `cyclonedx-py` or `syft`) as a CI artifact or on release; store or publish it. Document in SECURITY.md or release process.

**Prevents:** Blind spots in dependency inventory and slower response to supply-chain issues.

---

### 9. PR checklist and branch protection

**Why:** Ensures nothing merges without tests and audit; reduces "fix in main" and rework.

## What to do (branch protection):

- In GitHub: **Branch protection** on `main` (and `master` if used) requiring status checks (**Test**, **Dependency audit**, and **Lint**) to pass before merge. Maintainers: enable this in repo settings so PRs cannot merge with failing CI.
- In the **PR template**, make the checklist explicit: tests pass, `ruff check` clean, docs updated, security-sensitive changes considered. Reference CONTRIBUTING and TESTING.md.

**Prevents:** Merging broken or insecure code and follow-up fix commits.

---

### 10. Cursor rules and skills (keep extending)

**Why:** Rules and skills guide the agent so fewer violations are introduced in the first place; tests remain the enforcement.

## What to do (rules and skills):

- When you add a **new** quality or security check (e.g. Ruff in CI, Bandit, a new Sonar rule): update the **quality rule** and **skill** with the new command and what to avoid. Keep TESTING.md and this doc in sync.
- Consider a short **rule** that fires when editing config or connector code: "Use parameterized queries; no secrets in logs; run security tests after change."

**Prevents:** Regressions and bad habits from creeping in during daily edits.

---

## Summary table

| Layer               | Purpose                         | Effort | Prevents                            |
| ------------------  | ------------------------------- | ------ | ---------------------------------   |
| Ruff in CI          | Style, imports, simple bugs     | Low    | Drift, toil, many small regressions |
| Pre-commit          | Catch before push               | Low    | Failed CI, rework                   |
| Bandit              | Python security patterns        | Low    | Hardcoded secrets, unsafe APIs      |
| Semgrep             | Custom + community SAST         | Medium | Extra vulnerability/bug patterns    |
| mypy                | Type safety                     | Medium | Refactor bugs, wrong types          |
| MD029 / fix script  | Avoid doc rework                | Low    | Repeated manual numbering fixes     |
| ADRs / architecture | Record "why"                    | Low    | Wrong refactors, repeated mistakes  |
| SBOM                | Supply chain visibility         | Low    | Missing deps in incident response   |
| Branch protection   | Block bad merges                | Low    | Merging broken or insecure code     |
| Extend rules/skills | Guide agent on new checks       | Low    | New violations as you add tools     |

---

## What you might not be paying attention to yet

1. **Ruff not in CI** – So "no linter issues" is not enforced; adding Ruff to CI closes that gap.
1. **MD029 and semantic lists** – The fix script can overwrite intentional 1/2/3 numbering; either refine the script or document the restore step.
1. **Pre-commit** – Without it, issues are only found at push/CI; hooks reduce back-and-forth.
1. **Types** – No static typing yet; mypy (even gradual) would reduce refactor risk.
1. **"Why" in docs** – ADRs and a short architecture section help avoid refactors that undo past decisions.
1. **Branch protection** – If not already set, requiring Test + Audit (and Lint when added) prevents accidental merges.

Adopt what fits your team and timeline; the biggest quick wins are **Ruff in CI**, **branch protection**, and **MD029/fix-script** handling. Then add pre-commit and Bandit; consider mypy and Semgrep as you grow.
