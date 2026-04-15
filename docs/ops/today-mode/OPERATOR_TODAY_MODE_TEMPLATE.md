# Operator today mode — YYYY-MM-DD (carryover + effective focus)

**Português (Brasil):** [OPERATOR_TODAY_MODE_YYYY-MM-DD.pt_BR.md](OPERATOR_TODAY_MODE_YYYY-MM-DD.pt_BR.md)

> Copy this file to **`OPERATOR_TODAY_MODE_<date>.md`**, set the date in the title and links, and replace placeholders. Remove this note when the day file is real.

---

## Block 0 — Morning reality check (10–15 min)

Run **`carryover-sweep`** or **`.\scripts\operator-day-ritual.ps1 -Mode Morning`**, then:

1. `git fetch origin` · `git status -sb` · `gh pr list --state open`
2. **`origin/main`:** pull if another machine merged overnight.
3. **Working tree (public repo):** decide: commits, branch, stash, or continue.
4. **Stacked private git (`docs/private/`):** if pending, schedule **`.\scripts\private-git-sync.ps1`** (and **`-Push`** if policy says so).
5. `- [ ] **Block close (lab / VC):** when pausing or leaving lab later, type **`block-close`** in chat and follow VeraCrypt session policy in **private** **`docs/private/homelab/OPERATOR_VERACRYPT_SESSION_POLICY*.md`** — optional **boundary** checklist, **not** the full **`eod-sync`** git/gh ritual.

**Canonical rolling queue:** [CARRYOVER.md](CARRYOVER.md) · **Published truth:** [PUBLISHED_SYNC.md](PUBLISHED_SYNC.md)

---

## Carryover — (edit)

- [ ] (items)

---

## End of day

- **`block-close`** + VeraCrypt (private homelab policy above) when ending a **work block** or leaving lab; **`eod-sync`** for **`operator-day-ritual -Mode Eod`** + git/gh/PR + tomorrow’s today-mode pointer.
- **`eod-sync`** in chat **or** **`.\scripts\operator-day-ritual.ps1 -Mode Eod`**
- Prepare or skim **`OPERATOR_TODAY_MODE_<next-date>.md`** next

---

## Quick references

- Token-aware hub (if in tree): `docs/ops/TOKEN_AWARE_SCRIPTS_HUB.md`
- Session keywords: **`.cursor/rules/session-mode-keywords.mdc`** (**`block-close`**, **`eod-sync`**, **`private-stack-sync`**)
- Private rhythm: `docs/private/TODAY_MODE_CARRYOVER_AND_FOUNDER_RHYTHM.md`
