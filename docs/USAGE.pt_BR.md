# Como usar a aplicação de auditoria LGPD (pt-BR)

Este documento complementa o `docs/USAGE.md` em inglês e descreve, em português, como:

- Executar a aplicação via **CLI** e **API web**;
- Entender os parâmetros (`--config`, `--web`, `--port`, `--tenant`, `--technician`);
- Navegar pelo **dashboard web**;
- Iniciar varreduras e baixar relatórios/heatmaps usando **curl**.

**English:** [USAGE.md](USAGE.md)

> **Importante:** sempre que `docs/USAGE.md` for atualizado, mantenha este arquivo sincronizado (mesmas rotas, parâmetros e exemplos, traduzidos).

---

## 1. Interface de linha de comando (CLI)

O ponto de entrada é `main.py`.

### Argumentos

| Argumento      | Padrão       | Descrição                                                                                     |
|----------------|-------------|-----------------------------------------------------------------------------------------------|
| `--config`     | `config.yaml` | Caminho do arquivo de configuração (YAML ou JSON). Usado tanto em varredura única quanto para inicializar a API. |
| `--web`        | *(flag)*    | Inicia o servidor FastAPI em vez de executar uma varredura única.                            |
| `--port`       | `8088`      | Porta da API quando `--web` é usado. Ignorado em modo CLI.                                   |
| `--reset-data` | *(flag)*    | Operação de manutenção perigosa: apaga todas as sessões/achados/falhas do SQLite, remove relatórios/heatmaps em `report.output_dir` e registra o wipe na tabela `data_wipe_log`. Não inicia varredura. |
| `--tenant`     | *(vazio)*   | Nome do cliente/tenant na execução CLI; gravado na sessão e exibido em dashboard/relatórios. |
| `--technician` | *(vazio)*   | Nome do técnico/operador na execução CLI; também gravado na sessão e relatórios.             |

### Resultados

#### Varredura única (sem `--web`)

```bash
# Execução mínima
python main.py --config config.yaml

# Execução com tags de tenant e técnico
python main.py --config config.yaml --tenant "Acme Corp" --technician "Alice Silva"
```

- Carrega a configuração, varre todos os alvos (`targets`) e grava achados em `audit_results.db`.
- Cria uma nova sessão (UUID + timestamp) com metadados (`tenant_name`, `technician_name` opcionais).
- Gera um relatório Excel e um heatmap PNG para essa sessão.
- No console, você verá algo como:
  - `Scan session: <session_id>`
  - `Report written: <caminho_do_relatorio>`

#### Servidor API (`--web`)

```bash
python main.py --config config.yaml --web --port 8088
```

- Inicia o servidor FastAPI em `0.0.0.0:8088` (ou a porta passada em `--port`).
- Nenhuma varredura é executada automaticamente; você controla tudo via HTTP (dashboard ou curl).
- Configuração para a API:
  - Se `--config` não for usado, a API lê de `CONFIG_PATH` ou `config.yaml` no diretório atual.

---

## 2. API web e dashboard

