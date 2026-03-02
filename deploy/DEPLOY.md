# Deploy LGPD Audit (Docker & Swarm & Kubernetes)

## Default: Web API and frontend

When you run the image **without** overriding the command (e.g. `docker run ... image`, Compose, Swarm, or Kubernetes with no `command`/`args`), the container starts the **web API and frontend**:

- **Dashboard:** `http://<host>:8088/` (status, start scan, recent sessions, download reports)
- **Reports:** `http://<host>:8088/reports`
- **Configuration:** `http://<host>:8088/config`
- **API docs:** `http://<host>:8088/docs`
- **Health:** `http://<host>:8088/health`

Port **8088** is exposed. Config and persistent data (SQLite, reports) live under **`/data`** (mount a volume or bind mount with `config.yaml`).

## CLI one-shot (override)

To run a **single audit from the CLI** instead of the API, override the container command and pass config (and optional `--tenant` / `--technician`):

```bash
# Bind mount a dir that contains config.yaml at /data
docker run --rm -v "$(pwd)/data:/data" \
  YOUR_IMAGE \
  python main.py --config /data/config.yaml --tenant "Acme" --technician "Ops"
```

Or with `--entrypoint`:

```bash
docker run --rm -v "$(pwd)/data:/data" \
  --entrypoint python \
  YOUR_IMAGE \
  main.py --config /data/config.yaml
```

The report is written under `report.output_dir` in config (e.g. `/data`); copy it out from the volume or bind-mounted dir. Do **not** use `--web` in these overrides.

## Image

- **Dockerfile** at repo root. Build: `docker build -t python3-lgpd-crawler:latest .`
- **Public image**: Push to GitHub Container Registry (ghcr.io) or Docker Hub and use that name in Compose/Swarm/Kubernetes.

## 1. Build and push image (public repository)

### Option A – GitHub Container Registry (ghcr.io)

```bash
# From repo root
docker build -t ghcr.io/fabioleitao/python3-lgpd-crawler:latest .
docker login ghcr.io   # Use a GitHub Personal Access Token with read:packages, write:packages
docker push ghcr.io/fabioleitao/python3-lgpd-crawler:latest
```

### Option B – Docker Hub

```bash
docker build -t YOUR_DOCKERHUB_USER/python3-lgpd-crawler:latest .
docker login
docker push YOUR_DOCKERHUB_USER/python3-lgpd-crawler:latest
```

Then in `deploy/docker-compose.yml` set `image:` to your pushed image (e.g. `ghcr.io/fabioleitao/...` or `YOUR_DOCKERHUB_USER/...`).

## 2. Prepare config

The app expects **config at `/data/config.yaml`** inside the container. Use the same schema as in the repo (see `docs/USAGE.md`). Minimum for API-only:

- `targets: []`
- `report.output_dir: /data`
- `sqlite_path: /data/audit_results.db`
- `api.port: 8088`

Copy `deploy/config.example.yaml` and edit, then either:

- **Volume**: Create a volume and put `config.yaml` into it before first run, or
- **Bind mount**: Mount a host dir that contains `config.yaml` at `/data`.

Example with bind mount (host dir `./data`):

```bash
mkdir -p data
cp deploy/config.example.yaml data/config.yaml
# Edit data/config.yaml (targets, etc.)
```

## 3. Run as a normal container (single host)

```bash
# From repo root; image built locally
docker build -t python3-lgpd-crawler:latest .

# Run with a volume for /data (you must provide config inside the volume)
docker volume create lgpd-data
# Copy config into volume (e.g. run a temp container and copy file in), or use bind mount:

docker run -d --name lgpd-audit \
  -p 8088:8088 \
  -v "$(pwd)/data:/data" \
  -e CONFIG_PATH=/data/config.yaml \
  python3-lgpd-crawler:latest
```

Or use Compose (no Swarm):

```bash
# In deploy/docker-compose.yml use build: and image: as you prefer
# Ensure /data has config: e.g. bind mount ./data to /data (see below)
docker compose -f deploy/docker-compose.yml up -d
```

