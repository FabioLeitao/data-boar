# Plan: Readiness and operations (meta / “see the forest”)

**Status:** Discovery and checklist (not a delivery plan with phases)  
**Purpose:** Capture aspects that are easy to miss when focused on feature plans—so you can decide what to formalise, automate, or document next. No obligation to implement everything; use as a prioritised checklist.

---

## 1. Do you need a custom MCP?

**Recommendation: No, unless you have a specific gap.**

- **What you have:** Cursor + Git + CI (tests, Ruff, pip-audit, Sonar when configured) + existing MCPs (e.g. browser, GitKraken) + good docs and plans. That already covers most development and review workflows.
- **When a custom MCP might be worth it:** You need to automate something Cursor and existing tools don’t cover—e.g. calling an internal API, driving a proprietary system, or generating project-specific reports from your repo. Building and maintaining an MCP has a cost; only add one if the benefit is clear (e.g. “we run this check every release and it saves us X hours”).
- **Conclusion:** You’re fine without a custom MCP for current goals. Revisit if a concrete automation need appears.

---

## 2. Workflow and automation (quick wins)

| Item | Status / suggestion |
|------|---------------------|
| **Ruff in CI** | Done (lint job in `ci.yml`). |
| **Pre-commit** | Present (Ruff). Optional: add `ruff format --check` or markdown lint if you want format enforced on commit. |
| **Single “check-all” script** | Optional: a script (e.g. `scripts/check_all.sh` or `make check`) that runs `uv sync`, `uv run ruff check .`, `uv run pytest -v -W error`, `uv run pip-audit` so one command approximates CI locally. Reduces “it passed on my machine” gaps. |
| **Release checklist** | In CONTRIBUTING (audit, docs, secrets, lockfile). Optional: add “Update CHANGELOG or release notes” if you introduce a CHANGELOG. |
| **QUALITY_WORKFLOW_RECOMMENDATIONS.md** | Already lists Bandit, Semgrep, mypy, SBOM. Adopt incrementally when you want an extra safety layer; not required for “being set.” |

---

## 3. “Forest” aspects (what we might still need to understand or prepare for)

These are areas that often get less attention than feature plans but matter for long-term health and operations. Treat as a **checklist to discuss and prioritise**, not a mandatory to-do list.

### 3.1 Release and versioning

- **Changelog / release notes:** You have `docs/releases/` with versioned notes. Is there a single CHANGELOG.md (or “releases” as the changelog) and a habit of updating it on every release? If not, consider a lightweight rule: “every tagged release has an entry in docs/releases/ or CHANGELOG.”
- **Compatibility and deprecation:** When you change config or API, do you document “since when” and “replacement”? Optional: a short “Compatibility” section in CONTRIBUTING or USAGE (e.g. “we avoid breaking config keys; when we deprecate, we document for at least one minor version”).

### 3.2 Security response

- **Vulnerability reporting:** SECURITY.md already explains “do not open public issue with exploit” and “maintainers will acknowledge and investigate.” Optional: add an explicit expectation (e.g. “we aim to acknowledge within 5 working days and to fix or document within 30 days for high/critical”) if you want a clear SLA for yourselves and reporters.
- **Dependency alerts:** Dependabot + pip-audit + lockfile already reduce risk. Optional: document in CONTRIBUTING or SECURITY “we treat Dependabot security PRs as P0 and aim to merge or respond within X days.”

### 3.3 Operations and runbooks

- **OBSERVABILITY_SRE.md** already mentions runbooks and points to GET /status, healthchecks, and deploy docs. Optional: a single **Operator runbook** (one-pager or short doc) that says: “If the app is down: 1) Check /health and logs, 2) Check config and CONFIG_PATH, 3) Check disk and SQLite path, 4) Restart or scale; if a scan hangs: …” so someone unfamiliar can follow steps.
- **Backup and restore:** Self-upgrade plan mentions backup; do you have a minimal “what to backup (config, SQLite, report dir) and how to restore” written down for deployers?

### 3.4 Compliance and evidence (you are an audit/compliance tool)

- **Self-audit:** Can you briefly describe “how we prove our own compliance” (e.g. access control to config/repo, audit trail for config changes, no secrets in logs, dependency audit)? Optional: a short “Compliance and evidence” subsection in SECURITY or a dedicated doc for deployers who need to show that the tool itself is managed in a compliant way.
- **Data retention:** Do you document or configure how long reports and SQLite data are kept, and who can delete them? Optional: mention in USAGE or deploy docs “consider retention policy for report.output_dir and sqlite_path.”

### 3.5 Onboarding and bus factor

- **New contributor:** Can someone new go from “clone repo” to “I ran the app and the tests and I know where to change X” using only README, CONTRIBUTING, USAGE, and TESTING? Optional: a short “Onboarding” checklist in CONTRIBUTING (“1. Clone, 2. uv sync, 3. Copy config example, 4. uv run pytest, 5. Read PLANS_TODO for current work”).
- **Key person dependency:** If one person holds most context, consider a “handover” or “key decisions” doc (why we chose X, where the traps are) so the project isn’t blocked if that person is unavailable.

### 3.6 Dependencies and upgrades

- **Python and platform:** You already support 3.12+ and document it. Optional: a short “We support Python 3.12 and 3.13 on Linux, macOS, Windows; we will announce deprecation of a version at least one minor release ahead” in README or CONTRIBUTING.
- **Lockfile and refresh:** Already documented (uv.lock, refresh on release and when applying Dependabot). No change needed unless you want a written “upgrade policy” (e.g. “we refresh lockfile at least every N months or when a critical CVE appears”).

---

## 4. How to use this plan

- **Not a delivery plan:** This file does not define phases or to-dos to “complete” in the same way as PLAN_SECRETS_VAULT or PLAN_NOTIFICATIONS. It’s a **readiness and operations checklist**.
- **Sync with PLANS_TODO:** If you decide to implement something (e.g. “Operator runbook” or “CHANGELOG discipline”), you can add a single line or a small section to PLANS_TODO or to CONTRIBUTING, and optionally link back here.
- **Revisit when:** You do a release, onboard someone new, or get an audit request. Then you can ask: “Do we have what we need for release/onboarding/compliance?” and use this doc as a guide.

---

*Last updated: added as a meta/readiness checklist; no implementation to-dos.*
