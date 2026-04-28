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

## Integridade (checklist extendido)

Marque o que aplicar ao escopo deste PR (deixe em branco o que for N/A).

- [ ] **Python:** `uv run pytest` e `uv run ruff check .` limpos no escopo tocado.
- [ ] **Rust (`boar_fast_filter`):** alterei `rust/boar_fast_filter/**` ou o bridge Pro — executei `cargo clippy --locked --manifest-path rust/boar_fast_filter/Cargo.toml -- -D warnings` (e build local conforme `rust/boar_fast_filter/README.md` quando necessário).
- [ ] **Benchmark 200k / baseline 0.574x:** confirmei que o contrato em `tests/benchmarks/official_benchmark_200k.json` permanece alinhado — `uv run pytest tests/test_official_benchmark_200k_evidence.py` passa; se o perfil mudou de propósito, atualizei JSON + teste + narrativa no mesmo PR.
- [ ] **Fonte de verdade:** alterações de comportamento/CLI/API/conectores refletidas em `docs/TECH_GUIDE.md` e `docs/TECH_GUIDE.pt_BR.md` quando relevante para operadores.
- [ ] **Léxico de produto:** termos canônicos (**Data Sniffing**, **Deep Boring**, **Audit Trail**, **Safe-Hold**, etc.) não foram traduzidos ad hoc; seguem ADR 0035 / `docs/GLOSSARY.md`.

## Related issues
Fixes (issue number) (if applicable).
