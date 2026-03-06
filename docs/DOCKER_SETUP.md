# Docker Setup: MCP, Build, Push, Deploy

**Português (Brasil):** [DOCKER_SETUP.pt_BR.md](DOCKER_SETUP.pt_BR.md)

Run these steps in a terminal where **Docker** is available (e.g. PowerShell or CMD after starting Docker Desktop).

**Pre-built image:** The application is published on Docker Hub as `fabioleitao/python3-lgpd-crawler:latest` ([hub.docker.com/r/fabioleitao/python3-lgpd-crawler](https://hub.docker.com/r/fabioleitao/python3-lgpd-crawler)). You can `docker pull` and run that image instead of building from source (see [README](../README.md) and [deploy/DEPLOY.md](deploy/DEPLOY.md) ([pt-BR](deploy/DEPLOY.pt_BR.md))). The image includes the latest features (hybrid regex + ML + optional DL sensitivity detection; configurable ML/DL training terms via `ml_patterns_file`, `dl_patterns_file`, or `sensitivity_detection` in config — see [sensitivity-detection.md](sensitivity-detection.md)).

**Upgrading your local image:** To refresh Docker Desktop with the current version from the repository, pull the image and restart your container(s):

```powershell
docker pull fabioleitao/python3-lgpd-crawler:latest
# If you run a single container:
docker stop lgpd-audit
docker rm lgpd-audit
docker run -d --name lgpd-audit -p 8088:8088 -v "${PWD}/data:/data" -e CONFIG_PATH=/data/config.yaml fabioleitao/python3-lgpd-crawler:latest

# If you use Compose:
docker compose -f deploy/docker-compose.yml -f deploy/docker-compose.override.yml pull
docker compose -f deploy/docker-compose.yml -f deploy/docker-compose.override.yml up -d
```

Repeat this whenever you want to pick up a new version pushed to Docker Hub (e.g. after releases or updates to the repo).

---

## 1. Connect Cursor to Docker Desktop MCP

### Option A – Docker Desktop built-in MCP (if available)

1. Open **Docker Desktop** → **Settings** → **Features in development** (or **Beta**).
1. Enable **MCP** / **MCP Toolkit** if present.
1. Note the MCP endpoint (e.g. `npipe://...` on Windows).
1. In **Cursor** → **Settings** → **MCP** → **Add server**:
   - Name: `docker`
   - Command / URL: use the endpoint from Docker Desktop (or `docker-mcp` if it provides a CLI).

### Option B – Cursor MCP installer

```powershell
npm install -g @cursor/mcp-installer
cursor-mcp init
cursor-mcp install docker
cursor-mcp list
```

Then add the Docker MCP server in Cursor Settings → MCP using the path shown by `cursor-mcp list`.

### Option C – Manual Docker MCP

If you use a community Docker MCP (e.g. `cursor-docker-mcp`), add it in Cursor Settings → MCP with the server's command/args.

---

## 2. Build the image (web API mode)

The Dockerfile uses a multi-stage build (minimal runtime image; build tools only in the builder stage). From the **project root**:

```powershell
cd c:\Users\<username>\Documents\dev\python3-lgpd-crawler

docker build -t python3-lgpd-crawler:latest .
```

Default: web API + frontend. CLI remains available via `--entrypoint` override (see [deploy/DEPLOY.md](deploy/DEPLOY.md) ([pt-BR](deploy/DEPLOY.pt_BR.md))).

---

## 3. Tag and push to Docker Hub (fabioleitao)

Use your Docker Hub credentials (username `fabioleitao` and password or Access Token).

```powershell
# Tag for Docker Hub
docker tag python3-lgpd-crawler:latest fabioleitao/python3-lgpd-crawler:latest

# Log in (use your Docker Hub username and Access Token as password)
docker login
# Username: fabioleitao
# Password: <your password or Access Token>

# Push
docker push fabioleitao/python3-lgpd-crawler:latest
```

Optional: push a version tag (e.g. 1.0.9):

```powershell
docker tag python3-lgpd-crawler:latest fabioleitao/python3-lgpd-crawler:1.0.9
docker push fabioleitao/python3-lgpd-crawler:1.0.9
```

Non-interactive login with token:

```powershell
echo YOUR_ACCESS_TOKEN | docker login -u fabioleitao --password-stdin
docker push fabioleitao/python3-lgpd-crawler:latest
```

---

## 4. Deploy a local container (web API)

Config is in `data/config.yaml`. Run:

```powershell
cd c:\Users\<username>\Documents\dev\python3-lgpd-crawler

docker run -d --name lgpd-audit `
  -p 8088:8088 `
  -v "${PWD}/data:/data" `
  -e CONFIG_PATH=/data/config.yaml `
  python3-lgpd-crawler:latest
```

Or with **Docker Compose** (alternative to single-container run):

```powershell
copy deploy\docker-compose.override.example.yml deploy\docker-compose.override.yml
docker compose -f deploy/docker-compose.yml -f deploy/docker-compose.override.yml up -d
```

(Ensure `./data/config.yaml` exists; the override mounts `./data` at `/data`.) For **Docker Swarm** or **Kubernetes**, see [deploy/DEPLOY.md](deploy/DEPLOY.md) ([pt-BR](deploy/DEPLOY.pt_BR.md)).

---

## 5. Access

- **Dashboard:** <http://localhost:8088/>
- **API docs:** <http://localhost:8088/docs>
- **Health:** <http://localhost:8088/health>

---

## 6. Stop and remove

```powershell
docker stop lgpd-audit
docker rm lgpd-audit
```

Or with Compose: `docker compose -f deploy/docker-compose.yml -f deploy/docker-compose.override.yml down`
