# Lab smoke stack (PostgreSQL + MariaDB + optional MongoDB)

Docker Compose bundle for **LAN-only** multi-host Data Boar tests. See **[docs/ops/LAB_SMOKE_MULTI_HOST.md](../../docs/ops/LAB_SMOKE_MULTI_HOST.md)** for host order, firewall, and checklist.

**MongoDB:** not included in the default `docker compose up -d`; add **`docker compose -f docker-compose.yml -f docker-compose.mongo.yml up -d`** (or only `docker-compose.mongo.yml` if you need Mongo alone). Data Boar needs **`uv sync --extra nosql`** for `driver: mongodb`.

**Quick start:**

```bash
cd deploy/lab-smoke-stack
cp env.example .env
docker compose up -d
```

**Optional MongoDB (local `driver: mongodb` smoke):**

```bash
docker compose -f docker-compose.mongo.yml up -d
```

**Config example for Data Boar:** `config.lab-smoke.example.yaml` (copy elsewhere, set hub host IP, mount `tests/data/compressed` and `tests/data/homelab_synthetic` as documented). External/public API + DB eval: **`docs/ops/LAB_EXTERNAL_CONNECTIVITY_EVAL.md`**.

**SQL seeds:** `init/postgres/` and `init/mariadb/` — `01_*` base tables, `02_*` linkage + minor-adjacent + shared-phone rows.

**Mongo seed:** `init/mongodb/01_lab_smoke_seed.js` (database `lab_smoke_mongo`).

---

## Podman (optional — e.g. rootless experiments on LAB-NODE-01)

The same Compose files work with **Podman** on Debian/LMDE when the `podman` and `compose`/`podman-compose` stack is installed. This repo’s **Ansible baseline for LAB-NODE-01 still defaults to Docker CE** (`playbooks/lab-node-01-baseline.yml`); Podman is **opt-in** (`lab-node-01_install_podman: true`) and can **coexist** with Docker — you do **not** need to uninstall Docker to try Podman.

**Typical flow (hub host shell):**

```bash
cd deploy/lab-smoke-stack
cp env.example .env
# Podman 4+ (Debian bookworm/trixie backports or upstream):
podman compose up -d
podman compose -f docker-compose.mongo.yml up -d
```

**Rootless Podman:** published ports must reach LAN clients; if binds fail, check [Podman networking docs](https://docs.podman.io/en/latest/markdown/podman-compose.1.html) and firewall. Prefer the same **hub LAN IP** in Data Boar config as with Docker.

**Kubernetes (k3s):** `lab-node-01-baseline.yml` can install k3s (`lab-node-01_install_k3s: true`), but this stack is maintained as **Compose** for simplicity. Converting to Helm/manifests is a separate exercise — not required for Data Boar lab smoke.

**If `docker` service is stopped on LAB-NODE-01:** start it with `sudo systemctl start docker` (interactive sudo) before expecting `docker compose` to work; Podman does not replace `systemd` unit `docker` unless you deliberately migrate — document that choice in operator notes, not in tracked inventory.
