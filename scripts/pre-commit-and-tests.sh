#!/usr/bin/env bash
# pre-commit-and-tests.sh — Linux/macOS mirror of scripts/pre-commit-and-tests.ps1.
# Optional: maturin develop for rust/boar_fast_filter when rustc is on PATH (see build-rust-prefilter.ps1).
# Runs pre-commit (unless skipped) then full pytest with warnings as errors.
# Usage (from repo root):
#   ./scripts/pre-commit-and-tests.sh
#   ./scripts/pre-commit-and-tests.sh --skip-pre-commit
# Windows: prefer .\scripts\pre-commit-and-tests.ps1
set -euo pipefail

REPO_ROOT=$(cd "$(dirname "$0")/.." && pwd)
cd "$REPO_ROOT" || exit 2

SKIP_PRECOMMIT=0
while [[ $# -gt 0 ]]; do
  case "$1" in
    -SkipPreCommit | --skip-pre-commit) SKIP_PRECOMMIT=1 ;;
    -h | --help)
      echo "Usage: $0 [--skip-pre-commit]"
      exit 0
      ;;
    *)
      echo "pre-commit-and-tests.sh: unknown option: $1" >&2
      exit 2
      ;;
  esac
  shift
done

if [[ ! -f .venv/pyvenv.cfg ]]; then
  echo "No .venv/pyvenv.cfg - running uv sync to recreate the environment..." >&2
  uv sync
  if [[ ! -f .venv/pyvenv.cfg ]]; then
    echo "pre-commit-and-tests.sh: uv sync did not create .venv; fix disk path or UV_* env and retry." >&2
    exit 2
  fi
fi

# Optional Rust native extension (parity with scripts/build-rust-prefilter.ps1).
# Best-effort; set DATA_BOAR_SKIP_RUST_BUILD=1 to skip. Mirrors pre-commit-and-tests.ps1.
RUST_MANIFEST="$REPO_ROOT/rust/boar_fast_filter/Cargo.toml"
if [[ "$SKIP_PRECOMMIT" -eq 0 ]] && [[ -f "$RUST_MANIFEST" ]] && [[ "${DATA_BOAR_SKIP_RUST_BUILD:-}" != "1" ]]; then
  if command -v rustc >/dev/null 2>&1; then
    echo "Building Rust prefilter (boar_fast_filter)..." >&2
    uv run pip install maturin >/dev/null 2>&1 || true
    if uv run maturin develop --manifest-path "$RUST_MANIFEST" --release; then
      :
    else
      echo "Rust prefilter build failed or incomplete; continuing without native extension (tests may skip)." >&2
    fi
  else
    echo "rustc not on PATH; skipping Rust prefilter build." >&2
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
rc=$?
set -e
if [[ "$rc" -ne 0 ]]; then
  echo "pytest failed. Fix test failures before committing or pushing." >&2
fi
exit "$rc"
