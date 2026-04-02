# Today-mode carryover queue (rolling)

**Português (Brasil):** [CARRYOVER.pt_BR.md](CARRYOVER.pt_BR.md)

**Purpose:** Single **rolling list** of operator items that survive across dated `OPERATOR_TODAY_MODE_*` files. **Close, defer with date, or move to `PLANS_TODO` / an issue** — nothing immortal without an owner.

**Related:** **`carryover-sweep`** (morning), **`eod-sync`** (evening), **`docs/private/TODAY_MODE_CARRYOVER_AND_FOUNDER_RHYTHM.md`** (private).

---

## Queue (update in place)

| Item | Source | Status | Next step / defer |
| ---- | ------ | ------ | ----- |
| Close **1.6.8 release gate** (notes + tests + publish/defer decision) | 2026-04-02 | ⬜ Pending | Follow `OPERATOR_TODAY_MODE_2026-04-02.md` Block C; if deferred, write explicit target date |
| New external round **WRB + Gemini** with "code is truth" framing | 2026-04-02 | ⬜ Pending | Send WRB with 3 time lenses and build Gemini bundle with `--verify`; triage in `PLAN_GEMINI_FEEDBACK_TRIAGE.md` |
| Quantified snapshot (today / 3 days / 7 days) with front split | 2026-04-02 | ⬜ Pending | Run `.\scripts\progress-snapshot.ps1 -OutputMarkdown docs/private/progress/progress_snapshot_2026-04-02.md` |
| Founder LinkedIn/ATS profile full refresh | 2026-04-02 | ⬜ Pending | Apply private playbook section in `LINKEDIN_ATS_AND_POSITIONING_PLAYBOOK.pt_BR.md` |
| Time Machine USB recovery before repurposing as P0 external backup | 2026-04-02 | ⬜ Pending | Follow `docs/ops/TIME_MACHINE_USB_RECOVERY_AND_REPURPOSE.md` (read-only triage -> copy -> wipe -> new backup policy) |
| **Wabbix WRB** e-mail | 2026-03-26 / 03-29 / 03-31 | ⬜ Pending | Paste block: **`docs/ops/WRB_DELTA_SNAPSHOT_2026-03-31.md`** — send today or defer with a date in PLANS/private |
| **Slack** proof-of-ping (desktop + phone) | 2026-03-27 | ✅ Done | Founder-only channel confirmed; ping received on desktop + phone (**CHAN-OK**) |
| **Dependabot** PRs (#134 pypdf, #144 starlette, #147 pip group) | 2026-03-29 / 30 / 03-31 | ✅ Done | Merged (green + mergeable). Keep watching new PRs per **`SECURITY.md`** |
| **Branch protection** (required checks) | 2026-03-26 optional | ⬜ Optional | Enable when you want CI/Semgrep enforced on `main` |
| **Gemini Cold doc slice** (e.g. G-26-04 + G-26-13) | `PLANS_TODO.md` | ⬜ Optional | One **`docs`** PR; safest items first |
| **`/help` vs `main.py`** parity skim | 2026-03-29 | ⬜ When flags change | After next CLI/dashboard flag — **`tests/test_operator_help_sync.py`** |

**Done / archived (do not resurrect without new work):**

- **Tag `v1.6.7` + GitHub Release + Docker Hub** — shipped **2026-03-26** — see [PUBLISHED_SYNC.md](PUBLISHED_SYNC.md).
- **Help-sync / OpenAPI / README `--host`** for the 2026-03-27 pass — see completion logs in [OPERATOR_TODAY_MODE_2026-03-27.md](OPERATOR_TODAY_MODE_2026-03-27.md).

---

## Housekeeping PR (this folder move)

If you have **local commits** that created **`docs/ops/today-mode/`**, finish themed commits (docs/workflow), run **`.\scripts\lint-only.ps1`** or **`check-all`**, then merge to `main`.

---

## T14 + LMDE (parallel)

Hardware install is **out of Git** — use **[`docs/ops/LMDE7_T14_DEVELOPER_SETUP.md`](../LMDE7_T14_DEVELOPER_SETUP.md)** ([pt-BR](../LMDE7_T14_DEVELOPER_SETUP.pt_BR.md)) when the laptop is ready for **uv**, **git**, **SSH** keys, and repo clone.
