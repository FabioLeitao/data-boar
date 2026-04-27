#!/usr/bin/env pwsh
# dependabot-resync.ps1 - operator helper to refresh uv.lock + requirements.txt on a
# Dependabot pip PR branch so tests/test_dependency_artifacts_sync.py turns green again.
#
# Why this exists: Dependabot only edits requirements.txt; the project keeps
# pyproject.toml, uv.lock and requirements.txt as a single source of truth
# (CONTRIBUTING.md, tests/test_dependency_artifacts_sync.py). A naive "rage-merge" of
# a security bump (e.g. cryptography 47.0.0 for a CVE) would land an inconsistent
# lockfile and a misaligned SBOM.
#
# Doctrine: docs/ops/inspirations/DEFENSIVE_SCANNING_MANIFESTO.md (no surprise side
# effects) and docs/ops/inspirations/THE_ART_OF_THE_FALLBACK.md (diagnostic on fall).
# Windows/Linux pair: scripts/dependabot-resync.sh.
#
# Usage (from repo root, on a checked-out Dependabot PR branch):
#   .\scripts\dependabot-resync.ps1                  # regenerate, do not commit
#   .\scripts\dependabot-resync.ps1 -Commit          # regenerate + git add + git commit
#   .\scripts\dependabot-resync.ps1 -CheckOnly       # verify only, exit non-zero on drift

param(
    [switch]$Commit = $false,
    [switch]$CheckOnly = $false
)

$ErrorActionPreference = "Stop"
$repoRoot = (Get-Item $PSScriptRoot).Parent.FullName
Set-Location $repoRoot

if (-not (Get-Command uv -ErrorAction SilentlyContinue)) {
    Write-Host "dependabot-resync.ps1: 'uv' not on PATH. Install per docs/USAGE.md." -ForegroundColor Red
    exit 2
}

if ($CheckOnly) {
    Write-Host "=== dependabot-resync.ps1: CHECK ONLY (no writes) ===" -ForegroundColor Cyan
    & uv lock --check
    if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
    & uv run pytest tests/test_dependency_artifacts_sync.py -v -W error
    exit $LASTEXITCODE
}

Write-Host "=== dependabot-resync.ps1: regenerating uv.lock + requirements.txt ===" -ForegroundColor Cyan

# Step 1: refresh uv.lock from pyproject.toml.
& uv lock
if ($LASTEXITCODE -ne 0) {
    Write-Host "dependabot-resync.ps1: 'uv lock' failed. See output above." -ForegroundColor Red
    exit $LASTEXITCODE
}

# Step 2: re-export requirements.txt with the exact flags the guard expects.
& uv export --no-emit-package pyproject.toml -o requirements.txt
if ($LASTEXITCODE -ne 0) {
    Write-Host "dependabot-resync.ps1: 'uv export' failed." -ForegroundColor Red
    exit $LASTEXITCODE
}

# Step 3: run the same pytest the pre-commit hook runs. Diagnostic on fall.
& uv run pytest tests/test_dependency_artifacts_sync.py -v -W error
if ($LASTEXITCODE -ne 0) {
    Write-Host ""
    Write-Host "dependabot-resync.ps1: regen finished but the dependency-artifacts guard still fails." -ForegroundColor Red
    Write-Host "Most common cause: pyproject.toml on this branch does not yet include the version" -ForegroundColor Yellow
    Write-Host "Dependabot tried to land (direct dep). Edit pyproject.toml so the constraint accepts" -ForegroundColor Yellow
    Write-Host "the new version, then re-run this script." -ForegroundColor Yellow
    Write-Host "See .cursor/skills/dependabot-recommendations/SKILL.md for the canonical flow." -ForegroundColor Yellow
    exit 1
}

if ($Commit) {
    $diff = & git diff --quiet -- uv.lock requirements.txt
    if ($LASTEXITCODE -eq 0) {
        Write-Host "dependabot-resync.ps1: nothing to commit (already in sync)." -ForegroundColor Yellow
        exit 0
    }
    & git add uv.lock requirements.txt
    & git commit -m "chore(deps): resync uv.lock + requirements.txt after Dependabot bump"
    if ($LASTEXITCODE -ne 0) {
        Write-Host "dependabot-resync.ps1: git commit failed." -ForegroundColor Red
        exit $LASTEXITCODE
    }
    Write-Host "dependabot-resync.ps1: committed regen. Push when ready: git push" -ForegroundColor Green
}

Write-Host "dependabot-resync.ps1: done." -ForegroundColor Green