To use a **bind mount** for `data` instead of a named volume, in `deploy/docker-compose.yml` replace the volume:

```yaml
volumes:
  - ./data:/data   # instead of lgpd-data:/data
```

Create `deploy/data/config.yaml` (or `./data/config.yaml` if you run from repo root) from `config.example.yaml` before `up`.

## 4. Deploy as a Docker Swarm service (local machine)

### 4.1 Initialize Swarm (if not already)

```bash
docker swarm init
```

### 4.2 Use the stack (Compose file is Swarm-compatible)

From the **repository root**:

```bash
# Ensure config is available to the service. Option 1: bind mount a host dir
mkdir -p data
cp deploy/config.example.yaml data/config.yaml
# Edit data/config.yaml

# Override volume to bind mount ./data into the service
docker stack deploy -c deploy/docker-compose.yml lgpd-audit
```

If you use the default **named volume** `lgpd-data`, the first time the service starts the container will see an empty `/data`. You must put `config.yaml` into that volume (e.g. run a one-off container that mounts the volume and copies a file in, or use a config mount). Easiest for local: **bind mount**.

Create `deploy/docker-compose.override.yml` (or a fragment) to bind mount without editing the main file:

```yaml
# deploy/docker-compose.override.yml (optional, for bind mount)
version: "3.8"
services:
  lgpd-audit:
    volumes:
      - ./data:/data
```

Then from repo root:

```bash
docker stack deploy -c deploy/docker-compose.yml -c deploy/docker-compose.override.yml lgpd-audit
```

If you don’t use an override, ensure the stack’s `lgpd-data` volume is populated with `config.yaml` (e.g. via a one-off container).

### 4.3 Check the service

```bash
docker service ls
docker service ps lgpd-audit_lgpd-audit
docker service logs lgpd-audit_lgpd-audit
```

### 4.4 Access

- Dashboard: http://localhost:8088/
- API: http://localhost:8088/docs  
Port 8088 is exposed by the Compose file.

### 4.5 Remove the stack

```bash
docker stack rm lgpd-audit
```

## 5. Using the public image (no local build)

1. In `deploy/docker-compose.yml` set `image:` to your published image (e.g. `ghcr.io/fabioleitao/python3-lgpd-crawler:latest`) and remove or comment out the `build:` block.
2. Prepare `/data/config.yaml` as above (volume or bind mount).
3. Run with Compose or Swarm as in sections 3 and 4.

## 6. Kubernetes

A minimal deployment runs the **image default** (web API + frontend). No `command`/`args` in the manifest.

- Create a ConfigMap or Secret for `config.yaml`, or use a volume that provides `/data/config.yaml`.
- Apply from `deploy/kubernetes/` (see `deploy/kubernetes/README.md`).

```bash
kubectl apply -f deploy/kubernetes/
# Access via NodePort, LoadBalancer, or Ingress (port 8088).
```

To run **CLI one-shot** in Kubernetes, use a Job with `command`/`args` overriding to `python main.py --config /data/config.yaml` (and mount config + output volume).

## Summary

| Goal | Command / step |
|------|-----------------|
| Default (API + frontend) | Run image with no command override: `docker run`, Compose, Swarm, or Kubernetes |
| CLI one-shot | Override command: `docker run ... --entrypoint python IMAGE main.py --config /data/config.yaml` |
| Build image | `docker build -t python3-lgpd-crawler:latest .` |
| Push to registry | `docker tag ... YOUR_REGISTRY/python3-lgpd-crawler:latest` then `docker push ...` |
| Run API (single container) | `docker run -d -p 8088:8088 -v ./data:/data python3-lgpd-crawler:latest` |
| Compose | `docker compose -f deploy/docker-compose.yml up -d` (provide config in `./data`) |
| Swarm stack | `docker stack deploy -c deploy/docker-compose.yml -c deploy/docker-compose.override.yml lgpd-audit` |
| Kubernetes | `kubectl apply -f deploy/kubernetes/` (see deploy/kubernetes/README.md) |

All paths and image names assume you are in the repo root or in `deploy/` as indicated.
