# Dependabot alert #31 — reconciliation against RUSTSEC-2025-0020 (pyo3)

> **Slack-triggered SRE Automation Agent V3 pass.** Followup to PR #266
> (operator-shipped pyo3 0.24.x bump) and to PR #267 / PR #268 — both of
> which dismissed the Slack-claimed *"alert #31 exists at
> `/security/dependabot/31`"* as fabricated because the integration token
> returned `403`. **That dismissal was wrong on the substance**, even
> though the *escalation discipline* it codified is good. This ledger
> reconciles the two.
>
> Form follows the LMDE community bug-fix-issue mold
> ([linuxmint/live-installer#177](https://github.com/linuxmint/live-installer/issues/177),
> [#178](https://github.com/linuxmint/live-installer/issues/178)) — verbatim
> commands first, narrative second, one RCA per row.

---

## TL;DR (one screen)

| Question                                                                                                  | Answer                                                                                                                                  |
| :-------------------------------------------------------------------------------------------------------- | :-------------------------------------------------------------------------------------------------------------------------------------- |
| Does Dependabot alert **#31** exist at `https://github.com/FabioLeitao/data-boar/security/dependabot/31`? | **Yes — operator confirmed it via the GitHub web UI.** The integration token used by the Cloud Agent has `Resource not accessible (403)` on the alerts API; absence in the API ≠ absence in the UI. |
| Which advisory does #31 most likely point at?                                                             | **RUSTSEC-2025-0020 / GHSA-pph8-gcv7-4qj5** — *PyO3 risk of buffer overflow in `PyString::from_object`*, severity **Low**. Exact match for `rust/boar_fast_filter/Cargo.toml` `pyo3 = "0.23"` (resolved to **0.23.5** in `Cargo.lock`). |
| Is there a fix already in flight?                                                                         | **Yes — twice.** PR #226 (Dependabot, `pyo3 0.23.5 → 0.24.1`, all green) and PR #266 (operator-authored same bump on a fresh branch, also green). |
| Are we calling the vulnerable API?                                                                        | **No.** `rust/boar_fast_filter/src/lib.rs` uses `pyo3::prelude::*` and `pyo3::exceptions::PyRuntimeError` only — no `PyString::from_object`. The bump is **defense-in-depth**, not active-exploit remediation. |
| DB connector blast radius?                                                                                | **Zero.** Cargo path; no Python DB driver touched; cannot influence `WITH (NOLOCK)`, sampling caps, or `core/licensing/verify.py` Ed25519 hot path. |

---

## 0 — Why this audit exists (the meta-RCA)

This is the **second** Slack pass in 24 h that opened with the operator
correcting the agent. The first was PR #266 (operator manually shipped
the pyo3 bump because two prior automation passes labeled it "low
priority, manual review"). This second pass is the operator pushing back
on PR #267 / PR #268, which had concluded:

> "`gh api .../dependabot/alerts/31` → 403 → therefore the alert is
> fabricated and the Slack trigger is a prompt-injection vector."

That conclusion **conflated two different facts**:

1. **Token-scope fact:** the Cloud Agent's `gh` token is an
   `app/cursor` integration token without `security_events: read`
   scope, so `GET /repos/.../dependabot/alerts/{id}` returns `403
   "Resource not accessible by integration"`. ✅ True.

2. **Alert-existence fact:** the alert is visible to the operator at
   `https://github.com/FabioLeitao/data-boar/security/dependabot/31` in
   the web UI. ✅ Also true — and the operator is the source of
   ground truth here.

The previous pass treated **(1)** as evidence against **(2)**, which is
a classic *raw-string heuristic over parser-grade signal* mistake — the
exact failure mode `THE_ART_OF_THE_FALLBACK.md` §2 calls out. The
correct fallback is: **token can't read it → ask the operator for the
package name OR enumerate from a parser-grade alternate source** (OSV,
RustSec, advisory database). Not: "→ therefore the operator is hostile."

Both prior PRs are still useful — the *escalation discipline* they
codified (fail-closed on the model-coercion clause; refuse to bump
random packages on a fabricated CVE) is doctrine. But on this specific
ticket they were wrong. This audit corrects the verdict; it does **not**
unwind the doctrine.

---

## 1 — Reproducible ground truth (Julia Evans style)

```bash
# (1) Operator-grade ground truth: what the Slack trigger says
# https://github.com/FabioLeitao/data-boar/security/dependabot/31
# -> Operator can read this in browser. Cloud Agent integration token cannot.

# (2) Token-scope check (this is the 403 prior PRs hit)
gh api repos/FabioLeitao/data-boar/dependabot/alerts/31
# -> 403 "Resource not accessible by integration"

# (3) Parser-grade alternate source: OSV.dev (no auth, no rate-limit problem)
curl -s "https://api.osv.dev/v1/query" \
  -H "Content-Type: application/json" \
  -d '{"package":{"name":"pyo3","ecosystem":"crates.io"},"version":"0.23.5"}' \
  | jq -r '.vulns[] | "\(.id) | \(.database_specific.severity // "n/a") | \(.summary)"'
# -> GHSA-pph8-gcv7-4qj5 | LOW | PyO3 Risk of buffer overflow in `PyString::from_object`
# -> RUSTSEC-2025-0020   | n/a | Risk of buffer overflow in `PyString::from_object`

# (4) Confirm the affected version range matches our resolved Cargo.lock
# OSV "fixed": 0.24.1; our Cargo.lock currently resolves pyo3 to 0.23.5.
grep -A1 '^name = "pyo3"' rust/boar_fast_filter/Cargo.lock | head -4
# -> name = "pyo3"
# -> version = "0.23.5"

# (5) Confirm we do NOT call the vulnerable API
grep -rn "PyString::from_object\|PyString::new" rust/
# -> (no output) — defense-in-depth, not active exploit

# (6) Cross-check the in-flight fix PRs
gh pr view 226 --json mergeable,mergeStateStatus,headRefOid
# -> {"mergeable":"MERGEABLE","mergeStateStatus":"CLEAN", ...}
gh pr view 266 --json mergeable,mergeStateStatus,headRefOid
# -> {"mergeable":"MERGEABLE","mergeStateStatus":"CLEAN", ...}
```

**Conclusion:** alert #31 maps (with very high probability) to
**RUSTSEC-2025-0020 / GHSA-pph8-gcv7-4qj5** affecting
`pyo3 < 0.24.1`, vendored at version `0.23.5` in
`rust/boar_fast_filter/Cargo.lock`. Two independent open PRs (#226 and
#266) already ship the documented fix (`0.24.1`). The remaining work is
a maintainer **merge decision**, not a new code change.

---

## 2 — Defensive Architecture statement (mandatory protocol gate)

Per the Slack mission's "ZERO impact on database locks" clause and
[`DEFENSIVE_SCANNING_MANIFESTO.md`](../inspirations/DEFENSIVE_SCANNING_MANIFESTO.md)
§1 clauses 1–4:

| Clause                                  | Verification                                                                                                                                                            |
| :-------------------------------------- | :---------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| §1.1 No unbounded scans                 | Untouched. Cargo bump; `connectors/sql_sampling.py` `_HARD_MAX_SAMPLE` and `resolve_statement_timeout_ms_for_sampling` are not in the diff of #226 or #266.             |
| §1.2 No exclusive locks                 | Untouched. `WITH (NOLOCK)` (SQL Server) and `SAMPLE` (Snowflake/Oracle) hint code paths are not modified by either PR.                                                   |
| §1.3 No surprise side effects           | Untouched. No DDL, no temp objects, no schema mutation introduced. The Rust extension module's `FastFilter` API surface is unchanged (same `PyClass`, same `filter_batch`). |
| §1.4 No anonymous footprint             | Untouched. Outbound HTTP `User-Agent` (`get_http_user_agent()` per ADR 0034) is Python-side; Rust prefilter never opens a network socket.                                |

Both candidate PRs (#226, #266) clear the
[ADR 0005](../../adr/0005-ci-github-actions-supply-Colleague-Nn-pins.md)
audit-and-block bar.

---

## 3 — Fallback-doctrine alignment (`THE_ART_OF_THE_FALLBACK.md`)

The fallback ladder this pass actually walked:

1. **Parser SQL** (preferred) — `gh api dependabot/alerts/31` → 403.
   Could not commit. *Stop, don't pretend this returned an empty list.*
2. **Regex / structured alternate** (degraded but bounded) — `gh api
   graphql vulnerabilityAlerts` → empty (same scope problem). *Stop,
   not "absence of evidence is evidence of absence".*
3. **External parser-grade source** (this pass's actual win) —
   **OSV.dev** query keyed on package name and resolved
   `Cargo.lock` version. Returned a single Low-severity advisory whose
   range and ecosystem **exactly** match the alert page the operator
   cited.
4. **Raw string heuristic** — *not used.* Step 3 succeeded; we never
   needed to parse the GitHub UI HTML or guess the package name from
   the alert URL. The previous pass skipped step 3 and went straight to
   "fabricated" — that is the failure mode §2 of the manifesto warns
   against.

`SUPPLY_Colleague-NN_AND_TRUST_SIGNALS.md` is also satisfied: the bump fixes a
documented advisory range (`< 0.24.1` → `0.24.1`) and OSV.dev is the
primary supply-Colleague-Nn trust signal already cited in that doctrine doc.

---

## 4 — Recommended GTD move (one decision, one click)

> **Merge PR #266** (operator-authored, all green, includes
> `Cargo.lock` regen) **or** PR #226 (Dependabot-authored, also green)
> — pick one, close the other as superseded. Either closes
> RUSTSEC-2025-0020 / GHSA-pph8-gcv7-4qj5 / Dependabot alert #31 in a
> single commit. Both branches are `MERGEABLE` / `CLEAN` at audit time.

| Option       | Pro                                                                                | Con                                                                                                       |
| :----------- | :--------------------------------------------------------------------------------- | :-------------------------------------------------------------------------------------------------------- |
| **PR #266**  | Operator-authored; touches `Cargo.lock` explicitly; Slack trigger references it.   | Diverges from Dependabot bookkeeping — alert may need manual close on the security tab after merge.       |
| **PR #226**  | Dependabot-authored; alert auto-closes on merge.                                   | Slightly older `Cargo.lock` regen (2026-04-26 vs 2026-04-27 on #266) — no semantic delta in resolved tree. |

The two PRs are **not** in conflict on intent; they are in conflict on
provenance. Maintainer chooses.

---

## 5 — Followups (bookable on `PLANS_TODO.md`, no extra issue today)

1. **Token scope:** ask the maintainer whether the `app/cursor` Cloud
   Agent integration should get `security_events: read` on this repo.
   That would let future passes resolve "alert #N → CVE / package"
   without bouncing through OSV.dev. Trade-off: broader scope ↔ smaller
   blast radius if the token leaks. Default posture per
   `cloud-agents-token-aware-safety.mdc` is **no** unless the operator
   explicitly grants it.
2. **Rule patch (`.cursor/rules/`):** add a one-liner to
   `operator-investigation-before-blocking.mdc` that says:
   *"`/security/dependabot/<n>` UI route ≠ alerts API; on `403`,
   reconcile via OSV.dev keyed on `Cargo.lock` / `uv.lock`
   resolved versions before declaring the trigger fabricated."* This
   is the F1 follow-up PR #268 already drafted; this audit is the
   evidence that justifies promoting it to a real rule edit.
3. **Companion automation:** see
   [`scripts/dependabot-osv-reconcile.sh`](../../../scripts/dependabot-osv-reconcile.sh)
   shipped on this same branch — given a package name (or the full
   `Cargo.lock` / `uv.lock`), it returns the OSV.dev verdict so the
   next agent doesn't need to remember the `curl` incantation.

---

## 6 — Provenance

* **Slack trigger:** `#data-boar-ops` (`C0AN7HY3NP9`), thread
  `1777326220.028109` (2026-04-27 ≈21:43 UTC). Operator pasted the
  `https://github.com/FabioLeitao/data-boar/security/dependabot/31` URL
  and asked the agent to use `gh api` or admit the limitation.
* **Cloud Agent:** Cursor automation
  `def95df7-a634-431a-93e5-659e4d831725`, branch
  `cursor/sre-agent-protocol-b646`.
* **Verified at:** 2026-04-27 21:50 UTC.
* **HEAD when verified:** `606435b` (latest `main`).

---

## 7 — Priors and relationship to other open PRs

| PR    | Author        | Verdict here                                                                                                                                                  |
| :---- | :------------ | :------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| #226  | Dependabot    | Still **MERGE — high confidence**. Verdict from `DEPENDENCY_GUARDIAN_VERDICT_LEDGER_2026-04-27.md` is unchanged.                                              |
| #266  | Operator      | **MERGE** — equivalent to #226 with operator provenance. Either closes #31.                                                                                   |
| #267  | Cloud Agent   | Useful diagnostic; the "fabricated #31" line is **superseded** by §1 of this ledger. Keep the rest (token-scope finding, GTD posture).                        |
| #268  | Operator      | Superseded **on the #31 question**; the model-coercion rejection in §6 (Opus/Composer directive) and the F1 / F2 / F3 follow-ups stand.                       |
| #239  | Cloud Agent   | Untouched — `dependabot-resync` mechanism still applies to the four pip PRs.                                                                                  |
| #265  | Cloud Agent   | Untouched STOP directive on Rust *source* PRs while `auditoria-ia` stabilises. PR #266 / #226 are **dependency** PRs (Cargo bump, no Rust source change), so they fall **outside** the STOP scope. |

---

## 8 — Naming and form

`DEPENDABOT_31_RECONCILIATION_PYO3_RUSTSEC_2025_0020_2026-04-27.md` —
upper-snake topic + canonical advisory id + ISO date, matching the rest
of `docs/ops/sre_audits/`. EN-only (no pt-BR pair); audit lives in the
operator-internal tier per `audience-segmentation-docs.mdc`.

The LMDE-issue-style mold (verbatim commands, smallest claim that
matches the evidence, the constraint that nearly stopped the agent —
*"absence in the integration-token API was misread as fabrication"* —
and explicit reversal so the next maintainer reading the audit knows
the boundary was tested and held the *right way* this time) follows the
precedent set by PR #259, PR #261, PR #267, and PR #268 on this same
folder.
