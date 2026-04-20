# Guia técnico (Data Boar)

**English:** [TECH_GUIDE.md](TECH_GUIDE.md)

Este guia cobre instalação, configuração, referência da CLI e da API, conectores suportados e implantação. Para uma introdução de alto nível e o motivo da existência do Data Boar, consulte o [README raiz](../README.md).

## Recursos

- **Varredura multi-alvo**: Configure vários bancos de dados, sistemas de arquivos, APIs, compartilhamentos remotos, **Power BI** e **Power Apps (Dataverse)** em um único arquivo de configuração YAML/JSON. **Importação de escopo (CSV):** `scripts/scope_import_csv.py` gera um fragmento YAML de `targets` a partir de um CSV canônico para revisão e mescla manual — veja [USAGE.pt_BR.md](USAGE.pt_BR.md#scope-import-csv-fragment).
- **Bancos SQL**: PostgreSQL, MySQL, MariaDB, SQLite, Microsoft SQL Server, Oracle (via drivers SQLAlchemy).
- **Power BI (opcional)**: Descubra workspaces, datasets e tabelas via Power BI REST API; amostragem com DAX. OAuth2 do Azure AD (credenciais de cliente). Achados na planilha **Database findings**; inventário na aba **Data source inventory**.
- **Power Apps / Dataverse (opcional)**: Descubra entidades e atributos via Dataverse Web API; amostragem de linhas. OAuth2 do Azure AD (credenciais de cliente). Achados na planilha **Database findings**; inventário na aba **Data source inventory**.
- **Compartilhamentos remotos (opcional)**: SharePoint, WebDAV, SMB/CIFS, NFS — por FQDN ou IP com credenciais na config; instale `.[shares]`.
- **NoSQL (opcional)**: MongoDB, Redis — instale dependências opcionais: `uv pip install -e ".[nosql]"`.
- **Sistema de arquivos**: Varredura recursiva de diretórios locais (ou montados); verificação de permissão antes da leitura. Suporta muitas extensões: texto (`.txt`, `.csv`, `.json`, `.xml`, `.html`, `.md`, `.yml`, `.log`, `.ini`, `.sql`, `.rtf`, legendas **`.srt` / `.vtt` / `.ass` / `.ssa`**, etc.), documentos (`.pdf`, `.doc`, `.docx`, `.odt`, `.ods`, `.odp`, `.xls`, `.xlsx`, `.xlsm`, `.ppt`, `.pptx`), e-mail (`.eml`, `.msg`) e dados (`.sqlite`, `.db`). **Rich media opcional:** `file_scan.scan_rich_media_metadata` e `scan_image_ocr` (padrão desligado) acrescentam texto de EXIF/tags de áudio/tags de vídeo e OCR Tesseract opcional; instale `.[richmedia]` e, para OCR/tags de vídeo, **tesseract** / **ffprobe** no `PATH`. **Arquivos SQLite** (`.sqlite`, `.sqlite3`, `.db`) encontrados em disco são abertos e varridos como bancos (descobrir tabelas/colunas, amostrar e detectar); defina `file_scan.scan_sqlite_as_db: false` para pular. Defina `file_scan.extensions` como lista de sufixos ou `"*"` / `"all"` para todos os tipos suportados.
- **Detecção de sensibilidade**: Regex (configurável) + **ML** (TF-IDF + RandomForest) + **DL** opcional (embeddings de sentença + classificador) em nomes de colunas e conteúdo amostrado; nenhum dado bruto é armazenado. Você pode definir **termos de treinamento ML e DL** na config (inline ou via `ml_patterns_file` / `dl_patterns_file`). Veja [SENSITIVITY_DETECTION.md](SENSITIVITY_DETECTION.md) (inglês) ou [SENSITIVITY_DETECTION.pt_BR.md](SENSITIVITY_DETECTION.pt_BR.md) (Português – Brasil) para exemplos. **Letras de música e tablaturas** são detectadas por heurísticas para que sequências tipo data ou dígitos em letras e tablaturas sejam rebaixadas para MEDIUM/LOW e reduzir falsos positivos; PII forte (CPF, e-mail, etc.) continua reportando HIGH.
- **Multilíngue, multi-encoding e multirregional**: Config e arquivos de padrões suportam **UTF-8** (recomendado), UTF-8 com BOM e encodings legados (cp1252, Latin-1); o config principal é lido com **auto-detecção**. Amostras de conformidade e relatórios suportam **Unicode** e termos no idioma da sua região (ex.: EN+FR para Canadá, PT-BR+EN para Brasil). **Amostras de config para UK GDPR, EU GDPR, Benelux, PIPEDA, POPIA, APPI, PCI-DSS e outras regiões** estão em [compliance-samples/](compliance-samples/); veja [COMPLIANCE_FRAMEWORKS.pt_BR.md – Amostras de conformidade](COMPLIANCE_FRAMEWORKS.pt_BR.md#amostras-de-conformidade) ([EN](COMPLIANCE_FRAMEWORKS.md#compliance-samples)) para a lista e como usar. Defina **`pattern_files_encoding`** quando usar arquivos de padrões que não estejam em UTF-8. Veja [USAGE – Encoding de arquivos](USAGE.pt_BR.md#file-encoding-config-and-pattern-files) e [COMPLIANCE_FRAMEWORKS – Operação multilíngue e multirregional](COMPLIANCE_FRAMEWORKS.pt_BR.md#operação-multilíngue-multi-encoding-e-multirregional).
- **SQLite único**: Todos os achados e falhas por sessão (UUID + timestamp); metadados por varredura incluem **tenant_name** (cliente/tenant) e **technician_name** (operador responsável) opcionais. Tabelas separadas para achados de banco, achados de sistema de arquivos e falhas de varredura.
- **Relatórios**: Excel com planilhas **"Report info"** (Session ID, Started at, Tenant/Customer, Technician/Operator, Application, Version, Author, License, Copyright), "Database findings", "Filesystem findings", **"Data source inventory"** (metadados best-effort por alvo), opcional **"Suggested review (LOW)"** (colunas com nome de identificador persistidas quando `detection.persist_low_id_like_for_review` é true — redução de falsos negativos; veja [SENSITIVITY_DETECTION.pt_BR.md](SENSITIVITY_DETECTION.pt_BR.md)), "Scan failures", "Recommendations", "Praise / existing controls" (indicações de criptografia/hash/tokenização), **"Trends - Session comparison"** (esta execução vs até 3 anteriores; notas agregadas), **"Heatmap data"** (tabela mais imagem de heatmap embutida, ajustada a uma página na impressão) e um PNG standalone de heatmap de sensibilidade/risco. Report info e heatmap incluem opcionalmente a marca do mascote Data Boar; páginas de dashboard/relatórios mostram aplicação e atribuição de autor.
- **CLI e API REST**: Execute auditoria única pela linha de comando ou inicie a API (porta padrão 8088) para `/scan`, `/start`, `/scan_database`, `/status`, `/report`, `/heatmap`, `/list`, `/reports/{session_id}`, `/logs` e `PATCH /sessions/{session_id}` para metadados tenant/technician. As páginas **HTML** usam **prefixo de idioma** (ex.: `/en/`, `/pt-br/`); endpoints JSON permanecem sem prefixo — veja [USAGE.pt_BR.md](USAGE.pt_BR.md) (URLs principais / locale). Ambos os modos permitem marcar varreduras com informações opcionais de **tenant/customer** e **technician/operator**. **API key opcional** e **rate limiting** (veja [USAGE.pt_BR.md](USAGE.pt_BR.md)) protegem a API quando exposta. O dashboard web inclui **Help**, **About** (autor e licença) e cabeçalhos de segurança (veja [SECURITY.md](../SECURITY.md)). A aplicação funciona atrás de NAT, balanceadores de carga e proxies reversos (nginx, Traefik, Caddy); defina `X-Forwarded-Proto: https` quando o TLS for encerrado no proxy.

## Requisitos e preparação do ambiente

- **Sistema operacional**: Ubuntu 24.04 LTS / Debian 13 (recomendado) ou Linux/macOS/Windows recente.
- **Python**: **≥3.12** suportado; **3.13 recomendado** para paridade com a **imagem Docker publicada** (`python:3.13-slim`).
- **Gerenciador de pacotes**: [uv](https://github.com/astral-sh/uv) (recomendado) ou `pip`.

### Versões menores do Python (desenvolvimento local vs imagem Docker)

- **Declarado:** `pyproject.toml` exige **Python ≥3.12**. A **CI** roda **pytest** em **3.12 e 3.13** (veja `.github/workflows/ci.yml`).
- **Recomendado no host:** use **3.13** quando a distro empacotar (mesma família de intérprete que **Docker Hub** / `latest`); **3.12** segue totalmente suportado.
- **Análise estática:** `sonar.python.version` em `sonar-project.properties` fica em **3.12** (valor único do analisador Python do Sonar — não é teto de runtime).
- **Dockerfile** usa **`python:3.13-slim`** — imagens publicadas rodam **CPython 3.13** de ponta a ponta; disciplina de bump e matriz: `docs/plans/PYTHON_UPGRADE_PLAYBOOK.pt_BR.md` (versão EN homóloga no mesmo diretório).

### Instalar Python e bibliotecas do sistema (exemplo Linux)

No Debian/Ubuntu:

```bash
sudo apt update
sudo apt install -y python3.13 python3.13-venv python3.13-dev build-essential \
  libpq-dev libssl-dev libffi-dev unixodbc-dev default-libmysqlclient-dev
```

- Em distros mais antigas **sem** **`python3.13`**, use **`python3.12`** / **`python3.12-venv`** / **`python3.12-dev`** (ainda na CI).
- Os pacotes **`python3.*[-dev]`** e **`build-essential`** são necessários para compilar alguns drivers (ex.: clientes de banco).
- `libpq-dev`, `unixodbc-dev` e cabeçalhos SSL/FFI ajudam ao usar PostgreSQL, SQL Server, Oracle ou outros drivers SQLAlchemy.
- `default-libmysqlclient-dev` fornece cabeçalhos/bibliotecas para **mysqlclient** (MySQL/MariaDB); omita se usar só **pymysql** e os wheels cobrirem sua plataforma.

**Laptop ThinkPad LAB-NODE-01 com LMDE 7 (Debian 13):** checklist completo (atualização, `ufw`, firmware `fwupd`, pacotes acima + opcionais Podman/Docker) — **[LMDE7_LAB-NODE-01_DEVELOPER_SETUP.pt_BR.md](ops/LMDE7_LAB-NODE-01_DEVELOPER_SETUP.pt_BR.md)**.

**Outras distribuições Linux:** Para **RHEL/Fedora/AlmaLinux** (`dnf`), **Arch/Manjaro** (`pacman`), **Gentoo** (`emerge`), **Void** (`xbps`), **Alpine** (`apk`) e outros gerenciadores, veja **[OS_COMPATIBILITY_TESTING_MATRIX.pt_BR.md](ops/OS_COMPATIBILITY_TESTING_MATRIX.pt_BR.md)** para nomes de pacotes específicos e notas de instalação. **illumos** (OpenIndiana, etc.) / legado **OpenSolaris** é só **exploratório** (Tier 4 na matriz EN).

No Windows:

- Instale **Python 3.13** (recomendado) ou qualquer **3.12+** em python.org e marque "Adicionar Python ao PATH".
- **WSL2:** muitos desenvolvedores **executam** **`uv sync`** / **`pytest`** dentro de uma distro **Linux** (Debian, Ubuntu…) para paridade com os docs de servidor; clone o repo no **sistema de arquivos Linux** dentro do WSL, não só em `/mnt/c/...`. Distros **extra** para matriz de compatibilidade: [WINDOWS_WSL_MULTI_DISTRO_LAB.pt_BR.md](ops/WINDOWS_WSL_MULTI_DISTRO_LAB.pt_BR.md).
- Instale ferramentas de cliente de banco conforme necessário (ex.: Oracle Instant Client, driver ODBC do SQL Server) seguindo a documentação do fabricante.

### Instalar uv

O `uv` é um gerenciador rápido de pacotes/dependências Python:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh          # Linux/macOS
py -m pip install uv                                    # Windows (alternativa se não usar o instalador)
```

Após a instalação, verifique se o `uv` está no seu `PATH`:

```bash
uv --version
```

Você pode sempre usar `pip` + virtualenv se preferir.

## Instalar a aplicação

```bash
# Com uv (recomendado) – cria virtualenv e instala dependências
uv sync

# Ou com pip (dentro de um virtualenv ativado)
pip install -e .
```

### Executando a aplicação com uv

O `uv` também pode executar a aplicação diretamente com todas as dependências:

```bash
# Varredura CLI única
uv run python main.py --config config.yaml

# Iniciar o servidor da API (equivalente a python main.py --web)
uv run python main.py --config config.yaml --web --port 8088
```

Suporte opcional NoSQL (MongoDB, Redis):

```bash
uv pip install -e ".[nosql]"
# ou: pip install -e ".[nosql]"
```

## Configuração

Use um único arquivo de configuração em **YAML** ou **JSON**. A API carrega a partir de `CONFIG_PATH` ou `config.yaml` no diretório de trabalho. Para **destinos e credenciais** detalhados (bancos, sistemas de arquivos, APIs com basic/bearer/OAuth2 e conteúdo compartilhado), veja **[USAGE.pt_BR.md](USAGE.pt_BR.md)**. Para uso **multilíngue e multirregional** (encoding, amostras de conformidade por região), veja [USAGE – Encoding de arquivos](USAGE.pt_BR.md#file-encoding-config-and-pattern-files) e [COMPLIANCE_FRAMEWORKS](COMPLIANCE_FRAMEWORKS.pt_BR.md#operação-multilíngue-multi-encoding-e-multirregional). Exemplo `config.yaml`:

```yaml
targets:

- name: "Producao_Postgres"

  type: database
  driver: postgresql+psycopg2
  host: 10.0.0.50
  port: 5432
  user: audit_user
  pass: secure_password
  database: customers_db

- name: "Documentos_LGPD"

  type: filesystem
  path: /home/user/Documents/LGPD
  recursive: true

file_scan:
  extensions: [.txt, .csv, .pdf, .docx, .xlsx]
  recursive: true
  scan_sqlite_as_db: true   # open .sqlite/.db files as DBs and scan tables/columns
  sample_limit: 5
  # Opcional: varrer dentro de arquivos compactados (zip, tar, gz, bz2, xz, 7z, …)
  # Quando true, arquivos candidatos são abertos e membros internos com extensões suportadas
  # são varridos como arquivos normais. Isso pode aumentar bastante tempo de execução, I/O e uso
  # de espaço temporário; habilite só quando necessário e prefira escopo menor na primeira vez.
  scan_compressed: false
  # max_inner_size: faixa válida 1 MB–500 MB (padrão 10 MB); membros maiores são ignorados.
  # max_inner_size: 50_000_000   # limite opcional de bytes internos por arquivo compactado
  # compressed_extensions: [".zip", ".tar", ".gz", ".tgz", ".bz2", ".xz", ".7z"]
  # use_content_type: false   # magic bytes: recorte PDF + remapeamento rich media quando a extensão engana
  # scan_rich_media_metadata: false   # EXIF, mutagen, ffprobe (binários opcionais)
  # scan_image_ocr: false   # Tesseract via pytesseract + tesseract-ocr no sistema
  # ocr_lang: eng
  # ocr_max_dimension: 2000   # limitado entre 256 e 8000

report:
  output_dir: .

api:
  port: 8088

sqlite_path: audit_results.db
scan:
  max_workers: 1   # 1 = sequential; >1 = parallel

# Optional: external pattern files (no code change)
ml_patterns_file: ml_patterns.yaml
regex_overrides_file: regex_overrides.yaml
```

O legado `config/config.json` com `databases` e `file_scan.directories` é normalizado automaticamente.

### Arquivo de padrões ML (opcional)

Lista YAML/JSON de `text` + `label` (sensitive / non_sensitive) para treinar ou estender o classificador:

```yaml

- text: "cpf"

  label: sensitive

- text: "system_log"

  label: non_sensitive
```

### Padrões aprendidos (opcional)

Ao final de cada execução (quando o relatório é gerado), o motor pode gravar **padrões aprendidos**: termos classificados como sensíveis nessa varredura, para você mesclar em `ml_patterns_file` na próxima execução. Isso melhora a detecção futura e limita falsos positivos (apenas sensibilidade HIGH por padrão, confiança mínima e exclusão de termos genéricos como `id`, `name`).

Habilite na config:

```yaml
learned_patterns:
  enabled: true
  output_file: learned_patterns.yaml
  min_sensitivity: HIGH      # or MEDIUM to also capture borderline cases
  min_confidence: 70
  min_term_length: 3
  require_pattern: true      # only learn when a pattern was actually detected
  append: true               # merge with existing file
  exclude_if_in_ml_patterns: true   # skip terms already in ml_patterns_file
```

**Mesclar nos padrões ML:** Copie ou mescle entradas de `learned_patterns.yaml` no seu `ml_patterns_file`. Cada entrada tem `text` e `label: sensitive`; opcionalmente `pattern_detected` e `norm_tag` ajudam na revisão. Use o mesmo formato do arquivo de padrões ML (lista de `text` + `label`). Após mesclar, a próxima execução usará o conjunto expandido no classificador.

### Substituições de regex (opcional)

Lista YAML/JSON de `name`, `pattern`, opcional `norm_tag`:

```yaml

- name: LGPD_CPF

  pattern: "\b\d{3}\.?\d{3}\.?\d{3}-?\d{2}\b"
  norm_tag: "LGPD Art. 5"
```

### Limitação de taxa e segurança (opcional)

Para evitar sobrecarga acidental (várias varreduras seguidas ou muitas em paralelo quando chamado via API/dashboard), você pode habilitar um bloco `rate_limit` na config principal:

```yaml
rate_limit:
  enabled: true
  max_concurrent_scans: 1
  min_interval_seconds: 0
  grace_for_running_status: 0
```

Quando `enabled` é true, os endpoints da API que iniciam varreduras (`POST /scan`, `/start`, `/scan_database`) podem responder com **HTTP 429** e um payload JSON descrevendo o motivo (ex.: muitas varreduras em execução ou intervalo mínimo não decorrido). A CLI apenas imprime avisos com a mesma lógica, então scripts existentes continuam funcionando. Veja [USAGE.md](USAGE.md) e [data_boar.5](data_boar.5) para detalhes e exemplos completos de configuração.

## Executar

### CLI (auditoria única)

```bash
# Execução mínima com opções padrão
python main.py --config config.yaml

# Alterar porta de relatório/API via config (sem --web aqui; modo único ignora --port)
python main.py --config config_prod.yaml

# Marcar execução com tenant/customer e technician/operator
python main.py --config config.yaml --tenant "Acme Corp" --technician "Alice Colleague-V"

# Relatório gravado em report.output_dir, ex.: Relatorio_Auditoria_<session_id>.xlsx
```

### API REST (porta padrão 8088)

```bash
# Iniciar API na porta padrão 8088
python main.py --config config.yaml --web

# Iniciar API em porta customizada
python main.py --config config.yaml --web --port 9090

# Equivalente (sem usar a CLI do main.py)
uvicorn api.routes:app --host 0.0.0.0 --port 8088
```

## Argumentos da CLI (referência)

| Argumento           | Modo                     | Descrição                                                                                                                                                                                                             | Exemplos                                             |
| ---------           | ------                   | -------------                                                                                                                                                                                                         | ----------                                           |
| `--config PATH`     | CLI e API                | Caminho do arquivo de config YAML/JSON. Padrão `config.yaml` se omitido.                                                                                                                                              | `--config config.yaml`, `--config configs/prod.yaml` |
| `--web`             | Somente API              | Iniciar a API REST em vez de executar uma varredura única.                                                                                                                                                            | `--web`                                              |
| `--port N`          | Somente API              | Porta da API REST quando `--web` está definido. Padrão `8088`. Ignorado no modo CLI único.                                                                                                                            | `--web --port 9090`                                  |
| `--reset-data`      | Somente CLI (manutenção) | **Perigoso**: apaga todas as sessões de varredura, achados e falhas do SQLite, remove relatórios/heatmaps gerados em `report.output_dir` e registra o evento em `data_wipe_log` para auditoria. Não inicia varredura. | `--reset-data`                                       |
| `--tenant NAME`     | Somente CLI (único)      | Nome opcional de customer/tenant para esta varredura. Armazenado em `scan_sessions.tenant_name`, exibido no dashboard e na planilha **Report info**.                                                                  | `--tenant "Acme Corp"`                               |
| `--technician NAME` | Somente CLI (único)      | Nome opcional do técnico/operador responsável por esta varredura. Armazenado em `scan_sessions.technician_name`, exibido no dashboard e na planilha **Report info**.                                                  | `--technician "Alice Colleague-V"`                         |

Ao usar a API (`--web`), o servidor carrega a config de **`CONFIG_PATH`** (variável de ambiente) ou `config.yaml` no diretório de trabalho se `--config` não for informado na CLI.

**Dashboard web:** Com o servidor em execução, abra <http://localhost:8088/en/> (ou `/pt-br/`) para um dashboard simples: status da varredura, quantidade/qualidade dos dados descobertos (achados DB/FS, falhas), **gráfico de progresso ao longo do tempo** (total de achados e score de risco por sessão), campos opcionais para **tenant/customer** e **technician/operator** antes de iniciar uma varredura, sessões recentes (incluindo colunas tenant/technician) e links para **Reports** (lista e download) e **Configuration** (editar YAML no navegador). O `/` sem prefixo redireciona para o locale negociado (cookie, `Accept-Language`, config).

## Rotas da API (resumo)

| Método   | Endpoint                            | Descrição                                                                                                                                                       |
| -------- | ----------                          | -------------                                                                                                                                                   |
| `POST`   | `/scan` ou `/start`                 | Inicia auditoria completa em segundo plano; retorna `session_id`. Corpo JSON opcional: `{ "tenant": "Acme Corp", "technician": "Alice" }` para marcar a sessão. |
| `POST`   | `/scan_database`                    | Varredura pontual de um banco (corpo JSON); retorna `session_id`                                                                                                |
| `GET`    | `/status`                           | `running`, `current_session_id`, `findings_count`                                                                                                               |
| `GET`    | `/report`                           | Download do relatório Excel **último gerado**                                                                                                                   |
| `GET`    | `/heatmap`                          | Download do heatmap PNG **último gerado** (heatmap de sensibilidade/risco da sessão mais recente)                                                               |
| `GET`    | `/list` ou `/reports`               | Lista sessões anteriores (para escolher um relatório); inclui `tenant_name`, `technician_name`, contagens e status.                                             |
| `GET`    | `/reports/{session_id}`             | Regenera e baixa o relatório dessa sessão                                                                                                                       |
| `GET`    | `/heatmap/{session_id}`             | Regenera relatório (se necessário) e baixa o heatmap PNG dessa sessão                                                                                           |
| `PATCH`  | `/sessions/{session_id}`            | Define ou limpa o nome tenant/customer de uma sessão existente. Corpo: `{ "tenant": "..." }`.                                                                   |
| `PATCH`  | `/sessions/{session_id}/technician` | Define ou limpa o nome technician/operator de uma sessão existente. Corpo: `{ "technician": "..." }`.                                                           |

Para **implantação**, **uso da API web** (com exemplos de requisição/resposta), **configuração e credenciais** (bancos, sistemas de arquivos, APIs com basic/bearer/OAuth2 e conteúdo compartilhado) e **download de relatórios atuais e anteriores**, veja **[USAGE.md](USAGE.md)**.

## Bancos e drivers suportados

| Engine           | Driver (config)             | Nota                                                                                                                                  |
| -----------      | --------------------------- | -------------------------                                                                                                             |
| PostgreSQL       | `postgresql+psycopg2`       | psycopg2-binary                                                                                                                       |
| MySQL            | `mysql+pymysql`             | pymysql                                                                                                                               |
| MariaDB          | `mysql+pymysql`             | mesmo que MySQL                                                                                                                       |
| SQLite           | `sqlite`                    | database = path                                                                                                                       |
| SQL Server       | `mssql+pyodbc`              | pyodbc                                                                                                                                |
| Oracle (19+ RAC) | `oracle+oracledb`           | oracledb (modo thin; sem Oracle Client). Na config `database` = nome do serviço (ex.: customers_db ou ORCL).                          |
| Snowflake        | `snowflake`                 | opcional: `uv pip install -e ".[bigdata]"`; config usa `account`, `user`, `pass`, `database`, `schema`, `warehouse`, opcional `role`. |
| MongoDB          | `mongodb`                   | opcional: pymongo                                                                                                                     |
| Redis            | `redis`                     | opcional: redis                                                                                                                       |

Para MongoDB/Redis, adicione um alvo com `type: database` e `driver: mongodb` ou `redis` (host, port, database/password conforme necessário). Instale dependências opcionais: `uv pip install -e ".[nosql]"`. Para Snowflake, adicione um alvo com `type: database` e `driver: snowflake` e instale o extra `.[bigdata]`.

## Alvos REST/API e autenticação

Você pode varrer APIs HTTP(S) remotas em busca de dados pessoais ou sensíveis adicionando alvos com `type: api` ou `type: rest`. O conector chama os endpoints configurados (GET), interpreta JSON e aplica a mesma detecção de sensibilidade em nomes de campos e valores amostrados. A **autenticação** é configurável para usar credenciais estáticas, tokens bearer (ex.: negociados ou emitidos por um IdP) ou OAuth2 client credentials.

**Obrigatório:** `name`, `base_url` (ou `url`). **Opcional:** `paths` ou `endpoints` (lista de paths, ex.: `["/users", "/orders"]`), `discover_url` (GET retorna lista de paths a varrer), `timeout`, `headers` e um bloco `auth`.

### Tipos de auth

| Tipo              | Caso de uso                                                            | Config                                                                                                                                                      |
| ------            | ----------                                                             | --------                                                                                                                                                    |
| **basic**         | Usuário e senha estáticos                                              | `auth: { type: basic, username: "...", password: "..." }`                                                                                                   |
| **bearer**        | Token estático ou negociado (ex.: Kerberos/AD ou API key)              | `auth: { type: bearer, token: "..." }` ou `token_from_env: "MY_TOKEN_VAR"`                                                                                  |
| **oauth2_client** | OAuth2 client credentials (máquina a máquina)                          | `auth: { type: oauth2_client, token_url: "<https://...",> client_id: "...", client_secret: "..." }` (ou `client_secret: "${ENV_VAR}"` para ler do ambiente) |
| **custom**        | Cabeçalhos customizados (ex.: `Authorization: Negotiate ...`, API key) | `auth: { type: custom, headers: { "Authorization": "Bearer ...", "X-API-Key": "..." } }`                                                                    |

Se você omitir `auth` mas definir `user`/`username` e `pass`/`password` no alvo, a auth **basic** é usada.

## Exemplo de config (YAML) — API/REST

```yaml
targets:

- name: "Internal Users API"

  type: api
  base_url: "https://api.example.com"
  paths: ["/users", "/profiles"]
  auth:
    type: oauth2_client
    token_url: "https://auth.example.com/oauth/token"
    client_id: "audit-client"
    client_secret: "${API_OAUTH_SECRET}"
    scope: "read:users"

- name: "Legacy API (basic)"

  type: rest
  base_url: "https://legacy.example.com"
  paths: ["/v1/contacts"]
  auth:
    type: basic
    username: "audit_user"
    password: "***"

- name: "API with bearer token (e.g. negotiated)"

  type: api
  base_url: "https://api.example.com"
  paths: ["/data"]
  auth:
    type: bearer
    token_from_env: "NEGOTIATED_TOKEN"   # or use "token" for static value

- name: "API with custom header"

  type: api
  base_url: "https://api.example.com"
  paths: ["/export"]
  auth:
    type: custom
    headers:
      Authorization: "Bearer ..."
      X-Requested-By: "lgpd-audit"
```

Achados de alvos de API aparecem na planilha **Filesystem findings** com `file_name` no formato `GET /users | email` (endpoint e campo). O projeto usa **httpx** (já é dependência) para HTTP; não é necessária instalação extra para o conector REST.

## Power BI e Power Apps (Dataverse)

Você pode varrer **Power BI** (datasets e tabelas) e **Power Apps / Dataverse** (entidades e colunas) como fontes de dados. Ambos usam **OAuth2 client credentials do Azure AD** (registro de app com client secret). Não é necessária instalação extra (httpx já é dependência).

### Power BI

- **Tipo:** `powerbi`
- **Auth:** App Azure AD com permissões Power BI (`Dataset.Read.All` ou `Dataset.ReadWrite.All`). Habilite "Allow service principals to use Power BI APIs" no portal admin do Power BI se usar service principal.
- **Config:** `tenant_id`, `client_id`, `client_secret` (ou em `auth:`). Opcional: `workspace_ids` ou `group_ids` para limitar a workspaces específicos; omita para "My workspace" e todos os workspaces que o app pode ver.

O conector lista datasets e tabelas (push datasets expõem schema de tabela; para outros amostra via DAX), executa detecção de sensibilidade em nomes de colunas e valores amostrados e grava em **Database findings** (schema = nome do dataset, table = nome da tabela, column = coluna).

### Exemplo de config (YAML) — Power BI

```yaml
targets:

- name: "Power BI Compliance"

  type: powerbi
  tenant_id: "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
  client_id: "yyyyyyyy-yyyy-yyyy-yyyy-yyyyyyyyyyyy"
  client_secret: "${POWERBI_CLIENT_SECRET}"   # or literal
  # optional: limit to specific workspaces
  # workspace_ids: ["group-guid-1", "group-guid-2"]
```

### Power Apps / Dataverse

- **Tipo:** `dataverse` ou `powerapps`
- **Auth:** App Azure AD com permissão de aplicação ao Dataverse (ex.: "Common Data Service" / `user_impersonation` ou permissão de aplicação por ambiente). Consentimento de admin necessário.
- **Config:** `org_url` (ou `environment_url`), ex.: `<https://myorg.crm.dynamics.co>m`, mais `tenant_id`, `client_id`, `client_secret` (ou em `auth:`).

O conector lista entidades (tabelas), seus atributos, amostra linhas, executa detecção de sensibilidade e grava em **Database findings** (schema = nome lógico da entidade, table = entity set, column = atributo).

### Exemplo de config (YAML) — Dataverse

```yaml
targets:

- name: "Dataverse HR"

  type: dataverse
  org_url: "https://myorg.crm.dynamics.com"
  tenant_id: "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
  client_id: "yyyyyyyy-yyyy-yyyy-yyyy-yyyyyyyyyyyy"
  client_secret: "${DATAVERSE_CLIENT_SECRET}"
```

Use o mesmo `file_scan.sample_limit` (padrão 5) para controlar quantas linhas são amostradas por tabela/entidade no Power BI e Dataverse.

## SharePoint, WebDAV, SMB/CIFS e compartilhamentos NFS

Você pode varrer compartilhamentos de arquivos remotos por **FQDN ou IP** com credenciais na config. Instale dependências opcionais:
`uv pip install -e ".[shares]"`
(instala `smbprotocol`, `webdavclient3`, `requests_ntlm`).

| Tipo               | Host / URL                                                         | Credenciais                       | Notas                                                                       |
| ------             | ------------                                                       | -------------                     | --------                                                                    |
| **sharepoint**     | `site_url`: `<https://host/sites/sitenam>e`                        | `user`, `pass`; NTLM ou basic     | On-prem ou URL; path = pasta relativa ao servidor (ex.: `Shared Documents`) |
| **webdav**         | `base_url`: `<https://host/pat>h`                                  | `user`, `pass`                    | Listagem e download recursivos                                              |
| **smb** / **cifs** | `host`: FQDN ou IP, `share`: nome do share, `path`: caminho dentro | `user`, `pass`, opcional `domain` | Porta 445 padrão                                                            |
| **nfs**            | `path`: **ponto de montagem local** (NFS deve estar montado antes) | —                                 | `host` / `export_path` apenas para relatório                                |

### Exemplo de config (YAML) — Compartilhamentos de arquivo

```yaml
targets:
  # SMB/CIFS (Windows ou Samba)
- name: "FileServer HR"

  type: smb
  host: "fileserver.company.local"   # or 10.0.0.10
  share: "HR"
  path: "Documents"
  user: "audit_user"
  pass: "***"
  domain: "COMPANY"                 # optional
  port: 445
  recursive: true

  # WebDAV
- name: "WebDAV Storage"

  type: webdav
  base_url: "https://webdav.company.com/dav"
  user: "audit"
  pass: "***"
  path: "archive"
  recursive: true
  verify_ssl: true

  # SharePoint (on-prem ou URL; NTLM ou basic)
- name: "SharePoint HR"

  type: sharepoint
  site_url: "https://sharepoint.company.com/sites/hr"
  path: "Shared Documents"
  user: "audit@company.com"
  pass: "***"

  # NFS (path = ponto de montagem local; monte o NFS antes)
- name: "NFS Export"

  type: nfs
  host: "nfs.company.local"
  export_path: "/export/data"
  path: "/mnt/nfs_data"             # local mount point
```

Todos os tipos de share usam as mesmas configurações **file_scan** (extensions, recursive, scan_sqlite_as_db, sample_limit) da config. Os achados aparecem na planilha **Filesystem findings**.

Com `file_scan.use_content_type: true`, os conectores de **compartilhamento** usam o mesmo helper que o filesystem. **Disfarce simples** aqui é quando a **extensão do nome** não bate com o **formato real** (ex.: bytes de PDF atrás de `.txt` ou de extensão **não textual** como `.mp3`). Quem só segue a extensão erra; os *magic bytes* ainda mostram `%PDF-...` ou assinatura de mídia rica — daí PDFs seguem o fluxo de PDF na extração e **imagem/áudio/vídeo** com extensão enganosa são remapeados pela mesma tabela. `scan_rich_media_metadata` / `scan_image_ocr` valem para SMB, WebDAV e SharePoint (e dentro de arquivos compactados quando o membro interno for elegível). Continua **opt-in**; com o flag desligado, a escolha de tipo segue a extensão (salvo inclusão explícita de extensões rich media quando esses flags ampliam o conjunto).

Para **uma única execução** sem alterar o config gravado: CLI **`--content-type-check`**, ou **`POST /scan`** / **`POST /start`** com **`content_type_check: true`**, ou a caixa no dashboard (mesma ideia que **`--scan-compressed`** / **`scan_compressed`** para arquivos compactados).

## Adicionando novos conectores

Para suportar uma nova fonte de dados (ex.: outro driver de banco ou API), veja **[ADDING_CONNECTORS.md](ADDING_CONNECTORS.md)** (inglês) ou **[ADDING_CONNECTORS.pt_BR.md](ADDING_CONNECTORS.pt_BR.md)** (Português – Brasil). O guia descreve o contrato do conector, como registrar um novo tipo (ou driver), dependências opcionais e inclui instruções passo a passo e exemplos (estilo banco e estilo API).

## Log e alertas

- Arquivo de log: `audit_YYYYMMDD.log` (e console).
- A cada achado (possível dado pessoal/sensível), o app registra em log e imprime um `[ALERT]` no console para o operador ser notificado na hora.

## Dependências e segurança

- **Fonte da verdade:** Para a ferramenta **uv**, o **`pyproject.toml`** é a fonte de verdade das dependências declaradas; o **`uv.lock`** fixa a árvore resolvida para instalações reproduzíveis (evita quebras “funcionou ontem”). **pip** e **`requirements.txt`** são derivados (o requirements.txt é exportado do lockfile para ambientes pip). Não edite **`uv.lock`** nem **`requirements.txt`** à mão para mudanças de versão. Ao adicionar, remover ou alterar uma dependência, edite apenas o **`pyproject.toml`**, depois execute `uv lock` e export.

- **Regenere o lockfile e o requirements.txt após qualquer alteração de dependência:**

  ```bash
  # Na raiz do projeto: resolver e bloquear, depois exportar para pip
  uv lock
  uv export --no-emit-package pyproject.toml -o requirements.txt
  ```

  Faça commit de **pyproject.toml**, **uv.lock** e **requirements.txt**. Assim as instalações permanecem reproduzíveis e alinhadas; `pip install -r requirements.txt` equivale ao `uv sync`.

- **Dependabot / automação:** Se um PR (ex.: do Dependabot) sugerir atualizar só o `requirements.txt` ou o `uv.lock`, aplique a alteração na **fonte da verdade** primeiro: atualize a versão mínima correspondente no **`pyproject.toml`**, depois execute `uv lock` e `uv export --no-emit-package pyproject.toml -o requirements.txt` e faça commit dos três arquivos. Não faça merge de uma atualização de dependência que edite apenas `requirements.txt` ou `uv.lock`.

- **Verificar CVEs conhecidos:** Execute `uv pip audit` (ou `pip audit` se disponível) antes da implantação; corrija ou fixe pacotes vulneráveis.
- Veja também **Segurança e conformidade** abaixo.

## Páginas man

Para sistemas que usam a interface tradicional `man`, duas páginas de manual são fornecidas:

- **Seção 1 (comando):** [data_boar.1](data_boar.1) — descreve o programa, suas opções, a API web e exemplos com curl. Visualize com `man data_boar` (ou `man lgpd_crawler` com symlink de compatibilidade).
- **Seção 5 (formatos de arquivo):** [data_boar.5](data_boar.5) — descreve a topologia do arquivo de config principal e arquivos opcionais (regex overrides, arquivos de padrões ML/DL, padrões aprendidos), com exemplos. Visualize com `man 5 data_boar` (ou `man 5 lgpd_crawler` com symlink).

No Linux/BSD, a seção 1 é para comandos executáveis; a seção 5 é para configuração e convenções de formato de arquivo. Instale as páginas **Data Boar** e, para compatibilidade, opcionalmente crie symlinks para `man lgpd_crawler` (veja abaixo).

**Instale ambas as páginas** (crie os diretórios de destino antes para a cópia não falhar se estiverem ausentes). Logo após criar os diretórios, execute `chmod 755` neles para que todos os usuários possam acessar as páginas man; dependendo do umask padrão, diretórios novos podem ficar 750 e só root conseguir percorrê-los. Após copiar, execute `chmod 644` nos arquivos instalados para que todos possam ler as páginas (arquivos copiados podem ficar 640).

```bash
sudo mkdir -p /usr/local/share/man/man1/
sudo mkdir -p /usr/local/share/man/man5/
sudo chmod 755 /usr/local/share/man/man1/ /usr/local/share/man/man5/
sudo cp docs/data_boar.1 /usr/local/share/man/man1/
sudo cp docs/data_boar.5 /usr/local/share/man/man5/
sudo chmod 644 /usr/local/share/man/man1/data_boar.1 /usr/local/share/man/man5/data_boar.5
# Opcional: symlink de compatibilidade para quem ainda invoca `lgpd_crawler`
sudo ln -sf data_boar.1 /usr/local/share/man/man1/lgpd_crawler.1
sudo ln -sf data_boar.5 /usr/local/share/man/man5/lgpd_crawler.5
sudo mandb    # or: sudo makewhatis   # depends on distro
```

Depois da instalação, `man data_boar` e `man 5 data_boar` mostram o comando e os formatos de config. Com os symlinks de compatibilidade, `man lgpd_crawler` e `man 5 lgpd_crawler` mostram as mesmas páginas (apelido de comando legado).

```bash
man data_boar        # comando e opções (seção 1)
man 5 data_boar      # config e formatos de arquivo (seção 5)
```

Ao adicionar novas opções de CLI ou capacidades da API, atualize [data_boar.1](data_boar.1); ao adicionar ou alterar chaves de config ou formatos de arquivo de padrões, atualize [data_boar.5](data_boar.5) e o [README](../README.md) raiz. Para **alterações de versão** (convenção major.minor.build e onde atualizar o número de versão), veja [VERSIONING.md](VERSIONING.md).

## Implantar com Docker

Você pode executar a API como **um único container** (`docker run`), com **Docker Compose**, **Docker Swarm** ou **Kubernetes**. Você pode **puxar a imagem pré-construída** do Docker Hub ou **construir a partir do código** após clonar o repositório.

### Imagem pré-construída (Docker Hub)

Imagens Docker estão disponíveis no **Docker Hub** para você executar a aplicação sem clonar o repositório:

- **Docker Hub:** [hub.docker.com/r/fabioleitao/data_boar](https://hub.docker.com/r/fabioleitao/data_boar) — `fabioleitao/data_boar:latest` e `fabioleitao/data_boar:1.7.1`

A imagem inclui detecção de sensibilidade por regex + ML + DL opcional; você pode definir termos de treinamento ML/DL na config (veja [SENSITIVITY_DETECTION.md](SENSITIVITY_DETECTION.md) e [deploy/config.example.yaml](../deploy/config.example.yaml)).

Exemplo: executar a API web com um diretório de config local:

```bash
docker pull fabioleitao/data_boar:latest
docker run -d -p 8088:8088 -v /path/to/your/data:/data -e CONFIG_PATH=/data/config.yaml fabioleitao/data_boar:latest
```

Prepare `/data/config.yaml` a partir de `deploy/config.example.yaml` (veja [deploy/DEPLOY.md](deploy/DEPLOY.md) ([pt-BR](deploy/DEPLOY.pt_BR.md))). Você pode optar por usar esta imagem como container instanciado em vez de puxar o código do Git e construir localmente.

### Construir a partir do código

- **Build:** `docker build -t data_boar:latest .` (ou `docker build -t fabioleitao/data_boar:latest .` para push no Docker Hub; veja [deploy/DEPLOY.md](deploy/DEPLOY.md)).
- **Run:** Monte a config em `/data/config.yaml` (veja `deploy/config.example.yaml`). Exponha a porta 8088.
- **Compose:** `docker compose -f deploy/docker-compose.yml -f deploy/docker-compose.override.yml up -d` (prepare `./data/config.yaml` antes).
- **Swarm:** `docker stack deploy -c deploy/docker-compose.yml -c deploy/docker-compose.override.yml lgpd-audit`.
- **Kubernetes:** `kubectl apply -f deploy/kubernetes/` (veja [deploy/kubernetes/README.md](deploy/kubernetes/README.md)).

Passos completos (build, push, container único, Compose, Swarm, Kubernetes): **[deploy/DEPLOY.md](deploy/DEPLOY.md)** ([pt-BR](deploy/DEPLOY.pt_BR.md)). Para MCP, construa e faça push a partir do código: [DOCKER_SETUP.md](DOCKER_SETUP.md) ([pt-BR](DOCKER_SETUP.pt_BR.md)).

## Frameworks de conformidade e extensibilidade

A aplicação referencia explicitamente **LGPD**, **GDPR**, **CCPA**, **HIPAA** e **GLBA** em padrões embutidos e rótulos de relatório. Oferecemos **exemplos de configuração** (ex. [regex_overrides.example.yaml](regex_overrides.example.yaml), overrides de recomendação no [USAGE.pt_BR.md](USAGE.pt_BR.md)) para estender a **UK GDPR**, **PIPEDA**, **POPIA**, **APPI**, **PCI-DSS** ou normas customizadas sem alterar código: defina **`norm_tag`** em [regex overrides](SENSITIVITY_DETECTION.pt_BR.md) ou conectores customizados para qualquer rótulo de framework e use **`report.recommendation_overrides`** na config para personalizar o texto de recomendação. Podemos **ajudar com ajuste fino** (configs sob medida ou pequenas alterações no código) para maior compatibilidade quando você entrar em contato. Veja **[COMPLIANCE_FRAMEWORKS.pt_BR.md](COMPLIANCE_FRAMEWORKS.pt_BR.md)** ([EN](COMPLIANCE_FRAMEWORKS.md)) para a lista de regulamentações suportadas, arquivos de exemplo e extensibilidade.

## Segurança e conformidade

- Nenhum conteúdo amostrado bruto é persistido; apenas metadados (localização, padrão, sensibilidade, norm tag).
- A API web adiciona cabeçalhos de segurança por padrão (X-Content-Type-Options, X-Frame-Options, Content-Security-Policy, Referrer-Policy, Permissions-Policy e HSTS quando servido via HTTPS). Veja [SECURITY.md](../SECURITY.md).
- Use versões recentes e com CVE corrigidas do interpretador e das dependências (`uv sync` / `pip install -e .`).
- Mantenha credenciais em arquivos de config ou em variáveis de ambiente; evite commitar segredos.
- **Atrás de proxy reverso (nginx, Traefik, Caddy):** Defina `X-Forwarded-Proto: https` para tráfego com TLS encerrado para que HSTS e detecção de esquema funcionem corretamente.
- **Reportar vulnerabilidades:** Veja [SECURITY.md](../SECURITY.md). **Testes:** Veja [TESTING.md](TESTING.md). **Contribuindo:** Veja [CONTRIBUTING.md](../CONTRIBUTING.md).

## Documentação (veja também)

**Índice completo (todos os tópicos, EN e pt-BR):** [README.md](README.md) · [README.pt_BR.md](README.pt_BR.md). **Introdução na raiz:** [../README.md](../README.md) · [../README.pt_BR.md](../README.pt_BR.md). **Configuração e uso da API:** [USAGE.md](USAGE.md) · [USAGE.pt_BR.md](USAGE.pt_BR.md). **Sensibilidade (ML/DL):** [SENSITIVITY_DETECTION.md](SENSITIVITY_DETECTION.md) · [SENSITIVITY_DETECTION.pt_BR.md](SENSITIVITY_DETECTION.pt_BR.md). **Deploy:** [deploy/DEPLOY.md](deploy/DEPLOY.md) · [deploy/DEPLOY.pt_BR.md](deploy/DEPLOY.pt_BR.md). **Conectores:** [ADDING_CONNECTORS.md](ADDING_CONNECTORS.md) · [ADDING_CONNECTORS.pt_BR.md](ADDING_CONNECTORS.pt_BR.md). **Conformidade:** [COMPLIANCE_FRAMEWORKS.md](COMPLIANCE_FRAMEWORKS.md) · [COMPLIANCE_FRAMEWORKS.pt_BR.md](COMPLIANCE_FRAMEWORKS.pt_BR.md). **Testes, segurança, contribuição:** [TESTING.md](TESTING.md) · [TESTING.pt_BR.md](TESTING.pt_BR.md), [SECURITY.md](../SECURITY.md) · [SECURITY.pt_BR.md](../SECURITY.pt_BR.md), [CONTRIBUTING.md](../CONTRIBUTING.md) · [CONTRIBUTING.pt_BR.md](../CONTRIBUTING.pt_BR.md). **Direitos autorais/marca:** [COPYRIGHT_AND_TRADEMARK.md](COPYRIGHT_AND_TRADEMARK.md) · [COPYRIGHT_AND_TRADEMARK.pt_BR.md](COPYRIGHT_AND_TRADEMARK.pt_BR.md).

## Licença e direitos autorais

Veja [LICENSE](../LICENSE). Aviso de projeto e direitos autorais: [NOTICE](../NOTICE). Para formalizar direitos autorais e marca (registro, registradores): [COPYRIGHT_AND_TRADEMARK.md](COPYRIGHT_AND_TRADEMARK.md) ([pt-BR](COPYRIGHT_AND_TRADEMARK.pt_BR.md)).
