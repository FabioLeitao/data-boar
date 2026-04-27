#!/usr/bin/env bash
# build-rust-prefilter.sh - Linux/macOS twin of scripts/build-rust-prefilter.ps1.
#
# Build and install the optional Pro+ Rust pre-filter (boar_fast_filter / PyO3)
# into the active uv-managed Python environment via maturin develop. Behaviour
# mirrors the PowerShell helper:
#   - default to --release (override with --debug or --no-release)
#   - optional --target <triple> for cross-compile
#   - clear, deterministic exit codes (no silent fallthrough)
#
# Cross-platform pairing contract:
#   docs/ops/SCRIPTS_CROSS_PLATFORM_PAIRING.md
#   .cursor/rules/repo-scripts-wrapper-ritual.mdc
#
# Usage (from repo root):
#   ./scripts/build-rust-prefilter.sh
#   ./scripts/build-rust-prefilter.sh --debug
#   ./scripts/build-rust-prefilter.sh --target x86_64-unknown-linux-gnu
#
# Windows: prefer .\scripts\build-rust-prefilter.ps1 (identical intent).
set -euo pipefail

REPO_ROOT=$(cd "$(dirname "$0")/.." && pwd)
MANIFEST="$REPO_ROOT/rust/boar_fast_filter/Cargo.toml"

RELEASE=1
TARGET=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    -Release | --release) RELEASE=1 ;;
    -Debug | --debug | --no-release) RELEASE=0 ;;
    -Target | --target)
      if [[ $# -lt 2 ]]; then
        echo "build-rust-prefilter.sh: missing value for $1" >&2
        exit 2
      fi
      TARGET="$2"
      shift
      ;;
    -h | --help)
      echo "Usage: $0 [--release|--debug] [--target TRIPLE]"
      echo "  --release            Build release profile (default; same as PS1 -Release)"
      echo "  --debug|--no-release Build debug profile (same as PS1 -Release:\$false)"
      echo "  --target TRIPLE      Pass --target TRIPLE to maturin"
      exit 0
      ;;
    *)
      echo "build-rust-prefilter.sh: unknown option: $1" >&2
      exit 2
      ;;
  esac
  shift
done

if [[ ! -f "$MANIFEST" ]]; then
  echo "Rust manifest not found: $MANIFEST" >&2
  exit 2
fi

if ! command -v uv >/dev/null 2>&1; then
  echo "build-rust-prefilter.sh: uv not on PATH; install uv first (https://docs.astral.sh/uv/)." >&2
  exit 2
fi

if ! command -v cargo >/dev/null 2>&1; then
  echo "build-rust-prefilter.sh: cargo not on PATH; install Rust toolColleague-Nn (https://rustup.rs)." >&2
  exit 2
fi

cd "$REPO_ROOT"

echo "=== build-rust-prefilter.sh: maturin develop (boar_fast_filter) ===" >&2
echo "  manifest: $MANIFEST" >&2
echo "  release : $RELEASE" >&2
if [[ -n "$TARGET" ]]; then
  echo "  target  : $TARGET" >&2
fi

uv run pip install maturin

args=(develop --manifest-path "$MANIFEST")
if [[ "$RELEASE" -eq 1 ]]; then
  args+=(--release)
fi
if [[ -n "$TARGET" ]]; then
  args+=(--target "$TARGET")
fi

# Prefer the maturin shim that uv installed into the project venv; fall back to
# any maturin already on PATH (system / user install) for environments where the
# venv shim is not visible to the calling shell.
if [[ -x "$REPO_ROOT/.venv/bin/maturin" ]]; then
  MATURIN_BIN="$REPO_ROOT/.venv/bin/maturin"
elif command -v maturin >/dev/null 2>&1; then
  MATURIN_BIN=$(command -v maturin)
else
  echo "build-rust-prefilter.sh: maturin shim not found after uv pip install; check uv venv layout." >&2
  exit 2
fi

"$MATURIN_BIN" "${args[@]}"

echo "[OK] boar_fast_filter installed in current Python environment." >&2
