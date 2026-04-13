#!/usr/bin/env bash
# Optional: PATH for /usr/local/bin (bw), sudo timestamp refresh, hint for bw unlock.
# No secrets. Run from repo root or anywhere: bash scripts/t14-session-warm.sh
set -eu

if [[ -f /etc/profile.d/zz-local-bin.sh ]]; then
  # shellcheck source=/dev/null
  source /etc/profile.d/zz-local-bin.sh
fi
export PATH="/usr/local/bin:${PATH}"

echo "== T14 session warm (PATH + sudo) =="
echo "NOTE: tmux uses non-login bash — after baseline, /etc/bash.bashrc should include PATH for /usr/local/bin (role t14_bitwarden_cli). Open a new pane or: source /etc/bash.bashrc"
if command -v bw >/dev/null 2>&1; then
  echo "OK: bw -> $(command -v bw)"
else
  echo "NOTE: bw not on PATH — install via baseline (t14_bitwarden_cli) or: sudo npm install -g @bitwarden/cli"
fi

echo "Running sudo -v (refresh sudo timestamp)..."
sudo -v
echo "OK: sudo -v succeeded."
echo "Next: bw unlock  (then export BW_SESSION=... per Bitwarden docs)"
echo "      VeraCrypt: see docs/private/homelab/VERACRYPT_PRIVATE_REPO_SETUP.pt_BR.md section 6.0.1"
