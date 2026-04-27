# Hub de inspirações (comece aqui)

**English:** [INSPIRATIONS_HUB.md](INSPIRATIONS_HUB.md)

Página única de **navegação** para **insumos externos** escolhidos pelo mantenedor que moldam roadmap do Data Boar, tom de documentação e hardening — sem virar política automática.

**Pasta:** [`docs/ops/inspirations/`](README.pt_BR.md) (este diretório).

---

## Security / GRC (hardening, tom de compliance, enquadramento de ameaças)

| Documento                                                                                                                                   | O que é                                                                                                                                                                                                                                                                                                                                                                    |
| ------------------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| [SECURITY_NOW.md](SECURITY_NOW.md)                                                                                                          | Nota de fonte: **Security Now** (GRC) — perspectiva operacional de segurança em série.                                                                                                                                                                                                                                                                                     |
| [OWASP.md](OWASP.md)                                                                                                                        | Projetos e guias OWASP — padrões de segurança de aplicação.                                                                                                                                                                                                                                                                                                                |
| [CISA_KEV_AND_ADVISORIES.md](CISA_KEV_AND_ADVISORIES.md)                                                                                    | KEV e advisories CISA — insumos para priorizar patch/exposição.                                                                                                                                                                                                                                                                                                            |
| [SUPPLY_CHAIN_AND_TRUST_SIGNALS.pt_BR.md](SUPPLY_CHAIN_AND_TRUST_SIGNALS.pt_BR.md) · [EN](SUPPLY_CHAIN_AND_TRUST_SIGNALS.md)                | Cadeia de suprimentos + **sinais de confiança**: **fail-open** em registry/marketplace, **shadow AI** vs governança, padrão **Trivy mar/2026** em CI/advisories — liga a mitigações ([ADR 0005](../../adr/0005-ci-github-actions-supply-chain-pins.md), lockfile, audit, roadmap SBOM). **pt-BR:** espelho curto do bloco **follow-ups adiados**; nota completa em **EN**. |
| [WAZUH_NIST_CIS_LABOP_ALIGNMENT.pt_BR.md](WAZUH_NIST_CIS_LABOP_ALIGNMENT.pt_BR.md) · [EN](WAZUH_NIST_CIS_LABOP_ALIGNMENT.md)                | Índice da documentação oficial **Wazuh** (componentes, instalação, casos de uso) para aprendizado no **LAB-OP**; mapeamento **NIST CSF** + **CIS Controls** ao escopo honesto Data Boar vs **Detect/Recover** no homelab — não é certificação.                                                                                                                             |
| [LAB_OP_OBSERVABILITY_LEARNING_LINKS.pt_BR.md](LAB_OP_OBSERVABILITY_LEARNING_LINKS.pt_BR.md) · [EN](LAB_OP_OBSERVABILITY_LEARNING_LINKS.md) | **Nota mental:** favoritos de documentação oficial para **Grafana, Prometheus, Loki, Graylog, OpenSearch, Elasticsearch, OTel, Jaeger, Tempo, SigNoz, Netdata**; **Grafana Cloud** (free tier) + cuidado com SaaS estilo **Dynatrace** — alinha a [PLAN_LAB_OP_OBSERVABILITY_STACK.pt_BR.md](../../plans/PLAN_LAB_OP_OBSERVABILITY_STACK.pt_BR.md).                        |
| [ENTERPRISE_DB_OPS_AND_GRC_EVIDENCE.pt_BR.md](ENTERPRISE_DB_OPS_AND_GRC_EVIDENCE.pt_BR.md) · [EN](ENTERPRISE_DB_OPS_AND_GRC_EVIDENCE.md)    | Temas de operação estilo **Oracle-DBA** (prova de backup/restore, patching, segregação) + grades genéricas de templates **GRC/cyber** — o que **exportações** do Data Boar podem anexar vs fora de escopo (runbooks DBA/SOC).                                                                                                                                              |
| [QUALYS_THREAT_RESEARCH.pt_BR.md](QUALYS_THREAT_RESEARCH.pt_BR.md)                                                                          | Blog TRU / vulnerabilidades Qualys — divulgação coordenada em formato longo (ex.: AppArmor “CrackArmor”), enquadramento de risco de kernel/infra.                                                                                                                                                                                                                          |
| [SECURITY_INSPIRATION_GRC_SECURITY_NOW.md](../SECURITY_INSPIRATION_GRC_SECURITY_NOW.pt_BR.md)                                               | Ponte para operadores: como **consumimos** insight estilo Security Now no repositório.                                                                                                                                                                                                                                                                                     |

**Pessoas (detalhe sob Security/GRC):** **Steve Gibson** é a voz pública principal do **Security Now**; o tratamento completo fica nas notas acima. Um **ponteiro curto** também está em [ENGINEERING_CRAFT_INSPIRATIONS.pt_BR.md](ENGINEERING_CRAFT_INSPIRATIONS.pt_BR.md) pelo ângulo de **narrativa explicativa** (sem duplicar política).

