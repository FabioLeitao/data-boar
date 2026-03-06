# Política de segurança

**English:** [SECURITY.md](SECURITY.md)

Este documento descreve quais versões da aplicação são suportadas, qual linha de base de dependências é esperada e como reportar vulnerabilidades de segurança aos mantenedores.

## Versões suportadas

- **Aplicação:** `python3-lgpd-crawler` — o desenvolvimento atual tem como alvo **Python 3.12+**.
- Objetivamos suportar as últimas versões estáveis minor do Python 3.12 e 3.13 em Linux, macOS e Windows.
- Versões antigas do Python (< 3.12) não são testadas e devem ser consideradas não suportadas.

## Dependências e ambiente

As dependências são declaradas em **`pyproject.toml`** e gerenciadas principalmente via **uv**:

- Para instalar em um ambiente limpo:

  ```bash
  uv sync
  ```

- Para gerar um `requirements.txt` bloqueado para ambientes legados que usam pip puro:

  ```bash
  uv pip compile pyproject.toml -o requirements.txt
  ```

### Pré-requisitos de runtime (exemplo Linux)

No Ubuntu/Debian você deve ter pelo menos:

```bash
sudo apt update
sudo apt install -y \
  python3.12 python3.12-venv python3.12-dev build-essential \
  libpq-dev libssl-dev libffi-dev unixodbc-dev
```

Bibliotecas cliente adicionais podem ser necessárias dependendo de quais conectores você usa (ex.: Oracle, SQL Server, Snowflake); veja o `README.md` principal para notas específicas por conector.

## Manter as dependências atualizadas

- As dependências em **`pyproject.toml`** usam versões mínimas (`>=`) para permitir correções de segurança; o **Dependabot** (veja `.github/dependabot.yml`) abre PRs semanais para pip e GitHub Actions. Prefira fazer merge desses PRs após o CI (testes e auditoria) passar.

- Localmente, instale e execute uma auditoria de dependências:

  ```bash
  uv sync
  uv pip install pip-audit
  uv run pip-audit
  ```

  O CI executa a mesma auditoria em todo push/PR.

- Ao alterar dependências em `pyproject.toml`, regenere o `requirements.txt` usando o comando acima para que ambos os arquivos permaneçam em sincronia.

## Resistência a vulnerabilidades comuns

