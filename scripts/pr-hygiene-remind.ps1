#!/usr/bin/env pwsh
# Echo-only PR hygiene reminders (no network, no tests). Token-aware: read this output instead of re-opening long docs.
# Usage (from repo root): .\scripts\pr-hygiene-remind.ps1
# See: docs/ops/README.md § "Before you open a PR", CONTRIBUTING.md, AGENTS.md, docs/plans/TOKEN_AWARE_USAGE.md

Write-Host "=== PR hygiene (reminders only) ===" -ForegroundColor Cyan
Write-Host "1. Full gate:  .\scripts\check-all.ps1   (or: plans-stats --write, pre-commit, pytest -W error)"
Write-Host "2. Never commit:  docs/private/   (real inventory — gitignored)"
Write-Host "3. Never:  git add -f config.yaml   (secrets / LAN paths)"
Write-Host "4. Template:  docs/private.example/  -> copy to docs/private/  (policy: PRIVATE_OPERATOR_NOTES.md)"
Write-Host "5. Agents: no real hostnames, RFC1918 IPs, serials, or home paths in tracked Markdown/code comments."
Write-Host "=== end ===" -ForegroundColor Cyan
