#Requires -Version 5.1
<#
.SYNOPSIS
  Optional high-density Lab-Op path: ephemeral config via scp + one-shot container run on capable nodes only.

.DESCRIPTION
  Manifest-driven orchestration remains the default: .\\scripts\\lab-completao-orchestrate.ps1 (no -HybridLabOpHighDensity173).
  Resolves SSH targets from **docs/private/homelab/lab-op-hosts.manifest.json** (`sshHost` + first `repoPaths` entry), same family as **lab-completao-orchestrate.ps1**.
  **LAB-NODE-02 scan path:** uses **`/home/leitao/Documents`** if present, else **`/home/leitao/documents`** (Zorin/GNOME vs lowercase checklist path).
  **Containers (LAB-NODE-01 / LAB-NODE-03 / lab-node-02):** if **`tmux has-session -t completao`** succeeds on the host, sends **`tmux send-keys -t completao '…' Enter`** (container runs **asynchronously** in that pane). Otherwise runs **`podman`/`docker`** via **`ssh … bash -lc '…'`** (one-shot, no tmux required). Narrow **sudoers** / **-Privileged** in **lab-completao-host-smoke** is for **read-only host probes** only.
  **LAB-NODE-04:** passive SSH uses the manifest **repo** path so **`.venv/bin/python3`** is the clone venv under **`Projects/dev/data-boar`**, not **`~/.venv`**.
  Requires OpenSSH **scp**/**ssh** on the dev PC and non-interactive SSH.

.NOTES
  Orquestrador v1.7.3 - Lab-Op High-Density Test (ASCII-only for Windows PowerShell 5.1).
#>
$ErrorActionPreference = "Stop"

$RepoRoot = (Get-Item $PSScriptRoot).Parent.FullName
$manifestPath = Join-Path $RepoRoot "docs\private\homelab\lab-op-hosts.manifest.json"

function Get-HybridNodesFromManifest {
    param([Parameter(Mandatory = $true)][string] $ManifestPath)
    if (-not (Test-Path -LiteralPath $ManifestPath)) {
        throw "Hybrid v1.7.3 requires $ManifestPath (same manifest as lab-completao-orchestrate.ps1). Copy from docs/private.example/homelab/lab-op-hosts.manifest.example.json"
    }
    $m = Get-Content -LiteralPath $ManifestPath -Raw -Encoding utf8 | ConvertFrom-Json

    function Get-FirstRepoPath {
        param($HostEntry)
        if (-not $HostEntry) {
            return $null
        }
        if ($HostEntry.PSObject.Properties.Name -notcontains "repoPaths" -or -not $HostEntry.repoPaths) {
            return $null
        }
        $arr = @($HostEntry.repoPaths)
        if ($arr.Count -lt 1) {
            return $null
        }
        return [string]$arr[0]
    }

    $ordered = [System.Collections.Generic.List[object]]::new()
    $roleDefs = @(
        @{ Name = "lab-node-02"; Regex = '(?i)^lab-node-02$'; Type = "swarm" },
        @{ Name = "lab-node-01"; Regex = '(?i)lab-node-01'; Type = "podman" },
        @{ Name = "LAB-NODE-03"; Regex = '(?i)LAB-NODE-03|^minibt$'; Type = "docker" },
        @{ Name = "LAB-NODE-04"; Regex = '(?i)LAB-NODE-04'; Type = "passive" }
    )

    foreach ($rd in $roleDefs) {
        foreach ($h in $m.hosts) {
            if (-not $h.sshHost) {
                continue
            }
            if ([string]$h.sshHost -match $rd.Regex) {
                $ordered.Add(@{
                    Name     = $rd.Name
                    SshHost  = [string]$h.sshHost
                    Type     = $rd.Type
                    RepoPath = (Get-FirstRepoPath $h)
                })
                break
            }
        }
    }

    if ($ordered.Count -eq 0) {
        throw "No recognizable lab hosts in manifest (expected sshHost matching lab-node-02, lab-node-01, LAB-NODE-03, or LAB-NODE-04)."
    }
    return $ordered
}

$Nodes = Get-HybridNodesFromManifest -ManifestPath $manifestPath

# Optional tmux target (operator may `tmux new -s completao` on a node); detected per host before container step.
$TmuxSessionName = "completao"

# Docker Hub semver tag (see docs/releases/1.7.3.md); avoid :v1.7.3 unless that tag exists on Hub.
$ImageRef = "fabioleitao/data_boar:1.7.3"

function Deploy-Config {
    param(
        [Parameter(Mandatory = $true)] $Node,
        [Parameter(Mandatory = $true)][string] $Path
    )
    $projectName = "Lab-Completao-$($Node.Name)"
    $content = @"
project_name: "$projectName"
scan_options:
  heuristics_level: high
  recursive: true
targets:
  - type: filesystem
    path: "$Path"
"@
    $temp = New-TemporaryFile
    try {
        Set-Content -LiteralPath $temp.FullName -Value $content -Encoding ascii
        $dest = "$($Node.SshHost):/tmp/config_databoar.yaml"
        & scp.exe -q $temp.FullName $dest
        if ($LASTEXITCODE -ne 0) {
            throw "scp failed for $($Node.Name) -> $dest"
        }
    } finally {
        Remove-Item -LiteralPath $temp.FullName -Force -ErrorAction SilentlyContinue
    }
}

function Invoke-LAB-NODE-04PassiveSsh {
    param(
        [Parameter(Mandatory = $true)] $Node,
        [Parameter(Mandatory = $true)][string] $RepoPath
    )
    $e = $RepoPath -replace "'", "'\''"
    $inner = "cd '$e' && { echo '=== LAB-NODE-04 passive (repo .venv under clone) ==='; if [ -x .venv/bin/python3 ]; then echo 'using .venv/bin/python3 -m databoar'; .venv/bin/python3 -m databoar --help 2>&1 | head -n 40 || true; elif command -v python3 >/dev/null 2>&1; then echo 'fallback: python3 -m databoar'; python3 -m databoar --help 2>&1 | head -n 40 || true; else echo 'SKIP_NO_PYTHON_OR_VENV'; fi; echo '=== logs ==='; journalctl -n 100 --no-pager 2>/dev/null || true; df -h 2>/dev/null | head -n 16 || true; } 2>&1"
    $innerEsc = $inner.Replace('"', '\"')
    $target = $Node.SshHost
    & ssh.exe -o BatchMode=yes -o ConnectTimeout=30 $target $innerEsc
    if ($LASTEXITCODE -ne 0) {
        Write-Warning "LAB-NODE-04 passive SSH failed for $($Node.Name) ($target) (skip-on-failure)."
    }
}

function Test-HybridSshOk {
    param([string]$Target)
    & ssh.exe -o BatchMode=yes -o ConnectTimeout=12 $Target "echo HYBRID_SSH_OK" 2>&1 | Out-Null
    return ($LASTEXITCODE -eq 0)
}

function Test-HybridRemoteDir {
    param([string]$Target, [string]$DirPath)
    $de = $DirPath -replace "'", "'\''"
    $out = & ssh.exe -o BatchMode=yes -o ConnectTimeout=20 $Target "test -d '$de' && echo HYBRID_DIR_OK || echo HYBRID_DIR_FAIL" 2>&1 | Out-String
    return ($out -match "HYBRID_DIR_OK")
}

function Resolve-LAB-NODE-02ScanPath {
    param([string]$Target)
    foreach ($cand in @("/home/leitao/Documents", "/home/leitao/documents")) {
        if (Test-HybridRemoteDir -Target $Target -DirPath $cand) {
            Write-Host "Hybrid lab-node-02: using scan path $cand" -ForegroundColor DarkGray
            return $cand
        }
    }
    return $null
}

function Test-HybridTmuxSession {
    param(
        [Parameter(Mandatory = $true)][string] $Target,
        [Parameter(Mandatory = $true)][string] $SessionName
    )
    $sn = $SessionName -replace "'", "'\''"
    $out = & ssh.exe -o BatchMode=yes -o ConnectTimeout=15 $Target "tmux has-session -t '$sn' 2>/dev/null && echo HYBRID_TMUX_OK || echo HYBRID_TMUX_NO" 2>&1 | Out-String
    return ($out -match "HYBRID_TMUX_OK")
}

function Invoke-HybridContainerRun {
    param(
        [Parameter(Mandatory = $true)][string] $Target,
        [Parameter(Mandatory = $true)][string] $Engine,
        [Parameter(Mandatory = $true)][string] $Image,
        [Parameter(Mandatory = $true)][string] $NodeLabel,
        [int]$ConnectTimeoutSec = 300
    )
    if ($Engine -eq "podman") {
        $runLine = "podman run --rm -v /tmp/config_databoar.yaml:/app/config.yaml:Z $Image"
    } else {
        $runLine = "docker run --rm -v /tmp/config_databoar.yaml:/app/config.yaml $Image"
    }

    if (Test-HybridTmuxSession -Target $Target -SessionName $TmuxSessionName) {
        Write-Host "Hybrid ${NodeLabel}: tmux session '$TmuxSessionName' found — send-keys (run continues in pane)." -ForegroundColor DarkCyan
        $remote = "tmux send-keys -t $TmuxSessionName '$runLine' Enter"
        & ssh.exe -o BatchMode=yes -o ConnectTimeout=30 $Target $remote
        return $LASTEXITCODE
    }

    Write-Host "Hybrid ${NodeLabel}: no tmux session '$TmuxSessionName' — direct run (bash -lc)." -ForegroundColor DarkGray
    $inner = $runLine
    $remote = "bash -lc '$inner'"
    & ssh.exe -o BatchMode=yes -o ConnectTimeout=$ConnectTimeoutSec -o ServerAliveInterval=15 -o ServerAliveCountMax=20 $Target $remote
    return $LASTEXITCODE
}

foreach ($n in $Nodes) {
    Write-Host ">>> Preparando No: $($n.Name) ($($n.SshHost))" -ForegroundColor Cyan
    $target = $n.SshHost
    if (-not (Test-HybridSshOk -Target $target)) {
        Write-Warning "Hybrid health: SSH probe failed for $($n.Name) ($target) - skip (skip-on-failure)."
        continue
    }

    if ($n.Type -eq "passive") {
        $repoPath = $n.RepoPath
        if (-not $repoPath) {
            Write-Warning "Hybrid: LAB-NODE-04 has no repoPaths[0] in manifest - skip passive (skip-on-failure)."
            continue
        }
        if (-not (Test-HybridRemoteDir -Target $target -DirPath $repoPath)) {
            Write-Warning "Hybrid health: repo path missing on $($n.Name): $repoPath - skip passive (skip-on-failure)."
            continue
        }
        Invoke-LAB-NODE-04PassiveSsh -Node $n -RepoPath $repoPath
        continue
    }

    if ($n.Name -eq "lab-node-02") {
        $scanPath = Resolve-LAB-NODE-02ScanPath -Target $target
        if (-not $scanPath) {
            Write-Warning "Hybrid: lab-node-02 has neither /home/leitao/Documents nor /home/leitao/documents - skip container step (skip-on-failure)."
            continue
        }
    } else {
        $scanPath = "/home/leitao"
    }

    if (-not (Test-HybridRemoteDir -Target $target -DirPath $scanPath)) {
        Write-Warning "Hybrid health: scan path missing on $($n.Name): $scanPath - skip container step (skip-on-failure)."
        continue
    }

    Deploy-Config -Node $n -Path $scanPath

    $engine = if ($n.Type -eq "podman") { "podman" } else { "docker" }
    $rc = Invoke-HybridContainerRun -Target $target -Engine $engine -Image $ImageRef -NodeLabel $n.Name
    if ($rc -ne 0) {
        Write-Warning "Hybrid: $engine run failed on $($n.Name) ($target) exit=$rc - skip-on-failure."
    }
}

Write-Host "Hybrid v1.7.3 orchestration pass completed (per-node skip-on-failure where noted)." -ForegroundColor Green
exit 0
