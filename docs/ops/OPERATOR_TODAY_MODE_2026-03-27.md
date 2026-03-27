# Operator “today mode” — 2026-03-27 (full day)

**Português (Brasil):** [OPERATOR_TODAY_MODE_2026-03-27.pt_BR.md](OPERATOR_TODAY_MODE_2026-03-27.pt_BR.md)

**Purpose:** A **whole day** on **operator surfaces + doc/code alignment** — not just the first 10 minutes. **2026-03-26 evening** landed the **doc-bundle recovery** PR (merged); start below with **carryover + Slack**, then the technical blocks.

**Open this file first** when you sit down (**`today-mode 2026-03-27`**).

---

## Block 0 — First (≈ 20–40 min): carryover + Slack must actually ping you

### 0a — Sweep prior “today mode” dangling (no immortal backlog)

- Open **[OPERATOR_TODAY_MODE_2026-03-26.md](OPERATOR_TODAY_MODE_2026-03-26.md)** — anything still unchecked (e.g. **tag `v1.6.7` + GitHub Release + Docker**, **Wabbix WRB**, optional **branch protection**) either **do today**, **move to one PLANS row / issue**, or **defer explicitly** with a date — don’t leave it **dangling forever**.
- Optional weekly habit: skim **all** `docs/ops/OPERATOR_TODAY_MODE_*.md` still relevant; operator note **`docs/private/TODAY_MODE_CARRYOVER_AND_FOUNDER_RHYTHM.md`** explains daily vs founder checkpoint.

### 0b — Slack notifications (hard requirement before trusting “you were pinged”)

- **Problem to solve:** private channel + desktop open is **not enough** if **Windows** and **iPhone** never show a notification — you won’t see agent/CI signals on channel B.
- **Do:** read **[OPERATOR_NOTIFICATION_CHANNELS.md](OPERATOR_NOTIFICATION_CHANNELS.md)** (+ **[pt-BR](OPERATOR_NOTIFICATION_CHANNELS.pt_BR.md)**) and **prove** delivery: send a **test** to the channel, confirm **notification settings** (app + OS: Focus/DND, Slack mobile alerts), and trigger or verify the **“Slack operator ping (manual)”** / **CI failure** workflow path if configured. Goal: **one** confirmed ding on **phone** and **desktop** you actually notice.
- **Secrets** stay in GitHub Actions / env — never paste webhooks in chat or tracked docs.

---

## Today (2026-03-27) — technical blocks (after Block 0)

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

Day is “done” when: **Block 0** has either **Slack proof-of-ping** or a **tracked/next-step** note (issue/PLANS) for why not yet; **prior today-mode carryovers** are not invisible; and **pytest help-sync green**, **OpenAPI follow-up advanced** (merged doc or filed scoped issue), **README `--host` callout** satisfied or explicitly deferred with a **PLANS_TODO** / issue pointer.

---

## Chat shorthand

**`today-mode 2026-03-27`** or open this file.
