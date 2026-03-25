#!/usr/bin/env bash
# Data Boar — homelab inventory helper (run ON each Linux host; redact output before sharing).
# Usage: bash scripts/homelab-host-report.sh
# After clone: chmod +x scripts/homelab-host-report.sh   (typos: chmos / chmosd → chmod)
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
if command -v pip3 >/dev/null; then
  pip3 --version
elif command -v python3 >/dev/null && python3 -m pip --version >/dev/null 2>&1; then
  python3 -m pip --version
else
  echo "pip3: not in PATH (try: python3 -m pip --version)"
fi

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
# Debian/Ubuntu install to /usr/sbin/lynis — often missing from PATH in non-login scripts.
# Run from /tmp + sanitized env: some builds mis-resolve language/DB paths when cwd is the repo
# or when stale LYNIS_* / PWD leaks from the shell.
_lynis_resolve_bin() {
  local p deb_paths
  for p in /usr/sbin/lynis /usr/bin/lynis /usr/local/sbin/lynis; do
    if [[ -f "$p" ]] && [[ -r "$p" ]]; then
      if [[ -x "$p" ]]; then echo "$p"; return 0; fi
    fi
  done
  if command -v dpkg-query >/dev/null; then
    while IFS= read -r deb_paths; do
      [[ -z "$deb_paths" ]] && continue
      if [[ -f "$deb_paths" && -x "$deb_paths" ]]; then
        echo "$deb_paths"
        return 0
      fi
    done < <(dpkg-query -L lynis 2>/dev/null | grep -E '^/(usr/)?(s)?bin/lynis$' || true)
  fi
  PATH="/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"
  command -v lynis 2>/dev/null || true
}

_lynis_show_version() {
  local bin="$1"
  [[ -n "$bin" ]] || return 1
  [[ -f "$bin" ]] || return 1
  (
    cd /tmp 2>/dev/null || cd / 2>/dev/null || true
    unset OLDPWD LYNIS_HOME LYNIS_CONFIG_DIR 2>/dev/null || true
    # `show version` avoids some full-init code paths; fall back to --version.
    env -i \
      HOME="${HOME:-/tmp}" \
      PATH="/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin" \
      LANG="${LANG:-C.UTF-8}" \
      LC_ALL="${LC_ALL:-C.UTF-8}" \
      TERM="${TERM:-dumb}" \
      USER="${USER:-}" \
      "$bin" show version 2>&1 \
      || env -i \
        HOME="${HOME:-/tmp}" \
        PATH="/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin" \
        LANG="${LANG:-C.UTF-8}" \
        LC_ALL="${LC_ALL:-C.UTF-8}" \
        TERM="${TERM:-dumb}" \
        USER="${USER:-}" \
        "$bin" --version 2>&1
  )
}

LYNIS_BIN="$(_lynis_resolve_bin)"
if [[ -n "$LYNIS_BIN" ]]; then
  if ! _lynis_show_version "$LYNIS_BIN"; then
    echo "lynis: binary at $LYNIS_BIN but version query failed (try: sudo apt install --reinstall lynis; type -a lynis)"
  fi
else
  echo "lynis: not installed or not found under /usr/sbin, /usr/bin, dpkg -L lynis, or standard PATH"
fi

echo "--- kernel / sysctl / block (read-only sample) ---"
# Helps trace lab tuning (vm dirty ratios, schedulers, rotational flags) without dumping full sysctl -a.
if command -v sysctl >/dev/null; then
  sysctl vm.swappiness vm.dirty_ratio vm.dirty_background_ratio 2>/dev/null || true
  sysctl vm.dirty_expire_centisecs vm.dirty_writeback_centisecs 2>/dev/null || true
  sysctl kernel.randomize_va_space 2>/dev/null || true
fi
if [[ -r /proc/sys/vm/min_free_kbytes ]]; then
  echo "vm.min_free_kbytes: $(cat /proc/sys/vm/min_free_kbytes 2>/dev/null)"
fi

if command -v lsblk >/dev/null; then
  echo "--- lsblk (summary) ---"
  lsblk -o NAME,SIZE,TYPE,ROTA,RM,TRAN,MOUNTPOINTS 2>/dev/null | head -40 || true
fi

echo "--- /sys/block/*/queue (scheduler, rotational, nr_requests sample) ---"
for q in /sys/block/*/queue; do
  [[ -d "$q" ]] || continue
  dev="${q#/sys/block/}"
  dev="${dev%/queue}"
  [[ "$dev" == loop* ]] && continue
  if [[ -f "$q/scheduler" ]]; then
    echo "$dev scheduler: $(tr -d '\n' <"$q/scheduler" 2>/dev/null)"
  fi
  if [[ -f "$q/rotational" ]]; then
    echo "$dev rotational: $(tr -d '\n' <"$q/rotational" 2>/dev/null)"
  fi
  if [[ -f "$q/nr_requests" ]]; then
    echo "$dev nr_requests: $(tr -d '\n' <"$q/nr_requests" 2>/dev/null)"
  fi
done 2>/dev/null | head -80

echo "--- cpufreq (if present) ---"
if [[ -d /sys/devices/system/cpu/cpu0/cpufreq ]]; then
  for f in scaling_governor energy_performance_preference; do
    p="/sys/devices/system/cpu/cpu0/cpufreq/$f"
    [[ -r "$p" ]] && echo "cpu0 $f: $(tr -d '\n' <"$p" 2>/dev/null)"
  done
else
  echo "(no cpufreq sysfs — VM or older kernel?)"
fi

echo "--- Optional dev toolchains (not required for Data Boar) ---"
command -v go >/dev/null && go version || echo "go: not in PATH"
command -v rustc >/dev/null && rustc --version || echo "rustc: not in PATH"
command -v zig >/dev/null && zig version || echo "zig: not in PATH"
command -v odin >/dev/null && odin version 2>/dev/null || echo "odin: not in PATH"
command -v brew >/dev/null && brew --version 2>/dev/null | head -3 || echo "brew: not in PATH"

echo "=== end ==="
