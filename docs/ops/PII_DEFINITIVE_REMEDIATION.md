# PII and sensitive-history remediation — definitive operator runbook

**Português (Brasil):** [PII_DEFINITIVE_REMEDIATION.pt_BR.md](PII_DEFINITIVE_REMEDIATION.pt_BR.md)

**Audience:** Maintainer / operator with push access to `FabioLeitao/data-boar`, GitHub CLI or browser, and `git-filter-repo` installed.

**Goal:** Align **canonical `main`**, **Git history**, **CI `pii_history_guard --full-history`**, and **all clones** (dev PC, lab hosts, collaborators) so sensitive literals do not remain reachable in public Git blobs or commit messages.

**What automation cannot do for you:** Delete **other people’s forks**, purge **third-party caches**, or prove **Wayback** copies are gone. Those require GitHub support, fork owners, or time.

---

## A. Preconditions

1. **Backup mindset:** `scripts/run-pii-history-rewrite.ps1` creates a **mirror** under the parent of the repo before rewriting. Keep it until `main` is green and you have re-cloned everywhere.
2. **Tools:** `git`, `git-filter-repo` on PATH, `uv` (for tests), network access to `origin`.
3. **Clean working tree** before a history rewrite: commit or stash all intentional changes.

---

## B. Same-day hygiene (no history rewrite)

Use when you only need to align **current tracked files** and **incremental** guard:

```powershell
cd C:\path\to\data-boar
git fetch origin
git pull origin main
uv sync
uv run pytest tests/test_pii_guard.py tests/test_talent_public_script_placeholders.py tests/test_talent_ps1_tracked_no_inline_pool.py -q
uv run python scripts/pii_history_guard.py
```

**Lab Linux** (no `uv` on PATH): `python3 -m pytest …` if pytest is installed, or install `uv` per project docs.

---

## C. Full history rewrite (destructive on remote after push)

Run **only** after merging guard + replacement rules in `main` (this repo ships `scripts/filter_repo_pii_replacements.txt`).

1. **Commit** all intended tracked changes (guards, replacements, docs).
2. From repo root:

```powershell
.\scripts\run-pii-history-rewrite.ps1
```

3. Inspect the reported **`data-boar-history-rewrite-*`** path. If `pytest` and `pii_history_guard --full-history` are green there, you may push:

```powershell
.\scripts\run-pii-history-rewrite.ps1 -Push
```

4. **Immediately after any public force-push:**
   - **Delete stale remote branches** on GitHub that still point at **pre-rewrite** SHAs (or CI / `pii_history_guard --full-history` may still see old blobs).
   - **Every clone** (yours, lab, Contributor-A):  

```bash
git fetch origin
git reset --hard origin/main
git fetch --prune
```

5. **Forks (e.g. collaborator):** Owner must **delete the fork** or **re-fork / reset** from current `main`. You cannot fix their object database from upstream.

---

## D. Verification matrix (after push)

| Check | Command |
| ----- | ------- |
| Index + working tree guards | `uv run pytest tests/test_pii_guard.py -q` |
| Talent script placeholders | `uv run pytest tests/test_talent_public_script_placeholders.py tests/test_talent_ps1_tracked_no_inline_pool.py -q` |
| Full history | `uv run python scripts/pii_history_guard.py --full-history` |
| Optional local seeds | Keep **private** seeds in `docs/private/security_audit/PII_LOCAL_SEEDS.txt` (not in Git). Use `git log --all -S "…"` per line only on maintainer machine — see [PII_VERIFICATION_RUNBOOK.md](PII_VERIFICATION_RUNBOOK.md). |

---

## E. Editing replacement rules

- **File:** `scripts/filter_repo_pii_replacements.txt`
- **Format:** `git filter-repo` text replacements; lines starting with `#` are comments; `regex:…==>…` for patterns.
- **After editing:** Run **Section C** again (rewrite + tests) before the next force-push.

---

## F. Related documents

- [GITHUB_FORK_CLONE_VISIBILITY_AND_OPERATOR_AUDIT.md](GITHUB_FORK_CLONE_VISIBILITY_AND_OPERATOR_AUDIT.md) — what GitHub can list (forks) vs what it **cannot** (per-user `git clone`); minimal operator checklist.
- [PII_VERIFICATION_RUNBOOK.md](PII_VERIFICATION_RUNBOOK.md) — cadence and manual grep.
- [COMMIT_AND_PR.md](COMMIT_AND_PR.md) — no sensitive narratives in PR/commit text.
- [ADR 0020](../adr/0020-ci-full-git-history-pii-gate.md) — CI full-history gate.
