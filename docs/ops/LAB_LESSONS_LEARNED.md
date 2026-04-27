# LAB Lessons Learned (QA/SRE) — hub

**Português (Brasil):** this page is English-only by convention (same as ADRs and plan prose); the archive folder has **[`lab_lessons_learned/README.pt_BR.md`](lab_lessons_learned/README.pt_BR.md)**.

## What this file is

- **Rolling hub** for the latest lab QA / SRE cycle: scope, verdict, and pointers to **evidence files** (benchmark JSON, checkpoint behaviour, etc.).
- **Immutable history** lives under **`docs/ops/lab_lessons_learned/`** as dated snapshots — see **[`lab_lessons_learned/README.md`](lab_lessons_learned/README.md)** for the contract and ritual.

## Latest session (summary)

**Date:** 2026-04-27 (UTC, Slice 2).

**Verdict (short):** Pro Python fallback regression closed. Single-pass fused
regex in `core/prefilter.py` and `pro/worker_logic.py::basic_python_scan`,
plus removal of the no-op `deep_ml_analysis` hop in `pro/engine.py`, brings
the official 200k benchmark from **`speedup_vs_opencore = 0.574`** (Pro
slower) to **`1.197`** (Pro faster) on the same synthetic seed. Rust path
remains unchanged; findings parity (`100,000 == 100,000`) and zero DB-lock
impact are preserved per
[`DEFENSIVE_SCANNING_MANIFESTO.md`](inspirations/DEFENSIVE_SCANNING_MANIFESTO.md)
and the fallback hierarchy in
[`THE_ART_OF_THE_FALLBACK.md`](inspirations/THE_ART_OF_THE_FALLBACK.md).

**Previous session (frozen):** the `0.574x` figure and its reading guide are
preserved at
[`lab_lessons_learned/LAB_LESSONS_LEARNED_2026_04_25.md`](lab_lessons_learned/LAB_LESSONS_LEARNED_2026_04_25.md)
and
[`lab_lessons_learned/LAB_LESSONS_LEARNED_2026_04_27.md`](lab_lessons_learned/LAB_LESSONS_LEARNED_2026_04_27.md);
the Slice 2 dated archive is
[`lab_lessons_learned/LAB_LESSONS_LEARNED_2026_04_27_slice2.md`](lab_lessons_learned/LAB_LESSONS_LEARNED_2026_04_27_slice2.md).

> **Reading the new ratio (operator note).** The artifact
> [`tests/benchmarks/official_benchmark_200k.json`](../../tests/benchmarks/official_benchmark_200k.json)
> now records `speedup_vs_opencore = 1.197` (Pro `0.091s` vs OpenCore
> `0.109s` on the Cloud Agent VM). The number is `t_open / t_pro`, so
> `> 1.0` means Pro **faster**, not slower; the regression guard at
> [`tests/test_official_benchmark_200k_evidence.py`](../../tests/test_official_benchmark_200k_evidence.py)
> now requires `speedup >= 0.95` (5 percent noise band on slow CI). Findings
> parity (`100,000` on both paths) stays non-negotiable, with or without the
> Rust extension. The `rust_worker_path` flag is now derived from
> `pro.engine.RUST_AVAILABLE` instead of being hardcoded.

**Evidence paths (repo):**

- `tests/benchmarks/official_benchmark_200k.json`
- Kill/resume scenario uses gitignored local DB + state — see `.gitignore` (`data/qa_completao_*`).

## Archived sessions (public)

| Session date | Snapshot |
| ------------ | -------- |
| 2026-04-25 | [`lab_lessons_learned/LAB_LESSONS_LEARNED_2026_04_25.md`](lab_lessons_learned/LAB_LESSONS_LEARNED_2026_04_25.md) |
| 2026-04-27 | [`lab_lessons_learned/LAB_LESSONS_LEARNED_2026_04_27.md`](lab_lessons_learned/LAB_LESSONS_LEARNED_2026_04_27.md) (reading guide / regression guard for the 0.574x figure; no new measurement) |
| 2026-04-27 (Slice 2) | [`lab_lessons_learned/LAB_LESSONS_LEARNED_2026_04_27_slice2.md`](lab_lessons_learned/LAB_LESSONS_LEARNED_2026_04_27_slice2.md) (Pro Python fallback refactor; single-pass fused regex; new artifact, polarity-flipped guard) |

## Follow-ups → plans (tracked)

When a lesson becomes engineering work, promote it to **`docs/plans/PLANS_TODO.md`** (and refresh `python scripts/plans-stats.py --write`). Current bridge from the 2026-04-25 session:

| Topic | Bridge |
| ----- | ------ |
| Pro+ benchmark / executive claims | Verified vs aspirational table: [`docs/ops/SPRINT_GREAT_LEAP_POSTMORTEM.md`](SPRINT_GREAT_LEAP_POSTMORTEM.md); production-like benchmark profile before uplift narrative. |
| Integrity / tamper posture | [`docs/ops/INTEGRITY_CHECK_ALPHA_LOGIC.md`](INTEGRITY_CHECK_ALPHA_LOGIC.md), [`docs/ops/RELEASE_INTEGRITY.md`](RELEASE_INTEGRITY.md), plan row **Build identity & release integrity** in `PLANS_TODO.md`. |
| Completão narrative (private) | Use `docs/private/homelab/COMPLETAO_SESSION_*.md` per [`docs/ops/LAB_COMPLETAO_RUNBOOK.md`](LAB_COMPLETAO_RUNBOOK.md); mirror **numbers and pass/fail** here only. |

## Automation / assistant latch

- **Session token:** **`lab-lessons`** (English-only) loads **`.cursor/rules/lab-lessons-learned-archive.mdc`** when globs do not attach it — see [`docs/ops/OPERATOR_AGENT_COLD_START_LADDER.md`](OPERATOR_AGENT_COLD_START_LADDER.md) § *Token → rule latch (`lab-lessons`)`.
- **ADR:** [`docs/adr/0042-lab-lessons-learned-archive-contract.md`](../adr/0042-lab-lessons-learned-archive-contract.md).
