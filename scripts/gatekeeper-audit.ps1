#Requires -Version 5.1
<#
.SYNOPSIS
    Block commits when any maintainer PII seed literal appears in staged file blobs (index).

.DESCRIPTION
    Reads docs/private/security_audit/PII_LOCAL_SEEDS.txt (same contract as run-pii-local-seeds-pickaxe.ps1):
    one fixed string per non-comment line.

    Resolves paths with `git diff --cached --name-only` (staged add/modify/rename/copy/type-change only).
    If there is nothing staged, exits 0 immediately.

    Runs `git grep -n -F -f <tempfile> --cached -- <paths...>` so only blobs that would be included in the
    next commit are scanned — not the entire repository index for unrelated paths.

    If the seeds file is missing (CI, fresh clone without docs/private/), exits 0 with a yellow skip message
    unless -RequireSeeds is set.

.PARAMETER SeedsPath
    Override path to the seeds file (default: docs/private/security_audit/PII_LOCAL_SEEDS.txt).

.PARAMETER RequireSeeds
    If set, fail when the seeds file is missing instead of skipping.

.EXAMPLE
    .\scripts\gatekeeper-audit.ps1
    .\scripts\gatekeeper-audit.ps1 -RequireSeeds
#>
param(
    [string] $SeedsPath = "",
    [switch] $RequireSeeds
)

$ErrorActionPreference = "Stop"
$repoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
Set-Location $repoRoot

if (-not $SeedsPath) {
    $SeedsPath = Join-Path $repoRoot "docs\private\security_audit\PII_LOCAL_SEEDS.txt"
}
elseif (-not [System.IO.Path]::IsPathRooted($SeedsPath)) {
    $SeedsPath = Join-Path $repoRoot $SeedsPath
}

function Write-GateFail($msg) {
    Write-Host "GATEKEEPER-AUDIT: $msg" -ForegroundColor Red
}

function Write-GateSkip($msg) {
    Write-Host "GATEKEEPER-AUDIT: $msg" -ForegroundColor Yellow
}

if (-not (Test-Path -LiteralPath $SeedsPath)) {
    if ($RequireSeeds) {
        Write-GateFail "Seeds file required but missing: $SeedsPath"
        Write-GateFail "Copy from docs/private.example/security_audit/PII_LOCAL_SEEDS.example.txt"
        exit 1
    }
    Write-GateSkip "SKIP (no seeds file). Not an error — enable by copying PII_LOCAL_SEEDS.example.txt to docs/private/security_audit/PII_LOCAL_SEEDS.txt"
    exit 0
}

$lines = Get-Content -LiteralPath $SeedsPath -Encoding UTF8
$seeds = New-Object System.Collections.Generic.List[string]
foreach ($raw in $lines) {
    $t = $raw.Trim()
    if ($t.Length -eq 0) { continue }
    if ($t.StartsWith("#")) { continue }
    $seeds.Add($t) | Out-Null
}

if ($seeds.Count -eq 0) {
    Write-GateSkip "No active seed lines (only comments/blank). Nothing to scan."
    exit 0
}

Write-Host "=== gatekeeper-audit: PII seeds vs staged paths (--cached) ===" -ForegroundColor Cyan
Write-Host "  Seeds file: $SeedsPath ($($seeds.Count) active line(s))" -ForegroundColor Gray

$prevEap = $ErrorActionPreference
$ErrorActionPreference = "Continue"
$stagedOut = git -C $repoRoot diff --cached --name-only --diff-filter=ACMRT 2>&1
$ErrorActionPreference = $prevEap
if ($LASTEXITCODE -ne 0) {
    Write-GateFail "git diff --cached --name-only failed: $stagedOut"
    exit 2
}

$paths = @(
    $stagedOut | ForEach-Object { $_.Trim() } | Where-Object { $_.Length -gt 0 }
)
if ($paths.Count -eq 0) {
    Write-Host "GATEKEEPER-AUDIT: OK (nothing staged; no paths to scan)." -ForegroundColor Green
    exit 0
}

Write-Host "  Staged path(s): $($paths.Count)" -ForegroundColor Gray

$tmp = [System.IO.Path]::GetTempFileName()
try {
    $utf8NoBom = New-Object System.Text.UTF8Encoding $false
    [System.IO.File]::WriteAllLines($tmp, [string[]]$seeds.ToArray(), $utf8NoBom)

    $batchSize = 60
    for ($i = 0; $i -lt $paths.Count; $i += $batchSize) {
        $end = [Math]::Min($i + $batchSize, $paths.Count) - 1
        $chunk = $paths[$i..$end]
        $ErrorActionPreference = "Continue"
        $grepArgs = @("-C", $repoRoot, "grep", "-n", "-F", "-f", $tmp, "--cached", "--") + $chunk
        $out = & git @grepArgs 2>&1
        $ErrorActionPreference = $prevEap
        $text = if ($null -eq $out) { "" } else { ($out | Out-String).TrimEnd() }
        $code = $LASTEXITCODE

        if ($code -eq 0) {
            if ($text.Length -gt 0) {
                Write-GateFail "HIT — maintainer seed literal(s) found in staged content:"
                Write-Host $text -ForegroundColor Red
                Write-GateFail "ABORT: redact or unstage before commit/push."
                exit 1
            }
        }
        elseif ($code -eq 1) {
            if ($text.Length -gt 0) {
                Write-GateFail "Unexpected output with exit 1: $text"
                exit 2
            }
        }
        else {
            Write-GateFail "git grep failed (exit $code): $text"
            exit 2
        }
    }
}
finally {
    if (Test-Path -LiteralPath $tmp) {
        Remove-Item -LiteralPath $tmp -Force -ErrorAction SilentlyContinue
    }
}

Write-Host "GATEKEEPER-AUDIT: OK (no seed hits in staged paths)." -ForegroundColor Green
exit 0
