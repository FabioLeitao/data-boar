#!/usr/bin/env bash
# check-all.sh — Linux/macOS mirror of scripts/check-all.ps1.
# Delegates lint/tests to scripts/pre-commit-and-tests.sh (same as check-all.ps1).
# Full gate: optional gatekeeper (requires pwsh) + plans dashboard + pre-commit + pytest.
# Optional Rust prefilter build runs inside pre-commit-and-tests.* when rustc is available.
# From repo root:
#   ./scripts/check-all.sh
#   ./scripts/check-all.sh --skip-pre-commit
#   ./scripts/check-all.sh --include-version-smoke
# On Windows, prefer .\scripts\check-all.ps1 (identical flow).
set -euo pipefail

REPO_ROOT=$(cd "$(dirname "$0")/.." && pwd)
cd "$REPO_ROOT" || exit 2

SKIP_PRECOMMIT=0
INCLUDE_VERSION_SMOKE=0
while [[ $# -gt 0 ]]; do
  case "$1" in
    -SkipPreCommit | --skip-pre-commit) SKIP_PRECOMMIT=1 ;;
    -IncludeVersionSmoke | --include-version-smoke) INCLUDE_VERSION_SMOKE=1 ;;
    -h | --help)
      echo "Usage: $0 [options]"
      echo "  --skip-pre-commit          Only run pytest (same as check-all.ps1 -SkipPreCommit)"
      echo "  --include-version-smoke    After success, run version-readiness-smoke.ps1 (requires pwsh)"
      echo "  -h, --help                 This help"
      exit 0
      ;;
    *)
      echo "check-all.sh: unknown option: $1" >&2
      exit 2
      ;;
  esac
  shift
done

echo "=== check-all: lint + tests ===" >&2

# PII gate (parity with check-all.ps1) — reuses PowerShell script.
if command -v pwsh >/dev/null 2>&1; then
  pwsh "$REPO_ROOT/scripts/gatekeeper-audit.ps1" || exit "$?"
else
  echo "check-all.sh: WARN: pwsh not on PATH; skipping gatekeeper-audit.ps1 (install PowerShell for parity)." >&2
fi

# Plan dashboard (same order as check-all.ps1 — before pre-commit-and-tests).
PY=python3
if ! command -v python3 >/dev/null 2>&1; then
  PY=python
fi
echo "Refreshing plans status dashboard..." >&2
"$PY" "$REPO_ROOT/scripts/plans-stats.py" --write

ARGS=()
if [[ "$SKIP_PRECOMMIT" -eq 1 ]]; then
  ARGS+=(--skip-pre-commit)
fi

"$REPO_ROOT/scripts/pre-commit-and-tests.sh" "${ARGS[@]}"
exit_code=$?

if [[ "$exit_code" -eq 0 ]] && [[ "$INCLUDE_VERSION_SMOKE" -eq 1 ]]; then
  vsmoke="$REPO_ROOT/scripts/version-readiness-smoke.ps1"
  if [[ -f "$vsmoke" ]]; then
    if command -v pwsh >/dev/null 2>&1; then
      echo "Running version readiness smoke..." >&2
      pwsh "$vsmoke" || exit_code=$?
    else
      echo "check-all.sh: --include-version-smoke needs pwsh; skipping (script present)." >&2
    fi
  else
    echo "Version readiness smoke script not found; skipping." >&2
  fi
fi

if [[ "$exit_code" -eq 0 ]]; then
  echo "check-all: OK (pre-commit and pytest passed)." >&2
else
  echo "check-all: FAILED (see output above)." >&2
fi

exit "$exit_code"
