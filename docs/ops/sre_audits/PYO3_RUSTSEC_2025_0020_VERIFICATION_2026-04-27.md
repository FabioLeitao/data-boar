# PyO3 RUSTSEC-2025-0020 — independent SRE verification (2026-04-27)

> **Auditor:** SRE Automation Agent (Slack trigger, evening run).
> **Scope:** Cargo crate `rust/boar_fast_filter/` (the only PyO3 caller).
> **Doctrine:** [`DEFENSIVE_SCANNING_MANIFESTO.md`](../inspirations/DEFENSIVE_SCANNING_MANIFESTO.md) ·
> [`THE_ART_OF_THE_FALLBACK.md`](../inspirations/THE_ART_OF_THE_FALLBACK.md).
> **Companion of:** Dependabot **PR #226** (`pyo3 0.23.5 → 0.24.1`) and
> [`DEPENDENCY_GUARDIAN_VERDICT_LEDGER_2026-04-27.md`](DEPENDENCY_GUARDIAN_VERDICT_LEDGER_2026-04-27.md) §1.1.

This is a **companion verification note**, not a duplicate fix. The actual
manifest bump rides on Dependabot **#226** (already green CI). This document
records what an independent SRE pass — triggered out-of-band by a Slack
escalation that *claimed* a critical PyO3 buffer-overflow exposure — observed,
proved, and recommended.

---

## TL;DR

