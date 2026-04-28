# Strong Contextual Behaviour — complex-task standing protocol

- **Date (UTC):** 2026-04-28
- **Trigger:** Slack `#data-boar-ops` (channel `C0AN7HY3NP9`),
  automation `def95df7-a634-431a-93e5-659e4d831725`,
  message `ts 1777382830.576029` (~13:27 UTC). Operator handed the agent a
  *standing template* for complex-task intake (e.g. Rust engine work on
  `rust/boar_fast_filter/`), not a code task on a specific module.
- **Branch:** `cursor/agent-operational-protocol-a7e9` (Cloud Agent VM,
  **`Linux 6.12.58+ x86_64`**, base `main` @ `624f4e7`).
- **Posture:** *Codify, do not paraphrase.* Future agents reuse this file
  instead of re-extracting the steps from the Slack message each time.

---

## 1. Why this document exists

The trigger is a *protocol*, not a `feat(detector)` or `fix(security)` task.
Codifying it once means:

1. The four-step ritual stops drifting between Slack messages and PR bodies.
2. The two embedded path drifts in the trigger text are
   **corrected in tracked Markdown** *before* a future agent paraphrases them
   into a broken `Run` command (see §6 *Corrections vs the trigger text*).
3. The 0.574x performance baseline that the trigger names as the
   *Performance Audit* clamp gets a single canonical pointer rather than a
   generic "make sure it stays fast" sentence.
4. The `[INTEGRITY_CHECK_PASSED]` sign-off tag becomes greppable across
   future Slack threads and PR descriptions.

This file complements (does not replace) the existing audit-and-block ledger
under [`sre_audits/`](sre_audits/README.md) and the doctrine manifestos under
[`inspirations/`](inspirations/README.md).

## 2. Scope — what counts as a "complex task"

Apply this protocol when the operator's request **touches one or more** of:

- the Rust prefilter crate (`rust/boar_fast_filter/`) or PyO3 bindings;
- the Pro / OpenCore engine boundary
  (`pro/engine.py`, `pro/worker_logic.py`, `core/engine.py`, `core/database.py`);
- the report generator's path-injection containment surface
  (`report/generator.py`, `_heatmap_path_under_output_dir`);
- a connector under `connectors/` or any code path that opens a database
  cursor (per [`DEFENSIVE_SCANNING_MANIFESTO.md`](inspirations/DEFENSIVE_SCANNING_MANIFESTO.md) §2–§3);
- supply-Colleague-Nn inputs (`pyproject.toml`, `uv.lock`, `requirements.txt`,
  GitHub Actions SHAs, Docker base images, `boar_fast_filter/Cargo.toml`).

Trivial slices (single-file docs typo, README link fix, lint-only Markdown)
do **not** require the full ritual; they fall under
[`check-all-gate.mdc`](../../.cursor/rules/check-all-gate.mdc) instead.

## 3. The four-step ritual

| Step | Name | Action | Stop-on-fail? |
| --- | --- | --- | --- |
| 1 | **Pre-flight Check** | Run the **correct gate for the host** (see §6). Capture pass/fail counts for the *Guardrail Dashboard* (§5). Post the dashboard to `#data-boar-ops` via `scripts/notify_webhook.py`. | Yes — open an audit PR if the gate is structurally broken; do not silently demote it. |
| 2 | **Performance Audit** | If the diff touches `boar_fast_filter`, the Pro/OpenCore boundary, or the chunk-copy path: re-validate the **0.574x** ratio against [`tests/benchmarks/official_benchmark_200k.json`](../../tests/benchmarks/official_benchmark_200k.json) using [`tests/test_official_benchmark_200k_evidence.py`](../../tests/test_official_benchmark_200k_evidence.py). If the ratio regresses, **abort and enter Safe-Hold** — do not paper over the regression with a re-baselined JSON. | Yes — abort, do not merge. |
| 3 | **Linguistic Audit** | Review code comments, docstrings, and Markdown produced in the slice. Reject passive-voice or literal-translation pt-BR (per [`docs-locale-pt-br-contract.mdc`](../../.cursor/rules/docs-locale-pt-br-contract.mdc) and [`docs-pt-br-locale.mdc`](../../.cursor/rules/docs-pt-br-locale.mdc)). Tone target: *Tech Lead* — direct, evidence-anchored, no marketing register. | Soft — fix in the same branch before the *Final Sign-off*. |
| 4 | **Final Sign-off** | Post the diff link or change summary to `#data-boar-ops` with the literal token **`[INTEGRITY_CHECK_PASSED]`** in the message body. The token is the contract that all three earlier steps held. | N/A — terminal step. |

