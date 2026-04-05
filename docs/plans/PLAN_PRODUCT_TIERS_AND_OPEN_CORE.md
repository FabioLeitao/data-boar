# PLAN: Product Tiers and Open-Core Boundary Definition

**Status:** Draft — strategic, not yet legal-reviewed
**Priority:** [H2][U1] — critical before partner onboarding or public pricing page
**Related plans:** `PLAN_NEXT_WAVE_PLATFORM_AND_GTM.md`, `PLAN_GRC_INSPIRED_ENTERPRISE_TRUST_ACCELERATORS.md`, `PLAN_ENTERPRISE_HR_SST_ERP_CONNECTORS.md`, `PLAN_IMAGE_SENSITIVE_DATA_DETECTION.pt_BR.md`
**Commercial details (pricing, margins):** `docs/private/commercial/DATA_BOAR_FEATURE_TIER_STRATEGY.md` (gitignored)

---

## Summary

Define the sustainable open-core boundary for Data Boar: what is always free, what is
licensed, and why. Encode the boundary in the JWT enforcement model and document the
rationale so partners, reviewers, and contributors understand the product strategy.

This plan covers the feature matrix, tier rationale, and enforcement model.
Pricing, margin, and competitive intelligence live in the private commercial strategy doc above.

---

## Tier Model (5 levels)

| Tier | JWT claim | Target audience | Enforcement mode |
|---|---|---|---|
| **Community / Open Core** | absent or `community` | Researchers, DPOs, IT teams, students, freelancers | `open` — no token required |
| **Trial / POC** | `trial` | Pre-sales evaluations, proof-of-concept engagements | `enforced`; row-capped + watermarked |
| **Pro / Consultant** | `pro` | Independent consultants, MSSP, solo integrators | `enforced`; full features, single-client use |
| **Partner / Integrator** | `partner` | Resellers, MSPs, multi-client system integrators | `enforced`; multi-client + co-brand rights |
| **Enterprise** | `enterprise` | Large orgs, regulated industries, white-label OEM | `enforced`; all features + SLA + SSO + SIEM |

---

## Feature Tier Assignment (non-exhaustive)

### Ingestion sources

| Source | Community | Pro | Partner | Enterprise |
|---|---|---|---|---|
| Local filesystem, any path | ✅ | ✅ | ✅ | ✅ |
| MySQL, PostgreSQL, SQLite, MongoDB | ✅ | ✅ | ✅ | ✅ |
| Oracle, MSSQL, DB2 | — | ✅ | ✅ | ✅ |
| SAP HANA / R3 | — | — | ✅ | ✅ |
| Cloud storage (S3, GCS, Azure Blob) | — | ✅ | ✅ | ✅ |
| OneDrive / SharePoint (local sync path) | ✅ | ✅ | ✅ | ✅ |
| OneDrive / SharePoint API (tenant-wide) | — | — | ✅ | ✅ |
| Teams attachments (manual path) | ✅ | ✅ | ✅ | ✅ |
| Teams attachments (auto path discovery) | — | ✅ | ✅ | ✅ |
| Teams Graph API (live tenant scan) | — | — | — | ✅ |
| Outlook PST / OST archives | — | ✅ | ✅ | ✅ |
| IMAP live mailbox | — | — | ✅ | ✅ |

### File formats

| Format | Community | Pro | Enterprise |
|---|---|---|---|
| Text, CSV, JSON, XML, YAML, HTML | ✅ | ✅ | ✅ |
| DOCX, XLSX, PPTX, ODT, ODS | ✅ | ✅ | ✅ |
| PDF (text layer) | ✅ | ✅ | ✅ |
| PDF (image-only, via OCR) | — | ✅ | ✅ |
| Images / screenshots (OCR) | — | ✅ | ✅ |
| Screen capture folder auto-discovery | — | ✅ | ✅ |
| Legacy Office (XLS, DOC, WordPerfect) | ✅ | ✅ | ✅ |
| Archive files (ZIP, TAR, 7Z — recursive) | — | ✅ | ✅ |
| Audio files (Whisper transcription) | — | — | ✅ |
| JVM heap dumps (.hprof) | — | — | ✅ |
| OS core dumps / minidumps | — | — | ✅ |
| Browser artefacts | — | ✅ | ✅ |

