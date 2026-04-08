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
- [COLLABORATION_TEAM.md](../COLLABORATION_TEAM.md) — contributor fork / PR flow ([pt-BR](../COLLABORATION_TEAM.pt_BR.md)).

---

## G. What is already in this repository (engineering closure)

The following are **in `main`** as part of the PII hygiene arc (do not redo unless you change policy):

| Item | Location / behavior |
| ---- | -------------------- |
| Index + path scan | `tests/test_pii_guard.py` — tracked files; allows `docs/private.example/` etc. per prefixes |
| Full-history scan | `scripts/pii_history_guard.py` — skips added lines under `docs/private.example/`; LinkedIn placeholder allows Markdown backtick; SSH regex ignores `user@myserver.example.com` style placeholders |
| Talent CLI placeholders | `tests/test_talent_public_script_placeholders.py`, `tests/test_talent_ps1_tracked_no_inline_pool.py` |
| `filter-repo` rules file | `scripts/filter_repo_pii_replacements.txt` — repaired and valid for `--replace-text` / `--replace-message` |
| Rewrite automation | `scripts/run-pii-history-rewrite.ps1` — optional new rewrite if rules change |
| CI | Workflows run `pii_history_guard --full-history` after tests (see ADR 0020) |
| Ops docs | This file, [GITHUB_FORK_CLONE_VISIBILITY_AND_OPERATOR_AUDIT.md](GITHUB_FORK_CLONE_VISIBILITY_AND_OPERATOR_AUDIT.md), cross-links from [PII_VERIFICATION_RUNBOOK.md](PII_VERIFICATION_RUNBOOK.md) |

**Not a substitute for:** your private backups, external review (e.g. WRB), or collaborator fork deletion.

---

## H. Operator checklist — do these (assumed required until done)

Run in order where applicable. **No step below is optional** if you want organizational closure, not only “green tests on one laptop.”

### H.1 Full gate on your Windows dev PC (canonical)

```powershell
cd C:\path\to\data-boar
git fetch origin
git pull origin main
.\scripts\check-all.ps1
```

If anything fails, fix or open a scoped PR before declaring release hygiene complete.

### H.2 Confirm CI on GitHub

1. Open `https://github.com/FabioLeitao/data-boar/actions`
2. Confirm the latest workflow run on **`main`** is **green** (all jobs).

### H.3 Lab and secondary clones (machines you control)

On **each** host where `data-boar` is cloned (e.g. LAB-NODE-02, LAB-NODE-04, LAB-NODE-01, LAB-NODE-03 when reachable):

```bash
cd ~/Projects/dev/data-boar   # or your actual path
git fetch origin
git reset --hard origin/main
git fetch --prune
```

Then run the **same** guards as **Section D** using `python3` if `uv` is missing:

```bash
python3 scripts/pii_history_guard.py --full-history
```

Install `uv` on those hosts when practical so `check-all` or equivalent matches Windows.

### H.4 Collaborator fork (known public fork)

1. List forks:

```bash
gh api repos/FabioLeitao/data-boar/forks --paginate --jq '.[] | {owner: .owner.login, full_name, pushed_at, updated_at}'
```

2. **You** message the fork owner: upstream history was rewritten / guards updated; they must **delete the fork** or **re-sync** from current `main` (see [GITHUB_FORK_CLONE_VISIBILITY_AND_OPERATOR_AUDIT.md](GITHUB_FORK_CLONE_VISIBILITY_AND_OPERATOR_AUDIT.md) and [COLLABORATION_TEAM.md](../COLLABORATION_TEAM.md)).

3. You **cannot** delete their fork from your account.

### H.5 GitHub UI sweep (issues, PRs, discussions)

Automation does **not** rewrite issue/PR bodies. **Manually** search the repo on GitHub for patterns you care about (names, paths, case keywords) and redact or open a follow-up issue. Keep **no** sensitive narrative in public issue text going forward ([COMMIT_AND_PR.md](COMMIT_AND_PR.md)).

### H.6 External review (WRB or similar)

- Use **tracked** runbooks and product docs as evidence.
- Do **not** paste dossier content, private seeds, or LAN details into public issues or review forms.

### H.7 Private backups and application state

- Compare **your** offline backups to current behavior **outside** this repo; no assistant or CI can audit disks you do not attach here.

### H.8 Temporary clone directories (hygiene)

- Remove any **temporary** clone dirs you created for fork inspection (e.g. under `%TEMP%` / `/tmp`) when disk hygiene matters.

### H.9 Optional: `clean-slate.sh` on lab (LAB-NODE-02)

If you use `~/clean-slate.sh`: it is **destructive** (removes local `data-boar` then re-clones). Run only when you accept full re-download and seed-driven `git grep` cost. Ensure `~/.config/PII/PII_LOCAL_SEEDS.txt` exists before relying on that script.

---

## I. Cannot be completed without you (hard limits)

| Limit | Why |
| ----- | --- |
| Delete or reset **someone else’s fork** | GitHub permissions |
| **List of all `git clone` users** | Not exposed by GitHub for public repos |
| Prove **Wayback** / search cache / third-party mirror is clean | Out of repo scope |
| **WRB** outcome | Human process |
| Verify **private backup** bytes | Physical / vault access |
| **LAB-NODE-03** (or any host) when offline | Network / power |
| **Legal / HR** narrative | Not in this runbook |
