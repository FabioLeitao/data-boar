#!/usr/bin/env bash
# dependabot-resync.sh — operator helper to refresh uv.lock + requirements.txt on a
# Dependabot pip PR branch so tests/test_dependency_artifacts_sync.py turns green again.
#
# Why this exists: Dependabot only edits requirements.txt; the project keeps pyproject.toml,
# uv.lock and requirements.txt as a single source of truth (see CONTRIBUTING.md and
# tests/test_dependency_artifacts_sync.py). A naïve "rage-merge" of a security bump (e.g.
# cryptography 47.0.0 for a CVE) would land an inconsistent lockfile and a misaligned SBOM.
# This script applies the bot's pyproject change, then runs the canonical regenerate steps.
#
# Doctrine: docs/ops/inspirations/DEFENSIVE_SCANNING_MANIFESTO.md (no surprise side effects)
# and docs/ops/inspirations/THE_ART_OF_THE_FALLBACK.md (diagnostic on fall — print clear next
# steps if a step fails, never swallow the error). Linux/macOS twin of dependabot-resync.ps1.
#
# Usage (from repo root, on a checked-out Dependabot PR branch):
#   ./scripts/dependabot-resync.sh                # uv lock + uv export, do not git-commit
#   ./scripts/dependabot-resync.sh --commit       # also git add + commit the regen
#   ./scripts/dependabot-resync.sh --check        # only verify (no writes), exit non-zero on drift
set -euo pipefail

REPO_ROOT=$(cd "$(dirname "$0")/.." && pwd)
cd "$REPO_ROOT" || exit 2

DO_COMMIT=0
CHECK_ONLY=0
while [[ $# -gt 0 ]]; do
  case "$1" in
    --commit) DO_COMMIT=1 ;;
    --check) CHECK_ONLY=1 ;;
    -h|--help)
      cat <<EOF
Usage: $0 [--commit|--check]

  --commit   stage and commit the regenerated uv.lock + requirements.txt
             with Conventional Commit message: "chore(deps): resync uv.lock + requirements.txt".
  --check    do not write; run "uv lock --check" and the dependency-artifacts pytest.
  -h, --help show this help.

Operator workflow for a Dependabot pip PR (e.g. #224 cryptography 47.0.0):
  1. gh pr checkout 224
  2. ./scripts/dependabot-resync.sh --commit
  3. git push
  4. wait for CI green, then merge.
EOF
      exit 0
      ;;
    *)
      echo "dependabot-resync.sh: unknown option: $1" >&2
      exit 2
      ;;
  esac
  shift
done

if ! command -v uv >/dev/null 2>&1; then
  echo "dependabot-resync.sh: 'uv' not on PATH. Install per docs/USAGE.md or pyproject.toml header." >&2
  exit 2
fi

if [[ "$CHECK_ONLY" -eq 1 ]]; then
  echo "=== dependabot-resync.sh: CHECK ONLY (no writes) ===" >&2
  uv lock --check
  uv run pytest tests/test_dependency_artifacts_sync.py -v -W error
  exit 0
fi

echo "=== dependabot-resync.sh: regenerating uv.lock + requirements.txt ===" >&2

# Step 1: refresh uv.lock from pyproject.toml. On a Dependabot pip PR the pyproject
# constraint may already reflect the bumped version (direct dep) or be unchanged
# (transitive); either way uv lock makes the lockfile authoritative again.
uv lock

# Step 2: re-export requirements.txt with the exact same flags as
# tests/test_dependency_artifacts_sync.py (--no-emit-package pyproject.toml).
# This is the only export form the guard accepts.
uv export --no-emit-package pyproject.toml -o requirements.txt

# Step 3: run the same pytest the pre-commit hook runs. Diagnostic-on-fall:
# if it still fails we print the operator-facing fix path before exiting non-zero.
if ! uv run pytest tests/test_dependency_artifacts_sync.py -v -W error; then
  cat >&2 <<'EOF'

dependabot-resync.sh: regen finished but the dependency-artifacts guard still
fails. Most common cause: pyproject.toml on this branch does not yet include
the version Dependabot tried to land (direct dep). Edit pyproject.toml so the
constraint accepts the new version, then re-run this script.
See .cursor/skills/dependabot-recommendations/SKILL.md for the canonical flow.
EOF
  exit 1
fi

if [[ "$DO_COMMIT" -eq 1 ]]; then
  if git diff --quiet -- uv.lock requirements.txt; then
    echo "dependabot-resync.sh: nothing to commit (uv.lock + requirements.txt already in sync)." >&2
    exit 0
  fi
  git add uv.lock requirements.txt
  git commit -m "chore(deps): resync uv.lock + requirements.txt after Dependabot bump"
  echo "dependabot-resync.sh: committed regen. Push when ready: git push" >&2
fi

echo "dependabot-resync.sh: done." >&2
