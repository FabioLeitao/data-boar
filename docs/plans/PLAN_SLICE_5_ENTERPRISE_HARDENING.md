**Status:** RFC (doc-only) — open for review · proposed for after **S2a** (Transport + trust POC) closes
**Synced with:** [PLANS_TODO.md](PLANS_TODO.md) · [SPRINTS_AND_MILESTONES.md](SPRINTS_AND_MILESTONES.md) §3 (Kanban) / §4 (Sprints)
**Audience:** Internal product planning (operator + maintainers) · stakeholder narrative for **Slice 5 — Enterprise Hardening**

---

# Plan — Slice 5: Enterprise Hardening (RFC)

> *Russinovich-grade visibility + Charity-Majors-grade explainability,
> applied to a guest scanner that must never block the customer DB.*

This RFC sits **inside** the existing engineering doctrine cycle
([PLAN_ENGINEERING_DOCTRINE_CONSOLIDATION.md](PLAN_ENGINEERING_DOCTRINE_CONSOLIDATION.md))
and is a **roadmap critique + Slice 5 definition** triggered by the
strategic mission *"What is missing for a Fortune 500 CISO to approve Data Boar?"*.

It is **doc-only** in this PR. It proposes a coherent next slice but
**does not** add code, change CLI flags, modify SQL composition, or
introduce new dependencies. **Zero impact on customer database locks**
(see [DEFENSIVE_SCANNING_MANIFESTO.md](../ops/inspirations/DEFENSIVE_SCANNING_MANIFESTO.md) §1–§3).

---

## 1. RCA-style problem statement (Julia Evans framing)

**Symptom.** The shipped roadmap covers **scan correctness**, **HTTPS / trust state**, **passwordless dashboard auth**, **SQL sampling defensiveness**, and **doctrine manifestos**. It does **not** yet cover, in one place, the **enterprise readiness** questions a Fortune 500 CISO will ask in a procurement review:

- *"Where do you store customer secrets at rest in production?"*
- *"How is tenant A's evidence isolated from tenant B's evidence?"*
- *"When a scan fails, what does the operator (and auditor) get, automatically?"*
- *"Show me the SLI/SLO of your scanner, not just the findings."*
- *"Is this agent-based or agentless? Prove it."*

Each of those has **partial** answers scattered across plans (Secrets Vault Phase B, RBAC Phase 2, GRC trust accelerators A1–A4, Notifications, Doctrine Slice 2). None has a **named SKU-level commitment** that a procurement reviewer can quote.

**Root cause.** Enterprise hardening is currently **emergent** from the union of many `[H3]` rows. There is no single document tying those threads to a **buyer-facing posture statement** with **demo bar** and **acceptance criteria**.

**Constraint (non-negotiable).** Anything implemented from this slice **must preserve** the defensive posture:

- Sampling caps and statement timeouts in [`connectors/sql_sampling.py`](../../connectors/sql_sampling.py) ([`DEFENSIVE_SCANNING_MANIFESTO.md`](../ops/inspirations/DEFENSIVE_SCANNING_MANIFESTO.md) §2–§3).
- Fallback hierarchy and audit demotion rule in [`THE_ART_OF_THE_FALLBACK.md`](../ops/inspirations/THE_ART_OF_THE_FALLBACK.md) §2–§3.
- No new live connector reads at report-regen time (APG path stays SQLite-only — see [BENCHMARK_EVOLUTION.md](BENCHMARK_EVOLUTION.md) §1).

---

## 2. Gap analysis — what a Fortune 500 CISO will ask

The mission asked us to audit `PLANS_TODO.md` against **Russinovich** (Sysinternals-grade visibility) and **Charity Majors** (observability / system explains itself) standards. The table below names each gap, points at the **existing partial answer**, and grades the **enterprise gap** (G1–G6).

