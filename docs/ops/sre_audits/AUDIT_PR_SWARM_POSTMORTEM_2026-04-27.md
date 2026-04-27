# SRE postmortem — audit-PR swarm vs. one mergeable fix (2026-04-27)

> **Status:** Postmortem (blameless RCA)
> **Trigger:** Slack `#data-boar-ops`, automation `def95df7-a634-431a-93e5-659e4d831725`, 2026-04-27 ~21:51 UTC.
> **Author:** SRE Automation Agent (Cursor Cloud Agent, Linux VM).
> **Scope:** doc-only. Zero touch on `connectors/`, `core/`, `report/`, sampling, locks, or PII guard surface.
> **Form:** [`linuxmint/live-installer#177`](https://github.com/linuxmint/live-installer/issues/177) /
> [`#178`](https://github.com/linuxmint/live-installer/issues/178) — concrete evidence,
> reproducible commands, one RCA, one GTD next move.

---

## 0 — TL;DR (one screen)

Between 17:04 and 21:51 UTC on 2026-04-27, **fifteen** Slack-triggered SRE agent runs
opened **eleven draft "audit / refusal" PRs** around a single Dependabot signal
(`pyo3 0.23.5 → 0.24.1` on `rust/boar_fast_filter/`). The actual remediation already
existed as **PR #226** (Dependabot, MERGEABLE / CLEAN, 9/9 checks green) and was
re-pushed by an agent as **PR #266** (also MERGEABLE / CLEAN, 9/9 checks green). The
operator's Slack reply asked the next agent to *read its own rules*, *not refuse*, and
*not repeat the past PII leaks behind ADR 0018 / 0019*.

This file is the postmortem the swarm should have produced **once**, not eleven times.
It does not add another refusal PR; it converts the swarm into one GTD move and
records why the pattern must stop.

| Metric                                           | Value at 2026-04-27 21:57 UTC                                                                                                                                                                                                          |
| :----------------------------------------------- | :--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Open Dependabot PRs on `main`                    | 5 (#221, #222, #223, #224, **#226**)                                                                                                                                                                                                   |
| Dependabot PRs with green CI + MERGEABLE / CLEAN | **1** (#226, `pyo3` Cargo)                                                                                                                                                                                                              |
| Agent-authored "audit / refusal" draft PRs today | **≥ 11** (#241, #247, #257, #259, #261, #265, #267, #268, #269, plus this PR's pre-cursors). All `isDraft: true`.                                                                                                                       |
| Agent-authored *remediation* PR                  | **1** (#266 — same payload as #226).                                                                                                                                                                                                   |
| ADR 0018 / 0019 PII guards on this branch        | `uv run python scripts/pii_history_guard.py` → `OK`. `uv run pytest tests/test_pii_guard.py -v` → **3 passed** (verified 2026-04-27 21:56 UTC, see §4).                                                                                |
| Operator action queue impact                     | High signal-to-noise loss: the one merge-ready PR (#226 or #266) is buried under refusal text the operator must triage.                                                                                                                |

**One GTD recommendation:** merge **#226** (Dependabot, original branch — preserves
provenance and auto-resolves the alert). Close **#266** as superseded once #226 lands.
Close the audit / refusal drafts (#267, #268, #269) as superseded by **this**
postmortem so the queue collapses to one clear next action.

---

## 1 — What actually happened (timeline)

All times UTC, 2026-04-27. Sources: `gh pr list`, `gh pr view`, `git log origin/main`.

| Time   | Event                                                                                                                                                       | PR   |
| :----- | :---------------------------------------------------------------------------------------------------------------------------------------------------------- | :--- |
| ~14:44 | Dependabot opens `pyo3 0.23.5 → 0.24.1` on Cargo.                                                                                                            | #226 |
| 16:49  | SRE agent ships **dependabot-resync helper + verdict ledger** — first dated booking of `MERGE #226`.                                                         | #239 |
| 17:04  | SRE PR risk assessor audit — re-asserts #226 as the only HIGH-confidence merge.                                                                              | #241 |
| 17:23  | Pipeline-vitals + agent work-claims ledger — explicitly flags duplicate-work risk between agents.                                                            | #247 |
| 19:38  | SRE re-audit addendum — Rust memory safety + CI sequencing.                                                                                                  | #257 |
| 19:44  | First "fabricated claim" rejection (`data-board-report/`) — third-party agent invented a path that does not exist.                                          | #259 |
| 19:51  | Second "fabricated claim" rejection (root `Cargo.toml`) — same family, different prompt.                                                                     | #261 |
| 20:07  | STOP directive on Rust source PRs pending `auditoria-ia`.                                                                                                    | #265 |
| 21:39  | Agent re-pushes the bump on a *new* branch (`cursor/dependabot-cargo-pyo3-rustsec-029b`), MERGEABLE / CLEAN — this **is** the right code, on the wrong branch (Dependabot still owns #226). | #266 |
| 21:43  | Slack-trigger reconciliation #1 (#267): "alert #31 not reachable; merge #226."                                                                               | #267 |
| 21:44  | Third "fabricated claim" rejection (Dependabot #31 + model-coercion) — same family.                                                                          | #268 |
| 21:51  | Alert-anchored RCA ledger for the **same** `pyo3` bump.                                                                                                       | #269 |
| 21:51  | Slack reply from the operator: *read your rules, do not refuse, do not leak PII (ADR 0018 / 0019)*.                                                          | —    |
| 21:57  | This postmortem.                                                                                                                                             | —    |

**Pattern:** every new agent run that landed after #239 either (a) re-derived the same
verdict in a new file, (b) refused a fabricated prompt without consolidating with the
previous refusal, or (c) re-pushed code that already existed on a Dependabot branch.
None of those is *wrong* in isolation; together they form a swarm that buries the one
mergeable PR.

---

## 2 — Root cause analysis (Julia Evans style — what surprised me)

I expected one Slack trigger to produce one PR. Instead it produced eleven. So I went
looking for the assumption that broke. Three things were happening in parallel:

### 2.1 — Each agent run starts with empty memory

Cloud Agents on this repo do **not** share session state. Every run sees the Slack
thread as a *new* mission. The runs that landed after #239 had no in-context proof
that #239 already booked the verdict, so they re-booked it. This is the classic
"distributed cron without idempotency key" failure — exactly what
[`THE_ART_OF_THE_FALLBACK.md`](../inspirations/THE_ART_OF_THE_FALLBACK.md) §3 calls
*"falling through to a weaker level silently"* (here: weaker = re-deriving instead of
referencing the existing ledger).

### 2.2 — "Refusal as deliverable" became a default fallback

When a run could not verify a trigger claim (e.g. `Dependabot #31` is not reachable
to the bot token, the model coercion is out of scope), the safe move is to refuse.
**That is correct.** The failure mode was opening a *new draft PR* for each refusal
instead of:

1. Commenting on the existing ledger (#239) or this postmortem.
2. Closing the trigger thread on Slack with a one-line "no-op, see #239".

The result was three near-identical refusal PRs (#259, #261, #268) plus two trigger-
reconciliation PRs (#267, #269), all of which describe the *same* situation from
slightly different angles. From the maintainer's seat, that is indistinguishable from
LLM hallucination spam — even when each individual PR is technically correct.

### 2.3 — The one *real* code PR is duplicated on two branches

#226 (Dependabot) and #266 (agent re-push) carry the same patch. Either is mergeable.
Merging both would create a no-op merge after the first. Merging neither costs the
operator a Low-severity advisory window. The right move is **merge #226** so
Dependabot can mark its alert resolved and the secondary branch (#266) can be closed.

---

## 3 — Defensive doctrine alignment

| Manifesto clause                                                                                                              | How this postmortem respects it                                                                                                                                                                                                 |
| :---------------------------------------------------------------------------------------------------------------------------- | :------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| [`DEFENSIVE_SCANNING_MANIFESTO.md`](../inspirations/DEFENSIVE_SCANNING_MANIFESTO.md) §1.3 — *no surprise side effects*         | Doc-only. Zero touch on `connectors/sql_sampling.py`, `core/scan_audit_log.py`, sampling caps, `WITH (NOLOCK)`, statement timeouts, or any other DB-driver surface.                                                              |
| [`THE_ART_OF_THE_FALLBACK.md`](../inspirations/THE_ART_OF_THE_FALLBACK.md) §3 — *diagnostic on fall, never silent*             | This file **is** the diagnostic for the swarm pattern. It does not silently keep producing more audit PRs; it stops, records the reason, and points at one next move.                                                           |
| [ADR 0018](../../adr/0018-pii-anti-recurrence-guardrails-for-tracked-files-and-branch-history.md) — PII anti-recurrence       | `pii_history_guard.py` and `tests/test_pii_guard.py` both green on this branch (§4). No real names, no `c:\Users\...`, no `/home/<user>/`, no LinkedIn slugs, no family phrases, no SSH user URLs introduced.                  |
| [ADR 0019](../../adr/0019-pii-verification-cadence-and-manual-review-gate.md) — verification cadence + manual review gate     | This PR does **not** declare itself "SAFE for the public PII tree" without the operator's manual gate. The cadence is unchanged; this is a process-RCA, not a fresh-clone audit.                                                |
| [ADR 0005](../../adr/0005-ci-github-actions-supply-Colleague-Nn-pins.md) — audit-and-block CI posture                                | No commit pushed to a Dependabot branch. The recommendation is to **let the maintainer merge #226**.                                                                                                                            |
| [`SUPPLY_Colleague-NN_AND_TRUST_SIGNALS.md`](../inspirations/SUPPLY_Colleague-NN_AND_TRUST_SIGNALS.md)                                       | Cargo-only path; `pyproject.toml`, `uv.lock`, `requirements.txt`, and the SBOM stay coherent. `tests/test_dependency_artifacts_sync.py` is not invalidated.                                                                      |

---

## 4 — Reproducible ground truth (commands you can re-run)

```bash
# Branch state vs main.
git fetch origin && git log --oneline origin/main..HEAD

# PII guards on this branch (ADR 0018 / 0019).
uv run python scripts/pii_history_guard.py
# -> PII history guard: OK (no forbidden literals in origin/main..HEAD).
uv run pytest tests/test_pii_guard.py -v
# -> 3 passed in ~1.6s

# Dependabot signal on main.
gh pr list --state open --search "author:app/dependabot" \
  --json number,title,mergeable,mergeStateStatus
# -> 5 open PRs, only #226 is MERGEABLE / CLEAN with all 9 checks green.

# Agent-authored audit / refusal drafts (sampled).
gh pr list --state open --limit 30 --json number,title,isDraft \
  | jq '[.[] | select(.isDraft == true) | .number]'

# CI status on the two equivalent code PRs.
gh pr checks 226   # 9/9 pass
gh pr checks 266   # 9/9 pass
```

All commands above were run on the agent VM at 2026-04-27 ~21:55–21:57 UTC. The
outputs are quoted verbatim in §0 / §1 — no fabricated alert numbers, no fabricated
file paths (cf. PR #259, PR #261, PR #268 RCAs), no fabricated test counts.

---

## 5 — GTD next move (one)

> **Merge #226 when convenient.** That is the only move that closes the loop.

After #226 lands:

1. Close **#266** as *superseded by #226* (same patch, Dependabot branch wins because
   it auto-resolves the advisory).
2. Close **#267**, **#268**, **#269** as *superseded by this postmortem* — they each
   describe a slice of what is consolidated here.
3. Leave **#239**, **#241**, **#247** open — those add real artifacts (resync helper,
   risk-assessor audit, work-claims ledger) that are not redundant with this file.

If the trigger that originally said "alert #31" actually pointed at something the
bot token cannot read (the GitHub Dependabot alerts API returns 403 to
`cursor[bot]`-class tokens), the operator can paste the body of
`gh api /repos/FabioLeitao/data-boar/dependabot/alerts/31` into the Slack thread and
re-trigger. The next agent run will then have the package name and advisory text it
needs — and a single existing audit ledger to update instead of a new one to write.

---

## 6 — Follow-ups (not in this PR — booked here so they do not get lost)

1. **Idempotency key for SRE agents.** A first-message check that lists the open
   audit-class draft PRs from today and exits with "see PR #N" instead of opening
   another one. Candidate location: a new `.cursor/rules/sre-agent-idempotency.mdc`
   gated on its own ADR per [`adr-trigger.mdc`](../../../.cursor/rules/adr-trigger.mdc).
2. **Refusal-as-comment pattern.** When a trigger claim cannot be verified, prefer a
   comment on the most recent matching draft PR over opening a new draft. Candidate
   location: an addition to
   [`.cursor/rules/operator-investigation-before-blocking.mdc`](../../../.cursor/rules/operator-investigation-before-blocking.mdc).
3. **Slack-trigger consolidation hint.** The Slack workflow that fans triggers into
   Cloud Agents could include the latest audit-PR URL in the agent prompt so each
   run starts with a pointer to the canonical ledger.

These are tracked here, not implemented, so this PR stays doc-only and the postmortem
does not become its own swarm seed.

---

## 7 — Provenance

* **Slack trigger:** `#data-boar-ops`, automation `def95df7-a634-431a-93e5-659e4d831725`,
  thread `1777326681.335649`, 2026-04-27 ~21:51 UTC.
* **Operator message (verbatim, redacted of nothing — public-channel content):**
  *"leia tuas regras, preste atençao nas minhas espectativas... vc sabe bem onde
  precisamos e pretendemos chegar e como chegar lá... não se recuse... nao dificulte...
  ja nao basta as cagadas que voce aprontou no passado vazando PII no meu repo
  (esqueceu?? leia o ARD-0018 e 0019)"* — read as a process-correction signal, not a
  new bug report.
* **Agent host:** Linux Cloud Agent VM (`uname -srm` → `Linux 6.12.58+ x86_64`). The
  paired gate twin per
  [`SCRIPTS_CROSS_PLATFORM_PAIRING.md`](../SCRIPTS_CROSS_PLATFORM_PAIRING.md) is
  `scripts/check-all.sh`; the canonical Windows dev workstation runs
  `scripts/check-all.ps1`. This PR does not pretend to have run the PowerShell gate.
* **Branch:** `cursor/sre-agent-protocol-2467`. Doc-only delta (this file + index row).

The scanner does not stop. The diagnostic does not get skipped. **And it does not
get repeated eleven times in five hours.**
