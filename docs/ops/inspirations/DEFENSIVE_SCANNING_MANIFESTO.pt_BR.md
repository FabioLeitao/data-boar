# Manifesto de varredura defensiva (doutrina Data Boar)

**English:** [DEFENSIVE_SCANNING_MANIFESTO.md](DEFENSIVE_SCANNING_MANIFESTO.md)

> **Sementes:** [NASA Software Engineering Lab](https://nasa.github.io/) ·
> [Cloudflare Engineering blog](https://blog.cloudflare.com/) ·
> [Steve Gibson / Security Now](https://www.grc.com/securitynow.htm)
>
> *"Teste o que você voa. Falhar em produção não é resultado aceitável."*

Este é um **manifesto doutrinário**. Ele enuncia as regras inegociáveis que o
Data Boar precisa seguir ao tocar o banco de dados do cliente — do mesmo jeito
que um piloto trata uma turbina em operação: com respeito, redundância
instrumentada e checklist.

---

## 1. O contrato com o banco do cliente

O Data Boar é **convidado**. O cliente continua responsável pela base; nós
respondemos pelo nosso impacto sobre ela. O contrato tem quatro cláusulas:

1. **Sem varredura sem teto.** Toda leitura tem amostra com teto rígido e
   orçamento de tempo de relógio (wall-clock).
2. **Sem locks exclusivos.** Onde o dialeto suporta, a leitura por amostragem
   usa o menor nível de isolamento que ainda satisfaz "leitura estilo
   compliance" — ver §3 sobre `WITH (NOLOCK)`.
3. **Sem efeito colateral surpresa.** Nada de `DDL`, sem objetos temporários
   no servidor do cliente, sem mutação de schema sob `--verbose` ou
   `--debug`.
4. **Sem pegada anônima.** Toda instrução emitida é etiquetada para o DBA
   conseguir grepar nas views de atividade e identificar o Data Boar sem
   precisar paginar o operador.

As sementes desta postura:

- **NASA SEL** — *teste o que você voa*. Os mesmos caminhos de código de
  varredura que rodam no ambiente do cliente são exercitados em `tests/` e no
  `completão` do laboratório.
- **Cloudflare Engineering** — rigor de protocolo e post-mortems **públicos**
  com evidência numérica. Quando algo falha no laboratório, publicamos o RCA
  com números, não com vibração.
- **Steve Gibson** — código não invasivo e verificável. O SpinRite ganhou
  confiança sendo explícito sobre o que **não** faria; o Data Boar herda essa
  postura.

---

## 2. Tetos de amostragem e timeouts de instrução (válvulas de alívio)

Os defaults são **limitados**. O operador pode ajustar via env ou YAML, mas o
runtime sempre faz o clamp num teto rígido. Trate esses limites como
**válvulas de alívio**, não como botões livres.

| Controle | Default | Teto rígido | Código |
| -------- | ------- | ----------- | ------ |
| `DATA_BOAR_SQL_SAMPLE_LIMIT` | YAML config | `10_000` linhas / coluna | [`connectors/sql_sampling.py`](../../../connectors/sql_sampling.py) `_HARD_MAX_SAMPLE` |
| `DATA_BOAR_SAMPLE_STATEMENT_TIMEOUT_MS` | nenhum no driver | `60_000` ms (60 s) | mesmo arquivo, `resolve_statement_timeout_ms_for_sampling` |
| PostgreSQL `TABLESAMPLE SYSTEM (p)` | 1.0 % | 0.01–100.0 % | `_pg_tablesample_system_percent` |
| SQL Server `TABLESAMPLE SYSTEM (p)` | 10.0 % | 0.01–100.0 % | `_mssql_tablesample_system_percent` |

Esses tetos são **forçados** em código (`max(1, min(...))`), não pedidos com
gentileza no doc. Valores inválidos em env caem para a base documentada — nunca
para "sem teto".

---

## 3. Postura por dialeto (não confunda dialetos)

| Dialeto | Regra | Justificativa |
| ------- | ----- | -------------- |
| **Oracle** | `ROWNUM` é aplicado na consulta *externa*; a interna filtra `IS NOT NULL` antes. | Evita alimentar o limite de linhas com linhas só-nulas; forma clássica de subconsulta no Oracle. |
| **Snowflake** | `SAMPLE (n ROWS)` sobre uma view inline já filtrada de nulos. | Leitura ciente de custo de warehouse. |
| **SQL Server** | `SELECT TOP (n) … FROM … WITH (NOLOCK)` | **Amostragem somente leitura** estilo compliance: bloquear um writer longo é inaceitável; aceitamos leitura suja / não repetível **só** porque a saída é grau-amostra e nunca alimenta decisão transacional. |
| **PostgreSQL** | `LIMIT` como base; `TABLESAMPLE SYSTEM` mais `LIMIT` apenas quando a estimativa de cardinalidade aponta tabela grande. | Evita viés sequencial em heaps muito grandes. |
| **MySQL / DuckDB / Cockroach** | Só `LIMIT`. | Simplicidade de dialeto; sem `ORDER BY` implícito. |

**`WITH (NOLOCK)` é contrato, não gambiarra.** Ele documenta que o Data Boar
nunca vai bloquear um writer, mesmo que isso signifique ler uma tupla que está
prestes a sofrer rollback. Aceitamos essa assimetria porque a alternativa —
manter um shared lock durante uma varredura longa — violaria a cláusula 2 da
§1.

---

## 4. Atribuição de instrução (contrato DBA-grep)

Toda instrução de amostragem emitida começa com o comentário de linha:

```sql
-- Data Boar Compliance Scan
SELECT TOP (n) ... FROM ... WITH (NOLOCK)
```

Um DBA acompanhando `pg_stat_activity` / DMVs identifica o Data Boar sem
precisar fazer engenharia reversa do plano de execução. Esse comentário **não
é decorativo**; é como o DBA decide se mata nossa sessão ou se chama o
operador.

O comentário inicial é forçado em
[`connectors/sql_sampling.py`](../../../connectors/sql_sampling.py)
(`_COMPLIANCE_SCAN_LEADING`) — **não** remova em refatorações.

---

## 5. Sem `ORDER BY` em amostragem automática

`ORDER BY` em coluna sem índice força ordenação de tabela inteira. Isso é o
oposto de "leitura estilo compliance". A camada de composição **não pode**
injetar `ORDER BY` em SQL de amostragem automática; os tetos de dialeto (`TOP`
/ `LIMIT` / `ROWNUM` / `SAMPLE`) e dicas de cardinalidade do dicionário já
seguram o limite.

Se algum conector um dia precisar de ordem determinística, isso exige ADR e
opt-in explícito de `--ordered-sample` — não mudança silenciosa de
comportamento.

---

## 6. Faça / não faça (checklist de PR)

### Faça

- Coloque teto em **toda** leitura no código. Se o teto é "configurável",
  faça clamp.
- Etiquete toda instrução com `-- Data Boar Compliance Scan`.
- Documente novos dialetos neste arquivo *antes* de publicar o conector.
- Trate `WITH (NOLOCK)` e `TABLESAMPLE` como decisões de protocolo, não como
  micro-otimização.

### Não faça

- Não adicione um "fast path" que dribla o gerenciador de amostragem. A
  camada de composição é **uma só**; faça benchmark dentro dela.
- Não aceite "o cliente pediu para tirar o comentário de cabeçalho". A
  resposta na thread do PR é esta seção.
- Não rode `OPTION (RECOMPILE)` ou `WITH (READUNCOMMITTED)` como default — o
  primeiro desperdiça plan cache, o segundo é apelido SQL Server para
  `NOLOCK` e fica como **um** caminho de código explícito, não dois.
- Não escale silenciosamente de "compliance scan" para "audit-grade scan".
  Isso pede SKU novo e ADR.

---

## 7. Onde isso é forçado

- **Composição:** [`connectors/sql_sampling.py`](../../../connectors/sql_sampling.py)
- **Emissão de auditoria:** [`core/scan_audit_log.py`](../../../core/scan_audit_log.py)
- **Testes:** `tests/test_sql_sampling.py`, `tests/test_scan_audit_log.py`,
  `tests/test_scan_evidence.py`.
- **Docs do operador:** [`docs/USAGE.md`](../../USAGE.md) §SQL sampling,
  [`docs/TESTING.md`](../../TESTING.md).
- **Plano que conduz as Slices 2–3:**
  [`PLAN_ENGINEERING_DOCTRINE_CONSOLIDATION.md`](../../plans/PLAN_ENGINEERING_DOCTRINE_CONSOLIDATION.md).

O scanner é convidado na casa dos outros. Diz *obrigado*, deixa as luzes como
encontrou e assina o livro de visitas.
