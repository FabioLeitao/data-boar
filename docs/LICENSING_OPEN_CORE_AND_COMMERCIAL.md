# Open core and commercial licensing (draft policy)

This document describes the **intended** product boundary for Data Boar: an **open-core** distribution (community trust, auditability) plus **commercial** capabilities enforced by cryptographic licensing. It is a **draft** for operators and contributors; **final license terms require legal review** before you change the root `LICENSE` or ship paid builds.

## Model (Bitwarden-style hybrid)

| Layer | Intent | Typical license posture |
| ----- | ------ | ------------------------ |
| **Open core** | Essential scan, reporting, dashboard, connectors baseline; buildable from public sources without a paid token | Remains under a permissive or strong-copyleft OSI-approved license (today: **BSD 3-Clause** in `LICENSE`; future option: **AGPL-3.0** for server-side if you want stronger “self-host must share changes” terms) |
| **Commercial / source-available modules** | Enterprise features, advanced policies, premium connectors, or controlled trial/POC behaviour | **Source-available** terms: code may be visible for audit, but **production use requires a valid subscription** and a **signed license token** (see [LICENSING_SPEC.md](LICENSING_SPEC.md)) |

This mirrors the industry pattern used by projects such as **Bitwarden**: core under GPL/AGPL-style terms, with separate directories or packages under a **commercial / source-available** license for paid features. See Bitwarden’s server `LICENSE_FAQ.md` and `bitwarden_license/` layout for the idea (do not copy their license text without counsel).

## What stays in the public repository

- Scanner engine, connectors (baseline), report generation, API/dashboard (dashBOARd), tests, docs for **operators** (USAGE, SECURITY, deployment guides).
- **Runtime verification only**: public **Ed25519 verify key** (not the signing key), revocation list format, and the behaviour of `core/licensing/` when `licensing.enforcement` is enabled.

## What must never be in the public repository

- **Private signing keys**, operator “blob” secrets, or any material that allows forging valid license JWTs.
- The **license issuance** tool source or binaries intended only for your team (maintain in a **separate private repository**; see `tools/license-studio/README.md`).

## Default behaviour (development and CI)

With **no enforcement** (default), the application runs in **open** mode: no license file is required, and all features behave as today. This preserves forks, tests, and academic use until you explicitly enable enforcement in config or environment (see [LICENSING_SPEC.md](LICENSING_SPEC.md)).

## Next steps (legal)

1. Choose **BSD 3-Clause vs AGPL-3.0** for the open core (AGPL increases copyleft on network use; BSD maximizes adoption—trade-off with counsel).
2. Draft a **commercial / source-available** license for paid modules (or adapt a vetted template).
3. Add **NOTICE** / **THIRD_PARTY** files if you redistribute cryptography or other stacks under varied licenses.

## Future product tiers: partners vs end customers (planning reminder)

**Reminder for a later licensing pass** (IP protection, commerciality, profitability): consider **multiple commercial SKUs** with different **objectives, entitlements, and price points**—not unlike how database vendors segment **Express**, **Standard**, **Enterprise**, **Enterprise + options**, **RAC / add-ons**, etc.

**Use case to preserve explicitly:** **Consulting / integration partners** who hold a **partner-grade** (or **pro** / **enterprise**—names TBD) subscription and use Data Boar to deliver audits or implementations for **their customers** (third-party end clients), under **their** contract and entitlement, as distinct from:

- A **regular commercial** SKU aimed at **organisations that consume the product directly** (internal DPO / IT), and
- Optional **trial / POC** or **academic** postures you already separate in policy.

**Why it matters:** Partner-led delivery changes **risk, support, liability, metering, and brand** expectations. Pricing should reflect **different cost-to-serve** (e.g. multi-customer use, higher support load, possible white-label or co-brand rules). **Final tier names, contract text, and technical enforcement** require **legal + product** decisions before implementation.

**Technical direction (later):** encode tier/program in signed tokens (see [LICENSING_SPEC.md](LICENSING_SPEC.md) “Future extensions”) and enforce in `LicenseGuard` / reporting only after claims and contracts are fixed.

## Related documents

- [LICENSING_SPEC.md](LICENSING_SPEC.md) — token format, states, machine binding, revocation.
- [RELEASE_INTEGRITY.md](RELEASE_INTEGRITY.md) — optional signed release manifest.
- [HOSTING_AND_WEBSITE_OPTIONS.md](HOSTING_AND_WEBSITE_OPTIONS.md) — private repos and public site options.
