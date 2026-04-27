#!/usr/bin/env pwsh
# Run pre-commit (Ruff + plans-stats --check + markdown + pt-BR + commercial guard) and full pytest via uv.
# When not skipped, may run an optional maturin build for rust/boar_fast_filter (see build-rust-prefilter.ps1).
# Linux/macOS twin: scripts/pre-commit-and-tests.sh
# Usage (from repo root):
#   .\scripts\pre-commit-and-tests.ps1
#   .\scripts\pre-commit-and-tests.ps1 -SkipPreCommit   # only pytest

param(
    [switch]$SkipPreCommit = $false
)

$ErrorActionPreference = "Stop"
$repoRoot = (Get-Item $PSScriptRoot).Parent.FullName
Set-Location $repoRoot

# Recover from a broken/missing project venv (uv run needs .venv/pyvenv.cfg).
$venvCfg = Join-Path $repoRoot ".venv/pyvenv.cfg"
if (-not (Test-Path -LiteralPath $venvCfg)) {
    Write-Host "No .venv/pyvenv.cfg - running uv sync to recreate the environment..." -ForegroundColor Yellow
    uv sync
    if (-not (Test-Path -LiteralPath $venvCfg)) {
        Write-Host "check gate: uv sync did not create .venv; fix disk path or UV_* env and retry." -ForegroundColor Red
        exit 2
    }
}

# Optional Rust native extension (parity with scripts/build-rust-prefilter.ps1).
# Best-effort: developers without rustc/maturin still pass the gate; CI typically skips importorskip tests.
$rustManifest = Join-Path $repoRoot "rust\boar_fast_filter\Cargo.toml"
if ((-not $SkipPreCommit) -and (Test-Path -LiteralPath $rustManifest) -and ($env:DATA_BOAR_SKIP_RUST_BUILD -ne "1")) {
    if (Get-Command rustc -ErrorAction SilentlyContinue) {
        Write-Host "Building Rust prefilter (boar_fast_filter)..." -ForegroundColor Cyan
        uv run pip install maturin 2>$null | Out-Null
        uv run maturin develop --manifest-path $rustManifest --release
        if ($LASTEXITCODE -ne 0) {
            Write-Host "Rust prefilter build failed or incomplete; continuing without native extension (tests may skip)." -ForegroundColor Yellow
        }
    } else {
        Write-Host "rustc not on PATH; skipping Rust prefilter build." -ForegroundColor Yellow
    }
}

if (-not $SkipPreCommit) {
    Write-Host "Running pre-commit (Ruff + markdown + pt-BR locale guards)..." -ForegroundColor Cyan
    uv run pre-commit run --all-files
    if ($LASTEXITCODE -ne 0) {
        Write-Host "pre-commit failed. Attempting to auto-apply Ruff formatting and re-run pre-commit once..." -ForegroundColor Yellow
        try {
            # Best-effort: format the codebase with Ruff, then re-run pre-commit.
            uv run ruff format .
            uv run pre-commit run --all-files
        } catch {
            Write-Host "Auto-format step failed: $($_.Exception.Message)" -ForegroundColor Red
        }
        if ($LASTEXITCODE -ne 0) {
            Write-Host "pre-commit still failing after auto-format. Fix issues above before committing or pushing." -ForegroundColor Red
            exit $LASTEXITCODE
        }
    }
}

Write-Host "Running pytest (full suite, warnings treated as errors)..." -ForegroundColor Cyan
uv run pytest -v -W error --tb=short
if ($LASTEXITCODE -ne 0) {
    Write-Host "pytest failed. Fix test failures before committing or pushing." -ForegroundColor Red
}

exit $LASTEXITCODE

