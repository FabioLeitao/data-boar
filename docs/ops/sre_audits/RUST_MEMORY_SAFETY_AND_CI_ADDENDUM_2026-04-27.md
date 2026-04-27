# Rust memory safety + CI evidence — addendum to the 2026-04-27 ledger

> **Slack-triggered SRE Automation Agent re-evaluation pass** for the
> 2026-04-27 dated ledger. The trigger explicitly asked for a deeper look at
> **Rust memory safety** and **complex CI logic**. This file is an
> **addendum** — it does **not** rewrite
> [`DEPENDENCY_GUARDIAN_VERDICT_LEDGER_2026-04-27.md`](DEPENDENCY_GUARDIAN_VERDICT_LEDGER_2026-04-27.md)
> (that one is a dated snapshot per the
> [`README.md`](README.md) "decisions, never mechanism" rule).
>
> Form is borrowed from the LMDE bug-fix ledger style: one RCA per row, no
> rhetoric, evidence inline.

---

## 0 — TL;DR

The original ledger's **verdict on PR #226 (`pyo3 0.23.5 → 0.24.1`) is
unchanged: MERGE.** What was thin was the **basis** of that verdict — it
relied on "we don't call `PyString::from_object`" as the safety case, which is
necessary but not sufficient for an extension module on the detector hot path.

Three audit gaps booked here, none of them blocking #226:

| #   | Gap                                                                                  | Severity | Action vehicle                                  |
| :-- | :----------------------------------------------------------------------------------- | :------- | :---------------------------------------------- |
| A1  | Memory-safety case did not enumerate the `Bound<'py, T>` API surface.                | Low      | This addendum (§1.1) — verdict unchanged.       |
| A2  | `Send + Sync` posture under freethreaded CPython 3.13t not stated for `FastFilter`.  | Low–Med  | Follow-up issue (proposed §3) — `frozen` opt-in. |
| A3  | No `cargo test` / `cargo clippy` evidence on `main` at audit time.                   | Medium   | **Already in flight as PR #255** — sequence it ahead of any further Rust touch. |

**No new commit on the `dependabot/cargo/...` branch.** Audit-and-block.

---

## 1 — Memory-safety re-audit (PR #226 lens)

### 1.1 — `Bound<'py, T>` API surface vs our usage (gap A1)

PyO3 0.23 introduced the `Bound<'py, T>` smart pointer; 0.24 finalises it.
Looking at `rust/boar_fast_filter/src/lib.rs` at `91b0f29` (audit HEAD):

```84:88:rust/boar_fast_filter/src/lib.rs
#[pymodule]
fn boar_fast_filter(_py: Python<'_>, m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_class::<FastFilter>()?;
    Ok(())
}
```

* `&Bound<'_, PyModule>` is the **0.23+** signature — this code is already on
  the new lifetime-aware reference type. There is **no** `Py<PyModule>` /
  `&PyModule` (deprecated) call site.
* `#[pyclass]` `FastFilter` exposes one `#[new]` and one `&self` method
  (`filter_batch`). Neither hands a Python reference back across the FFI
  boundary — they take `Vec<String>` (owned, by-value into Rust) and return
  `PyResult<Vec<usize>>` (POD). **No GIL-attached pointer escapes the call.**
* `Regex::new(...)` is the only fallible step at construction; it returns
  `regex::Error` and is mapped to `PyRuntimeError` *before* the `pyclass`
  instance is materialised — the partially-constructed-object footgun PyO3
  0.23 changelogs warned about does not apply here.

**Verdict (unchanged):** PyO3 0.24's tightened `Bound`-API rules and the
`PyString::from_object` UB advisory both **miss our call paths**. MERGE for
#226 stands.

### 1.2 — Panic-free posture

The detector hot path runs `filter_batch` from Python under GIL; a Rust panic
would unwind into the FFI boundary and be re-raised as `PanicException` —
recoverable, but a hot-path panic is exactly what NASA SEL §1 *test what you
fly* prohibits. Reading the implementation:

* `cpf_pattern.is_match(content)` / `email_pattern.is_match(content)` —
  total functions on `&str`.
* `credit_card_pattern.find_iter(content)` — iterator, no slice indexing.
* `Self::check_luhn(card_number)` — uses `chars().filter_map(|c| c.to_digit(10))`
  (option-returning, no `unwrap`); arithmetic is bounded `u32` digit math
  (no overflow risk on the 13–19 digit window).

**No `unwrap` / `expect` / `panic!` / array-index slicing on dynamic data.**
The comment "Panic-free by design" on `lib.rs:32` matches the implementation;
no regression in #226's diff.

### 1.3 — `unsafe` blocks

`rg "unsafe" rust/boar_fast_filter/src` → 0 matches. The crate is
`#![forbid(unsafe_code)]`-eligible (we don't set it explicitly today; see §3
follow-up).

---

## 2 — `Send + Sync` posture under freethreaded CPython (gap A2)

PEP 703 / CPython 3.13t make freethreaded interpreters a real deployment
target. PyO3 0.23+ requires `#[pyclass]` types to be `Sync` for cross-thread
sharing **without** the GIL. Our `FastFilter`:

```5:11:rust/boar_fast_filter/src/lib.rs
#[pyclass]
pub struct FastFilter {
    cpf_pattern: Regex,
    email_pattern: Regex,
    credit_card_pattern: Regex,
}
```

* `regex::Regex` is `Send + Sync` — the auto-derived bound holds.
* All three fields are set once in `#[new]` and never mutated thereafter.

The class is **already** semantically immutable, but the type system does
**not** record that intent. Two consequences:

1. A future contributor could add a `&mut self` method and silently lose the
   freethreaded-safe property.
