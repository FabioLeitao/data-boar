# Operator “today mode” — 2026-03-27 (full day)

**Português (Brasil):** [OPERATOR_TODAY_MODE_2026-03-27.pt_BR.md](OPERATOR_TODAY_MODE_2026-03-27.pt_BR.md)

**Purpose:** A **whole day** on **operator surfaces + doc/code alignment** — not just the first 10 minutes. Assumes **2026-03-26 evening** landed the **doc-bundle recovery** PR (playbook, sliding-window audit, meta script, GEMINI/recovery links).

---

## Evening before (2026-03-26) — close the tree

Do this **before** you log off if still open:

1. **`git status`** — only **tracked** paths in scope; **`docs/private/`** stays untracked.
1. **`.\scripts\check-all.ps1`** (or `lint-only` if you already ran full tests).
1. **One coherent PR** (recommended single theme): doc-bundle recovery + workflow tooling — e.g. commits split **`docs(workflow):`** vs **`test(workFlow):`** if you prefer two commits; avoid mixing unrelated product code.
1. **After merge:** optional tag/release only if that was already the plan from [OPERATOR_TODAY_MODE_2026-03-26.md](OPERATOR_TODAY_MODE_2026-03-26.md); do not conflate with this slice unless intentional.

---

## Today (2026-03-27) — recommended blocks

### Block A — Help sync gate (≈ 45–90 min)

- Run **`uv run pytest tests/test_operator_help_sync.py -v`** from repo root.
- Re-read **`docs/OPERATOR_HELP_AUDIT.md`** — treat **Follow-ups** as the backlog for the day, not a footnote.
- If green: note “last run date” in a private line in **`docs/private/GEMINI_WORKFLOW_ROI_AND_HELP_SYNC_PREP.md`** or your journal; if red: fix **code or manifest first**, then surfaces (USAGE, man, `/help`).

### Block B — OpenAPI vs real bodies (≈ 90–120 min)

- **Goal:** Close or shrink the audit checkbox: OpenAPI / Swagger text vs **`POST /scan`** (and related) as implemented in **`api/routes`**.
- **Outcome:** small tracked doc or OpenAPI description edits **or** a single issue capturing intentional gaps (with pointers to code).

### Block C — README exposure one-liner (≈ 30–45 min)

- **Goal:** README + **`.pt_BR.md`**: when you describe LAN / Docker-less exposure, **`--host`** (and link to USAGE) appears without forcing readers to guess loopback defaults.
- **Cross-check:** SECURITY/DEPLOY bullets still match **`core/host_resolution.py`** story.

### Block D — Web `/help` parity skim (≈ 30 min)

- Quick read **`api/templates/help.html`** vs **`main.py`** argparse for **recent** flags (transport, API key, scan options). Not full duplication — **no contradictions**.

### Block E — Recovery tooling dry run (≈ 15–30 min, optional)

- **`.\scripts\recovery-doc-bundle-sanity.ps1`** (no bundle) — confirms pytest compile slice.
- If you keep a private concat copy: one **`--sweep-windows`** run for peace of mind ([DOC_BUNDLE_RECOVERY_PLAYBOOK.md](DOC_BUNDLE_RECOVERY_PLAYBOOK.md)).

### Block F — Plans / Band A thin pass (≈ 30–45 min, optional)

- Skim **`docs/plans/PLANS_TODO.md`** Priority band **–1 / –1b**; don’t start a new feature spiral — **one** checkbox or issue promotion if obvious.

---

## Stop condition

Day is “done” when: **pytest help-sync green**, **OpenAPI follow-up advanced** (merged doc or filed scoped issue), **README `--host` callout** satisfied or explicitly deferred with a **PLANS_TODO** / issue pointer.

---

## Chat shorthand

**`today-mode 2026-03-27`** or open this file.