---

## Doutrina (manifestos normativos)

Manifestos curtos e normativos que consolidam o **DNA de engenharia** do
Data Boar. Cada arquivo enuncia regras de **faça / não faça**, cita as
sementes de mentor e aponta para o código ou regra que já força a doutrina.

| Documento                                                                                | Sementes                                                       | Escopo                                                                                                                                    |
| --------                                                                                 | --------                                                       | ------                                                                                                                                    |
| [THE_ART_OF_THE_FALLBACK.pt_BR.md](THE_ART_OF_THE_FALLBACK.pt_BR.md)                     | Usagi Electric · The 8-Bit Guy                                 | Hierarquia de fallback: Parser SQL → Regex → String crua; nunca falhar em silêncio.                                                       |
| [DEFENSIVE_SCANNING_MANIFESTO.pt_BR.md](DEFENSIVE_SCANNING_MANIFESTO.pt_BR.md)           | NASA SEL · Cloudflare · Steve Gibson                           | Tetos de amostragem, statement timeouts, postura `WITH (NOLOCK)`, comentários SQL líderes, regra "convidado no banco do cliente".         |
| [ENGINEERING_BENCH_DISCIPLINE.pt_BR.md](ENGINEERING_BENCH_DISCIPLINE.pt_BR.md)           | Adam Savage · Julia Evans (b0rk) · Aviões e Músicas            | Ergonomia de bancada, cultura de checklist, logs narrados.                                                                                |
| [INTERNAL_DIAGNOSTIC_AESTHETICS.pt_BR.md](INTERNAL_DIAGNOSTIC_AESTHETICS.pt_BR.md)       | Mark Russinovich (Sysinternals)                                | Como `--verbose`, `completão -Privileged` e o JSON de auditoria devem *parecer* — classe de diagnóstico de baixo nível.                   |
| [ACTIONABLE_GOVERNANCE_AND_TRUST.pt_BR.md](ACTIONABLE_GOVERNANCE_AND_TRUST.pt_BR.md)     | Narrativa Tailscale · Charity Majors (Honeycomb) · Cloudflare  | O relatório executivo entrega o *caminho da cura* (APG); o sistema se explica.                                                            |

Plano motor: [PLAN_ENGINEERING_DOCTRINE_CONSOLIDATION.md](../../plans/PLAN_ENGINEERING_DOCTRINE_CONSOLIDATION.md).

---

## Craft de engenharia (pessoas, produtos, narrativa)

| Documento                                                                                             | O que é                                                                                                                                                                                     |
| ----------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| [ENGINEERING_CRAFT_INSPIRATIONS.pt_BR.md](ENGINEERING_CRAFT_INSPIRATIONS.pt_BR.md)                    | Tabela de **desenvolvedores, canais ou produtos** (ferramentas estilo Sysinternals, educadores em vídeo, linhagem TiddlyWiki, etc.) com **por que importa** para o Data Boar.               |
| [ENGINEERING_CRAFT_ANALYSIS.pt_BR.md](ENGINEERING_CRAFT_ANALYSIS.pt_BR.md)                            | **Nota de fonte** curta: liga a tabela à análise profunda (mesmo papel de [SECURITY_NOW.md](SECURITY_NOW.md) para Security Now).                                                            |
| [ENGINEERING_CRAFT_INSPIRATION_ANALYSIS.pt_BR.md](../ENGINEERING_CRAFT_INSPIRATION_ANALYSIS.pt_BR.md) | **Análise profunda**: clusters temáticos, imitar/evitar, fluxo, checklist — paralelo a [SECURITY_INSPIRATION_GRC_SECURITY_NOW.pt_BR.md](../SECURITY_INSPIRATION_GRC_SECURITY_NOW.pt_BR.md). |

Use ao desenhar features, docs de operador ou “como explicamos trade-offs” — ainda **não** substitui modelagem de ameaças ou testes.

---

## Como estender

1. Acrescentar linha ao arquivo de tabela / nota certa (security vs engineering).
2. Manter entradas **curtas**; link para profundidade fora (craft de engenharia: atualizar [ENGINEERING_CRAFT_INSPIRATION_ANALYSIS.pt_BR.md](../ENGINEERING_CRAFT_INSPIRATION_ANALYSIS.pt_BR.md) quando **temas transversais** mudarem, não a cada linha nova).
3. Se alguém cobre os dois eixos (ex.: segurança + narrativa), pôr **detalhe** em Security/GRC e **ponteiro** em craft se fizer sentido.

---

## Relacionado (fora desta pasta)

- [Canais de notificação ao operador](../OPERATOR_NOTIFICATION_CHANNELS.pt_BR.md) — como CI/alertas chegam a humanos (assunto distinto do conteúdo de inspiração).

