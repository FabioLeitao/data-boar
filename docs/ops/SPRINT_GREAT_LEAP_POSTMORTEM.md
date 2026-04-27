# Sprint post-mortem: Pro+ discovery, Rust pre-filter, SRE throttling

**Português (Brasil):** [SPRINT_GREAT_LEAP_POSTMORTEM.pt_BR.md](SPRINT_GREAT_LEAP_POSTMORTEM.pt_BR.md)

This note separates **verified evidence** from **aspirational lab targets**. Only verified rows should appear in customer-facing material.

## Verified in this repository session (evidence-backed)

Source of truth: [LAB_LESSONS_LEARNED.md](LAB_LESSONS_LEARNED.md) (hub; dated snapshots: [lab_lessons_learned/LAB_LESSONS_LEARNED_2026_04_25.md](lab_lessons_learned/LAB_LESSONS_LEARNED_2026_04_25.md), [lab_lessons_learned/LAB_LESSONS_LEARNED_2026_04_27_slice2.md](lab_lessons_learned/LAB_LESSONS_LEARNED_2026_04_27_slice2.md)), `tests/benchmarks/official_benchmark_200k.json`, checkpoint file from kill test.

| Topic | Result |
| ----- | ------ |
| Rust extension `boar_fast_filter` | Built and importable in project `.venv` (PyO3 updated for CPython 3.13). |
| Official benchmark (200k rows, 8 workers) — Slice 1 (frozen) | OpenCore `0.252242s`, Pro path `0.439419s`, `speedup_vs_opencore = 0.574` (Pro **slower** in that profile). |
| Official benchmark (200k rows, 8 workers) — Slice 2 (current) | OpenCore `0.108942s`, Pro path `0.091026s`, `speedup_vs_opencore = 1.197` (Pro **faster** after the fused-regex refactor; Python fallback path, `rust_worker_path: false`). |
| Checkpoint + kill resume | `last_processed_id` advanced from `104000` to table end; second run completed with consistent finding counts. |
| Throttling | `BoarThrottler` increased concurrency toward configured max during scan. |

## Not verified here (do not claim without a reproducible lab run)

The numbers below are **examples of what a future lab-op campaign might target**. They are **not** recorded as measured outcomes in this repo session.

| Claim | Status |
| ----- | ------ |
| 1,000,000 mock rows end-to-end | Not executed in this documentation pass. |
| OpenCore ~420s vs Pro+ ~28s (~15x) | Not measured; contradicts current official benchmark artifact. |
| “100% false positive reduction” on random numeric sequences | Not measured as a controlled study; Luhn reduces obvious non-Luhn card shapes only. |
| Full `completao` orchestrator green on lab-op | Not completed end-to-end in this assistant session. |

## Technical conclusions (honest)

- **Checkpointing and throttling** are the strongest “mission critical” wins captured here.
- **Performance marketing** needs a benchmark profile aligned with real workloads (chunk size, downstream ML cost, I/O realism) before quoting speedups.
- **Direction vs ratio (do not double-invert).** `speedup_vs_opencore = X` is `t_open / t_pro`. Slice 1 captured `X = 0.574` (Pro slower, ~`1.74x` OpenCore wall-clock); Slice 2 records `X = 1.197` (Pro faster) after the fused-regex refactor. The regression guard [`tests/test_official_benchmark_200k_evidence.py`](../../tests/test_official_benchmark_200k_evidence.py) now requires `speedup >= 0.95` (5 percent noise band) plus the OpenCore ↔ Pro findings parity (`100,000` hits on both paths), so future executive copy or manifests cannot drift from the recorded artifact silently.
- **Refactor that fixed the regression (Slice 2).** Three concrete bottlenecks in the Python fallback: (a) double regex pass in `pro/worker_logic.basic_python_scan` (OpenCore regex, then card regex on the misses); (b) two `re.search` calls per row in `core/prefilter.OpenCorePreFilter._looks_sensitive`; (c) phantom `deep_ml_analysis` no-op hop in `pro/engine.process_chunk_worker`. The refactor fuses CPF / e-mail / card-shape into a single compiled alternation with named groups, short-circuits CPF and e-mail, fires Luhn arithmetic only when the regex actually matches a card-shape span, and removes the no-op hop. Same finding contract; zero database impact.

## Next verification steps

1. Re-run `tests/benchmarks/run_official_bench.py` at scale after tuning chunking and worker count; archive JSON under `tests/benchmarks/`.
2. Run full lab-op `completao` and attach logs under private homelab reports per runbook.
3. If integrity auto-defense is required in product, implement per `INTEGRITY_CHECK_ALPHA_LOGIC.md` with an ADR.
