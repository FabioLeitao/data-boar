# LAB Lessons Learned — session snapshot 2026-04-27 (Slice 2)

**Archive note:** Immutable snapshot for the **Slice 2** SRE-protocol session
that closed the regression captured by Slice 1
([`LAB_LESSONS_LEARNED_2026_04_27.md`](LAB_LESSONS_LEARNED_2026_04_27.md)
remains the reading-guide for the original `0.574x` figure and is **not**
rewritten — see the archive contract in
[`README.md`](README.md) and
[ADR 0042](../../adr/0042-lab-lessons-learned-archive-contract.md)).

Date: 2026-04-27 (UTC session, post-handoff)

## Trigger (operator handoff)

Slack handoff from the operator to the agent automation:

> Sua missão imediata: identifique o gargalo técnico no motor de processamento
> que causa essa lentidão no perfil Pro e aplique uma refatoração agressiva
> seguindo o padrão NASA de resiliência e a eficiência Savage. Não quero apenas
> explicações; quero um PR com código otimizado que traga a performance para
> perto de 1.0x.

## Root cause analysis (Julia Evans-style)

Three concrete bottlenecks were identified in the Pro Python fallback path:

1. **Double regex pass in `pro/worker_logic.py::basic_python_scan`.**
   - First the row went through `OpenCorePreFilter.filter_candidates()`
     (regex over **every** row).
   - Then **every non-matching row** was scanned **again** with the card-shape
     regex to catch Luhn-valid cards that OpenCore missed.
   - Net effect: ~**2x** the regex work of OpenCore on the synthetic 200k
     workload, which is exactly what the `0.574x` ratio reflected (Pro wall-
     clock ≈ `1 / 0.574 ≈ 1.74x` OpenCore).

2. **Two `re.search` calls per row in `core/prefilter.py`.**
   `_looks_sensitive` ran the CPF regex *and* the e-mail regex; on the hot
   path that is two interpreter dispatches per row.

3. **Phantom `deep_ml_analysis` hop in `pro/engine.py::process_chunk_worker`.**
   Every chunk went through a no-op pass that materialised a second list and
   added a function-call dispatch with no behavioural payload.

## Refactor (NASA / Savage / Gibson posture)

The PR consolidates the three fixes:

- **Fused candidate regex.** `core/prefilter.py` now uses a single compiled
  alternation `_OPENCORE_CANDIDATE_RX = CPF | e-mail`. The hot loop binds
  `_search` locally and uses a list comprehension. The original
  `_CPF_CANDIDATE_RX` and `_EMAIL_CANDIDATE_RX` symbols stay exported for
  backward compatibility.
- **Single-pass Pro fallback.** `pro/worker_logic.basic_python_scan` now uses
  one fused regex `_FUSED_PRO_RX = CPF | e-mail | card-shape` with named
  groups. CPF / e-mail short-circuit on the first match; Luhn arithmetic only
  fires when the regex actually matches a card-shape span. Defensive
  `finditer` walk handles rows that carry both an invalid card and a valid
  CPF / e-mail later in the string (no detection loss).
- **Honest worker pipeline.** `process_chunk_worker` no longer routes through
  `deep_ml_analysis`; the helper stays in the module so external imports do
  not break.
- **Truthful artifact.** `tests/benchmarks/run_official_bench.py` now writes
  `"rust_worker_path": bool(RUST_AVAILABLE)` instead of a hardcoded `True`
  (publication-truthfulness rule, no invented facts).

## Defensive posture (`DEFENSIVE_SCANNING_MANIFESTO.md`)

- **Zero database impact.** The refactor only touches in-memory pre-filter
  code; no SQL is composed, no connection is opened, no lock is acquired.
- **Same finding contract.** OpenCore ↔ Pro hits parity (`100,000 == 100,000`)
  is preserved; the regression guard at
  [`tests/test_official_benchmark_200k_evidence.py`](../../../tests/test_official_benchmark_200k_evidence.py)
  still asserts it.
- **No new public-tier identifiers.** The benchmark seed remains the four-row
  synthetic CPF / e-mail / card-shape / clean-text pattern.

## Resilience posture (`THE_ART_OF_THE_FALLBACK.md`)

- The Rust → Python fallback hierarchy is unchanged: `process_chunk_worker`
  still tries `boar_fast_filter.FastFilter` first and degrades to
  `basic_python_scan` only when the extension is unavailable.
- The faster Python fallback narrows the gap between the strongest and the
  weakest path, which is the doctrinal goal — when the Rust extension is
  missing in customer environments, Pro stays useful instead of being a
  performance regression.

## Verified evidence (this session)

| Profile (200k rows, 8 workers, no Rust) | Before (Slice 1) | After (Slice 2) |
| --------------------------------------- | ---------------- | --------------- |
| `opencore_seconds`                      | `0.252242`       | `0.108942`      |
| `pro_seconds`                           | `0.439419`       | `0.091026`      |
| `speedup_vs_opencore` (`t_open / t_pro`) | `0.574`          | `1.197`         |
| `opencore_hits`                         | `100000`         | `100000`        |
| `pro_hits`                              | `100000`         | `100000`        |
| `rust_worker_path` flag                 | `true` (wrong)   | `false` (real)  |

Both runs were captured on the same Cloud Agent VM under
[`tests/benchmarks/run_official_bench.py`](../../../tests/benchmarks/run_official_bench.py);
the per-run absolute numbers are smaller than the 2026-04-25 lab figures
because of the lighter VM, but the **ratio doctrine** (`speedup >= ~1.0` with
a 5 percent noise band) is what the regression guard now enforces.

## Regression guard update

[`tests/test_official_benchmark_200k_evidence.py`](../../../tests/test_official_benchmark_200k_evidence.py)
flipped polarity:

- The old `test_benchmark_pro_path_is_slower_in_this_profile` was the right
  assertion for Slice 1 (pin a known regression so the docs and JSON could not
  drift). It would now block legitimate Slice 2 progress.
- The new `test_benchmark_pro_path_is_at_least_as_fast` asserts
  `speedup_vs_opencore >= 0.95` (5 percent noise band on slow CI runners).
  Findings parity, JSON arithmetic, and the `official_pro_v1` provenance
  shape stay non-negotiable.

## Follow-ups → plans (tracked)

| Topic                                 | Bridge                                                                                                                                                                          |
| ------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Real Rust path benchmark              | When `boar_fast_filter` is rebuilt for CPython 3.13 in CI, re-run the harness and pin a Rust-on artifact (`rust_worker_path: true`).                                            |
| Production-like profile               | Larger row count, realistic chunking, downstream ML stage — see [`SPRINT_GREAT_LEAP_POSTMORTEM.md`](../SPRINT_GREAT_LEAP_POSTMORTEM.md) "Next verification steps".              |
| Card detection coverage               | Confirm Luhn-only acceptance is consistent with downstream report `card` taxonomy; consider dialect-aware detection in connectors before any "audit-grade" SKU promise.        |