| #   | Gap                                                | Existing partial answer                                                                                                                                                                                                                                                                | Enterprise gap                                                                                                                                              |
| --- | ----                                               | -----------------------                                                                                                                                                                                                                                                                | ---------------                                                                                                                                             |
| G1  | **External secrets manager** (AWS SM, HashiCorp Vault, Azure Key Vault) | [`PLAN_SECRETS_VAULT.md`](PLAN_SECRETS_VAULT.md) Phase A ✅ (env, redaction, .gitignore) · Phase B `⬜ Pending` (`@vault:` resolver, local encrypted store, re-import flow). | **No first-class adapter** for the three buyer-named vaults; today, "production secret storage" answer is *"use env / redact in UI"*. Procurement-blocking. |
| G2  | **Multi-tenant evidence isolation** (per-tenant audit, vault namespace, report scoping) | `dbtier` JWT, RBAC Phase 2 ([`PLAN_DASHBOARD_REPORTS_ACCESS_CONTROL.md`](PLAN_DASHBOARD_REPORTS_ACCESS_CONTROL.md)), tenant-aware `targets[]`, `roles_json` on `webauthn_credentials`. | **No documented contract** for *"if I deploy one Data Boar instance for two tenants, evidence cannot cross"*. RBAC alone does not promise that. |
| G3  | **Automated post-mortem on failed scans** (CISO-grade RCA, not "completão failed") | Doctrine Slice 2 (RCA in `completão` failure path) `⬜ Pending` · `core/scan_audit_log.py` already records strategy demotion. | **No artifact** the operator can attach to a customer ticket when a scan *fails partway*: must be a **single Markdown / JSON post-mortem** generated automatically, not a tail of stderr. |
| G4  | **Performance telemetry (Honeycomb-class)** — events with structured fields, traceable across scan stages | Audit log JSON, `--export-audit-trail`, executive report methodology section. | **No OTel-shaped exports**, no per-stage timing histograms, no "show me the p95 of the sampling stage" answer. Charity Majors’ bar: *the system must explain itself without the operator instrumenting it*. |
| G5  | **Agentless scanning posture (positioning + proof)** | Architecture is **already** agentless (outbound JDBC/REST/SMB; no software installed inside customer DB). | **The README does not say it loudly enough.** A Fortune 500 CISO reads "scanner" and assumes "agent on the box". Doc-only fix; high leverage. |
| G6  | **Compliance evidence diligence trail (review packet)** | M-TRUST-04 in [`PLAN_GRC_INSPIRED_ENTERPRISE_TRUST_ACCELERATORS.md`](PLAN_GRC_INSPIRED_ENTERPRISE_TRUST_ACCELERATORS.md) §A4. | M-TRUST-04 has no concrete template, no automation, no pin in `PLANS_TODO`. Slice 5 names the artifact. |

**What this RFC explicitly does not introduce as gaps:** SOC-2 certification, FedRAMP, HSM-backed key storage, on-prem air-gapped distribution. Those are **deferrals**, listed in §6 — not silent omissions.

---

## 3. Slice 5 — Enterprise Hardening (definition)

Slice 5 is **one coherent narrative**, executed as **five small phases** that match the engineering DNA the project has already committed to (defensive, fallback-aware, observability-first). Each phase ships a **doc-grade artifact first**, then a **thin code slice** when the operator promotes it from this RFC.

