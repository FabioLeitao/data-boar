#Requires -Version 5.1
<#
.SYNOPSIS
  Run lab-completao-host-smoke.sh on each LAB-OP host from the manifest; save consolidated logs.

.DESCRIPTION
  Same manifest as lab-op-sync-and-collect.ps1 (docs/private/homelab/lab-op-hosts.manifest.json).
  Optional per-host "completaoHealthUrl" for remote curl from the dev PC after SSH smoke.
  Optional per-host "completaoEngineMode":"container" or "completaoSkipEngineImport":true when the host
  runs Data Boar only via Docker/Swarm/Podman (skip bare-metal uv / import core.engine) - see LAB_COMPLETAO_RUNBOOK.md.

  By default, runs scripts/lab-completao-inventory-preflight.ps1 (15-day freshness) and lab-op-sync-and-collect.ps1
  when private LAB_SOFTWARE_INVENTORY.md / OPERATOR_SYSTEM_MAP.md are missing or stale - see LAB_COMPLETAO_RUNBOOK.md.

  "Completao" is NOT pytest - see docs/ops/LAB_COMPLETAO_RUNBOOK.md.

.EXAMPLE
  .\scripts\lab-completao-orchestrate.ps1

.EXAMPLE
  .\scripts\lab-completao-orchestrate.ps1 -Privileged
#>
param(
    [string] $ManifestPath = "",
    [string] $RepoRoot = "",
    [switch] $Privileged,
    [switch] $SkipFping,
    [int] $InventoryMaxAgeDays = 15,
    [switch] $SkipInventoryPreflight,
    [switch] $SkipGitPullOnInventoryRefresh
)

$ErrorActionPreference = "Stop"
if (-not $RepoRoot) {
    $RepoRoot = (Get-Item $PSScriptRoot).Parent.FullName
}
$primaryManifest = Join-Path $RepoRoot "docs\private\homelab\lab-op-hosts.manifest.json"
$fallbackManifest = Join-Path $RepoRoot "docs\private\homelab\lab-op-hosts.manifest.example.json"
if (-not $ManifestPath) {
    if (Test-Path -LiteralPath $primaryManifest) {
        $ManifestPath = $primaryManifest
    } elseif (Test-Path -LiteralPath $fallbackManifest) {
        $ManifestPath = $fallbackManifest
        Write-Warning "Using example manifest; copy to lab-op-hosts.manifest.json for real hosts."
    }
}
if (-not $ManifestPath -or -not (Test-Path -LiteralPath $ManifestPath)) {
    throw "Missing manifest: copy docs/private.example/homelab/lab-op-hosts.manifest.example.json to docs/private/homelab/lab-op-hosts.manifest.json"
}

if (-not $SkipInventoryPreflight) {
    $preflight = Join-Path $RepoRoot "scripts\lab-completao-inventory-preflight.ps1"
    if (Test-Path -LiteralPath $preflight) {
        & $preflight -RepoRoot $RepoRoot -ManifestPath $ManifestPath -MaxAgeDays $InventoryMaxAgeDays -AutoRefresh -SkipFping:$SkipFping -SkipGitPullOnRefresh:$SkipGitPullOnInventoryRefresh
    }
}

$manifest = Get-Content -LiteralPath $ManifestPath -Raw -Encoding utf8 | ConvertFrom-Json
$outDir = Join-Path $RepoRoot "docs\private\homelab\reports"
if ($manifest.outDir) {
    $outDir = $manifest.outDir -replace "/", [IO.Path]::DirectorySeparatorChar
    if (-not [IO.Path]::IsPathRooted($outDir)) {
        $outDir = Join-Path $RepoRoot $outDir
    }
}
New-Item -ItemType Directory -Force -Path $outDir | Out-Null

$stamp = Get-Date -Format "yyyyMMdd_HHmmss"
$fping = Get-Command fping -ErrorAction SilentlyContinue

$privArg = ""
if ($Privileged) { $privArg = " --privileged" }

function Get-SshHostname {
    param([string]$Alias)
    $g = & ssh -G $Alias 2>$null
    if ($LASTEXITCODE -ne 0) { return $null }
    foreach ($line in $g) {
        if ($line -match '^hostname (.+)$') {
            return $Matches[1].Trim()
        }
    }
    return $null
}

function Invoke-CmdCapture {
    param([Parameter(Mandatory = $true)][string]$CmdLine)
    return (& cmd.exe /c $CmdLine | Out-String)
}

$master = [System.Text.StringBuilder]::new()
[void]$master.AppendLine("=== lab-completao-orchestrate $stamp ===")
[void]$master.AppendLine("repo: $RepoRoot")

