#!/usr/bin/env pwsh
# Run pre-commit (Ruff lint + format check) and the full pytest suite via uv.
# Usage (from repo root):
#   .\scripts\pre-commit-and-tests.ps1
#   .\scripts\pre-commit-and-tests.ps1 -SkipPreCommit   # only pytest

param(
    [switch]$SkipPreCommit = $false
)

$ErrorActionPreference = "Stop"
$repoRoot = (Get-Item $PSScriptRoot).Parent.FullName
Set-Location $repoRoot

if (-not $SkipPreCommit) {
    Write-Host "Running pre-commit (Ruff lint + format check)..." -ForegroundColor Cyan
    uv run pre-commit run --all-files
    if ($LASTEXITCODE -ne 0) {
        Write-Host "pre-commit failed. Fix issues above before committing or pushing." -ForegroundColor Red
        exit $LASTEXITCODE
    }
}

Write-Host "Running pytest (full suite, warnings treated as errors)..." -ForegroundColor Cyan
uv run pytest -v -W error --tb=short
if ($LASTEXITCODE -ne 0) {
    Write-Host "pytest failed. Fix test failures before committing or pushing." -ForegroundColor Red
}

exit $LASTEXITCODE

