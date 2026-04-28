# Integrity audit protocol

**Português (Brasil):** [AUDIT_PROTOCOL.pt_BR.md](AUDIT_PROTOCOL.pt_BR.md)

This document governs **alignment between code and the technical promise** of Data Boar for maintainers, agents, and reviewers. It complements gates already enforced in CI (pytest, Ruff, plans hub, PII guards) and **does not replace** them.

## Translation rigour (LCM-style operator prose)

Portuguese (Brazil) operator-facing text should read like **deliberate technical Brazilian Portuguese**, not a word-for-word gloss of English.

- **Avoid:** calques that sound like UI translated by inertia (for example, *"o script permite você..."* when the intent is capability exposure).
- **Prefer:** direct, accountable phrasing — *"o script expõe a funcionalidade..."*, *"a ferramenta assegura o rastro de auditoria..."* — while keeping **product terms** (Data Sniffing, Deep Boring, Safe-Hold, Audit Trail) as established in the glossary and stakeholder docs.

Full locale contract: **`.cursor/rules/docs-locale-pt-br-contract.mdc`**. After substantive edits to tracked **`*.pt_BR.md`**, run **`uv run pytest tests/test_docs_pt_br_locale.py`**.

## Native core (Rust)

The **`boar_fast_filter`** extension is part of the performance story. When touching the hot path or packaged wheel:

- Run **`cargo clippy --locked`** (and the project’s documented Rust checks) on the native crate before claiming the core is clean.
- Prefer **native fixes** when profiling shows the bottleneck inside the Rust layer; Python changes should not mask a core regression.

## Performance evidence and regression ADR

Any intentional change that **weakens** the published A/B interpretation for the official 200k profile must be accompanied by:

1. Regenerated **`tests/benchmarks/official_benchmark_200k.json`** (when the profile is re-run), and
2. Updated narrative in **`docs/ops/LAB_LESSONS_LEARNED.md`** / post-mortem docs as needed, and
3. If the change is a deliberate trade-off (not a bugfix), an **ADR** that records the regression or new baseline — see existing discussion in **`docs/ops/SPRINT_GREAT_LEAP_POSTMORTEM.md`**.

**Reading the 0.574 figure:** `speedup_vs_opencore = 0.574` means Pro is **0.574× as fast as** OpenCore in that artifact (Pro **slower**). The pytest guard **`tests/test_official_benchmark_200k_evidence.py`** pins direction and key fields so docs and marketing cannot drift silently.

## Related

- **`.cursor/rules/persona-rigor.mdc`** — assistant persona and Safe-Hold discipline.
- **`docs/ops/LAB_LESSONS_LEARNED.md`** — rolling hub for lab evidence.
- **`tests/benchmarks/run_official_bench.py`** — regenerates the JSON artifact when re-measured.