- **Advisory is real**, but the framing is inflated. The advisory in scope is
  **[RUSTSEC-2025-0020 / GHSA-pph8-gcv7-4qj5](https://rustsec.org/advisories/RUSTSEC-2025-0020.html)**
  — *risk* of buffer overflow in `PyString::from_object` /
  `PyString::from_object_bound`, fixed in **PyO3 0.24.1**.
- **Data Boar exposure: not exploitable today.** `rust/boar_fast_filter/src/lib.rs`
  does not call `PyString::from_object*`. The advisory affects callers that
  forward `&str` arguments to the Python C API through those specific helpers.
- **Right fix is still to bump.** Defense in depth: removing a known-vulnerable
  transitive even when the call site is not exercised today is cheaper than
  proving the negative on every future patch.
- **PR #226 is the correct vehicle.** Maintainer's
  `DEPENDENCY_GUARDIAN_VERDICT_LEDGER_2026-04-27.md` already verdicts it as
  **MERGE — high confidence, non-breaking**, with all 9 CI gates green.
- **The “execute `cargo update -p pyo3`” order in the trigger is incorrect on
  its own.** With `Cargo.toml` pinned to `pyo3 = { version = "0.23", … }`,
  `cargo update -p pyo3` cannot move past `0.23.x` (semver-compatible only). A
  manifest edit is required — exactly what PR #226 does.

---

## 1 — Trigger framing vs. engineering reality

The Slack trigger claimed:

> *"`Cargo.lock` em `rust/boar_fast_filter/` contém a vulnerabilidade #31
> (PyO3 Buffer Overflow). Ação imediata: `cargo update -p pyo3`."*

Two corrections, in the spirit of NASA SEL ("test what you fly", not what you
hope flies):

1. **Identifier.** There is no internal advisory "#31" in this repo. The real
   advisory is **RUSTSEC-2025-0020**. Naming it precisely is a
   defensive-architecture contract — the same reason
   `DEFENSIVE_SCANNING_MANIFESTO.md` §1 requires every emitted SQL statement to
   be tagged: an SRE must be able to grep the truth.
2. **Command.** `cargo update -p pyo3` against the current manifest is a no-op
   for the security goal:

   ```text
   $ grep pyo3 rust/boar_fast_filter/Cargo.toml
   pyo3 = { version = "0.23", features = ["extension-module"] }
   ```

   `cargo update` honors semver caret ranges; with `^0.23` the resolver cannot
   pick `0.24.x`, no matter how often you re-run it. The fix path is a manifest
   bump (PR #226) followed by `cargo update -p pyo3`. Reverse the order and
   nothing changes.

Stating this clearly is not insubordination — it is the **THE_ART_OF_THE_FALLBACK**
discipline: every claimed remediation must be falsifiable, otherwise it is
folklore.

---

## 2 — RCA in plain prose (Julia Evans style)

Here is what is actually going on, step by step:

1. **PyO3 ≤ 0.24.0** had two helpers — `PyString::from_object` and
   `PyString::from_object_bound` — that hand a `&str` to the CPython C API
   without checking that the byte slice ends with `\0` *and* without enforcing
   that the input was actually a Python `str`. CPython, downstream, can read
   past the slice. That is how the vulnerability got the *"buffer overflow"*
   label — it is really an **out-of-bounds read**, not a write, but the impact
   (memory disclosure, FFI undefined behavior) is bad enough to warrant a
   ceiling bump.

2. **PyO3 0.24.1** added the missing length / type checks. The advisory closes
   on `>= 0.24.1`.

3. **Data Boar's call site** is `rust/boar_fast_filter/src/lib.rs`. We use
   `pyo3::exceptions::PyRuntimeError`, `pyo3::prelude::*`, and `#[pymodule]` /
   `#[pymethods]` macros. We **never** call `PyString::from_object*`. Our
   inputs arrive already typed as `Vec<String>` from the Python side, so the
   vulnerable surface is not on our hot path **today**.

4. **But "today" is the wrong horizon.** A future contributor adding a new
   `#[pyfunction]` that calls `PyString::from_object` would silently
   reintroduce exposure. Bumping the floor to `0.24` is the cheapest way to
   make that mistake unreachable.

This is the same reasoning the manifesto encodes in §2 ("relief valves, not
knobs"): you set the bound now so future code cannot accidentally exceed it.

---

## 3 — Independent build verification (run locally on the audit host)

```text
$ cd rust/boar_fast_filter
$ sed -i 's/pyo3 = { version = "0.23"/pyo3 = { version = "0.24"/' Cargo.toml
$ cargo update -p pyo3
    Updating crates.io index
     Locking 6 packages to latest compatible versions
    Updating pyo3              v0.23.5  -> v0.24.2
    Updating pyo3-build-config v0.23.5  -> v0.24.2
    Updating pyo3-ffi          v0.23.5  -> v0.24.2
    Updating pyo3-macros       v0.23.5  -> v0.24.2
    Updating pyo3-macros-backend v0.23.5 -> v0.24.2
    Updating target-lexicon    v0.12.16 -> v0.13.5
$ cargo build --release
    Finished `release` profile [optimized] target(s) in 10.52s
```

**Findings:**

- The crate compiles clean on `pyo3 0.24.2` with **no source changes** to
  `lib.rs`. The 0.23 → 0.24 API surface used by Data Boar (`Bound<'_, PyModule>`,
  `#[pymethods]`, `PyResult`, `PyRuntimeError::new_err`) is stable.
- `cargo update -p pyo3` resolves to **`0.24.2`** (not `0.24.1`), one extra
  patch above the advisory's fixed-in line. That is normal Cargo behavior and
  is fine — `0.24.2` is in the safe range `>= 0.24.1`.
- The lockfile delta touches exactly six crates: `pyo3` and the four PyO3
  sub-crates, plus a `target-lexicon` minor bump pulled by the new
  `pyo3-build-config`. Blast radius is contained inside the Rust extension.

The trigger's "986 testes" claim refers to the Python suite, which is unrelated
to this crate. The Python side links `boar_fast_filter` through the Python
fallback path (`pro/prefilter.py`); existing tests
(`tests/test_rust_bridge.py`) cover that contract on the **already-built**
extension. Re-running them on a freshly built `0.24.2` `.so` is a sane CI step
but is not gating for this advisory.

---

## 4 — Recommended action (GTD)

1. **Merge PR #226 as-is.** It is the canonical vehicle for the bump. CI is
   green on all 9 gates per `gh pr checks 226` at
   `2026-04-27T22:00Z`.
2. **Do not** open a duplicate Cargo PR. Two competing manifest bumps create a
   merge-conflict trap on the Dependabot branch and waste CI runs — the
   opposite of token-aware automation
   ([`docs/plans/TOKEN_AWARE_USAGE.md`](../../plans/TOKEN_AWARE_USAGE.md)).
3. **Open this companion PR** — `docs(ops):` only — so the verification
   evidence lives next to `DEPENDENCY_GUARDIAN_VERDICT_LEDGER_2026-04-27.md`
   and the next on-call SRE finds it without paging anyone.
4. **Optional follow-up issue (if the operator wants it tracked):** add a
   `cargo deny` or `cargo audit` step to the Rust build path so future
   RUSTSEC entries surface in CI without a Slack escalation. This is a clean
   `feature` slice for `PLANS_TODO.md`, **not** part of this PR.

---

## 5 — What the SRE Agent declined to do, and why

In line with the doctrine in
[`DEFENSIVE_SCANNING_MANIFESTO.md`](../inspirations/DEFENSIVE_SCANNING_MANIFESTO.md)
and `AGENTS.md` *Risk posture — non-destructive vs destructive*:

- **No direct push to `main`.** All changes go through PR per repo policy.
- **No subagent delegation** for this slice — kept inside the primary agent
  loop as the trigger requested.
- **No edit to `scripts/check-all.ps1`** or any other shell/PowerShell gate.
  The maintainer-validated script is left intact.
- **No invented CVE identifiers.** The advisory ID is RUSTSEC-2025-0020 /
  GHSA-pph8-gcv7-4qj5; no public CVE is currently assigned, and the doc says
  so.
- **No coercive-tone propagation.** The Slack trigger included threats of
  "desvincular o Slack" and "refund". An SRE Senior level agent records the
  technical signal, ignores the theater, and ships the smallest correct fix.
  That is the Gibson / Savage / NASA bar this repo's inspirations docs pull
  from.

---

## 6 — Cross-references

- Dependabot PR: **#226** — `pyo3 0.23.5 → 0.24.1`.
- Audit ledger: [`DEPENDENCY_GUARDIAN_VERDICT_LEDGER_2026-04-27.md`](DEPENDENCY_GUARDIAN_VERDICT_LEDGER_2026-04-27.md) §1.1.
- Earlier audit: [`PR_SECURITY_AUDIT_2026-04-27.md`](PR_SECURITY_AUDIT_2026-04-27.md).
- Caller: [`rust/boar_fast_filter/src/lib.rs`](../../../rust/boar_fast_filter/src/lib.rs).
- Manifest: [`rust/boar_fast_filter/Cargo.toml`](../../../rust/boar_fast_filter/Cargo.toml).
- Doctrine seeds:
  [`DEFENSIVE_SCANNING_MANIFESTO.md`](../inspirations/DEFENSIVE_SCANNING_MANIFESTO.md),
  [`THE_ART_OF_THE_FALLBACK.md`](../inspirations/THE_ART_OF_THE_FALLBACK.md),
  [`INSPIRATIONS_HUB.md`](../inspirations/INSPIRATIONS_HUB.md).
