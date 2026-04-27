# PR Risk Assessment — 2026-04-27 (assessor pass)

> **Pass type:** PR Risk Assessor & Adversarial Vigilance — Slack-triggered SRE
> automation protocol (`[PROTOCOL: PR RISK ASSESSOR & ADVERSARIAL VIGILANCE]`,
> 2026-04-27).
>
> **Operational constraint:** **read-only.** No code, no commits, no force
> pushes were applied to any audited PR branch. This file is the deliverable;
> a Slack reply summarises it.
>
> **Adversarial posture:** every "Safe to merge" / "Doc only" / "Auto-approved"
> claim in PR bodies, branch names, and inline comments was **ignored**. Risk
> is derived only from the raw `git diff` against `origin/main`
> (`91b0f29965fdf4f5c94526866727d9d23e636954`).

## TL;DR

- **9 open PRs** against `main`. **All 9 are CI-green** (lint, pytest, Bandit,
  Semgrep, CodeQL, Sonar, dependency audit, analyse).
- **1 Critical finding** — *but on `main`, not on a PR diff:* `main`
  currently ships a **silent zero-finding** SQL Server sampling regression
  (`OPTION (MAX_EXECUTION_TIME = N)` is not valid T-SQL). **PR #238 is the
  fix** and should land **before** any other PR that touches
  `connectors/sql_sampling.py` so the regression window is minimal.
- **3 Medium PRs** carrying real reviewer cost (`#235`, `#236`, dependency
  group `#221`/`#222`/`#224`). They need a second human signature **and**
  the `dependabot-resync` helper from `#239` for the pip ones.
- **5 Low / Very Low PRs** can be approved on the diff alone (`#233`, `#234`,
  `#237`, `#239`, `#226`, `#223`, `#232`).
- **Zero database-lock impact** introduced by any of the diffs (clauses 2 and
  3 of [`DEFENSIVE_SCANNING_MANIFESTO.md`](../inspirations/DEFENSIVE_SCANNING_MANIFESTO.md)
  §1 are preserved). `WITH (NOLOCK)`, `_HARD_MAX_SAMPLE`, and the
  `-- Data Boar Compliance Scan` leading comment are intact in every PR
  inspected.

## Methodology (read this before challenging the verdicts)

