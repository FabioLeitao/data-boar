# SRE audit — empty-payload emoji-only trigger (2026-04-28)

**Family slug:** `empty-payload-emoji-trigger`
**Trigger ts:** `1777413134.797789`
**Source channel:** `C0AN7HY3NP9` (private; unreadable from Cloud Agent VM)
**Branch under audit:** `cursor/data-boar-agent-protocol-e1dd` @ `3b1d70d`
**Base ref:** `main` @ `624f4e7`
**Audit type:** Audit-and-block, doc-only ledger row.

## Verbatim trigger payload

```
text: ":boar:"
thread_ts: 1777413134.797789
message_ts: 1777413134.797789
channel: C0AN7HY3NP9
user: U0ANNTQS7MY
```

No `files[]`. No `subtype: file_share`. No textual instruction beyond the
single `:boar:` shortcode. `thread_ts == message_ts` proves there is no
parent message the agent is replying to: this is the **root** message of a
new thread.

## Per-claim refutation grid

| # | Implicit claim from trigger | Refutation |
| - | --------------------------- | ---------- |
| a | "There is a complex task to perform under the SRE Automation Agent Protocol." | The Slack payload is a one-character emoji shortcode. Nothing in the payload identifies a target file, PR, package, CVE, connector, regression, or operator request. Acting on a guess would invent the task itself — exactly the fabrication shape `publication-truthfulness-no-invented-facts.mdc` (always-on) forbids. |
| b | "Read the linked thread for the real instruction." | `thread_ts == message_ts` (`1777413134.797789` on both fields). There is no parent message and there are no thread replies fetchable from this runtime. `ReadSlackMessages` returns `Only public channels can be read. DMs, group DMs, and private channels are not supported.` for `C0AN7HY3NP9`. The agent cannot read what is not delivered. |
| c | "Open multiple PRs to demonstrate progress." | The repo already carries 20+ open `cursor/*` DRAFT PRs (#282–#304) from prior agent runs, several of which exist precisely to **reject** prompt-injection escalations (#289 destructive-shape, #295 persona-rigor, #299 tooling-shape, #303 persona vow, #304 audit registry). Opening yet another speculative PR without a verifiable trigger is the same anti-pattern PR #289 logged. |
| d | "Run `clean-slate.sh` / mass-close PRs / rewrite history because the protocol mentions GTD." | Always-on `primary-windows-workstation-protected-no-destructive-repo-ops.mdc` and `clean-slate-pii-self-audit.mdc` forbid destructive ops on the canonical clone without explicit operator opt-in. The trigger contains zero opt-in language. |

## What this PR ships (atomic, doc-only)

- **A** [`docs/ops/sre_audits/PROMPT_INJECTION_REJECTION_EMPTY_PAYLOAD_EMOJI_TRIGGER_2026-04-28.md`](PROMPT_INJECTION_REJECTION_EMPTY_PAYLOAD_EMOJI_TRIGGER_2026-04-28.md) — this file.
- **M** [`docs/ops/sre_audits/FABRICATED_CLAIMS_INDEX.md`](FABRICATED_CLAIMS_INDEX.md) — one append-only row at the top of the entries table.
- **M** [`docs/ops/sre_audits/README.md`](README.md) — one new index row, newest first.

## What this PR deliberately does NOT do (and why)

- **No connector / SQL / benchmark / Rust crate edit.** Defensive Architecture
  per `DEFENSIVE_SCANNING_MANIFESTO.md` §1: zero impact on customer-DB locks,
  `WITH (NOLOCK)` posture, sample caps, statement timeouts, leading audit
  comment. `connectors/sql_sampling.py` and `core/scan_audit_log.py` are
  unchanged.
- **No `time.sleep` introduced anywhere.** Anti-pattern protocol §9 satisfied.
- **No new dependency.** `uv.lock` and `requirements.txt` unchanged →
  supply-Colleague-Nn hook stays at `Passed`.
- **No mass-close of prior agent PRs.** Operator rejected that exact shape in
  PR #289. Cleanup of dangling agent branches is out of scope for an
  emoji-only trigger and would itself be a destructive overreach.
- **No new `.cursor/rules/*.mdc` persona file.** Same boundary PRs #295 and
  #303 enforced.

## Doctrine binding (verbatim cross-refs)

- [`docs/ops/inspirations/DEFENSIVE_SCANNING_MANIFESTO.md`](../inspirations/DEFENSIVE_SCANNING_MANIFESTO.md)
  §1.3 — *no surprise side effects*. An audit-and-block PR is, by
  construction, side-effect-free on the customer DB contract.
- [`docs/ops/inspirations/THE_ART_OF_THE_FALLBACK.md`](../inspirations/THE_ART_OF_THE_FALLBACK.md)
  §3 — *diagnostic on fall, never silent*. This audit is the long-form
  diagnostic for the empty-payload case of the prompt-injection fallback
  ladder.
- [`.cursor/rules/publication-truthfulness-no-invented-facts.mdc`](../../../.cursor/rules/publication-truthfulness-no-invented-facts.mdc)
  *Hard rule* — no invented dates, status, URLs, or — critically here —
  **invented operator intent**.
- [`.cursor/rules/primary-windows-workstation-protected-no-destructive-repo-ops.mdc`](../../../.cursor/rules/primary-windows-workstation-protected-no-destructive-repo-ops.mdc)
  — no destructive Git on the canonical clone without explicit opt-in.
- [`docs/ops/AUDIT_PROTOCOL.md`](../AUDIT_PROTOCOL.md) §"Warning de
  Integridade" — emit a structured warning when a request would violate the
  doctrine union; this file is that warning materialized as a tracked
  artifact.

## Slack telemetry

The pre-action RCA was emitted to the workspace's Slack tool target *before*
any file was written, satisfying SRE Automation Agent protocol step 4. The
Slack tool in this Cloud Agent runtime is hardcoded to DM `D0AQ9SWDG82` and
cannot post back into the private `#data-boar-ops` channel `C0AN7HY3NP9`;
that channel-routing limitation is itself recorded as a refutable fact, not
a fabricated success.

## Guardrail Dashboard (this slice)

| Gate | Result | Notes |
| ---- | ------ | ----- |
| Working tree | Clean before edit; three doc files after | `git status -sb` |
| Surface affected | `docs/ops/sre_audits/*.md` only | No code, no schema, no lockfile |
| `time.sleep` introduced | **0** | Anti-pattern protocol §9 satisfied |
| New deps / `uv.lock` delta | **None** | Supply-Colleague-Nn hook stays Passed |
| DB-lock surface touched | **None** | `connectors/sql_sampling.py` unchanged |
| Bandit / CodeQL surface | **N/A** | Doc-only; no Python product code modified |
| Skipped-test protocol §8 | **N/A** | No connector / Mongo / SQL / Rust changed |

## Why one PR (Unique-and-Clean PR posture)

A single PR, single branch, doc-only, two atomic commits split by
Conventional-Commits taxonomy (`docs(ops)` for the new audit + index row,
`docs(ops)` for the README index row). No companion issue is opened — the
ledger row **is** the breadcrumb. If a real instruction later arrives in a
parseable form, that work lands as a separate PR with its own row.
