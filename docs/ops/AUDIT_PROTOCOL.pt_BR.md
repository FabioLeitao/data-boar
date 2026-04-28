# Protocolo de auditoria — registro de rituais e contratos (Bancada do Adam Savage)

**English:** [AUDIT_PROTOCOL.md](AUDIT_PROTOCOL.md)

> *"A ferramenta que não funciona não fica na bancada."* — diretiva do operador,
> trigger Slack 2026-04-28. Adam Savage / Tested.com — **first-order
> retrievability**.

Este arquivo é o **registro único** onde toda mudança em um **ritual**,
**contrato**, **guardrail** ou **doutrina de agente** do Data Boar precisa
ser anotada **antes** de o chat / sessão que a propôs ser fechado. É a
*trilha de papel* que as inspirações já exigem (NASA "test what you fly",
Usagi Electric "registre cada beco sem saída como evidência", Cloudflare
"publique o RCA com números"), mas reunida em **um** lugar para que um
auditor consiga responder em segundos:

> *"O que mudou no nosso protocolo no dia `X`, quem disparou e onde está a
> evidência de PR / ADR / teste?"*

Não substitui [`docs/adr/`](../adr/README.md) (decisões de arquitetura),
[`docs/plans/PLANS_TODO.md`](../plans/PLANS_TODO.md) (sequenciamento), nem
nenhum dos manifestos em
[`docs/ops/inspirations/`](inspirations/INSPIRATIONS_HUB.md). Ele **aponta**
para eles.

---

## 1. Os três contratos (texto canônico)

Estes três contratos vieram da diretiva do operador no Slack
(2026-04-28, *"Bancada de Adam Savage"*) e agora são obrigatórios para todo
agente, contribuidor e mantenedor que mexer neste repositório.

### Contrato 1 — Disciplina de bancada (ferramenta órfã sai)

> *"Ferramenta que não funciona não fica na bancada."*

- Scripts em [`scripts/`](../../scripts/) e wrappers citados em
  [`docs/ops/TOKEN_AWARE_SCRIPTS_HUB.md`](TOKEN_AWARE_SCRIPTS_HUB.md) PRECISAM
  estar acessíveis a partir de pelo menos um dos seguintes: um runbook
  documentado, uma regra `.cursor/rules/*.mdc`, um teste, ou um job de CI.
