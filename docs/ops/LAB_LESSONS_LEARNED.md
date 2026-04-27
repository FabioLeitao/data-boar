# LAB Lessons Learned (QA/SRE) — hub

**Português (Brasil):** this page is English-only by convention (same as ADRs and plan prose); the archive folder has **[`lab_lessons_learned/README.pt_BR.md`](lab_lessons_learned/README.pt_BR.md)**.

## What this file is

- **Rolling hub** for the latest lab QA / SRE cycle: scope, verdict, and pointers to **evidence files** (benchmark JSON, checkpoint behaviour, etc.).
- **Immutable history** lives under **`docs/ops/lab_lessons_learned/`** as dated snapshots — see **[`lab_lessons_learned/README.md`](lab_lessons_learned/README.md)** for the contract and ritual.

## Latest session (summary)

**Date:** 2026-04-25 (UTC−3).

**Verdict (short):** Rust `boar_fast_filter` import **OK**; checkpoint + kill-resume **OK**; throttler ramp to max workers **OK**; official 200k benchmark shows Pro path **slower** than OpenCore in the tested profile (**0.574x** — not a business-case speedup yet).

> **Reading the 0.574x figure (operator note).** The recorded
> `speedup_vs_opencore = 0.574` in
> [`tests/benchmarks/official_benchmark_200k.json`](../../tests/benchmarks/official_benchmark_200k.json)
> means **Pro is 0.574x as fast as OpenCore** in this profile, i.e. Pro takes
> roughly `1 / 0.574 ≈ 1.74x` more wall-clock time. The Slack handoff
> phrasing **"0.574x mais lento"** is consistent in direction (Pro slower) but
> arithmetically refers to the same ratio — do not double-invert it when
> updating manifests, executive copy, or lab lessons. The regression guard at
> [`tests/test_official_benchmark_200k_evidence.py`](../../tests/test_official_benchmark_200k_evidence.py)
> pins this direction and the OpenCore ↔ Pro findings parity (`100,000` hits
> on both paths) so prose and JSON cannot drift apart silently.

**Full narrative (frozen):** [`lab_lessons_learned/LAB_LESSONS_LEARNED_2026_04_25.md`](lab_lessons_learned/LAB_LESSONS_LEARNED_2026_04_25.md)

**Evidence paths (repo):**

- `tests/benchmarks/official_benchmark_200k.json`
- Kill/resume scenario uses gitignored local DB + state — see `.gitignore` (`data/qa_completao_*`).

## Archived sessions (public)

| Session date | Snapshot |
| ------------ | -------- |
| 2026-04-25 | [`lab_lessons_learned/LAB_LESSONS_LEARNED_2026_04_25.md`](lab_lessons_learned/LAB_LESSONS_LEARNED_2026_04_25.md) |
| 2026-04-27 | [`lab_lessons_learned/LAB_LESSONS_LEARNED_2026_04_27.md`](lab_lessons_learned/LAB_LESSONS_LEARNED_2026_04_27.md) (reading guide / regression guard for the 0.574x figure; no new measurement) |

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
