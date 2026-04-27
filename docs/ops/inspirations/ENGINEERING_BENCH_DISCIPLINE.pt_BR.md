# Disciplina de bancada de engenharia (doutrina Data Boar)

**English:** [ENGINEERING_BENCH_DISCIPLINE.md](ENGINEERING_BENCH_DISCIPLINE.md)

> **Sementes:** [Adam Savage / Tested.com](https://www.tested.com/) ·
> [Julia Evans (b0rk)](https://jvns.ca/) ·
> [Aviões e Músicas (Lito Sousa)](https://www.youtube.com/@avioesemusicas)
>
> *"Recuperação de primeira ordem. Cultura de checklist. O complexo virando intuitivo."*

Este é um **manifesto doutrinário** sobre como a oficina do Data Boar é
montada — a bancada, os scripts, os logs — para que a próxima pessoa (ou o
próximo agente) consiga sentar e entregar com segurança.

---

## 1. Por que ergonomia de bancada importa

Quando o operador abre o Cursor de manhã, três coisas precisam ser
verdadeiras em poucos minutos:

1. A ferramenta certa para a tarefa está **à mão** — não enterrada em três
   pastas.
2. Existe **checklist** para qualquer ação crítica em segurança (release,
   `completão` de laboratório, operação destrutiva sobre o clone canônico).
3. A saída é **narrada**, não só emitida: um humano consegue ler o log e
   reconstruir o que aconteceu, em que ordem e por quê.

As sementes:

- **Adam Savage** — *recuperação de primeira ordem*: a ferramenta que você
  mais usa fica mais perto da mão. Oficina desorganiza quando esse
  princípio escorrega.
- **Julia Evans** — *o complexo virando intuitivo*. Plano de execução SQL,
  permissões Linux, redes — quando explicados como zines com diagramas,
  deixam de ser arcanos.
- **Aviões e Músicas** — cultura de checklist transplantada da aviação. Voo
  longo começa com um fluxo que até o comandante já rodou mil vezes. O mesmo
  vale para release e smoke do laboratório.

---

## 2. A bancada (onde mora cada ferramenta do Data Boar)

A "bancada" do Data Boar é a pasta `scripts/` somada aos runbooks
documentados. O princípio de **recuperação de primeira ordem** é forçado por
dois hubs:

| Necessidade | Ferramenta de primeira mão |
| ----------- | -------------------------- |
| Gate local completo | `.\scripts\check-all.ps1` (ou `./scripts/check-all.sh`) |
| Só lint (docs/templates) | `.\scripts\lint-only.ps1` |
| Testes alvo | `.\scripts\quick-test.ps1 -Path tests/test_foo.py` |
| Commit + descrição + PR | `.\scripts\commit-or-pr.ps1` |
| Build da imagem de laboratório | `.\scripts\docker-lab-build.ps1` |
| Smoke de orquestração no laboratório | `.\scripts\lab-completao-orchestrate.ps1 -Privileged` |
| Benchmark A/B | `.\scripts\benchmark-ab.ps1` |
| Busca por nome de arquivo (Windows) | `.\scripts\es-find.ps1` |

Índices:

- [`docs/ops/TOKEN_AWARE_SCRIPTS_HUB.md`](../TOKEN_AWARE_SCRIPTS_HUB.md) —
  tabela completa.
- [`.cursor/rules/check-all-gate.mdc`](../../../.cursor/rules/check-all-gate.mdc)
  — tabela diária de comandos.
- [`.cursor/rules/repo-scripts-wrapper-ritual.mdc`](../../../.cursor/rules/repo-scripts-wrapper-ritual.mdc)
  — *use o wrapper antes de reinventar a sequência de shell*.

**Doutrina:** se você se pegar escrevendo um encantamento de shell mais
longo do que três linhas, **pare** e cheque se já existe um wrapper que
codifica esse fluxo. Reinventar custa tokens, esconde bug e reduz
auditabilidade.

---

## 3. Cultura de checklist (Aviões e Músicas)

Piloto roda checklist não porque esqueceu como voar, mas porque o **pico de
carga** no pouso é justamente quando a memória humana falha. Software tem o
mesmo formato: o instante em que se corta uma release, faz merge de um
branch de vários dias ou se roda um passo privilegiado de orquestração.

Os equivalentes no repositório — não são opcionais:

- **Checklist de pré-merge:** `git fetch` → `git status -sb` →
  `.\scripts\check-all.ps1` → revisão do diff → merge.
- **Checklist de pré-release:**
  [`.cursor/rules/release-publish-sequencing.mdc`](../../../.cursor/rules/release-publish-sequencing.mdc)
  — tagueia *antes* de o `-beta` cair em `main`, smoke do Docker, cola texto
  no Hub.
- **Checklist de pré-completão:**
  [`docs/ops/LAB_COMPLETAO_RUNBOOK.md`](../LAB_COMPLETAO_RUNBOOK.md) —
  manifesto fresco, `sudo -n`, raio do impacto, proteção da estação primária.

Checklist pulado em silêncio é o mesmo que checklist nenhum. Testes e
regras forçam esses fluxos para que o checklist rode mesmo com o operador
cansado.

---

## 4. Logs narrados (estilo Julia Evans, b0rk)

Despejo grande de log não é narração. **Narração** é quando um estranho
consegue ler o log um ano depois e reconstruir a história. Os logs do Data
Boar miram esse padrão:

- **Cada passo diz o que está fazendo e por quê** (uma frase curta acima do
  comando).
- **Cada passo imprime o que mudou**, não só o exit code.
- **Erros incluem o próximo passo** ("retry com `-Verbose`", "veja
  [`docs/ops/TROUBLESHOOTING.md`](../TROUBLESHOOTING.md)").
- **Carimbos de tempo** quando a etapa toma mais que poucos segundos.
- **Densidade sem ruído** — cor e símbolo são sinal, não decoração.

Contraexemplo (não fazer):

```text
INFO: starting
INFO: starting
INFO: done
ERROR: 1
```

Melhor (fazer):

```text
[1/4] benchmark legacy   v1.7.3   ...
       wall_time=18.7s   exit=0
[2/4] benchmark current  HEAD     ...
       wall_time=14.2s   exit=0
       Δ=-24% (significativo só se o cluster repetir — ver BENCHMARK_EVOLUTION.md §3)
[3/4] manifest gravado   benchmark_runs/2026-04-27/times.txt
[4/4] arquivo histórico  benchmark_runs/2026-04-27/
```

Mesma informação; o segundo se **explica**. Esse padrão vale para
`completão`, `data-boar-report` e a saída do CLI. Ver também a postura de
diagnóstico em
[`INTERNAL_DIAGNOSTIC_AESTHETICS.pt_BR.md`](INTERNAL_DIAGNOSTIC_AESTHETICS.pt_BR.md).

---

## 5. Faça / não faça (checklist de revisão)

### Faça

- Adicione ou atualize um wrapper assim que uma sequência ad-hoc aparecer
  pela segunda vez.
- Trate `check-all` como gate de segurança. Verde, ou conserta. Não
  publique "quase verde".
- Escreva linhas de log como se um estranho fosse ler em seis meses —
  porque vai.

### Não faça

- Não cole sequência de 30 linhas de shell no chat como se fosse script.
  Promova para `scripts/` para ficar testável.
- Não deixe wrapper falante demais. Modo verboso é opt-in
  ([`INTERNAL_DIAGNOSTIC_AESTHETICS.pt_BR.md`](INTERNAL_DIAGNOSTIC_AESTHETICS.pt_BR.md));
  o modo padrão é curto e denso.
- Não misture assuntos sem relação no mesmo PR. A bancada se mantém limpa
  com uma fatia por branch
  ([`.cursor/rules/execution-priority-and-pr-batching.mdc`](../../../.cursor/rules/execution-priority-and-pr-batching.mdc)).

---

## 6. Onde isso é reforçado

- [`docs/ops/TOKEN_AWARE_SCRIPTS_HUB.md`](../TOKEN_AWARE_SCRIPTS_HUB.md) — layout da bancada.
- [`docs/ops/COMMIT_AND_PR.md`](../COMMIT_AND_PR.md) — checklist de PR.
- [`docs/ops/LAB_COMPLETAO_RUNBOOK.md`](../LAB_COMPLETAO_RUNBOOK.md) — checklist de voo.
- [`docs/ops/inspirations/INTERNAL_DIAGNOSTIC_AESTHETICS.pt_BR.md`](INTERNAL_DIAGNOSTIC_AESTHETICS.pt_BR.md) — voz do log.
- [`PLAN_ENGINEERING_DOCTRINE_CONSOLIDATION.md`](../../plans/PLAN_ENGINEERING_DOCTRINE_CONSOLIDATION.md) — Slices 2–3 conectam este manifesto a comentários no código e ao relatório executivo.

A bancada continua usável quando **todo mundo** trata como "problema da
próxima pessoa". A disciplina é essa.
