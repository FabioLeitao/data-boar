---
name: token-aware-automation
description: Use when deciding how to run lint, tests, or commit/PR. Prefer repo scripts (check-all, lint-only, quick-test, commit-or-pr and helpers) over ad-hoc commands to save tokens and keep behaviour consistent.
---

# Token-aware automation (scripts first)

When you need to **verify lint or tests**, or when the user asks to **commit, create a description, push, or create a PR**, use the repo scripts from the project root so behaviour is consistent and token use stays low.

## Which script to use (lint and tests)

| Goal | Script | When it saves tokens |
|------|--------|----------------------|
| Full gate before commit/PR | `.\scripts\check-all.ps1` | Single command = one round-trip |
| Tests only (no pre-commit) | `.\scripts\check-all.ps1 -SkipPreCommit` | Skips Ruff/markdown when you only care about tests |
| Lint/format only | `.\scripts\lint-only.ps1` | No pytest when you only changed docs, templates, or style |
| One test file or keyword | `.\scripts\quick-test.ps1 -Path tests/test_foo.py` or `-Keyword "content_type"` | Fewer tests = faster feedback and fewer tokens |

## Commit, push, and PR (use automation)

When the user asks to **commit**, **write a description**, **push to GitHub**, or **create a PR**, use the commit-or-pr workflow instead of raw `git add` / `git commit` / `git push`:

| Goal | Script | Notes |
|------|--------|--------|
| See what would be committed (no commit) | `.\scripts\preview-commit.ps1` or `.\scripts\commit-or-pr.ps1 -Action Preview` | Run first to list files and propose title/body. |
| Commit locally with title and body | `.\scripts\commit-or-pr.ps1 -Action Commit -Title "Short title" -Body "Bullet1`nBullet2"` | Body: use `` `n `` for newlines in PowerShell. |
| Create PR (commit if needed, push, open browser) | `.\scripts\commit-or-pr.ps1 -Action PR -Title "..." -Body "..." -RunTests` | Prefer `-RunTests` so tests run before push. |
| Create PR with body from file (avoids escaping) | `.\scripts\create-pr.ps1 -Title "Title" -BodyFilePath path\to\body.txt` | Write body to a temp file, then pass path; no here-string in shell. |
| One-off PR with predefined message | Create a small .ps1 that sets `$Title` and `$Body` (here-string) and calls `commit-or-pr.ps1 -Action PR -Title $Title -Body $Body -RunTests` | Same pattern as `scripts/do_pr.ps1`; avoids CLI escaping. |

## Complete workflow: check → pre-commit → commit → describe → safe synced PR

When the user wants to **check, pre-commit, commit, describe, and create a safe synced PR**, use these **concrete actions in order** (script-only, token-optimal):

| Step | Action | Script / command |
|------|--------|------------------|
| 1 | **Check + pre-commit** (lint, format, markdown, tests in one run) | `.\scripts\check-all.ps1` |
| 2 | **Preview** (see what would be committed; no commit) | `.\scripts\preview-commit.ps1` |
| 3 | **Propose** title and body from the file list and context | (you suggest a short title and bullet-point body) |
| 4 | **Commit + describe + safe synced PR** (commit, run tests, fetch/rebase if behind, push, open PR) | `.\scripts\commit-or-pr.ps1 -Action PR -Title "Title" -Body "Bullet1`nBullet2" -RunTests` |

For a **long PR body**, use one of:

- `.\scripts\create-pr.ps1 -Title "Title" -BodyFilePath path\to\body.txt` (body in file)
- A one-off .ps1 that sets `$Title` and `$Body` (here-string) and calls `commit-or-pr.ps1 -Action PR -Title $Title -Body $Body -RunTests`

**Why this order:** One full gate (`check-all.ps1`) before any commit; one preview to avoid wrong scope; one PR action that re-runs tests and syncs (fetch+rebase) before push. No ad-hoc `git`/`pytest`/`ruff` in between.

Workflow that saves tokens (shorter form):

1. **Preview:** run `.\scripts\preview-commit.ps1` (or `commit-or-pr.ps1 -Action Preview`) to see changed files and diff summary.
2. **Propose:** from the file list and context, suggest a short title and bullet-point body.
3. **Commit or PR:** run `commit-or-pr.ps1 -Action Commit` (or `-Action PR -RunTests`) with that title and body. For a multi-line body without escaping issues, use `create-pr.ps1 -Title "..." -BodyFilePath (temp file)` or a one-off .ps1 with a here-string for `$Body`.

## Rules of thumb

- **After code change:** `.\scripts\check-all.ps1 -SkipPreCommit` (or full `check-all.ps1` before commit).
- **After docs/template/style change:** `.\scripts\lint-only.ps1`; run full check-all before pushing.
- **Iterating on one area:** `.\scripts\quick-test.ps1 -Keyword "content_type"` (or `-Path tests/test_file_scan_use_content_type_flag.py`); run full check-all when the slice is done.
- **User asks to commit / push / create PR:** use `preview-commit.ps1` then `commit-or-pr.ps1` (or `create-pr.ps1` for PR with body file); do not use ad-hoc `git add`/`git commit`/`git push` when the script covers the need.

Avoid running raw `pytest`, `ruff`, `pre-commit`, or manual git commit/push when a script already does the same thing; the scripts are the single source of behaviour and keep sessions token-efficient.