| Phase | Name                                       | Primary artifact (doc-first)                                                                                                                          | Thin code slice (later)                                                                                                                                                                                                          | Demo bar                                                                                                            |
| ----- | ----                                       | -----------------------                                                                                                                               | -----------------------                                                                                                                                                                                                          | --------                                                                                                            |
| **5.1** | **Secrets Manager Integration (G1)**     | New section in [`PLAN_SECRETS_VAULT.md`](PLAN_SECRETS_VAULT.md) Phase B: `@vault:aws-sm:...`, `@vault:hashicorp:...`, `@vault:azure-kv:...` resolver contract; failure semantics; key rotation story. | One adapter (AWS Secrets Manager preferred, smallest auth surface) behind `core/secrets/resolver.py`; lazy-imported optional dep `[secrets-aws]`; resolver returns `None` → falls back to env (per [`THE_ART_OF_THE_FALLBACK.md`](../ops/inspirations/THE_ART_OF_THE_FALLBACK.md)). | Operator points config at AWS SM, runs a scan, redacted UI shows `@vault:` ref, audit log records resolver demotion if the SM call failed. |
| **5.2** | **Multi-tenant Evidence Isolation (G2)** | New file `docs/ops/MULTITENANT_EVIDENCE_ISOLATION.md` (EN + pt-BR) — contract: `tenant_id` namespace in audit log, vault key prefix, report path prefix; **explicit non-goal** of cross-tenant SQL row hiding. | Add `tenant_id` field to `core/scan_audit_log.py` row (nullable, default operator install); thread through `report/executive_report.py` headers; RBAC `roles_json` already supports per-tenant binding. | `GET /status?tenant=acme` returns evidence count + last scan only for that tenant; cross-tenant access denied with `403`. |
| **5.3** | **Automated Failed-scan Post-mortem (G3)** | Closes Doctrine **Slice 2** to-do (Step 9 of [`PLAN_ENGINEERING_DOCTRINE_CONSOLIDATION.md`](PLAN_ENGINEERING_DOCTRINE_CONSOLIDATION.md)) — extends RCA from `completão` to **product runtime**. New `report/post_mortem.py` produces `<scan_id>.post_mortem.md` (+ JSON twin) on **any non-zero connector exit**. | Hook into existing `scan_audit_log` writer; reuse Sysinternals-style narrative from [`INTERNAL_DIAGNOSTIC_AESTHETICS.md`](../ops/inspirations/INTERNAL_DIAGNOSTIC_AESTHETICS.md). | A failed scan produces a one-screen Markdown with: which connector, exit code, narrowed hypothesis, last successful sampling step, suggested next action. **No customer DB re-read** to write it. |
| **5.4** | **Performance Telemetry — opt-in OTel (G4)** | New ADR (next number, see [`docs/adr/README.md`](../adr/README.md)) — *"Optional OpenTelemetry exporter for scan-stage events; off by default; Honeycomb / Tempo / Jaeger compatible."* Plus a one-page operator runbook in `docs/ops/`. | `core/telemetry/otel_exporter.py` lazy-imports `opentelemetry-api` only when `telemetry.enabled: true`. Spans: `scan.connect`, `scan.sample`, `scan.regex`, `scan.fallback`, `scan.report`. Field whitelist documented (no PII / no raw query bodies). | Operator points OTLP at Honeycomb/Tempo, sees per-stage p50/p95/p99 timing, can filter by `connector_kind` and `tenant_id`. **Off by default**. |
| **5.5** | **Agentless posture & review packet (G5 + G6)** | Doc-only update to README (EN + pt-BR) — *"Data Boar is **agentless**: outbound connections only, no software installed on the customer DB host"* — backed by a one-page `docs/ARCHITECTURE_AGENTLESS.md`. Concrete `docs/ops/REVIEW_PACKET_TEMPLATE.md` for M-TRUST-04. | `scripts/build-review-packet.ps1` + `.sh` twin: collects `--export-audit-trail`, post-mortems, SBOM filenames, last release notes into `out/review-packet/<date>.zip`. | Stakeholder reviewer (Wabbix-style) receives one zip with a deterministic structure; CISO procurement quotes the agentless paragraph verbatim. |

**Done-when (Slice 5 as a whole):**

1. All five phases have a **named artifact in this repo** (file or PR) the operator can show in a buyer call.
2. **No regression** in `tests/test_sql_sampling.py`, `tests/test_scan_audit_log.py`, `tests/test_executive_report*.py`, `tests/test_rbac.py`, or the WebAuthn / locale tests.
3. **Zero new SQL composition paths** that bypass `connectors/sql_sampling.py`.
4. `BENCHMARK_EVOLUTION.md` gets a Slice-5 row showing **no measurable regression** vs the v1.7.3 baseline (`0.574x` ratio gate or better — see [BENCHMARK_EVOLUTION.md](BENCHMARK_EVOLUTION.md)).

