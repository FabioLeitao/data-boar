# Data Boar Subscription Tiers

Data Boar follows an **open-core** model inspired by projects like [Bitwarden](https://bitwarden.com/pricing/) and [NetSpot](https://www.netspotapp.com/pt/netspotpro.html):
a fully functional open core available to all, with commercial tiers that unlock advanced capabilities and commercial-use rights.

> **Note:** Exact pricing, availability dates, and feature assignments per tier are determined by the product team.
> This page is a structural overview only. For current pricing, contact the maintainer or see the website (when available).

## Tier overview

| Tier | Intended audience | License token | Key differentiator |
|---|---|---|---|
| **Community** | Internal DPOs, researchers, students, individual use | Not required (open mode) | Full open-core functionality; no cost |
| **Trial / POC** | Pre-sales evaluations, proof-of-concept | Time-limited signed token | Row-capped report; watermarked; converts to Pro/Partner |
| **Pro / Consultant** | Independent consultants, solo MSSPs | Annual signed token | Commercial delivery to **one client per engagement** |
| **Partner** | System integrators, MSPs, multi-client resellers | Annual org token | Multi-client delivery; co-brand rights; partner portal (future) |
| **Enterprise** | Large organisations, regulated industries, OEM | Custom enterprise agreement | All features + SLA + white-label add-on + SSO/LDAP |

## What changes between tiers

- **Detection depth:** ML/DL heuristics, confidence calibration, and advanced FN-reduction are Pro+
- **Connectors:** Cloud (O365, Google Drive, S3-class), SAP, enterprise ERP connectors are Pro/Partner+
- **File formats:** Legacy office suites (WordPerfect, Access, OneNote), binary string extraction, and browser artefacts are Pro+
- **Reports:** Dashboard RBAC, audit trail, compliance evidence mapping (GRC-ready) are Partner+
- **Commercial rights:** Delivering audits as a paid service to third parties requires at minimum a Pro licence

## Enforcement model

Tiers are enforced via **signed Ed25519 JWT licence tokens** (see [`LICENSING_SPEC.md`](LICENSING_SPEC.md)).
The open-core Community tier runs without a token (`licensing.mode: open`).

## Contact

To evaluate a Trial or enquire about Pro/Partner/Enterprise pricing, open an issue or contact the maintainer directly.

---

*See also: [`LICENSING_OPEN_CORE_AND_COMMERCIAL.md`](LICENSING_OPEN_CORE_AND_COMMERCIAL.md) for the open-core policy and brand IP inventory.*