# SRE branch-hygiene RCA — `git branch -r` screen-bloat (2026-04-28)

> **Trigger:** Slack `#data-boar-ops`, message `ts 1777370978.136399`
> (~10:09 UTC, 2026-04-28). Operator note: the prior `prune` helped, but
> `git branch -r` still does not "fit on one screen"; ask was to delete
> `cursor/sre-*` branches that are *integradas ou abandonadas*, with the
> explicit rule **"se não tem PR aberto, não tem por que ter branch no
> origin"** and **"se não for sidequest investigativa óbvia progredindo,
> não tem por que ter dangling branch"**.
> **Auditor:** SRE Automation Agent (Cloud Agent automation
> `def95df7-a634-431a-93e5-659e4d831725`).
> **Doctrine:**
> [`DEFENSIVE_SCANNING_MANIFESTO.md`](../inspirations/DEFENSIVE_SCANNING_MANIFESTO.md)
> §1.3, [`THE_ART_OF_THE_FALLBACK.md`](../inspirations/THE_ART_OF_THE_FALLBACK.md)
> §3, `AGENTS.md` *Risk posture*.

This is an **RCA + workflow PR**, not a fabrication rejection. The
operator's rule is sound and worth encoding; the work was to (a) measure
the actual orphan set against the literal qualifiers and (b) ship a
reusable, read-only helper so the next person can answer the same
question in one command.

---

## TL;DR — outcome

After `git fetch --prune origin` at `2026-04-28T10:19Z` (base `main` @
`624f4e7`):

```text
total remote refs                          : 41
remote refs backed by an OPEN PR (gh)      : 40 of 41
remote refs in keep-list (main, …)         : 1
remote refs that are TRULY orphan (no PR)  : 1
   - fix-rust-ci-coverage-9061 (last commit 2026-04-27 17:24 -03,
                                ahead=6, behind=2)
```

A second orphan, `cursor/sre-agent-protocol-370e`, existed five minutes
earlier but was harvested by a parallel `git fetch --prune origin` while
this audit was preparing — see §3.

**What this PR ships (workflow + docs only — no behavior change):**

1. `scripts/git-list-remote-orphan-branches.sh` (+ `.ps1` twin per
   [`SCRIPTS_CROSS_PLATFORM_PAIRING.md`](../SCRIPTS_CROSS_PLATFORM_PAIRING.md))
   — read-only lister that answers "which remote branches have no open
   PR right now?" and prints `git push origin --delete <branch>` lines
   the operator can copy after a final review. **It never deletes
   anything itself.**
2. New §3.1 in [`BRANCH_AND_DOCKER_CLEANUP.md`](../BRANCH_AND_DOCKER_CLEANUP.md)
   pointing at the helper and reaffirming the open-PR rule.
3. This audit (dated, in `docs/ops/sre_audits/`) so the *real*
   screen-bloat RCA — the open-PR backlog, not orphan branches — is on
   record next to PR #273 ("audit-PR swarm vs. one mergeable fix").

**What this PR explicitly does *not* do:**

- It does **not** run `git push origin --delete` against any branch
  that backs an open PR (40 branches today). Deleting the head ref of an
  open PR auto-closes the PR; PRs #268 / #279 / #281 / #284 / #289 *are*
  the audit paper trail this folder exists to preserve.
- It does **not** run `git push origin --delete` against
  `fix-rust-ci-coverage-9061` either — the operator's rule says "se não
  for sidequest investigativa óbvia progredindo, não tem por que ter
  dangling branch", but that branch is 6 commits ahead of `main` and
  related to the live Rust-CI work in PRs #255 / #256 / #257 / #260 /
  #263. That is a *human* call, not a script call. The lister surfaces
  the row and waits.
- It does **not** modify `report/generator.py`, connectors, sampling
  code, or any product behavior. **Zero impact on database locks** per
  `DEFENSIVE_SCANNING_MANIFESTO.md` §1.3.

---

## 1. Methodology (what I actually did)

In SRE / NASA SEL style: collect evidence first, classify, *then* act.
Per [`THE_ART_OF_THE_FALLBACK.md`](../inspirations/THE_ART_OF_THE_FALLBACK.md)
§2 the strongest signal wins, so the helper composes only trusted
parser-grade signals — not regex guesses about what looks "old".

```bash
# 1. Refresh remote refs
git fetch --prune origin

# 2. Single source of truth for "is this branch backed by an OPEN PR?"
gh pr list --state open --limit 500 --json headRefName \
    -q '.[].headRefName' | sort -u > /tmp/open_pr_branches.txt

# 3. All remote branches (skip the HEAD pointer + the literal 'origin' token)
git for-each-ref --format='%(refname:short)' refs/remotes/origin \
    | sed 's|^origin/||' \
    | grep -Ev '^(HEAD|origin)$' \
    | sort -u > /tmp/all_remote.txt

# 4. Set difference == orphan candidates (no open PR, not in keep-list)
comm -23 /tmp/all_remote.txt /tmp/open_pr_branches.txt \
    | grep -Ev '^(main|auditoria-ia|HEAD|chore/.*release.*|chore/.*beta.*)$'
```