---

## 4. Reprioritization (effort vs. stakeholder value)

Stakeholder value is graded against a **Fortune 500 CISO procurement** lens; effort is graded against the **2-person-and-an-agent** reality (see [SPRINTS_AND_MILESTONES.md](SPRINTS_AND_MILESTONES.md) §1). **One change per row** — no compound moves.

| Order | Phase                                  | Stakeholder value | Effort   | Why this rank                                                                                                                                                                                          |
| ----- | -----                                  | ----------------- | ------   | ------------                                                                                                                                                                                           |
| **1** | **5.5** — Agentless posture & review packet (doc-only first) | **High**          | **Low**  | Reframes the entire pitch; doc-only PR; unlocks every later sales conversation; cites G5 + G6 in one move. **Should ship in the same merge window as this RFC promotion.**                              |
| **2** | **5.3** — Failed-scan post-mortem      | **High**          | **Low–Med** | Reuses existing `scan_audit_log` and the Doctrine Slice 2 work that is already `⬜ Pending`. Closes a real procurement objection: *"what does the operator hand me when it breaks?"*. |
| **3** | **5.1** — Secrets Manager (AWS SM first) | **High**          | **Med**  | Requires one cloud SDK and a careful resolver fallback path; high CISO recall ("you support AWS SM?"); unblocks the Vault Phase B story already in `PLANS_TODO`.                                       |
| **4** | **5.2** — Multi-tenant evidence isolation | **Med**           | **Med**  | Contract is mostly doc + a `tenant_id` field; the RBAC plumbing is already on `main`. Lower urgency than 5.1 because most current installs are single-tenant.                                          |
| **5** | **5.4** — OTel performance telemetry    | **Med-High**      | **Med**  | Honeycomb-class story; powerful for technical buyers; **last** because it is the only phase with a new optional dependency tree (`opentelemetry-*`) and would benefit from 5.3 post-mortem already shipped. |

**Backlog (do not promote in Slice 5):** SOC-2 audit prep, FedRAMP narrative, HSM key custody, on-prem signed-image distribution. These belong in a **separate** plan after Slice 5 demonstrates the runtime story.

**Sprint placement:** Slice 5 is **after S2a** (Transport + trust POC) closes. While S2a is open, 5.5 (doc-only) may run **in parallel** as a sidequest with subtype `pauseable` (per [`session-mode-keywords`](../../.cursor/rules/session-mode-keywords.mdc)).

---

## 5. Engineering DNA references (Council of Mentors)

This slice is **not** a tone reference. It maps each phase to a **normative manifesto** already in the repo:

| Phase | Manifesto                                                                                          | Why                                                                                                                                                |
| ----- | ----------                                                                                         | ---                                                                                                                                                |
| 5.1   | [DEFENSIVE_SCANNING_MANIFESTO.md](../ops/inspirations/DEFENSIVE_SCANNING_MANIFESTO.md) §1 (contract) · [THE_ART_OF_THE_FALLBACK.md](../ops/inspirations/THE_ART_OF_THE_FALLBACK.md) §3 (diagnostic on fall) | Vault-down is a fallback case, not a crash. Resolver demotion **must** be audit-logged.                                                            |
| 5.2   | [ACTIONABLE_GOVERNANCE_AND_TRUST.md](../ops/inspirations/ACTIONABLE_GOVERNANCE_AND_TRUST.md)        | Tenant isolation is a governance contract, not a config hint.                                                                                       |
| 5.3   | [INTERNAL_DIAGNOSTIC_AESTHETICS.md](../ops/inspirations/INTERNAL_DIAGNOSTIC_AESTHETICS.md) (Russinovich) · [ENGINEERING_BENCH_DISCIPLINE.md](../ops/inspirations/ENGINEERING_BENCH_DISCIPLINE.md) | Failed-scan output should *feel* like a Sysinternals diagnostic, not a Python traceback.                                                            |
| 5.4   | [ACTIONABLE_GOVERNANCE_AND_TRUST.md](../ops/inspirations/ACTIONABLE_GOVERNANCE_AND_TRUST.md) (Charity Majors / Honeycomb)                            | The scanner must explain itself without external instrumentation.                                                                                  |
| 5.5   | [DEFENSIVE_SCANNING_MANIFESTO.md](../ops/inspirations/DEFENSIVE_SCANNING_MANIFESTO.md) §1 (guest in the customer DB) | Agentless is the natural-language summary of clauses 1–4 of the customer-DB contract.                                                              |

