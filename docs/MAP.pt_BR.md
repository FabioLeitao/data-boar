# Mapa de tópicos da documentação (navegação por preocupação)

**English:** [MAP.md](MAP.md)

Esta página é um **índice por preocupação**: liga perguntas de alto nível (o que importa para **CISO**, **DPO** ou **arquiteto de segurança**) aos guias onde comportamento, chaves de config e limites estão descritos. Use quando já souber o tema (ex.: menores, hints de jurisdição) e quiser o caminho mais curto sem vasculhar pastas. O índice plano completo continua em **[README.pt_BR.md](README.pt_BR.md)** ([EN](README.md)).

---

## Dados de menores e privacidade infantil (âmbito técnico)

| Pergunta | Leia primeiro | Config / comportamento | Relacionados |
| -------- | ------------- | ------------------------ | ------------- |
| Como o produto marca dados de **possível menor** (DDN/idade), limiares, varredura opcional ampliada e cruzamento? | **[MINOR_DETECTION.pt_BR.md](MINOR_DETECTION.pt_BR.md)** ([EN](MINOR_DETECTION.md)) | `detection.minor_age_threshold`, `detection.minor_full_scan`, `detection.minor_cross_reference` | [SENSITIVITY_DETECTION.pt_BR.md](SENSITIVITY_DETECTION.pt_BR.md) ([EN](SENSITIVITY_DETECTION.md)), [USAGE.pt_BR.md](USAGE.pt_BR.md) seções `detection` / relatório ([EN](USAGE.md)) |
| **FELCA** (Brasil) e posicionamento de suporte **só a metadados**? | **[COMPLIANCE_FRAMEWORKS.pt_BR.md](COMPLIANCE_FRAMEWORKS.pt_BR.md)** — *Padrões auditáveis e de gestão* ([EN](COMPLIANCE_FRAMEWORKS.md)) | Mesmo: flags de menor são para inventário, não verificação de idade | [COMPLIANCE_AND_LEGAL.pt_BR.md](COMPLIANCE_AND_LEGAL.pt_BR.md) ([EN](COMPLIANCE_AND_LEGAL.md)) |
| **EUA** COPPA / AB 2273 / CO CPA menores — amostras YAML **técnicas** (norm tags, sem aconselhamento jurídico)? | **[COMPLIANCE_FRAMEWORKS.pt_BR.md](COMPLIANCE_FRAMEWORKS.pt_BR.md)** — tabela de amostras e disclaimers ([EN](COMPLIANCE_FRAMEWORKS.md)) | Arquivos em [compliance-samples/](compliance-samples/) (ex.: `compliance-sample-us_ftc_coppa.yaml`) | [compliance-samples/README.pt_BR.md](compliance-samples/README.pt_BR.md) ([EN](compliance-samples/README.md)) |

O histórico de desenho da detecção de menores está num plano **concluído** em `docs/plans/completed/` no seu checkout (`PLAN_MINOR_DATA_DETECTION`); o guia do operador acima é o ponto de entrada mantido (sem link para planos aqui, por regras de arquitetura da documentação).

---

## Dicas de jurisdição (heurística, só metadados)

| Pergunta | Leia primeiro | Config / comportamento | Relacionados |
| -------- | ------------- | ------------------------ | ------------- |
| O que são **jurisdiction hints**, para quem são e como ativar (CLI, API, painel, YAML)? | **[USAGE.pt_BR.md](USAGE.pt_BR.md)** — busque **jurisdiction_hints** / **Report info** ([EN](USAGE.md)) | `report.jurisdiction_hints`, `--jurisdiction-hint`, corpo do `POST /scan` | [COMPLIANCE_AND_LEGAL.pt_BR.md](COMPLIANCE_AND_LEGAL.pt_BR.md) ([EN](COMPLIANCE_AND_LEGAL.md)) |
| Por que não são conclusões jurídicas e o que o ADR fixou? | **[ADR 0026](adr/0026-optional-jurisdiction-hints-dpo-facing-heuristic-metadata-only.md)** (inglês) | Índice: [adr/README.pt_BR.md](adr/README.pt_BR.md) ([EN](adr/README.md)) | [COMPLIANCE_TECHNICAL_REFERENCE.pt_BR.md](COMPLIANCE_TECHNICAL_REFERENCE.pt_BR.md) ([EN](COMPLIANCE_TECHNICAL_REFERENCE.md)) |

---

## Detecção sensível e profundidade de compliance (pontes)

| Pergunta | Leia primeiro | Notas |
| -------- | ------------- | ----- |
| Regex, ML/DL, overrides, dicas de formato do conector | **[SENSITIVITY_DETECTION.pt_BR.md](SENSITIVITY_DETECTION.pt_BR.md)** ([EN](SENSITIVITY_DETECTION.md)) | Complementa [USAGE.pt_BR.md](USAGE.pt_BR.md) relatório e chaves `detection` ([EN](USAGE.md)) |
| Norm tags, amostras, operação multirregional | **[COMPLIANCE_FRAMEWORKS.pt_BR.md](COMPLIANCE_FRAMEWORKS.pt_BR.md)** ([EN](COMPLIANCE_FRAMEWORKS.md)) | Inclui subseção setor segurador BR e tabela de amostras |
| Encodings, limites de API, postura de evidência (TI / DPO) | **[COMPLIANCE_TECHNICAL_REFERENCE.pt_BR.md](COMPLIANCE_TECHNICAL_REFERENCE.pt_BR.md)** ([EN](COMPLIANCE_TECHNICAL_REFERENCE.md)) | Limites operacionais, não aconselhamento jurídico |

---

## Onde isso se encaixa

- **Instalação e execução técnicas:** [TECH_GUIDE.pt_BR.md](TECH_GUIDE.pt_BR.md) ([EN](TECH_GUIDE.md)) termina com um ponteiro **Topic map** de volta a esta página.
- **Glossário (termos por tema):** [GLOSSARY.pt_BR.md](GLOSSARY.pt_BR.md) ([EN](GLOSSARY.md)).

Se faltar um tema neste mapa, inclua uma linha em **MAP.md** e **MAP.pt_BR.md** no mesmo PR.