| Step | What we did                                                                                              |
| ---- | -------------------------------------------------------------------------------------------------------- |
| 1    | `git fetch origin` + `gh pr list --state open` against `FabioLeitao/data-boar` at 2026-04-27 17:00 UTC.   |
| 2    | For each PR: `gh pr view <N> --json` (title, files, mergeStateStatus) and `gh pr checks <N>`.            |
| 3    | For each PR with code under `connectors/`, `core/`, `pro/`, `cli/`: full `git diff origin/main..prN`.    |
| 4    | Classified per protocol thresholds: **Very Low** (typos/docs/logging) → **High** (core infra rewrites). |
| 5    | Applied [`THE_ART_OF_THE_FALLBACK.md`](../inspirations/THE_ART_OF_THE_FALLBACK.md) §3 "diagnostic on fall" — every demoted level (e.g. regex hot path, dependency major bumps) gets a recorded reason, not a silent ack. |
| 6    | Merge-order analysis: identified one **critical interaction** between the security fix (#238) and the doctrinal-comment slice (#232). |

The assessor **did not** run the test suite or build the Rust extension on
this audit branch — that work was already done on each PR's own CI run
(linked above) and the protocol forbids re-pushing. *Test what you fly* still
applies: the PRs we recommend for merge each shipped their own evidence
artefacts (regression tests for #238, single-pass parity tests for #235,
benchmark JSON for #232/#236).

## Critical finding — `main` is currently shipping broken MSSQL SQL

**Severity:** P0 / silent data-loss-grade false negative.
**Affected branch:** `origin/main` — *not* introduced by any open PR.
**RCA path traced through `git blame` is captured in PR #238's body.*

### Evidence (raw diff against `origin/main`)

`origin/main:connectors/sql_sampling.py`, line 329 (function
`_plan_mssql_column_sample`):

```python
opt = f" OPTION (MAX_EXECUTION_TIME = {int(statement_timeout_ms)})"
```

Default connector path resolves `statement_timeout_ms` to **5000 ms** when
the operator does not override it (see
`SQLConnector._connect_args_from_target` → `resolve_statement_timeout_ms_for_sampling`),
so this clause is emitted on **every** SQL Server sampling statement, by
default.

`OPTION (MAX_EXECUTION_TIME = N)` is a **MySQL** optimiser hint syntax. T-SQL
does **not** accept it; SQL Server raises *"Incorrect syntax near
MAX_EXECUTION_TIME"*. The connector's broad `except Exception` block in
`SQLConnector.sample()` catches that error and returns an empty string, so
the scanner reports zero sensitive data on any MSSQL column. The compliance
report claims the database is clean. There is no operator-visible failure
beyond a log warning.

### Why this is a manifesto violation, not just a bug

This pattern is exactly what
[`THE_ART_OF_THE_FALLBACK.md`](../inspirations/THE_ART_OF_THE_FALLBACK.md) §3
("diagnostic on fall — Data Boar never falls through to a weaker level
silently") was written to prevent. The current `main` falls all the way from
"compliance SQL sampling" to "no findings" without an audit row, without a
strategy demotion log entry, and without an operator-visible error. Worst
fail mode: **safe-looking output**.

It is also a violation of
[`DEFENSIVE_SCANNING_MANIFESTO.md`](../inspirations/DEFENSIVE_SCANNING_MANIFESTO.md)
§3 ("dialect-specific posture — do not blur dialects"). The MySQL
`MAX_EXECUTION_TIME` hint was cross-applied to MSSQL without checking the
T-SQL grammar.

### Fix and merge order (the `#238` ↔ `#232` trap)

- **PR #238** removes the bogus `OPTION` clause, keeps the
  `statement_timeout_ms` argument for API parity (audit log still records
  the budget), and adds a regression test that fails if `OPTION` or
  `MAX_EXECUTION_TIME` ever reappears in the MSSQL plan.
- **PR #232** adds doctrinal comments **to the same function** but does
  **not** remove the buggy line. Its diff against `origin/main` is
  comment-only on the docstring and on `resolve_sql_sample_limit`; the
  buggy `opt = …` line is unchanged.
- **Therefore:** if `#232` merges before `#238`, the bug stays in `main`
  with new doctrinal commentary describing how it should not exist. If
  `#238` merges first, `#232` will need a trivial rebase (the comment
  block is in a different region of the file — no logical conflict
  expected).

**Recommended order:** `#238` → `#232` → everything else.

## Per-PR risk table (raw diff is the source of truth)

| PR  | Title (truncated)                                                                                    | Files | +/-       | CI    | Risk      | Verdict                                                       |
| --- | ---------------------------------------------------------------------------------------------------- | ----- | --------- | ----- | --------- | ------------------------------------------------------------- |
| #221 | `deps(pip): bump the pip-minor-patch group across 1 directory with 35 updates`                       | 1     | +1238 / -769 | green | **Medium** | Run `dependabot-resync` from #239 + 2 reviewers.              |
| #222 | `deps(pip): bump chardet from 5.2.0 to 7.4.3`                                                        | 1     | +37 / -3   | green | **Medium** | Major-version on encoding-fallback hot path. Run resync.      |
| #223 | `deps(pip): bump tzdata from 2025.3 to 2026.2`                                                       | 1     | +3 / -3    | green | **Very Low** | Data-only bump. Approve when resynced.                        |
| #224 | `deps(pip): bump cryptography from 46.0.7 to 47.0.0`                                                 | 1     | +50 / -44  | green | **Medium** | Major-version on hazmat / `webauthn`. 2 reviewers + resync.   |
| #226 | `chore(deps): bump pyo3 from 0.23.5 to 0.24.1 in /rust/boar_fast_filter`                            | 2     | +13 / -13  | green | **Low**    | Independent of the pip-resync trap. Approve.                  |
| #232 | `feat(ops,report,detector,plans): doctrine Slices 2-4`                                              | 7     | +447 / -6  | green | **Low***   | Doc + RCA-block edits; *order-of-merge note vs #238 (above)*. |
| #233 | `fix(ci): move SLACK_WEBHOOK_URL guard out of job-level if`                                          | 6     | +150 / -23 | green | **Low**    | YAML-only + tests guard structure. Approve.                   |
| #234 | `docs(ops): SRE security audit of open PRs (2026-04-27)`                                            | 2     | +254 / 0   | green | **Very Low** | Markdown-only audit deliverable. Approve.                     |
| #235 | `perf(detector): Slice 2 — single-pass fused regex`                                                 | 10    | +313 / -74 | green | **Medium** | Hot path, ML stage hop removed. 2 reviewers — bench evidence. |
| #236 | `feat(report) + refactor(detector): Slices 2-4`                                                     | 8     | +602 / -27 | green | **Medium** | Large surface; reporter + worker_logic + new tests. 2 reviewers. |
| #237 | `docs(inspirations): bilingual pt-BR doctrine manifestos`                                           | 12    | +871 / 0   | green | **Very Low** | Markdown + EN/pt-BR pairing only. Approve.                    |
| #238 | `fix(security): drop bogus T-SQL OPTION (MAX_EXECUTION_TIME) on MSSQL sampling`                     | 6     | +37 / -13  | green | **Low**    | **Merge first** — small, narrow, regression-tested. Auto-approve. |
| #239 | `feat(workflow,docs): dependabot-resync helper + SRE Dependency Guardian audit`                     | 4     | +458 / 0   | green | **Low**    | Net-new helper + docs. Approve. *Sequence helper before pip PRs.* |

`*` *Risk Level for #232 stays Low because the **diff itself** is doc/RCA-block
work and does not regress anything; the order-of-merge dependency is captured
in the §"Critical finding" trap above.*

## Per-PR notes (Medium and above)

### #235 — `perf(detector): Slice 2`

- **Why Medium:** rewrites `pro/worker_logic.py::process_chunk_pro` into a
  single fused-regex pass and drops the no-op `deep_ml_analysis` hop on the
  hot path. This is the right doctrinal move per
  [`THE_ART_OF_THE_FALLBACK.md`](../inspirations/THE_ART_OF_THE_FALLBACK.md)
  §2 ("strongest strategy first; one demotion at a time"), and the
  `tests/benchmarks/official_benchmark_200k.json` evidence pins the new
  ratio. But: regex on every row of every customer payload is a 100%-hit
  hot path — any subtle corruption here lands as either *false negatives*
  (compliance blind spot) or *false positives* (operator burnout). Two
  reviewers should re-derive the alternation by hand and confirm the
  named-group `card` semantics match the legacy two-pass behaviour for
  edge cases (Luhn-only-on-card-shape, mixed delimiters, 13–19 digit
  bounds).
- **Database lock impact:** none. Work is purely in-process Python on
  already-sampled rows.

### #236 — `feat(report) + refactor(detector): Slices 2-4`

- **Why Medium:** 602 added lines is a large surface, with overlap on
  `pro/worker_logic.py` (#235) and on `cli/reporter.py` (#232). Specifically,
  `cli/reporter.py` is touched by **#232 (+100/-1)** *and* **#236 (+199/-8)**.
  Same file, different slices, both `MERGEABLE/CLEAN` against `main` —
  but **not** against each other. Whichever merges first will force the
  other into a rebase that should be re-CI'd.
- **Tests added:** `test_basic_python_scan_single_pass_parity.py`,
  `test_cli_reporter_rca.py`. Good coverage.
- Recommend two reviewers; one should focus on the reporter RCA-block
  output shape (operator-visible) and one on the detector parity test.

### #221 / #222 / #224 — Dependabot pip PRs

These are the same systemic finding called out in
[`PR_SECURITY_AUDIT_2026-04-27.md`](PR_SECURITY_AUDIT_2026-04-27.md) (PR
#234) and the dependency-guardian companion
[`PR_SECURITY_AUDIT_2026-04-27_dependency_guardian.md`](PR_SECURITY_AUDIT_2026-04-27_dependency_guardian.md)
(PR #239): Dependabot does not run `uv lock` / `uv export`, so each pip PR
will fail `tests/test_dependency_artifacts_sync.py` until the operator (or
helper script) resyncs. The fix is in PR #239's
`scripts/dependabot-resync.sh` / `scripts/dependabot-resync.ps1`.

- **#222 — `chardet 5 → 7`** is the most sensitive of the three because
  encoding fallback is the third level of
  [`THE_ART_OF_THE_FALLBACK.md`](../inspirations/THE_ART_OF_THE_FALLBACK.md)
  §2 (raw_string heuristics for binary or mixed-encoding payloads). A
  silent semantic change in `chardet` would degrade fallback truthfulness
  without a CI signal.
- **#224 — `cryptography 46 → 47`** changes the surface that hazmat /
  `webauthn` consumers depend on; review against the change log before
  merging.
- **#221 — pip-minor-patch group with 35 updates** is the highest blast
  radius even though each individual bump is minor. Two reviewers, one
  with eyes on transitive surface (e.g. anything in the `pro/` /
  `core/detector*` import graph).

## Recommended action set (in order)

1. **NOW — `#238`.** Auto-approve and merge. This closes the silent
   zero-finding regression on every SQL Server target. No reviewer
   request needed; the diff is 23 net lines, narrow, regression-tested,
   and CI-green.
2. **NEXT — `#234`, `#239`, `#237`, `#233`, `#226`, `#223`, `#232`.**
   These are Very Low / Low and can be approved on the diff alone. `#239`
   should land before any pip Dependabot PR rebase so the helper is
   available to the operator.
3. **THEN — `#221`, `#222`, `#224`.** After `#239` is merged, run
   `scripts/dependabot-resync.sh` (or `.ps1`) on each Dependabot branch,
   request **two reviewers** per PR (one for the `requirements.txt` /
   `uv.lock` resync, one for the dependency change log).
4. **PARALLEL — `#235`, `#236`.** Two reviewers each. Specifically:
   - One reviewer must compare `pr235:pro/worker_logic.py` to `main` and
     confirm the fused-regex semantics match the legacy two-pass loop
     for the `BENCHMARK_EVOLUTION.md` corpus.
   - One reviewer must confirm the `cli/reporter.py` overlap between
     `#232` and `#236` is resolved (rebase the second one to merge,
     re-run CI, then approve).

## Reviewer assignment (per protocol)

The protocol asks for "max 2 reviewers" per PR. The current open repo has
**one** human maintainer (`@FabioLeitao`) and a few CI bots. With one human
in the loop, the practical assignment is:

- **Single reviewer (operator) — Very Low / Low rows:** `#226`, `#223`,
  `#232`, `#233`, `#234`, `#237`, `#238`, `#239`.
- **Single reviewer (operator) + one additional human deferred via
  Slack reply** — Medium rows: `#221`, `#222`, `#224`, `#235`, `#236`.
  When a second reviewer is not available, the protocol requirement
  ("Medium → 2 reviewers") downgrades to **explicit operator
  acknowledgement of the assessor's findings in the PR thread before
  merge**. That operator ack stands in for the missing second pair of
  eyes, *and is recorded in the audit log*; it is **not** a silent
  approval.

This is itself an instance of the manifesto: when you cannot run the
ideal protocol, you record the demotion and proceed with eyes open
(THE_ART_OF_THE_FALLBACK §3).

## Defensive architecture / database impact (zero by construction)

This audit deliverable:

- **Adds no Python code.** The diff is only this file under
  `docs/ops/sre_audits/`.
- **Does not run sampling SQL.** Every observation about
  `connectors/sql_sampling.py` was made by reading the file, not by
  executing a query.
- **Does not touch caps or timeouts.** `_HARD_MAX_SAMPLE = 10_000`,
  `resolve_statement_timeout_ms_for_sampling`, `WITH (NOLOCK)`,
  `_COMPLIANCE_SCAN_LEADING`, and the per-dialect strategy table from
  [`DEFENSIVE_SCANNING_MANIFESTO.md`](../inspirations/DEFENSIVE_SCANNING_MANIFESTO.md)
  §2–§4 are unchanged. PR #238's fix preserves all of the above.

## Doctrine references

- [`docs/ops/inspirations/DEFENSIVE_SCANNING_MANIFESTO.md`](../inspirations/DEFENSIVE_SCANNING_MANIFESTO.md)
  (NASA SEL · Cloudflare · Steve Gibson) — sampling caps, `WITH (NOLOCK)`,
  attribution comment, no `ORDER BY` on auto-sampling.
- [`docs/ops/inspirations/THE_ART_OF_THE_FALLBACK.md`](../inspirations/THE_ART_OF_THE_FALLBACK.md)
  (Usagi Electric · The 8-Bit Guy) — strategy demotion must be logged;
  do not skip levels; never fall through silently.
- [`docs/ops/inspirations/SUPPLY_CHAIN_AND_TRUST_SIGNALS.md`](../inspirations/SUPPLY_CHAIN_AND_TRUST_SIGNALS.md)
  — SBOM ↔ `uv.lock` ↔ `requirements.txt` alignment for every pip bump.
- [`PR_SECURITY_AUDIT_2026-04-27.md`](PR_SECURITY_AUDIT_2026-04-27.md) and
  [`PR_SECURITY_AUDIT_2026-04-27_dependency_guardian.md`](PR_SECURITY_AUDIT_2026-04-27_dependency_guardian.md)
  — earlier passes from the same Slack-triggered protocol; this one extends
  them with explicit risk classification + reviewer assignment.

## Reproducer (so the next assessor pass can re-derive these verdicts)

```bash
git fetch origin
gh pr list --state open --limit 50 --json number,title,additions,deletions,changedFiles,mergeable,mergeStateStatus
for pr in 221 222 223 224 226 232 233 234 235 236 237 238 239; do
  gh pr checks "$pr"
  gh pr view "$pr" --json files,baseRefOid,headRefOid
done
git fetch origin pull/238/head:pr238
git diff origin/main..pr238 -- connectors/sql_sampling.py
git fetch origin pull/232/head:pr232
git diff origin/main..pr232 -- connectors/sql_sampling.py
git show origin/main:connectors/sql_sampling.py | grep -n "MAX_EXECUTION_TIME"
```

The `OPTION (MAX_EXECUTION_TIME = …)` line on `origin/main` is the
falsifiable evidence behind the Critical finding above. If a future audit
runs these commands and the line is **gone**, the regression is closed and
this section can be archived.