**Opção: executar via Docker (sem clonar o Git)**  
Uma imagem pré-construída está disponível no Docker Hub: `fabioleitao/python3-lgpd-crawler:latest` ([hub.docker.com/r/fabioleitao/python3-lgpd-crawler](https://hub.docker.com/r/fabioleitao/python3-lgpd-crawler)). Faça pull e execute com um config montado em `/data/config.yaml` (veja o README “Deploy com Docker” e `deploy/DEPLOY.md`). Você pode usar esse container em vez de instalar a partir do código.

### URLs principais

- **Dashboard:** `http://<host>:<port>/`
- **Reports:** `http://<host>:<port>/reports`
- **Configuration:** `http://<host>:<port>/config`
- **Help:** `http://<host>:<port>/help` — início rápido e exemplos de config
- **About:** `http://<host>:<port>/about` — aplicação, versão, autor e licença (conforme LICENSE)
- **Swagger UI:** `http://<host>:<port>/docs`
- **Health:** `http://<host>:<port>/health` — sonda para Docker/Kubernetes

### O que o dashboard mostra

- Estado da varredura (`Running`/`Idle`), ID da sessão atual, contagem de achados.
- Estatísticas da última execução (achados em bancos, filesystem, falhas, total).
- Gráfico **“Progress over time”** com total de achados e score de risco (0–100) por sessão.
- Campos de entrada para **cliente/tenant** e **técnico/operador**, usados ao clicar em “Start scan”.
- Tabela de sessões recentes com:
  - ID, data de início, tenant, técnico, achados DB/FS, falhas e link “Download” (gera o Excel dessa sessão).

### Rotas de API (resumo)

| Método | Endpoint                 | Finalidade                                                                                                   |
|--------|--------------------------|--------------------------------------------------------------------------------------------------------------|
| `POST` | `/scan` ou `/start`     | Inicia uma varredura completa em background; retorna `session_id`. Aceita `{ "tenant", "technician" }`.     |
| `POST` | `/scan_database`        | Inicia varredura pontual de um único banco (body JSON). Pode incluir `tenant` e `technician`.               |
| `GET`  | `/status`               | Retorna `running`, `current_session_id`, `findings_count`.                                                  |
| `GET`  | `/report`               | Baixa o último relatório Excel gerado (ou gera a partir da sessão mais recente).                            |
| `GET`  | `/heatmap`              | Baixa o último heatmap PNG gerado (sessão mais recente).                                                    |
| `GET`  | `/logs`                 | Baixa o arquivo de log mais recente (`audit_YYYYMMDD.log`) com registros de conexões e achados.            |
| `GET`  | `/list` ou `/reports`   | Lista sessões anteriores com data, status, contagens, `tenant_name` e `technician_name` (se definidos).     |
| `GET`  | `/reports/{session_id}` | Gera (se necessário) e baixa o relatório Excel para a sessão indicada.                                      |
| `GET`  | `/heatmap/{session_id}` | Gera (se necessário) e baixa o heatmap PNG para a sessão indicada.                                          |
| `GET`  | `/logs/{session_id}`    | Baixa o primeiro arquivo de log que contiver o `session_id` informado (análise detalhada da sessão).        |
| `PATCH`| `/sessions/{session_id}` | Atualiza/limpa o tenant de uma sessão existente (`{ "tenant": "..." }`).                                   |
| `PATCH`| `/sessions/{session_id}/technician` | Atualiza/limpa o técnico de uma sessão existente (`{ "technician": "..." }`).                    |
| `GET`  | `/about`       | Página About (HTML): aplicação, versão, autor, licença.                                           |
| `GET`  | `/about/json`  | Informações de about em JSON (nome, versão, autor, licença, copyright).                           |
| `GET`  | `/health`      | Sonda de liveness/readiness para Docker e Kubernetes.                                             |

---

## 3. Exemplos de uso da API com curl

### Iniciar varredura completa

```bash
# Sem metadados extras
curl -X POST http://localhost:8088/scan

# Com tenant e technician
curl -X POST http://localhost:8088/scan \
  -H "Content-Type: application/json" \
  -d '{ "tenant": "Acme Corp", "technician": "Alice Silva" }'
```

Resposta típica:

```json
{
  "status": "started",
  "session_id": "a1b2c3d4-20250301_143022"
}
```

### Verificar status

```bash
curl http://localhost:8088/status
```

```json
{
  "running": true,
  "current_session_id": "a1b2c3d4-20250301_143022",
  "findings_count": 42
}
```

### Varredura pontual de banco de dados

```bash
curl -X POST http://localhost:8088/scan_database \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Ad-hoc Postgres",
    "host": "db.example.com",
    "port": 5432,
    "user": "audit",
    "password": "secret",
    "database": "mydb",
    "driver": "postgresql+psycopg2",
    "tenant": "Acme Corp",
    "technician": "Alice Silva"
  }'
```

### Listar sessões anteriores

```bash
curl http://localhost:8088/list
```

Resposta (exemplo):

```json
{
  "sessions": [
    {
      "session_id": "a1b2c3d4-20250301_143022",
      "started_at": "2025-03-01T14:30:22",
      "finished_at": "2025-03-01T14:35:10",
      "status": "completed",
      "tenant_name": "Acme Corp",
      "technician_name": "Alice Silva",
      "database_findings": 12,
      "filesystem_findings": 30,
      "scan_failures": 0
    }
  ]
}
```

### Baixar o último relatório Excel

```bash
curl -o report.xlsx http://localhost:8088/report
```

### Baixar o último arquivo de log

```bash
curl -o audit.log http://localhost:8088/logs
```

### Baixar o último heatmap PNG

```bash
curl -o heatmap.png http://localhost:8088/heatmap
```

### Baixar relatório e heatmap de uma sessão específica

```bash
curl -o report_20250301.xlsx \
  "http://localhost:8088/reports/a1b2c3d4-20250301_143022"

curl -o heatmap_20250301.png \
  "http://localhost:8088/heatmap/a1b2c3d4-20250301_143022"
```

### Baixar o arquivo de log associado a uma sessão específica

```bash
curl -o audit_20250301.log \
  "http://localhost:8088/logs/a1b2c3d4-20250301_143022"
```

Esse endpoint procura, entre os arquivos `audit_YYYYMMDD.log` disponíveis (do mais recente para o mais antigo), o primeiro cujo conteúdo contenha o `session_id` informado e devolve esse arquivo.

---

## 4. Notas sobre configuração

- A aplicação utiliza um único arquivo de configuração (YAML/JSON) com as chaves principais:
  - `targets` – alvos a escanear (bancos, diretórios, APIs, compartilhamentos).
  - `file_scan` – extensões, recursividade, `scan_sqlite_as_db`, `sample_limit`.
  - `report` – `output_dir` para relatórios/heatmaps.
  - `api` – porta da API.
  - `sqlite_path` – caminho do banco SQLite com resultados.
  - `scan` – `max_workers` para paralelismo.
  - `api.workers` – número de workers uvicorn (padrão 1; 2+ para mais requisições concorrentes).

Para detalhes de todos os campos e exemplos completos, consulte `README.md` e `docs/USAGE.md` (inglês), que são as referências canônicas.

**Produção atrás de proxy reverso (nginx, Traefik, Caddy):** A aplicação se comporta corretamente atrás de NAT, load balancer ou proxy reverso. Quando o TLS for terminado no proxy, defina **X-Forwarded-Proto: https** para que os cabeçalhos de segurança (ex.: HSTS) funcionem. Veja [SECURITY.md](../SECURITY.md) para os cabeçalhos HTTP de segurança.

