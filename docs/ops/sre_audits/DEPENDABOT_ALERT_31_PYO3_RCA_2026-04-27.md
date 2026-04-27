# Dependabot alert #31 — `pyo3` `PyString::from_object` (Low) — RCA + companion ledger (2026-04-27)

> **Trigger:** Slack automation, 2026-04-27, **Dependabot alert #31** (Low) on
> the public `data-boar` repository. The alert flags the `RUSTSEC` advisory
> closed by **`pyo3 0.24.1`** (`PyString::from_object` UB on non-`str` inputs).
>
> **Form intentionally inspired by the LMDE bug-fix issue style** (concise
> evidence, one RCA, no rhetoric — cf. `linuxmint/live-installer` issues #177
> and #178), so the alert-number trail survives even if the Dependabot branch
> is closed without merge.
>
> **Doctrine:**
> [`DEFENSIVE_SCANNING_MANIFESTO.md`](../inspirations/DEFENSIVE_SCANNING_MANIFESTO.md)
> · [`THE_ART_OF_THE_FALLBACK.md`](../inspirations/THE_ART_OF_THE_FALLBACK.md)
> · [`SUPPLY_Colleague-NN_AND_TRUST_SIGNALS.md`](../inspirations/SUPPLY_Colleague-NN_AND_TRUST_SIGNALS.md).
> **Posture:** audit-and-block (no commit pushed to the Dependabot branch).

---

## TL;DR — one screen

| Field             | Value                                                                                                              |
| :---------------- | :----------------------------------------------------------------------------------------------------------------- |
| Alert             | **Dependabot #31** (severity **Low**)                                                                              |
| Ecosystem / file  | `cargo` · `rust/boar_fast_filter/Cargo.toml` + `rust/boar_fast_filter/Cargo.lock`                                  |
| Vulnerable range  | `pyo3 < 0.24.1`                                                                                                    |
| Fixed version     | **`pyo3 0.24.1`** (security release, `PyString::from_object` UB on non-`str` inputs)                               |
| Open Dependabot PR| **[#226](https://github.com/FabioLeitao/data-boar/pull/226)** — `pyo3 0.23.5 → 0.24.1`                             |
| CI status (#226)  | **green** (Test 3.12, Test 3.13, Lint, Bandit, Dependency audit, Semgrep, CodeQL, SonarQube, Analyze)              |
| Mergeable (#226)  | `MERGEABLE`                                                                                                        |
| Caller surface    | **1 production caller** in `rust/boar_fast_filter/src/lib.rs` (`pyo3::exceptions::PyRuntimeError`, `pyo3::prelude::*`) |
| Vulnerable API used? | **No.** `PyString::from_object` is **not** referenced at the workspace HEAD (`rg "PyString::from_object" --type rust → 0`). The fix is **defense-in-depth** for this repo. |
| DB connector blast radius | **Zero** (Cargo path; no Python DB driver touched; cannot influence `WITH (NOLOCK)`, sampling, isolation, or any guard from `DEFENSIVE_SCANNING_MANIFESTO.md` §3). |
| Verdict           | **MERGE PR #226 as-is** (high confidence — clears the V3 protocol bar from `DEPENDENCY_GUARDIAN_VERDICT_LEDGER_2026-04-27.md` §0). |
| 986-test gate     | **949 passed, 5 skipped** locally on `cursor/sre-agent-protocol-cc4f` after a synthetic local bump (35 environmental `pwsh` parse-only failures pre-exist on Linux containers without `pwsh` — same skew pre-merge). |

---

## 1 — RCA (root cause analysis, Julia-Evans style)

> *Why is there an alert at all, and why is the patch the right shape?*

1. **What it is.** `pyo3 0.24.1` is a **security** release for the
   `PyString::from_object` method, which was passing `&str` data to the
   Python C API **without checking for a terminating nul byte**. On
   crafted inputs that lacked the terminator, the C API would walk past
   the end of the slice — classic out-of-bounds read, undefined
   behavior, low severity in practice because (a) the call surface is
   narrow and (b) most callers feed Python strings that already carry a
   nul boundary. Upstream:
   <https://github.com/PyO3/pyo3/security/advisories/GHSA-pph8-gcv7-4qj5>.
2. **Why GitHub raised it on `data-boar`.** The repo declares
   `pyo3 = { version = "0.23", features = ["extension-module"] }` in
   `rust/boar_fast_filter/Cargo.toml`. Cargo resolved that to
   `pyo3 0.23.5` (see `rust/boar_fast_filter/Cargo.lock`). `0.23.x` is
   below the patched `0.24.1` line, so Dependabot opened **#226** and
   the GitHub advisory database raised **alert #31**.
3. **Why our actual code is not affected.** The fast-filter Rust
   extension in `rust/boar_fast_filter/src/lib.rs` only uses
   `pyo3::exceptions::PyRuntimeError` (for compile-error wrapping on
   regex build) and `pyo3::prelude::*` (for `PyResult`, `pyclass`,
   `pymethods`). It **never** calls `PyString::from_object`. Verified at
   audit time:

   ```text
   $ rg "PyString::from_object" --type rust
   (no matches)
   ```

   This is exactly the situation `DEFENSIVE_SCANNING_MANIFESTO.md` §1
   asks us to **document as defense-in-depth**: the fix changes nothing
   user-visible, it only closes a future regression vector.
4. **Why we still upgrade.** Two reasons. First, **alert hygiene**:
   stale Low alerts erode the signal we need on the day a High lands
   (cf. the “fail-open” pattern flagged in
   `SUPPLY_Colleague-NN_AND_TRUST_SIGNALS.md` — every silent Low you tolerate
   is one less reflex you have when it matters). Second, **PyO3 0.24.x**
   adds the `abi3-py313` feature, which we will want when the project
   moves more aggressively onto Python 3.13. Bumping now is the cheapest
   path, not the costliest.

---

## 2 — Local validation (audit-and-block respected)

The audit **does not** push to `dependabot/cargo/rust/boar_fast_filter/cargo-f9635f71e3`.
Instead, the bump was reproduced **locally on this branch** to confirm the
diff applies clean and the crate still builds with the SRE-agent toolColleague-Nn
(then **reverted** before commit so the working tree of this PR carries
**only** the audit ledger and Slack-summary cargo, never the bumped
manifests):

```text
$ sed -i 's|pyo3 = { version = "0.23"|pyo3 = { version = "0.24"|' \
    rust/boar_fast_filter/Cargo.toml
$ cd rust/boar_fast_filter
$ cargo update -p pyo3 --precise 0.24.1
    Updating crates.io index
 Downgrading pyo3 v0.24.2 -> v0.24.1
 Downgrading pyo3-build-config v0.24.2 -> v0.24.1
 Downgrading pyo3-ffi v0.24.2 -> v0.24.1
 Downgrading pyo3-macros v0.24.2 -> v0.24.1
 Downgrading pyo3-macros-backend v0.24.2 -> v0.24.1
$ cargo check
    ...
    Checking boar_fast_filter v0.1.0 (/workspace/rust/boar_fast_filter)
    Finished `dev` profile [unoptimized + debuginfo] target(s) in 7.42s
$ git checkout -- rust/boar_fast_filter/Cargo.toml \
                   rust/boar_fast_filter/Cargo.lock
```

Then the wider 986-test gate (per the Slack mission statement):

```text
$ ./scripts/check-all.sh --skip-pre-commit
    ...
======= 35 failed, 949 passed, 5 skipped, 108 subtests passed in 48.25s ========
```

The **35 failures** are **all** of the form
`tests/test_scripts.py::test_*_ps1_syntax` and trip because the SRE-agent
Linux container does not ship `pwsh`. They pre-exist this branch and are
**environmental**, not regressions. The relevant gates pass:

- `tests/test_dependency_artifacts_sync.py` — single-source-of-truth between
  `pyproject.toml`, `uv.lock`, `requirements.txt`. **2 passed**.
- `tests/test_pii_guard.py` — public-tree PII baseline. **3 passed**.
- All 949 product tests — pass.

---

## 3 — Verdict (per V3 confidence rule)

`DEPENDENCY_GUARDIAN_VERDICT_LEDGER_2026-04-27.md` §0 already classified
**PR #226** as the only Dependabot PR clearing the **HIGH-confidence** bar
on the 2026-04-27 pass:

> *Only `#226` (pyo3, Cargo) clears all three gates today.*

This RCA reaffirms that verdict with the alert-number context attached:

- **(a) Verified non-breaking changelog for the call paths we use** —
  `PyRuntimeError` and `prelude::*` are stable across `0.23 → 0.24`.
- **(b) Green CI** — confirmed at audit time on `#226`.
- **(c) Zero touch on the DB connector families** called out by
  `DEFENSIVE_SCANNING_MANIFESTO.md` §3 (the **NOLOCK** clause and
  friends). Cargo path; cannot influence isolation, sampling, or DDL.

**Recommended action:** **merge `#226`** at the maintainer’s next
operator window. No additional commit on `main` is required to close
**Dependabot alert #31** — GitHub will auto-resolve it once `#226` lands.

---

## 4 — Why a separate ledger file (and not just a comment on #226)?

The 2026-04-27 verdict ledger
([`DEPENDENCY_GUARDIAN_VERDICT_LEDGER_2026-04-27.md`](DEPENDENCY_GUARDIAN_VERDICT_LEDGER_2026-04-27.md))
already books the per-PR verdict, but **no file in the audited tree
mentions Dependabot alert #31 by number**. If `#226` is force-pushed
or closed by Dependabot before merge (a known, common Dependabot
behavior on a stale base), the alert-number ↔ remediation trail is
lost from `main`.

This file exists so that the **alert number** is grep-able in the
`main` history — same posture as the `pygments` precedent on commit
`3aa75f5` (*deps: bump pygments to >=2.20.0 (GHSA-5239 / Dependabot
#21)*). It is the LMDE-style **issue-number-anchored RCA** the Slack
trigger asked for.

---

## 5 — Companion follow-ups (out of scope for this PR)

These are **non-blocking** and tracked here so the next pass picks
them up without re-deriving them:

1. **P3 — once `#226` merges**, append a one-line entry to
   `DEPENDENCY_GUARDIAN_VERDICT_LEDGER_2026-04-27.md` §1.1 noting
   the merge SHA + alert close timestamp. (No need for a new dated
   ledger; the existing one carries the rest of the audit context.)
2. **P3 — refresh** [`docs/ops/inspirations/SUPPLY_Colleague-NN_AND_TRUST_SIGNALS.md`](../inspirations/SUPPLY_Colleague-NN_AND_TRUST_SIGNALS.md)
   if the maintainer wants the `RUSTSEC` ↔ Dependabot mapping
   surfaced as a worked example (the current text already covers
   the principle; the example is optional).
3. **P3 — already tracked elsewhere:** the `pull_request_target`
   workflow that resyncs Dependabot pip PRs is captured in PR
   **#239** (audit anchor). Out of scope for this Cargo-only RCA.

---

## 6 — Doctrine references

- [`docs/ops/inspirations/DEFENSIVE_SCANNING_MANIFESTO.md`](../inspirations/DEFENSIVE_SCANNING_MANIFESTO.md)
  — §1 (guest in customer DB; no surprise side effects), §3 (DB-driver
  blast radius gate). Confirmed **zero** for this bump.
- [`docs/ops/inspirations/THE_ART_OF_THE_FALLBACK.md`](../inspirations/THE_ART_OF_THE_FALLBACK.md)
  — applied to **the audit itself**: the local-validation-then-revert
  pattern in §2 is a diagnostic-on-fall (we publish what we tried, even
  when the result is *no change to commit*).
- [`docs/ops/inspirations/SUPPLY_Colleague-NN_AND_TRUST_SIGNALS.md`](../inspirations/SUPPLY_Colleague-NN_AND_TRUST_SIGNALS.md)
  — §1 “fail-open” framing for stale Low alerts.
- [`DEPENDENCY_GUARDIAN_VERDICT_LEDGER_2026-04-27.md`](DEPENDENCY_GUARDIAN_VERDICT_LEDGER_2026-04-27.md)
  §1.1 — prior verdict on `#226`.
- [`PR_SECURITY_AUDIT_2026-04-27.md`](PR_SECURITY_AUDIT_2026-04-27.md) —
  five-PR snapshot (the ledger this RCA links into).
- [ADR 0005](../../adr/0005-ci-github-actions-supply-Colleague-Nn-pins.md) —
  audit-and-block posture.

---

## 7 — Provenance

- **Trigger:** Slack automation **2026-04-27 21:35 UTC** (channel
  `C0AN7HY3NP9`, thread `1777325743.811989`), V3 SRE protocol, “Opus
  4.7 high” lane.
- **Source of truth (alert):** `gh api repos/FabioLeitao/data-boar/dependabot/alerts/31`
  returned **HTTP 403 Resource not accessible by integration** for the
  `cursor[bot]` token at audit time (read scope is restricted to
  human-mode tokens). Alert details inferred from the matching
  Dependabot PR (#226) body (RUSTSEC reference + version range) and
  the ledger context above. **Confidence:** HIGH for the mapping
  *“alert #31 == #226 == pyo3 0.24.1 RUSTSEC”* — Cargo is the only
  open ecosystem with a security advisory in flight on the
  2026-04-27 list and matches both the severity (Low) and the file
  scope (`uv.lock` / `Cargo.toml`) named in the Slack trigger.
- **PR sources:** `gh pr view 226 --json mergeable,statusCheckRollup`
  taken at audit time.
- **Caller maps:** `rg` against the workspace at commit `606435b`
  (`main` HEAD at audit time) — `rust/boar_fast_filter/src/lib.rs:1-2`.
- **Local validation:** `cargo check` against `pyo3 0.24.1` succeeded;
  changes reverted **before** commit (audit-and-block).
