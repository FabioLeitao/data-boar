# Data Boar — Windows dev workstation inventory (run on the PC; redact before sharing).
# Usage: pwsh -File scripts/windows-dev-report.ps1
# See: docs/ops/WINDOWS_WSL_MULTI_DISTRO_LAB.md

$ErrorActionPreference = "Continue"
Write-Host "=== windows-dev-report $(Get-Date -Format o) ==="
Write-Host "HOST: $env:COMPUTERNAME"

Write-Host "--- WSL ---"
wsl.exe -l -v 2>&1

Write-Host "--- PATH tools ---"
foreach ($c in @("go", "rustc", "cargo", "uv", "docker", "zig", "odin", "python", "python3")) {
    $g = Get-Command $c -ErrorAction SilentlyContinue
    if ($g) { Write-Host "$c -> $($g.Source)" } else { Write-Host "$c -> (not in PATH)" }
}

Write-Host "--- Versions ---"
if (Get-Command go -ErrorAction SilentlyContinue) { go version }
if (Get-Command rustc -ErrorAction SilentlyContinue) { rustc --version }
if (Get-Command uv -ErrorAction SilentlyContinue) { uv --version }
if (Get-Command docker -ErrorAction SilentlyContinue) { docker --version }
if (Get-Command zig -ErrorAction SilentlyContinue) { zig version }
if (Get-Command odin -ErrorAction SilentlyContinue) { odin version 2>&1 }

Write-Host "--- Visual Studio (vswhere) ---"
$vswhere = Join-Path ${env:ProgramFiles(x86)} "Microsoft Visual Studio\Installer\vswhere.exe"
if (Test-Path $vswhere) {
    # Stable + Preview/Insiders (without -prerelease, Insiders often does not appear)
    Write-Host "(all products, including prerelease / Insiders):"
    & $vswhere -all -prerelease -products * -property displayName, installationVersion, installationPath 2>&1
    Write-Host "`n(text dump):"
    & $vswhere -all -prerelease -products * -format text 2>&1
} else {
    Write-Host "vswhere.exe not found"
}

Write-Host "--- Disk (OS volume) ---"
Get-PSDrive -PSProvider FileSystem | Where-Object { $_.Name -eq "C" } | Format-List Name, Used, Free

Write-Host "=== end ==="
