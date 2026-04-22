#!/usr/bin/env pwsh
# Single gate script: run lint/format (via pre-commit) + full pytest suite.
# Regression hooks include tests/test_detector_entertainment_regression.py (ML vs lyrics/OSS Markdown).
# Usage (from repo root):
#   .\scripts\check-all.ps1
#   .\scripts\check-all.ps1 -SkipPreCommit   # only pytest (e.g. when iterating quickly)

param(
    [switch]$SkipPreCommit = $false,
    [switch]$IncludeVersionSmoke = $false
)

$ErrorActionPreference = "Stop"
$repoRoot = (Get-Item $PSScriptRoot).Parent.FullName
Set-Location $repoRoot

# PII gate: maintainer seeds vs staged paths only (see scripts/gatekeeper-audit.ps1).
& "$repoRoot\scripts\gatekeeper-audit.ps1"
if ($LASTEXITCODE -ne 0) {
    Write-Host "check-all: ABORTED by gatekeeper-audit (PII seed hit in staged files)." -ForegroundColor Red
    exit $LASTEXITCODE
}

Write-Host "=== check-all: lint + tests ===" -ForegroundColor Cyan

# Keep plan dashboard stats in sync before lint/tests.
Write-Host "Refreshing plans status dashboard..." -ForegroundColor Yellow
& python "$repoRoot\scripts\plans-stats.py" --write
if ($LASTEXITCODE -ne 0) {
    Write-Host "check-all: FAILED to refresh plans dashboard." -ForegroundColor Red
    exit $LASTEXITCODE
}

# Delegate to the existing script so we keep behaviour in one place.
$argsList = @()
if ($SkipPreCommit) {
    $argsList += "-SkipPreCommit"
}

& "$repoRoot\scripts\pre-commit-and-tests.ps1" @argsList
$exitCode = $LASTEXITCODE

if ($exitCode -eq 0 -and $IncludeVersionSmoke) {
    $smokeScript = "$repoRoot\scripts\version-readiness-smoke.ps1"
    if (Test-Path -LiteralPath $smokeScript) {
        Write-Host "Running version readiness smoke..." -ForegroundColor Yellow
        & $smokeScript
        $exitCode = $LASTEXITCODE
    } else {
        Write-Host "Version readiness smoke script not found; skipping." -ForegroundColor Yellow
    }
}

if ($exitCode -eq 0) {
    Write-Host "check-all: OK (pre-commit and pytest passed)." -ForegroundColor Green
} else {
    Write-Host "check-all: FAILED (see output above)." -ForegroundColor Red
}

exit $exitCode

