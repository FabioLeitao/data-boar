# Como usar o Data Boar (aplicação de auditoria LGPD) — pt-BR

**Data Boar** é o nome da aplicação (baseado na tecnologia lgpd_crawler; id de pacote/distribuição: `python3-lgpd-crawler`). Este documento complementa o `docs/USAGE.md` em inglês e descreve, em português, como:

- Executar a aplicação via **CLI** e **API web**;
- Entender os parâmetros (`--config`, `--web`, `--port`, `--host`, `--tenant`, `--technician`, `--scan-compressed`, `--content-type-check`);
- Navegar pelo **dashboard web**;
- Iniciar varreduras e baixar relatórios/heatmaps usando **curl**.

**English:** [USAGE.md](USAGE.md)

> **Importante:** sempre que `docs/USAGE.md` for atualizado, mantenha este arquivo sincronizado (mesmas rotas, parâmetros e exemplos, traduzidos).

---

## 1. Interface de linha de comando (CLI)

O ponto de entrada é `main.py`.

### Argumentos

| Argumento              | Padrão        | Descrição                                                                                                                                                                                              |
| ---                    | ---           | ---                                                                                                                                                                                                    |
| `--config`             | `config.yaml` | Caminho do arquivo de configuração (YAML ou JSON). Usado em varredura única e para resolver `api.port` / `api.host` ao subir a API.                                                                    |
| `--web`                | *(flag)*      | Inicia o servidor FastAPI em vez de executar uma varredura única.                                                                                                                                      |
| `--port`               | `8088`        | Porta da API quando `--web` é usado. Pode ser sobrescrita por `api.port` no config, salvo se você passar `--port` explicitamente. Ignorado em modo varredura única.                                    |
| `--host`               | *(resolvido)* | Endereço de bind quando `--web` (ex.: `127.0.0.1`, `0.0.0.0`). **Prevalece** sobre `api.host` e `API_HOST`. Se omitido: `api.host` → `API_HOST` → padrão seguro **`127.0.0.1`**. Ver §2.               |
| `--reset-data`         | *(flag)*      | Operação de manutenção perigosa: apaga todas as sessões/achados/falhas do SQLite, remove relatórios/heatmaps em `report.output_dir` e registra o wipe na tabela `data_wipe_log`. Não inicia varredura. |
| `--export-audit-trail` | *(caminho opcional)* | Exporta trilha de auditoria em JSON a partir do SQLite (`data_wipe_log`, resumo de sessões; futuro: integridade). Sem caminho ou com `-` → **stdout**; caso contrário grava no arquivo. **Não** altera o banco. Incompatível com `--web` e `--reset-data`. |
| `--tenant`             | *(vazio)*     | Nome do cliente/tenant na execução CLI; gravado na sessão e exibido em dashboard/relatórios.                                                                                                           |
| `--technician`         | *(vazio)*     | Nome do técnico/operador na execução CLI; também gravado na sessão e relatórios.                                                                                                                       |
| `--scan-compressed`    | *(flag)*      | Sobrescrita pontual: ativa varredura dentro de arquivos compactados como se `file_scan.scan_compressed` estivesse true.                                                                                |
| `--content-type-check` | *(flag)*      | Sobrescrita pontual: inferência por magic bytes como se `file_scan.use_content_type` estivesse true (arquivos renomeados/ocultos).                                                                     |

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
- O relatório também inclui a aba **Data source inventory** com metadados best-effort das fontes (alvo, tipo, produto/versão, dica de versão de API/protocolo, dica de transporte e detalhes brutos).
- Imprime linhas `INFO` de confiança do runtime (stdout + stderr); em estado inesperado, alerta explícito: **THERE IS SOMETHING DIFFERENT AND UNEXPECTED IN THIS RUNTIME**.
- No console, você verá algo como:
- `Scan session: <session_id>`
- `Report written: <caminho_do_relatorio>`

#### Servidor API (`--web`)

```bash
python main.py --config config.yaml --web --port 8088
# Escutar em todas as interfaces (sobrescreve config / API_HOST; use só com controles de rede):
python main.py --config config.yaml --web --host 0.0.0.0 --port 8088
```

