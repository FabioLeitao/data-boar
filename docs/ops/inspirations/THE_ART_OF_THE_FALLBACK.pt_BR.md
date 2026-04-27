# A arte do fallback (doutrina Data Boar)

**English:** [THE_ART_OF_THE_FALLBACK.md](THE_ART_OF_THE_FALLBACK.md)

> **Sementes:** [Usagi Electric](https://www.youtube.com/@UsagiElectric) ·
> [The 8-Bit Guy](https://www.youtube.com/@The8BitGuy)
>
> *"Se o componente é velho e está sujo, o sistema precisa saber lidar com isso."*

Este é um **manifesto doutrinário** — não é referência de tom nem roadmap.
Ele descreve como o Data Boar precisa se comportar quando uma entrada
"Data Soup" é desconhecida, malformada ou só parcialmente legível.

---

## 1. Por que isso existe

Ambiente de cliente nunca é tão limpo quanto laptop de dev. Exportações de
banco vêm com sequências UTF-8 corrompidas, arquivos `.docx` se passando por
`.zip`, planilhas antigas com codificação misturada por célula e dialetos
SQL contra os quais o parser nunca foi testado. **O Data Boar tem que seguir
em frente e emitir um diagnóstico** — falha silenciosa é resultado pior que
cobertura degradada.

Dois restauradores inspiram essa postura:

- **Usagi Electric** documenta a engenharia reversa de máquinas que "não
  deveriam mais dar boot" — e registra cada beco sem saída como evidência.
  Os entregáveis são paciência mais log honesto.
- **The 8-Bit Guy** restaura máquinas de 8 bits com restrições apertadas,
  ferramentas baratas e narração metódica. Escassez de recurso não é
  desculpa para pular o diagnóstico.

Junto: **resiliência até o silício, com rastro escrito**.

---

## 2. A hierarquia de fallback (ordem canônica)

Ao analisar um payload de cliente — dialeto SQL, exportação semi-estruturada,
blob de texto bruto — o Data Boar tenta a estratégia **mais forte** primeiro
e degrada em seguida:

1. **Parser SQL** (preferência).
   Use SQLAlchemy / sqlparse / AST específico de dialeto quando a fonte
   declara um dialeto conhecido. Sinal mais forte, menor superfície de falso
   positivo.

2. **Padrão regex** (degradado, com teto).
   Quando a AST não consegue consumir o payload (ex.: dump de dialeto
   misto), cai para regex ancorado com padrões documentados. Os padrões
   precisam de revisão e nunca rodam sem teto sobre memória arbitrária.

3. **Heurística de string crua** (último recurso).
   Pontuação por frequência de tokens / dicionário, checagem de byte líder
   para formatos binários, varredura de bytes resiliente a codificação para
   marcadores sensíveis. Usado só quando os passos 1 e 2 recusaram-se a
   confirmar e rotulado explicitamente como
   `"strategy": "raw_string_heuristic"` na saída de auditoria.

A hierarquia é **monotônica**: um conector nunca tenta `raw_string` antes de
tentar (e recusar) `regex`, e nunca tenta `regex` antes de tentar (e recusar)
`parser`. Pular níveis esconde bug.

---

## 3. A regra "diagnóstico ao cair"

> **O Data Boar nunca degrada para um nível mais fraco em silêncio.**

Cada passo de fallback **precisa** produzir uma entrada de auditoria com:

- O nível tentado (`parser_sql`, `regex`, `raw_string`).
- Uma justificativa curta e factual para a degradação (ex.: `"sqlparse:
  unrecognized dialect"`, `"regex: anchor budget exceeded"`).
- O próximo nível escolhido.
- Um id de correlação (`session_id` + tabela/coluna quando aplicável).

Essas entradas são publicadas via
[`core/scan_audit_log.py`](../../../core/scan_audit_log.py) e
[`report/scan_evidence.py`](../../../report/scan_evidence.py); o relatório
executivo cita a **última** justificativa de degradação na seção de
metodologia.

Exemplo no formato que o operador vê:

```text
[fallback] table=customers column=notes
  parser_sql      → recusou (dialect=mixed_postgres_mssql)
  regex           → recusou (budget=512 KiB excedido)
  raw_string      → engajou (heuristic=cpf_proximity, samples=200)
```

---

## 4. Faça / não faça (checklist de revisão)

### Faça

- Trate cada surpresa "Data Soup" como **dado de primeira classe**, não
  como exceção a engolir.
- Coloque teto em cada estratégia: orçamento de bytes, tempo de compilação
  do regex, linhas amostradas.
- Emita a justificativa de degradação na **mesma linha** de auditoria do
  achado final — assim o revisor reproduz com o mesmo `session_id`.
- Na dúvida, reduza **cobertura**, nunca **a veracidade** do log de
  auditoria.

### Não faça

- Não capture uma exceção do parser e siga em `regex` *sem* logar a
  degradação. Esse é justamente o modo de falha que este manifesto evita.
- Não adicione um quarto nível "abaixo de string crua" sem ADR. Heurística
  baseada só em entropia gera ruído que contamina o relatório executivo.
- Não reaproveite o rótulo de uma estratégia entre dialetos quando a
  implementação for diferente (ver regras de rastreabilidade de auditoria
  em [`DEFENSIVE_SCANNING_MANIFESTO.pt_BR.md`](DEFENSIVE_SCANNING_MANIFESTO.pt_BR.md)).

---

## 5. Onde isso é (e será) forçado

| Camada | Arquivo | Forçado em |
| ------ | ------- | ---------- |
| Composição da SQL de amostragem | [`connectors/sql_sampling.py`](../../../connectors/sql_sampling.py) | Rótulo de estratégia por plano; sem `ORDER BY` implícito; ciente de dialeto. |
| Forma do log de auditoria | [`core/scan_audit_log.py`](../../../core/scan_audit_log.py) | Resumo por provider + resumo de estratégia por conector. |
| Metodologia do relatório executivo | [`report/executive_report.py`](../../../report/executive_report.py) | Seção 3 — última justificativa de degradação citada. |
| Plano que conduz as Slices 2–3 | [`PLAN_ENGINEERING_DOCTRINE_CONSOLIDATION.md`](../../plans/PLAN_ENGINEERING_DOCTRINE_CONSOLIDATION.md) | Adiciona bloco de RCA + comentários doutrinários referenciando este arquivo. |

---

## 6. Manifestos e regras relacionados

- [`DEFENSIVE_SCANNING_MANIFESTO.pt_BR.md`](DEFENSIVE_SCANNING_MANIFESTO.pt_BR.md) —
  por que cada passo tem teto rígido.
- [`INTERNAL_DIAGNOSTIC_AESTHETICS.pt_BR.md`](INTERNAL_DIAGNOSTIC_AESTHETICS.pt_BR.md) —
  como o log de degradação **lê** em `--verbose`.
- [`ACTIONABLE_GOVERNANCE_AND_TRUST.pt_BR.md`](ACTIONABLE_GOVERNANCE_AND_TRUST.pt_BR.md) —
  por que o relatório executivo precisa exibir evidência de fallback.

O scanner não para. O diagnóstico não é pulado. A regra é só essa.
