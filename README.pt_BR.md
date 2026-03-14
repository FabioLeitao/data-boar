# Data Boar (Português – Brasil)

![Data Boar mascot](api/static/mascot/data_boar_mascote_color.svg)

Data Boar é uma aplicação para auditoria de dados pessoais e sensíveis em bancos de dados e sistemas de arquivos, alinhada a **LGPD**, **GDPR**, **CCPA**, **HIPAA** e **GLBA**. Ela descobre e mapeia possíveis dados pessoais/sensíveis via **regex** e **ML**, armazena apenas **metadados** em um banco SQLite local (incluindo tags opcionais de **cliente/tenant** e **técnico/operador** por varredura) e gera relatórios em Excel e um **heatmap** de sensibilidade/risco em PNG. O nome do pacote Python permanece **python3-lgpd-crawler** para compatibilidade. O mascote de **javali** (boar) reforça a ideia de um crawler “farejando” e procurando dados em várias fontes (bancos, arquivos, APIs, dashboards, compartilhamentos) para fins de conformidade.

> **Release atual:** 1.5.0 (veja [docs/releases/1.5.0.md](docs/releases/1.5.0.md) e a página de [Releases no GitHub](https://github.com/FabioLeitao/data-boar/releases)).

> **Manutenção da documentação:** sempre que um novo recurso ou opção de linha de comando for adicionado, atualize **este arquivo** e o `README.md` em inglês, bem como os arquivos `docs/USAGE.md` e `docs/USAGE.pt_BR.md`, para manter as versões sincronizadas.
> **English:** [README.md](README.md) · [docs/USAGE.md](docs/USAGE.md)

## Funcionalidades principais

- **Múltiplos alvos:** configure, em um único arquivo YAML/JSON, vários bancos de dados, diretórios de arquivos, APIs HTTP, compartilhamentos remotos (SharePoint, WebDAV, SMB/CIFS, NFS), **Power BI** e **Power Apps (Dataverse)**.
- **Bancos SQL:** PostgreSQL, MySQL, MariaDB, SQLite, SQL Server, Oracle, Snowflake (extras opcionais via `pyproject.toml`).
- **Detecção de sensibilidade:** combina regex configurável com ML (TF‑IDF + RandomForest) e opcionalmente DL (embeddings + classificador) em nomes de colunas e amostras de conteúdo. Já reconhece de fábrica PII (CPF, e-mail, telefone, etc.) e **categorias sensíveis** (saúde, religião, filiação política, gênero, biométrico, genético, raça, sindicato, PEP, vida sexual). Nenhum dado bruto é salvo. Termos de treino ML/DL podem ser definidos no config (inline ou via arquivos); guia completo: [docs/sensitivity-detection.pt_BR.md](docs/sensitivity-detection.pt_BR.md) (português) · [docs/sensitivity-detection.md](docs/sensitivity-detection.md) (inglês).
- **Heurísticas para reduzir falsos positivos:** letras de música e cifras de violão são detectadas e tratadas de forma especial para reduzir falsos positivos (datas/números em letras/cifras não viram HIGH sozinhos).
- **SQLite único:** todas as sessões de varredura são gravadas em `audit_results.db`, com tabelas separadas para achados de banco de dados, achados de filesystem e falhas de varredura. Cada sessão tem `session_id`, `started_at`, `finished_at`, `status`, `tenant_name` (cliente/tenant) e `technician_name` (técnico/operador).
- **Relatórios:** para cada sessão, é gerado um arquivo Excel com abas:
- **Report info** (Session ID, Started at, Tenant/Customer, Technician/Operator, Application, Version, Author, License, Copyright; mascote opcional)
- Database findings, Filesystem findings, Scan failures, Recommendations, Praise / existing controls, **Trends – Session comparison** (esta execução vs até 3 anteriores; notas agregadas), **Heatmap data** (tabela + imagem do heatmap embutida, ajuste a uma página ao imprimir)
- Um arquivo **heatmap_\<session_prefix\>.png** é gerado com o mapa de calor de sensibilidade/risco (inclui rodapé com aplicação, autor e licença).
- **CLI e API REST:** modo de execução única via linha de comando ou modo servidor (FastAPI) com dashboard web (Help, About com autor e licença), endpoints para varreduras, relatórios, heatmap, logs e `PATCH /sessions/{session_id}` para metadados de tenant/técnico. Opcionalmente é possível exigir **chave de API** (X-API-Key ou Authorization: Bearer) para todos os endpoints exceto GET /health. A aplicação funciona atrás de NAT, load balancer ou proxy reverso (nginx, Traefik, Caddy); defina **X-Forwarded-Proto: https** quando o TLS for terminado no proxy.

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

| Argumento           | Modo           | Descrição                                                                                                                                                                              |
| ------------------- | -------------- | ---------------------------------------------------------------------------------------------------                                                                                    |
| `--config PATH`     | CLI & API      | Caminho do arquivo de configuração YAML/JSON (padrão `config.yaml`).                                                                                                                   |
| `--web`             | API            | Inicia o servidor FastAPI em vez de executar uma varredura única.                                                                                                                      |
| `--port N`          | API            | Porta da API (padrão 8088). Ignorada em modo CLI.                                                                                                                                      |
| `--reset-data`      | CLI            | **Perigoso**: apaga todas as sessões/achados/falhas do SQLite, remove relatórios/heatmaps em `report.output_dir` e grava um registro na tabela `data_wipe_log`. Não executa varredura. |
| `--tenant NAME`     | CLI            | Nome do cliente/tenant para a sessão; exibido no dashboard, relatórios e aba “Report info”.                                                                                            |
| `--technician NAME` | CLI            | Nome do técnico/operador responsável pela sessão; também exibido no dashboard e relatórios.                                                                                            |

Quando a API está rodando, se `--config` não for fornecido, o servidor lê o caminho da variável de ambiente `CONFIG_PATH` ou usa `config.yaml` no diretório atual.

### Rate limiting e segurança

Para evitar sobrecarga acidental (múltiplas varreduras disparadas em sequência ou sessões demais em paralelo via API/dashboard), é possível habilitar um bloco `rate_limit` no arquivo de configuração:

```yaml
rate_limit:
  enabled: true
  max_concurrent_scans: 1
  min_interval_seconds: 0
  grace_for_running_status: 0
```

Quando `enabled` for true, os endpoints de início de varredura (`POST /scan`, `/start`, `/scan_database`) podem responder **HTTP 429** com um JSON explicando o motivo (por exemplo, sessões demais em execução ou intervalo mínimo ainda não cumprido). A CLI apenas emite avisos com a mesma lógica, sem alterar o código de saída. Detalhes completos e exemplos estão em `docs/USAGE.md` (inglês), `docs/USAGE.pt_BR.md` (português) e na página de manual `docs/lgpd_crawler.5` (seção 5 – formatos de arquivo).

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

| Método   | Endpoint                            | Descrição                                                                                                |
| -------- | --------------------------          | -------------------------------------------------------------------------------------------------        |
| `POST`   | `/scan` ou `/start`                 | Inicia uma varredura completa em background; retorna `session_id`. Aceita body `{ tenant, technician }`. |
| `POST`   | `/scan_database`                    | Varredura pontual de um único banco (JSON com host/porta/user/pass/driver/etc.).                         |
| `GET`    | `/status`                           | Retorna `running`, `current_session_id`, `findings_count`.                                               |
| `GET`    | `/report`                           | Baixa o último relatório Excel gerado (ou gera a partir da última sessão se necessário).                 |
| `GET`    | `/heatmap`                          | Baixa o último heatmap PNG gerado.                                                                       |
| `GET`    | `/list` ou `/reports`               | Lista sessões anteriores com tenant/technician, contagens e status.                                      |
| `GET`    | `/reports/{session_id}`             | Gera (se preciso) e baixa o relatório Excel dessa sessão.                                                |
| `GET`    | `/heatmap/{session_id}`             | Gera (se preciso) e baixa o heatmap PNG dessa sessão.                                                    |
| `PATCH`  | `/sessions/{session_id}`            | Ajusta/limpa o `tenant` de uma sessão existente.                                                         |
| `PATCH`  | `/sessions/{session_id}/technician` | Ajusta/limpa o `technician` de uma sessão existente.                                                     |
| `GET`    | `/about`                            | Página About (HTML): aplicação, versão, autor, licença.                                                  |
| `GET`    | `/about/json`                       | Informações de about em JSON (nome, versão, autor, licença).                                             |
| `GET`    | `/health`                           | Sonda de liveness/readiness para Docker e Kubernetes.                                                    |

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

## Páginas de manual (man)

Em sistemas que usam a interface tradicional
`man`
, há duas páginas de manual:

- **Seção 1 (comando):** `docs/lgpd_crawler.1` – descreve o programa, suas opções, a API web e exemplos com curl. Visualize com `man data_boar` ou `man lgpd_crawler` (ou `man 1 data_boar`, `man 1 lgpd_crawler`).
- **Seção 5 (formatos de arquivo):** `docs/lgpd_crawler.5` – descreve a topologia do config principal e dos arquivos opcionais (regex overrides, arquivos de termos ML/DL, learned patterns), com exemplos. Visualize com `man 5 data_boar` ou `man 5 lgpd_crawler`.

No Linux/BSD, a seção 1 é para programas e comandos; a seção 5 é para formatos de arquivo e convenções de configuração. Instale ambas as páginas e crie os symlinks (veja abaixo) para que **data_boar** e **lgpd_crawler** funcionem: `man data_boar` / `man lgpd_crawler` para o comando, `man 5 data_boar` / `man 5 lgpd_crawler` para config e formatos de arquivo.

**Instalar ambas as páginas** (crie os diretórios de destino antes para que o `cp` não falhe se não existirem). Logo após criar os diretórios, execute `chmod 755` neles para que todos os usuários possam acessar as páginas de manual; dependendo do umask padrão, diretórios novos podem ficar 750 e apenas root conseguiria acessá-los. Após copiar, execute `chmod 644` nos arquivos instalados para que todos possam lê-los (os arquivos copiados podem ficar 640).

```bash
sudo mkdir -p /usr/local/share/man/man1/
sudo mkdir -p /usr/local/share/man/man5/
sudo chmod 755 /usr/local/share/man/man1/ /usr/local/share/man/man5/
sudo cp docs/lgpd_crawler.1 /usr/local/share/man/man1/
sudo cp docs/lgpd_crawler.5 /usr/local/share/man/man5/
sudo chmod 644 /usr/local/share/man/man1/lgpd_crawler.1 /usr/local/share/man/man5/lgpd_crawler.5
sudo ln -sf lgpd_crawler.1 /usr/local/share/man/man1/data_boar.1
sudo ln -sf lgpd_crawler.5 /usr/local/share/man/man5/data_boar.5
sudo mandb    # ou: sudo makewhatis   # conforme a distro
```

Os symlinks fazem com que **data_boar** e **lgpd_crawler** apontem para as mesmas páginas. Depois:

```bash
man data_boar        # ou: man lgpd_crawler     # comando e opções (seção 1)
man 5 data_boar      # ou: man 5 lgpd_crawler   # config e formatos de arquivo (seção 5)
```

Ao adicionar novas opções de CLI ou capacidades da API, atualize `docs/lgpd_crawler.1`; ao alterar chaves de config ou formatos de arquivos de padrão, atualize `docs/lgpd_crawler.5` e este README para que as man pages continuem refletindo o comportamento atual. Os mesmos arquivos são visualizados como `man data_boar` e `man lgpd_crawler` (seções 1 e 5) via symlinks na instalação. Para **bumps de versão** (convenção major.minor.build e onde atualizar o número da versão), veja [docs/VERSIONING.pt_BR.md](docs/VERSIONING.pt_BR.md) ([inglês](docs/VERSIONING.md)).

## Deploy com Docker

Você pode executar a API como **container único** (`docker run`), com **Docker Compose**, **Docker Swarm** ou **Kubernetes**. É possível **usar a imagem pré-construída** no Docker Hub ou **construir a partir do código** após clonar o repositório.

### Imagem pré-construída (Docker Hub)

Imagens Docker estão disponíveis no **Docker Hub**, permitindo executar a aplicação sem clonar o repositório:

- **Branded (Data Boar):** [hub.docker.com/r/fabioleitao/data_boar](https://hub.docker.com/r/fabioleitao/data_boar) — `fabioleitao/data_boar:latest` e `fabioleitao/data_boar:1.5.0`
- **Legado:** [hub.docker.com/r/fabioleitao/python3-lgpd-crawler](https://hub.docker.com/r/fabioleitao/python3-lgpd-crawler) — `fabioleitao/python3-lgpd-crawler:latest` (a mesma imagem pode ser publicada nos dois nomes)

Exemplo: executar a API web com um diretório local de configuração:

```bash
docker pull fabioleitao/data_boar:latest
docker run -d -p 8088:8088 -v /caminho/para/seu/data:/data -e CONFIG_PATH=/data/config.yaml fabioleitao/data_boar:latest
```

Prepare `/data/config.yaml` a partir de `deploy/config.example.yaml` (veja [docs/deploy/DEPLOY.pt_BR.md](docs/deploy/DEPLOY.pt_BR.md) ([EN](docs/deploy/DEPLOY.md))). Você pode optar por usar essa imagem como container em vez de clonar o código do Git e construir localmente.

### Construir a partir do código

- **Build:** `docker build -t python3-lgpd-crawler:latest .`
- **Executar:** Monte o config em `/data/config.yaml`. Exponha a porta 8088.
- **Compose:** `docker compose -f deploy/docker-compose.yml -f deploy/docker-compose.override.yml up -d` (prepare `./data/config.yaml` antes).
- **Swarm:** `docker stack deploy -c deploy/docker-compose.yml -c deploy/docker-compose.override.yml lgpd-audit`.
- **Kubernetes:** `kubectl apply -f deploy/kubernetes/` (veja `deploy/kubernetes/README.md`).

Passos completos em **[docs/deploy/DEPLOY.pt_BR.md](docs/deploy/DEPLOY.pt_BR.md)** ([EN](docs/deploy/DEPLOY.md)). Para MCP, build e push a partir do código: [docs/DOCKER_SETUP.pt_BR.md](docs/DOCKER_SETUP.pt_BR.md) ([EN](docs/DOCKER_SETUP.md)). A aplicação se comporta corretamente atrás de NAT, load balancer ou proxy reverso (nginx, Traefik, Caddy); defina **X-Forwarded-Proto: https** quando o TLS for terminado no proxy. Cabeçalhos de segurança HTTP (incl. HSTS quando em HTTPS) são aplicados por padrão; veja [SECURITY.md](SECURITY.md).

## Frameworks de conformidade e extensibilidade

A aplicação referencia explicitamente **LGPD**, **GDPR**, **CCPA**, **HIPAA** e **GLBA** nos padrões embutidos e nas abas de relatório. É possível estender o suporte a outras normas (ex.: UK GDPR, PIPEDA, APPI, POPIA) sem alterar código: defina **`norm_tag`** nos [overrides de regex](docs/sensitivity-detection.pt_BR.md) ou em conectores customizados com qualquer rótulo de framework e use **`report.recommendation_overrides`** no config para personalizar o texto das recomendações. Detalhes em **[docs/compliance-frameworks.pt_BR.md](docs/compliance-frameworks.pt_BR.md)**.

## Dependências e sincronização (pyproject.toml e requirements.txt)

- **Fonte de verdade:** Para a toolchain **uv**, o **`pyproject.toml`** é a única fonte de verdade das bibliotecas; **pip** e **`requirements.txt`** são derivados (o requirements.txt é gerado a partir do pyproject.toml para ambientes que usam pip). As dependências são declaradas em **`pyproject.toml`**; o **`requirements.txt`** não deve ser editado à mão para alterações de versão. Ao adicionar, remover ou alterar uma dependência, edite apenas **`pyproject.toml`** e depois regenere o `requirements.txt`.
- **Regenerar requirements.txt após qualquer alteração de dependência:**

```bash
# Na raiz do projeto: gerar requirements.txt a partir de pyproject.toml com uv
uv pip compile pyproject.toml -o requirements.txt
```

Isso gera um `requirements.txt` travado e consistente com o que `uv sync` instala.
- **Dependabot / automação:** Se um PR (ex.: do Dependabot) sugerir atualizar apenas o `requirements.txt`, aplique a alteração na **fonte de verdade** primeiro: atualize a versão mínima correspondente em **`pyproject.toml`** (ex.: `fonttools>=4.62.1`), execute `uv pip compile pyproject.toml -o requirements.txt` e faça commit dos dois arquivos. Não faça merge de uma atualização de dependência que edite só o `requirements.txt`.

---

Para detalhes mais avançados (conectores opcionais, REST APIs, Power BI, Dataverse, compartilhamentos), consulte também:

- `README.md` (inglês, completo)
- `docs/USAGE.md` (inglês, foco em uso)
- `docs/USAGE.pt_BR.md` (português – uso da API e configuração)
- **Adicionar novo conector:** [docs/ADDING_CONNECTORS.pt_BR.md](docs/ADDING_CONNECTORS.pt_BR.md) (português) · [docs/ADDING_CONNECTORS.md](docs/ADDING_CONNECTORS.md) (inglês)
- **Detecção de sensibilidade (ML/DL):** [docs/sensitivity-detection.pt_BR.md](docs/sensitivity-detection.pt_BR.md) (português) · [docs/sensitivity-detection.md](docs/sensitivity-detection.md) (inglês)

## Licença e direitos autorais

Veja [LICENSE](LICENSE). Aviso de projeto e direitos autorais: [NOTICE](NOTICE). Para tornar direitos autorais e marca oficial (registro, registros): [docs/COPYRIGHT_AND_TRADEMARK.pt_BR.md](docs/COPYRIGHT_AND_TRADEMARK.pt_BR.md) (português) · [docs/COPYRIGHT_AND_TRADEMARK.md](docs/COPYRIGHT_AND_TRADEMARK.md) (inglês).
