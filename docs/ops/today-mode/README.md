# Operator today mode (dated checklists)

**Português (Brasil):** [README.pt_BR.md](README.pt_BR.md)

**Purpose:** One place for **dated day plans** (`OPERATOR_TODAY_MODE_YYYY-MM-DD.md`), the **active carryover queue**, and **how to keep “published” aligned with `pyproject.toml`** so checklists do not drift.

**Session keywords:** Type **`today-mode YYYY-MM-DD`** (English-only token) in chat; see **`.cursor/rules/session-mode-keywords.mdc`**. Morning/evening shell helper: **`scripts/operator-day-ritual.ps1`** (lists recent files under this folder).

---

## Canonical companions (read often)

| Doc | Role |
| --- | ---- |
| [CARRYOVER.md](CARRYOVER.md) | **Rolling queue** — promote, defer, or close items (no silent backlog). |
| [PUBLISHED_SYNC.md](PUBLISHED_SYNC.md) | **GitHub Release + Docker Hub vs repo version** — refresh after each publish. |
| [PRIVATE_OPERATOR_NOTES.md](../../PRIVATE_OPERATOR_NOTES.md) | Private rhythm note path (`docs/private/…`) when relevant. |

---

## Dated checklists (newest last)

| Date | English | pt-BR |
| ---- | ------- | ----- |
| 2026-03-26 | [OPERATOR_TODAY_MODE_2026-03-26.md](OPERATOR_TODAY_MODE_2026-03-26.md) | [OPERATOR_TODAY_MODE_2026-03-26.pt_BR.md](OPERATOR_TODAY_MODE_2026-03-26.pt_BR.md) |
| 2026-03-27 | [OPERATOR_TODAY_MODE_2026-03-27.md](OPERATOR_TODAY_MODE_2026-03-27.md) | [OPERATOR_TODAY_MODE_2026-03-27.pt_BR.md](OPERATOR_TODAY_MODE_2026-03-27.pt_BR.md) |
| 2026-03-29 | [OPERATOR_TODAY_MODE_2026-03-29.md](OPERATOR_TODAY_MODE_2026-03-29.md) | [OPERATOR_TODAY_MODE_2026-03-29.pt_BR.md](OPERATOR_TODAY_MODE_2026-03-29.pt_BR.md) |
| 2026-03-30 | [OPERATOR_TODAY_MODE_2026-03-30.md](OPERATOR_TODAY_MODE_2026-03-30.md) | [OPERATOR_TODAY_MODE_2026-03-30.pt_BR.md](OPERATOR_TODAY_MODE_2026-03-30.pt_BR.md) |
| **2026-03-31** | [OPERATOR_TODAY_MODE_2026-03-31.md](OPERATOR_TODAY_MODE_2026-03-31.md) | [OPERATOR_TODAY_MODE_2026-03-31.pt_BR.md](OPERATOR_TODAY_MODE_2026-03-31.pt_BR.md) |

**WRB paste blocks** stay next to ops runbooks (e.g. **`docs/ops/WRB_DELTA_SNAPSHOT_*.md`**) — not in this folder.

---

## Adding a new day

1. Copy the structure from the **most recent** `OPERATOR_TODAY_MODE_*.md` (or **2026-03-31**).
1. Link **`CARRYOVER.md`** and **`PUBLISHED_SYNC.md`** from Block 0 when the day touches release or carryover.
1. After a **real publish** (tag + GitHub Release + Docker Hub), update **`PUBLISHED_SYNC.md`**, **`docs/plans/PLANS_TODO.md`** release rows if needed, and **`python scripts/plans-stats.py --write`**.

---

## Navigation

- Parent index: **[`docs/ops/README.md`](../README.md)** ([pt-BR](../README.pt_BR.md)).
