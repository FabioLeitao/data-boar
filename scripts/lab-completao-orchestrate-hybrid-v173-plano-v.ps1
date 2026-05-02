#Requires -Version 5.1
<#
.SYNOPSIS
  Plano V: Pre-flight helpers (slice 2) + cross-runtime orchestration loop (slice 3), ASCII-only.

.DESCRIPTION
  Slice 2 - Test-DataBoarMounts / Test-LocalSource: SSH material checks (mounts + paths).

  Slice 3 - Invoke-DataBoarPlanVInventoryOrchestration: for each inventory row, mkdir ephemeral tree on Linux,
  SCP boar_config.yaml, then Swarm stack deploy OR podman run OR metal nohup. Stack names, stack files,
  and podman container names include RunID to avoid collisions.

  Slice 4 - Invoke-DataBoarPlanVResilientRun: on terminating error, catch renames remote boar_config.yaml/config.yaml
  to *.failed (forensic); finally always prints coverage report (RunId, SMB/NFS/SSHFS probe, local log paths);
  optional teardown removes stack / podman session containers / metal PID for this RunId (zombie reduction).

.NOTES
  Hybrid family: ssh.exe / scp.exe -o BatchMode=yes pattern matches lab-completao-orchestrate-hybrid-v173.ps1.
  Swarm: if -StackYamlLocalPath is omitted, emits a minimal bind-mounted stack under the remote bench config dir.
  Podman: operator-requested --privileged -v /:/host:ro (high blast radius) plus config bind; lab-only.
  Example inventory uses 192.0.2.0/24 documentation addresses (RFC 5737 TEST-NET-1), not RFC1918 literals.
#>

Set-StrictMode -Version 2
$ErrorActionPreference = "Stop"

function Resolve-DataBoarSshTarget {
    param(
        [Parameter(Mandatory = $true)][string] $NodeName,
        [Parameter(Mandatory = $true)][string] $IpAddress,
        [string] $SshUser = ""
    )
    $u = $SshUser
    if (-not $u) {
        $u = [string]$env:DATA_BOAR_LAB_SSH_USER
    }
    if (-not $u) {
        $u = "leitao"
    }
    return "${u}@${IpAddress}"
}

function Get-RemoteMountEntryCount {
    param(
        [Parameter(Mandatory = $true)][string] $SshTarget,
        [Parameter(Mandatory = $true)][string] $MountPath,
        [int] $ConnectTimeoutSeconds = 20
    )
    $p = $MountPath -replace "'", "'\''"
    # ls -A: exclude . and .. so count 0 means truly no entries (RCDD-style material check).
    $inner = "if [ ! -d '$p' ]; then echo DATABOAR_COUNT_MISSING; exit 2; fi; n=`$(ls -A '$p' 2>/dev/null | wc -l); echo DATABOAR_COUNT:`$n"
    $innerEsc = $inner.Replace('"', '\"')
    $out = & ssh.exe -o BatchMode=yes -o ConnectTimeout=$ConnectTimeoutSeconds -o StrictHostKeyChecking=accept-new $SshTarget $innerEsc 2>&1 | Out-String
    return @{
        Raw    = $out
        Exit   = $LASTEXITCODE
        Target = $SshTarget
        Path   = $MountPath
    }
}

