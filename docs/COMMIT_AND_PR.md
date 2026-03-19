# Commit and PR workflow (Agent Review Panel–style)

**Português (Brasil):** [COMMIT_AND_PR.pt_BR.md](COMMIT_AND_PR.pt_BR.md)

When you ask the agent to **preview**, **commit locally**, or **create a PR** with a short description and bullet points, it uses the same flow as the old Cursor “Agent Review Panel”: review changes, optionally select files, then choose commit or open PR in the browser with the form pre-filled. Before pushing, it **fetches** and **rebase-pulls** if the branch is behind the remote so your preferred workflow (linear history, no accidental overwrites) is preserved.

## What the agent does when you ask

- **“Preview”** or **“Show me what would be committed”**:
- Lists the files that would be included (excluding `audit_results.db`).
- Shows a short diff summary (`git diff --stat`).
- Shows the **proposed commit title and bullet-point body** (from the agent or your message).
- **Does not stage or commit.** You can then say “Commit locally” or “Create PR” to proceed.

- **“Commit locally”** (optionally: “… with message: …”):
- Stages all changed files **except** `audit_results.db`.
- Builds a **short title** and **bullet-point body** from the changes (or uses what you said).
- Runs `git commit -m "<title>" -m "<body>"` on the current branch.

- **“Create a PR”** (optionally: “… with description: …” or “… on branch X”):
- If you have **uncommitted changes**: stages (optionally only `-IncludeFiles`), commits with the given title/body.
- If you have **no uncommitted changes but have local commits not yet pushed**: does not create a new commit; uses those existing local commits for the PR.
- **Before pushing:** runs **`git fetch origin`** and, if your branch is **behind** the remote, runs **`git pull --rebase origin <branch>`** so your local commits sit on top of the latest remote (avoids divergent history and failed pushes). If rebase hits conflicts, the script exits and asks you to resolve and run `git rebase --continue` or `git rebase --abort`.
- If you asked for a specific branch (e.g. “on branch `feature/xyz`”), creates or checks out that branch before committing (when there are changes).
- **Pushes** the current branch to `origin` via your existing SSH credentials (all local commits are included).
- **Opens the PR in your default browser** with the title and description **pre-filled**:
    - Uses **`gh pr create --title ... --body-file ... --base <default> --web`** so the GitHub “New pull request” form opens with title and body already set; you review and click “Create pull request.”
    - If `gh` is not available: opens the GitHub **compare** page so you can create the PR there in your logged-in session.

## Selecting which files to include

You can limit the commit/PR to specific files with **`-IncludeFiles`** (comma-separated or array). The script then stages only those paths (and their children if you pass a directory).

- **Preview first:** run with `-Action Preview` to see all candidate files and the proposed title/body.
- **Then either:** run again with `-Action Commit` or `-Action PR` and, if you want to include only some files, add:

  `-IncludeFiles "path1","path2"` (e.g. `-IncludeFiles "README.md","api/routes.py"`).

## Doing it yourself

### Preview: file list vs commit message

**`-Action Preview` without `-Title` / `-Body`** only guarantees an accurate **list of files** and **`git diff --stat`**. The script **does not infer** a commit message from your changes.

- **Before (confusing):** the script used **hardcoded example** defaults (e.g. “Update: security and docs” / CSP bullets) so Preview looked like a real proposal — it was not.
- **Now:** if you omit `-Title`, Preview prints a **yellow NOTE** and shows “(not set)”. You must pass **`-Title`** and usually **`-Body`** for **Commit** or **PR** (Commit **fails** without a title).

### Commands

From the repo root (PowerShell):

```powershell
# Preview only (no commit) – see files; message is NOT auto-generated (see note above)
.\scripts\preview-commit.ps1
# Optional: preview the exact title/body you will use for Commit/PR
.\scripts\commit-or-pr.ps1 -Action Preview -Title "Your title" -Body "Bullet one`nBullet two"

# Commit only (example: FN reduction + commit-or-pr script)
$body = @"
- MEDIUM threshold: sensitivity_detection.medium_confidence_threshold (loader + detector + engine)
- Suggested review: core/suggested_review, SQL persist_low_id_like_for_review, Excel sheet
- commit-or-pr: empty default title; Preview NOTE; PR when already pushed requires -Title
- Docs: SENSITIVITY_DETECTION, USAGE, TECH_GUIDE, PLANS_TODO, COMMIT_AND_PR; detection merge fix in loader
"@
.\scripts\commit-or-pr.ps1 -Action Commit -Title "feat: FN reduction slice + commit-or-pr message clarity" -Body $body

# Create PR on current branch (commit, push, open PR in default browser for approval)
.\scripts\commit-or-pr.ps1 -Action PR -Title "Your short title" -Body "Bullet one`nBullet two"

