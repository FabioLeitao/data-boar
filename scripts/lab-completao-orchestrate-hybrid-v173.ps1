#Requires -Version 5.1
<#
.SYNOPSIS
  Optional high-density Lab-Op path: ephemeral config via scp + container run on capable nodes only.

.DESCRIPTION
  Manifest-driven orchestration remains the default: .\\scripts\\lab-completao-orchestrate.ps1 (no -HybridLabOpHighDensity173).
  LAB-NODE-04 has no Docker (hardware-bound): this script never runs containers there; only SSH passive collect (python/venv try + logs).
  DB/Swarm-heavy scans belong on LAB-NODE-02 and LAB-NODE-01; LAB-NODE-03 stays on Docker image scan only (no host uv).
  Requires OpenSSH scp/ssh on the dev PC, non-interactive SSH, and a warmed tmux target pane for container nodes.

.NOTES
  Orquestrador v1.7.3 - Lab-Op High-Density Test (ASCII-only for Windows PowerShell 5.1).
#>
$ErrorActionPreference = "Stop"

$Nodes = @(
    @{ Name = "lab-node-02"; Type = "swarm"; User = "leitao"; IP = "lab-node-02.local" },
    @{ Name = "lab-node-01"; Type = "podman"; User = "leitao"; IP = "lab-node-01.local" },
    @{ Name = "LAB-NODE-03"; Type = "docker"; User = "leitao"; IP = "LAB-NODE-03.local" },
    @{ Name = "LAB-NODE-04"; Type = "passive"; User = "leitao"; IP = "LAB-NODE-04.local" }
)

$ImageRef = "fabioleitao/data_boar:v1.7.3"

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
        $dest = "$($Node.User)@$($Node.IP):/tmp/config_databoar.yaml"
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
        [Parameter(Mandatory = $true)][string] $ScanPath
    )
    $e = $ScanPath -replace "'", "'\''"
    $inner = "cd '$e' && { echo '=== LAB-NODE-04 passive (no Docker) ==='; if [ -x .venv/bin/python3 ]; then .venv/bin/python3 -m databoar --help 2>&1 | head -n 40 || true; elif command -v python3 >/dev/null 2>&1; then python3 -m databoar --help 2>&1 | head -n 40 || true; else echo 'SKIP_NO_PYTHON_OR_VENV'; fi; echo '=== logs ==='; journalctl -n 100 --no-pager 2>/dev/null || true; df -h 2>/dev/null | head -n 16 || true; } 2>&1"
    $innerEsc = $inner.Replace('"', '\"')
    $target = "$($Node.User)@$($Node.IP)"
    & ssh.exe -o BatchMode=yes -o ConnectTimeout=30 $target $innerEsc
    if ($LASTEXITCODE -ne 0) {
        Write-Warning "LAB-NODE-04 passive SSH failed for $($Node.Name) (skip-on-failure)."
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

foreach ($n in $Nodes) {
    Write-Host ">>> Preparando No: $($n.Name)" -ForegroundColor Cyan
    $target = "$($n.User)@$($n.IP)"
    if (-not (Test-HybridSshOk -Target $target)) {
        Write-Warning "Hybrid health: SSH probe failed for $($n.Name) ($target) - skip (skip-on-failure)."
        continue
    }

    $scanPath = if ($n.Name -eq "lab-node-02") { "/home/leitao/documents" } else { "/home/leitao" }

    if ($n.Type -eq "passive") {
        if (-not (Test-HybridRemoteDir -Target $target -DirPath $scanPath)) {
            Write-Warning "Hybrid health: scan path missing on $($n.Name): $scanPath - skip passive (skip-on-failure)."
            continue
        }
        Invoke-LAB-NODE-04PassiveSsh -Node $n -ScanPath $scanPath
        continue
    }

    if (-not (Test-HybridRemoteDir -Target $target -DirPath $scanPath)) {
        Write-Warning "Hybrid health: scan path missing on $($n.Name): $scanPath - skip container step (skip-on-failure)."
        continue
    }

    Deploy-Config -Node $n -Path $scanPath

    if ($n.Type -eq "podman") {
        $runCmd = "podman run --rm -v /tmp/config_databoar.yaml:/app/config.yaml:Z $ImageRef"
    } else {
        $runCmd = "docker run --rm -v /tmp/config_databoar.yaml:/app/config.yaml $ImageRef"
    }

    $remote = "tmux send-keys -t completao '$runCmd' Enter"
    & ssh.exe -o BatchMode=yes -o ConnectTimeout=30 $target $remote
    if ($LASTEXITCODE -ne 0) {
        Write-Warning "ssh/tmux send failed for $($n.Name) ($target) - skip-on-failure."
        continue
    }
}

Write-Host "Hybrid v1.7.3 orchestration pass completed (per-node skip-on-failure where noted)." -ForegroundColor Green