function Test-DataBoarMounts {
    <#
    .SYNOPSIS
      Pre-flight: SSH to node and verify bench mounts are present and non-empty.
    .PARAMETER NodeName
      Label for logs (RCDD evidence bundle).
    .PARAMETER IpAddress
      IPv4 or resolvable host for SSH (combined with SshUser unless SshTarget is set).
    .PARAMETER SshTarget
      Optional full ssh destination user@host. When set, IpAddress/SshUser are ignored for SSH.
    .PARAMETER SshUser
      SSH username when building user@IpAddress (default: env DATA_BOAR_LAB_SSH_USER, then leitao).
    .PARAMETER ConnectTimeoutSeconds
      Per-invocation SSH connect timeout.
    #>
    param(
        [Parameter(Mandatory = $true)][string] $NodeName,
        [Parameter(Mandatory = $true)][string] $IpAddress,
        [string] $SshTarget = "",
        [string] $SshUser = "",
        [int] $ConnectTimeoutSeconds = 20
    )
    $mounts = @(
        "/mnt/smb_synthetic",
        "/mnt/nfs_bench",
        "/mnt/sshfs_lab"
    )
    $target = if ($SshTarget) { $SshTarget } else { (Resolve-DataBoarSshTarget -NodeName $NodeName -IpAddress $IpAddress -SshUser $SshUser) }

    Write-Host "PreFlight mounts: node=$NodeName ssh=$target" -ForegroundColor Cyan

    foreach ($m in $mounts) {
        $r = Get-RemoteMountEntryCount -SshTarget $target -MountPath $m -ConnectTimeoutSeconds $ConnectTimeoutSeconds
        if ($r.Exit -ne 0) {
            Write-Warning "PreFlight mounts FAIL node=$NodeName path=$m ssh_exit=$($r.Exit) raw=$($r.Raw)"
            return $false
        }
        $line = ($r.Raw -split "`r?`n" | Where-Object { $_ -match "DATABOAR_COUNT:" } | Select-Object -First 1)
        if (-not $line) {
            Write-Warning "PreFlight mounts FAIL node=$NodeName path=$m no_count_line raw=$($r.Raw)"
            return $false
        }
        if ($line -match "DATABOAR_COUNT_MISSING") {
            Write-Warning "PreFlight mounts FAIL node=$NodeName path=$m missing_dir"
            return $false
        }
        $digits = [regex]::Match($line, "DATABOAR_COUNT:\s*(\d+)").Groups[1].Value
        if (-not $digits) {
            Write-Warning "PreFlight mounts FAIL node=$NodeName path=$m unparsable_line=$line"
            return $false
        }
        $n = 0
        [void][int]::TryParse($digits, [ref]$n)
        if ($n -le 0) {
            Write-Warning "PreFlight mounts FAIL node=$NodeName path=$m empty_or_zero count=$n (abort node)"
            return $false
        }
        Write-Host "  OK $m entries=$n" -ForegroundColor DarkGreen
    }
    return $true
}

function Test-LocalSource {
    <#
    .SYNOPSIS
      Pre-flight: verify Documents scan path and /var/log exist (material paths).
    .PARAMETER SshTarget
      When set (user@host), runs test -d on the remote node via SSH.
    .PARAMETER DocumentsPath
      Default /home/leitao/Documents (matches hybrid v1.7.3 latitude resolution primary).
    .PARAMETER LogPath
      Default /var/log.
    .PARAMETER ConnectTimeoutSeconds
      SSH timeout when SshTarget is used.
    #>
    param(
        [string] $SshTarget = "",
        [string] $DocumentsPath = "/home/leitao/Documents",
        [string] $LogPath = "/var/log",
        [int] $ConnectTimeoutSeconds = 20
    )
    if ($SshTarget) {
        $d = $DocumentsPath -replace "'", "'\''"
        $l = $LogPath -replace "'", "'\''"
        $inner = "if [ ! -d '$d' ]; then echo DATABOAR_LOCALSRC_FAIL_docs; exit 2; fi; if [ ! -d '$l' ]; then echo DATABOAR_LOCALSRC_FAIL_log; exit 3; fi; echo DATABOAR_LOCALSRC_OK"
        $innerEsc = $inner.Replace('"', '\"')
        $out = & ssh.exe -o BatchMode=yes -o ConnectTimeout=$ConnectTimeoutSeconds -o StrictHostKeyChecking=accept-new $SshTarget $innerEsc 2>&1 | Out-String
        if ($LASTEXITCODE -ne 0) {
            Write-Warning "Test-LocalSource SSH FAIL target=$SshTarget exit=$LASTEXITCODE raw=$out"
            return $false
        }
        if ($out -notmatch "DATABOAR_LOCALSRC_OK") {
            Write-Warning "Test-LocalSource SSH unexpected output target=$SshTarget raw=$out"
            return $false
        }
        Write-Host "Test-LocalSource OK (remote) $SshTarget docs=$DocumentsPath log=$LogPath" -ForegroundColor DarkGreen
        return $true
    }

    $okDocs = Test-Path -LiteralPath $DocumentsPath -PathType Container
    $okLog = Test-Path -LiteralPath $LogPath -PathType Container
    if (-not $okDocs) {
        Write-Warning "Test-LocalSource FAIL missing_docs local path=$DocumentsPath"
        return $false
    }
    if (-not $okLog) {
        Write-Warning "Test-LocalSource FAIL missing_log local path=$LogPath"
        return $false
    }
    Write-Host "Test-LocalSource OK (local) docs=$DocumentsPath log=$LogPath" -ForegroundColor DarkGreen
    return $true
}

