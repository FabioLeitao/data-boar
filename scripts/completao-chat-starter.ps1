#Requires -Version 5.1
<#
.SYNOPSIS
    Print a minimal Cursor chat starter for lab completão (token + tier shorthand).

.DESCRIPTION
    Pairs with docs/ops/COMPLETAO_OPERATOR_PROMPT_LIBRARY.md — line 1 must stay the
    English session token "completao" alone; line 2 is a tier:* shorthand so you
    rarely need the full LAB_COMPLETAO_FRESH_AGENT_BRIEF copy-paste blocks.

.PARAMETER Tier
    smoke | smoke-main | smoke-tag | followup-repo | followup-poc | followup-cli | evidence

.PARAMETER LabGitRef
    Used when Tier is smoke-tag (e.g. v1.7.3) or to override smoke-main default.

.PARAMETER Clip
    Copy printed block to clipboard (Windows).

.EXAMPLE
    .\scripts\completao-chat-starter.ps1
    .\scripts\completao-chat-starter.ps1 -Tier followup-repo -Clip
#>
param(
    [ValidateSet(
        "smoke",
        "smoke-main",
        "smoke-tag",
        "followup-repo",
        "followup-poc",
        "followup-cli",
        "evidence"
    )]
    [string]$Tier = "smoke-main",

    [string]$LabGitRef = "",

    [switch]$Clip,

    [switch]$Help
)

$ErrorActionPreference = "Stop"

function Show-Help {
    @'
completao-chat-starter.ps1 - print minimal chat lines for lab completão (UTF-8 docs; this help is ASCII-only)

Tiers (line 2 after completao):
  smoke           -> tier:smoke  -> lab-completao-orchestrate.ps1 -Privileged
  smoke-main      -> tier:smoke-main (default) + -LabGitRef origin/main
  smoke-tag       -> tier:smoke-tag + -LabGitRef <tag> -SkipGitPullOnInventoryRefresh (pass -LabGitRef vX.Y.Z)
  followup-repo   -> tier:followup-repo -> lab-op-repo-status.ps1
  followup-poc    -> tier:followup-poc -> smoke-maturity + smoke-webauthn scripts
  followup-cli    -> tier:followup-cli -> LAB_EXTERNAL_CONNECTIVITY_EVAL
  evidence        -> tier:evidence -> consolidate session notes

Docs: docs/ops/COMPLETAO_OPERATOR_PROMPT_LIBRARY.md
'@
}

if ($Help) {
    Show-Help
    exit 0
}

$line2 = switch ($Tier) {
    "smoke" { "tier:smoke" }
    "smoke-main" { "tier:smoke-main" }
    "smoke-tag" { "tier:smoke-tag" }
    "followup-repo" { "tier:followup-repo" }
    "followup-poc" { "tier:followup-poc" }
    "followup-cli" { "tier:followup-cli" }
    "evidence" { "tier:evidence" }
}

$cmd = switch ($Tier) {
    "smoke" { ".\scripts\lab-completao-orchestrate.ps1 -Privileged" }
    "smoke-main" { ".\scripts\lab-completao-orchestrate.ps1 -Privileged -LabGitRef origin/main" }
    "smoke-tag" {
        if (-not $LabGitRef) {
            Write-Error "Tier smoke-tag requires -LabGitRef vX.Y.Z (e.g. -LabGitRef v1.7.3)"
        }
        ".\scripts\lab-completao-orchestrate.ps1 -Privileged -LabGitRef $LabGitRef -SkipGitPullOnInventoryRefresh"
    }
    "followup-repo" { ".\scripts\lab-op-repo-status.ps1" }
    "followup-poc" { ".\scripts\smoke-maturity-assessment-poc.ps1; .\scripts\smoke-webauthn-json.ps1" }
    "followup-cli" { "# Read docs/ops/LAB_EXTERNAL_CONNECTIVITY_EVAL.md then run main.py with private config if present" }
    "evidence" { "# Consolidate session notes under docs/private/homelab/ per LAB_COMPLETAO_FRESH_AGENT_BRIEF block E" }
}

$block = @"
completao

$line2

# Suggested command (repo root):
$cmd
"@

Write-Host $block

if ($Clip) {
    Set-Clipboard -Value ($block.TrimEnd())
    Write-Host "`n( Copied to clipboard )" -ForegroundColor DarkGray
}
