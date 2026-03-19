---
name: token-aware-automation
description: Use when deciding how to run lint or tests. Prefer repo scripts (check-all, lint-only, quick-test) over ad-hoc commands to save tokens and keep behaviour consistent.
---

# Token-aware automation (scripts first)

When you need to **verify lint or tests**, use the repo scripts from the project root so behaviour is consistent and token use stays low.

## Which script to use

| Goal | Script | When it saves tokens |
|------|--------|----------------------|
| Full gate before commit/PR | `.\scripts\check-all.ps1` | Single command = one round-trip |
| Tests only (no pre-commit) | `.\scripts\check-all.ps1 -SkipPreCommit` | Skips Ruff/markdown when you only care about tests |
| Lint/format only | `.\scripts\lint-only.ps1` | No pytest when you only changed docs, templates, or style |
| One test file or keyword | `.\scripts\quick-test.ps1 -Path tests/test_foo.py` or `-Keyword "content_type"` | Fewer tests = faster feedback and fewer tokens |

## Rules of thumb

- **After code change:** `.\scripts\check-all.ps1 -SkipPreCommit` (or full `check-all.ps1` before commit).
- **After docs/template/style change:** `.\scripts\lint-only.ps1`; run full check-all before pushing.
- **Iterating on one area:** `.\scripts\quick-test.ps1 -Keyword "content_type"` (or `-Path tests/test_file_scan_use_content_type_flag.py`); run full check-all when the slice is done.

Avoid running raw `pytest`, `ruff`, or `pre-commit` when a script already does the same thing; the scripts are the single source of behaviour and keep sessions token-efficient.
