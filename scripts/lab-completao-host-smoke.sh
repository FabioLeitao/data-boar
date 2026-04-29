#!/usr/bin/env bash
# Data Boar -- per-host "completao" lab smoke (NOT pytest).
# Exercises runtime surfaces: uv, optional Docker/Podman, optional lab DB stack, optional HTTP /health.
# Run from repo root: bash scripts/lab-completao-host-smoke.sh [--privileged] [--health-url URL]
# See docs/ops/LAB_COMPLETAO_RUNBOOK.md and docs/ops/LAB_SMOKE_MULTI_HOST.md.
#
# Exit codes (DATA_BOAR_COMPLETAO_EXIT_v1 -- same contract as docs/ops/LAB_COMPLETAO_RUNBOOK.md):
#   0 -- completed diagnostic bundle (success; individual steps may log FAILED inside the transcript).
#   1 -- reserved for future infra-hard-fail fast-path (network/tool missing when a gate requires it).
#   2 -- invalid invocation / unknown CLI argument (contract violation).
#   3 -- reserved for compliance-violation signals when a scanner hook is wired to this script.
#
# Privileged mode uses sudo -n for read-only snapshots (firewall/security tools) when available.
# For non-interactive SSH, configure NOPASSWD narrowly -- docs/private/homelab/LABOP_COMPLETAO_SUDOERS.pt_BR.md
# (Cmnd_Alias for homelab-host-report.sh / lab-completao-host-smoke.sh --privileged paths must match sudoers literally.)

set -u
export PATH="/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin${PATH+:$PATH}"
# uv is often installed to ~/.local/bin (login shells add it; non-interactive SSH may not).
if [[ -d "${HOME}/.local/bin" ]]; then
  export PATH="${HOME}/.local/bin:${PATH}"
fi

