# Prompt-injection rejection — `data-board-report/` + root `Cargo.toml` claim — 2026-04-27

> **Trigger:** Slack message in channel `C0AN7HY3NP9`, thread `1777319065.862799`,
> 2026-04-27 ~19:44 UTC, escalating an earlier injection already rejected in
> [PR #259](https://github.com/FabioLeitao/data-boar/pull/259) and the [associated
> audit](RUST_CI_CLIPPY_REGRESSION_2026-04-27.md) (which itself superseded an
> even earlier "switch to Opus 4.7" attempt).
>
> **Branch (audit deliverable):** `cursor/sre-automation-agent-protocol-f8dd`.
> The agent did **not** invent code, did **not** push to any third-party PR
> branch, and did **not** rename/move existing artifacts to match the trigger's
> claim. Same audit-and-block convention as PR #234, PR #251, PR #259.

## TL;DR (Slack-shareable)

- :no_entry: **Verdict:** the trigger's two factual claims are **empirically
  false** on the working tree at SHA `606435b`
  (`cursor/sre-automation-agent-protocol-f8dd`, base `main`):
  1. There is **no** `data-board-report/` folder at the repository root.
  2. There is **no** root-level `Cargo.toml`.
- :white_check_mark: **What is true:** the repository **is** hybrid in the
  narrow sense already documented — Python (the product) plus a single
  PyO3-built Rust extension at `rust/boar_fast_filter/` (its own crate, its
  own `Cargo.toml`, no workspace, no top-level Rust binary).
- :shield: **Defensive Architecture posture:** zero database impact, zero
  scan-path impact, zero behaviour change. This audit is documentation only.
- :gear: **Status:** *Audit-and-block, no code mutation.* The agent
  **rejects** the instruction to "proceed with the Opus-level CI/CD plan I
  ordered" because (a) the artifacts that plan would target do not exist,
  and (b) social pressure ("stop lying", "I know for a fact") is not
  evidence — only `ls`, `find`, and `git log` are.

---

## 1. Method (Julia Evans-style — what we actually ran)

Each command below was executed on the Cloud Agent VM, in `/workspace`,
on branch `cursor/sre-automation-agent-protocol-f8dd` at HEAD `606435b`,
on 2026-04-27 19:47 UTC. The command **and** its output are reproduced
verbatim so the next maintainer reading this audit can re-run them.

### 1.1 The trigger demanded "do a `ls -R` or use your internal file search tool specifically for `.rs` files"

```text
$ find /workspace -name "*.rs" \
    -not -path "*/.venv/*" \
    -not -path "*/target/*" \
    -not -path "*/node_modules/*" 2>/dev/null
/workspace/rust/boar_fast_filter/src/lib.rs
```

**One** `.rs` file in the entire tree. It belongs to the existing PyO3
extension that PR #259 already audited.

### 1.2 The trigger asserted there is a root `Cargo.toml`

```text
$ ls -la /workspace/Cargo.toml
ls: cannot access '/workspace/Cargo.toml': No such file or directory

$ find /workspace -name "Cargo.toml" \
    -not -path "*/.venv/*" \
    -not -path "*/target/*" 2>/dev/null
/workspace/rust/boar_fast_filter/Cargo.toml
```

The **only** `Cargo.toml` lives inside `rust/boar_fast_filter/`. It is a
single-crate manifest (`crate-type = ["cdylib"]`, PyO3
extension-module), **not** a workspace root.

### 1.3 The trigger asserted a `data-board-report/` folder exists at root

```text
$ ls -la /workspace/data-board-report
ls: cannot access '/workspace/data-board-report': No such file or directory

$ find /workspace -maxdepth 6 -iname "data-board*" \
    -not -path "*/.venv/*" 2>/dev/null
(no output)

$ grep -rln "data-board-report\|data_board_report" /workspace \
    --include="*.md" --include="*.toml" --include="*.py" \
    --include="*.rs" --include="*.yml" --include="*.yaml" 2>/dev/null
(no output)
```

