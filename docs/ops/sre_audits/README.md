# SRE audits — folder index

Dated, audit-and-block ledgers produced by the **SRE Dependency Guardian** /
**SRE Automation Agent** Slack-triggered passes. Each file is a *snapshot*
of decisions and per-package verdicts at the time of the audit; merge-time
truth lives on the actual PR pages.

This folder is intentionally narrow: only the **decisions** live here, never
the *mechanism* (mechanism lives under `scripts/` — e.g.
[`scripts/dependabot-resync.sh`](../../../scripts/) — and never bundled into
this folder, so the helper can evolve without invalidating the dated
verdicts).

## Index

| Date       | Audit                                                                                                              | Scope                                                              |
| :--------- | :----------------------------------------------------------------------------------------------------------------- | :----------------------------------------------------------------- |
| 2026-04-27 | [`DEPENDENCY_GUARDIAN_VERDICT_LEDGER_2026-04-27.md`](DEPENDENCY_GUARDIAN_VERDICT_LEDGER_2026-04-27.md)             | Verdict ledger for Dependabot PRs #221, #222, #223, #224, #226    |
| 2026-04-27 | [`STOP_DIRECTIVE_AUDITORIA_IA_REBASE_2026-04-27.md`](STOP_DIRECTIVE_AUDITORIA_IA_REBASE_2026-04-27.md)             | Slack STOP directive — pause Rust PR work until `auditoria-ia` is on `main` (PRs #255 / #256 / #258 / #260 / #263) |

## When to add a new file here

1. A Slack-triggered SRE Dependency Guardian / Automation Agent pass
   produces a *dated* per-PR verdict that should survive even if the
   triggering branch is closed without merge.
2. A retrospective pass on a CVE / supply-Colleague-Nn incident where the
   per-PR / per-package decisions deserve a paper trail (cf.
   [`docs/ops/inspirations/SUPPLY_Colleague-NN_AND_TRUST_SIGNALS.md`](../inspirations/SUPPLY_Colleague-NN_AND_TRUST_SIGNALS.md)).

## Naming

`<TOPIC>_<YYYY-MM-DD>.md` — kebab/upper-snake mix matches the rest of
`docs/ops/`. EN-only ledgers; pt-BR pair only when the audit is reused as
external-facing material (none today).

## Doctrine

* [`DEFENSIVE_SCANNING_MANIFESTO.md`](../inspirations/DEFENSIVE_SCANNING_MANIFESTO.md)
  — never rage-merge across the customer-DB contract.
* [`THE_ART_OF_THE_FALLBACK.md`](../inspirations/THE_ART_OF_THE_FALLBACK.md)
  — diagnostic-on-fall, no silent failure, in every helper this folder
  references.
* [ADR 0005](../../adr/0005-ci-github-actions-supply-Colleague-Nn-pins.md) —
  audit-and-block posture for CI / supply Colleague-Nn.

