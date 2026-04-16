# ADR 0022: Public glossary — compliance laws, roles, and platform terms

**Status:** Accepted
**Date:** 2026-04-08

## Context

[GLOSSARY.md](../GLOSSARY.md) originally emphasised **product** vocabulary: **finding**, **session**, **target**, **connector**, **heatmap**, **ADR**, etc. External readers also hit **acronyms and laws** scattered across [USAGE.md](../USAGE.md), [COMPLIANCE_FRAMEWORKS.md](../COMPLIANCE_FRAMEWORKS.md), [OBSERVABILITY_SRE.md](../OBSERVABILITY_SRE.md), and [SECURITY.md](../SECURITY.md) — **LGPD**, **GDPR**, **DPO**, **SRE**, **OAuth2**, **TLS**, **SBOM**, **SLI/SLO/SLA**, **ML/DL**, and others — without a single short definition page.

| Option | Pros | Cons |
|---|---|---|
| **Expand GLOSSARY.md** with one-line definitions and links to long-form docs | Discoverable from [docs/README.md](../README.md); keeps EN + pt-BR pairs ([GLOSSARY.pt_BR.md](../GLOSSARY.pt_BR.md)); avoids duplicating full legal text | Must stay short; risk of drift vs COMPLIANCE_FRAMEWORKS if not updated together |
| Rely only on inline explanation in each doc | No new file rows | Readers repeat context; translators work harder |
| New separate “compliance terms” doc | Could go deeper | Splits glossary; more links to maintain |

## Decision

1. **Treat [GLOSSARY.md](../GLOSSARY.md) as the umbrella index** for both product terms and **cross-cutting platform / compliance / transport** terms that appear in operator and integrator docs.
2. **Keep definitions to one table row** (short); point to **canonical detail** in COMPLIANCE_FRAMEWORKS, USAGE, SENSITIVITY_DETECTION, OBSERVABILITY_SRE, SECURITY, or ADRs (e.g. SBOM → [ADR 0003](0003-sbom-roadmap-cyclonedx-then-syft.md)).
3. **Maintain English + pt-BR** glossary files in lockstep when adding or changing entries (same skill as other user-facing docs).
4. **Include culture-of-delivery terms** (e.g. **Agile Manifesto**) only as minimal gloss + pointer that they are not product features — avoids bloating the table while helping readers who see maintainer-facing references.
5. **Organise the glossary by theme**, not as a single alphabetical table: sections such as product identity, session/targets, findings/overrides, laws/roles, APIs/transport, ML, etc. Within each section, sort rows **alphabetically** by the first column. Add a short **taxonomy** overview (table mapping theme → scope) at the top of [GLOSSARY.md](../GLOSSARY.md) so readers know how to browse.

## Consequences

- **Positive:** Lower barrier for DPOs, SREs, and integrators; single jump-off point linked from [docs/README.md](../README.md).
- **Negative:** More rows to review when compliance or observability docs change meaningfully.
- **Watch:** Do not paste long statutory text into the glossary; legal nuance stays in COMPLIANCE_FRAMEWORKS and sample YAML.

## References

- [GLOSSARY.md](../GLOSSARY.md) · [GLOSSARY.pt_BR.md](../GLOSSARY.pt_BR.md) — **§9** (*Compliance positioning & artefacts*) extends the umbrella with **metadata-only finding**, **counsel**, **DPIA**/**RoPA**/**TIA**/**SCC**, **PEP**/**KYC**, **compliance sample**; positioning record: [ADR 0025](0025-compliance-positioning-evidence-inventory-not-legal-conclusion-engine.md).
- [ADR 0002](0002-operator-facing-security-and-technical-docs.md) (operator-facing docs)
- [ADR 0004](0004-external-docs-no-markdown-links-to-plans.md) (external-tier IA)
- [.cursor/skills/documentation-en-pt-br/SKILL.md](../../.cursor/skills/documentation-en-pt-br/SKILL.md)
