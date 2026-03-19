#!/usr/bin/env pwsh
# Single gate script: run lint/format (via pre-commit) + full pytest suite.
# Usage (from repo root):
#   .\scripts\check-all.ps1
#   .\scripts\check-all.ps1 -SkipPreCommit   # only pytest (e.g. when iterating quickly)

param(
    [switch]$SkipPreCommit = $false
)

$ErrorActionPreference = "Stop"
$repoRoot = (Get-Item $PSScriptRoot).Parent.FullName
Set-Location $repoRoot

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

if ($exitCode -eq 0) {
    Write-Host "check-all: OK (pre-commit and pytest passed)." -ForegroundColor Green
} else {
    Write-Host "check-all: FAILED (see output above)." -ForegroundColor Red
}

exit $exitCode