- **Injeção SQL:** Nomes de tabelas e colunas usados em SQL dinâmico (conectores) vêm do inspetor do banco (discover), não de entrada do usuário. Identificadores são escapados por dialeto: aspas duplas para SQLite/Postgres/Oracle (`"` → `""`), backtick para MySQL (`` ` `` → ` `` `). O banco de auditoria local (SQLite) usa apenas ORM do SQLAlchemy e consultas parametrizadas; `session_id` e outros valores fornecidos pelo usuário nunca são concatenados em SQL bruto. Veja **`tests/test_security.py`** para testes de regressão.
- **Path traversal:** O `session_id` nos caminhos da API é validado com um padrão estrito (alfanumérico e sublinhado, 12–64 caracteres) antes do uso em caminhos de arquivo ou buscas; valores inválidos retornam HTTP 400. Veja **`api/routes.py`** `_validate_session_id` e **`tests/test_routes_responses.py`**.
- **Config e serialização:** O config YAML é carregado com `yaml.safe_load` (sem deserialização de objetos Python arbitrários). Veja **`tests/test_security.py`** para um teste que rejeita tags YAML inseguras.

## Cabeçalhos HTTP de segurança (web e API)

A aplicação adiciona os seguintes cabeçalhos a todas as respostas web e da API por padrão:

- **X-Content-Type-Options: nosniff** — evita detecção de tipo MIME.
- **X-Frame-Options: DENY** — evita que o app seja incorporado em frames (mitigação de clickjacking).
- **Content-Security-Policy** — restringe origens de script, estilo e recursos ao app e ao CDN do Chart.js; permite scripts/estilos inline exigidos pelo dashboard atual.
- **Referrer-Policy: strict-origin-when-cross-origin** — limita informações de referrer enviadas em requisições cross-origin.
- **Permissions-Policy** — desabilita recursos do navegador não usados pelo app (câmera, microfone, geolocalização, etc.).
- **Strict-Transport-Security (HSTS)** — definido apenas quando a requisição é considerada HTTPS (direta ou via `X-Forwarded-Proto: https` de um proxy confiável), para que implantações somente HTTP não fiquem bloqueadas. Quando presente, usa `max-age=31536000; includeSubDomains; preload`.

Quando o app estiver atrás de um proxy reverso (ex.: nginx, Caddy, load balancer), garanta que o proxy defina **X-Forwarded-Proto: https** para requisições com TLS terminado para que o HSTS seja aplicado corretamente. Não habilite HSTS na camada do app para HTTP puro; o proxy pode adicionar HSTS ao servir via HTTPS.

## Chave de API opcional (empresarial)

A API não implementa autenticação por padrão; proteja o app no proxy reverso ou no nível de rede quando exposto. Para empresas que desejam um gate de segredo compartilhado simples sem alterar o modelo “proteger no proxy”, a aplicação suporta uma **chave de API opcional**:

- No config, defina `api.require_api_key: true` e `api.api_key` (literal) ou `api.api_key_from_env: "VAR"` (lê a chave do ambiente). Quando habilitado, toda requisição exceto **GET /health** deve incluir o cabeçalho **X-API-Key** ou **Authorization: Bearer &lt;chave&gt;**; caso contrário a API retorna **401**. O endpoint **/health** nunca é protegido para que load balancers e orquestradores ainda recebam 200.
- **Boa prática:** Use uma chave forte e aleatória e armazene-a em uma variável de ambiente (ex.: `api_key_from_env: "AUDIT_API_KEY"`). Não registre em log nem faça commit da chave no controle de versão. Isso é apenas um gate simples; para autenticação e autorização completas, use o proxy reverso ou um provedor de identidade.

## Endurecimento de implantação e proxy reverso

Os cabeçalhos de segurança (incluindo CSP) são implementados em **`api/routes.py`** (middleware aplicado às respostas web e da API). Para endurecer implantações em container e cluster:

- **Docker e Kubernetes:** Veja **`docs/deploy/DEPLOY.md`** ([pt-BR](docs/deploy/DEPLOY.pt_BR.md)), seção **“Security and hardening (optional)”**, para:
  - Executar como não-root, limites de recursos e healthchecks.
  - Exemplos opcionais Kubernetes: **securityContext** (runAsNonRoot, readOnlyRootFilesystem, drop capabilities), **NetworkPolicy** (`deploy/kubernetes/network-policy.example.yaml`) e **PodDisruptionBudget** (`deploy/kubernetes/pdb.example.yaml`).

Quando a API ou o dashboard for **exposto à internet ou a redes não confiáveis**, execute-o atrás de um **proxy reverso** com **TLS**, **autenticação/autorização** adequadas e considere um **WAF** (web application firewall). A chave de API e o rate limiting do app (veja [docs/USAGE.md](docs/USAGE.md) ([pt-BR](docs/USAGE.pt_BR.md))) complementam, mas não substituem, a segurança no nível do proxy.

## Reportar uma vulnerabilidade

Se você acredita ter encontrado uma vulnerabilidade de segurança neste projeto:

1. **Não abra uma issue pública com detalhes de exploração.**
1. Em vez disso:
   - Abra uma nova issue na aba **Issues** com uma descrição curta e em alto nível (sem dados sensíveis de PoC), **ou**
   - Se os security advisories do GitHub ou o reporte privado estiver disponível para este repositório, prefira esse canal.
1. Inclua pelo menos:
   - Versão/commit do projeto que você está usando.
   - Versão do Python e detalhes do SO.
   - Uma descrição mínima do impacto (ex.: divulgação de informação, escalação de privilégio, DoS).
1. Os mantenedores irão:
   - Confirmar o recebimento o mais rápido possível.
   - Investigar e, se confirmado, trabalhar em uma correção e coordenar a divulgação.

Se não tiver certeza se algo é sensível do ponto de vista de segurança, prefira o canal privado (ou uma issue pública mínima) para que possamos triar com segurança.