Output at `2026-04-28T10:19Z` (base `main` @ `624f4e7`):

```text
fix-rust-ci-coverage-9061
```

The lister script wraps exactly this pipeline.

---

## 2. Findings — per Slack qualifier

| Slack qualifier | Verifiable on `main` @ `624f4e7` (2026-04-28T10:19Z) | Outcome |
| :-- | :-- | :-- |
| "Delete `cursor/sre-*` que **já foram integradas**." | `git rev-list --count origin/main..origin/cursor/sre-*` is non-zero for **all 40** `cursor/sre-*` refs — none are integrated yet (they all back open PRs awaiting merge or close). | **0 of 40 match.** |
| "Delete `cursor/sre-*` que **foram abandonadas**." | "Abandoned" requires no live PR. `gh pr list --state open --json headRefName` returns a head ref for **all 40** `cursor/sre-*` branches (PRs #235–#289). | **0 of 40 match.** |
| "Se não tem PR aberto, não tem por que ter branch no origin." | The set difference (remote branches) ∖ (open-PR head refs) ∖ (keep-list) yields exactly `{fix-rust-ci-coverage-9061}` after the parallel prune. The lister implements this rule end-to-end. | **Encoded as the new helper.** |
| "Se não for sidequest investigativa óbvia progredindo, não tem por que ter dangling branch." | `fix-rust-ci-coverage-9061`: ahead=6, behind=2, last commit 2026-04-27 17:24 -03, no open PR. *Looks* like an abandoned Rust-CI sidequest related to PRs #255/#256/#260/#263, but classifying "óbvia progredindo" vs "abandoned" is a human read, not a script read. | **Surfaced for human review.** |
| "Quero ver esse `git branch -r` caber em uma tela só." | The screen-fit goal cannot be achieved by deleting the 1–2 orphans alone. The dominant term in `git branch -r` is the **40 open `cursor/sre-*` PRs**. Pulling that down requires merging or closing PRs — the lever PR #273 already analyzes ("audit-PR swarm vs. one mergeable fix"). | **Documented, not actioned.** |

---

## 3. Why the second orphan disappeared mid-audit

While preparing this PR, a parallel `git fetch --prune origin` (operator
or other automation) deleted `origin/cursor/sre-agent-protocol-370e`
between two reads of the lister. This is **expected** and is *itself*
the empirical answer to the screen-bloat ask: the prune lever already
works; there is simply nothing else for it to harvest right now. Per
[`THE_ART_OF_THE_FALLBACK.md`](../inspirations/THE_ART_OF_THE_FALLBACK.md)
§3, the diagnostic is: *prune did its job, the residue is the open-PR
fleet, not orphans*.

---

## 4. Defensive Architecture posture

Per [`DEFENSIVE_SCANNING_MANIFESTO.md`](../inspirations/DEFENSIVE_SCANNING_MANIFESTO.md)
§1.3 (*no surprise side effects*) the lister is **read-only by design**:
no `git push --delete`, no `git branch -D`, no `gh pr close`. The same
rule that keeps Data Boar from issuing schema mutations against a
customer database keeps this helper from mutating the GitHub state
surface on a Cloud-Agent VM.

Per [`THE_ART_OF_THE_FALLBACK.md`](../inspirations/THE_ART_OF_THE_FALLBACK.md)
§2 (monotonic ladder) the lister composes only **trusted parser-grade
signals**:

1. `git fetch --prune origin` — refresh the source of truth.
2. `gh pr list --state open --json headRefName` — single source of
   truth for "is this branch backed by an open PR?"
3. `git for-each-ref refs/remotes/origin` — single source of truth for
   "what branches even exist on the remote?"
4. **Set difference** — the only "logic" the helper applies. No regex
   guessing of what looks "old".

Zero impact on database locks (no DB code touched).
Zero behavior change to the report pipeline.
Zero PRs closed, zero branches deleted by this PR.

---

## 5. What lands

| Path | Class | Rationale |
| ---- | ----- | --------- |
| `scripts/git-list-remote-orphan-branches.sh` | workflow | Read-only lister: prints orphan branches (no open PR, not in keep-list) plus suggested `git push origin --delete` lines for the operator to copy. Never deletes anything itself. |
| `scripts/git-list-remote-orphan-branches.ps1` | workflow | Cross-platform twin per [`SCRIPTS_CROSS_PLATFORM_PAIRING.md`](../SCRIPTS_CROSS_PLATFORM_PAIRING.md). ASCII-only per `pre-commit-ruff.mdc` PowerShell rule. |
| `docs/ops/BRANCH_AND_DOCKER_CLEANUP.md` | docs | Adds §3.1 — "Find branches with no open PR" — pointing at the new helper and reaffirming the open-PR rule. |
| `docs/ops/sre_audits/BRANCH_HYGIENE_RCA_2026-04-28.md` | docs | This audit. |
| `docs/ops/sre_audits/README.md` | docs | Index sync. |

---

## 6. Form (LMDE-issue-style — Julia Evans style RCA)

Same precedent as PRs #259 / #261 / #268 / #281 / #284 / #289
([`linuxmint/live-installer#177`](https://github.com/linuxmint/live-installer/issues/177)
/ [`#178`](https://github.com/linuxmint/live-installer/issues/178)):

- **What was asked:** Delete `cursor/sre-*` branches *integradas ou
  abandonadas*; obey the rule "no open PR → no branch on origin" and
  "no dangling branch unless it is an obviously-progressing
  investigative sidequest".
- **What I checked first (not last):** `gh pr list --state open --json
  headRefName` against `git for-each-ref refs/remotes/origin`. Every
  `cursor/sre-*` branch backs a live OPEN PR.
- **What is actually orphan today:** `fix-rust-ci-coverage-9061`
  (1 branch). One other (`cursor/sre-agent-protocol-370e`) was harvested
  by a parallel `--prune` mid-audit.
- **Why I did not just delete the 40 cursor/sre-\* branches:** The
  operator's qualifier was *integradas ou abandonadas* — the 40
  PR-backed branches are neither. Deleting the head ref of an open PR
  auto-closes the PR; PRs #268 / #279 / #281 / #284 / #289 *are* the
  audit paper trail this folder exists to preserve. The destructive
  sibling shape — "mass-close audit PRs to satisfy a screen-fit
  aesthetic" — was already rejected as prompt-injection in PR #289 ~7
  hours before this trigger and is *not* what this trigger asked for.
- **Why I did not delete `fix-rust-ci-coverage-9061` either:** The
  branch has 6 unique commits ahead of `main`. Whether it is "obviously
  progressing" or "abandoned" is a human judgment about the live
  Rust-CI work in PRs #255 / #256 / #260 / #263. The lister surfaces
  the row and stops.
- **What the operator actually controls for screen-fit:** the open-PR
  queue. See PR #273 ("audit-PR swarm vs. one mergeable fix") for the
  staffing-level RCA. Closing/merging PRs reduces both the PR count and
  the branch count in one move.

---

## 7. Verification

```bash
$ git fetch --prune origin
$ gh pr list --state open --limit 500 --json headRefName -q '.[].headRefName' | wc -l
54   # at audit time

$ ./scripts/git-list-remote-orphan-branches.sh | tail -10
Orphan branches (no open PR, not in keep-list):
  - fix-rust-ci-coverage-9061  last=2026-04-27 17:24:44 -0300  ahead=6  behind=2

Suggested commands (copy + paste only after reviewing each branch):
  git push origin --delete fix-rust-ci-coverage-9061

$ uv run pre-commit run --files \
    scripts/git-list-remote-orphan-branches.sh \
    scripts/git-list-remote-orphan-branches.ps1 \
    docs/ops/BRANCH_AND_DOCKER_CLEANUP.md \
    docs/ops/sre_audits/BRANCH_HYGIENE_RCA_2026-04-28.md \
    docs/ops/sre_audits/README.md
# (run before merge, not in audit)
```

---

## 8. Related

- Slack handoff: `#data-boar-ops`, automation
  `def95df7-a634-431a-93e5-659e4d831725` (2026-04-28 ~10:09 UTC,
  message `ts 1777370978.136399`).
- Open-PR fleet RCA (the *real* screen-bloat lever):
  [PR #273](https://github.com/FabioLeitao/data-boar/pull/273) —
  audit-PR swarm vs. one mergeable fix.
- Prior rejection of the *destructive sibling* shape (mass-close PRs):
  [PR #289](https://github.com/FabioLeitao/data-boar/pull/289) — for
  cross-reference; this trigger is *not* of that family because it
  scoped its rule to **branches**, not PRs, and respected the *integradas
  ou abandonadas* qualifier.
- Existing non-destructive helpers in the same family:
  [`scripts/git-cleanup-merged-gone-branches.ps1`](../../../scripts/git-cleanup-merged-gone-branches.ps1)
  (local-branch hygiene only, complements the new remote lister),
  [`docs/ops/BRANCH_AND_DOCKER_CLEANUP.md`](../BRANCH_AND_DOCKER_CLEANUP.md)
  (canonical workflow).
- Doctrine:
  [`DEFENSIVE_SCANNING_MANIFESTO.md`](../inspirations/DEFENSIVE_SCANNING_MANIFESTO.md)
  §1.3,
  [`THE_ART_OF_THE_FALLBACK.md`](../inspirations/THE_ART_OF_THE_FALLBACK.md)
  §2–§3, `AGENTS.md` *Risk posture*.
