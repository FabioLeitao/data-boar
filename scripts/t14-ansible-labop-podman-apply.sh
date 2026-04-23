#!/usr/bin/env bash
# Data Boar — narrow LAB-OP entrypoint for Podman Ansible apply (LAB-NODE-01 / Debian family).
#
# Intended for passwordless sudo via a fixed Cmnd_Alias (same discipline as
# scripts/homelab-host-report.sh --privileged). Do NOT widen NOPASSWD beyond
# this script path + the flags listed in sudoers.
#
# Usage (as operator, with sudoers configured):
#   sudo -n /bin/bash /home/USER/Projects/dev/data-boar/scripts/lab-node-01-ansible-labop-podman-apply.sh --apply
#   sudo -n /bin/bash .../lab-node-01-ansible-labop-podman-apply.sh --check
#
# Without root: re-invokes via sudo -n when possible.
#
# See: docs/ops/LAB_OP_PRIVILEGED_COLLECTION.md, ops/automation/ansible/README.md

set -euo pipefail

export PATH="/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin${PATH+:$PATH}"

usage() {
  cat <<'EOF'
Usage: bash scripts/lab-node-01-ansible-labop-podman-apply.sh --apply | --check

  --apply   Run playbooks/lab-node-01-podman.yml on this host (localhost inventory).
  --check   Ansible --check --diff (dry-run).

Requires: ansible-playbook, perl. Passwordless sudo must match the exact
/bin/bash <repo>/scripts/lab-node-01-ansible-labop-podman-apply.sh <flag> allowlist.
EOF
}

APPLY=0
CHECK=0
while [[ $# -gt 0 ]]; do
  case "$1" in
    --apply) APPLY=1; shift ;;
    --check) CHECK=1; shift ;;
    -h|--help) usage; exit 0 ;;
    *)
      echo "Unknown argument: $1" >&2
      usage >&2
      exit 2
      ;;
  esac
done

if [[ "$((APPLY + CHECK))" -ne 1 ]]; then
  echo "Specify exactly one of --apply or --check." >&2
  usage >&2
  exit 2
fi

SCRIPT_PATH="$(readlink -f "${BASH_SOURCE[0]}" 2>/dev/null || realpath "${BASH_SOURCE[0]}" 2>/dev/null || echo "${BASH_SOURCE[0]}")"
SCRIPT_DIR="$(cd "$(dirname "$SCRIPT_PATH")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
ANSIBLE_DIR="$REPO_ROOT/ops/automation/ansible"
PLAYBOOK="$ANSIBLE_DIR/playbooks/lab-node-01-podman.yml"

if [[ ! -d "$ANSIBLE_DIR" ]] || [[ ! -f "$PLAYBOOK" ]]; then
  echo "Expected repo layout missing (ansible dir or lab-node-01-podman.yml)." >&2
  exit 2
fi

# Re-exec as root with sudo -n when not root (NOPASSWD path must match /bin/bash + this script + flag).
if [[ "$(id -u)" -ne 0 ]]; then
  if ! command -v sudo >/dev/null 2>&1; then
    echo "sudo not available; run as root or install sudo." >&2
    exit 2
  fi
  exec sudo -n /bin/bash "$SCRIPT_PATH" "$@"
fi

cd "$ANSIBLE_DIR"
cp -f inventory.example.ini inventory.local.ini
perl -0777 -pe 's/^\[lab-node-01\]\n.*?\n\n/[lab-node-01]\nlocalhost ansible_connection=local\n\n/ms' -i inventory.local.ini

export ANSIBLE_ROLES_PATH=./roles

OPERATOR="${SUDO_USER:-}"
if [[ -z "$OPERATOR" || "$OPERATOR" == "root" ]]; then
  OPERATOR="$(stat -c '%U' "$REPO_ROOT" 2>/dev/null || true)"
fi
if [[ -z "$OPERATOR" || "$OPERATOR" == "root" ]]; then
  echo "Could not resolve operator login for Ansible facts (SUDO_USER or repo owner)." >&2
  exit 2
fi

EXTRA_ARGS=()
if [[ "$CHECK" == 1 ]]; then
  EXTRA_ARGS=(--check --diff)
else
  EXTRA_ARGS=(--diff)
fi

exec ansible-playbook -i inventory.local.ini "${EXTRA_ARGS[@]}" \
  -e "ansible_user=$OPERATOR" \
  "$PLAYBOOK"
