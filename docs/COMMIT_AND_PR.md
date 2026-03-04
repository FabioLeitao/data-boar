# Commit and PR workflow (Agent Review Panel–style)

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

From the repo root (PowerShell):

```powershell
# Preview only (no commit) – see files and proposed message
.\scripts\commit-or-pr.ps1 -Action Preview -Title "Your title" -Body "Bullet one`nBullet two"

# Commit only
.\scripts\commit-or-pr.ps1 -Action Commit -Title "Your short title" -Body "Bullet one`nBullet two"

# Create PR on current branch (commit, push, open PR in default browser for approval)
.\scripts\commit-or-pr.ps1 -Action PR -Title "Your short title" -Body "Bullet one`nBullet two"

# Create PR but include only selected files
.\scripts\commit-or-pr.ps1 -Action PR -IncludeFiles "README.md","scripts/commit-or-pr.ps1" -Title "Your title" -Body "Bullets..."

# Create PR on a new or existing branch
.\scripts\commit-or-pr.ps1 -Action PR -Branch "feature/my-change" -Title "Your title" -Body "Bullets..."
```

- **Push** uses your normal Git remote and SSH keys.
- **Browser**: With `gh` installed and authenticated, the PR form opens with title and description filled in; you only need to confirm and click “Create pull request.”

## Requirements

- **Git** and (for PR) **SSH** or HTTPS push to GitHub.
- **GitHub CLI (`gh`)** and `gh auth login` for the best experience: PR form opens pre-filled in your browser. If `gh` is missing, the script still opens the compare page so you can create the PR manually.

## Notes

- The script skips `audit_results.db` (local scan DB); it is listed in `.gitignore` and should not be committed.
- The agent does **not** have access to your credentials; it runs `git` and `gh` in your environment, so your SSH and `gh auth` are used.