### Detection capabilities

| Capability | Community | Pro | Enterprise |
|---|---|---|---|
| Regex patterns (CPF, CNPJ, email, CC, phone) | ✅ | ✅ | ✅ |
| International patterns (SSN, NI, IBAN, etc.) | ✅ | ✅ | ✅ |
| Custom user-defined pattern sets | ✅ | ✅ | ✅ |
| ML/NLP entity recognition (spaCy) | — | ✅ | ✅ |
| Confidence scoring + calibration | — | ✅ | ✅ |
| Context-aware detection | — | ✅ | ✅ |
| Secrets detection (API keys, private keys) | ✅ | ✅ | ✅ |

### Reporting

| Output | Community | Pro | Partner | Enterprise |
|---|---|---|---|---|
| Console, JSON, CSV, Excel, HTML | ✅ | ✅ | ✅ | ✅ |
| PDF report | — | ✅ | ✅ | ✅ |
| Trend dashboard (multi-scan history) | — | ✅ | ✅ | ✅ |
| GRC-mapped report (LGPD/GDPR articles) | — | — | ✅ | ✅ |
| White-label / custom branding | — | — | — | ✅ |
| Audit trail (Colleague-Nn of custody) | — | — | ✅ | ✅ |
| RBAC multi-user dashboard | — | — | ✅ | ✅ |
| SIEM export (Elastic, Splunk, CEF) | — | — | — | ✅ |

---

## Surveillance-Adjacent Features — Policy

Some features (screenshot scanning, audio transcription, browser artefacts, memory dumps)
have legitimate compliance uses but could be misused for covert employee monitoring.

**Policy:** These features require minimum Pro license and explicit `--scope` flag.
The generated report includes a legal notice about appropriate-use requirements.
The EULA at all paid tiers explicitly requires operator legal basis for scanning.

See the commercial strategy document for the "Compliance Investigator" add-on option.

---

## Enforcement Roadmap

| Milestone | Description |
|---|---|
| M1 — Token parsing | JWT read + `dbtier` claim extraction (no hard block yet) |
| M2 — Soft enforcement | Warn when Pro+ feature used without token; log to report |
| M3 — Hard enforcement | Block Pro+ features without valid token; Trial row cap |
| M4 — Partner enforcement | Multi-client use allowed only with `partner`+ claim |
| M5 — Enterprise features | Audio, dumps, SSO, SIEM gated behind `enterprise` claim |

---

## What to Protect as IP (vs. Open Core)

| Asset | Protection model |
|---|---|
| Core regex engine + patterns | Open (drives trust, adoption, and contributions) |
| OCR integration (Tesseract) | Open (it's an existing OSS library) |
| ML/NLP model weights | Closed (trained by us; not committed to repo) |
| License issuance tooling | Closed (separate private repo) |
| Audit trail / Colleague-Nn-of-custody module | Closed (Pro+) |
| Audio transcription pipeline | Closed (Enterprise) |
| Dump parsing engine | Closed (Enterprise) |
| White-label customization hooks | Closed (Enterprise add-on) |

---

## Open Questions (operator decision required)

- [ ] Should OCR on images be Open Core or Pro? (currently assigned to Pro — revisit)
- [ ] Is there a "Compliance Investigator" add-on tier, or does everything escalate to Enterprise?
- [ ] Should the SAP connector be Partner or Enterprise? (currently Partner)
- [ ] Audio transcription: use `openai-whisper` (GPL) or `faster-whisper` (MIT/LGPL)? License matters commercially.
- [ ] Where does the git secrets scanning fit vs. TruffleHog? Differentiation or overlap?

---

## Next Steps

- [ ] Legal review of EULA language for surveillance-adjacent features
- [ ] Implement M1 token parsing (low-risk, no behavior change)
- [ ] Define trial row cap and watermark design
- [ ] Validate pricing with 5-10 prospect conversations (see commercial strategy doc)