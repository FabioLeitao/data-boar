# python3-lgpd-crawler (Português – Brasil)

Aplicação para auditoria de dados pessoais e sensíveis em bancos de dados e sistemas de arquivos, alinhada a **LGPD**, **GDPR**, **CCPA**, **HIPAA** e **GLBA**. Ela descobre e mapeia possíveis dados pessoais/sensíveis via **regex** e **ML**, armazena apenas **metadados** em um banco SQLite local (incluindo tags opcionais de **cliente/tenant** e **técnico/operador** por varredura) e gera relatórios em Excel e um **heatmap** de sensibilidade/risco em PNG.

> **Manutenção da documentação:** sempre que um novo recurso ou opção de linha de comando for adicionado, atualize **este arquivo** e o `README.md` em inglês, bem como os arquivos `docs/USAGE.md` e `docs/USAGE.pt_BR.md`, para manter as versões sincronizadas.  
> **English:** [README.md](README.md) · [docs/USAGE.md](docs/USAGE.md)

## Funcionalidades principais

- **Múltiplos alvos:** configure, em um único arquivo YAML/JSON, vários bancos de dados, diretórios de arquivos, APIs HTTP, compartilhamentos remotos (SharePoint, WebDAV, SMB/CIFS, NFS), **Power BI** e **Power Apps (Dataverse)**.
- **Bancos SQL:** PostgreSQL, MySQL, MariaDB, SQLite, SQL Server, Oracle, Snowflake (extras opcionais via `pyproject.toml`).
- **Detecção de sensibilidade:** combina regex configurável com classificador de ML (TF‑IDF + RandomForest) aplicado a nomes de colunas e amostras de conteúdo. Nenhum dado bruto é salvo – apenas local, padrão detectado, nível de sensibilidade, norma, etc.
- **Heurísticas para reduzir falsos positivos:** letras de música e cifras de violão são detectadas e tratadas de forma especial para reduzir falsos positivos (datas/números em letras/cifras não viram HIGH sozinhos).
- **SQLite único:** todas as sessões de varredura são gravadas em `audit_results.db`, com tabelas separadas para achados de banco de dados, achados de filesystem e falhas de varredura. Cada sessão tem `session_id`, `started_at`, `finished_at`, `status`, `tenant_name` (cliente/tenant) e `technician_name` (técnico/operador).
- **Relatórios:** para cada sessão, é gerado um arquivo Excel com abas:
  - **Report info** (Session ID, Started at, Tenant/Customer, Technician/Operator, Application, Version, Author, License, Copyright)
  - Database findings, Filesystem findings, Scan failures, Recommendations, Praise / existing controls, Trends – Session comparison, Heatmap data
- Um arquivo **heatmap_\<session_prefix\>.png** é gerado com o mapa de calor de sensibilidade/risco (inclui rodapé com aplicação, autor e licença).
- **CLI e API REST:** modo de execução única via linha de comando ou modo servidor (FastAPI) com dashboard web (Help, About com autor e licença), endpoints para varreduras e relatórios. A aplicação funciona atrás de NAT, load balancer ou proxy reverso (nginx, Traefik, Caddy); defina **X-Forwarded-Proto: https** quando o TLS for terminado no proxy.

## Requisitos e preparação do ambiente