- Inicia o FastAPI em **`<bind>:<port>`**. O bind padrão é **`127.0.0.1`**, salvo `api.host`, `API_HOST` ou **`--host`** (a CLI ganha). A imagem Docker oficial define `API_HOST=0.0.0.0` para a porta publicada funcionar de fora do container.
- Nenhuma varredura é executada automaticamente; você controla tudo via HTTP (dashboard ou curl).
- Configuração para a API:
- Se `--config` não for usado, a API lê de `CONFIG_PATH` ou `config.yaml` no diretório atual.

---

## 2. API web e dashboard

## Opção: executar via Docker (sem clonar o Git)

Imagens pré-construídas estão no Docker Hub: `fabioleitao/data_boar:latest` ([hub.docker.com/r/fabioleitao/data_boar](https://hub.docker.com/r/fabioleitao/data_boar)). Faça pull e execute com um config montado em `/data/config.yaml` (veja o README “Deploy com Docker” e [docs/deploy/DEPLOY.pt_BR.md](deploy/DEPLOY.pt_BR.md) ([EN](deploy/DEPLOY.md))). Você pode usar esse container em vez de instalar a partir do código.

### URLs principais

- **Dashboard:** `http://<host>:<port>/`
- **Reports:** `http://<host>:<port>/reports`
- **Configuration:** `http://<host>:<port>/config`
- **Help:** `http://<host>:<port>/help` — início rápido, exemplos de config, detecção de sensibilidade e `recommendation_overrides`, links para README e USAGE (EN/pt-BR)
- **About:** `http://<host>:<port>/about` — aplicação, versão, autor e licença (conforme LICENSE)
- **Swagger UI:** `http://<host>:<port>/docs` — documentação interativa da API (OpenAPI)
- **Health:** `http://<host>:<port>/health` — sonda de liveness/readiness para Docker/Kubernetes (sempre público mesmo com API key exigida)

### O que o dashboard mostra

- Estado da varredura (`Running`/`Idle`), ID da sessão atual, contagem de achados.
- Estatísticas da última execução (achados em bancos, filesystem, falhas, total).
- Gráfico **“Progress over time”** com total de achados e score de risco (0–100) por sessão.
- Campos de entrada para **cliente/tenant** e **técnico/operador**, usados ao clicar em “Start scan”.
- Tabela de sessões recentes com:
- ID, data de início, tenant, técnico, achados DB/FS, falhas e link “Download” (gera o Excel dessa sessão).

### Rotas de API (resumo)

| Método  | Endpoint                            | Finalidade                                                                                              |
| ---     | ---                                 | ---                                                                                                     |
| `POST`  | `/scan` ou `/start`                 | Inicia uma varredura completa em background; retorna `session_id`. Aceita `{ "tenant", "technician" }`. |
| `POST`  | `/scan_database`                    | Inicia varredura pontual de um único banco (body JSON). Pode incluir `tenant` e `technician`.           |
| `GET`   | `/status`                           | Retorna `running`, `current_session_id`, `findings_count`.                                              |
| `GET`   | `/report`                           | Baixa o último relatório Excel gerado (ou gera a partir da sessão mais recente).                        |
| `GET`   | `/heatmap`                          | Baixa o último heatmap PNG gerado (sessão mais recente).                                                |
| `GET`   | `/logs`                             | Baixa o arquivo de log mais recente (`audit_YYYYMMDD.log`) com registros de conexões e achados.         |
| `GET`   | `/list` ou `/reports`               | Lista sessões anteriores com data, status, contagens, `tenant_name` e `technician_name` (se definidos). |
| `GET`   | `/reports/{session_id}`             | Gera (se necessário) e baixa o relatório Excel para a sessão indicada.                                  |
| `GET`   | `/heatmap/{session_id}`             | Gera (se necessário) e baixa o heatmap PNG para a sessão indicada.                                      |
| `GET`   | `/logs/{session_id}`                | Baixa o primeiro arquivo de log que contiver o `session_id` informado (análise detalhada da sessão).    |
| `PATCH` | `/sessions/{session_id}`            | Atualiza/limpa o tenant de uma sessão existente (`{ "tenant": "..." }`).                                |
| `PATCH` | `/sessions/{session_id}/technician` | Atualiza/limpa o técnico de uma sessão existente (`{ "technician": "..." }`).                           |
| `GET`   | `/about`                            | Página About (HTML): aplicação, versão, autor, licença.                                                 |
| `GET`   | `/about/json`                       | Informações de about em JSON (nome, versão, autor, licença, copyright).                                 |
| `GET`   | `/health`                           | Sonda de liveness/readiness para Docker e Kubernetes.                                                   |

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
- `targets` – alvos a escanear (bancos, diretórios, APIs, compartilhamentos). Não há limite rígido de alvos por varredura; listas muito grandes (ex.: centenas de bancos ou APIs) podem aumentar tempo e uso de memória—considere um escopo razoável por varredura.
- `file_scan` – extensões, recursividade, `scan_sqlite_as_db`, `sample_limit` (estilo linhas/TOPN), `file_sample_max_chars` (orçamento de caracteres para `.txt`/`.md` em FS/shares), opcionalmente `scan_compressed` (varrer dentro de arquivos compactados, ex.: zip, tar, 7z — desligado por padrão), limites de tamanho (`max_inner_size`, faixa válida 1 MB–500 MB; padrão 10 MB) e `compressed_extensions`, e `file_passwords` (senhas para PDFs e documentos ZIP protegidos por senha; ver [USAGE.md](USAGE.md), seção Global options, para exemplo YAML e limitações). Para suporte a .7z instale o extra opcional: `pip install -e ".[compressed]"`.
- **Aviso (scan_compressed):** Habilitar `scan_compressed: true` pode **aumentar bastante** o tempo de execução, I/O em disco e uso de espaço temporário. Use só quando precisar inspecionar o interior de arquivos compactados; na primeira vez, prefira um escopo menor (ex.: um diretório ou poucos caminhos).
- **`use_content_type` (opt-in):** Quando `true`, o scanner usa um helper de **magic bytes** para inferir o formato real do **arquivo** (ex.: PDF renomeado como `.txt`, ou imagem/áudio/vídeo com extensão errada) em filesystem e **compartilhamentos** (SMB/WebDAV/SharePoint). Aumenta I/O e CPU por **arquivo**; o padrão é só por extensão. **CLI:** `--content-type-check` força isso numa execução one-shot. **API/dashboard:** `content_type_check: true` no corpo de **`POST /scan`** ou a caixa no dashboard aplica só àquela varredura; o `config.yaml` gravado não é alterado. Detalhes e exemplos YAML: [USAGE.md](USAGE.md) (seção Global options / file_scan).
- **Rich media (opt-in):** `file_scan.scan_rich_media_metadata: true` lê amostras limitadas de metadados: EXIF de imagens (Pillow), tags de áudio (**mutagen** — `uv pip install -e ".[richmedia]"`) e tags de vídeo com **ffprobe** (binário no `PATH`). `file_scan.scan_image_ocr: true` aciona **Tesseract** numa miniatura limitada (`pytesseract` + pacote do sistema `tesseract-ocr`). **Privacidade:** OCR lê **pixels visíveis**; habilite só onde houver base legal e política clara. Padrão **false** para ambos. `ocr_lang` (padrão `eng`) e `ocr_max_dimension` (padrão 2000, entre 256 e 8000) ajustam o OCR.
- **Legendas (padrão):** `.srt`, `.vtt`, `.ass`, `.ssa` entram na lista padrão de extensões e são lidas como texto UTF-8 (normalização de tempos), sem flag extra.
- `report` – `output_dir` para relatórios/heatmaps; opcionalmente `recommendation_overrides` (lista de mapeamentos por `norm_tag` para Base legal, Risco, Recomendação, Prioridade, Relevante para). Exemplo completo em [USAGE.md](USAGE.md) (seção 4, Global options); exemplo para categorias sensíveis (saúde, religião, política, PEP, raça, sindicato, genético, biométrico, vida sexual) em [USAGE.md#recommendation_overrides](USAGE.md) e abaixo em pt-BR (ver também [PLAN_SENSITIVE_CATEGORIES_ML_DL.md](plans/completed/PLAN_SENSITIVE_CATEGORIES_ML_DL.md)).
- `api` – porta da API; opcionalmente `require_api_key`, `api_key` ou `api_key_from_env` para exigir chave de API (cabeçalho X-API-Key ou Authorization: Bearer); GET /health permanece público. **Em produção recomenda-se** `require_api_key: true` e chave forte via variável de ambiente (ex.: `api.api_key_from_env: "AUDIT_API_KEY"`) para não armazenar a chave no config. Ver [SECURITY.md](../SECURITY.md).
- Por padrão, quando você inicia a API via CLI (`python main.py --web ...`), o servidor web faz bind em **`127.0.0.1` (loopback)**. No container oficial (Docker image), ele define `API_HOST=0.0.0.0` para que a porta publicada funcione a partir de fora do Docker Desktop/WSL.

- Se você estiver atrás de proxy reverso ou com restrições de rede específicas, ainda pode sobrescrever com `api.host` no config (por exemplo, `0.0.0.0` / `127.0.0.1`) — mas mantenha o default seguro em `127.0.0.1` a menos que o runtime esteja explicitamente cercado por regras de rede/Ingress.
- `sqlite_path` – caminho do banco SQLite com resultados.
- `scan` – `max_workers` para paralelismo.
- `timeouts` – timeouts globais para conexões (ex.: `connect_seconds`, `read_seconds`); cada alvo pode sobrescrever com `connect_timeout`, `read_timeout` ou `timeout`. Ver abaixo.
- `api.workers` – número de workers uvicorn (padrão 1; 2+ para mais requisições concorrentes).
- Opcionais: `ml_patterns_file`, `dl_patterns_file`, `regex_overrides_file`, `sensitivity_detection` (termos ML/DL inline), `learned_patterns` (export de termos classificados), **`pattern_files_encoding`** (encoding dos arquivos de padrões; ver abaixo).
- **Pedindo acesso à TI:** Quando for preciso solicitar permissões à equipe de TI (ex.: pastas compartilhadas, contas de banco, tokens de API), solicite o **mínimo** necessário. Veja [OPERATOR_IT_REQUIREMENTS.pt_BR.md](ops/OPERATOR_IT_REQUIREMENTS.pt_BR.md) para o checklist por fonte (somente leitura, sem admin), o que não precisamos e uma breve justificativa, alinhada a zero-trust ou IAM restrito. ([EN](ops/OPERATOR_IT_REQUIREMENTS.md))

### Encoding de arquivos (config e arquivos de padrões) {#file-encoding-config-and-pattern-files}

Config e amostras de conformidade podem usar diferentes conjuntos de caracteres. A aplicação suporta isso para que termos multilíngues (ex.: japonês, árabe, francês) e ambientes legados não quebrem em produção.

- **Arquivo de config:** Lido com **auto-detecção**: UTF-8, UTF-8 com BOM, ANSI Windows (cp1252) e Latin-1 são tentados em ordem. Não é necessário definir encoding para o config principal.
- **Arquivos de padrões** (`regex_overrides_file`, `ml_patterns_file`, `dl_patterns_file`): Lidos com o encoding definido por **`pattern_files_encoding`** (padrão **`utf-8`**). Use quando seus YAML/JSON estiverem em outro encoding (ex.: `cp1252`, `latin_1`, `utf-8-sig`). Bytes inválidos são substituídos para que um caractere problemático não derrube a varredura.
- **Recomendação:** Salve todos os configs e amostras em **UTF-8** para melhor compatibilidade com conteúdo multilíngue (amostras para APAC, EMEA etc.). O relatório Excel e o heatmap suportam Unicode.

Exemplo no config:

```yaml
pattern_files_encoding: utf-8   # padrão; ou cp1252, latin_1, utf-8-sig para legado
regex_overrides_file: docs/compliance-samples/compliance-sample-uk_gdpr.yaml
ml_patterns_file: docs/compliance-samples/compliance-sample-pipeda.yaml
```

**Padrões regex customizados:** Para a aplicação se atentar a **novos valores possivelmente pessoais ou sensíveis** (ex.: RG, placa, número de plano de saúde), defina **`regex_overrides_file`** no config com o caminho de um arquivo YAML/JSON contendo uma lista de `{ name, pattern, norm_tag }`. O detector aplica cada padrão ao nome da coluna e ao texto amostrado; qualquer match é reportado com sensibilidade HIGH (ou MEDIUM em contexto de letras/cifras). Formato e exemplos (RG, placa, CEP, telefone EUA, etc.): [SENSITIVITY_DETECTION.pt_BR.md#padrões-regex-customizados-detectar-novos-dados-pessoaissensíveis](SENSITIVITY_DETECTION.pt_BR.md#padrões-regex-customizados-detectar-novos-dados-pessoaissensíveis) (pt-BR) · [SENSITIVITY_DETECTION.md#custom-regex-patterns-detecting-new-personalsensitive-values](SENSITIVITY_DETECTION.md#custom-regex-patterns-detecting-new-personalsensitive-values) (EN). Para **múltiplas regulamentações e exemplos de configuração** (embutidas: LGPD, GDPR, CCPA, HIPAA, GLBA; extensibilidade para UK GDPR, PIPEDA, POPIA, APPI, PCI-DSS ou custom) e ajuda com ajuste fino, veja [COMPLIANCE_FRAMEWORKS.pt_BR.md](COMPLIANCE_FRAMEWORKS.pt_BR.md) ([EN](COMPLIANCE_FRAMEWORKS.md)).

**Outras regulamentações e amostras de conformidade:** Amostras de config prontas para **UK GDPR**, **EU GDPR**, **Benelux**, **PIPEDA**, **POPIA**, **APPI**, **PCI-DSS** e outras regiões estão em [compliance-samples/](compliance-samples/). Defina `regex_overrides_file` e `ml_patterns_file` com o arquivo da amostra e mescle o `recommendation_overrides` da amostra em `report.recommendation_overrides`. Lista completa, o que vai onde e como usar: [COMPLIANCE_FRAMEWORKS.pt_BR.md – Amostras de conformidade](COMPLIANCE_FRAMEWORKS.pt_BR.md#amostras-de-conformidade) ([EN](COMPLIANCE_FRAMEWORKS.md#compliance-samples)).

**Exemplo `recommendation_overrides` para categorias sensíveis (LGPD Art. 5 II, 11; GDPR Art. 9):** Você pode adicionar entradas para que achados de saúde, religião, política, PEP, raça, sindicato, genético, biométrico e vida sexual tenham Base legal, Risco e Prioridade corretos na aba Recomendações. Exemplo (inglês): [USAGE.md](USAGE.md). Em pt-BR, use os mesmos `norm_tag_pattern` (ex.: `health`, `religious`, `political`, `PEP`, `race`, `union`, `genetic`, `biometric`, `sex life`) e preencha `base_legal`, `risk`, `recommendation`, `priority`, `relevant_for` conforme sua política. Ver [PLAN_SENSITIVE_CATEGORIES_ML_DL.md](plans/completed/PLAN_SENSITIVE_CATEGORIES_ML_DL.md) e [SENSITIVITY_DETECTION.pt_BR.md](SENSITIVITY_DETECTION.pt_BR.md).

### Rate limiting e segurança contra abuso

Para evitar DoS acidental ou abuso (muitas varreduras em sequência ou sessões demais em paralelo), use o bloco `rate_limit` no config:

```yaml
rate_limit:
  enabled: true               # quando presente, o padrão é true
  max_concurrent_scans: 1     # máximo de varreduras em execução ao mesmo tempo (API)
  min_interval_seconds: 0     # intervalo mínimo em segundos entre inícios de varredura
  grace_for_running_status: 0 # opcional; tolerância extra quando o status ainda mostra running
```

- Quando `rate_limit.enabled` for true, os endpoints de início de varredura (`POST /scan`, `POST /start`, `POST /scan_database`) podem responder **HTTP 429** com JSON:

  ```json
  {
    "detail": {
      "error": "rate_limited",
      "reason": "too_many_running_scans",
      "running_scans": 2,
      "max_concurrent_scans": 1,
      "source": "scan"
    }
  }
  ```

- A CLI usa a mesma lógica apenas para imprimir **avisos** (não muda o código de saída), de forma a manter scripts existentes funcionando enquanto você enxerga quando sua política bloquearia chamadas via API/dashboard.
- É possível sobrescrever os valores via variáveis de ambiente: `RATE_LIMIT_ENABLED`, `RATE_LIMIT_MAX_CONCURRENT_SCANS`, `RATE_LIMIT_MIN_INTERVAL_SECONDS`, `RATE_LIMIT_GRACE_FOR_RUNNING_STATUS`.
- **Produção:** O rate limiting é a primeira linha de defesa contra abuso e sobrecarga de varreduras. Desabilitar ou relaxar os limites (ex.: `max_concurrent_scans` alto ou `min_interval_seconds` zero) aumenta o risco de abuso e esgotamento de recursos; mantenha os limites ativos com valores conservadores em produção.

### Timeouts para conexões com fontes de dados

É possível configurar timeouts de conexão e de leitura (em segundos) usados ao abrir e ler bancos, APIs ou outros alvos. Os padrões globais valem para todos os alvos; cada alvo pode sobrescrevê-los.

```yaml
timeouts:
  connect_seconds: 25   # padrão 25 — tempo máximo para estabelecer conexão
  read_seconds: 90      # padrão 90 — tempo máximo de espera para leitura/resposta
```

- **Sobrescrita por alvo:** Em qualquer alvo você pode definir `connect_timeout`, `read_timeout` ou um único `timeout` (usado para connect e read quando o outro não for definido). Os valores do alvo sobrescrevem os timeouts globais quando presentes. Valores em segundos; mínimo 1.

Exemplo (padrões globais e um alvo mais lento):

```yaml
timeouts:
  connect_seconds: 25
  read_seconds: 90

targets:

- name: fast-db

    type: database
    # usa 25 / 90
- name: slow-api

    type: api
    connect_timeout: 60
    read_timeout: 120

- name: legacy

    type: database
    timeout: 45   # 45 para connect e read
```

Os conectores usam os valores mesclados (global ou por alvo) ao abrir conexões e fazer I/O; veja o esquema do config e a documentação dos conectores.

### Timeouts e carga

Recomendações para que as varreduras permaneçam estáveis sem sobrecarregar os alvos nem esperar indefinidamente:

1. **Não espere para sempre:** Defina timeouts de conexão e de leitura para que um alvo travado não bloqueie toda a varredura. Use as dicas de falha no relatório para identificar falhas por timeout e qual alvo falhou.
1. **Não seja agressivo demais:** Timeouts muito baixos geram falsos timeouts em redes ocupadas ou lentas (ex.: durante backup). Se aparecerem muitos timeouts, **aumente** `connect_seconds` e `read_seconds` (ou por alvo `connect_timeout` / `read_timeout`) e considere reexecutar em horário de menor uso.
1. **Evite DoS e “muito rápido demais”:** Use **rate_limit** (ex.: `max_concurrent_scans: 1`, `min_interval_seconds: 5`) e **scan.max_workers: 1** (ou 2) para que o scanner não abra muitas conexões ao mesmo tempo. Isso reduz carga nos alvos e evita amplificar lentidão ou causar DoS.
1. **Janelas de backup ou manutenção:** Se as varreduras rodarem durante backup ou manutenção, aumente os timeouts e mantenha o paralelismo baixo; ou agende varreduras fora dessas janelas.
1. **Sobrescrita por alvo:** Para um banco ou API lento, defina `connect_timeout` / `read_timeout` (ou `timeout`) nesse alvo em vez de aumentar os padrões globais para todos.

### API e segurança (CSP, cabeçalhos)

A API web e o dashboard enviam **cabeçalhos de segurança** em toda resposta (veja [SECURITY.md](../SECURITY.md)): X-Content-Type-Options, X-Frame-Options, **Content-Security-Policy (CSP)**, Referrer-Policy, Permissions-Policy e HSTS quando a requisição é considerada HTTPS.

- **CSP padrão:** Scripts e estilos são permitidos da origem da aplicação (`'self'`). O dashboard carrega o Chart.js do **CDN jsDelivr** (`<https://cdn.jsdelivr.ne>t`), permitido por padrão para o gráfico “Progress over time”. Uma quantidade mínima de script inline é usada para os dados do gráfico; o restante da lógica do dashboard fica em `/static/dashboard.js`.
- **CSP mais restrito:** Para remover `'unsafe-inline'` (ex.: perfil de alta segurança), você pode definir um CSP mais restrito no **proxy reverso** (sobrescrevendo o cabeçalho da aplicação) ou usar um toggle de env/config se a aplicação passar a oferecer um no futuro. Com CSP mais restrito, todo script e estilo deve vir de origens permitidas (`'self'` e o CDN); qualquer script inline restante nos templates precisaria ser refatorado para arquivos externos. Veja [SECURITY.md](../SECURITY.md) e [docs/deploy/DEPLOY.pt_BR.md](deploy/DEPLOY.pt_BR.md) ([EN](deploy/DEPLOY.md)) (Security and hardening) para endurecimento de implantação (Docker, Kubernetes, proxy reverso).

Para detalhes de todos os campos e exemplos completos, consulte `README.md` e `docs/USAGE.md` (inglês), que são as referências canônicas.

**Produção atrás de proxy reverso (nginx, Traefik, Caddy):** A aplicação se comporta corretamente atrás de NAT, load balancer ou proxy reverso. Quando o TLS for terminado no proxy, defina **X-Forwarded-Proto: https** para que os cabeçalhos de segurança (ex.: HSTS) funcionem. Veja [SECURITY.md](../SECURITY.md) para os cabeçalhos HTTP de segurança.

#### Formatos de CNPJ (legado numérico e alfanumérico)

Para o **CNPJ** brasileiro, o detector inclui dois padrões regex embutidos:

- `LGPD_CNPJ` – formato **legado, apenas numérico** (14 dígitos, pontuação opcional `./-/`: `XX.XXX.XXX/XXXX-XX`).
- `LGPD_CNPJ_ALNUM` – formato **alfanumérico** em que as 12 primeiras posições podem conter `A–Z` ou `0–9`, e as duas últimas posições permanecem dígitos (check digits); a pontuação é opcional nos mesmos lugares.

Ambos usam o mesmo `norm_tag` (`LGPD Art. 5`). Nesta etapa a detecção é apenas por **compatibilidade de formato** (sem validação de dígito verificador); veja [SENSITIVITY_DETECTION.pt_BR.md](SENSITIVITY_DETECTION.pt_BR.md#formatos-de-cnpj-brasil-numérico-legado-e-alfanumérico) para detalhes e para saber como estender/substituir padrões via `regex_overrides_file`.

### Notificações ao operador (opcional)

Após o fim da varredura (CLI ou `POST /scan` / `POST /start` em segundo plano), a aplicação pode enviar um **resumo curto em pt-BR** para **Slack**, **Microsoft Teams**, **Telegram** ou um **webhook JSON genérico**. O padrão é **desligado** (`notifications.enabled: false`).

- **Config:** bloco opcional `notifications` com `operator.slack_webhook_url`, `teams_webhook_url`, `telegram_bot_token` + `telegram_chat_id` ou `generic_webhook_url`. URLs podem usar `${VAR_DE_AMBIENTE}` para não commitar segredos. Os POSTs de webhook repetem algumas vezes em caso de HTTP 5xx ou erro de rede transitório.
- **Manual / CI:** `python scripts/notify_webhook.py "mensagem"` (mesmo `config.yaml`; exige `notifications.enabled: true` e um canal configurado).
- **Detalhes:** [PLAN_NOTIFICATIONS_OFFBAND_AND_SCAN_COMPLETE.md](plans/PLAN_NOTIFICATIONS_OFFBAND_AND_SCAN_COMPLETE.md).

**Documentação relacionada:** Índice completo da documentação (todos os tópicos, ambos os idiomas): [README.md](README.md) · [README.pt_BR.md](README.pt_BR.md). Guia técnico: [TECH_GUIDE.md](TECH_GUIDE.md) · [TECH_GUIDE.pt_BR.md](TECH_GUIDE.pt_BR.md). [SENSITIVITY_DETECTION.pt_BR.md](SENSITIVITY_DETECTION.pt_BR.md) (termos de treino ML/DL; [inglês](SENSITIVITY_DETECTION.md)). Para `recommendation_overrides` cobrindo categorias sensíveis (saúde, religião, política, PEP, raça, sindicato, genético, biométrico, vida sexual), veja o exemplo acima (Notas sobre configuração) e [PLAN_SENSITIVE_CATEGORIES_ML_DL.md](plans/completed/PLAN_SENSITIVE_CATEGORIES_ML_DL.md). Para adicionar um novo conector (banco, API, share), veja [ADDING_CONNECTORS.pt_BR.md](ADDING_CONNECTORS.pt_BR.md) ou [ADDING_CONNECTORS.md](ADDING_CONNECTORS.md) (inglês). Deploy: [deploy/DEPLOY.pt_BR.md](deploy/DEPLOY.pt_BR.md) · [deploy/DEPLOY.md](deploy/DEPLOY.md). Mais: [TESTING.pt_BR.md](TESTING.pt_BR.md) ([EN](TESTING.md)), [TOPOLOGY.pt_BR.md](TOPOLOGY.pt_BR.md) ([EN](TOPOLOGY.md)), [COMMIT_AND_PR.pt_BR.md](ops/COMMIT_AND_PR.pt_BR.md) ([EN](ops/COMMIT_AND_PR.md)), [COMPLIANCE_FRAMEWORKS.pt_BR.md](COMPLIANCE_FRAMEWORKS.pt_BR.md) ([EN](COMPLIANCE_FRAMEWORKS.md)). Em sistemas com `man`: `man data_boar` ou `man lgpd_crawler` (comando e API), e `man 5 data_boar` ou `man 5 lgpd_crawler` (config e formatos).