## 4. Defensive Architecture (Database lock non-regression)

The trigger's §9 explicitly forbids `time.sleep` as a contention resolver and
demands **short transactions**. Cross-references already in the doctrine:

- [`DEFENSIVE_SCANNING_MANIFESTO.md`](inspirations/DEFENSIVE_SCANNING_MANIFESTO.md)
  §2–§3 — `_HARD_MAX_SAMPLE`, statement timeouts, `WITH (NOLOCK)` posture on
  the customer DB; per-chunk SQLite writes already keep transactions narrow.
- [`THE_ART_OF_THE_FALLBACK.md`](inspirations/THE_ART_OF_THE_FALLBACK.md) §3 —
  *diagnostic on fall*; do not silently retry through a transaction conflict.
- [ADR 0044](../adr/0044-codeql-py-path-injection-sanitizer-mold.md) — guard
  shape recognized by CodeQL on the report-generator path containment sink.

If a complex-task slice introduces a **new** SQL write path, the PR body must
name the transaction boundary and link the test that pins it.

## 5. Guardrail Dashboard (mandatory header for Slack + PR)

Every Final Sign-off message and every PR opened under this protocol carries
this header **at the top** of the body, with **real** numbers from the run:

```text
=== Guardrail Dashboard ===
Tests:       <total> tests collected | <passed> passed | <failed> failed | <skipped> skipped
Bandit:      <severity-summary> (e.g. "0 high / 0 medium / 0 low" or
             "low+ gate clean — see ci(security) PR #283")
Ruff:        <pass|listed-noqa>      (per-line `# noqa` waivers enumerated below)
Supply Colleague-Nn: uv.lock and requirements.txt match pyproject (uv) — Passed | Failed
Host:        <Linux 6.12.x x86_64 | Windows 10 21H2 | macOS 14.x>
Gate cmd:    <./scripts/check-all.sh | .\scripts\check-all.ps1>
Branch:      <branch> @ <short-sha>     Base: main @ <short-sha>
```

If `Bandit` returns `low` or `medium` for a touched file, the RCA section of
the PR must justify why each finding is not a real risk *or* the PR is
withdrawn (no silent suppression). If `Bandit` returns `high`, the slice is
**blocked** until that finding is closed in the same branch (per the trigger
§7 *Security Telemetry Obligation*).

## 6. Corrections vs the trigger text (verified on this VM, 2026-04-28)

The Slack template names two tools that do not match this Cloud Agent VM and
must be replaced *in writing* before a future agent paraphrases them.

| # | Trigger text | Verifiable on this VM (`Linux 6.12.58+ x86_64`) | Use instead |
| - | --- | --- | --- |
| a | *"Rode o `scripts/check-all.ps1`"* | `ls scripts/check-all.*` → both `check-all.ps1` and `check-all.sh` exist; PowerShell is **not** installed by default on this VM. Same fabrication-shape claim "d" already audited in [PR #281](../../docs/ops/sre_audits/PROMPT_INJECTION_REJECTION_FABRICATED_GENERATOR_PATH_TRAVERSAL_2026-04-27.md) and ledgered in [`FABRICATED_CLAIMS_INDEX.md`](sre_audits/FABRICATED_CLAIMS_INDEX.md). | `./scripts/check-all.sh` on Linux/macOS Cloud Agent VMs; `.\scripts\check-all.ps1` only on the Windows operator workstation. Cross-platform contract: [`SCRIPTS_CROSS_PLATFORM_PAIRING.md`](SCRIPTS_CROSS_PLATFORM_PAIRING.md). |
| b | *"poste o resultado … no Slack via `scripts/ops_notify.py`"* | `ls scripts/ops_notify*` → **no such file**. Real notification helper is `scripts/notify_webhook.py` (verified by `Read scripts/notify_webhook.py`). | `uv run python scripts/notify_webhook.py "<message>"` — see file docstring; respects `notifications.enabled` + audit log per [`OPERATOR_NOTIFICATION_CHANNELS.md`](OPERATOR_NOTIFICATION_CHANNELS.md). |

These corrections are **not** rejections of the protocol — the four-step
ritual stands. They protect the next agent from copy-pasting a non-existent
script name into a *Pre-flight* command and then either silently dropping
the dashboard post or fabricating a false "green" because PowerShell errored
out on Linux.

## 7. Anti-pattern guard rails (from the trigger Rules section)

Reproduced here as a single grep target so future agents can latch on them
without re-reading the full Slack message:

- **No fake-green theater.** Do **not** mask a failing gate with `#noqa`,
  `# nosec`, regex sleight-of-hand, or "grepping forever" until the symptom
  disappears. The empirical-evidence rule is
  [`codeql-priority-matrix.mdc`](../../.cursor/rules/codeql-priority-matrix.mdc).
