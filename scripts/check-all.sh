#!/usr/bin/env bash
# check-all.sh — Linux/macOS (bash) mirror of scripts/check-all.ps1.
# Full gate: optional gatekeeper (requires pwsh) + plans dashboard + pre-commit + pytest.
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

echo "=== check-all.sh: lint + tests (repo: $REPO_ROOT) ===" >&2

# PII gate (parity with check-all.ps1) — reuses PowerShell script.
if command -v pwsh >/dev/null 2>&1; then
  pwsh "$REPO_ROOT/scripts/gatekeeper-audit.ps1" || exit "$?"
else
  echo "check-all.sh: WARN: pwsh not on PATH; skipping gatekeeper-audit.ps1 (install PowerShell for parity)." >&2
fi

# Plan dashboard
PY=python3
if ! command -v python3 >/dev/null 2>&1; then
  PY=python
fi
echo "Refreshing plans status dashboard..." >&2
"$PY" "$REPO_ROOT/scripts/plans-stats.py" --write

# Recover from missing venv
if [[ ! -f .venv/pyvenv.cfg ]]; then
  echo "No .venv/pyvenv.cfg - running uv sync to recreate the environment..." >&2
  uv sync
  if [[ ! -f .venv/pyvenv.cfg ]]; then
    echo "check-all.sh: uv sync did not create .venv; fix disk path or UV_* env and retry." >&2
    exit 2
  fi
fi

if [[ "$SKIP_PRECOMMIT" -eq 0 ]]; then
  echo "Running pre-commit (Ruff + markdown + pt-BR locale guards)..." >&2
  if ! uv run pre-commit run --all-files; then
    echo "pre-commit failed. Attempting to auto-apply Ruff formatting and re-run pre-commit once..." >&2
    uv run ruff format . 2>/dev/null || true
    if ! uv run pre-commit run --all-files; then
      echo "pre-commit still failing after auto-format. Fix issues above before committing or pushing." >&2
      exit 1
    fi
  fi
fi

echo "Running pytest (full suite, warnings treated as errors)..." >&2
set +e
uv run pytest -v -W error --tb=short
pytest_rc=$?
set -e
if [[ "$pytest_rc" -ne 0 ]]; then
  echo "pytest failed. Fix test failures before committing or pushing." >&2
  exit "$pytest_rc"
fi

if [[ "$INCLUDE_VERSION_SMOKE" -eq 1 ]]; then
  vsmoke="$REPO_ROOT/scripts/version-readiness-smoke.ps1"
  if [[ -f "$vsmoke" ]]; then
    if command -v pwsh >/dev/null 2>&1; then
      echo "Running version readiness smoke..." >&2
      pwsh "$vsmoke" || exit "$?"
    else
      echo "check-all.sh: --include-version-smoke needs pwsh; skipping (script present)." >&2
    fi
  else
    echo "Version readiness smoke script not found; skipping." >&2
  fi
fi

echo "check-all.sh: OK (pre-commit and pytest passed)." >&2
exit 0
