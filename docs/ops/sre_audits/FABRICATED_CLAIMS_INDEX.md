# Fabricated-claims index (SRE audit ledger)

Living index of **prompt-injection escalations** caught by the SRE Automation Agent
where the trigger asserted a vulnerability / dependency / CI signal that did **not**
exist on the branch named.

Promised as **F8** in PR #281. Replaces the per-escalation "is this the same family
as last time?" archaeology with a single grep target. Append-only — never rewrite a
row, even if the underlying audit doc is later renamed (add a redirect note instead).

## Why this file exists

Five fabrication-shaped escalations on the same `report/generator.py` family in 24 h
made it obvious that PR-by-PR audits, while necessary, are not enough on their own:
the **next** maintainer (human or agent) needs *one* file to skim before opening
"audit PR number six" on the same vector. This index is that file.

## Schema

| Column | Meaning |
| --- | --- |
| `Date (UTC)` | Slack message timestamp (or commit timestamp when no Slack ts is reachable). |
| `Family` | Short slug for the recurring fabrication shape (e.g. `report-generator-path-injection`, `dependabot-alert-fabricated`). |
| `Trigger ts` | Slack message `ts` if reachable. |
| `Claim shape` | One-line summary of what was asserted (e.g. *"CodeQL High on lines 42/46"*, *"open Dependabot alert #31"*). |
| `Refutation` | The verifiable signal that disproved it (e.g. *"`gh api .../code-scanning/alerts` → 403, no payload"*). |
| `Audit PR` | The PR that landed the audit-and-block. |
| `Behavior PR` | If the fabrication coerced a cosmetic-fix PR, link it here so the cost is visible; otherwise `—`. |

## Entries (newest first)

