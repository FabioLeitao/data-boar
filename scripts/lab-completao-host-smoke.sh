#!/usr/bin/env bash
# Data Boar — per-host "completao" lab smoke (NOT pytest).
# Exercises runtime surfaces: uv, optional Docker/Podman, optional lab DB stack, optional HTTP /health.
# Run from repo root: bash scripts/lab-completao-host-smoke.sh [--privileged] [--health-url URL]
# See docs/ops/LAB_COMPLETAO_RUNBOOK.md and docs/ops/LAB_SMOKE_MULTI_HOST.md.
#
# Privileged mode uses sudo -n for read-only snapshots (firewall/security tools) when available.
# For non-interactive SSH, configure NOPASSWD narrowly — docs/private/homelab/LABOP_COMPLETÃO_SUDOERS.pt_BR.md

set -u
export PATH="/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin${PATH+:$PATH}"
# uv is often installed to ~/.local/bin (login shells add it; non-interactive SSH may not).
if [[ -d "${HOME}/.local/bin" ]]; then
  export PATH="${HOME}/.local/bin:${PATH}"
fi

LC_PRIV=0
LC_HEALTH_URL="${LAB_COMPLETAO_HEALTH_URL:-}"
LC_REPO_ROOT=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    --privileged) LC_PRIV=1 ;;
    --health-url)
      LC_HEALTH_URL="${2:-}"
      shift
      ;;
    --repo-root)
      LC_REPO_ROOT="${2:-}"
      shift
      ;;
    --help|-h)
      cat <<'EOF'
Usage: bash scripts/lab-completao-host-smoke.sh [--privileged] [--health-url URL] [--repo-root PATH]

  --privileged   Best-effort read-only probes via sudo -n (iptables/nft/ufw/fail2ban status).
  --health-url   Override LAB_COMPLETAO_HEALTH_URL (e.g. http://127.0.0.1:8088/health).
  --repo-root    Repo root (default: infer from script location).

Environment:
  LAB_COMPLETAO_HEALTH_URL   Optional URL for curl -sf (Data Boar /health or similar).
EOF
      exit 0
      ;;
    *)
      echo "lab-completao-host-smoke: unknown arg: $1 (try --help)" >&2
      exit 2
      ;;
  esac
  shift
done

if [[ -z "$LC_REPO_ROOT" ]]; then
  _here=$(cd "$(dirname "$0")/.." && pwd)
  LC_REPO_ROOT="$_here"
fi

_lc_section() { echo "--- $* ---"; }
_lc_cmd() { command -v "$1" >/dev/null 2>&1; }
_lc_try() { "$@" 2>/dev/null || true; }
_lc_sudo() {
  if [[ "$LC_PRIV" != "1" ]] || ! _lc_cmd sudo; then
    return 0
  fi
  sudo -n "$@" 2>/dev/null || echo "(sudo -n failed or denied for: $*)"
}

echo "=== lab-completao-host-smoke $(date -Iseconds 2>/dev/null || date) ==="
echo "REPO_ROOT: $LC_REPO_ROOT"
echo "HOST: $(hostname -f 2>/dev/null || hostname 2>/dev/null || echo unknown)"
echo "PRIVILEGED: $LC_PRIV"

_lc_section "uname"
uname -a 2>/dev/null || true

_lc_section "uv"
if _lc_cmd uv; then
  uv --version
else
  echo "uv: not in PATH"
fi

_lc_section "Python import (engine)"
if [[ -f "$LC_REPO_ROOT/pyproject.toml" ]] && _lc_cmd uv; then
  (cd "$LC_REPO_ROOT" && uv run python -c "import core.engine; print('import core.engine: OK')" 2>&1) || echo "import core.engine: FAILED"
else
  echo "(skip: no uv or no pyproject.toml)"
fi

_lc_section "Docker / Podman"
if _lc_cmd docker; then
  docker --version
  _lc_try docker info 2>&1 | head -n 20
  _lc_try docker compose version
else
  echo "docker: not in PATH"
fi
if _lc_cmd podman; then
  podman --version
  _lc_try podman info 2>&1 | head -n 15
else
  echo "podman: not in PATH (optional)"
fi

_lc_section "lab-smoke-stack (deploy/lab-smoke-stack)"
LSS="$LC_REPO_ROOT/deploy/lab-smoke-stack"
if [[ -d "$LSS" ]] && [[ -f "$LSS/docker-compose.yml" ]]; then
  if _lc_cmd docker; then
    (cd "$LSS" && _lc_try docker compose ps 2>&1) || true
  elif _lc_cmd podman; then
    (cd "$LSS" && _lc_try podman compose ps 2>&1) || true
  else
    echo "(no docker/podman for stack status)"
  fi
else
  echo "(no deploy/lab-smoke-stack on this clone)"
fi

_lc_section "HTTP health (optional)"
if [[ -n "$LC_HEALTH_URL" ]]; then
  echo "URL: $LC_HEALTH_URL"
  if _lc_cmd curl; then
    curl -sS -m 15 -w "\nHTTP_CODE:%{http_code}\n" "$LC_HEALTH_URL" 2>&1 | tail -n 30
  else
    echo "curl: not in PATH"
  fi
else
  echo "(LAB_COMPLETAO_HEALTH_URL / --health-url not set)"
fi

if [[ "$LC_PRIV" == "1" ]]; then
  _lc_section "privileged read-only (sudo -n)"
  _lc_sudo iptables-save 2>/dev/null | head -n 40
  _lc_sudo nft list ruleset 2>/dev/null | head -n 40
  if _lc_cmd ufw; then
    _lc_sudo ufw status verbose 2>/dev/null || true
  fi
  for svc in fail2ban sshguard auditd; do
    if _lc_cmd systemctl; then
      echo -n "$svc: "
      systemctl is-active "$svc" 2>/dev/null || echo "n/a"
    fi
  done
fi

echo "=== lab-completao-host-smoke END ==="
