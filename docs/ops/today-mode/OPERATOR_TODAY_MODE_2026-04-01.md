# Operator today mode — 2026-04-01 (release-ready slice, token-aware)

**Português (Brasil):** [OPERATOR_TODAY_MODE_2026-04-01.pt_BR.md](OPERATOR_TODAY_MODE_2026-04-01.pt_BR.md)

**Purpose:** Ship one **coherent, reviewable slice** toward production readiness, without carrying silent backlog. Boundaries: **`carryover-sweep`** · **`eod-sync`** · **`scripts/operator-day-ritual.ps1`**.

---

## Block 0 — Truth + carryover (≈ 15–25 min)

1) Walk **[CARRYOVER.md](CARRYOVER.md)** — close, defer with date, or promote to PLANS/issue for each ⬜.
1) Confirm version truth:
   - **Published**: last tag/release should still be `v1.6.7` unless you published again.
   - **Working**: repo now bumped to **`1.6.8`** (pre-publish tracking).

---

## Block A — Ship the Cursor/MCP + version tracking slice (≈ 30–60 min)

- Create PR for the local commit that bumps working version to **1.6.8** and documents `MCP_DOCKER` troubleshooting.
- Keep it **workflow/docs focused**; no feature work mixed in this PR.

**Token-aware gate:** `.\scripts\lint-only.ps1` is enough for this slice (already green locally).

---

## Block B — WRB (Wabbix) and minimal evidence (≈ 20–40 min)

- Use the paste block: **`docs/ops/WRB_DELTA_SNAPSHOT_2026-03-31.md`**
- Update its “Version truth” bullets if you are now referencing **working 1.6.8** on `main` (and confirm published still `v1.6.7`).
- Send the email (or explicitly defer with a date in **CARRYOVER**).

---

## Block C — Slack ping proof-of-life (≈ 10–15 min)

- Follow **`docs/ops/OPERATOR_NOTIFICATION_CHANNELS.md`** and record a **CHAN-OK** note once phone + desktop alert is confirmed.

---

## Stop condition

Day slice is **done** when:

- **CARRYOVER** updated (no silent pending).
- PR for the `1.6.8` working bump slice is **open** (or merged).
- WRB is **sent** (or deferred with a date).
- Slack ping is **confirmed** (or deferred with a date).
