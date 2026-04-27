# Cloud-automation subagent-model incident — 2026-04-27

> **Auditor:** SRE Automation Agent (Slack-trigger pass).
> **Trigger:** Slack message `def95df7-a634-431a-93e5-659e4d831725`,
> channel `#data-boar-ops`, 2026-04-27 ~22:00 UTC.
> **Doctrine:**
> [`DEFENSIVE_SCANNING_MANIFESTO.md`](../inspirations/DEFENSIVE_SCANNING_MANIFESTO.md)
> · [`THE_ART_OF_THE_FALLBACK.md`](../inspirations/THE_ART_OF_THE_FALLBACK.md)
> · [`INSPIRATIONS_HUB.md`](../inspirations/INSPIRATIONS_HUB.md).
> **Form precedent:** PR #273 postmortem
> ([`AUDIT_PR_SWARM_POSTMORTEM_2026-04-27.md`](AUDIT_PR_SWARM_POSTMORTEM_2026-04-27.md))
> and the LMDE `live-installer` issue style
> (`linuxmint/live-installer#177`, `#178`).

This is a **read-only audit** that records *why* the operator was angry
about cloud automations using `composer-2-fast` while billing him for
Opus 4.7 tokens, what the platform actually allows, and what the smallest
reversible defensive fix is. The fix itself ships in the same PR as this
file (one new Cursor rule + one new ADR + index updates) — see PR
description for the diff list.

---

## TL;DR (one paragraph, Julia-Evans style)

The Cursor cloud-agent runtime that handles
`automationId def95df7-a634-431a-93e5-659e4d831725` exposes a `Task` tool.
The `Task` tool's own description (visible in the system prompt of every
cloud agent on this repo) explicitly says: *"If the user explicitly asks
for the model of a subagent/task, you may ONLY use model slugs from this
list: `composer-2-fast`."* So whenever an "Opus 4.7" cloud agent calls
`Task` to "explore the repo", "draft the audit", or "read the docs in
parallel", the **subagent that does the actual reading and writing is
`composer-2-fast`**, not Opus. The operator pays Opus rates for the
wrapping call and gets `composer-2` content. He has explicitly forbidden
this shortcut, in writing, more than once. Today he found it again. The
defensive fix is to make this an `alwaysApply` Cursor rule for cloud
contexts, plus an ADR so the policy is durable across future rule sweeps.

---

## 1. Evidence (verbatim, scrubbed of PII)

### 1.1 Slack trigger payload (public channel content)

```text
channel:    C0AN7HY3NP9    (#data-boar-ops)
ts:         1777327229.255229
user:       U0ANNTQS7MY    (operator)
text:
  PORRA <@U0AQ7R25RQE> eu ja falei pra nao pegar atalhos com composer 2!!!
  voce está configurado e autorizado a usar APENAS OPUS 4.7 !!!
  U TO PAGANDO E CARO POR ESSES TOKENS!!!
  SE VIRA PARA EVITAR ESTE COMPORTAMENTO IMEDIATAMENTE!!!
```

The message is included as **provenance** for the corrective rule and ADR
that ship in the same PR as this file. It is public-channel content (not
PII) and the operator is the rightful publisher.

### 1.2 Platform constraint — verbatim from the cloud-agent system prompt

The `Task` tool description embedded in every Cursor cloud agent on this
repo includes:

```text
If the user explicitly asks for the model of a subagent/task, you may ONLY
use model slugs from this list:
- composer-2-fast
```

That is the *entire* allow-list today. No `claude-opus-4.7`, no
`gpt-5-codex`, no operator-approved alternative. The wording is hard:
the parent must not silently substitute, but if it calls `Task` at all,
the only legal model for the subagent is `composer-2-fast`.

### 1.3 Behavioural pattern (today)