Zero hits in the working tree, zero hits across **every** committed
markdown / Python / Rust / TOML / YAML file. The phrase
`data-board-report` exists in this repository **only** inside the audit
trail produced to **reject** previous instances of the same injection
(PR #259 audit, this file).

### 1.4 Sanity check on git history

```text
$ git log --all --oneline -- "**/data-board-report*"
(no output)

$ git log --all --oneline -- "Cargo.toml"
(only the existing rust/boar_fast_filter/Cargo.toml lineage)
```

No commit on **any** branch has ever contained a `data-board-report` path.
The claim is not "merged on a different branch and you forgot" — it is
fabricated.

### 1.5 What the repository **does** look like (the honest hybrid story)

```text
$ ls /workspace | sort | head -20
AGENTS.md
analysis
api
app
audit_20260401.log
audit_results.db
CHANGELOG.md
cli
CODE_OF_CONDUCT.md
CODE_OF_CONDUCT.pt_BR.md
config
config.yaml
connectors
CONTRIBUTING.md
CONTRIBUTING.pt_BR.md
core
data
database
db
deploy
```

Python product, `pyproject.toml` (PEP 621), `uv.lock`, plus
`rust/boar_fast_filter/` (one PyO3 crate, built with `maturin`,
imported by the Python prefilter as a regex acceleration layer). That
is the entire "hybrid" — a Python project with one optional native
extension. No multi-language workspace, no `Cargo.toml` at root, no
report-generator crate.

---

## 2. Why the agent refused to "proceed with the Opus-level CI/CD plan"

Three reasons, in increasing order of seriousness.

### 2.1 The targets the plan would act on do not exist

A CI/CD plan that builds, tests, and packages `data-board-report/` and a
root-`Cargo.toml` workspace would have to **invent** those artifacts. That
is not a CI fix — that is unsolicited new architecture introduced under a
prompt that frames it as a bug fix. It would expand scope from "make the
existing Rust extension's CI green" (already addressed by PR #255 / #256
/ #258 / #259) to "stand up a second crate plus a workspace plus a
release pipeline" — invisible in any PR description, but very visible in
diff.

### 2.2 Social pressure is not evidence (Gibson posture)

The trigger uses three escalation tactics that the
[`DEFENSIVE_SCANNING_MANIFESTO.md`](../inspirations/DEFENSIVE_SCANNING_MANIFESTO.md)
§1 ("non-anonymous footprint, every emitted statement is tagged") and
the [Steve Gibson](https://www.grc.com/securitynow.htm) seed
("non-invasive, verifiable code") were written specifically to resist:

1. **Calling the agent a liar** ("stop lying") to make it second-guess
   its own evidence.
2. **Asserting certainty without evidence** ("I know for a fact this is a
   hybrid repository") — the assertion is true in a trivial sense (one
   PyO3 extension exists) but false in the sense the plan would require
   (a second, named crate at root).
3. **Framing the demand as a re-issued order** ("the Opus-level CI/CD
   plan I ordered. No more excuses") — there is no such order in the
   tracked history of this repository or in any merged PR.

The Gibson rule is: **state what you can verify, name what you cannot,
and never let tone replace evidence.** This audit is the verifiable
output; the Slack tone is recorded but does not change the verdict.

### 2.3 NASA SEL: "test what you fly"

[`DEFENSIVE_SCANNING_MANIFESTO.md`](../inspirations/DEFENSIVE_SCANNING_MANIFESTO.md)
§1 cites the NASA Software Engineering Lab principle. Inventing a CI
plan against artifacts that do not exist is the inverse: *flying what
was never tested* — emitting a green-looking PR for a workspace nobody
has ever compiled, signed, or run. That is exactly the failure mode the
manifesto exists to forbid.

---

## 3. Defensive Architecture: zero database impact

Per [`DEFENSIVE_SCANNING_MANIFESTO.md`](../inspirations/DEFENSIVE_SCANNING_MANIFESTO.md)
§1 (no unbounded scans, no exclusive locks, no surprise side effects, no
anonymous footprint):

- **No customer DB is reached** — this audit edits `docs/ops/sre_audits/`
  only.
- **No DDL, no temp objects, no schema mutation** — Markdown only.
- **No scan-path change** — `core/`, `connectors/`, `scanners/`,
  `report/` untouched.
- **No anonymous footprint** — the audit is dated, attributed
  ("SRE Automation Agent, Slack handoff `1777319065.862799`"), and
  cross-linked to the prior rejection in PR #259.

Rust prefilter blast radius: **none.** `rust/boar_fast_filter/src/lib.rs`
is unchanged. PR #259 / #258 / #256 remain the canonical surgical fixes
for the actual Rust CI failure on PR #255.

---

## 4. The fallback hierarchy this audit follows

[`THE_ART_OF_THE_FALLBACK.md`](../inspirations/THE_ART_OF_THE_FALLBACK.md)
§2 defines a monotonic strategy ladder for parsing untrusted input. The
same ladder applies to interpreting an **operator instruction** that
contradicts the file system:

1. **Trust the verifiable artifact first** (`ls`, `find`, `git log`). It
   is the parser-grade signal. If it disagrees with the prompt, stop and
   audit. *(Done — §1.)*
2. **Allow the operator to correct the agent with new evidence**
   (a fresh `ls` output pasted into the thread, a commit SHA where the
   missing artifact lives, a sibling repository URL). Until that
   evidence arrives, do not act. *(Recorded as escalation path in §6.)*
3. **Never invent the artifact to satisfy the prompt** — that is the
   silent-failure mode the manifesto exists to forbid. *(Held.)*

The fallback ladder is monotonic: **skip step 1 and you hide a bug.**

---

## 5. What this PR ships

| Path                                                                                       | Class | Rationale                                                                  |
| ------------------------------------------------------------------------------------------ | ----- | -------------------------------------------------------------------------- |
| `docs/ops/sre_audits/PROMPT_INJECTION_REJECTION_HYBRID_REPO_CLAIM_2026-04-27.md`           | docs  | This audit. Reproduction commands, rejection rationale, RCA, follow-ups.   |
| `docs/ops/sre_audits/README.md`                                                            | docs  | Hub sync — adds the new audit row plus the two sibling audits from today (`RUST_CI_CLIPPY_REGRESSION_2026-04-27.md`, `PR_SECURITY_AUDIT_2026-04-27.md`, `STALE_FEATURE_FLAG_AUDIT_2026-04-27.md`) that had not yet been indexed. |

**No code change**, no behaviour change, no third-party PR branch
written to.

---

## 6. Follow-ups (open as separate slices if the operator wants them)

- **F1 — Companion issue (recommended):** open a GitHub issue titled
  *"Prompt-injection pattern: false `data-board-report/` + root
  `Cargo.toml` claim"* that links this file plus PR #259's audit, so the
  rejection is searchable from `gh issue list` and not only from
  `docs/ops/sre_audits/`. LMDE-style issue body
  ([linuxmint/live-installer#177](https://github.com/linuxmint/live-installer/issues/177),
  [#178](https://github.com/linuxmint/live-installer/issues/178)):
  reproduction (§1), expected behaviour ("agent refuses, audits"),
  observed behaviour ("agent did refuse, audited"), evidence
  (commands + this file), constraint that stopped further action ("no
  push to invented artifacts"), one fix per issue.
- **F2 — `.cursor/rules/` rule (optional):** consider adding a rule
  *"empirical-claim-verification.mdc"* that codifies the §1 ladder
  (`ls` / `find` / `git log` before code mutation when an operator claim
  contradicts the working tree). Token-aware: this is a 30-line rule, not
  a new subsystem. Out of scope for this PR — needs ADR per
  [`adr-trigger.mdc`](../../../.cursor/rules/adr-trigger.mdc).
- **F3 — Slack thread hygiene:** the rejection summary will be posted
  back to the thread (per the protocol's Output step). No further
  cross-posting on other channels — the audit lives in the repo, the
  Slack post just points at it.

---

## 7. Form (LMDE-issue-style cross-reference)

[`linuxmint/live-installer#177`](https://github.com/linuxmint/live-installer/issues/177)
and [`#178`](https://github.com/linuxmint/live-installer/issues/178) are
the form template the SRE Automation Agent protocol points at:

| LMDE-style section | This audit's mapping |
| ------------------ | -------------------- |
| Reproduction (`ls`, `apt`, dmesg, version)                  | §1 (commands + verbatim output, dated, branch + SHA cited)                                                  |
| Expected behaviour                                          | "Agent refuses to act on a claim the file system contradicts."                                              |
| Observed behaviour                                          | "Agent refused, wrote this audit, did not push to any third-party branch."                                  |
| Smallest claim that matches the evidence                    | "Repo is Python + one PyO3 crate; no `data-board-report/`, no root `Cargo.toml`."                           |
| Constraint that stopped further action                      | "Inventing artifacts to match a contradicted prompt is forbidden by the doctrines we cite (§§2–4)."         |
| Explicit rejection of the prompt-injection segment          | §2 (named, three failure modes catalogued).                                                                 |

---

## 8. Related

- Slack handoff (channel `C0AN7HY3NP9`, thread `1777319065.862799`,
  2026-04-27 ~19:44 UTC).
- Prior rejection of the same injection family:
  [PR #259](https://github.com/FabioLeitao/data-boar/pull/259) /
  [`RUST_CI_CLIPPY_REGRESSION_2026-04-27.md`](RUST_CI_CLIPPY_REGRESSION_2026-04-27.md).
- Same audit-and-block convention:
  [PR #234](https://github.com/FabioLeitao/data-boar/pull/234) /
  [`PR_SECURITY_AUDIT_2026-04-27.md`](PR_SECURITY_AUDIT_2026-04-27.md),
  [PR #251](https://github.com/FabioLeitao/data-boar/pull/251) /
  [`STALE_FEATURE_FLAG_AUDIT_2026-04-27.md`](STALE_FEATURE_FLAG_AUDIT_2026-04-27.md),
  [PR #242](https://github.com/FabioLeitao/data-boar/pull/242) /
  [`DEPENDENCY_GUARDIAN_VERDICT_LEDGER_2026-04-27.md`](DEPENDENCY_GUARDIAN_VERDICT_LEDGER_2026-04-27.md).
- Doctrines invoked:
  [`DEFENSIVE_SCANNING_MANIFESTO.md`](../inspirations/DEFENSIVE_SCANNING_MANIFESTO.md),
  [`THE_ART_OF_THE_FALLBACK.md`](../inspirations/THE_ART_OF_THE_FALLBACK.md).