function Test-DataBoarPlanVMountCountPositive {
    param(
        [Parameter(Mandatory = $true)][string] $SshTarget,
        [Parameter(Mandatory = $true)][string] $MountPath,
        [int] $ConnectTimeoutSeconds = 20
    )
    $r = Get-RemoteMountEntryCount -SshTarget $SshTarget -MountPath $MountPath -ConnectTimeoutSeconds $ConnectTimeoutSeconds
    if ($r.Exit -ne 0) {
        return $false
    }
    $line = ($r.Raw -split "`r?`n" | Where-Object { $_ -match "DATABOAR_COUNT:" } | Select-Object -First 1)
    if (-not $line -or ($line -match "DATABOAR_COUNT_MISSING")) {
        return $false
    }
    $digits = [regex]::Match($line, "DATABOAR_COUNT:\s*(\d+)").Groups[1].Value
    if (-not $digits) {
        return $false
    }
    $n = 0
    [void][int]::TryParse($digits, [ref]$n)
    return ($n -gt 0)
}

function Get-DataBoarPlanVMountProtocolStatus {
    param(
        [Parameter(Mandatory = $true)][string] $NodeName,
        [Parameter(Mandatory = $true)][string] $SshTarget,
        [int] $ConnectTimeoutSeconds = 20
    )
    $smb = "/mnt/smb_synthetic"
    $nfs = "/mnt/nfs_bench"
    $sshfs = "/mnt/sshfs_lab"
    return [pscustomobject]@{
        Node        = $NodeName
        SshTarget   = $SshTarget
        SmbOk       = (Test-DataBoarPlanVMountCountPositive -SshTarget $SshTarget -MountPath $smb -ConnectTimeoutSeconds $ConnectTimeoutSeconds)
        NfsOk       = (Test-DataBoarPlanVMountCountPositive -SshTarget $SshTarget -MountPath $nfs -ConnectTimeoutSeconds $ConnectTimeoutSeconds)
        SshfsOk     = (Test-DataBoarPlanVMountCountPositive -SshTarget $SshTarget -MountPath $sshfs -ConnectTimeoutSeconds $ConnectTimeoutSeconds)
        SmbPath     = $smb
        NfsPath     = $nfs
        SshfsPath   = $sshfs
    }
}

function Get-DataBoarPlanVRemoteBenchRoot {
    param([Parameter(Mandatory = $true)][string] $RunId)
    return "/tmp/databoar_bench_$RunId"
}

function Invoke-DataBoarPlanVRemoteSh {
    param(
        [Parameter(Mandatory = $true)][string] $SshTarget,
        [Parameter(Mandatory = $true)][string] $RemoteShellSnippet,
        [int] $ConnectTimeoutSeconds = 45
    )
    $innerEsc = $RemoteShellSnippet.Replace('"', '\"')
    $null = & ssh.exe -o BatchMode=yes -o ConnectTimeout=$ConnectTimeoutSeconds -o StrictHostKeyChecking=accept-new $SshTarget $innerEsc 2>&1
    return $LASTEXITCODE
}