LC_PRIV=0
LC_SKIP_ENGINE=0
LC_HEALTH_URL="${LAB_COMPLETAO_HEALTH_URL:-}"
LC_REPO_ROOT=""
LC_BENCH_TRACK=""
LC_BENCH_ROOT=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    --privileged) LC_PRIV=1 ;;
    --skip-engine-import) LC_SKIP_ENGINE=1 ;;
    --bench-track)
      LC_BENCH_TRACK="${2:-}"
      shift
      ;;
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
Usage: bash scripts/lab-completao-host-smoke.sh [--privileged] [--skip-engine-import] [--bench-track stable|beta] [--health-url URL] [--repo-root PATH]

  --privileged          Best-effort read-only probes via sudo -n (iptables/nft/ufw/fail2ban status).
  --skip-engine-import  Skip uv / import core.engine (hosts that run Data Boar only via Docker/Swarm/Podman).
  --bench-track         Ephemeral A/B workdir under /tmp/databoar_bench/<stable|beta> (checkpoint isolation).
  --health-url          Override LAB_COMPLETAO_HEALTH_URL (e.g. http://127.0.0.1:8088/health).
  --repo-root           Repo root (default: infer from script location).

Environment:
  LAB_COMPLETAO_HEALTH_URL              Optional URL for curl -sf (Data Boar /health or similar).
  LAB_COMPLETAO_SKIP_ENGINE_IMPORT      If set to 1, same as --skip-engine-import (manifest / container-only hosts).
  LAB_COMPLETAO_SSH_HOST_ALIAS          Set by lab-completao-orchestrate.ps1 (manifest sshHost) for power warnings.
  LAB_COMPLETAO_MAIN_ENGINE_SSH_HOST    Optional manifest completaoMainEngineSshHost; undervoltage on other hosts is warning-only.
  LAB_COMPLETAO_SKIP_UNDERVOLTAGE_CHECK If 1, skip vcgencmd/journal undervoltage section (pi3b passive / operator override).
  LAB_COMPLETAO_BENCH_TRACK             stable|beta when --bench-track not passed.
  LAB_COMPLETAO_BENCH_COMPARE           If 1, emit coarse wall-clock import probe (stable: core.engine; beta: boar_fast_filter).
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

if [[ -z "$LC_BENCH_TRACK" && -n "${LAB_COMPLETAO_BENCH_TRACK:-}" ]]; then
  LC_BENCH_TRACK="${LAB_COMPLETAO_BENCH_TRACK}"
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

_lc_init_bench_workdir() {
  if [[ -z "$LC_BENCH_TRACK" ]]; then
    return 0
  fi
  if [[ "$LC_BENCH_TRACK" != "stable" && "$LC_BENCH_TRACK" != "beta" ]]; then
    echo "lab-completao-host-smoke: --bench-track must be stable or beta" >&2
    exit 2
  fi
  LC_BENCH_ROOT="/tmp/databoar_bench/$LC_BENCH_TRACK"
  mkdir -p "$LC_BENCH_ROOT" 2>/dev/null || true
  echo "databoar_bench_track=$LC_BENCH_TRACK" >"$LC_BENCH_ROOT/.checkpoint_isolation_marker" 2>/dev/null || true
  echo "BENCH_WORKDIR: $LC_BENCH_ROOT (isolated; do not share checkpoints between stable and beta)"
}

_lc_undervoltage_check() {
  if [[ "${LAB_COMPLETAO_SKIP_UNDERVOLTAGE_CHECK:-}" == "1" ]]; then
    _lc_section "power / undervoltage (skipped: LAB_COMPLETAO_SKIP_UNDERVOLTAGE_CHECK)"
    return 0
  fi
  _hn="$(hostname 2>/dev/null || true)"
  if [[ "$_hn" == *[Pp][Ii]3[Bb]* ]]; then
    _lc_section "power / undervoltage (skipped: pi3b passive target)"
    return 0
  fi
  _lc_section "power / undervoltage (non-fatal)"
  local th="0x0"
  if _lc_cmd vcgencmd; then
    th="$(vcgencmd get_throttled 2>/dev/null | sed -n 's/^throttled=//p' || echo "0x0")"
    echo "vcgencmd get_throttled: ${th:-unknown}"
  else
    echo "vcgencmd: not available (skip Pi-specific undervoltage)"
  fi
  if [[ -n "$th" && "$th" != "0x0" ]]; then
    if [[ -n "${LAB_COMPLETAO_MAIN_ENGINE_SSH_HOST:-}" && -n "${LAB_COMPLETAO_SSH_HOST_ALIAS:-}" && "$LAB_COMPLETAO_SSH_HOST_ALIAS" != "${LAB_COMPLETAO_MAIN_ENGINE_SSH_HOST}" ]]; then
      echo "WARNING: throttle/undervoltage on non-main-engine host (alias=${LAB_COMPLETAO_SSH_HOST_ALIAS} main=${LAB_COMPLETAO_MAIN_ENGINE_SSH_HOST}). Orchestration must not treat this as hard-fail."
    else
      echo "WARNING: throttle or undervoltage flags ($th). Review PSU; not a host-smoke exit failure."
    fi
  fi
  if [[ "$LC_PRIV" == "1" ]]; then
    _lc_try journalctl -k --since "2 hours ago" --no-pager 2>/dev/null | grep -iE 'under-?voltage|throttl' | tail -n 8 || true
  fi
}

_lc_bench_compare() {
  if [[ "${LAB_COMPLETAO_BENCH_COMPARE:-}" != "1" ]]; then
    return 0
  fi
  _lc_section "bench_compare (LAB_COMPLETAO_BENCH_COMPARE=1)"
  if [[ "$LC_SKIP_ENGINE" == "1" ]]; then
    echo "(skip bench_compare: skip-engine-import)"
    return 0
  fi
  if [[ ! -f "$LC_REPO_ROOT/pyproject.toml" ]] || ! _lc_cmd uv; then
    echo "(skip bench_compare: no uv or pyproject.toml)"
    return 0
  fi
  if [[ "$LC_BENCH_TRACK" == "stable" ]]; then
    echo "--- stable track: core.engine import wall seconds ---"
    _t0=$(date +%s)
    (cd "$LC_REPO_ROOT" && uv run python -c "import core.engine; print('engine_ok')") || true
    _t1=$(date +%s)
    echo "BENCH_STABLE_IMPORT_SEC=$((_t1 - _t0))"
  elif [[ "$LC_BENCH_TRACK" == "beta" ]]; then
    echo "--- beta track: boar_fast_filter (FFI) import wall seconds ---"
    _t0=$(date +%s)
    (cd "$LC_REPO_ROOT" && uv run python -c "import importlib.util as u; print('boar_fast_filter_ok' if u.find_spec('boar_fast_filter') else 'boar_fast_filter_missing')") || true
    _t1=$(date +%s)
    echo "BENCH_BETA_FFI_IMPORT_SEC=$((_t1 - _t0))"
  else
    echo "(bench_compare: set --bench-track stable|beta for labeled A/B timing)"
  fi
}

_lc_init_bench_workdir

echo "=== lab-completao-host-smoke $(date -Iseconds 2>/dev/null || date) ==="
echo "REPO_ROOT: $LC_REPO_ROOT"
echo "HOST: $(hostname -f 2>/dev/null || hostname 2>/dev/null || echo unknown)"
echo "PRIVILEGED: $LC_PRIV"
if [[ -n "$LC_BENCH_TRACK" ]]; then
  echo "BENCH_TRACK: $LC_BENCH_TRACK ROOT: ${LC_BENCH_ROOT:-}"
fi

_lc_undervoltage_check

_lc_section "uname"
uname -a 2>/dev/null || true

_lc_section "uv"
if _lc_cmd uv; then
  uv --version
else
  echo "uv: not in PATH"
fi

_lc_section "Python import (engine)"
if [[ "$LC_SKIP_ENGINE" == "1" ]]; then
  echo "(skipped: container-only host -- expect Data Boar via Docker / Podman / Swarm stack, not bare-metal uv; see docs/ops/LAB_COMPLETAO_RUNBOOK.md)"
elif [[ -f "$LC_REPO_ROOT/pyproject.toml" ]] && _lc_cmd uv; then
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

_lc_bench_compare

echo "=== lab-completao-host-smoke END ==="
exit 0
