#Requires -Version 5.1
<#
.SYNOPSIS
  Run lab-completao-host-smoke.sh on each LAB-OP host from the manifest; save consolidated logs.

.DESCRIPTION
  Same manifest as lab-op-sync-and-collect.ps1 (docs/private/homelab/lab-op-hosts.manifest.json).
  Optional per-host "completaoHealthUrl" for remote curl from the dev PC after SSH smoke.
  Optional per-host "completaoEngineMode":"container" or "completaoSkipEngineImport":true when the host
  runs Data Boar only via Docker/Swarm/Podman (skip bare-metal uv / import core.engine) - see LAB_COMPLETAO_RUNBOOK.md.
  Optional "completaoHardwareProfile":"pi3b" (or sshHost matching pi3b): no Docker/container smoke on that host;
  local python3/.venv only, else skip with warning, plus journal/syslog tail for analysis on T14/Latitude.
  Optional "completaoHardwareProfile":"mini-bt-void" (or sshHost matching mini-bt): forces skip-engine-import and logs
  Void xbps hint for mysqlclient build deps; keep DB/Swarm-heavy work on Latitude and T14.

  By default, runs scripts/lab-completao-inventory-preflight.ps1 (15-day freshness) and lab-op-sync-and-collect.ps1
  when private LAB_SOFTWARE_INVENTORY.md / OPERATOR_SYSTEM_MAP.md are missing or stale - see LAB_COMPLETAO_RUNBOOK.md.

  "Completao" is NOT pytest - see docs/ops/LAB_COMPLETAO_RUNBOOK.md.

  Optional -LabGitRef (or manifest "completaoTargetRef") runs lab-op-git-ensure-ref.ps1 before host smoke so LAB clones
  match a known ref (release tag, origin/main, branch tip). Use -AlignLabClonesToLabGitRef to reset clones (destructive).
  When pinning a tag, use -SkipGitPullOnInventoryRefresh so inventory refresh does not git pull clones to main first.

.EXAMPLE
  .\scripts\lab-completao-orchestrate.ps1

.EXAMPLE
  .\scripts\lab-completao-orchestrate.ps1 -Privileged

.EXAMPLE
  .\scripts\lab-completao-orchestrate.ps1 -Privileged -LabGitRef v1.2.0 -SkipGitPullOnInventoryRefresh

.EXAMPLE
  Optional fixed-matrix high-density container path (Podman on T14, Docker elsewhere, ephemeral /tmp config):
  .\scripts\lab-completao-orchestrate.ps1 -HybridLabOpHighDensity173
#>
param(
    [string] $ManifestPath = "",
    [string] $RepoRoot = "",
    [switch] $HybridLabOpHighDensity173,
    [switch] $Privileged,
    [switch] $SkipFping,
    [int] $InventoryMaxAgeDays = 15,
    [switch] $SkipInventoryPreflight,
    [switch] $SkipGitPullOnInventoryRefresh,
    [string] $LabGitRef = "",
    [switch] $SkipLabGitRefCheck,
    [switch] $AlignLabClonesToLabGitRef
)

$ErrorActionPreference = "Stop"
if ($HybridLabOpHighDensity173) {
    $hybrid = Join-Path $PSScriptRoot "lab-completao-orchestrate-hybrid-v173.ps1"
    if (-not (Test-Path -LiteralPath $hybrid)) {
        throw "Missing $hybrid"
    }
    & $hybrid
    exit $LASTEXITCODE
}
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

$effectiveLabRef = $LabGitRef
if (-not $effectiveLabRef -and $manifest.PSObject.Properties.Name -contains "completaoTargetRef" -and $manifest.completaoTargetRef) {
    $effectiveLabRef = [string]$manifest.completaoTargetRef
}
if ($effectiveLabRef -and -not $SkipLabGitRefCheck) {
    $ensureScript = Join-Path $RepoRoot "scripts\lab-op-git-ensure-ref.ps1"
    if (-not (Test-Path -LiteralPath $ensureScript)) {
        throw "Missing $ensureScript"
    }
    $ensureMode = "Check"
    if ($AlignLabClonesToLabGitRef) {
        $ensureMode = "Reset"
    }
    Write-Host "lab-completao-orchestrate: lab-op-git-ensure-ref ref=$effectiveLabRef mode=$ensureMode" -ForegroundColor Cyan
    & $ensureScript -RepoRoot $RepoRoot -ManifestPath $ManifestPath -Ref $effectiveLabRef -Mode $ensureMode -SkipFping:$SkipFping
    if ($LASTEXITCODE -ne 0) {
        throw "lab-op-git-ensure-ref failed (ref=$effectiveLabRef mode=$ensureMode). Align LAB clones or use -SkipLabGitRefCheck. See docs/ops/LAB_COMPLETAO_RUNBOOK.md (Target git ref for reproducible completao)."
    }
}

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

function Get-CompletaoHardwareProfile {
    param($HostEntry, [string]$Alias)
    if ($HostEntry.PSObject.Properties.Name -contains "completaoHardwareProfile" -and $HostEntry.completaoHardwareProfile) {
        return [string]$HostEntry.completaoHardwareProfile
    }
    if ($Alias -match "pi3b") {
        return "pi3b"
    }
    if ($Alias -match "mini-bt|minibt") {
        return "mini-bt-void"
    }
    return ""
}