function Copy-DataBoarPlanVToRemote {
    param(
        [Parameter(Mandatory = $true)][string] $LocalFile,
        [Parameter(Mandatory = $true)][string] $SshTarget,
        [Parameter(Mandatory = $true)][string] $RemotePath
    )
    if (-not (Test-Path -LiteralPath $LocalFile)) {
        throw "Copy-DataBoarPlanVToRemote: missing local file $LocalFile"
    }
    $rp = $RemotePath -replace "'", "'\''"
    $parent = Split-Path -Parent $RemotePath
    $parEsc = $parent -replace "'", "'\''"
    $mkEc = Invoke-DataBoarPlanVRemoteSh -SshTarget $SshTarget -RemoteShellSnippet "mkdir -p '$parEsc'"
    if ($mkEc -ne 0) {
        return $false
    }
    & scp.exe -q -o BatchMode=yes -o StrictHostKeyChecking=accept-new $LocalFile "${SshTarget}:${rp}"
    return ($LASTEXITCODE -eq 0)
}

function New-DataBoarPlanVSwarmStackYamlText {
    param(
        [Parameter(Mandatory = $true)][string] $RunId,
        [Parameter(Mandatory = $true)][string] $RemoteBenchRoot,
        [Parameter(Mandatory = $true)][string] $ImageRef
    )
    $cfgPath = "$RemoteBenchRoot/config/boar_config.yaml"
    $yaml = @"
version: '3.8'
services:
  scanner_${RunId}:
    image: ${ImageRef}
    volumes:
      - type: bind
        source: ${cfgPath}
        target: /app/config.yaml
        read_only: true
    networks:
      - databoar_planv_${RunId}
networks:
  databoar_planv_${RunId}:
    driver: overlay
"@
    return $yaml
}

