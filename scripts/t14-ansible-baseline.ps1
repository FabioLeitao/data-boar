param(
  [Parameter(Mandatory = $false)]
  [string]$SshHost = "lab-node-01",

  [Parameter(Mandatory = $false)]
  [string]$RepoPath = "~/Projects/dev/data-boar",

  [Parameter(Mandatory = $false)]
  [switch]$Apply,

  [Parameter(Mandatory = $false)]
  [switch]$SkipCheck
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

function ConvertTo-UnixLf {
  param([string]$Text)
  if ([string]::IsNullOrEmpty($Text)) { return $Text }
  return ($Text -replace "`r`n", "`n" -replace "`r", "`n").TrimEnd()
}

# Bash does not expand ~ inside double quotes. Remote `cd "~/foo"` fails; use $HOME instead.
function Get-BashCdPath {
  param([string]$RepoOrPath)
  if ($RepoOrPath -match '^\~/(.*)$') {
    return "`$HOME/$($Matches[1])"
  }
  return $RepoOrPath
}

function Invoke-LAB-NODE-01Ssh {
  param(
    [string]$Cmd,
    # Remote sudo/become often needs a TTY (e.g. Defaults requiretty). Plain ssh has none.
    [switch]$AllocateTTY
  )
  $Cmd = ConvertTo-UnixLf $Cmd
  if ($AllocateTTY) {
    ssh -tt $SshHost $Cmd
  } else {
    ssh $SshHost $Cmd
  }
  if ($LASTEXITCODE -ne 0) {
    throw "SSH command failed with exit code $LASTEXITCODE"
  }
}

Write-Host "== LAB-NODE-01 Ansible baseline ==" -ForegroundColor Cyan
Write-Host "Host: $SshHost"
Write-Host "Repo: $RepoPath"
Write-Host "Mode: $(if ($Apply) { 'APPLY' } else { 'CHECK' })"

$bashRepoRoot = Get-BashCdPath $RepoPath
$bashAnsibleDir = Get-BashCdPath "$RepoPath/ops/automation/ansible"

# Remote scripts must use LF only: PowerShell here-strings are CRLF on Windows and break bash (cd $'path\r', set, perl, ansible).
$preflightLines = @(
  'set -eu',
  "cd `"$bashRepoRoot`"",
  'command -v git >/dev/null',
  'command -v ansible-playbook >/dev/null'
)
Invoke-LAB-NODE-01Ssh ($preflightLines -join "`n")

# 2) Optional: warm sudo timestamp (separate SSH session still needs -tt for Ansible become if requiretty).
Write-Host "Check sudo cache on $SshHost." -ForegroundColor Yellow
ssh $SshHost "sudo -n true" | Out-Null
if ($LASTEXITCODE -ne 0) {
  Write-Host "sudo cache not warm; prompting once (interactive TTY)." -ForegroundColor Yellow
  ssh -tt $SshHost "sudo -v"
  if ($LASTEXITCODE -ne 0) {
    throw "sudo -v failed with exit code $LASTEXITCODE"
  }
}

# 3) Generate a local inventory pinned to localhost/local connection, then run check/apply.
$runModeArgs = if ($Apply) { "--diff" } else { "--check --diff" }

$runLines = @(
  'set -eu',
  "cd `"$bashAnsibleDir`"",
  'cp -f inventory.example.ini inventory.local.ini',
  "perl -0777 -pe 's/^\[lab-node-01\]\n.*?\n\n/[lab-node-01]\nlocalhost ansible_connection=local\n\n/ms' -i inventory.local.ini"
)
if ($Apply -and -not $SkipCheck) {
  $runLines += 'ANSIBLE_ROLES_PATH=./roles ansible-playbook -i inventory.local.ini playbooks/lab-node-01-baseline.yml --check --diff'
  $runLines += 'ANSIBLE_ROLES_PATH=./roles ansible-playbook -i inventory.local.ini playbooks/lab-node-01-baseline.yml --diff'
} else {
  $runLines += "ANSIBLE_ROLES_PATH=./roles ansible-playbook -i inventory.local.ini playbooks/lab-node-01-baseline.yml $runModeArgs"
}
Invoke-LAB-NODE-01Ssh ($runLines -join "`n") -AllocateTTY

Write-Host "Done." -ForegroundColor Green
