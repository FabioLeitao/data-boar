# Próximos passos – Solução de auditoria LGPD (arquivado)

**English:** [NEXT_STEPS.md](NEXT_STEPS.md)

*Este documento está arquivado em [completed/](.) como o checklist do plano de implementação; todos os itens estão Feitos. Para o status atual dos planos e to-dos abertos, veja [../PLANS_TODO.md](../PLANS_TODO.md).*

Plano dos próximos passos com base no [plano de implementação](../../.cursor/plans/lgpd_audit_solution_full_implementation_4a673b9e.plan.md) e no estado atual do código.

---

## 1. Status vs plano

| Item do plano                          | Status   | Notas                                                                                                 |
| ---                                    | ---      | ---                                                                                                   |
| config/loader.py                       | Feito    | YAML/JSON unificado, esquema normalizado                                                              |
| core/session.py                        | Feito    | UUID + timestamp                                                                                      |
| core/database.py                       | Feito    | SQLite único, 4 tabelas, LocalDBManager                                                               |
| core/detector.py                       | Feito    | Regex + ML a partir do config                                                                         |
| core/scanner.py                        | Feito    | Usa apenas o detector                                                                                 |
| core/connector_registry.py             | Feito    | Registry + connector_for_target                                                                       |
| core/engine.py                         | Feito    | start_audit, generate_final_reports, paralelo/sequencial                                              |
| connectors/sql_connector.py            | Feito    | Discover + sample, Oracle/MSSQL/MySQL/Postgres/etc.                                                   |
| connectors/filesystem_connector.py    | Feito    | Verificação de permissão, recursivo, muitas extensões                                                 |
| connectors/mongodb_connector.py       | Feito    | Opcional, pymongo                                                                                     |
| connectors/redis_connector.py          | Feito    | Opcional, redis                                                                                       |
| report/generator.py                    | Feito    | Excel + heatmap, DB/FS/falhas/recomendações                                                           |
| api/routes.py                          | Feito    | /scan, /start, /status, /report, /list, /reports/{id}; GET /, /reports, /config (dashboard)           |
| Web dashboard (frontend)               | Feito    | GET / dashboard, GET /reports list, GET/POST /config editor; Jinja2 + static; sem WebSocket (conforme plano) |
| main.py                                | Feito    | --config, --web, --port 8088                                                                          |
| utils/logger.py                        | Feito    | Logger unificado, log_finding, notify_violation                                                       |
| README.md                              | Feito    | Instalação, config, execução, DBs, tipos de arquivo                                                    |
| TOPOLOGY.md                            | Feito    | Topologia de módulos/classes/funções                                                                   |
| config.yaml                            | Feito    | Forma unificada, targets DB (comentados), file_scan                                                   |
| pyproject.toml                         | Feito    | requires-python 3.12+, opcional nosql/bigdata                                                         |
| requirements.txt                       | Em uso   | Manter em sincronia com pyproject.toml                                                                |

---

## 2. Próximos passos recomendados (em ordem)

### 2.1 Consolidar código legado e testes — Feito

- **run.py** – Wrapper fino (config.loader + AuditEngine + api.routes.app, porta 8088); docstring recomenda `main.py`.
- **api/app.py** – Reexporta app de `api.routes` (única app FastAPI).
- **scanners/** – README de depreciação adicionado; usar `core.engine` + `connectors` + `report.generator`.
- **database/** – README de depreciação adicionado; usar `core.database` e `connectors`.
- **file_scan/**, **db/**, **report/sqlite_reporter.py**, **logging_custom/** – Notas de legado em vigor; testes usam `config.loader`, `core.*`, `connectors`.
- **Testes** – Usam `core.scanner`, `core.detector`, `config.loader`, `core.database`, `core.connector_registry`; sem imports legados.

---

### 2.2 Padrões aprendidos (opcional) — Feito

- **Implementado:** Config opcional `learned_patterns`; ao gerar o relatório, termos de achados HIGH (ou MEDIUM) são coletados. YAML de saída compatível com ml_patterns_file; README documenta o merge.

---

### 2.3 "Praise" no relatório para proteções existentes — Feito

- **Implementado:** `report/generator.py` adiciona a planilha "Praise / existing controls" quando algum achado tem nome de coluna ou pattern_detected com palavras-chave de proteção (encrypted, hash, tokenized, masked, etc.). Linhas listam target, fonte, coluna/arquivo, padrão e indicação.

---

### 2.4 Dependências e segurança — Feito

- **Feito:** README tem "Dependencies and security" com `uv pip compile pyproject.toml -o requirements.txt` e `uv pip audit`. `requirements.txt` regenerado a partir de pyproject.toml.

---

### 2.5 Conectores opcionais (BigData / APIs) — Feito

- **Implementado:** Conector REST/API (`connectors/rest_connector.py`) com auth: basic, bearer, oauth2_client, headers custom. Targets `type: api` ou `type: rest`; README documenta tabela de auth e exemplos YAML.

---

### 2.6 SQLite / .db no scan de filesystem — Feito

- **Implementado:** Quando `file_scan.scan_sqlite_as_db` é true (padrão), arquivos .sqlite/.sqlite3/.db são abertos com SQLAlchemy; discover de tabelas/colunas, sample, detector; resultados em filesystem_findings. Config: `file_scan.scan_sqlite_as_db`, `file_scan.sample_limit`.

---

### 2.7 Manutenção de TOPOLOGY e README — Feito

- **Atualizado:** TOPOLOGY.md documenta file_scan.scan_sqlite_as_db/sample_limit, fluxo SQLite-as-DB do FilesystemConnector e rota da API `POST /scan_database`. README documenta o comportamento e as rotas.

---

### 2.8 Web dashboard (frontend) — Feito

- **Conforme plano:** Sem WebSocket/streaming; apenas REST API e download de arquivos. Frontend em HTML renderizado no servidor (Jinja2), sem SPA.
- **Implementado:** Dashboard (GET /), Reports (GET /reports), Configuration (GET/POST /config); templates em `api/templates/`, estáticos em `api/static/`; documentado em README e docs/USAGE.md.

---

## 3. Checklist por arquivo (do plano)

(Conforme tabela em [NEXT_STEPS.md](NEXT_STEPS.md) — todos os itens com status Done ou em uso.)

---

## 4. Fora do escopo (conforme plano)

- Sem armazenamento de conteúdo bruto de DB/arquivo; apenas metadados (e opcionalmente exemplo anonimizado).
- **SMB/NFS/WebDAV/SharePoint:** Suportados via conectores opcionais (type smb, cifs, nfs, webdav, sharepoint; instalar `.[shares]`). NFS exige path pré-montado.
- Deep learning é opcional; o padrão permanece regex + classificador TF-IDF.
- Sem WebSocket/streaming na UI; apenas REST API e download. O dashboard web (2.8) segue isso: páginas renderizadas no servidor (Jinja2) consumindo a mesma REST API.

---

## 5. Ordem sugerida de trabalho

1. **2.1** – Consolidar código legado e corrigir testes.
1. **2.4** – Dependências e segurança.
1. **2.7** – TOPOLOGY + README após 2.1 e 2.4.
1. **2.3** – "Praise" no relatório.
1. **2.2** – Padrões aprendidos (opcional).
1. **2.6** – SQLite-as-DB no file scan (opcional).
1. **2.5** – Conectores opcionais BigData/API.
1. **2.8** – Web dashboard — Feito.