function Invoke-DataBoarPlanVInventoryOrchestration {
    <#
    .SYNOPSIS
      Slice 3: loop inventory - SCP boar_config.yaml, then Swarm / Podman / Metal runtime branch.
    .PARAMETER RunId
      Ephemeral id (e.g. yyyyMMdd_HHmmss) - must be safe for docker stack and container names.
    .PARAMETER Inventory
      Array of hashtables: Name, Ip, Type (Swarm|Podman|Metal), optional SshUser, optional MetalBinary (remote path for Metal).
    .PARAMETER BoarConfigLocalPath
      Local path to boar_config.yaml (or operator-named YAML) to upload as remote .../config/boar_config.yaml.
    .PARAMETER StackYamlLocalPath
      Optional local compose/stack file for Swarm. When omitted, a minimal stack is generated (bind config only).
    .PARAMETER PodmanImage
      Image ref for Podman branch (and generated Swarm stack when no StackYamlLocalPath).
    .PARAMETER ConnectTimeoutSeconds
      SSH connect timeout.
    #>
    param(
        [Parameter(Mandatory = $true)][string] $RunId,
        [Parameter(Mandatory = $true)] $Inventory,
        [Parameter(Mandatory = $true)][string] $BoarConfigLocalPath,
        [string] $StackYamlLocalPath = "",
        [string] $PodmanImage = "",
        [int] $ConnectTimeoutSeconds = 45
    )
    if (-not $PodmanImage) {
        $PodmanImage = [string]$env:DATA_BOAR_PLANV_IMAGE
    }
    if (-not $PodmanImage) {
        $PodmanImage = "fabioleitao/data_boar:latest"
    }
    $remoteRoot = Get-DataBoarPlanVRemoteBenchRoot -RunId $RunId
    $stackName = "databoar_$RunId"
    $stackRemotePath = "$remoteRoot/config/stack.yaml"
    $tmpStack = [System.IO.Path]::GetTempFileName()
    try {
        foreach ($node in $Inventory) {
            $nName = [string]$node.Name
            $nIp = [string]$node.Ip
            $nType = ([string]$node.Type).Trim().ToLowerInvariant()
            $nUser = [string]$node.SshUser
            $ssh = Resolve-DataBoarSshTarget -NodeName $nName -IpAddress $nIp -SshUser $nUser
            Write-Host "PlanV orchestrate: node=$nName type=$nType ssh=$ssh root=$remoteRoot" -ForegroundColor Cyan

            $mk = "mkdir -p '$remoteRoot/bin' '$remoteRoot/config' '$remoteRoot/results' '$remoteRoot/logs' && echo PLANV_MK_OK"
            if ((Invoke-DataBoarPlanVRemoteSh -SshTarget $ssh -RemoteShellSnippet $mk -ConnectTimeoutSeconds $ConnectTimeoutSeconds) -ne 0) {
                throw "PlanV: mkdir failed on $nName ($ssh)"
            }
            $remoteCfg = "$remoteRoot/config/boar_config.yaml"
            if (-not (Copy-DataBoarPlanVToRemote -LocalFile $BoarConfigLocalPath -SshTarget $ssh -RemotePath $remoteCfg)) {
                throw "PlanV: scp boar_config failed on $nName ($ssh)"
            }

            if ($nType -eq "swarm") {
                if ($StackYamlLocalPath -and (Test-Path -LiteralPath $StackYamlLocalPath)) {
                    if (-not (Copy-DataBoarPlanVToRemote -LocalFile $StackYamlLocalPath -SshTarget $ssh -RemotePath $stackRemotePath)) {
                        throw "PlanV: scp stack yaml failed on $nName"
                    }
                } else {
                    $body = New-DataBoarPlanVSwarmStackYamlText -RunId $RunId -RemoteBenchRoot $remoteRoot -ImageRef $PodmanImage
                    $enc = New-Object System.Text.UTF8Encoding $false
                    [System.IO.File]::WriteAllText($tmpStack, $body, $enc)
                    if (-not (Copy-DataBoarPlanVToRemote -LocalFile $tmpStack -SshTarget $ssh -RemotePath $stackRemotePath)) {
                        throw "PlanV: scp generated stack failed on $nName"
                    }
                }
                $sr = $stackRemotePath -replace "'", "'\''"
                $deploy = "docker stack deploy -c '$sr' '$stackName' && echo PLANV_STACK_OK"
                if ((Invoke-DataBoarPlanVRemoteSh -SshTarget $ssh -RemoteShellSnippet $deploy -ConnectTimeoutSeconds 120) -ne 0) {
                    throw "PlanV: docker stack deploy failed on $nName stack=$stackName"
                }
                Write-Host "  Swarm stack deployed: $stackName (compose $stackRemotePath)" -ForegroundColor DarkGreen
            }
            elseif ($nType -eq "podman") {
                $slug = ($nName -replace '[^a-zA-Z0-9]', '_').ToLowerInvariant()
                $cname = "databoar_${RunId}_$slug"
                $cfgEsc = $remoteCfg -replace "'", "'\''"
                $runInner = "podman rm -f '$cname' 2>/dev/null || true; podman run -d --name '$cname' --privileged -v /:/host:ro -v '$cfgEsc':/app/config.yaml:ro '$PodmanImage' && echo PLANV_PODMAN_OK"
                if ((Invoke-DataBoarPlanVRemoteSh -SshTarget $ssh -RemoteShellSnippet $runInner -ConnectTimeoutSeconds 120) -ne 0) {
                    throw "PlanV: podman run failed on $nName container=$cname"
                }
                Write-Host "  Podman container: $cname (privileged + host bind per operator spec)" -ForegroundColor DarkGreen
            }
            elseif ($nType -eq "metal") {
                $metalBin = [string]$node.MetalBinary
                if (-not $metalBin) {
                    $metalBin = [string]$env:DATA_BOAR_PLANV_METAL_BINARY
                }
                if (-not $metalBin) {
                    $metalBin = "/usr/local/bin/databoar"
                }
                $mb = $metalBin -replace "'", "'\''"
                $logF = "$remoteRoot/logs/metal_${RunId}.log" -replace "'", "'\''"
                $pidF = "$remoteRoot/logs/metal_${RunId}.pid" -replace "'", "'\''"
                $metalInner = "chmod +x '$mb' 2>/dev/null || true; nohup '$mb' >'$logF' 2>&1 & echo `$! > '$pidF' && sync && echo PLANV_METAL_OK"
                if ((Invoke-DataBoarPlanVRemoteSh -SshTarget $ssh -RemoteShellSnippet $metalInner -ConnectTimeoutSeconds 60) -ne 0) {
                    throw "PlanV: metal launch failed on $nName binary=$metalBin"
                }
                Write-Host "  Metal nohup started binary=$metalBin log=$remoteRoot/logs/metal_${RunId}.log" -ForegroundColor DarkGreen
            }
            else {
                throw "PlanV: unknown Type '$($node.Type)' for node $nName (expected Swarm|Podman|Metal)"
            }
        }
    }
    finally {
        if (Test-Path -LiteralPath $tmpStack) {
            Remove-Item -LiteralPath $tmpStack -Force -ErrorAction SilentlyContinue
        }
    }
    Write-Host "PlanV orchestration finished for RunId=$RunId stack_or_prefix=$stackName" -ForegroundColor Cyan
}

