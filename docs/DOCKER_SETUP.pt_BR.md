# Docker Setup: MCP, build, push e deploy

**English:** [DOCKER_SETUP.md](DOCKER_SETUP.md)

Execute estes passos em um terminal onde o **Docker** esteja disponível (ex.: PowerShell ou CMD após iniciar o Docker Desktop).

**Imagem pré-construída:** A aplicação é publicada no Docker Hub como `fabioleitao/data_boar:latest` ([hub.docker.com/r/fabioleitao/data_boar](https://hub.docker.com/r/fabioleitao/data_boar)). Você pode usar `docker pull` e executar essa imagem em vez de construir a partir do código (veja [README](../README.md) e [deploy/DEPLOY.md](deploy/DEPLOY.md) ([pt-BR](deploy/DEPLOY.pt_BR.md))). A imagem inclui as funcionalidades atuais (detecção de sensibilidade híbrida regex + ML + DL opcional; termos de treino ML/DL configuráveis via `ml_patterns_file`, `dl_patterns_file` ou `sensitivity_detection` no config — veja [SENSITIVITY_DETECTION.pt_BR.md](SENSITIVITY_DETECTION.pt_BR.md)).

**Atualizando sua imagem local:** Para atualizar o Docker Desktop com a versão atual do repositório, faça pull da imagem e reinicie o(s) container(es):

```powershell
docker pull fabioleitao/data_boar:latest
# Se você usa um único container
docker stop data-boar-audit
docker rm data-boar-audit
docker run -d --name data-boar-audit -p 8088:8088 -v "${PWD}/data:/data" -e CONFIG_PATH=/data/config.yaml fabioleitao/data_boar:latest

# Se usa Compose
docker compose -f deploy/docker-compose.yml -f deploy/docker-compose.override.yml pull
docker compose -f deploy/docker-compose.yml -f deploy/docker-compose.override.yml up -d
```

Repita sempre que quiser usar uma nova versão publicada no Docker Hub (ex.: após releases ou atualizações no repositório).

---

## 1. Conectar o Cursor ao Docker Desktop MCP

### Opção A – MCP integrado do Docker Desktop (se disponível)

1. Abra **Docker Desktop** → **Settings** → **Features in development** (ou **Beta**).
1. Ative **MCP** / **MCP Toolkit** se estiver presente.
1. Anote o endpoint MCP (ex.: `npipe://...` no Windows).
1. Em **Cursor** → **Settings** → **MCP** → **Add server**:
   - Name: `docker`
   - Command / URL: use o endpoint do Docker Desktop (ou `docker-mcp` se ele fornecer um CLI).

### Opção B – Instalador MCP do Cursor

```powershell
npm install -g @cursor/mcp-installer
cursor-mcp init
cursor-mcp install docker
cursor-mcp list
```

Depois adicione o servidor Docker MCP em Cursor Settings → MCP usando o caminho exibido por `cursor-mcp list`.

### Opção C – Docker MCP manual

Se você usa um MCP Docker da comunidade (ex.: `cursor-docker-mcp`), adicione-o em Cursor Settings → MCP com o command/args do servidor.

---

## 2. Construir a imagem (modo API web)

O Dockerfile usa build multi-stage (imagem de runtime mínima; ferramentas de build apenas no estágio de build). A partir da **raiz do projeto**:

```powershell
cd c:\Users\<username>\Documents\dev\python3-lgpd-crawler

docker build -t data_boar:latest .
```

Padrão: API web + frontend. O CLI continua disponível via override de `--entrypoint` (veja [deploy/DEPLOY.md](deploy/DEPLOY.md) ([pt-BR](deploy/DEPLOY.pt_BR.md))).

---

## 3. Tag e push para o Docker Hub (fabioleitao)

Use suas credenciais do Docker Hub (usuário `fabioleitao` e senha ou Access Token).

```powershell
# Tag para Docker Hub
docker tag data_boar:latest fabioleitao/data_boar:latest

# Login (use seu usuário Docker Hub e Access Token como senha)
docker login
# Username: fabioleitao
# Password: <sua senha ou Access Token>

# Push
docker push fabioleitao/data_boar:latest
```

Opcional: enviar uma tag de versão (ex.: 1.6.3):

```powershell
docker tag data_boar:latest fabioleitao/data_boar:1.6.3
docker push fabioleitao/data_boar:1.6.3
```

Login não interativo com token:

```powershell
echo YOUR_ACCESS_TOKEN | docker login -u fabioleitao --password-stdin
docker push fabioleitao/data_boar:latest
```

---

## 4. Implantar um container local (API web)

O config fica em `data/config.yaml`. Execute:

```powershell
cd c:\Users\<username>\Documents\dev\python3-lgpd-crawler

docker run -d --name data-boar-audit `
  -p 8088:8088 `
  -v "${PWD}/data:/data" `
  -e CONFIG_PATH=/data/config.yaml `
  data_boar:latest
```

Ou com **Docker Compose** (alternativa ao run com container único):

```powershell
copy deploy\docker-compose.override.example.yml deploy\docker-compose.override.yml
docker compose -f deploy/docker-compose.yml -f deploy/docker-compose.override.yml up -d
```

(Garanta que `./data/config.yaml` exista; o override monta `./data` em `/data`.) Para **Docker Swarm** ou **Kubernetes**, veja [deploy/DEPLOY.md](deploy/DEPLOY.md) ([pt-BR](deploy/DEPLOY.pt_BR.md)).

---

## 5. Acesso

- **Dashboard:** <http://localhost:8088/>
- **Documentação da API:** <http://localhost:8088/docs>
- **Health:** <http://localhost:8088/health>

---

## 6. Parar e remover

```powershell
docker stop data-boar-audit
docker rm data-boar-audit
```

Ou com Compose: `docker compose -f deploy/docker-compose.yml -f deploy/docker-compose.override.yml down`
