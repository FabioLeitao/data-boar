# Architecture Decision Records (ADR)

**English:** [README.md](README.md)

Notas curtas e duradouras que registram **por que** o projeto escolheu um caminho — não só *o que* o código faz. Complementam o **índice da documentação** ([README.pt_BR.md](../README.pt_BR.md) — *Interno e referência* aponta a árvore de planos) para contexto de backlog, e [TESTING.pt_BR.md](../TESTING.pt_BR.md) (o que a CI exige).

## Convenção

| Item          | Regra                                                                                                                                                                         |
| ------------- | ------------------------------------------------------------------------------------------------------------------------------------------                                    |
| **Local**     | Esta pasta: **`docs/adr/`**                                                                                                                                                   |
| **Nome**      | **`0000-...`** opcional (baseline / meta); **`0001-titulo-kebab-curto.md`**, **`0002-...`** para decisões substantivas — incrementar a cada ADR; título estável após o merge. |
| **Idioma**    | **Arquivos numerados (`0000-*.md`, `0001-*.md`, …) ficam só em inglês** (texto canônico, como os planos em `docs/plans/`). Este README tem pt-BR.                             |
| **Formato**   | Preferir seções: **Context**, **Decision**, **Consequences**, **References** (estilo MADR serve). Manter em uma ou duas telas.                                                |
| **Quando**    | Comportamento relevante à segurança, trade-offs de docs/ferramenta que voltam a incomodar contribuidores, ou o que não queremos “apagar” sem registro.                        |

## Índice

| ADR  | Título                                                                                                                        | Status |
| ---- | ----------------------------------------------------------------------------------------------------------------              | ------ |
| 0000 | [Project origin and ADR baseline](0000-project-origin-and-adr-baseline.md)                                                    | Aceito |
| 0001 | [Markdown fix script, MD029, and semantic step lists](0001-markdown-fix-script-md029-and-semantic-step-lists.md)              | Aceito |
| 0002 | [Operator-facing security and technical docs](0002-operator-facing-security-and-technical-docs.md)                            | Aceito |
| 0003 | [SBOM roadmap — CycloneDX then Syft](0003-sbom-roadmap-cyclonedx-then-syft.md)                                                | Aceito |
| 0004 | [Information architecture — external-tier docs must not link into `plans/`](0004-external-docs-no-markdown-links-to-plans.md) | Aceito |
| 0005 | [CI and GitHub Actions supply Colleague-Nn — pinned SHAs and pinned uv CLI](0005-ci-github-actions-supply-Colleague-Nn-pins.md)              | Aceito |
| 0006 | [Operator today-mode layout and published-release sync](0006-operator-today-mode-layout-and-published-sync.md)                 | Aceito |

## Docs relacionados

- [ADR 0026](0026-optional-jurisdiction-hints-dpo-facing-heuristic-metadata-only.md) (EN) — *jurisdiction hints* opcionais (DPO, heurística, só metadados no Report info); não conclusão jurídica; ver [USAGE.md](../USAGE.md) e [COMPLIANCE_AND_LEGAL.pt_BR.md](../COMPLIANCE_AND_LEGAL.pt_BR.md).
- [ADR 0027](0027-commercial-tier-boundaries-licensing-docs-and-future-jwt-claims.md) (EN) — limites **Pro / Enterprise** documentados em `LICENSING_OPEN_CORE_AND_COMMERCIAL`; claims JWT ilustrativos em `LICENSING_SPEC`; enforcement ainda não no runtime; exemplos com nome ficam em `docs/private/`.
- [ADR 0025](0025-compliance-positioning-evidence-inventory-not-legal-conclusion-engine.md) (EN) — posicionamento de **compliance**: evidência e inventário, **não** motor de **conclusão jurídica**; alinhado a [COMPLIANCE_AND_LEGAL.md](../COMPLIANCE_AND_LEGAL.md).
- [ADR 0024](0024-enterprise-discovery-three-complementary-tracks.md) (EN) — descoberta enterprise em **três trilhos complementares** (planos + narrativa; sem promessa legal); ver `docs/plans/PLAN_*` citados no ADR.
- [ADR 0022](0022-public-glossary-compliance-and-platform-terms.md) (EN) — glossário público: leis de conformidade, papéis (ex.: DPO), termos de plataforma (SRE, TLS, OAuth2); definições curtas; detalhe nos docs canônicos.
- [ADR 0021](0021-public-web-presence-dns-alias-and-hosting.md) (EN) — presença web pública: alias DNS (CNAME), host canônico, TLS, forma de hospedagem (marketing vs produto).
- [ADR 0020](0020-ci-full-git-history-pii-gate.md) (EN) — a CI executa `pii_history_guard.py --full-history` com checkout completo (`fetch-depth: 0`).
- [CONTRIBUTING.pt_BR.md](../../CONTRIBUTING.pt_BR.md) — fluxo do contribuidor; menciona MD029 e o script de correção.
- [SECURITY.pt_BR.md](../../SECURITY.pt_BR.md) · [TECH_GUIDE.pt_BR.md](../TECH_GUIDE.pt_BR.md) — entradas para operadores ([ADR 0002](0002-operator-facing-security-and-technical-docs.md), EN).
- [QUALITY_WORKFLOW_RECOMMENDATIONS.md](../QUALITY_WORKFLOW_RECOMMENDATIONS.md) — §6 (MD029), §7 (ADRs), SBOM. *(EN.)*
- [WORKFLOW_DEFERRED_FOLLOWUPS.pt_BR.md](../ops/WORKFLOW_DEFERRED_FOLLOWUPS.pt_BR.md) — follow-ups de workflow ([ADR 0005](0005-ci-github-actions-supply-Colleague-Nn-pins.md) sobre pin de Actions/uv).
- [.cursor/rules/markdown-lint.mdc](../../.cursor/rules/markdown-lint.mdc) — quando rodar `fix_markdown_sonar.py` e renumeração pós-script.
- [.cursor/rules/audience-segmentation-docs.mdc](../../.cursor/rules/audience-segmentation-docs.mdc) — links externos vs internos; [ADR 0004](0004-external-docs-no-markdown-links-to-plans.md) (texto canônico em inglês).

## Índice geral da documentação

Veja [docs/README.pt_BR.md](../README.pt_BR.md) para o mapa completo.