function Invoke-DataBoarPlanVForensicConfigRenameOnAllNodes {
    <#
    .SYNOPSIS
      Fatal-error path: rename remote boar_config.yaml and config.yaml to *.failed for forensic evidence (all inventory nodes).
    #>
    $ctx = $script:DataBoarPlanVRunContext
    if (-not $ctx -or -not $ctx.Inventory) {
        return
    }
    $rr = [string]$ctx.RemoteRoot
    foreach ($node in $ctx.Inventory) {
        $nUser = [string]$node.SshUser
        $ssh = Resolve-DataBoarSshTarget -NodeName ([string]$node.Name) -IpAddress ([string]$node.Ip) -SshUser $nUser
        $snippet = "for f in boar_config.yaml config.yaml; do fp='$rr/config/'`"`$f`"; if [ -f `"`$fp`" ]; then mv -f `"`$fp`" `"`$fp.failed`" && echo PLANV_FORENSIC_MV:`"`$f`"; fi; done"
        $null = Invoke-DataBoarPlanVRemoteSh -SshTarget $ssh -RemoteShellSnippet $snippet -ConnectTimeoutSeconds 30
    }
}

function Invoke-DataBoarPlanVWriteCoverageReport {
    $ctx = $script:DataBoarPlanVRunContext
    Write-Host ""
    Write-Host "=== Relatorio de Cobertura de Scan (Lessons Learned / Plan V) ===" -ForegroundColor Yellow
    if (-not $ctx) {
        Write-Host "RunId: (context missing)" -ForegroundColor Red
        Write-Host "=== Fim do relatorio ===" -ForegroundColor Yellow
        return
    }
    Write-Host ("RunId: {0}" -f $ctx.RunId)
    Write-Host ("RemoteBenchRoot (all nodes): {0}" -f $ctx.RemoteRoot)
    Write-Host ("LocalLogRoot (orchestrator): {0}" -f $ctx.LocalLogRoot)
    Write-Host "Local log paths:" -ForegroundColor Cyan
    Write-Host ("  - {0}" -f (Join-Path $ctx.LocalLogRoot "logs"))
    if ($ctx.TranscriptPath) {
        Write-Host ("  - Transcript: {0}" -f $ctx.TranscriptPath)
    }
    Write-Host "Status de acesso por protocolo (material: mount nao vazio):" -ForegroundColor Cyan
    foreach ($row in $ctx.ProtocolRows) {
        $smbS = if ($row.SmbOk) { "OK" } else { "FAIL" }
        $nfsS = if ($row.NfsOk) { "OK" } else { "FAIL" }
        $sfsS = if ($row.SshfsOk) { "OK" } else { "FAIL" }
        Write-Host ("  Node={0} SSH={1} SMB({2})={3} NFS({4})={5} SSHFS({6})={7}" -f $row.Node, $row.SshTarget, $row.SmbPath, $smbS, $row.NfsPath, $nfsS, $row.SshfsPath, $sfsS)
    }
    $ok = $ctx.OrchestrationOk
    Write-Host ("Orchestration completed without throw: {0}" -f $ok)
    Write-Host ("Fatal path handled (forensic rename attempted): {0}" -f $ctx.TrapFired)
    Write-Host "=== Fim do relatorio ===" -ForegroundColor Yellow
    Write-Host ""
}

