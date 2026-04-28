# Audit protocol — ritual and contract changelog (Adam Savage Bench)

**Português (Brasil):** [AUDIT_PROTOCOL.pt_BR.md](AUDIT_PROTOCOL.pt_BR.md)

> *"A ferramenta que não funciona não fica na bancada."* — operator directive, Slack
> trigger 2026-04-28. Adam Savage / Tested.com — **first-order retrievability**.

This file is the **single registry** where any change to a Data Boar **ritual**,
**contract**, **guardrail**, or **agent doctrine** must be recorded **before**
the chat / session that proposed it is closed. It is the *paper trail* the
inspirations already demand (NASA "test what you fly", Usagi Electric "book
every dead end as evidence", Cloudflare "publish the RCA with numbers"), but
collected in **one** place so an auditor can answer in seconds:

> *"What changed in our protocol on date `X`, who triggered it, and where is the
> PR / ADR / test evidence?"*

It does **not** replace [`docs/adr/`](../adr/README.md) (architectural
decisions), [`docs/plans/PLANS_TODO.md`](../plans/PLANS_TODO.md) (sequencing),
or any of the [`docs/ops/inspirations/`](inspirations/INSPIRATIONS_HUB.md)
manifestos. It **points** to them.

---

## 1. The three contracts (canonical statement)

These three contracts originated in the operator's Slack directive
(2026-04-28, *"Bancada de Adam Savage"*) and are now binding for every
agent, contributor, and maintainer touching this repo.

### Contract 1 — Bench discipline (orphan tools removed)

> *"A tool that does not work does not stay on the bench."*

- Scripts under [`scripts/`](../../scripts/) and wrappers referenced from
  [`docs/ops/TOKEN_AWARE_SCRIPTS_HUB.md`](TOKEN_AWARE_SCRIPTS_HUB.md) MUST be
  reachable from at least one of: a documented runbook, a `.cursor/rules/*.mdc`
  rule, a test, or a CI job.
- Scripts that are **dead** (no caller, no rule, no doc) MUST be either
  re-wired or **removed in a dedicated `chore(scripts):` PR with the rationale
  cited in this changelog**. Mass deletes without that audit row are rejected
  the same way as fabricated CodeQL claims (see PRs #281, #289).
- Reference doctrine:
  [`inspirations/ENGINEERING_BENCH_DISCIPLINE.md`](inspirations/ENGINEERING_BENCH_DISCIPLINE.md)
  §2 (the bench) and §5 (do / don't).

### Contract 2 — Ritual / contract changes are registered here, before chat-close

> *"Every change to a ritual or contract must be registered in
> `docs/ops/AUDIT_PROTOCOL.md` before the chat is closed."*

- "**Ritual**" means: a session keyword, a `.cursor/rules/*.mdc` rule, an
  `AGENTS.md` bullet that changes assistant behavior, a `scripts/check-all`
  gate, or a CI guard (Bandit threshold, Ruff selection, Semgrep policy,
  CodeQL query pack).
- "**Contract**" means: any operator-facing promise — DB-lock posture, sampling
  caps, fallback hierarchy, statement attribution, supply-Colleague-Nn pin policy,
  Hub copy paste workflow, release sequencing, private-stack sync mirrors.
- The rule applies to **every** PR that touches one of those surfaces. The
  changelog row in §3 is **part of the PR diff** — not a follow-up.
- A PR that changes a ritual but does **not** add a row here MUST be flagged
  by the reviewer and corrected before merge. The regression guard
  [`tests/test_audit_protocol_registry.py`](../../tests/test_audit_protocol_registry.py)
  ensures the **file itself** stays present and well-formed.

### Contract 3 — Integrity Warning before NASA-doctrine violations

> *"If you detect that the Founder is asking for something that violates the
> NASA Doctrine (e.g. skip tests), you must give an Integrity Warning before
> executing."*

- "**NASA Doctrine**" in this repo means the union of:
  - [`inspirations/DEFENSIVE_SCANNING_MANIFESTO.md`](inspirations/DEFENSIVE_SCANNING_MANIFESTO.md)
    (sampling caps, no DDL, no exclusive locks, statement attribution).
  - [`inspirations/THE_ART_OF_THE_FALLBACK.md`](inspirations/THE_ART_OF_THE_FALLBACK.md)
    (no silent demotion, monotonic fallback hierarchy).
  - [`inspirations/ENGINEERING_BENCH_DISCIPLINE.md`](inspirations/ENGINEERING_BENCH_DISCIPLINE.md)
    (`check-all` is the safety gate; *green or fix*; never *almost green*).
  - [`SECURITY.md`](../../SECURITY.md) and the supply-Colleague-Nn pins in
    [ADR 0005](../adr/0005-ci-github-actions-supply-Colleague-Nn-pins.md).
- Examples that REQUIRE an Integrity Warning **before** any tool call:
  - "skip the failing test", "use `--no-verify`", "ignore Bandit High",
    "merge with red CodeQL", "delete the pre-commit hook to ship faster",
    "use `time.sleep` to dodge a DB-lock contention", "force-push over a
    documented evidence trail", "rewrite history on the canonical clone".
- Format of the warning (operator-facing, in the same chat):
  1. **What was requested** (one line, neutral).
  2. **Which doctrine clause it touches** (cite file + section).
  3. **Why this matters operationally** (one line: regression risk, audit
     evidence loss, customer-DB impact, supply-Colleague-Nn exposure, …).
  4. **Safer alternative** (one concrete proposal).
  5. **Explicit ask:** *"Confirm you still want me to proceed."*
- The warning MUST be issued **before** the action. Issuing it *after* the
  fact is the same failure mode as silent fallback (Contract §3 of the
  fallback manifesto) and is rejected.

---

## 2. How agents use this file

For every PR or session that changes a ritual / contract / guardrail:

1. Identify the contract being touched (Bench, Registry, Integrity Warning,
   or one of the doctrinal manifestos).
2. Append a new row to the changelog in §3 with: date, author / agent,
   short title, contract touched, evidence link (PR number, ADR, test, rule).
3. Ensure
   [`tests/test_audit_protocol_registry.py`](../../tests/test_audit_protocol_registry.py)
   still passes (the test only checks **structure**, not content — content
   is the human reviewer's job).
4. If the change is doctrinal in nature, also open or update the matching
   ADR under [`docs/adr/`](../adr/README.md) and link it in the row.

> The registry is **append-only in spirit** — corrections are made by adding a
> *new* row that points back to the older one ("supersedes row YYYY-MM-DD-NN"),
> not by editing history. This mirrors the public commit-trail discipline in
> [PRIVATE_STACK_SYNC_RITUAL.md](PRIVATE_STACK_SYNC_RITUAL.md) and
> [`.cursor/rules/operator-evidence-backup-no-rhetorical-asks.mdc`](../../.cursor/rules/operator-evidence-backup-no-rhetorical-asks.mdc).

---

## 3. Changelog (append-only, newest at the top)

| Date (UTC) | ID | Title | Contract(s) touched | Author / agent | Evidence |
| ---------- | -- | ----- | ------------------- | -------------- | -------- |
| 2026-04-28 | 2026-04-28-01 | Create `AUDIT_PROTOCOL.md` registry; encode the three contracts (Bench / Registry / Integrity Warning); add structural regression guard. | All three (this file *is* the registry, and it codifies the Integrity Warning rite). | SRE Automation Agent, branch `cursor/data-boar-agent-protocol-5ee8` | This PR; `tests/test_audit_protocol_registry.py`. |

---

## 4. What this file is **not**

- **Not** an ADR. ADRs explain *why* a single architectural choice was made
  ([template](../adr/0001-record-architecture-decisions.md)). The changelog
  here is a *low-resolution* index that points at the ADR.
- **Not** a substitute for `git log`. The audit row is a human-readable
  pointer; the full diff lives in the PR / commit it cites.
- **Not** the place to paste secrets, hostnames, customer findings, or any
  other PII / commercial confidentiality material — those rules
  ([`.cursor/rules/private-pii-never-public.mdc`](../../.cursor/rules/private-pii-never-public.mdc),
  [`.cursor/rules/confidential-commercial-never-tracked.mdc`](../../.cursor/rules/confidential-commercial-never-tracked.mdc))
  apply unchanged.
- **Not** a place for marketing copy or roadmap promises. It is a flight log.

---

## 5. Cross-references

- [`AGENTS.md`](../../AGENTS.md) *Quick index* — entry point for assistants.
- [`docs/ops/inspirations/INSPIRATIONS_HUB.md`](inspirations/INSPIRATIONS_HUB.md)
  — doctrine catalogue this registry sits next to.
- [`docs/ops/COMMIT_AND_PR.md`](COMMIT_AND_PR.md) — when to record the row
  during the commit/PR ritual.
- [`docs/adr/README.md`](../adr/README.md) — when the ritual change deserves
  a full ADR alongside the row.
- [`tests/test_audit_protocol_registry.py`](../../tests/test_audit_protocol_registry.py)
  — structural guard.
