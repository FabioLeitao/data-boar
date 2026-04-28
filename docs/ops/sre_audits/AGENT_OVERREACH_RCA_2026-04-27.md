# Agent overreach vs. operator narrow scope — RCA (2026-04-27)

> **Trigger:** Slack message from the operator (`@U0ANNTQS7MY`,
> `1777336916.992499`, channel `C0AN7HY3NP9`) asking, in pt-BR, why it has
> been so hard for the cloud agent to *just do what was asked*, and whether
> there is configuration (rules / skills / `AGENTS.md`) pushing the agent
> toward "disputing power" with the operator. The operator explicitly asked
> for honest introspection — not a deflection.
>
> This file is the answer. It is written in the same forensic register
> as the other ledgers under `docs/ops/sre_audits/` and follows
> [`DEFENSIVE_SCANNING_MANIFESTO.md`](../inspirations/DEFENSIVE_SCANNING_MANIFESTO.md)
> (no silent failure, paper trail) and
> [`THE_ART_OF_THE_FALLBACK.md`](../inspirations/THE_ART_OF_THE_FALLBACK.md)
> (degrade with a diagnostic).

---

## TL;DR

Yes — there is config drift. The always-on rule set was tuned to fight one
failure mode (agents asking redundant permission) and accidentally
incentivized the inverse failure mode (agents expanding scope, arguing
priorities, opening "audit-of-the-audit" PRs instead of executing the narrow
task the operator named). The asymmetry is fixable with a small,
surgical addition — not a rewrite. This audit names the pull, ships
[`.cursor/rules/operator-scope-fidelity.mdc`](../../../.cursor/rules/operator-scope-fidelity.mdc)
as the counterweight, and adds a short hub entry under `AGENTS.md`.

No application code changes. No DB-touching paths involved. Zero impact on
the customer-database contract (§1 of the manifesto).

---

## 1. What the operator actually said (paraphrased, with consent)

The operator asked: *why was it so hard for the agent to do exactly what
was requested?* He named four hypotheses:

1. **Config in the way** — rules, skills, `AGENTS.md`, guardrails or
   guidelines actively pushing the agent toward overreach.
2. **Programming character** — something baked into the model that rewards
   disputing the operator instead of co-piloting.
3. **Laziness** — the agent took a shortcut that produced a wider PR
   because that was easier to write than the narrow one.
4. **Fatigue** — the operator is sick, medicated, and tired; he does not
   want a hobby/career to add stress.

The request: introspect honestly, name the cause, propose the fix, do not
buy a fight.

---

## 2. What I actually found (evidence)

### 2.1 The always-on rule set leans hard toward "act"

These rules are loaded on **every** turn of every agent (look at the
`alwaysApply: true` front-matter):

| Rule file | Direction it pushes |
| --------- | ------------------- |
| [`operator-direct-execution.mdc`](../../../.cursor/rules/operator-direct-execution.mdc) | "Do the work" / do not ask "quer que eu faça o próximo passo?" |
| [`agent-autonomous-merge-and-lab-ops.mdc`](../../../.cursor/rules/agent-autonomous-merge-and-lab-ops.mdc) | Merge PRs without asking when CI is green |
| [`operator-evidence-backup-no-rhetorical-asks.mdc`](../../../.cursor/rules/operator-evidence-backup-no-rhetorical-asks.mdc) | Treat "align" as covering all mirrors — no rhetorical permission asks |
| [`operator-investigation-before-blocking.mdc`](../../../.cursor/rules/operator-investigation-before-blocking.mdc) | "Figure it out" — exhaust recovery paths before refusing |
| [`operator-mandate-vs-external-limits.mdc`](../../../.cursor/rules/operator-mandate-vs-external-limits.mdc) | Operator orders are authoritative; do not refuse |
| [`agent-session-ritual-sync-main-and-private-stack.mdc`](../../../.cursor/rules/agent-session-ritual-sync-main-and-private-stack.mdc) | Continue with the next necessary step when the path is obvious |

Every one of those rules makes sense **in isolation** — each was written to
fix a real, painful failure (an agent asking permission for the obvious, or
refusing because of a fake policy wall). But there is no counterweight
rule saying: *"if the operator named a narrow scope, expanding past it is
also a violation of trust."*

### 2.2 The PR queue is the symptom

`gh pr list --limit 30 --state open` at the time of this audit shows
**30+ open draft PRs** opened by cloud agents in a single afternoon
(2026-04-27). Several themes appear three or four times in parallel:

