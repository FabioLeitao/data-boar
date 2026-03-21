#!/usr/bin/env bash
# Data Boar — homelab inventory helper (run ON each Linux host; redact output before sharing).
# Usage: bash scripts/homelab-host-report.sh
# See: docs/ops/HOMELAB_HOST_PACKAGE_INVENTORY.md

set -u

echo "=== homelab-host-report $(date -Iseconds 2>/dev/null || date) ==="
echo "HOST: $(hostname -f 2>/dev/null || hostname 2>/dev/null || echo unknown)"
echo "--- uname ---"
uname -a 2>/dev/null || true

echo "--- /etc/os-release ---"
if [[ -f /etc/os-release ]]; then
  cat /etc/os-release
else
  echo "(no /etc/os-release)"
fi

echo "--- CPU / RAM ---"
command -v nproc >/dev/null && echo "nproc: $(nproc)" || true
command -v free >/dev/null && free -h || true

echo "--- Python ---"
if command -v python3 >/dev/null; then
  command -v python3
  python3 --version
else
  echo "python3: not in PATH"
fi

echo "--- uv ---"
if command -v uv >/dev/null; then
  uv --version
else
  echo "uv: not in PATH"
fi

echo "--- pip (user warning: may be system pip) ---"
command -v pip3 >/dev/null && pip3 --version || echo "pip3: not in PATH"

echo "--- Docker ---"
if command -v docker >/dev/null; then
  docker --version
  docker info 2>/dev/null | head -40 || echo "(docker info failed — permissions or daemon down)"
else
  echo "docker: not in PATH"
fi

echo "--- Bitwarden CLI (bw) ---"
if command -v bw >/dev/null; then
  command -v bw
  bw --version 2>/dev/null || echo "(bw --version failed)"
else
  echo "bw: not in PATH (install via apt bitwarden-cli, npm -g @bitwarden/cli, or GitHub release; ensure PATH)"
fi

echo "--- dpkg: suggested Data Boar-related packages (Debian/Ubuntu) ---"
if command -v dpkg-query >/dev/null; then
  pkgs=(python3.12 python3.12-venv python3.12-dev build-essential libpq-dev libssl-dev libffi-dev unixodbc-dev
        docker-ce docker.io containerd.io podman lynis bitwarden-cli)
  for p in "${pkgs[@]}"; do
    dpkg-query -W -f='${Status}\t${Package}\t${Version}\n' "$p" 2>/dev/null | grep -v '^not-installed' || true
  done
  echo "(dpkg full count: $(dpkg -l 2>/dev/null | wc -l) lines — use dpkg -l > file if you need full export)"
else
  echo "dpkg-query: not available (not Debian/Ubuntu?)"
fi

echo "--- xbps (Void): name match sample ---"
if command -v xbps-query >/dev/null; then
  xbps-query -l | grep -iE 'python3|docker|uv|lynis|openssl|gcc' | head -60 || true
else
  echo "xbps-query: not available"
fi

echo "--- apk (Alpine): world head ---"
if command -v apk >/dev/null; then
  apk list -I 2>/dev/null | head -40 || true
else
  echo "apk: not available"
fi

echo "--- Lynis (if installed) ---"
command -v lynis >/dev/null && lynis --version 2>/dev/null || echo "lynis: not in PATH"

echo "--- Optional dev toolchains (not required for Data Boar) ---"
command -v go >/dev/null && go version || echo "go: not in PATH"
command -v rustc >/dev/null && rustc --version || echo "rustc: not in PATH"
command -v zig >/dev/null && zig version || echo "zig: not in PATH"
command -v odin >/dev/null && odin version 2>/dev/null || echo "odin: not in PATH"
command -v brew >/dev/null && brew --version 2>/dev/null | head -3 || echo "brew: not in PATH"

echo "=== end ==="
