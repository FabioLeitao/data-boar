#!/usr/bin/env bash
# scripts/dependabot-osv-reconcile.sh
#
# When a Dependabot alert is visible to the operator at
# https://github.com/<owner>/<repo>/security/dependabot/<n> but the Cloud
# Agent's `gh` integration token returns 403 on the alerts API, we still
# need a parser-grade signal so we don't fall back to "raw string
# heuristic" mistakes (declaring the alert fabricated). OSV.dev is the
# fallback we trust per docs/ops/inspirations/THE_ART_OF_THE_FALLBACK.md
# §2 and SUPPLY_Colleague-NN_AND_TRUST_SIGNALS.md.
#
# Usage:
#   scripts/dependabot-osv-reconcile.sh <ecosystem> <package> <version>
#
# Examples:
#   scripts/dependabot-osv-reconcile.sh crates.io pyo3 0.23.5
#   scripts/dependabot-osv-reconcile.sh PyPI cryptography 46.0.7
#
# Exit codes:
#   0 — query ran; advisories may or may not be present (see stdout)
#   2 — usage error
#   3 — network or OSV API failure
#
# This script is intentionally a thin wrapper over the OSV.dev v1 API.
# It does NOT mutate the working tree. Doctrine-aligned per
# DEFENSIVE_SCANNING_MANIFESTO.md §1.3 (no surprise side effects).

set -euo pipefail

if [[ $# -ne 3 ]]; then
  cat >&2 <<EOF
usage: $0 <ecosystem> <package> <version>

Common ecosystems:
  crates.io   — Rust / Cargo
  PyPI        — Python / pip / uv
  npm         — Node.js
  Go          — Go modules
  Maven       — Java
  RubyGems    — Ruby

Tip: the resolved version comes from your lockfile, not pyproject.toml.
For Cargo:   grep -A1 'name = "<pkg>"' rust/<crate>/Cargo.lock
For Python:  grep '^<pkg>==' requirements.txt   (or uv.lock)
EOF
  exit 2
fi

ECOSYSTEM="$1"
PACKAGE="$2"
VERSION="$3"

PAYLOAD=$(cat <<JSON
{"package":{"name":"${PACKAGE}","ecosystem":"${ECOSYSTEM}"},"version":"${VERSION}"}
JSON
)

if ! RESPONSE=$(curl -fsS \
    --max-time 15 \
    -H "Content-Type: application/json" \
    -d "${PAYLOAD}" \
    "https://api.osv.dev/v1/query"); then
  echo "[ERROR] OSV.dev query failed (network or API)." >&2
  echo "[ERROR] Doctrine: surface the failure, never silently downgrade." >&2
  exit 3
fi

# Pretty print: id | severity | summary
# Falls back to raw JSON if jq is missing (still useful, never silent).
if command -v jq >/dev/null 2>&1; then
  COUNT=$(printf '%s' "${RESPONSE}" | jq -r '.vulns // [] | length')
  if [[ "${COUNT}" == "0" ]]; then
    echo "[OK] No advisories on OSV.dev for ${ECOSYSTEM}:${PACKAGE}@${VERSION}."
    echo "[OK] If the operator sees a Dependabot alert at"
    echo "     /security/dependabot/<n> for this package, it may be a"
    echo "     newer/internal advisory — ask the operator to paste the"
    echo "     CVE / GHSA / RUSTSEC id and re-trigger."
    exit 0
  fi
  echo "[FOUND] ${COUNT} advisory(ies) for ${ECOSYSTEM}:${PACKAGE}@${VERSION}:"
  printf '%s\n' "${RESPONSE}" | jq -r '
    .vulns[] |
    . as $v |
    (([(.affected // [])[] | (.ranges // [])[] | (.events // [])[] | select(.fixed) | .fixed] | first) // "n/a") as $fixed |
    (([(.references // [])[] | select(.type == "ADVISORY") | .url] | first)
     // ([(.references // [])[] | select(.type == "WEB") | .url] | first)
     // "n/a") as $url |
    "  - \($v.id) | \($v.database_specific.severity // "n/a") | \($v.summary // "(no summary)")\n      fixed: \($fixed)\n      url:   \($url)"
  '
else
  echo "[WARN] jq not found; printing raw OSV response." >&2
  printf '%s\n' "${RESPONSE}"
fi