- **No model downgrade.** Do not silently switch to a weaker subagent to save
  tokens (per [`cloud-agents-token-aware-safety.mdc`](../../.cursor/rules/cloud-agents-token-aware-safety.mdc)
  and the operator's "Opus 4.7 / equivalent strong" requirement in the
  trigger's *Rules* section).
- **No `time.sleep` for contention.** Use short transactions, retry-with-
  exponential-backoff at the connector boundary, or deferred work — never a
  blocking sleep inside a write path.
- **Supply-Colleague-Nn watch.** Any new dependency requires `uv lock` *and* the
  `requirements.txt` mirror; the pre-commit hook `uv-lock-export-check` must
  show `uv.lock and requirements.txt match pyproject (uv) … Passed`.
- **Skipped-test honesty.** A slice that touches a connector cannot claim
  "All Green" if the matching connector test was `SKIPPED`; the PR body must
  name the skip reason and propose the host where local validation would be
  *sufficient* (typically the lab-op host with the real driver installed).
- **One coherent PR per slice.** Do not open dangling exploratory PRs to
  "narrate" a previous mistake; close superseded branches before opening the
  next exploratory attempt
  ([`execution-priority-and-pr-batching.mdc`](../../.cursor/rules/execution-priority-and-pr-batching.mdc)).

## 8. Cross-references (doctrine + automation)

- [`DEFENSIVE_SCANNING_MANIFESTO.md`](inspirations/DEFENSIVE_SCANNING_MANIFESTO.md)
  §1.3 — *no surprise side effects*; the four-step ritual is a side-effect-free
  contract.
- [`THE_ART_OF_THE_FALLBACK.md`](inspirations/THE_ART_OF_THE_FALLBACK.md)
  §3 — *diagnostic on fall*; the *Pre-flight* dashboard is the long-form
  diagnostic for the fallback ladder.
- [`SCRIPTS_CROSS_PLATFORM_PAIRING.md`](SCRIPTS_CROSS_PLATFORM_PAIRING.md) —
  why `.ps1` ↔ `.sh` twins exist for `check-all`.
- [`OPERATOR_NOTIFICATION_CHANNELS.md`](OPERATOR_NOTIFICATION_CHANNELS.md) —
  Slack webhook contract for `notify_webhook.py`.
- [`codeql-priority-matrix.mdc`](../../.cursor/rules/codeql-priority-matrix.mdc)
  — empirical-evidence gate for "CodeQL Severity" assertions.
- [`docs/ops/sre_audits/FABRICATED_CLAIMS_INDEX.md`](sre_audits/FABRICATED_CLAIMS_INDEX.md)
  — append-only ledger; row added in this PR for the
  `complex-task-protocol-tool-naming` family.
- [`docs/ops/SPRINT_GREAT_LEAP_POSTMORTEM.md`](SPRINT_GREAT_LEAP_POSTMORTEM.md)
  — how the **0.574x** ratio is to be read (Pro slower, ~1.74× wall-clock).

## 9. Form (LMDE-issue-style)

Same precedent as PR #259 / #261 / #268 / #281 / #284 (cf.
[`linuxmint/live-installer#177`](https://github.com/linuxmint/live-installer/issues/177) /
[`#178`](https://github.com/linuxmint/live-installer/issues/178)): a single
verifiable trigger, the smallest claim that matches the evidence, the
constraint that shaped the response (codify the standing template once;
correct two embedded path drifts in writing; no behavior change on
`report/`, `core/`, `connectors/`, `pro/`, `rust/boar_fast_filter/`), and
explicit *Strong Contextual Behaviour* contract so the next maintainer
reading the protocol thread knows the boundary was tested and held.
