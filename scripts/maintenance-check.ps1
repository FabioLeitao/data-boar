# Local triage for maintenance rows –1 (Dependabot) and –1b (Docker Scout image).
# Does not modify the repo. Run from repo root after `gh auth login` and (for Scout) Docker Desktop.
# Usage: .\scripts\maintenance-check.ps1
# See SECURITY.md, docs/COMMIT_AND_PR.md, and .cursor/rules/dependabot-hygiene.mdc.

$ErrorActionPreference = "Continue"
Write-Host "=== Maintenance check: Dependabot + Docker Scout ===" -ForegroundColor Cyan
Write-Host ""

Write-Host "## Open Dependabot PRs (GitHub CLI)" -ForegroundColor Yellow
if (Get-Command gh -ErrorAction SilentlyContinue) {
    gh pr list --state open --author "dependabot[bot]" --limit 25 2>&1
    if ($LASTEXITCODE -ne 0) {
        Write-Host "(gh pr list exited $LASTEXITCODE — check auth: gh auth login)" -ForegroundColor DarkYellow
    }
} else {
    Write-Host "GitHub CLI (gh) not found. Install: https://cli.github.com/" -ForegroundColor Yellow
}
Write-Host ""

Write-Host "## Docker Scout quickview (published image)" -ForegroundColor Yellow
if (Get-Command docker -ErrorAction SilentlyContinue) {
    docker scout quickview fabioleitao/data_boar:latest 2>&1
} else {
    Write-Host "Docker not found; skip Scout (install Docker Desktop for local quickview)." -ForegroundColor Yellow
}
Write-Host ""

Write-Host "## Next steps" -ForegroundColor Green
Write-Host "  1. Merge or apply Dependabot changes only after: .\scripts\check-all.ps1 (and CI green on PR)."
Write-Host "  2. For image CVEs: rebuild/push image after Dockerfile / deps fixes; re-run Scout on the new digest."
Write-Host "  3. requirements.txt is uv-exported; wheel/pip are not direct app deps — Dockerfile upgrades pip/wheel in build + runtime."
