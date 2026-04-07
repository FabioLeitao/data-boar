#Requires -Version 5.1
<#
.SYNOPSIS
    Cheap, reproducible post-remediation audit for Windows username leakage.

.DESCRIPTION
    Creates a fresh clone, runs short git history/tree checks for:
      C:\Users\ + operator username
    and prints command + result evidence.

.PARAMETER RepoUrl
    Repository URL to clone.

.PARAMETER TempCloneName
    Folder name under $env:TEMP for the temporary clone.

.PARAMETER KeepClone
    Keep the temporary clone after execution.

.PARAMETER RunCheckAll
    Also run full validation gate (uv sync + scripts/check-all.ps1).

.PARAMETER TargetUserSegment
    Username segment to probe (for incident response on a known leaked username).
    Do not commit real usernames in this file; pass at runtime only.

.EXAMPLE
    .\scripts\new-b2-verify.ps1

.EXAMPLE
    .\scripts\new-b2-verify.ps1 -RunCheckAll -KeepClone
#>
param(
    [string]$RepoUrl = "https://github.com/FabioLeitao/data-boar.git",
    [string]$TempCloneName = "data-boar-reaudit-short",
    [switch]$KeepClone,
    [switch]$RunCheckAll,
    [string]$TargetUserSegment = ""
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

function Write-Step {
    param([string]$Message)
    Write-Host "`n=== $Message ===" -ForegroundColor Cyan
}

function Invoke-AuditCheck {
    param(
        [string]$Name,
        [string]$CommandText,
        [scriptblock]$Command,
        [ValidateSet("zero","any")]
        [string]$Expected = "zero"
    )

    Write-Host ""
    Write-Host ">>> $CommandText" -ForegroundColor Yellow
    $output = & $Command 2>&1
    $exitCode = $LASTEXITCODE
    $lines = @($output)

    if ($exitCode -gt 1) {
        Write-Host "Exit code: $exitCode (error)" -ForegroundColor Red
        if ($lines.Count -gt 0) { $lines | ForEach-Object { Write-Host $_ } }
        return [PSCustomObject]@{
            Name      = $Name
            Command   = $CommandText
            ExitCode  = $exitCode
            MatchCount= $lines.Count
            Passed    = $false
        }
    }

    $passed = $true
    if ($Expected -eq "zero" -and $lines.Count -ne 0) {
        $passed = $false
    }

    Write-Host "Exit code: $exitCode"
    Write-Host "Match count: $($lines.Count)"
    if ($lines.Count -gt 0) { $lines | ForEach-Object { Write-Host $_ } }

    return [PSCustomObject]@{
        Name       = $Name
        Command    = $CommandText
        ExitCode   = $exitCode
        MatchCount = $lines.Count
        Passed     = $passed
    }
}

$tempRoot = $env:TEMP
$clonePath = Join-Path $tempRoot $TempCloneName
$targetUserPath = if ($TargetUserSegment) {
    "C:\Users\" + $TargetUserSegment
} else {
    "C:\Users\<username>"
}
$targetPlaceholder = "C:\Users\<username>"

Write-Step "Preparing fresh clone"
Write-Host "RepoUrl: $RepoUrl"
Write-Host "ClonePath: $clonePath"
if (Test-Path -LiteralPath $clonePath) {
    Remove-Item -LiteralPath $clonePath -Recurse -Force
}
git clone $RepoUrl $clonePath
if ($LASTEXITCODE -ne 0) {
    throw "git clone failed."
}

Push-Location $clonePath
try {
    Write-Step "Running short audit checks"
    $results = @()
    $results += Invoke-AuditCheck `
        -Name "log_s_users_fabio" `
        -CommandText ("git log --all -S `"{0}`" --oneline" -f $targetUserPath) `
        -Command { git log --all -S $targetUserPath --oneline } `
        -Expected "zero"

    $results += Invoke-AuditCheck `
        -Name "grep_all_revs_users_fabio" `
        -CommandText ("git grep -n -F `"{0}`" $(git rev-list --all)" -f $targetUserPath) `
        -Command { git grep -n -F $targetUserPath $(git rev-list --all) } `
        -Expected "zero"

    $results += Invoke-AuditCheck `
        -Name "grep_head_placeholder" `
        -CommandText ("git grep -n -F `"{0}`" -- `":(exclude)*.lock`"" -f $targetPlaceholder) `
        -Command { git grep -n -F $targetPlaceholder -- ":(exclude)*.lock" } `
        -Expected "any"

    if ($RunCheckAll) {
        Write-Step "Optional full gate"
        Write-Host ">>> uv sync"
        uv sync
        if ($LASTEXITCODE -ne 0) { throw "uv sync failed." }
        Write-Host ">>> .\scripts\check-all.ps1"
        .\scripts\check-all.ps1
        if ($LASTEXITCODE -ne 0) { throw "check-all failed." }
    }

    Write-Step "Summary"
    $results | Format-Table Name, ExitCode, MatchCount, Passed -AutoSize
    $failed = @($results | Where-Object { -not $_.Passed })
    if ($failed.Count -gt 0) {
        Write-Host ""
        Write-Host "FINAL STATUS: NOT SAFE (one or more checks failed)" -ForegroundColor Red
        exit 1
    }

    Write-Host ""
    Write-Host "FINAL STATUS: SAFE (target pattern not found)" -ForegroundColor Green
    exit 0
}
finally {
    Pop-Location
    if (-not $KeepClone -and (Test-Path -LiteralPath $clonePath)) {
        Remove-Item -LiteralPath $clonePath -Recurse -Force
        Write-Host "Removed temp clone: $clonePath" -ForegroundColor DarkGray
    } elseif ($KeepClone) {
        Write-Host "Kept temp clone: $clonePath" -ForegroundColor DarkGray
    }
}
