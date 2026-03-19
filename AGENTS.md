# Agent / assistant notes (Cursor, Copilot, etc.)

- **Git & PR state:** The model does **not** see GitHub or your local repo unless a command runs in-session. Before advising **merge**, **next steps after a PR**, or sharing a **PR number/URL**, refresh state (`git fetch`, `git pull` on `main`, and/or `gh pr view`). See **`.cursor/rules/git-pr-sync-before-advice.mdc`** (always applied) and **`CONTRIBUTING.md`** → *PR state and agent advice*.
- **Automation:** Prefer **`scripts/check-all.ps1`**, **`scripts/commit-or-pr.ps1`**, and related helpers — **``.cursor/skills/token-aware-automation/SKILL.md`**.
- **Plans:** Single source of truth for backlog sequencing is **`docs/plans/PLANS_TODO.md`** (English-only history); operator runbooks live under **`docs/ops/`** (EN + pt-BR).
