# Docker Setup: MCP, Build, Push, Deploy

Run these steps in a terminal where **Docker** is available (e.g. PowerShell or CMD after starting Docker Desktop).

**Pre-built image:** The application is also published on Docker Hub as `fabioleitao/python3-lgpd-crawler:latest` ([hub.docker.com/r/fabioleitao/python3-lgpd-crawler](https://hub.docker.com/r/fabioleitao/python3-lgpd-crawler)). You can `docker pull` and run that image instead of building from source (see README and `deploy/DEPLOY.md`).

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
2. Enable **MCP** / **MCP Toolkit** if present.
3. Note the MCP endpoint (e.g. `npipe://...` on Windows).
4. In **Cursor** → **Settings** → **MCP** → **Add server**:
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

If you use a community Docker MCP (e.g. `cursor-docker-mcp`), add it in Cursor Settings → MCP with the server’s command/args.

---

## 2. Build the image (web API mode)

The Dockerfile uses a multi-stage build (minimal runtime image; build tools only in the builder stage). From the **project root**:

```powershell
cd c:\Users\fabio\Documents\dev\python3-lgpd-crawler

docker build -t python3-lgpd-crawler:latest .
```

Default: web API + frontend. CLI remains available via `--entrypoint` override (see `deploy/DEPLOY.md`).

---

## 3. Tag and push to Docker Hub

Replace `YOUR_DOCKERHUB_USER` with your Docker Hub username.

```powershell
# Tag for Docker Hub
docker tag python3-lgpd-crawler:latest YOUR_DOCKERHUB_USER/python3-lgpd-crawler:latest

# Log in (use your Docker Hub username and Access Token as password)
docker login
# Username: YOUR_DOCKERHUB_USER
# Password: <paste your Access Token>

# Push
docker push YOUR_DOCKERHUB_USER/python3-lgpd-crawler:latest
```

Or non-interactive login with token:

```powershell
echo YOUR_ACCESS_TOKEN | docker login -u YOUR_DOCKERHUB_USER --password-stdin
docker push YOUR_DOCKERHUB_USER/python3-lgpd-crawler:latest
```

---

## 4. Deploy a local container (web API)

Config is in `data/config.yaml`. Run:

```powershell
cd c:\Users\fabio\Documents\dev\python3-lgpd-crawler

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

(Ensure `./data/config.yaml` exists; the override mounts `./data` at `/data`.) For **Docker Swarm** or **Kubernetes**, see **[deploy/DEPLOY.md](deploy/DEPLOY.md)**.

---

## 5. Access

- **Dashboard:** http://localhost:8088/
- **API docs:** http://localhost:8088/docs
- **Health:** http://localhost:8088/health

---

## 6. Stop and remove

```powershell
docker stop lgpd-audit
docker rm lgpd-audit
```

Or with Compose: `docker compose -f deploy/docker-compose.yml -f deploy/docker-compose.override.yml down`
