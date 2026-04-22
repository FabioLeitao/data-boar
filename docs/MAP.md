# Documentation topic map (navigation by concern)

**Português (Brasil):** [MAP.pt_BR.md](MAP.pt_BR.md)

This page is a **concern-driven index**: it connects high-level questions (what a **CISO**, **DPO**, or **security architect** cares about) to the concrete guides where behaviour, config keys, and limits are defined. Use it when you already know the topic (e.g. minors, cross-border hints) and want the shortest path without browsing every folder. The full flat index remains **[README.md](README.md)** ([pt-BR](README.pt_BR.md)).

---

## Minor data and child-related privacy (technical scope)

| Question | Read first | Config / behaviour | Related |
| -------- | ---------- | ------------------- | ------- |
| How does the product flag **possible minor** data (DOB, age columns), thresholds, optional full scan, and cross-reference? | **[MINOR_DETECTION.md](MINOR_DETECTION.md)** ([pt-BR](MINOR_DETECTION.pt_BR.md)) | `detection.minor_age_threshold`, `detection.minor_full_scan`, `detection.minor_cross_reference` | [SENSITIVITY_DETECTION.md](SENSITIVITY_DETECTION.md) ([pt-BR](SENSITIVITY_DETECTION.pt_BR.md)), [USAGE.md](USAGE.md) `detection` / report sections ([pt-BR](USAGE.pt_BR.md)) |
| Brazil **FELCA** (digital child/adolescent statute) and how the product positions **metadata-only** support? | **[COMPLIANCE_FRAMEWORKS.md](COMPLIANCE_FRAMEWORKS.md)** — *Auditable and management standards* ([pt-BR](COMPLIANCE_FRAMEWORKS.pt_BR.md)) | Same: minor flags are inventory-oriented, not age verification | [COMPLIANCE_AND_LEGAL.md](COMPLIANCE_AND_LEGAL.md) ([pt-BR](COMPLIANCE_AND_LEGAL.pt_BR.md)) |
| **U.S.** COPPA / CA AB 2273 / CO CPA minors — **technical** YAML samples (norm tags, not legal advice)? | **[COMPLIANCE_FRAMEWORKS.md](COMPLIANCE_FRAMEWORKS.md)** — compliance samples table and disclaimers ([pt-BR](COMPLIANCE_FRAMEWORKS.pt_BR.md)) | Files under [compliance-samples/](compliance-samples/) (e.g. `compliance-sample-us_ftc_coppa.yaml`) | [compliance-samples/README.md](compliance-samples/README.md) ([pt-BR](compliance-samples/README.pt_BR.md)) |

Design history for minor detection lives in a **completed** plan file under `docs/plans/completed/` in your checkout (`PLAN_MINOR_DATA_DETECTION`); the operator guide above is the maintained entry point (no plan link here per information-architecture rules).

---

## Jurisdiction hints (heuristic, metadata-only)

| Question | Read first | Config / behaviour | Related |
| -------- | ---------- | ------------------- | ------- |
| What are **jurisdiction hints**, who are they for, and how do I enable them (CLI, API, dashboard, YAML)? | **[USAGE.md](USAGE.md)** — search **jurisdiction_hints** / **Report info** ([pt-BR](USAGE.pt_BR.md)) | `report.jurisdiction_hints`, `--jurisdiction-hint`, `POST /scan` body | [COMPLIANCE_AND_LEGAL.md](COMPLIANCE_AND_LEGAL.md) ([pt-BR](COMPLIANCE_AND_LEGAL.pt_BR.md)) |
| Why hints are **not** legal conclusions and what ADR locked in? | **[ADR 0026](adr/0026-optional-jurisdiction-hints-dpo-facing-heuristic-metadata-only.md)** (English) | Index: [adr/README.md](adr/README.md) ([pt-BR](adr/README.pt_BR.md)) | [COMPLIANCE_TECHNICAL_REFERENCE.md](COMPLIANCE_TECHNICAL_REFERENCE.md) ([pt-BR](COMPLIANCE_TECHNICAL_REFERENCE.pt_BR.md)) |

---

## Sensitive detection and compliance depth (bridge topics)

| Question | Read first | Notes |
| -------- | ---------- | ----- |
| Regex, ML/DL, overrides, connector format hints | **[SENSITIVITY_DETECTION.md](SENSITIVITY_DETECTION.md)** ([pt-BR](SENSITIVITY_DETECTION.pt_BR.md)) | Pairs with [USAGE.md](USAGE.md) report and `detection` keys ([pt-BR](USAGE.pt_BR.md)) |
| Norm tags, samples, multi-region operation | **[COMPLIANCE_FRAMEWORKS.md](COMPLIANCE_FRAMEWORKS.md)** ([pt-BR](COMPLIANCE_FRAMEWORKS.pt_BR.md)) | Includes Brazil insurance LGPD anchor subsection and sample table |
| Encodings, API limits, evidence posture (IT / DPO) | **[COMPLIANCE_TECHNICAL_REFERENCE.md](COMPLIANCE_TECHNICAL_REFERENCE.md)** ([pt-BR](COMPLIANCE_TECHNICAL_REFERENCE.pt_BR.md)) | Operational limits, not legal advice |

---

## Where this fits

- **Technical install and run:** [TECH_GUIDE.md](TECH_GUIDE.md) ([pt-BR](TECH_GUIDE.pt_BR.md)) ends with a short **Topic map** pointer back here.
- **Glossary (terms by theme):** [GLOSSARY.md](GLOSSARY.md) ([pt-BR](GLOSSARY.pt_BR.md)).

If a topic is missing from this map, add a row in **both** `MAP.md` and `MAP.pt_BR.md` in the same PR.