function Invoke-DataBoarPlanVCleanupSessionResources {
    <#
    .SYNOPSIS
      Stop podman containers, remove swarm stack, stop metal PID for this RunId; light remote wait to reap children.
    #>
    $ctx = $script:DataBoarPlanVRunContext
    if (-not $ctx -or -not $ctx.Inventory) {
        return
    }
    $runId = [string]$ctx.RunId
    $stackName = [string]$ctx.StackName
    foreach ($node in $ctx.Inventory) {
        $nName = [string]$node.Name
        $nIp = [string]$node.Ip
        $nType = ([string]$node.Type).Trim().ToLowerInvariant()
        $nUser = [string]$node.SshUser
        $ssh = Resolve-DataBoarSshTarget -NodeName $nName -IpAddress $nIp -SshUser $nUser
        if ($nType -eq "swarm") {
            $inner = "docker stack rm '$stackName' 2>/dev/null || true; echo PLANV_STACK_RM_DONE"
            $null = Invoke-DataBoarPlanVRemoteSh -SshTarget $ssh -RemoteShellSnippet $inner -ConnectTimeoutSeconds 90
        }
        elseif ($nType -eq "podman") {
            $slug = ($nName -replace '[^a-zA-Z0-9]', '_').ToLowerInvariant()
            $cname = "databoar_${runId}_$slug"
            $inner = "podman stop '$cname' 2>/dev/null || true; podman rm -f '$cname' 2>/dev/null || true; echo PLANV_PODMAN_RM_DONE"
            $null = Invoke-DataBoarPlanVRemoteSh -SshTarget $ssh -RemoteShellSnippet $inner -ConnectTimeoutSeconds 60
        }
        elseif ($nType -eq "metal") {
            $pidFile = ([string]$ctx.RemoteRoot) + "/logs/metal_${runId}.pid"
            $pf = $pidFile -replace "'", "'\''"
            $inner = 'if [ -f ''' + $pf + ''' ]; then kill $(cat ''' + $pf + ''') 2>/dev/null || true; rm -f ''' + $pf + '''; fi; wait 2>/dev/null || true; echo PLANV_METAL_STOP_DONE'
            $null = Invoke-DataBoarPlanVRemoteSh -SshTarget $ssh -RemoteShellSnippet $inner -ConnectTimeoutSeconds 30
        }
    }
    foreach ($node in $ctx.Inventory) {
        $nUser = [string]$node.SshUser
        $ssh = Resolve-DataBoarSshTarget -NodeName ([string]$node.Name) -IpAddress ([string]$node.Ip) -SshUser $nUser
        $reap = "sleep 1; wait 2>/dev/null || true; echo PLANV_REAP_OK"
        $null = Invoke-DataBoarPlanVRemoteSh -SshTarget $ssh -RemoteShellSnippet $reap -ConnectTimeoutSeconds 15
    }
}

function Invoke-DataBoarPlanVResilientRun {
    <#
    .SYNOPSIS
      Slice 4 entry: trap + try orchestration + finally report + optional teardown (zombie / orphan reduction).
    .PARAMETER RunId
      When empty, uses Get-Date yyyyMMdd_HHmmss.
    .PARAMETER TearDownAfterRun
      When true (default), removes stack/podman/metal resources for this RunId after the run (lab hygiene).
    .PARAMETER RunPreflightMounts
      When true, runs Test-DataBoarMounts before orchestration (fails fast).
    .PARAMETER StartTranscript
      When true, writes Start-Transcript to LocalLogRoot (Windows orchestrator).
    #>
    param(
        [string] $RunId = "",
        [Parameter(Mandatory = $true)] $Inventory,
        [Parameter(Mandatory = $true)][string] $BoarConfigLocalPath,
        [string] $StackYamlLocalPath = "",
        [string] $PodmanImage = "",
        [bool] $TearDownAfterRun = $true,
        [bool] $RunPreflightMounts = $false,
        [bool] $StartTranscript = $false,
        [int] $ConnectTimeoutSeconds = 45
    )
    if (-not $RunId) {
        $RunId = Get-Date -Format "yyyyMMdd_HHmmss"
    }
    $localRoot = Join-Path $env:TEMP "databoar_planv_$RunId"
    $logDir = Join-Path $localRoot "logs"
    New-Item -ItemType Directory -Force -Path $logDir | Out-Null
    $remoteRoot = Get-DataBoarPlanVRemoteBenchRoot -RunId $RunId
    $stackName = "databoar_$RunId"
    $protocolRows = New-Object System.Collections.Generic.List[object]
    foreach ($node in $Inventory) {
        $nUser = [string]$node.SshUser
        $ssh = Resolve-DataBoarSshTarget -NodeName ([string]$node.Name) -IpAddress ([string]$node.Ip) -SshUser $nUser
        $protocolRows.Add((Get-DataBoarPlanVMountProtocolStatus -NodeName ([string]$node.Name) -SshTarget $ssh -ConnectTimeoutSeconds 20))
    }
    $transcriptPath = $null
    if ($StartTranscript) {
        $transcriptPath = Join-Path $logDir "planv_transcript.log"
        try {
            Start-Transcript -LiteralPath $transcriptPath -Force | Out-Null
        } catch {
            $transcriptPath = $null
        }
    }
    $script:DataBoarPlanVRunContext = @{
        RunId              = $RunId
        Inventory          = $Inventory
        RemoteRoot         = $remoteRoot
        LocalLogRoot       = $localRoot
        ProtocolRows       = $protocolRows
        OrchestrationOk    = $false
        TrapFired          = $false
        TearDownAfterRun   = $TearDownAfterRun
        StackName          = $stackName
        TranscriptPath     = $transcriptPath
    }

    # Resilience / Lessons Learned (PS 5.1): a bare trap+try/finally runs finally before trap on
    # terminating errors, so rename-after-fatal would run after the coverage report. Use catch for
    # forensic rename, then finally for report + teardown (correct order).

    try {
        if ($RunPreflightMounts) {
            foreach ($node in $Inventory) {
                $nUser = [string]$node.SshUser
                $ok = Test-DataBoarMounts -NodeName ([string]$node.Name) -IpAddress ([string]$node.Ip) -SshUser $nUser -ConnectTimeoutSeconds 20
                if (-not $ok) {
                    throw "PlanV preflight mounts failed for node $($node.Name)"
                }
            }
        }
        Invoke-DataBoarPlanVInventoryOrchestration -RunId $RunId -Inventory $Inventory -BoarConfigLocalPath $BoarConfigLocalPath -StackYamlLocalPath $StackYamlLocalPath -PodmanImage $PodmanImage -ConnectTimeoutSeconds $ConnectTimeoutSeconds
        $script:DataBoarPlanVRunContext["OrchestrationOk"] = $true
    } catch {
        $script:DataBoarPlanVRunContext["TrapFired"] = $true
        Write-Warning ("PLANV_FATAL: {0}" -f $_.Exception.Message)
        try {
            Invoke-DataBoarPlanVForensicConfigRenameOnAllNodes
        } catch {
            Write-Warning ("PLANV_FORENSIC_RENAME_ERROR: {0}" -f $_.Exception.Message)
        }
        throw
    }
    finally {
        if ($StartTranscript -and $transcriptPath) {
            try {
                Stop-Transcript | Out-Null
            } catch {
            }
        }
        Invoke-DataBoarPlanVWriteCoverageReport
        if ($script:DataBoarPlanVRunContext -and $script:DataBoarPlanVRunContext["TearDownAfterRun"]) {
            Invoke-DataBoarPlanVCleanupSessionResources
        }
    }
}

# Example (documentation IPs only - replace for real lab):
# $RunID = Get-Date -Format "yyyyMMdd_HHmmss"
# $Inventory = @(
#   @{ Name = "Latitude"; Ip = "192.0.2.50"; Type = "Swarm" },
#   @{ Name = "T14-Pro"; Ip = "192.0.2.60"; Type = "Podman" },
#   @{ Name = "Lab-Op-1"; Ip = "192.0.2.71"; Type = "Metal"; MetalBinary = "/opt/databoar/bin/databoar" }
# )
# Invoke-DataBoarPlanVResilientRun -RunId $RunID -Inventory $Inventory -BoarConfigLocalPath "C:\path\boar_config.yaml" -TearDownAfterRun:$true
# (or invoke orchestration only without Invoke-DataBoarPlanVResilientRun:)
# Invoke-DataBoarPlanVInventoryOrchestration -RunId $RunID -Inventory $Inventory -BoarConfigLocalPath "C:\path\boar_config.yaml"
