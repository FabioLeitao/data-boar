# Hub de inspirações (comece aqui)

**English:** [INSPIRATIONS_HUB.md](INSPIRATIONS_HUB.md)

Página única de **navegação** para **insumos externos** escolhidos pelo mantenedor que moldam roadmap do Data Boar, tom de documentação e hardening — sem virar política automática.

**Pasta:** [`docs/ops/inspirations/`](README.pt_BR.md) (este diretório).

---

## Security / GRC (hardening, tom de compliance, enquadramento de ameaças)

| Documento | O que é |
| --------- | ------- |
| [SECURITY_NOW.md](SECURITY_NOW.md) | Nota de fonte: **Security Now** (GRC) — perspectiva operacional de segurança em série. |
| [OWASP.md](OWASP.md) | Projetos e guias OWASP — padrões de segurança de aplicação. |
| [CISA_KEV_AND_ADVISORIES.md](CISA_KEV_AND_ADVISORIES.md) | KEV e advisories CISA — insumos para priorizar patch/exposição. |
| [QUALYS_THREAT_RESEARCH.pt_BR.md](QUALYS_THREAT_RESEARCH.pt_BR.md) | Blog TRU / vulnerabilidades Qualys — divulgação coordenada em formato longo (ex.: AppArmor “CrackArmor”), enquadramento de risco de kernel/infra. |
| [SECURITY_INSPIRATION_GRC_SECURITY_NOW.md](../SECURITY_INSPIRATION_GRC_SECURITY_NOW.pt_BR.md) | Ponte para operadores: como **consumimos** insight estilo Security Now no repositório. |

**Pessoas (detalhe sob Security/GRC):** **Steve Gibson** é a voz pública principal do **Security Now**; o tratamento completo fica nas notas acima. Um **ponteiro curto** também está em [ENGINEERING_CRAFT_INSPIRATIONS.pt_BR.md](ENGINEERING_CRAFT_INSPIRATIONS.pt_BR.md) pelo ângulo de **narrativa explicativa** (sem duplicar política).

---

## Craft de engenharia (pessoas, produtos, narrativa)

| Documento | O que é |
| --------- | ------- |
| [ENGINEERING_CRAFT_INSPIRATIONS.pt_BR.md](ENGINEERING_CRAFT_INSPIRATIONS.pt_BR.md) | Tabela de **desenvolvedores, canais ou produtos** (ferramentas estilo Sysinternals, educadores em vídeo, linhagem TiddlyWiki, etc.) com **por que importa** para o Data Boar. |
| [ENGINEERING_CRAFT_ANALYSIS.pt_BR.md](ENGINEERING_CRAFT_ANALYSIS.pt_BR.md) | **Nota de fonte** curta: liga a tabela à análise profunda (mesmo papel de [SECURITY_NOW.md](SECURITY_NOW.md) para Security Now). |
| [ENGINEERING_CRAFT_INSPIRATION_ANALYSIS.pt_BR.md](../ENGINEERING_CRAFT_INSPIRATION_ANALYSIS.pt_BR.md) | **Análise profunda**: clusters temáticos, imitar/evitar, fluxo, checklist — paralelo a [SECURITY_INSPIRATION_GRC_SECURITY_NOW.pt_BR.md](../SECURITY_INSPIRATION_GRC_SECURITY_NOW.pt_BR.md). |

Use ao desenhar features, docs de operador ou “como explicamos trade-offs” — ainda **não** substitui modelagem de ameaças ou testes.

---

## Como estender

1. Acrescentar linha ao arquivo de tabela / nota certa (security vs engineering).
1. Manter entradas **curtas**; link para profundidade fora (craft de engenharia: atualizar [ENGINEERING_CRAFT_INSPIRATION_ANALYSIS.pt_BR.md](../ENGINEERING_CRAFT_INSPIRATION_ANALYSIS.pt_BR.md) quando **temas transversais** mudarem, não a cada linha nova).
1. Se alguém cobre os dois eixos (ex.: segurança + narrativa), pôr **detalhe** em Security/GRC e **ponteiro** em craft se fizer sentido.

---

## Relacionado (fora desta pasta)

- [Canais de notificação ao operador](../OPERATOR_NOTIFICATION_CHANNELS.pt_BR.md) — como CI/alertas chegam a humanos (assunto distinto do conteúdo de inspiração).
