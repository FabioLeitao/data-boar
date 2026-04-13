param(
  [Parameter(Mandatory = $false)]
  [string]$SshHost = "t14",

  [Parameter(Mandatory = $false)]
  [string]$RepoPath = "~/Projects/dev/data-boar",

  [Parameter(Mandatory = $false)]
  [switch]$Apply,

  [Parameter(Mandatory = $false)]
  [switch]$SkipCheck
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

function Invoke-T14Ssh([string]$Cmd) {
  ssh $SshHost $Cmd
  if ($LASTEXITCODE -ne 0) {
    throw "SSH command failed with exit code $LASTEXITCODE"
  }
}

Write-Host "== T14 Ansible baseline ==" -ForegroundColor Cyan
Write-Host "Host: $SshHost"
Write-Host "Repo: $RepoPath"
Write-Host "Mode: $(if ($Apply) { 'APPLY' } else { 'CHECK' })"

# 1) Preflight: ensure repo exists and git/ansible are present.
# Use POSIX "set -eu" only: ssh runs /bin/sh (dash on Debian/LMDE), which does not support "pipefail".
Invoke-T14Ssh @"
set -eu
cd "$RepoPath"
command -v git >/dev/null
command -v ansible-playbook >/dev/null
"@

# 2) One interactive step: warm up sudo so Ansible can run non-interactively afterwards.
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

$checkThenApply = if ($Apply -and -not $SkipCheck) {
  @"
ANSIBLE_ROLES_PATH=./roles ansible-playbook -i inventory.local.ini playbooks/t14-baseline.yml --check --diff
ANSIBLE_ROLES_PATH=./roles ansible-playbook -i inventory.local.ini playbooks/t14-baseline.yml --diff
"@
} else {
  "ANSIBLE_ROLES_PATH=./roles ansible-playbook -i inventory.local.ini playbooks/t14-baseline.yml $runModeArgs"
}

Invoke-T14Ssh @"
set -eu
cd "$RepoPath/ops/automation/ansible"
cp -f inventory.example.ini inventory.local.ini
perl -0777 -pe 's/^\[t14\]\n.*?\n\n/[t14]\nlocalhost ansible_connection=local\n\n/ms' -i inventory.local.ini
$checkThenApply
"@

Write-Host "Done." -ForegroundColor Green

