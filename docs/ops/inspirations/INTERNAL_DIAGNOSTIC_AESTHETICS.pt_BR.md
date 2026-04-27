# Estética interna de diagnóstico (doutrina Data Boar)

**English:** [INTERNAL_DIAGNOSTIC_AESTHETICS.md](INTERNAL_DIAGNOSTIC_AESTHETICS.md)

> **Semente:** [Mark Russinovich / Sysinternals](https://learn.microsoft.com/en-us/sysinternals/)
>
> *"Uma boa ferramenta de diagnóstico te ensina o sistema a cada execução."*

Este é um **manifesto doutrinário** sobre como as superfícies de diagnóstico
do Data Boar — `--verbose`, `completão -Privileged`, JSON de auditoria e a
seção de metodologia do relatório executivo — devem *parecer*. O padrão é
**Sysinternals**: denso, honesto e didático, não muralha de ruído.

---

## 1. O padrão Sysinternals

Process Explorer, Process Monitor, Autoruns e ProcDump conquistaram
confiança em duas décadas fazendo três coisas:

1. **Mostrar, não resumir.** Existe uma coluna para tudo o que importa; o
   usuário decide para o que olhar.
2. **Nomear o desconhecido explicitamente.** Quando um valor não foi
   verificado, o software fala isso ("not verified"), em vez de mentir com
   confiança.
3. **Ensinar o SO no caminho.** Ler a saída do Sysinternals é uma aula curta
   de como o kernel realmente funciona.

As superfícies de diagnóstico do Data Boar miram o mesmo padrão — traduzido
para o "kernel do banco de dados" que o cliente acompanha.

---

## 2. As três superfícies de diagnóstico

### 2.1 `--verbose` (console de dev / operador)

**Propósito:** explicar o que o scanner está fazendo, em tempo real,
enquanto faz. Ferramenta de bancada, não documento para stakeholder.

**Padrão:**

- Cada conector anuncia dialeto, teto de amostragem, statement timeout e
  estratégia de fallback *antes* de executar a primeira amostra.
- Toda decisão de amostragem registra o rótulo da estratégia
  (`TOP_NOLOCK_SQLSERVER`, `TABLESAMPLE_SYSTEM_POSTGRESQL`,
  `LIMIT_BASELINE_MYSQL`) — ver
  [`connectors/sql_sampling.py`](../../../connectors/sql_sampling.py).
- Eventos de degradação na hierarquia de fallback imprimem uma linha cada,
  alinhada
  ([`THE_ART_OF_THE_FALLBACK.pt_BR.md`](THE_ART_OF_THE_FALLBACK.pt_BR.md) §3).
- Sem métrica inventada. Se um número é estimativa, a linha diz
  `~estimate=...`, não `count=...`.

### 2.2 `completão -Privileged` (orquestração de laboratório)

**Propósito:** provar que o laboratório ainda espelha o ambiente do cliente.
Observabilidade SRE, não folder de marketing.

**Padrão:**

- Cada host de laboratório imprime cabeçalho de inventário (SO, kernel,
  Docker, Python, disco livre) antes de qualquer teste rodar.
- Cada passo imprime `[k/N] <step>` mais o tempo de relógio medido e o exit
  code.
- Falhas emitem **bloco de RCA** modelado em post-mortem da Cloudflare:
  qual etapa, qual host, qual seria o próximo comando manual (ver
  [`DEFENSIVE_SCANNING_MANIFESTO.pt_BR.md`](DEFENSIVE_SCANNING_MANIFESTO.pt_BR.md) §1).
- Passos privilegiados dizem `sudo -n` ou "interativo" — nunca caem no
  meio do caminho em silêncio.

### 2.3 JSON de auditoria / manifesto de varredura

**Propósito:** artefato grau-evidência. O DPO, CISO ou auditor lê isso seis
meses depois sem o operador de plantão.

**Padrão:**

- Validado contra schema. Os nomes dos campos são estáveis; campos novos
  são aditivos.
- Tetos de amostragem, statement timeouts, postura de dialeto e
  `safety_tags` estão sempre presentes, mesmo quando o scanner não chegou a
  acionar nenhum deles. *Ausência de chave é problema maior do que valor
  fora do default.*
- Cada entrada de auditoria carrega `session_id` para a linha ser
  reproduzível.
- Ver [`report/scan_evidence.py`](../../../report/scan_evidence.py) e
  [`report/evidence_collector.py`](../../../report/evidence_collector.py).

---

## 3. Voz e densidade (estilo)

A voz de diagnóstico é **Russinovich**, não **status page**:

- **Curto, técnico, factual.** Sem ponto de exclamação. Sem "tá tudo
  certo!". Ou está tudo certo e a gente diz isso uma vez, ou não está e a
  gente diz exatamente o que está errado.
- **Um conceito por linha.** Linha de várias cláusulas é coisa de prosa,
  não de log.
- **Números com unidade.** `wall_time=14.2s`, não `time=14.2`.
- **Vocabulário ciente de dialeto.** Use `WITH (NOLOCK)` para SQL Server,
  `TABLESAMPLE SYSTEM` para PostgreSQL — o nome certo para o motor certo,
  sempre.

Contraexemplo (não fazer):

```text
✨ Scan completado com sucesso!! 🚀
Tabelas: muitas
Achados: muitos
```

Melhor (fazer):

```text
scan finished
  session_id        2026-04-27_t14_a993c0dc
  tables_visited    248 / 248
  rows_sampled      18_412 (cap=10000/col, sem overrun)
  fallback_demotions 3   (ver scan_manifest_2026-04-27.yaml#fallbacks)
  safety_tags       NOLOCK_SQLSERVER, TABLESAMPLE_PG, COMPLIANCE_COMMENT
```

---

## 4. A regra "sem números inventados"

Vem de
[`.cursor/rules/publication-truthfulness-no-invented-facts.mdc`](../../../.cursor/rules/publication-truthfulness-no-invented-facts.mdc)
e vale com força dentro da saída de diagnóstico:

- Nunca arredondar para uma confiança que não foi medida.
- Nunca imprimir percentil com menos do que o mínimo documentado de
  amostras.
- Nunca citar "score de compliance" que o scanner não derivou
  deterministicamente do próprio log de auditoria.

Se o dado não está, a linha diz isso. É mais útil do que uma média
confiante.

---

## 5. Faça / não faça (checklist de revisão)

### Faça

- Acrescente coluna quando há sinal real e o usuário pode filtrar por ele.
- Escreva a linha de diagnóstico como se um DBA fosse colar num ticket.
- Exibe a **última** justificativa de degradação da hierarquia de fallback
  na seção de metodologia do relatório executivo (ver
  [`ACTIONABLE_GOVERNANCE_AND_TRUST.pt_BR.md`](ACTIONABLE_GOVERNANCE_AND_TRUST.pt_BR.md)).

### Não faça

- Não bote emoji em log que auditor vai ler. Emoji vive no chat e na
  vitrine do README, não em `scan_manifest_*.yaml` nem na saída de
  `--verbose`.
- Não trunque instrução de amostragem no JSON de auditoria. Truncar é o
  que faz revisor desconfiar do artefato.
- Não publique linha nova de `--verbose` sem checar que
  `tests/test_scan_audit_log.py` continua verde.

---

## 6. Onde isso é forçado

| Superfície | Arquivo | Teste |
| ---------- | ------- | ----- |
| Rótulo de amostragem e composição da SQL | [`connectors/sql_sampling.py`](../../../connectors/sql_sampling.py) | `tests/test_sql_sampling.py` |
| Forma do log de auditoria | [`core/scan_audit_log.py`](../../../core/scan_audit_log.py) | `tests/test_scan_audit_log.py` |
| Manifesto de varredura | [`report/scan_evidence.py`](../../../report/scan_evidence.py) | `tests/test_scan_evidence.py` |
| Seção 3 de metodologia do relatório executivo | [`report/executive_report.py`](../../../report/executive_report.py) | `tests/test_executive_report*.py` |

---

## 7. Relacionado

- [`DEFENSIVE_SCANNING_MANIFESTO.pt_BR.md`](DEFENSIVE_SCANNING_MANIFESTO.pt_BR.md) —
  o que mostramos é o que prometemos.
- [`THE_ART_OF_THE_FALLBACK.pt_BR.md`](THE_ART_OF_THE_FALLBACK.pt_BR.md) —
  cada degradação é logada.
- [`ACTIONABLE_GOVERNANCE_AND_TRUST.pt_BR.md`](ACTIONABLE_GOVERNANCE_AND_TRUST.pt_BR.md) —
  estas superfícies alimentam a narrativa para stakeholder.

Diagnóstico que não ensina é diagnóstico em que ninguém vai confiar.
