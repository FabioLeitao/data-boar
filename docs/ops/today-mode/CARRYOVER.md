# Today-mode carryover queue (rolling)

**Português (Brasil):** [CARRYOVER.pt_BR.md](CARRYOVER.pt_BR.md)

**Purpose:** Single **rolling list** of operator items that survive across dated `OPERATOR_TODAY_MODE_*` files. **Close, defer with date, or move to `PLANS_TODO` / an issue** — nothing immortal without an owner.

**Related:** **`carryover-sweep`** (morning), **`eod-sync`** (evening), **`docs/private/TODAY_MODE_CARRYOVER_AND_FOUNDER_RHYTHM.md`** (private).

---

## Queue (update in place)

| Item | Source | Status | Next step / defer |
| ---- | ------ | ------ | ----- |
| **Wabbix WRB** e-mail | 2026-03-26 / 03-29 / 03-31 | ⬜ Pending | Paste block: **`docs/ops/WRB_DELTA_SNAPSHOT_2026-03-31.md`** — send today or defer with a date in PLANS/private |
| **Slack** proof-of-ping (desktop + phone) | 2026-03-27 | ⬜ Pending | **`docs/ops/OPERATOR_NOTIFICATION_CHANNELS.md`** — confirmed ding or note **CHAN-OK** |
| **Dependabot** PRs (#134 pypdf, #143 pip group, #144 starlette) | 2026-03-29 / 30 | ⬜ Pending | **`deps`** session; **`gh pr checks`** + merge when green per **`SECURITY.md`** |
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
