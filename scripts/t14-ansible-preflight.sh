#!/usr/bin/env bash
# Preflight checks before t14-baseline.yml — inventory, sudo, bw, docker apt list perms.
# Run on the T14 (or any Debian target) from repo root: bash scripts/t14-ansible-preflight.sh
set -eu

REPO_ROOT="$(git -C "$(dirname "$0")/.." rev-parse --show-toplevel 2>/dev/null || true)"
if [[ -z "${REPO_ROOT}" ]]; then
  echo "ERROR: not inside a git clone of data-boar (expected repo root)." >&2
  exit 1
fi
ANSIBLE_DIR="${REPO_ROOT}/ops/automation/ansible"
INV_LOCAL="${ANSIBLE_DIR}/inventory.local.ini"

echo "== T14 Ansible preflight (${REPO_ROOT}) =="
echo

if ! command -v ansible-playbook >/dev/null 2>&1; then
  echo "MISSING: ansible-playbook — install: sudo apt update && sudo apt install -y ansible"
  exit 1
fi
echo "OK: ansible-playbook ($(ansible-playbook --version | head -1))"

if [[ ! -f "${INV_LOCAL}" ]]; then
  echo "MISSING: ${INV_LOCAL}"
  echo "  Fix: cd ${ANSIBLE_DIR} && cp -f inventory.example.ini inventory.local.ini"
  echo "  If you run the playbook ON this laptop, set under [t14]:"
  echo "    localhost ansible_connection=local"
  exit 1
fi
echo "OK: inventory.local.ini exists"

if grep -qE 'ansible_connection=local' "${INV_LOCAL}" && grep -qE 'localhost' "${INV_LOCAL}"; then
  echo "OK: inventory mentions localhost + ansible_connection=local (good for on-machine runs)"
elif grep -qE '^\[t14\]' "${INV_LOCAL}"; then
  echo "NOTE: for playbook ON this laptop, prefer: localhost ansible_connection=local under [t14]"
fi

if sudo -n true 2>/dev/null; then
  echo "OK: sudo is passwordless (NOPASSWD) for this session/user"
else
  echo "ACTION: run sudo -v once, then ansible-playbook --ask-become-pass ..."
fi

DOCKER_LIST="/etc/apt/sources.list.d/docker.list"
if [[ -f "${DOCKER_LIST}" ]]; then
  dmode="$(stat -c '%a' "${DOCKER_LIST}" 2>/dev/null || echo "")"
  echo "INFO: ${DOCKER_LIST} mode=${dmode}"
  if [[ "${dmode}" != "644" ]]; then
    echo "WARN: docker.list should be 0644 (avoids Permission denied for user-space apt readers)"
    echo "      Fix: sudo chmod 644 ${DOCKER_LIST} && sudo chown root:root ${DOCKER_LIST}"
    echo "      Or re-run the baseline (t14_docker_ce sets 0644)."
  fi
else
  echo "INFO: ${DOCKER_LIST} not present yet (Docker role not applied or Docker disabled)"
fi

if [[ -x /usr/local/bin/bw ]]; then
  echo "OK: Bitwarden CLI at /usr/local/bin/bw"
elif command -v bw >/dev/null 2>&1; then
  echo "OK: bw on PATH ($(command -v bw))"
else
  echo "MISSING: bw (Bitwarden CLI) — install via baseline role t14_bitwarden_cli, or:"
  echo "  sudo apt install -y nodejs npm && sudo npm install -g @bitwarden/cli"
  echo "  Then: source /etc/profile.d/zz-local-bin.sh 2>/dev/null || export PATH=\"/usr/local/bin:\${PATH}\""
fi

echo
echo "Next (from ${ANSIBLE_DIR}):"
echo "  cd ${ANSIBLE_DIR}"
echo "  ansible-playbook -i inventory.local.ini --ask-become-pass playbooks/t14-baseline.yml --diff"
echo