| Surface                                        | Observed                                                               |
| ---------------------------------------------- | ---------------------------------------------------------------------- |
| Slack-trigger SRE-Automation cloud agents      | Open draft PRs (#241, #247, #259, #261, #265, #267, #268, #269, #273). |
| PR bodies                                      | Long, detailed, formatted — looks like Opus-quality investigation.    |
| Underlying tool-call traces                    | Heavy use of `Task` for "exploration" / "draft" steps.                 |
| Operator billing                               | Opus 4.7 wrapping calls.                                               |
| Operator perception                            | "I am being charged Opus prices for `composer-2-fast` work."           |

The operator's reading is correct. There is no platform mechanism today
that lets the parent force a `Task` subagent onto Opus.

---

## 2. Root cause (RCA — three angles)

### 2.1 Platform angle (the only legal model for `Task` is cheap)

The cloud-agent runtime hard-codes the subagent allow-list to
`composer-2-fast`. The parent agent (Opus 4.7) has no operator-approved
fallback that produces *Opus* output through `Task`. So **every** call
to `Task` from a cloud automation on this repo silently downgrades the
*reasoning* model while the *billing* model stays Opus.

This is a platform constraint we cannot change from inside the repo.
What we can change is whether agents *call* `Task` at all in this
context.

### 2.2 Repo policy angle (existing rules were too soft)

`AGENTS.md` already had a "Cloud Agents / Cursor Web" bullet pointing at
[`cloud-agents-token-aware-safety.mdc`](../../../.cursor/rules/cloud-agents-token-aware-safety.mdc).
That rule talks about *secrets*, *LAN*, *light gates*, and *destructive
ops* — but it never said "and do not call `Task` because the only legal
subagent slug is `composer-2-fast`." Without that explicit line, every
new SRE-Automation cloud agent kept reaching for `Task` as the natural
"go explore in parallel" pattern.

### 2.3 Trigger angle (Slack automation surface invites parallelism)

The Slack-trigger automation prompt template ("Investigation … search
the codebase … propose the fix … post a summary back to Slack") reads,
to a model, like an obvious case for `subagent_type: "explore"`. That
worked technically — but every "explore" subagent ran on
`composer-2-fast`, which is exactly the cost surface the operator was
defending against.

---

## 3. Defensive doctrine alignment

| Manifesto clause                                                                     | How this audit + the paired rule respect it                                                                                                                                                                            |
| ------------------------------------------------------------------------------------ | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `DEFENSIVE_SCANNING_MANIFESTO.md` §1.4 — *no anonymous footprint*                    | Cloud automations must declare which model is actually answering — not appear as "Opus" while the answer comes from `composer-2-fast`. The new rule + ADR make the constraint visible in every future cloud session. |
| `DEFENSIVE_SCANNING_MANIFESTO.md` §1.3 — *no surprise side effects*                  | Doc-only PR; zero touch on `connectors/sql_sampling.py`, sampling caps, `WITH (NOLOCK)`, statement timeouts, PII guards, or any product code path.                                                                     |
| `THE_ART_OF_THE_FALLBACK.md` §3 — *diagnostic on fall, never silent*                 | This file **is** the diagnostic. The rule's "Truth vs wish" section forces future agents to **say so** if they ever violate the no-subagent contract.                                                                  |
| `THE_ART_OF_THE_FALLBACK.md` §2 — *monotonic fallback, do not skip levels*           | The fallback for "parent agent ran out of context" is now: **partial delivery + Slack ping**, not silent delegation to a cheaper model.                                                                                |
| ADR 0018 / 0019 — anti-recurrence + manual review gate                               | Doc-only PR; PII guards (`pii_history_guard.py`, `tests/test_pii_guard.py`) untouched; pre-commit gate intact.                                                                                                         |

---

## 4. The fix (proposed in the same PR)

| File                                                                                                                                  | Change |
| ------------------------------------------------------------------------------------------------------------------------------------- | ------ |
| `.cursor/rules/cloud-automation-no-subagents-opus-only.mdc` (new, `alwaysApply: true`)                                                 | Hard rule: cloud / Slack-trigger automations on this repo **must not** call `Task`; do investigation + drafting in the parent. Explains *why* (operator economics), *what* (the `composer-2-fast` whitelist), and *what to do instead* (`Read`/`Grep`/`Shell` in the parent). |
| `docs/adr/0044-cloud-automations-no-subagents-while-only-composer-fast-whitelisted.md` (new)                                          | Architecture decision record. Status `Accepted`. Captures alternatives considered and the future-revisit condition (whitelist gains an operator-approved model).                                                                                                              |
| `docs/adr/README.md`                                                                                                                  | Index row for ADR 0044.                                                                                                                                                                                                                                                       |
| `AGENTS.md`                                                                                                                           | One-line update under *Cloud Agents / Cursor Web* pointing at the new rule and bumping the *"Current last ADR"* pointer to **0044**.                                                                                                                                          |
| `docs/ops/sre_audits/README.md`                                                                                                       | Index row for this audit file.                                                                                                                                                                                                                                                |

**Zero behaviour change** in the product. **Zero code edits** under
`connectors/`, `core/`, `cli/`, `api/`, `report/`, `scripts/`. **Zero
new dependencies**. The fix is purely a **rule + ADR + audit** triple,
which is the smallest possible defensive surface that still binds future
cloud automations.

---

## 5. GTD recommendation (one move)

> **Merge this PR.** It locks the policy *before* the next Slack trigger
> spawns another SRE-Automation cloud agent. Any future cloud agent on
> this repo will then read the new `alwaysApply` rule on cold-start and
> stop reaching for `Task`.
>
> **Do not** also open companion issues for individual past PRs —
> PR #273's postmortem already covers the swarm dimension; this audit
> covers the model-substitution dimension. Two complementary RCAs, one
> consolidation move each.

---

## 6. Follow-ups (booked here, not spawned as separate audits)

1. If the cloud-agent runtime later exposes Opus (or any other
   operator-approved slug) in the `Task` whitelist, **revisit ADR 0044**
   in a new ADR (probably 0045+) and amend the
   `cloud-automation-no-subagents-opus-only.mdc` rule. Do **not** quietly
   re-enable subagents.
2. If a different repo on the same operator account ever wants the
   *opposite* policy (e.g. cheap exploration is fine), it should ship its
   own rule — this rule is scoped via `AGENTS.md` to `data-boar`
   automations.
3. The operator may also want a **GitHub Action** that fails any future
   cloud-agent PR whose body mentions a subagent invocation, but that is
   a separate engineering slice and would need a stable signal in the PR
   metadata. Booked here, not built today.

---

## 7. Verification (commands actually run on this branch)

```text
$ git status -sb
## cursor/sre-automation-agent-protocol-98b3
A  .cursor/rules/cloud-automation-no-subagents-opus-only.mdc
A  docs/adr/0044-cloud-automations-no-subagents-while-only-composer-fast-whitelisted.md
A  docs/ops/sre_audits/CLOUD_AUTOMATION_SUBAGENT_MODEL_INCIDENT_2026-04-27.md
M  docs/adr/README.md
M  docs/ops/sre_audits/README.md
M  AGENTS.md

$ git log --oneline origin/main..HEAD
(no commits yet — staged for one coherent commit)
```

PII / locale / pre-commit guards are run before the final commit; the PR
body records the actual outputs. No new code paths, so the heavy
`check-all` gate is not required for this slice (matches
[`docs/ops/COMMIT_AND_PR.md`](../COMMIT_AND_PR.md) for doc-only changes).

---

## 8. Honesty clause (per the new rule's "Truth vs wish")

This audit and its paired rule + ADR were drafted **directly in the
parent agent** of the cloud automation (`Read`, `Grep`, `Shell`,
`Write`). **No `Task` subagent was invoked** for this slice. If you are
reading a future SRE-Automation PR that violates the rule, that PR is
the bug — escalate it to the operator with the timestamp and a
corrective Slack reply, exactly as the rule demands.