- Scripts **mortos** (sem chamador, sem regra, sem doc) PRECISAM ser
  rewireados ou **removidos em um PR `chore(scripts):` dedicado, com a
  justificativa registrada neste changelog**. Deletes em massa sem essa
  linha de auditoria são rejeitados pelo mesmo motivo que claims fabricadas
  de CodeQL (ver PRs #281, #289).
- Doutrina de referência:
  [`inspirations/ENGINEERING_BENCH_DISCIPLINE.md`](inspirations/ENGINEERING_BENCH_DISCIPLINE.md)
  §2 (a bancada) e §5 (do / don't).

### Contrato 2 — Mudanças de ritual / contrato são registradas aqui, antes de fechar o chat

> *"Toda mudança de ritual ou contrato precisa ser registrada em
> `docs/ops/AUDIT_PROTOCOL.md` antes de fechar o chat."*

- "**Ritual**" significa: uma session keyword, uma regra
  `.cursor/rules/*.mdc`, um bullet do `AGENTS.md` que muda comportamento do
  agente, um portão do `scripts/check-all`, ou um guard de CI (limiar do
  Bandit, seleção do Ruff, política do Semgrep, query pack do CodeQL).
- "**Contrato**" significa: qualquer promessa para o operador — postura de
  lock no banco, limites de amostragem, hierarquia de fallback, atribuição
  de statement, política de pin de supply Colleague-Nn, fluxo de cópia da página
  do Hub, sequenciamento de release, mirrors do private-stack.
- A regra vale para **todo** PR que mexa em uma dessas superfícies. A linha
  do changelog na §3 é **parte do diff do PR** — não é follow-up.
- Um PR que altera ritual mas **não** adiciona linha aqui PRECISA ser
  apontado pelo revisor e corrigido antes do merge. O guard estrutural em
  [`tests/test_audit_protocol_registry.py`](../../tests/test_audit_protocol_registry.py)
  garante apenas que o **arquivo** continue presente e bem-formado.

### Contrato 3 — Warning de Integridade antes de violação da Doutrina NASA

> *"Se você detectar que o Founder está pedindo algo que viola a Doutrina
> NASA (ex.: pular testes), você deve dar um Warning de Integridade antes
> de executar."*

- "**Doutrina NASA**" neste repo é a união de:
  - [`inspirations/DEFENSIVE_SCANNING_MANIFESTO.md`](inspirations/DEFENSIVE_SCANNING_MANIFESTO.md)
    (limites de amostragem, sem DDL, sem locks exclusivos, atribuição de
    statement).
  - [`inspirations/THE_ART_OF_THE_FALLBACK.md`](inspirations/THE_ART_OF_THE_FALLBACK.md)
    (sem demoção silenciosa, hierarquia monotônica de fallback).
  - [`inspirations/ENGINEERING_BENCH_DISCIPLINE.md`](inspirations/ENGINEERING_BENCH_DISCIPLINE.md)
    (`check-all` é o portão de segurança; *verde ou conserta*; nunca
    *quase verde*).
  - [`SECURITY.md`](../../SECURITY.md) e os pins de supply Colleague-Nn em
    [ADR 0005](../adr/0005-ci-github-actions-supply-Colleague-Nn-pins.md).
- Exemplos que EXIGEM Warning de Integridade **antes** de qualquer ação:
  - "pula o teste que falhou", "usa `--no-verify`", "ignora Bandit High",
    "merge com CodeQL vermelho", "apaga o pre-commit pra entregar mais
    rápido", "usa `time.sleep` pra contornar contenção de lock no banco",
    "force-push em cima de uma trilha de evidência documentada", "reescreve
    histórico no clone canônico".
- Formato do warning (no mesmo chat, voltado para o operador):
  1. **O que foi pedido** (uma linha, neutro).
  2. **Qual cláusula da doutrina é tocada** (cite arquivo + seção).
  3. **Por que isso importa operacionalmente** (uma linha: risco de
     regressão, perda de evidência, impacto no banco do cliente, exposição
     de supply Colleague-Nn, …).
  4. **Alternativa mais segura** (uma proposta concreta).
  5. **Pergunta explícita:** *"Confirma que ainda quer que eu execute?"*
- O warning PRECISA ser emitido **antes** da ação. Emitir *depois* dos fatos
  é o mesmo modo de falha do fallback silencioso (Cláusula §3 do manifesto
  de fallback) e é rejeitado.

---

## 2. Como agentes usam este arquivo

Para todo PR ou sessão que mude um ritual / contrato / guardrail:

1. Identifique qual contrato está sendo tocado (Bancada, Registro, Warning
   de Integridade, ou um dos manifestos doutrinais).
2. Adicione uma nova linha no changelog em §3 com: data, autor / agente,
   título curto, contrato tocado, link de evidência (número de PR, ADR,
   teste, regra).
3. Garanta que
   [`tests/test_audit_protocol_registry.py`](../../tests/test_audit_protocol_registry.py)
   continua passando (o teste só checa **estrutura**, não conteúdo —
   conteúdo é trabalho do revisor humano).
4. Se a mudança é doutrinal, abra ou atualize também o ADR correspondente
   em [`docs/adr/`](../adr/README.md) e linke na linha.

> O registro é **append-only no espírito** — correções vêm como uma *nova*
> linha apontando para a antiga ("supersedes linha YYYY-MM-DD-NN"), não
> editando histórico. Isto espelha a disciplina de trilha de commits em
> [PRIVATE_STACK_SYNC_RITUAL.md](PRIVATE_STACK_SYNC_RITUAL.md) e
> [`.cursor/rules/operator-evidence-backup-no-rhetorical-asks.mdc`](../../.cursor/rules/operator-evidence-backup-no-rhetorical-asks.mdc).

---

## 3. Changelog (append-only, mais recente no topo)

| Data (UTC) | ID | Título | Contrato(s) tocado(s) | Autor / agente | Evidência |
| ---------- | -- | ------ | --------------------- | -------------- | --------- |
| 2026-04-28 | 2026-04-28-01 | Criação do `AUDIT_PROTOCOL.md`; codificação dos três contratos (Bancada / Registro / Warning de Integridade); guard estrutural de regressão. | Os três (este arquivo *é* o registro e codifica o rito do Warning). | SRE Automation Agent, branch `cursor/data-boar-agent-protocol-5ee8` | Este PR; `tests/test_audit_protocol_registry.py`. |

---

## 4. O que este arquivo **não** é

- **Não** é um ADR. ADRs explicam *por quê* uma escolha de arquitetura foi
  feita ([template](../adr/0001-record-architecture-decisions.md)). O
  changelog aqui é um índice de *baixa resolução* que aponta para o ADR.
- **Não** substitui `git log`. A linha de auditoria é um ponteiro legível;
  o diff completo vive no PR / commit que ela cita.
- **Não** é lugar para colar segredos, hostnames, achados de cliente, ou
  qualquer outro material de PII / confidencialidade comercial — as regras
  ([`.cursor/rules/private-pii-never-public.mdc`](../../.cursor/rules/private-pii-never-public.mdc),
  [`.cursor/rules/confidential-commercial-never-tracked.mdc`](../../.cursor/rules/confidential-commercial-never-tracked.mdc))
  continuam valendo sem mudança.
- **Não** é lugar para marketing ou promessas de roadmap. É um diário de
  bordo.

---

## 5. Referências cruzadas

- [`AGENTS.md`](../../AGENTS.md) *Quick index* — porta de entrada para
  assistentes.
- [`docs/ops/inspirations/INSPIRATIONS_HUB.md`](inspirations/INSPIRATIONS_HUB.md)
  — catálogo de doutrina ao lado deste registro.
- [`docs/ops/COMMIT_AND_PR.md`](COMMIT_AND_PR.md) — quando registrar a linha
  durante o ritual de commit/PR.
- [`docs/adr/README.md`](../adr/README.md) — quando a mudança de ritual
  merece um ADR completo junto da linha.
- [`tests/test_audit_protocol_registry.py`](../../tests/test_audit_protocol_registry.py)
  — guard estrutural.