- **Sistema operacional:** Ubuntu 24.04 / Debian 13 (recomendado) ou versão recente de Linux/macOS/Windows.
- **Python:** 3.12+.
- **Gerenciador de pacotes:** [uv](https://github.com/astral-sh/uv) (recomendado) ou `pip`.

### Instalando Python e bibliotecas de sistema (exemplo Debian/Ubuntu)

```bash
sudo apt update
sudo apt install -y python3.12 python3.12-venv python3.12-dev build-essential \
  libpq-dev libssl-dev libffi-dev unixodbc-dev
```

No Windows, instale Python 3.12 pelo instalador oficial e, se necessário, clientes de banco de dados/ODBC conforme a documentação de cada fornecedor.

### Instalando o uv

```bash
# Linux/macOS (instalador oficial)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Alternativa (Windows ou fallback)
py -m pip install uv

uv --version
```

## Instalação da aplicação

No diretório raiz do projeto:

```bash
# Com uv (recomendado) – cria venv e instala dependências
uv sync

# Ou com pip (dentro de um venv já ativado)
pip install -e .
```

### Executando com uv

```bash
# Varredura única (CLI)
uv run python main.py --config config.yaml

# API web
uv run python main.py --config config.yaml --web --port 8088
```

## Execução (CLI e API)

### CLI (varredura única)

```bash
# Execução mínima
python main.py --config config.yaml

# Execução com tags de cliente/tenant e técnico/operador
python main.py --config config.yaml --tenant "Acme Corp" --technician "Alice Silva"

# Relatório será salvo em report.output_dir (config), ex.: Relatorio_Auditoria_<session_id>.xlsx
```

### API REST (servidor)

```bash
# Inicia API na porta 8088
python main.py --config config.yaml --web --port 8088

# Ou apenas:
python main.py --web --port 8088
```

#### Argumentos da CLI (resumo)

| Argumento         | Modo         | Descrição                                                                                         |
|-------------------|--------------|---------------------------------------------------------------------------------------------------|
| `--config PATH`   | CLI & API    | Caminho do arquivo de configuração YAML/JSON (padrão `config.yaml`).                            |
| `--web`           | API          | Inicia o servidor FastAPI em vez de executar uma varredura única.                               |
| `--port N`        | API          | Porta da API (padrão 8088). Ignorada em modo CLI.                                                |
| `--reset-data`    | CLI          | **Perigoso**: apaga todas as sessões/achados/falhas do SQLite, remove relatórios/heatmaps em `report.output_dir` e grava um registro na tabela `data_wipe_log`. Não executa varredura. |
| `--tenant NAME`   | CLI          | Nome do cliente/tenant para a sessão; exibido no dashboard, relatórios e aba “Report info”.     |
| `--technician NAME` | CLI        | Nome do técnico/operador responsável pela sessão; também exibido no dashboard e relatórios.     |

Quando a API está rodando, se `--config` não for fornecido, o servidor lê o caminho da variável de ambiente `CONFIG_PATH` ou usa `config.yaml` no diretório atual.

## Navegando pelo dashboard web

Com a API em execução (`--web`), acesse no navegador:

- **Dashboard:** `http://<host>:<port>/`
  - Mostra estado da varredura (Running/Idle), sessão atual, contagem de achados.
  - Bloco de “Data discovery (last run)” com contagens de achados em bancos, filesystem e falhas.
  - Gráfico **“Progress over time”** (total de achados + score de risco 0–100 por sessão).
  - Botão **"Start scan"**: dispara varredura completa de **todos os alvos** da configuração atual (mesmo que o CLI com esse config).
  - Campos opcionais para **cliente/tenant** e **técnico/operador** antes de iniciar uma nova varredura.
  - Tabela de sessões recentes com ID, data, tenant, técnico, achados e link para download.

- **Reports:** `http://<host>:<port>/reports`
  - Lista todas as sessões com ID, datas, status, tenant, técnico, contagens e botão “Download” por linha.

- **Configuration:** `http://<host>:<port>/config`
  - Editor de YAML da configuração; ao salvar, o arquivo apontado por `CONFIG_PATH` ou `config.yaml` é atualizado.
- **Help:** `http://<host>:<port>/help` — início rápido, exemplos de config e links para README/USAGE.
- **About:** `http://<host>:<port>/about` — nome da aplicação, versão, autor e licença (conforme LICENSE do repositório).

## API (rotas principais)

| Método | Endpoint                 | Descrição                                                                                       |
|--------|--------------------------|-------------------------------------------------------------------------------------------------|
| `POST` | `/scan` ou `/start`     | Inicia uma varredura completa em background; retorna `session_id`. Aceita body `{ tenant, technician }`. |
| `POST` | `/scan_database`        | Varredura pontual de um único banco (JSON com host/porta/user/pass/driver/etc.).               |
| `GET`  | `/status`               | Retorna `running`, `current_session_id`, `findings_count`.                                     |
| `GET`  | `/report`               | Baixa o último relatório Excel gerado (ou gera a partir da última sessão se necessário).       |
| `GET`  | `/heatmap`              | Baixa o último heatmap PNG gerado.                                                             |
| `GET`  | `/list` ou `/reports`   | Lista sessões anteriores com tenant/technician, contagens e status.                            |
| `GET`  | `/reports/{session_id}` | Gera (se preciso) e baixa o relatório Excel dessa sessão.                                      |
| `GET`  | `/heatmap/{session_id}` | Gera (se preciso) e baixa o heatmap PNG dessa sessão.                                          |
| `PATCH`| `/sessions/{session_id}`            | Ajusta/limpa o `tenant` de uma sessão existente.                                  |
| `PATCH`| `/sessions/{session_id}/technician`| Ajusta/limpa o `technician` de uma sessão existente.                              |
| `GET`  | `/about`       | Página About (HTML): aplicação, versão, autor, licença.                           |
| `GET`  | `/about/json`  | Informações de about em JSON (nome, versão, autor, licença).                       |
| `GET`  | `/health`      | Sonda de liveness/readiness para Docker e Kubernetes.                              |

## Exemplos com curl

Iniciar uma varredura com tenant e técnico:

```bash
curl -X POST http://localhost:8088/scan \
  -H "Content-Type: application/json" \
  -d '{ "tenant": "Acme Corp", "technician": "Alice Silva" }'
```

Baixar o último relatório Excel:

```bash
curl -o report.xlsx http://localhost:8088/report
```

Baixar o último heatmap PNG:

```bash
curl -o heatmap.png http://localhost:8088/heatmap
```

## Deploy com Docker

Você pode executar a API como **container único** (`docker run`), com **Docker Compose**, **Docker Swarm** ou **Kubernetes**. É possível **usar a imagem pré-construída** no Docker Hub ou **construir a partir do código** após clonar o repositório.

### Imagem pré-construída (Docker Hub)

Uma imagem Docker está disponível no **Docker Hub**, permitindo executar a aplicação sem clonar o repositório:

- **Repositório:** [hub.docker.com/r/fabioleitao/python3-lgpd-crawler](https://hub.docker.com/r/fabioleitao/python3-lgpd-crawler)
- **Nome da imagem:** `fabioleitao/python3-lgpd-crawler:latest` (tag `latest`; outras tags de versão podem ser publicadas)

Exemplo: executar a API web com um diretório local de configuração:

```bash
docker pull fabioleitao/python3-lgpd-crawler:latest
docker run -d -p 8088:8088 -v /caminho/para/seu/data:/data -e CONFIG_PATH=/data/config.yaml fabioleitao/python3-lgpd-crawler:latest
```

Prepare `/data/config.yaml` a partir de `deploy/config.example.yaml` (veja [deploy/DEPLOY.md](deploy/DEPLOY.md)). Você pode optar por usar essa imagem como container em vez de clonar o código do Git e construir localmente.

### Construir a partir do código

- **Build:** `docker build -t python3-lgpd-crawler:latest .`
- **Executar:** Monte o config em `/data/config.yaml`. Exponha a porta 8088.
- **Compose:** `docker compose -f deploy/docker-compose.yml -f deploy/docker-compose.override.yml up -d` (prepare `./data/config.yaml` antes).
- **Swarm:** `docker stack deploy -c deploy/docker-compose.yml -c deploy/docker-compose.override.yml lgpd-audit`.
- **Kubernetes:** `kubectl apply -f deploy/kubernetes/` (veja `deploy/kubernetes/README.md`).

Passos completos em **[deploy/DEPLOY.md](deploy/DEPLOY.md)**. A aplicação se comporta corretamente atrás de NAT, load balancer ou proxy reverso (nginx, Traefik, Caddy); defina **X-Forwarded-Proto: https** quando o TLS for terminado no proxy. Cabeçalhos de segurança HTTP (incl. HSTS quando em HTTPS) são aplicados por padrão; veja [SECURITY.md](SECURITY.md).

## Dependências e sincronização (pyproject.toml e requirements.txt)

- O arquivo **`pyproject.toml`** é a fonte de verdade das dependências.  
- Quando precisar de um `requirements.txt` (por exemplo para ambientes legados):

```bash
uv pip compile pyproject.toml -o requirements.txt
```

Isso gera um `requirements.txt` travado e consistente com o que `uv sync` instala.

---

Para detalhes mais avançados (conectores opcionais, REST APIs, Power BI, Dataverse, compartilhamentos), consulte também:

- `README.md` (inglês, completo)
- `docs/USAGE.md` (inglês, foco em uso)
- `docs/USAGE.pt_BR.md` (português – uso da API e configuração)