foreach ($h in $manifest.hosts) {
    $alias = $h.sshHost
    if (-not $alias) { continue }

    $healthUrl = ""
    if ($h.PSObject.Properties.Name -contains "completaoHealthUrl" -and $h.completaoHealthUrl) {
        $healthUrl = [string]$h.completaoHealthUrl
    }

    $skipEngineImport = $false
    if ($h.PSObject.Properties.Name -contains "completaoSkipEngineImport") {
        $v = $h.completaoSkipEngineImport
        if ($v -eq $true -or "$v" -eq "true") { $skipEngineImport = $true }
    }
    if ($h.PSObject.Properties.Name -contains "completaoEngineMode") {
        $em = [string]$h.completaoEngineMode
        if ($em -eq "container") { $skipEngineImport = $true }
    }

    Write-Host "=== Host: $alias ===" -ForegroundColor Cyan
    $hostLogSb = [System.Text.StringBuilder]::new()
    [void]$hostLogSb.AppendLine("=== lab-completao-orchestrate $stamp host=$alias ===")
    [void]$master.AppendLine("")
    [void]$master.AppendLine("### SSH host: $alias ###")

    if (-not $SkipFping -and $fping) {
        $hn = Get-SshHostname -Alias $alias
        if ($hn) {
            $fp = & fping -c 1 -t 400 $hn 2>&1 | Out-String
            [void]$hostLogSb.AppendLine($fp)
            [void]$master.AppendLine($fp)
        }
    }

    $probeCmd = "ssh.exe -o BatchMode=yes -o ConnectTimeout=12 $alias `"echo LABOP_SSH_OK`" 2>&1"
    $probeText = Invoke-CmdCapture -CmdLine $probeCmd
    if ($LASTEXITCODE -ne 0 -or $probeText -notmatch "LABOP_SSH_OK") {
        Write-Warning "SSH probe failed for $alias - skip."
        [void]$master.AppendLine("SSH probe FAILED")
        [void]$hostLogSb.AppendLine("SSH probe FAILED")
        $safe = ($alias -replace '[^\w\-\.]', '_')
        Set-Content -LiteralPath (Join-Path $outDir "${safe}_${stamp}_completao_host_smoke.log") -Value $hostLogSb.ToString() -Encoding utf8
        continue
    }

    foreach ($rp in $h.repoPaths) {
        if (-not $rp) { continue }
        $rpEsc = $rp -replace "'", "'\''"
        $healthEsc = ""
        if ($healthUrl) {
            $hu = $healthUrl -replace "'", "'\''"
            $healthEsc = " --health-url '$hu'"
        }
        $skipEsc = ""
        if ($skipEngineImport) { $skipEsc = " --skip-engine-import" }
        # Require an up-to-date clone (script ships on main); clear message if missing after git sync.
        $remoteCmd = "cd '$rpEsc' && if [ ! -f scripts/lab-completao-host-smoke.sh ]; then echo 'MISSING_SCRIPT: scripts/lab-completao-host-smoke.sh not in clone - on the host: cd to repo, git fetch origin && integrate origin/main (see docs/ops/LAB_COMPLETAO_RUNBOOK.md)'; exit 3; fi && bash scripts/lab-completao-host-smoke.sh$privArg$healthEsc$skipEsc 2>&1"
        $remoteCmdEsc = $remoteCmd.Replace('"', '\"')
        $remoteLine = "ssh.exe -o BatchMode=yes -o ConnectTimeout=180 $alias `"$remoteCmdEsc`" 2>&1"
        $remoteOut = Invoke-CmdCapture -CmdLine $remoteLine
        [void]$hostLogSb.AppendLine("--- repo: $rp ---")
        [void]$hostLogSb.AppendLine($remoteOut)
        [void]$master.AppendLine("--- repo: $rp ---")
        [void]$master.AppendLine($remoteOut)
    }

    if ($healthUrl) {
        try {
            $r = Invoke-WebRequest -Uri $healthUrl -TimeoutSec 15 -UseBasicParsing
            $curlLine = "dev-PC curl completaoHealthUrl: HTTP $($r.StatusCode) len=$($r.RawContentLength)"
            [void]$hostLogSb.AppendLine($curlLine)
            [void]$master.AppendLine($curlLine)
        } catch {
            $curlFail = "dev-PC curl completaoHealthUrl FAILED: $($_.Exception.Message)"
            [void]$hostLogSb.AppendLine($curlFail)
            [void]$master.AppendLine($curlFail)
        }
    }

    $safe = ($alias -replace '[^\w\-\.]', '_')
    $oneFile = Join-Path $outDir "${safe}_${stamp}_completao_host_smoke.log"
    Set-Content -LiteralPath $oneFile -Value $hostLogSb.ToString() -Encoding utf8
    Write-Host "Wrote $oneFile" -ForegroundColor Green
}

$allFile = Join-Path $outDir "completao_${stamp}_allhosts.log"
Set-Content -LiteralPath $allFile -Value $master.ToString() -Encoding utf8
Write-Host "Wrote consolidated $allFile" -ForegroundColor Green
Write-Host "Append lessons learned using docs/private/homelab/COMPLETAO_SESSION_TEMPLATE.pt_BR.md" -ForegroundColor DarkGray
