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

## Engineering doctrine (apply when the surface is governed)
Skip the items that do not apply to this PR. The full contract is in
[`.cursor/rules/engineering-doctrine-and-performance-baseline.mdc`](../.cursor/rules/engineering-doctrine-and-performance-baseline.mdc).

- [ ] **Source of truth:** if code changed, the matching `docs/USAGE*.md`,
  `docs/TECH_GUIDE*.md`, manifesto, or ADR is updated in this PR (or
  explicitly deferred with rationale).
- [ ] **Rust core:** when `rust/boar_fast_filter/**` changed, ran
  `cargo fmt --check`, `cargo clippy --locked -- -D warnings`, and
  `cargo test --locked`.
- [ ] **Performance baseline (Pro hot path):** when `pro/**`, `rust/**`,
  or `tests/benchmarks/**` changed, either re-ran the 200k benchmark on the
  lab host (`scripts/benchmark-ab.ps1`) and updated
  `docs/plans/BENCHMARK_EVOLUTION.md` §8, or stated explicitly that the
  change is **algorithmic-only** and the regression guard
  (`tests/test_official_benchmark_200k_evidence.py`) is unaffected.
  (Reminder: `speedup_vs_opencore = 0.574` means **Pro is 0.574x as fast
  as OpenCore** — a debt baseline to improve from, not a floor to stay
  above. Do not double-invert the figure in PR copy.)
- [ ] **Sacred lexicon:** kept `Data Sniffing` / `Deep Boring` / `Safe-Hold`
  / `Audit Trail` un-translated and **out of** the README executive pitch
  slice ([ADR 0035](../docs/adr/0035-readme-stakeholder-pitch-vs-deck-vocabulary.md)).
- [ ] **Defensive scanning manifesto:** when touching `connectors/sql_sampling.py`,
  `core/scan_audit_log.py`, or any new SQL composition path, named the
  clause engaged (sample cap, statement timeout, dialect posture, leading
  SQL comment, fallback hierarchy demotion log).

## Related issues
Fixes (issue number) (if applicable).