# Create PR but include only selected files
.\scripts\commit-or-pr.ps1 -Action PR -IncludeFiles "README.md","scripts/commit-or-pr.ps1" -Title "Your title" -Body "Bullets..."

# Create PR on a new or existing branch
.\scripts\commit-or-pr.ps1 -Action PR -Branch "feature/my-change" -Title "Your title" -Body "Bullets..."

# Create PR and run the test suite before pushing (no push if tests fail)
.\scripts\commit-or-pr.ps1 -Action PR -Title "Your title" -Body "Bullets..." -RunTests

# Create PR with body from a file (avoids escaping multi-line body in the shell)
.\scripts\create-pr.ps1 -Title "Your title" -BodyFilePath "path\to\body.txt"
.\scripts\create-pr.ps1 -Title "Your title" -BodyFilePath $env:TEMP\pr-body.txt -RunTests
```

- **Push** uses your normal Git remote and SSH keys. PR **always pushes the current branch to origin** so the central repo (data-boar) has the full progress and history.
- **Browser**: With `gh` installed and authenticated, the PR form opens with title and description filled in; you only need to confirm and click “Create pull request.”

## Which repository to use (data-boar only)

- **`origin`** points to **FabioLeitao/data-boar** — this is the **only** repo you push to and open PRs in. All new work and branding live here.
- A remote named **`python3-lgpd-crawler-legacy-and-history-only`** (the old python3-lgpd-crawler repo) is kept for **legacy history and fetch only**. Do **not** push to it; push is disabled so accidental pushes fail safely.
- When you open the PR in the browser (compare page or `gh pr create --web`), ensure:
- **Base repository:** `FabioLeitao/data-boar`
- **Base branch:** `main`
- **Compare/head:** your branch (e.g. `2026-03-14-3i1y`) in **data-boar**
- If GitHub suggests “you may need to fork,” it usually means the **base** dropdown is set to another repo (e.g. the old one). Change the base to **data-boar** and base branch to **main** so the PR is “same repo” and no fork is needed.

## Requirements

- **Git** and (for PR) **SSH** or HTTPS push to GitHub.
- **GitHub CLI (`gh`)** and `gh auth login` for the best experience: PR form opens pre-filled in your browser. If `gh` is missing, the script still opens the compare page so you can create the PR manually.

## Notes

- The script **respects `.gitignore`**: it uses `git check-ignore` so only non-ignored paths are ever staged or committed (e.g. `audit_results.db`, `*.db-journal`, `.env.local`, reports/heatmaps, `__pycache__`, etc. are never included).
- The agent does **not** have access to your credentials; it runs `git` and `gh` in your environment, so your SSH and `gh auth` are used.

## Complete workflow: check, pre-commit, commit, describe, and safe synced PR

When you want to **check**, run **pre-commit**, **commit**, **describe**, and create a **safe, synced PR** using repo scripts (best for saving tokens and one source of truth), use these **concrete actions in order** from the repo root (PowerShell):

| Step | Goal | Command |
|------|------|--------|
| 0 | **Optional:** open Dependabot PRs + Docker Scout quickview (read-only; needs `gh`, optional Docker) | `.\scripts\maintenance-check.ps1` |
| 1 | **Check + pre-commit** (Ruff lint, format, markdown, full pytest in one run) | `.\scripts\check-all.ps1` |
| 2 | **Preview** (see what would be committed; no stage, no commit) | `.\scripts\preview-commit.ps1` |
| 3 | **Propose** a short commit title and bullet-point PR body from the file list and context | (you or the agent suggest title and body) |
| 4 | **Commit + describe + safe synced PR** (commit with title/body, run tests again, fetch+rebase if behind, push, open PR in browser) | `.\scripts\commit-or-pr.ps1 -Action PR -Title "Your title" -Body "Bullet1`nBullet2" -RunTests` |

For a **long PR body**, use:

- `.\scripts\create-pr.ps1 -Title "Your title" -BodyFilePath path\to\body.txt` (optionally add `-RunTests`; it defaults to on), or
- A one-off `.ps1` that sets `$Title` and `$Body` (e.g. here-string) and calls `commit-or-pr.ps1 -Action PR -Title $Title -Body $Body -RunTests`.

**Why this order:** One full gate before committing; one preview to confirm scope; one PR step that re-runs tests and syncs (fetch + rebase if behind) before push, so the PR is safe and synced. No ad-hoc `git add`/`git commit`/`git push` or raw `pytest`/`ruff` in between when these scripts cover the need.

**Documentation index** (all topics, both languages): [README.md](README.md) · [README.pt_BR.md](README.pt_BR.md).
