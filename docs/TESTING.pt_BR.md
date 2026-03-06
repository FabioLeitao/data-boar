# Testes

**English:** [TESTING.md](TESTING.md)

Este documento descreve como executar a suíte de testes e o que cada módulo de teste cobre. Todos os testes devem passar **sem erros ou avisos** (`-W error`). O CI executa o mesmo comando a cada push e pull request.

## Executando os testes

A partir da raiz do projeto:

```bash
# Suíte completa (recomendado; usa addopts do pyproject.toml incluindo -W error)
uv run pytest -v -W error

# Ou confiar apenas nos addopts
uv run pytest -v

# Executar um único arquivo de teste
uv run pytest tests/test_routes_responses.py -v -W error

# Executar testes que correspondem a uma palavra-chave
uv run pytest -v -W error -k "session_id"
```

**Requisitos:** Python 3.12+, dependências instaladas (`uv sync` ou `pip install -e .`). Nenhum serviço externo é necessário; os testes usam configs temporários e SQLite em memória ou temporário quando preciso.

## Visão geral dos módulos de teste

| Módulo                                | Objetivo                                                                                                                                                                                                                                                          |
| ------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **test_aggregated_identification.py** | Mapeamento de categorias, regras de agregação e saída do relatório para agregação de quasi-identificadores (LGPD/compliance).                                                                                                                                     |
| **test_api_key.py**                   | Chave de API opcional: quando `api.require_api_key` é true, X-API-Key ou Bearer é obrigatório; GET /health permanece público.                                                                                                                                     |
| **test_api_scan.py**                  | POST /scan dispara auditoria completa usando o config carregado; sessão e comportamento em background.                                                                                                                                                            |
| **test_audit.py**                     | Detecção de sensibilidade: CPF, e-mail, religião, filiação política, classificação de baixa sensibilidade.                                                                                                                                                         |
| **test_csp_headers.py**               | Cabeçalhos de segurança e Content-Security-Policy no dashboard e páginas de ajuda (sem `unsafe-inline` em script-src).                                                                                                                                            |
| **test_data_scanner.py**              | Registro de conectores: filesystem, banco (Postgres), API, resolução de target desconhecido.                                                                                                                                                                       |
| **test_database.py**                  | Normalização de config (vazio, legado, rate_limit, scan.max_workers), LocalDBManager, sessões, wipe.                                                                                                                                                                |
| **test_docs_markdown.py**             | Qualidade da documentação: README e docs/USAGE existem, têm título e conteúdo chave; links relativos resolvem; SECURITY.md tem conteúdo.                                                                                                                           |
| **test_learned_patterns.py**          | Padrões aprendidos: coleta (sensibilidade, padrão, filesystem), grava YAML, exclusões.                                                                                                                                                                              |
| **test_logic.py**                     | Lógica de auditoria: CPF no conteúdo, downgrade de letras/tablatura, compatibilidade retroativa dos resultados do scan.                                                                                                                                             |
| **test_minor_detection.py**           | Detecção de menor: heurísticas de idade/DOB, flag possible_minor, fiação de config, priorização no relatório.                                                                                                                                                     |
| **test_markdown_lint.py**             | Regras estilo SonarQube/markdownlint nos arquivos .md do projeto: MD009, MD012, MD024, MD036, MD051, MD060, MD031 (espaços em torno de cercas), MD034 (sem URLs nuas), alinhamento de tabelas. Exclui .venv, .cursor, .git.                                          |
| **test_ml_engine.py**                 | MLSensitivityScanner: seed random_state (S6709), hiperparâmetros (S6973), nomenclatura de variáveis locais (S117), comportamento de predict.                                                                                                                          |
| **test_rate_limit_api.py**            | Limite de taxa: 429 quando máximo de scans concorrentes ou min_interval excedido; desabilitado por padrão para configs legados.                                                                                                                                   |
| **test_report_recommendations.py**    | Recomendações do relatório, overrides, resumo executivo, min_sensitivity, linha/prioridade possible_minor, config_scope_hash.                                                                                                                                      |
| **test_report_trends.py**             | Aba de tendências e informações do relatório (tenant, technician) nos relatórios gerados.                                                                                                                                                                         |
| **test_routes_responses.py**          | Contrato da API e OpenAPI: session_id inválido → 400; 429/400/404 documentados no OpenAPI; página de config usa constante do template.                                                                                                                           |
| **test_scripts.py**                   | Verificações de scripts Shell/PowerShell: sintaxe bash de `prep_audit.sh`, parse do `scripts/commit-or-pr.ps1`. Veja [Testes de scripts](#testes-de-scripts) abaixo.                                                                                               |
| **test_security.py**                  | Resistência a injeção SQL, validação de session_id (path traversal), uso apenas ORM para session_id, YAML safe_load. Veja [SECURITY.md](../SECURITY.md).                                                                                                            |
| **test_sonarqube_python.py**          | Guardas estilo SonarQube: regex session_id, constantes de resposta/relatório, helpers de refatoração, sem except nu em módulos chave.                                                                                                                             |
| **test_sql_connector.py**             | Conector SQL: skip de schemas (Oracle vs padrão), should_skip_schema, discover (fallback SQLite).                                                                                                                                                                  |

## Testes de qualidade e segurança

Esses testes codificam regras **SonarQube** ou de **contrato da API** para que regressões sejam detectadas no CI. Ao adicionar ou alterar comportamento da API, esquema de config ou regras de qualidade, atualize o módulo de teste relevante e mantenha este documento em sincronia.

### Testes de scripts

Scripts são validados apenas quanto a **sintaxe e estrutura**; não é necessário root nem rede. O `commit-or-pr.ps1` é verificado via parse do PowerShell (sem execução).

### Markdown lint

Os arquivos `.md` do projeto são verificados quanto a regras estilo SonarQube/markdownlint (MD009, MD012, MD024, MD036, MD051, MD060, MD031, MD034, alinhamento de tabelas). Execute: `uv run pytest tests/test_markdown_lint.py -v -W error`.

## CI

O GitHub Actions (`.github/workflows/ci.yml`) executa: (1) Testes — `uv run pytest -v -W error`; (2) Auditoria de dependências — `uv run pip-audit`; (3) SonarQube/SonarCloud quando `SONAR_TOKEN` está definido. O CodeQL está em `.github/workflows/codeql.yml`. O mesmo `sonar-project.properties` na raiz do repositório é usado pelo extension no IDE e pelo scanner no CI.

Para usar a lista de issues do SonarQube de forma automatizada: execute `uv run python scripts/sonar_issues.py` (ou `--json`) com `SONAR_TOKEN` definido; o script usa o `sonar.projectKey` do `sonar-project.properties`.

## Ver também

- [CONTRIBUTING.md](../CONTRIBUTING.md) — Configuração local e fluxo; execute os testes antes de abrir um PR.
- [SECURITY.md](../SECURITY.md) — Versões suportadas e auditoria de dependências.
- [docs/USAGE.md](USAGE.md) e [docs/USAGE.pt_BR.md](USAGE.pt_BR.md) — Comportamento da API e config coberto pelos testes.
