# boar_fast_filter (Rust + PyO3)

High-speed candidate pre-filter for Data Boar Pro+.

Current suspects include:

- CPF-like strings
- email-like strings
- credit card candidates that pass Luhn (13-19 digits)

## Build (dev)

From repository root:

```powershell
uv run pip install maturin
maturin develop --manifest-path rust/boar_fast_filter/Cargo.toml --release
```

This makes `boar_fast_filter` importable in the active Python environment.

Windows helper:

```powershell
.\scripts\build-rust-prefilter.ps1
```

Target override example:

```powershell
.\scripts\build-rust-prefilter.ps1 -Target x86_64-pc-windows-msvc
```

## Quick smoke

```python
from boar_fast_filter import FastFilter
f = FastFilter()
print(f.filter_batch(["clean", "cpf 390.533.447-05", "mail a@example.test"]))
```

## Rust-only test loop (no Python required)

The crate exposes a pure-Rust API (`FastFilter::try_new`,
`FastFilter::filter_batch_pure`, `FastFilter::check_luhn`) so `cargo test`
exercises the same logic that PyO3 binds. From `rust/boar_fast_filter/`:

```bash
cargo fmt --all -- --check
cargo check --all-targets --locked
cargo test --all-targets --locked
cargo clippy --all-targets --locked -- -D warnings
```

CI runs the same four steps via `.github/workflows/rust-ci.yml` (path-scoped
to `rust/**` so unrelated PRs do not spin Rust builds). Clippy uses
`-D warnings`, so any new lint promotes to a CI failure.