function Test-CompletaoSshRepoDir {
    param([string]$Alias, [string]$RepoPath)
    if (-not $RepoPath) {
        return $true
    }
    $e = $RepoPath -replace "'", "'\''"
    $inner = "test -d '$e' && echo COMPLETAO_HEALTH_OK || echo COMPLETAO_HEALTH_FAIL"
    $innerEsc = $inner.Replace('"', '\"')
    $remoteLine = "ssh.exe -o BatchMode=yes -o ConnectTimeout=25 $Alias `"$innerEsc`" 2>&1"
    $out = Invoke-CmdCapture -CmdLine $remoteLine
    if ($LASTEXITCODE -ne 0) {
        return $false
    }
    return ($out -match "COMPLETAO_HEALTH_OK")
}

function Build-Pi3bPassiveRemoteCmd {
    param([string]$RepoPathEsc)
    # Single-line bash for ssh: no Docker; try venv/system python -m databoar; collect logs for T14/Latitude review.
    return "cd '$RepoPathEsc' && { echo '=== pi3b passive path (hardware: no Docker) ==='; if [ -x .venv/bin/python3 ]; then echo 'using .venv/bin/python3 -m databoar --help'; .venv/bin/python3 -m databoar --help 2>&1 | head -n 50 || true; elif command -v python3 >/dev/null 2>&1; then echo 'no .venv; trying python3 -m databoar --help'; python3 -m databoar --help 2>&1 | head -n 50 || true; else echo 'SKIP_NO_PYTHON_OR_VENV'; fi; echo '=== recent logs (journal/syslog) ==='; journalctl -n 120 --no-pager 2>/dev/null || true; test -r /var/log/syslog && tail -n 80 /var/log/syslog 2>/dev/null || true; test -r /var/log/messages && tail -n 80 /var/log/messages 2>/dev/null || true; df -h 2>/dev/null | head -n 24 || true; } 2>&1"
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

    $hwProfile = Get-CompletaoHardwareProfile -HostEntry $h -Alias $alias
    if ($hwProfile -match '^mini-bt-void') {
        $skipEngineImport = $true
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
        Write-Warning "SSH probe failed for $alias - skip (skip-on-failure)."
        [void]$master.AppendLine("SSH probe FAILED (skip-on-failure)")
        [void]$hostLogSb.AppendLine("SSH probe FAILED (skip-on-failure)")
        $safe = ($alias -replace '[^\w\-\.]', '_')
        Set-Content -LiteralPath (Join-Path $outDir "${safe}_${stamp}_completao_host_smoke.log") -Value $hostLogSb.ToString() -Encoding utf8
        continue
    }

    $firstRepo = $null
    foreach ($rp in $h.repoPaths) {
        if ($rp) {
            $firstRepo = $rp
            break
        }
    }
    if ($firstRepo -and -not (Test-CompletaoSshRepoDir -Alias $alias -RepoPath $firstRepo)) {
        Write-Warning "Completao health check failed (repo dir missing or SSH error) for $alias path=$firstRepo - skip host (skip-on-failure)."
        [void]$master.AppendLine("REPO_HEALTH_FAIL skip-on-failure firstRepo=$firstRepo")
        [void]$hostLogSb.AppendLine("REPO_HEALTH_FAIL skip-on-failure firstRepo=$firstRepo")
        $safe = ($alias -replace '[^\w\-\.]', '_')
        Set-Content -LiteralPath (Join-Path $outDir "${safe}_${stamp}_completao_host_smoke.log") -Value $hostLogSb.ToString() -Encoding utf8
        continue
    }

    if ($hwProfile -match '^mini-bt-void') {
        $voidNote = "LAB_NOTE mini-bt Void: run sudo xbps-install -S libmariadbclient-devel pkg-config if mysqlclient build fails; if uv sync still fails, use a private clone branch or gitignored local pyproject overlay on that host only (do not strip DB deps from the canonical Git repo); keep MariaDB/DB scan load on Latitude/T14; this host: filesystem + logs + skip-engine-import."
        [void]$hostLogSb.AppendLine($voidNote)
        [void]$master.AppendLine($voidNote)
        Write-Host $voidNote -ForegroundColor DarkYellow
    }

    if ($hwProfile -match '^pi3b') {
        $piRp = $firstRepo
        if (-not $piRp) {
            $piRp = "/home/leitao"
            $piNote = "PI3B_NOTE no repoPaths in manifest; using passive base $piRp (NFS/home or operator default)."
            Write-Host $piNote -ForegroundColor DarkYellow
            [void]$master.AppendLine($piNote)
            [void]$hostLogSb.AppendLine($piNote)
        }
        if (-not (Test-CompletaoSshRepoDir -Alias $alias -RepoPath $piRp)) {
            Write-Warning "Pi3B health: passive base missing or unreadable $piRp - skip host (skip-on-failure)."
            [void]$master.AppendLine("PI3B_HEALTH_FAIL skip-on-failure path=$piRp")
            [void]$hostLogSb.AppendLine("PI3B_HEALTH_FAIL skip-on-failure path=$piRp")
            $safe = ($alias -replace '[^\w\-\.]', '_')
            Set-Content -LiteralPath (Join-Path $outDir "${safe}_${stamp}_completao_host_smoke.log") -Value $hostLogSb.ToString() -Encoding utf8
            continue
        }
        $rpEsc = $piRp -replace "'", "'\''"
        $piRemote = Build-Pi3bPassiveRemoteCmd -RepoPathEsc $rpEsc
        $piRemoteEsc = $piRemote.Replace('"', '\"')
        $piLine = "ssh.exe -o BatchMode=yes -o ConnectTimeout=180 $alias `"$piRemoteEsc`" 2>&1"
        $piOut = Invoke-CmdCapture -CmdLine $piLine
        [void]$hostLogSb.AppendLine("--- pi3b passive (no Docker / no container smoke) repo: $piRp ---")
        [void]$hostLogSb.AppendLine($piOut)
        [void]$master.AppendLine("--- pi3b passive repo: $piRp ---")
        [void]$master.AppendLine($piOut)
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
        Write-Host "Wrote $oneFile (pi3b passive path)" -ForegroundColor Green
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
