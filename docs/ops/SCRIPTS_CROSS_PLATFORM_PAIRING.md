# Cross-platform script pairing (Windows `.ps1` ↔ Linux/macOS `.sh`)

**Português (Brasil):** [SCRIPTS_CROSS_PLATFORM_PAIRING.pt_BR.md](SCRIPTS_CROSS_PLATFORM_PAIRING.pt_BR.md)

## Purpose

Some **developer gates** and **thin wrappers** exist in **two forms**: **PowerShell** (historical primary workstation: Windows 11) and **bash** (Linux / macOS, CI-like shells, collaborators). This document is the **contract** to keep them **behaviourally aligned** when either side changes — similar in spirit to **code → English docs → pt-BR docs**, but for **automation entry points**.

**Related:** **`.cursor/rules/repo-scripts-wrapper-ritual.mdc`** (always skim the hub before reinventing shell), **`docs/ops/TOKEN_AWARE_SCRIPTS_HUB.md`**, **`.cursor/skills/token-aware-automation/SKILL.md`**.

## Rules (maintainers + assistants)

1. **Paired scripts:** When you **add** or **change behaviour** (flags, order of steps, exit codes, retry logic) in one member of a pair, update the **sibling** in the **same PR** when practical; if not, add a **tracked TODO** (e.g. `PLANS_TODO.md` row) and link both filenames so the gap is visible.
2. **New gate wrapper:** If you introduce a **new** Windows-first **`scripts/*.ps1`** that operators are expected to run routinely from the repo root, consider whether a **`scripts/*.sh`** twin is warranted for Linux — and vice versa if you add a **Linux-first** **`*.sh`** that Windows contributors would miss.
3. **Not everything is paired:** Lab-only **`*.sh`** (SSH targets), Windows-only **`es-find.ps1`**, and large orchestrators may stay **single-platform**; document that in the hub row or script header instead of inventing a hollow twin.
4. **Canonical behaviour:** The **`.ps1`** remains the **reference** for Windows-first docs strings today; **`.sh`** mirrors **intent** (`uv`, `pre-commit`, `pytest` flags). If behaviour diverges, fix the drift — do not “paper over” with docs-only claims.

## Current paired gates (dev PC)

| Intent | Windows | Linux / macOS |
| ------ | ------- | ------------- |
| Full gate (gatekeeper + plans + pre-commit + pytest) | `scripts/check-all.ps1` | `scripts/check-all.sh` |
| Lint / hooks only | `scripts/lint-only.ps1` | `scripts/lint-only.sh` |
| Pytest subset (`-Path` / `-Keyword`) | `scripts/quick-test.ps1` | `scripts/quick-test.sh` |
| Pre-commit + full pytest (no gatekeeper / no plans-stats) | `scripts/pre-commit-and-tests.ps1` | `scripts/pre-commit-and-tests.sh` |
| Pro+ Rust pre-filter build (`maturin develop` for `boar_fast_filter`) | `scripts/build-rust-prefilter.ps1` | `scripts/build-rust-prefilter.sh` |

**Note:** `check-all.ps1` calls **`gatekeeper-audit.ps1`** and **`plans-stats.py`** before delegating to **`pre-commit-and-tests.ps1`**; `check-all.sh` does the same at the shell level. **`pre-commit-and-tests.*`** skips gatekeeper and plans-stats by design.

**Rust builder twin:** `build-rust-prefilter.{ps1,sh}` both call `maturin develop --manifest-path rust/boar_fast_filter/Cargo.toml`, default to `--release`, and accept a `--target`/`-Target` override. The bash twin maps `-Release` ↔ `--release`, `-Debug`/`--no-release` ↔ debug profile, and `-Target X` ↔ `--target X`. Keep both in sync when adding flags (e.g. cargo features, off-by-default profiles).

## Verification

- **Linux / CI:** `bash -n scripts/<name>.sh` (see **`tests/test_scripts.py`**).
- **Windows:** PowerShell parse checks for **`*.ps1`** in the same test module.
