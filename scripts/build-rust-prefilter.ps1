param(
    [switch]$Release = $true,
    [string]$Target = ""
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$repoRoot = Split-Path -Parent $PSScriptRoot
$manifestPath = Join-Path $repoRoot "rust\boar_fast_filter\Cargo.toml"

if (-not (Test-Path -LiteralPath $manifestPath)) {
    throw "Rust manifest not found: $manifestPath"
}

Push-Location $repoRoot
try {
    & uv run pip install maturin
    if ($LASTEXITCODE -ne 0) {
        throw "Failed to install maturin"
    }

    $args = @("develop", "--manifest-path", $manifestPath)
    if ($Release) {
        $args += "--release"
    }
    if ($Target) {
        $args += @("--target", $Target)
    }

    & maturin @args
    if ($LASTEXITCODE -ne 0) {
        throw "maturin develop failed"
    }
    Write-Host "[OK] boar_fast_filter installed in current Python environment." -ForegroundColor Green
}
finally {
    Pop-Location
}
