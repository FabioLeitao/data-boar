#!/usr/bin/env pwsh
# git-list-remote-orphan-branches.ps1
# Read-only inventory of remote branches that have *no* open PR backing them.
#
# Why this exists (Slack 2026-04-28, message ts 1777370978.136399):
#   The Cloud-Agent fleet leaves dozens of `cursor/sre-*` remote branches behind.
#   Most of them back live OPEN PRs --- those are *not* orphans, deleting them
#   would auto-close the PR and lose the audit paper trail (see
#   `docs/ops/sre_audits/FABRICATED_CLAIMS_INDEX.md`, mass-close fabrication).
#
#   This script answers exactly one question: "which remote branches have NO
#   open PR right now?" It never deletes anything. It prints
#   `git push origin --delete <branch>` lines you can copy after a final
#   read --- per `docs/ops/BRANCH_AND_DOCKER_CLEANUP.md` rules.
#
# Doctrine:
#   * docs/ops/inspirations/DEFENSIVE_SCANNING_MANIFESTO.md Section 1.3 ---
#     no surprise side effects: read-only by design.
#   * docs/ops/inspirations/THE_ART_OF_THE_FALLBACK.md Section 3 ---
#     diagnostic on fall: emit the list with provenance, not silent action.
#   * AGENTS.md Risk posture --- destructive ops require operator review.
#
# Usage (repo root):
#   .\scripts\git-list-remote-orphan-branches.ps1
#   .\scripts\git-list-remote-orphan-branches.ps1 -Pattern 'cursor/sre-'
#   .\scripts\git-list-remote-orphan-branches.ps1 -IncludeStaleDays 14

[CmdletBinding()]
param(
    [string]$Pattern = "",
    [int]$IncludeStaleDays = 0
)

$ErrorActionPreference = "Stop"
$KeepRegex = '^(main|HEAD|auditoria-ia|chore/.*release.*|chore/.*beta.*)$'

function Test-Tool($name) {
    if (-not (Get-Command $name -ErrorAction SilentlyContinue)) {
        Write-Host "$name not found" -ForegroundColor Red
        exit 1
    }
}
Test-Tool git
Test-Tool gh

Write-Host "==> Refreshing remote refs (git fetch --prune origin)" -ForegroundColor Cyan
& git fetch --prune origin | Out-Null

$openPrBranches = & gh pr list --state open --limit 500 --json headRefName -q '.[].headRefName' |
    Sort-Object -Unique

$remoteBranches = & git for-each-ref --format='%(refname:short)' refs/remotes/origin |
    ForEach-Object { $_ -replace '^origin/', '' } |
    Where-Object { $_ -and ($_ -ne 'HEAD') -and ($_ -ne 'origin') } |
    Sort-Object -Unique

$openSet = [System.Collections.Generic.HashSet[string]]::new([string[]]$openPrBranches)
$orphans = $remoteBranches | Where-Object {
    -not $openSet.Contains($_) -and ($_ -notmatch $KeepRegex)
}
if ($Pattern) {
    $orphans = $orphans | Where-Object { $_ -match $Pattern }
}

Write-Host ""
Write-Host "Remote branch inventory (origin):"
Write-Host ("  total remote refs    : {0}" -f $remoteBranches.Count)
Write-Host ("  branches with open PR: {0}" -f $openPrBranches.Count)
if ($Pattern) { Write-Host ("  -Pattern filter      : {0}" -f $Pattern) }
Write-Host ""

if (-not $orphans -or $orphans.Count -eq 0) {
    Write-Host "No orphan branches found (every non-protected remote branch is backed by an open PR)." -ForegroundColor Green
    exit 0
}

Write-Host "Orphan branches (no open PR, not in keep-list):" -ForegroundColor Yellow
$cutoff = $null
if ($IncludeStaleDays -gt 0) {
    $cutoff = (Get-Date).AddDays(-$IncludeStaleDays)
}

$rows = @()
foreach ($b in $orphans) {
    $lastIso = (& git log -1 --format='%cI' "origin/$b" 2>$null)
    $ahead   = (& git rev-list --count "origin/main..origin/$b" 2>$null)
    $behind  = (& git rev-list --count "origin/$b..origin/main" 2>$null)
    if ($cutoff -and $lastIso) {
        try {
            $lastDate = [datetime]::Parse($lastIso)
            if ($lastDate -gt $cutoff) { continue }
        } catch { }
    }
    $rows += [pscustomobject]@{
        Branch = $b
        Last   = $lastIso
        Ahead  = $ahead
        Behind = $behind
    }
}

if (-not $rows -or $rows.Count -eq 0) {
    Write-Host "No orphan branches matched the staleness filter." -ForegroundColor Green
    exit 0
}

$rows | Format-Table -AutoSize | Out-String | Write-Host

Write-Host "Suggested commands (copy + paste only after reviewing each branch):" -ForegroundColor Yellow
foreach ($row in $rows) {
    Write-Host ("  git push origin --delete {0}" -f $row.Branch)
}

Write-Host ""
Write-Host "This script is read-only. It does NOT delete anything." -ForegroundColor Green
Write-Host "Doctrine: DEFENSIVE_SCANNING_MANIFESTO Section 1.3, THE_ART_OF_THE_FALLBACK Section 3, AGENTS.md Risk posture."
