# Plan: Scope import from exports (inventory bootstrap → YAML config)

**Status:** Not started (planning / backlog catalogue)

**Synced with:** [PLANS_TODO.md](PLANS_TODO.md)

### Operator sequencing (maintainer — relative to GRC / maturity)

**Intended order:** (1) **[PLAN_MATURITY_SELF_ASSESSMENT_GRC_QUESTIONNAIRE.md](PLAN_MATURITY_SELF_ASSESSMENT_GRC_QUESTIONNAIRE.md)** — DOCX → curated YAML, architecture **A** POC; (2) **this plan** — **manual CSV / export breadcrumbs** → canonical asset list → config fragments (Phases B/C), even when the customer only has a **hand-maintained spreadsheet**; (3) **[#86](https://github.com/FabioLeitao/data-boar/issues/86)** — session + **passwordless (Bitwarden Passwordless.dev minimum)** + RBAC on **`/{locale}/…`** per [PLAN_DASHBOARD_REPORTS_ACCESS_CONTROL.md](PLAN_DASHBOARD_REPORTS_ACCESS_CONTROL.md). **Yes, this sequence is achievable** as a roadmap; delivery is **token- and sprint-paced** — see [TOKEN_AWARE_USAGE.md](TOKEN_AWARE_USAGE.md).

**Related plans:** [PLAN_NEXT_WAVE_PLATFORM_AND_GTM.md](PLAN_NEXT_WAVE_PLATFORM_AND_GTM.md) (N2 modular runtime + GTM), [PLAN_OPT_IN_NETWORK_PORT_SERVICE_HINTS.md](PLAN_OPT_IN_NETWORK_PORT_SERVICE_HINTS.md) (active probes — complementary), [PLAN_ENTERPRISE_HR_SST_ERP_CONNECTORS.md](PLAN_ENTERPRISE_HR_SST_ERP_CONNECTORS.md) (live back-office connectors — different scope), [PLAN_DATA_SOURCE_VERSIONS_AND_HARDENING.md](PLAN_DATA_SOURCE_VERSIONS_AND_HARDENING.md) (future: tags from imported asset metadata).

<!-- plans-hub-summary: Offline exports (monitoring, ITSM, assessment) → canonical format → Data Boar config targets; seed early scan rounds for consultants and enterprise teams. -->
<!-- plans-hub-related: PLAN_NEXT_WAVE_PLATFORM_AND_GTM.md, PLAN_OPT_IN_NETWORK_PORT_SERVICE_HINTS.md, PLAN_ENTERPRISE_HR_SST_ERP_CONNECTORS.md -->

---

## Purpose

Help teams get **faster time-to-first-value** by turning **breadcrumbs** they already have — **exports** from tools whose primary job is *not* Data Boar — into **mergeable config fragments** (YAML/JSON) for the first rounds of scanning.

Typical sources (examples, not an exhaustive commitment):

| Category | Examples | What we usually extract |
| -------- | -------- | ------------------------ |
| **Assessment / sizing (consultant or customer)** | Dell **Live Optics** (incl. free tier usage as a service provider), similar exports | Hosts, storage paths, workload hints → **prioritized targets** |
| **ITSM / asset / tickets** | **GLPI**, Movidesk, Jira SM exports | Asset lists, owners, categories → **tags and target lists** |
| **Classic monitoring** | **Nagios**, **Cacti**, Icinga-class | Hosts, services, sometimes paths → **host:port** seeds |
| **Observability / APM** | **Prometheus** (targets/rules exports), **Datadog**, **Dynatrace** | Service/host inventory, dependency maps → **scope hints** (not full tracing) |

**Positioning:** This is **“use their breadcrumbs to feed the first rounds”** — closer to **the customer’s existing teams and tools**, not a claim that Data Boar *replaces* those systems.

---

## Non-goals (v1)

- **Live API integrations** to every vendor (auth, rate limits, firewall stories) — track as **separate** future work if needed.
- **Replacing CMDB, ITSM, or observability platforms** — we **import hints**, not operational truth.
- **Guaranteeing** a parser for every export format — ship a **canonical** format first; vendor-specific adapters are **incremental** and tested per format.

**When there is nothing to import:** If the customer has **no** exportable inventory, scope seeding from files does not apply—use the **opt-in** path in [PLAN_OPT_IN_NETWORK_PORT_SERVICE_HINTS.md](PLAN_OPT_IN_NETWORK_PORT_SERVICE_HINTS.md) only with **explicit** technician authorization and allowlists (see that plan’s **Worst case: zero inventory** section).

---

## Relationship to other work

| Plan | Relationship |
| ---- | ------------- |
| [PLAN_OPT_IN_NETWORK_PORT_SERVICE_HINTS.md](PLAN_OPT_IN_NETWORK_PORT_SERVICE_HINTS.md) | **Complements:** passive **export → config** vs optional **active** TCP probes on allowlisted scope. |
| [PLAN_ENTERPRISE_HR_SST_ERP_CONNECTORS.md](PLAN_ENTERPRISE_HR_SST_ERP_CONNECTORS.md) | **Distinct:** enterprise plan targets **sampling business data** via connectors; this plan targets **bootstrap scope** from files. |
| [PLAN_DATA_SOURCE_VERSIONS_AND_HARDENING.md](PLAN_DATA_SOURCE_VERSIONS_AND_HARDENING.md) | **Future:** imported asset IDs / owners may **enrich** `data_source_inventory` or report metadata. |

---

## Canonical import model (draft)

**Design direction:** one **documented** canonical schema (JSON or CSV) that the engine can consume — e.g. rows with: `asset_id`, `hostname`, `ip`, `path_hints[]`, `port_hints[]`, `tags[]`, `source_system`, `source_export_type`, `confidence` (optional).

Vendor-specific adapters **map** to this schema; the **loader** merges or emits a **config fragment** for operator review (never silent overwrite of secrets).

---

## Phases

| Phase | Deliverable | Status |
| ----- | ----------- | ------ |
| A | **Plan + schema doc** (this file + TECH_GUIDE / USAGE pointer when code exists) | ✅ Plan filed (canonical schema remains **draft** until Phase B) |
| B | **CLI or script**: canonical file → **stdout** or **fragment file** (merge instructions) | ⬜ Pending |
| C | **One reference adapter** (e.g. generic CSV host list or GLPI-shaped export) + pytest | ⬜ Pending |
| D | **Docs (EN + pt-BR):** operator workflow, privacy note (exports may contain sensitive infra metadata) | ⬜ Pending |
| E | **Optional:** second adapter; **commercial** narrative: “accelerator” / partner-delivered slices ([LICENSING_SPEC.md](../LICENSING_SPEC.md)) | ⬜ Pending |

---

## Risks

- **Format drift:** Vendor exports change between versions — version adapters and fixtures per format.
- **Over-promising:** “Integrates with X” without tests — prefer **“adapter for export vY”** language.
- **Sensitive metadata:** Exports can list hosts, IPs, org structure — document **handling** in SECURITY/USAGE (no new secrets in tracked samples).

---

## Token-aware sequencing

Prefer **one phase per session**; **A → B** before chasing multiple vendor adapters. Align with **[TOKEN_AWARE_USAGE.md](TOKEN_AWARE_USAGE.md)** and priority band in [PLANS_TODO.md](PLANS_TODO.md) (`[H3][U2]` / backlog unless a customer engagement elevates it).
