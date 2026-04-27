# Governança acionável e confiança (doutrina Data Boar)

**English:** [ACTIONABLE_GOVERNANCE_AND_TRUST.md](ACTIONABLE_GOVERNANCE_AND_TRUST.md)

> **Sementes:** [Disciplina narrativa da Tailscale](https://tailscale.com/blog) ·
> [Charity Majors / Honeycomb](https://charity.wtf/) ·
> [Post-mortems da Cloudflare](https://blog.cloudflare.com/)
>
> *"O sistema precisa se explicar. O relatório não entrega achados — entrega o
> caminho da cura."*

Este é um **manifesto doutrinário** sobre o entregável para o cliente: o
relatório executivo, o Action Plan Generator (APG) e a narrativa em torno
deles. O padrão é **observabilidade + ação**: o stakeholder precisa
conseguir ler o artefato e saber o que *fazer* a seguir.

---

## 1. O contrato do entregável

Um engajamento Data Boar deixa três artefatos na mesa:

1. **Markdown executivo** — saída do `data-boar-report`, narrativa
   grau-stakeholder, gerada a partir de um `session_id` fixo.
2. **Manifesto YAML do scan** — `scan_manifest_*.yaml`, evidência
   legível por máquina que ancora cada afirmação do Markdown.
3. **Invocação reprodutível do CLI** — o comando exato do `data-boar-report`
   e a sessão SQLite que o alimenta.

Esses três juntos formam o "triângulo da confiança". Tirar qualquer um
transforma o entregável em um deck de slide — **não** é por isso que o
cliente está pagando.

As sementes desta postura:

- **Tailscale** — quando algo está dando errado, o produto escreve uma
  página *curta, honesta, acionável* dizendo o que aconteceu e o que fazer.
  Sem amortecimento corporativo.
- **Charity Majors / Honeycomb** — *o sistema precisa se explicar*. Se o
  operador precisa ler o código-fonte para saber o que aconteceu, a
  observabilidade falhou.
- **Post-mortems da Cloudflare** — evidência numérica, com timestamp, com a
  seção "o que mudamos" claramente visível.

---

## 2. O Action Plan Generator (APG) — o "caminho da cura"

A seção **4 — Plano de ação (APG)** do Markdown executivo **não** é uma
lista ordenada de achados. É o *caminho da cura* do cliente.

Estrutura obrigatória (já forçada por
[`report/executive_report.py`](../../../report/executive_report.py)):

| Subseção | Propósito | Voz |
| -------- | --------- | --- |
| `### 4.1 Prioridades imediatas (Top 3)` | As três ações de maior alavancagem. | Imperativa, uma frase cada. |
| `### 4.2 Inventário por tipo de dado (achado → risco → recomendação técnica)` | Inventário completo por padrão. | Três colunas, sem ponte narrativa. |

**Doutrina:**

- Cada item do `Top 3` precisa ser **executável pelo cliente**, não por
  nós. Se o conserto exige feature nova do Data Boar, isso vai para a
  Seção 5 (notas de roadmap), não para a Seção 4.
- Cada linha de inventário precisa citar um **padrão**, uma **classe de
  risco** e uma **mitigação técnica** — sem "revisar e mitigar" vago.
- Sem amostra crua de célula. Sem tupla tabela/coluna que vazaria o dado
  real do cliente para o entregável. Só contagens e padrões — ver
  [`docs/REPORTS_AND_COMPLIANCE_OUTPUTS.md`](../../REPORTS_AND_COMPLIANCE_OUTPUTS.md).

O APG existe porque *achado sem caminho de mitigação é entrega de
ansiedade, não de segurança*. A gente não vende ansiedade.

---

## 3. A metodologia da segurança (Seção 3)

A seção **3 — Metodologia e segurança** do Markdown é onde provamos que
fomos um bom convidado no banco do cliente. Ela cita:

- Os tetos de amostragem efetivamente aplicados (por dialeto).
- O statement timeout em milissegundos.
- A postura por dialeto (`WITH (NOLOCK)` para SQL Server,
  `TABLESAMPLE SYSTEM` para PostgreSQL etc.).
- O comentário SQL líder usado para rastreabilidade pelo DBA.
- A **última degradação de fallback** quando ocorreu na sessão (referência
  cruzada
  [`THE_ART_OF_THE_FALLBACK.pt_BR.md`](THE_ART_OF_THE_FALLBACK.pt_BR.md)).

Esta seção é o mesmo motivo pelo qual o piloto assina o caderno de
manutenção: ela torna o contrato de
[`DEFENSIVE_SCANNING_MANIFESTO.pt_BR.md`](DEFENSIVE_SCANNING_MANIFESTO.pt_BR.md)
auditável *depois* do fato, não só *durante* o scan.

**Slice 3 do [PLAN_ENGINEERING_DOCTRINE_CONSOLIDATION.md](../../plans/PLAN_ENGINEERING_DOCTRINE_CONSOLIDATION.md)**
estende esta seção com prosa explícita: "tratamos este banco do mesmo jeito
que um piloto trata uma turbina em operação".

---

## 4. O sistema se explica (postura Honeycomb)

Os entregáveis respondem a três perguntas de "auto-explicação" sem o
operador no telefone:

| Pergunta | Onde mora a resposta |
| -------- | -------------------- |
| *O que o Data Boar fez, e em que escopo?* | Markdown § 2 + `audit_trail` no manifesto. |
| *O Data Boar respeitou o banco enquanto fazia isso?* | Markdown § 3 + `safety_tags` no manifesto. |
| *O que o cliente deve fazer, em que ordem?* | Markdown § 4 (APG) + § 5 (notas de roadmap). |

Se um stakeholder não consegue responder a uma dessas só lendo o artefato,
isso é **bug doutrinário** — abre como linha em `PLAN_*.md`, não como
escapatória "explicamos na call".

---

## 5. Faça / não faça (checklist de revisão)

### Faça

- Trate o relatório executivo como **superfície de produto** — todo PR que
  mexe nas seções dele atualiza `tests/test_executive_report*.py`.
- Coloque o APG antes da tabela de achados quando o público é
  não-técnico.
- Cite a última degradação de fallback e o teto de amostragem real, não
  "best-effort sampling" genérico.
- Para cada afirmação no Markdown, deixe um campo do manifesto que o
  revisor consegue grepar.

### Não faça

- Não escreva "score de densidade de vulnerabilidade" nem qualquer métrica
  composta sem derivação determinística no código. Ver a regra *sem
  números inventados* em
  [`INTERNAL_DIAGNOSTIC_AESTHETICS.pt_BR.md`](INTERNAL_DIAGNOSTIC_AESTHETICS.pt_BR.md) §4.
- Não substitua o APG por uma visão "só heatmap de risco". Heatmap é
  decoração sem plano de ação anexo.
- Não condicione a Seção 3 (metodologia) a "se o operador ligou auditoria
  verbosa". A Seção 3 está **sempre** presente; o que muda é a
  profundidade do manifesto.

---

## 6. Onde isso é forçado

| Camada | Arquivo |
| ------ | ------- |
| Seções do Markdown executivo | [`report/executive_report.py`](../../../report/executive_report.py) |
| Schema do manifesto de varredura | [`report/scan_evidence.py`](../../../report/scan_evidence.py) · [`schemas/`](../../../schemas/) |
| Engine de recomendação (insumos do APG) | [`report/recommendation_engine.py`](../../../report/recommendation_engine.py) |
| Testes | `tests/test_executive_report*.py` · `tests/test_scan_evidence.py` |
| Narrativa do operador | [`docs/REPORTS_AND_COMPLIANCE_OUTPUTS.md`](../../REPORTS_AND_COMPLIANCE_OUTPUTS.md) · [`docs/plans/BENCHMARK_EVOLUTION.md`](../../plans/BENCHMARK_EVOLUTION.md) §1 |

---

## 7. Relacionado

- [`DEFENSIVE_SCANNING_MANIFESTO.pt_BR.md`](DEFENSIVE_SCANNING_MANIFESTO.pt_BR.md) —
  o que prometemos para o banco.
- [`THE_ART_OF_THE_FALLBACK.pt_BR.md`](THE_ART_OF_THE_FALLBACK.pt_BR.md) —
  o que prometemos sobre resiliência.
- [`INTERNAL_DIAGNOSTIC_AESTHETICS.pt_BR.md`](INTERNAL_DIAGNOSTIC_AESTHETICS.pt_BR.md) —
  como a auditoria embaixo se parece.
- [`ENGINEERING_BENCH_DISCIPLINE.pt_BR.md`](ENGINEERING_BENCH_DISCIPLINE.pt_BR.md) —
  a bancada que produz esses artefatos de modo repetível.

O cliente fica com o relatório depois que o engajamento acaba. Ele precisa
continuar útil em seis meses, sem operador de plantão. O padrão é esse.