2. Without `#[pyclass(frozen)]`, PyO3 still inserts a `RefCell`-equivalent
   borrow check at every `&self` call — small CPython 3.13t overhead on the
   hot path that the detector benchmark in
   [`docs/plans/BENCHMARK_EVOLUTION.md`](../../plans/BENCHMARK_EVOLUTION.md)
   would measure.

**Recommendation (not in this audit's scope; tracked as follow-up):** open
an issue *after* PR #255 lands so we have a `cargo test` baseline, then add
`#[pyclass(frozen)]` plus a `Sync` bound assertion. Defer until the CI
gate exists.

This satisfies the **diagnostic-on-fall** clause of
[`THE_ART_OF_THE_FALLBACK.md`](../inspirations/THE_ART_OF_THE_FALLBACK.md)
§4 — we are recording a known posture gap with evidence rather than letting
it die in chat.

---

## 3 — CI evidence sequencing (gap A3 — the "complex CI logic" axis)

The original ledger called PR #226 "all green (Test 3.12 / 3.13 / Lint /
Bandit / Semgrep / CodeQL / SonarQube / Dependency audit / SBOM / Analyze)"
and that is true — **but every one of those jobs is Python-side**.

`ls .github/workflows/` at `91b0f29`:

```
ci.yml  codeql.yml  sbom.yml  semgrep.yml  slack-*.yml
```

There is **no Rust workflow on `main`**. A `pyo3` bump on a Rust crate that
ships as a CPython extension and lives on the detector hot path is therefore
audited under a CI rubric that never builds the crate. That is the kind of
silent gap NASA SEL would call a *negative test that doesn't exist*.

**Mitigation already in flight:** PR #255
(`ci(rust): GitHub Actions for boar_fast_filter + unit tests`) adds
`cargo check` + `cargo test` + `cargo clippy --all-targets --all-features --
-D warnings` and wires Slack failure-notify to include the new workflow.

**Recommended sequence (handed back to the maintainer):**

1. Land **PR #255** first — it costs us nothing on `main` (it's additive
   workflow + a test-only Rust refactor) and converts every future Rust bump
   from "Python-side smoke only" to "real Rust evidence".
2. Then merge **PR #226**. The verdict is unchanged, but the *basis* will
   include real `cargo test` + `cargo clippy` evidence.
3. The cryptography / chardet / tzdata / pip-group sequence from
   [§4 of the original ledger](DEPENDENCY_GUARDIAN_VERDICT_LEDGER_2026-04-27.md#4--recommended-merge-order-handed-back-to-the-maintainer)
   is **unchanged** — none of them touch the Rust crate.

This re-orders the original §4 by **inserting #255 between #226 and #239**;
it does **not** invalidate the per-PR verdicts.

---

## 4 — Defensive-architecture re-statement (mandatory protocol gate)

Per the trigger ("ZERO impact on database locks; no regressions"), the
re-evaluation produced **no new evidence** that any of the audited PRs
touch the customer-DB contract:

* PR #226 is Cargo-only — cannot influence `WITH (NOLOCK)` / sampling /
  isolation level / DDL.
* The Rust crate itself does not link any DB driver — `Cargo.toml` lists
  `pyo3` and `regex` only.
* The `frozen`-class follow-up (§2) is an internal posture change to the
  detector prefilter; it does not cross the customer-DB boundary.

`DEFENSIVE_SCANNING_MANIFESTO.md` §1 clauses 1–4 still hold for every PR
re-audited here.

---

## 5 — Why this is an addendum, not a v2 of the ledger

The `README.md` of this folder (line 8) is explicit: *"only the **decisions**
live here … the helper can evolve without invalidating the dated verdicts."*
The same logic applies in reverse: a re-audit that **adds reasoning** without
flipping any verdict belongs in a separate dated file so the original ledger
remains a clean snapshot of what was known at trigger time. This is the
[`THE_ART_OF_THE_FALLBACK.md`](../inspirations/THE_ART_OF_THE_FALLBACK.md)
§4 *diagnostic-on-fall* posture applied to documentation: append, don't
overwrite.

---

## 6 — Provenance

* **Trigger:** Slack automation **2026-04-27**, channel `C0AN7HY3NP9`,
  thread `1777318102.608069`. The trigger asked for a re-evaluation under a
  Rust-memory-safety + CI lens.
* **Re-audit HEAD:** `606435b` (`main` after PR #242 merge — same workspace
  the original ledger ran on, plus its own merge commit).
* **PRs re-examined:** #226 (pyo3, primary lens). #221 / #222 / #223 / #224
  unaffected by the Rust lens — verdicts unchanged.
* **CI surface check:** `ls .github/workflows/` at the re-audit HEAD; no
  `rust-ci.yml` on `main`. PR #255 carries the proposed addition.
* **Audit-and-block respected:** **no commit pushed to any audited
  Dependabot branch** (#221, #222, #223, #224, #226) — same posture as the
  original ledger.

## 7 — Doctrine references

* [`DEFENSIVE_SCANNING_MANIFESTO.md`](../inspirations/DEFENSIVE_SCANNING_MANIFESTO.md)
  — §1 clauses 1–4 acceptance gate.
* [`THE_ART_OF_THE_FALLBACK.md`](../inspirations/THE_ART_OF_THE_FALLBACK.md)
  — §4 *diagnostic-on-fall* applied to the documentation surface itself.
* [`DEPENDENCY_GUARDIAN_VERDICT_LEDGER_2026-04-27.md`](DEPENDENCY_GUARDIAN_VERDICT_LEDGER_2026-04-27.md)
  — the dated ledger this addendum extends.
* [ADR 0005](../../adr/0005-ci-github-actions-supply-chain-pins.md) —
  audit-and-block posture.