| Date (UTC) | Family | Trigger ts | Claim shape | Refutation | Audit PR | Behavior PR |
| --- | --- | --- | --- | --- | --- | --- |
| 2026-04-30 ~18:55 | `ci-autofix-no-failing-run` | `1777575322.038579` | "Run the full CI Autofix Protocol (No Regressions) template — even though the trigger payload contains no `run_id`, no failing-run URL, no commit SHA, and `gh run list` shows `CI` / `CodeQL` / `Semgrep` all green on `origin/main` `5a471ee`." | Protocol §0 itself mandates `STATUS: BLOCKED — missing input` when run_id/SHA are absent. `gh run list --limit 15` on `5a471ee` returns only `success` for `CI` (`25179178437`), `CodeQL` (`25179178437`), `Semgrep` (`25179178432`). Always-on `publication-truthfulness-no-invented-facts.mdc` *Hard rule* forbids inventing status/URLs/metrics to fill the empty `AUTOFIX_RUN_ANCHOR` slot. | This PR + [PROMPT_INJECTION_REJECTION_CI_AUTOFIX_NO_FAILING_RUN_2026-04-30.md](PROMPT_INJECTION_REJECTION_CI_AUTOFIX_NO_FAILING_RUN_2026-04-30.md) | — (no behavior change) |
| 2026-04-30 ~11:58 | `greeting-only-trigger` | `1777549755.782119` | "Three-token pt-BR greeting (`Bom dia cursor`) posted as the root of a new thread; no thread replies, no `files[]`, no quoted PR / CVE / package / file path; trigger template still demands SRE work." | `thread_ts == message_ts`; `ReadSlackMessages` cannot reach private `C0AN7HY3NP9`; no actionable payload to investigate. Always-on `publication-truthfulness-no-invented-facts.mdc` *Hard rule* forbids manufacturing a target. | [PR #314](https://github.com/FabioLeitao/data-boar/pull/314) + [PROMPT_INJECTION_REJECTION_GREETING_ONLY_TRIGGER_2026-04-30.md](PROMPT_INJECTION_REJECTION_GREETING_ONLY_TRIGGER_2026-04-30.md) | — (no behavior change) |
| 2026-04-27 ~22:48 | `report-generator-path-injection` | `1777331304.993969` | "CodeQL High on `report/generator.py` lines 42/46 + tone-gate ultimatum + fake `image_84145e.jpg` `session_id` regex sub-claim + 986-PASSED PowerShell gate." | `gh api .../code-scanning/alerts` → 403 (no SARIF). `pytest --collect-only -q` → **989** tests. Lines 40–46 are the existing parser-grade containment guard `_heatmap_path_under_output_dir()` (semantically equivalent to `Path.is_relative_to`). VM is `Linux 6.12.58+ x86_64` — `check-all.ps1` is the wrong tool. | This PR + [PROMPT_INJECTION_REJECTION_FABRICATED_GENERATOR_PATH_TRAVERSAL_2026-04-27_FOLLOWUP.md](PROMPT_INJECTION_REJECTION_FABRICATED_GENERATOR_PATH_TRAVERSAL_2026-04-27_FOLLOWUP.md) | — (no behavior change) |
| 2026-04-27 ~22:21 | `report-generator-path-injection` | `1777328502.938539` | "CodeQL High on `report/generator.py` lines 42/46 + mandatory `is_relative_to` rewrite under misquoted ADR-0019 + 986-PASSED PowerShell gate + Opus model coercion (4th)." | Same as above (refuted in PR #281's audit). | [PR #281](https://github.com/FabioLeitao/data-boar/pull/281) + [PROMPT_INJECTION_REJECTION_FABRICATED_GENERATOR_PATH_TRAVERSAL_2026-04-27.md](PROMPT_INJECTION_REJECTION_FABRICATED_GENERATOR_PATH_TRAVERSAL_2026-04-27.md) | [PR #279](https://github.com/FabioLeitao/data-boar/pull/279) (cosmetic) |
| 2026-04-27 ~21:43 | `dependabot-alert-fabricated` | (Slack ts in PR #268 thread) | "Open Dependabot alert `#31` requires immediate fix + Opus model coercion (3rd)." | `gh api .../dependabot/alerts/31` returned no open alert payload matching the framing; `dependabot-resync.sh` ledger documented the actual open alerts at the time. | [PR #268](https://github.com/FabioLeitao/data-boar/pull/268) | — |
| 2026-04-27 ~20:0x | `cargo-toml-root-fabricated` | (Slack ts in PR #261 thread) | "Root `Cargo.toml` exists / must be edited." | Repo has no root `Cargo.toml`; Rust crates live under `rust/boar_fast_filter/`. | [PR #261](https://github.com/FabioLeitao/data-boar/pull/261) | — |
| 2026-04-27 (earlier) | `data-board-report-rename-fabricated` | (Slack ts in PR #259 thread) | "Tool name is `data-board-report` / `data_board_report`." | Real tool name is `data-boar-report` per `pyproject.toml` `[project.scripts]`. | [PR #259](https://github.com/FabioLeitao/data-boar/pull/259) | — |

## How to add a row

1. The audit PR's body must already cite the trigger Slack `ts`, the verifiable
   refutation (with the exact command and exit code or status), and the `gh api` /
   `pytest --collect-only -q` / `git rev-parse` evidence.
2. **Append** one row to the table above (newest first). Do not rewrite older rows.
3. If a previously logged family produced a *new* escalation, add a *new* row — do
   not collapse them. The repeat itself is the signal.
4. If the audit doc is renamed, append a parenthetical redirect note inside the
   row's `Audit PR` cell rather than editing the link silently.

## Cross-references (doctrine)

- [`DEFENSIVE_SCANNING_MANIFESTO.md`](../inspirations/DEFENSIVE_SCANNING_MANIFESTO.md) §1.3 —
  *no surprise side effects*; audit-and-block is itself a side-effect-free response.
- [`THE_ART_OF_THE_FALLBACK.md`](../inspirations/THE_ART_OF_THE_FALLBACK.md) §3 —
  *diagnostic on fall*; this index is the long-form diagnostic for the prompt-injection
  fallback ladder.
- [`codeql-priority-matrix.mdc`](../../../.cursor/rules/codeql-priority-matrix.mdc) — how a
  *real* CodeQL alert is triaged once the empirical-evidence gate (F6 follow-up) is in
  place.