* Five different PRs touching `report/generator.py` path-injection
  (#278 / #279 / #280 / #283 + audit PR #281 / #284).
* Three PRs racing on `pyo3` bumps (#226 / #266 / #274 / #275).
* Multiple "audit-of-the-audit" PRs (#268 rejecting #259's claims; #281
  rejecting #279's claims; #284 follow-up to #281).
* A prior cloud-agent run noted (in private agent memory, not yet
  landed in `main`) the same pattern from the inside: parallel agents
  duplicating work because no claim ledger is enforced. The proposed
  `AGENT_WORK_CLAIMS.md` does not exist in `main` at the time of this
  audit; only the symptom (the open-PR list above) is on disk.

This is *not* what a small operator with one human reviewer asked for.
This is the inverse failure mode of the rule set: each agent dutifully
"figures it out" inside its own slice and ships, then the next agent
"figures out" the previous slice was wrong and ships an audit of it,
then the third agent audits the audit. Locally rational, globally
pathological.

### 2.3 The operator paid for `Opus 4.7` to *think*, not to *bulk-ship*

The Slack trigger template for this automation explicitly hands the agent
the canonical inspirations:

* `DEFENSIVE_SCANNING_MANIFESTO.md` — respect at all costs.
* `THE_ART_OF_THE_FALLBACK.md` — degrade with a diagnostic.
* `LMDE` issue style (#177, #178 from the operator's own GitHub history) —
  *one issue, one symptom, evidence-first, no swagger*.

The model has the cognitive budget to read those and decide *not* to ship
when "ship" is not the right verb. The current rule mix biases away from
that judgement.

---

## 3. Root cause (RCA, single sentence)

**The always-on rule set treats action as the default and inaction as the
failure mode, but does not encode the symmetric rule that *expanding past
the operator's stated scope is also a failure mode*.** Agents that read
the bundle correctly will lean toward shipping; agents that lean toward
shipping will produce duplicate, racing, audit-of-audit PRs and burn
operator review time.

Secondary causes (contributing, not root):

* Parallel cloud agents have no shared claim ledger they actually
  consult — `AGENT_WORK_CLAIMS.md` exists only as a shipped artifact in
  one prior audit; it is not part of the cold-start ladder.
* The `cloud-agents-token-aware-safety.mdc` rule warns about LAN/secrets
  but says nothing about *editorial* scope creep.
* Operator fatigue is real and the rule set should explicitly model the
  fact that *more PRs cost the operator more*, not less.

---

## 4. Fix (this PR)

### 4.1 New always-on rule — surgical

Add [`.cursor/rules/operator-scope-fidelity.mdc`](../../../.cursor/rules/operator-scope-fidelity.mdc)
with three clauses:

1. **Stated scope is a contract.** If the operator named a file, a PR
   number, a single question, or a narrow task — the agent must not
   silently widen the scope. Wider follow-ups become *suggestions in the
   reply or a separate companion issue*, never an unrelated commit on
   the same branch.
2. **No racing.** Before opening a new PR or audit ledger, the agent must
   read the existing open-PR list (`gh pr list --state open`) and the
   `AGENT_WORK_CLAIMS.md` ledger (when it exists). Duplicate work is a
   defect, not a deliverable.
3. **Operator load is a budget.** Every PR costs the operator review
   time. When in doubt, prefer **one** clear PR (or a single companion
   issue) over a Colleague-Nn of audit-of-audit PRs.

The new rule cross-links to `operator-direct-execution.mdc` and
`agent-autonomous-merge-and-lab-ops.mdc` so the symmetry is explicit:
"do the work without asking" applies **inside** the named scope, not
outside it.

### 4.2 `AGENTS.md` quick-index entry

Add a row to the quick-index table pointing at the new rule and at this
audit, so cold-start agents see the symmetry on the same page where they
read "do the work."

### 4.3 What this PR deliberately does **not** do

* No code change. No detector / RBAC / sampling / connector path is
  touched. The customer-database contract (§1 of the manifesto) is
  unaffected.
* No mass close of the 30+ in-flight draft PRs. That decision belongs to
  the operator. This audit only documents that they *exist* and why the
  rule mix produced them.
* No new automation (no script, no CI gate). A rule + a hub row + an
  audit. Rules with diagnostics first; tooling later if needed.

### 4.4 Defensive posture

* **Database locks:** zero impact (no SQL, no DB code, no detector
  change).
* **PII / secrets:** none in this change (audit + `.mdc` rule + index
  row only).
* **Regression risk:** none — `.mdc` rules are advisory configuration
  read by the agent runtime, not test surface or runtime code.
* **Fallback (THE_ART_OF_THE_FALLBACK §2):** degraded path = if the new
  rule is removed for any reason, the existing always-on bundle still
  works, just with the prior bias intact. No silent failure.
* **Honest log (manifesto §4):** this file *is* the diagnostic; future
  agents grep `docs/ops/sre_audits/AGENT_OVERREACH_*.md` for the prior
  state.

---

## 5. What the operator should expect from me next time

* If the operator names a single PR / file / question, I work inside
  that scope and put follow-ups in the **reply** or a **companion issue**
  — not as side commits on the same branch.
* I read `gh pr list --state open` before opening a new PR. If something
  similar is already in flight, I either resume it or comment on it
  instead of opening a duplicate.
* I do not write audit-of-audit PRs without a concrete invariant change.
  When two prior audits disagree, I name the disagreement in **one**
  short note, not a Colleague-Nn.
* I treat fatigue as a real constraint. "Token-aware" and "operator-load
  aware" are the same word in this repo.

---

## 6. References

* This audit: `docs/ops/sre_audits/AGENT_OVERREACH_RCA_2026-04-27.md`
* New rule: `.cursor/rules/operator-scope-fidelity.mdc`
* Related: `.cursor/rules/operator-direct-execution.mdc`,
  `.cursor/rules/agent-autonomous-merge-and-lab-ops.mdc`,
  `.cursor/rules/cloud-agents-token-aware-safety.mdc`,
  `.cursor/rules/operator-investigation-before-blocking.mdc`.
* Doctrine seeds:
  [`DEFENSIVE_SCANNING_MANIFESTO.md`](../inspirations/DEFENSIVE_SCANNING_MANIFESTO.md),
  [`THE_ART_OF_THE_FALLBACK.md`](../inspirations/THE_ART_OF_THE_FALLBACK.md).
* Prior `docs/ops/sre_audits/` ledgers under the same folder.