---

## 6. Out of scope (explicit deferrals — do not silently expand)

- **SOC-2 / ISO 27001 / FedRAMP** certification work. These need an external auditor and a budget; Slice 5 makes them **possible**, it does not deliver them.
- **HSM-backed** key custody. Today the local encrypted vault accepts a key from env / file; HSM is a future plan.
- **Air-gapped on-prem signed image** distribution. Tracked in [PLAN_BUILD_IDENTITY_RELEASE_INTEGRITY.md](PLAN_BUILD_IDENTITY_RELEASE_INTEGRITY.md).
- **Renaming** the `connectors/` module hierarchy or refactoring `core/detector.py`.
- **New CLI flags or YAML keys** in this RFC (only proposals; flags ship in their own `PLAN_*.md` per [docs-plans.mdc](../../.cursor/rules/docs-plans.mdc)).

---

## 7. Sequential to-dos

| Step | Phase | Description                                                                                                                                            | Status      |
| ---- | ----- | -----------                                                                                                                                            | ------      |
| 1    | RFC   | Author this plan (gap analysis + phases + reprioritization)                                                                                            | ✅ Done      |
| 2    | RFC   | Add row to [`PLANS_TODO.md`](PLANS_TODO.md) and *Integration / active threads* bullet for Slice 5; refresh `plans-stats` / `plans_hub_sync`            | ✅ Done      |
| 3    | 5.5   | Doc-only: `docs/ARCHITECTURE_AGENTLESS.md` + README pitch update (EN + pt-BR) + `docs/ops/REVIEW_PACKET_TEMPLATE.md`                                    | ⬜ Pending   |
| 4    | 5.5   | Cross-platform `scripts/build-review-packet.ps1` + `.sh` twin (per [SCRIPTS_CROSS_PLATFORM_PAIRING.md](../ops/SCRIPTS_CROSS_PLATFORM_PAIRING.md))      | ⬜ Pending   |
| 5    | 5.3   | `report/post_mortem.py` + tests + USAGE update; reuse `core/scan_audit_log` row schema                                                                  | ⬜ Pending   |
| 6    | 5.1   | Extend `PLAN_SECRETS_VAULT.md` Phase B with `@vault:aws-sm:` resolver contract + ADR; ship AWS SM adapter behind `[secrets-aws]` extra                  | ⬜ Pending   |
| 7    | 5.2   | `docs/ops/MULTITENANT_EVIDENCE_ISOLATION.md` (EN + pt-BR) + `tenant_id` field in `scan_audit_log`; tests for cross-tenant `403` on `/status` and `/reports` | ⬜ Pending   |
| 8    | 5.4   | ADR for opt-in OTel exporter; `core/telemetry/otel_exporter.py` behind `[telemetry]` extra; runbook in `docs/ops/`                                      | ⬜ Pending   |
| 9    | RFC   | Update [`BENCHMARK_EVOLUTION.md`](BENCHMARK_EVOLUTION.md) with Slice 5 row showing no regression vs v1.7.3                                              | ⬜ Pending   |

---

## 8. Why this is doc-only and zero-impact (defensive architecture confirmation)

