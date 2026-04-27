# boar_fast_filter (Rust + PyO3)

High-speed candidate pre-filter for Data Boar Pro+.

Current suspects include:

- CPF-like strings
- email-like strings
- credit card candidates that pass Luhn (13-19 digits)

## Build (dev)

From repository root, either invoke `maturin` directly or use one of the
cross-platform helper scripts (kept in lock-step per
[`docs/ops/SCRIPTS_CROSS_PLATFORM_PAIRING.md`](../../docs/ops/SCRIPTS_CROSS_PLATFORM_PAIRING.md)).

Direct (any OS):

```bash
uv run pip install maturin
maturin develop --manifest-path rust/boar_fast_filter/Cargo.toml --release
```

This makes `boar_fast_filter` importable in the active Python environment.

Windows helper:

```powershell
.\scripts\build-rust-prefilter.ps1
.\scripts\build-rust-prefilter.ps1 -Target x86_64-pc-windows-msvc
```

Linux / macOS helper (twin of the PowerShell script):

```bash
./scripts/build-rust-prefilter.sh
./scripts/build-rust-prefilter.sh --target x86_64-unknown-linux-gnu
./scripts/build-rust-prefilter.sh --debug   # skip --release
```

## Quick smoke

```python
from boar_fast_filter import FastFilter
f = FastFilter()
print(f.filter_batch(["clean", "cpf 390.533.447-05", "mail a@example.test"]))
```
