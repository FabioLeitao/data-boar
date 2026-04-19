#Requires -Version 5.1
<#
.SYNOPSIS
    Build sdist+wheel and publish data-boar to PyPI (uv).

.DESCRIPTION
    Uses `uv build` then `uv publish`. Set UV_PUBLISH_TOKEN (PyPI API token) in the environment
    or pass -Token. Never commit tokens. For first-time publish, ensure the PyPI project name
    `data-boar` is created / allowed on your account.

    Dry run: .\scripts\pypi-publish.ps1 -DryRun

.EXAMPLE
    $env:UV_PUBLISH_TOKEN = "<pypi-api-token>"
    .\scripts\pypi-publish.ps1
#>
param(
    [switch]$DryRun,
    [string]$Token = ""
)

$ErrorActionPreference = "Stop"
$repoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
Set-Location $repoRoot

if (-not (Get-Command uv -ErrorAction SilentlyContinue)) {
    Write-Host "uv: not found. Install uv and run from repo root." -ForegroundColor Red
    exit 1
}

Write-Host "=== uv build ===" -ForegroundColor Cyan
& uv build
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

if ($DryRun) {
    Write-Host "=== uv publish --dry-run ===" -ForegroundColor Cyan
    & uv publish --dry-run dist/*
    exit $LASTEXITCODE
}

if ($Token) {
    $env:UV_PUBLISH_TOKEN = $Token
}

if (-not $env:UV_PUBLISH_TOKEN) {
    Write-Host "UV_PUBLISH_TOKEN is not set. Set it (PyPI API token) or use -DryRun." -ForegroundColor Yellow
    Write-Host "Example: `$env:UV_PUBLISH_TOKEN = '<token>'; .\scripts\pypi-publish.ps1" -ForegroundColor Gray
    exit 1
}

Write-Host "=== uv publish (PyPI) ===" -ForegroundColor Cyan
& uv publish dist/*
exit $LASTEXITCODE
