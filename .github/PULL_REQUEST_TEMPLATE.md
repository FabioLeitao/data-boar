## Description
Brief description of the change and why it is needed.

## Type of change
- [ ] Bug fix
- [ ] New feature
- [ ] Documentation
- [ ] Refactor / maintenance
- [ ] Other (describe):

## Checklist
- [ ] Tests pass locally (`uv run pytest`).
- [ ] Lint passes (`uv run ruff check .`) and no new linter/format issues.
- [ ] Docs/README updated if behaviour or setup changed.
- [ ] Security-sensitive changes: considered impact and SECURITY.md (e.g. dependency changes, config, auth).

## Integrity checklist (Data Boar protocol)

- [ ] **Python:** `uv run pytest` and `uv run ruff check .` pass (or `./scripts/check-all.sh` / `.\scripts\check-all.ps1` where that is the operator gate).
- [ ] **Rust core:** `cargo clippy --locked` passes on the native engine (`boar_fast_filter` / crate under `rust/` as documented in CONTRIBUTING) when this PR touches the hot path, FFI, or packaged extension.
- [ ] **Performance evidence:** If this PR changes the 200k official benchmark profile or its interpretation, `tests/benchmarks/official_benchmark_200k.json` and `tests/test_official_benchmark_200k_evidence.py` were updated together (the pinned ratio is **`speedup_vs_opencore = 0.574`** — Pro slower than OpenCore in that artifact; do not invert the story without updating the JSON).
- [ ] **Doc drift:** Paired EN + `*.pt_BR.md` surfaces reflect behaviour changes (see **`docs/ops/AUDIT_PROTOCOL.md`**).
- [ ] **pt-BR copy:** No new calques or “translated UI” tone in operator-facing Portuguese; product terms stay as in the glossary (Data Sniffing, Deep Boring, Safe-Hold, Audit Trail).

## Related issues
Fixes (issue number) (if applicable).
