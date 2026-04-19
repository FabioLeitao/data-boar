# Lab smoke stack (PostgreSQL + MariaDB)

Docker Compose bundle for **LAN-only** multi-host Data Boar tests. See **[docs/ops/LAB_SMOKE_MULTI_HOST.md](../../docs/ops/LAB_SMOKE_MULTI_HOST.md)** for host order, firewall, and checklist.

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
