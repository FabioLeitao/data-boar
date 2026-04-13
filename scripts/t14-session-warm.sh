#!/usr/bin/env bash
# Optional: PATH for /usr/local/bin (bw), sudo timestamp refresh, hint for bw unlock.
# No secrets. Run from repo root or anywhere: bash scripts/lab-node-01-session-warm.sh
set -eu

if [[ -f /etc/profile.d/zz-local-bin.sh ]]; then
  # shellcheck source=/dev/null
  source /etc/profile.d/zz-local-bin.sh
fi
export PATH="/usr/local/bin:${PATH}"

echo "== LAB-NODE-01 session warm (PATH + sudo) =="
if command -v bw >/dev/null 2>&1; then
  echo "OK: bw -> $(command -v bw)"
else
  echo "NOTE: bw not on PATH — install via baseline (lab-node-01_bitwarden_cli) or: sudo npm install -g @bitwarden/cli"
fi

echo "Running sudo -v (refresh sudo timestamp)..."
sudo -v
echo "OK: sudo -v succeeded."
echo "Next: bw unlock  (then export BW_SESSION=... per Bitwarden docs)"
echo "      VeraCrypt: see docs/private/homelab/VERACRYPT_PRIVATE_REPO_SETUP.pt_BR.md section 6.0.1"
