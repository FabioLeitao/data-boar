# Maintenance: single front of work (after spring clean)

**Intent:** After a burst of parallel branches and PRs, keep **one active development front** when possible: one open PR per coherent slice, merge, then start the next. Side work is allowed when the priority matrix demands it (e.g. security, CI), but each side track should close with merge or explicit supersede.

**Related:** `AGENTS.md` (dangling open PR guard), `docs/plans/PLANS_TODO.md` (recommended sequence), [PYTHON_UPGRADE_PLAYBOOK.md](PYTHON_UPGRADE_PLAYBOOK.md).

---

## Slice S1 — CI matches supported Python minors (done in same PR as this doc update)

- **Goal:** Run `pytest` on **Python 3.12 and 3.13** in GitHub Actions (`fail-fast: false`), aligned with `CONTRIBUTING.md` / `SECURITY.md` support claims.
- **Type:** `workflow` + `documentation` (CI YAML + `docs/TESTING*.md`).
- **Supersedes:** Open PR #79 (`pr/ci-python-313-matrix-playbook`) once this lands — close #79 with a comment pointing to the replacement PR; delete remote branch `pr/ci-python-313-matrix-playbook`.
- **Extras (logical):** Lint/audit/Sonar stay on a single Python (3.12) to limit minutes unless we later widen intentionally.

---

## Slice S2 — Prune merged remote heads

- **Goal:** Remove `origin/*` branch tips whose PRs are merged and whose commits are already on `main` (no resumable delta).
- **Type:** `workflow` (repo hygiene only).
- **Safety:** Do not delete branches that still have unique commits vs `main` without explicit review.

---

## Slice S3 — Legacy `origin/feature/*` and `origin/commit` ✅ completed

- **Goal:** Classify each: archive, resume as a new branch from `main`, or delete if fully superseded.
- **Outcome (verified):** Tips of `origin/commit`, `origin/feature/agent-review-style-pr-automation`, `origin/feature/agent-review-style-pr-automation-2`, and `origin/feature/release-1.4.0-completed-plans` were **already ancestors of `main`** (no commits ahead). **No resumable work** — safe disposal only.
- **Action taken:** Remote branches **deleted** on `origin` after `git merge-base --is-ancestor` + `rev-list --count main..branch` = 0.
- **If similar branches reappear:** Re-run the same checks before delete; do not prune if `aheadOfMain > 0` without review.

---

## Slice S4 — Optional maintenance aligned to `PLANS_TODO.md`

Pick **one** per session when CI is green:

| Track | Aligns to | Notes |
| ----- | --------- | ----- |
| `pr/docker-scout-high-slice` | Order **–1b** (Docker Hub Scout) | Rebase on `main`, refresh base image, Scout + `check-all`. |
| `pr/deps-security-refresh` | Dependabot / security hygiene | Rebase, resolve lock conflicts, full test gate. |
| `pr/api-report-path-hardening` | Security / API hardening | Diff vs `main` first; may already be superseded by merged slices. |

Do **not** stack these in one PR unless they are truly the same incident (e.g. one Scout round-trip).

---

## Operating rule (minimal open fronts)

1. `gh pr list --state open` before starting a new slice.
2. Prefer **merge or close** existing open PRs before opening another **workflow** PR.
3. Product features (`feat/*`) follow `PLANS_TODO.md` after maintenance gates are green.

*Last updated: S3 legacy remote prune + commit-type guidance in `AGENTS.md` / execution rule.*