This PR introduces **one new file** (this RFC), **one row** in `PLANS_TODO.md`, **one bullet** in *Integration / active threads*, and the regenerated `PLANS_HUB.md` / `plans-stats` blocks. It does **not**:

- Touch `connectors/sql_sampling.py`, `core/scan_audit_log.py`, or `report/executive_report.py`.
- Add or change any SQL composition path; **`WITH (NOLOCK)`**, sampling caps, statement timeouts, and `-- Data Boar Compliance Scan` leading comment are unchanged.
- Open new outbound connections (no new HTTP user-agent surface, see [ADR 0034](../adr/0034-outbound-http-user-agent-data-boar-prospector.md)).
- Add a new dependency or modify `pyproject.toml` / `uv.lock` / `requirements.txt`.

Therefore **zero regression risk** at merge time. The phases above will each carry their own RCA + tests when promoted, per
[`AGENTS.md`](../../AGENTS.md) → *Proactive anti-regression automation*.

---

## 9. References

- [PLAN_ENGINEERING_DOCTRINE_CONSOLIDATION.md](PLAN_ENGINEERING_DOCTRINE_CONSOLIDATION.md) — parent doctrine cycle (Slices 1–4).
- [PLAN_GRC_INSPIRED_ENTERPRISE_TRUST_ACCELERATORS.md](PLAN_GRC_INSPIRED_ENTERPRISE_TRUST_ACCELERATORS.md) — A1–A4 trust accelerators; M-TRUST-04 review packet baseline.
- [PLAN_SECRETS_VAULT.md](PLAN_SECRETS_VAULT.md) — Phase A done; Phase B is the home for 5.1 adapter rows.
- [PLAN_DASHBOARD_REPORTS_ACCESS_CONTROL.md](PLAN_DASHBOARD_REPORTS_ACCESS_CONTROL.md) — RBAC Phase 2 prerequisite for 5.2.
- [PLAN_NOTIFICATIONS_OFFBAND_AND_SCAN_COMPLETE.md](PLAN_NOTIFICATIONS_OFFBAND_AND_SCAN_COMPLETE.md) — failed-scan notification hook reused in 5.3.
- [BENCHMARK_EVOLUTION.md](BENCHMARK_EVOLUTION.md) — regression budget gate.
- [SPRINTS_AND_MILESTONES.md](SPRINTS_AND_MILESTONES.md) §3–§5 — Kanban + milestones (Slice 5 lands after S2a).
- [DEFENSIVE_SCANNING_MANIFESTO.md](../ops/inspirations/DEFENSIVE_SCANNING_MANIFESTO.md), [THE_ART_OF_THE_FALLBACK.md](../ops/inspirations/THE_ART_OF_THE_FALLBACK.md), [INTERNAL_DIAGNOSTIC_AESTHETICS.md](../ops/inspirations/INTERNAL_DIAGNOSTIC_AESTHETICS.md), [ACTIONABLE_GOVERNANCE_AND_TRUST.md](../ops/inspirations/ACTIONABLE_GOVERNANCE_AND_TRUST.md) — engineering DNA references cited per phase in §5.

<!-- plans-hub-summary: RFC for Slice 5 — Enterprise Hardening: agentless positioning + post-mortem on failed scans + secrets manager (AWS SM / HashiCorp Vault / Azure KV) + multi-tenant evidence isolation + opt-in OTel telemetry. Doc-only; zero impact on customer DB locks. -->
<!-- plans-hub-related: PLAN_ENGINEERING_DOCTRINE_CONSOLIDATION.md, PLAN_GRC_INSPIRED_ENTERPRISE_TRUST_ACCELERATORS.md, PLAN_SECRETS_VAULT.md, PLAN_DASHBOARD_REPORTS_ACCESS_CONTROL.md, PLAN_NOTIFICATIONS_OFFBAND_AND_SCAN_COMPLETE.md, BENCHMARK_EVOLUTION.md -->
