# Multi-host lab smoke (DB stack + filesystem + network)

**Português (Brasil):** [LAB_SMOKE_MULTI_HOST.pt_BR.md](LAB_SMOKE_MULTI_HOST.pt_BR.md)

**Purpose:** Run a **repeatable**, **collaborator-friendly** lab round that exercises **PostgreSQL**, **MariaDB**, **compressed file samples**, and **LAN paths** (bind mounts, optional SMB/NFS/sshfs/cloud-backed folders) beyond what CI alone covers.

**Scope:** Operator-controlled lab only. **Do not** forward ports to the Internet. Use **synthetic** data from this repo and the bundled SQL seeds — **never** real customer or family PII in shared configs.

---

## 1. Recommended host order (efficiency)

**Policy:** Prefer **at least two** independent dimensions where it matters: e.g. two **Docker CE** hubs for `lab-smoke-stack` (**lab-node-02 + LAB-NODE-01** is enough). **LAB-NODE-03** and **LAB-NODE-04** are **not** required to run Docker or Compose; they still add value for **libc / ARM** CLI scans over LAN.

| Order | Host / role | Why |
| ----- | ----------- | --- |
| 1a | **LAB-NODE-01** (x86_64 Linux, Docker CE via [lab-node-01-baseline.yml](../../ops/automation/ansible/playbooks/lab-node-01-baseline.yml)) | First-class hub for `deploy/lab-smoke-stack` (DB containers). Same playbook adds the operator to the **`docker`** group — **log out/in** (or `newgrp docker`) after Ansible or `docker compose` fails with **permission denied** on `docker.sock`. |
| 1b | **lab-node-02** (Zorin, Docker) | Second hub: repeat the same compose stack so LAN DB smoke is not “one host only.” |
| 2 | **WORKSTATION (Windows dev)** | `docker-lab-build.ps1` / Hub image + quick `/health` + scan against **hub LAN IP** for DB targets; optional mount of `tests/data/compressed`. Optional **WSL2** clone for a second execution surface — [WSL2_DATA_BOAR_DEV_TESTING.md](WSL2_DATA_BOAR_DEV_TESTING.md). |
| 3 | **LAB-NODE-03** (Void **musl**) | Catches **wheel / libc** surprises (`cryptography`, `mysqlclient` build); run **CLI** scan to DB over LAN after opening firewall port. **No** Docker requirement. |
| 4 | **LAB-NODE-04** (ARM, low RAM) | **Last** — slow; use `scan.max_workers: 1`; confirm `uv sync` / MariaDB headers per **HOMELAB_HOST_PACKAGE_INVENTORY.md**. **Prerequisite:** free disk space (`git fetch` failed on full SD in recent LAB-OP runs). **No** Docker requirement. |

---

## 2. Deploy the DB stack (LAB-NODE-01 or hub host)

From the machine that will **own** the databases:

```bash
cd deploy/lab-smoke-stack
cp env.example .env
# edit .env if ports or passwords must change
docker compose up -d
docker compose ps
```

- **PostgreSQL** listens on **host port `55432`** (maps to 5432).
- **MariaDB** listens on **host port `33306`** (maps to 3306).

**Firewall:** allow TCP from lab LAN to those ports **only** (e.g. UFW on Ubuntu, `nft` on Void). **Do not** expose on WAN.

**Swarm:** For a single-node lab, `docker compose up` is enough. To use **Stack**, convert `ports`/`networks` as needed and `docker stack deploy`; keep the same published ports for other hosts to reach the DBs.

**Podman (optional):** Same `docker-compose.yml` files; use `podman compose` on the hub if you prefer rootless/OCI without uninstalling Docker CE — see [deploy/lab-smoke-stack/README.md](../../deploy/lab-smoke-stack/README.md) (Podman section). **k3s** remains a separate opt-in in [lab-node-01-baseline.yml](../../ops/automation/ansible/playbooks/lab-node-01-baseline.yml); converting this stack to Kubernetes manifests is not required for lab smoke.

**SCP or partial copy:** If `init/postgres` / `init/mariadb` were copied without world-readable bits, containers may fail with **Permission denied** on `/docker-entrypoint-initdb.d`. On the hub run `chmod -R a+rX init/postgres init/mariadb` under `deploy/lab-smoke-stack`, or use **`ops/automation/ansible/playbooks/lab-smoke-stack-init-perms.yml`** with inventory group **`[lab_smoke]`** (see **`ops/automation/ansible/inventory.example.ini`**). **Docker CE** on Debian-family hosts: **`deploy/ansible/roles/docker`** (ADR 0009).

**`permission denied` connecting to the Docker socket:** On LAB-NODE-01, apply [lab-node-01-baseline.yml](../../ops/automation/ansible/playbooks/lab-node-01-baseline.yml) (or add the operator to group **`docker`** and **start a new login session**). Non-interactive SSH cannot supply `sudo` password for `docker compose`; fix group membership instead of relying on `sudo docker` for routine compose.

---

## 3. Point Data Boar at the DBs

1. Copy `deploy/lab-smoke-stack/config.lab-smoke.example.yaml` to a **private** path (or gitignored name).
1. Replace **`HOST_LAB_DB`** with:
   - The **LAN IPv4** of the hub host (LAB-NODE-01), or
   - **`host.docker.internal`** if the Data Boar container runs **on the same OS** as Docker Desktop / same host with published ports, or
   - A **Docker network DNS** name if both services share one Compose project (advanced).
1. Run **Data Boar** (CLI or `--web`) from the host that should run the scan; ensure **routes and firewall** allow TCP to `HOST_LAB_DB:55432` and `:33306`.

**Pass criteria:** session completes; **findings** or schema metadata for `lab_customers` / `lab_notes`; **no** connection errors in `scan_failures` (see [TROUBLESHOOTING_MATRIX.md](../TROUBLESHOOTING_MATRIX.md)).

---

## 4. Filesystem: compressed corpus + innocuous paths

1. Mount **read-only** the repo directory `tests/data/compressed` (contains `sample1.zip`, `sample2.7z`, etc.) into the Data Boar container or use a bind path for native `uv run`.
1. Set `file_scan.scan_compressed: true` and extensions per [HOMELAB_VALIDATION.md](HOMELAB_VALIDATION.md) **§7**.
1. Install **`uv sync --extra compressed`** if you need **`.7z`** support.

**Optional “inócuo” tree:** add a parallel folder with only operational text (SKU, internal ticket IDs) to confirm **zero** false alarms on clean content.

---

## 5. Shares (SMB / NFS / sshfs / cloud)

Data Boar reads **whatever path the process sees**. There is no separate “SMB connector” — the OS must mount the share first.

| Mechanism | Pattern |
| --------- | ------- |
| **SMB/CIFS** | Mount on the **same host** that runs Data Boar (`/mnt/lab-share/...`); put that path in `filesystem` target. |
| **NFS** | Same — mount first, then `path:` in YAML. |
| **sshfs** | Mount remote directory on **lab-node-02** (or WORKSTATION WSL), then point `path:` to the mount. Latency affects scan time — acceptable for lab. |
| **OneDrive / pCloud / Google Drive / Dropbox** | Use the vendor’s **local sync folder** (fully synced files). **Files On-Demand** placeholders can block reads — pin or hydrate files before scanning. |

**Cross-host:** Other machines (lab-node-02, LAB-NODE-03) can use **TCP** to the hub DB; they do **not** need the same cloud mounts unless you are testing **filesystem** on that host — then mount or copy fixtures locally.

---

## 6. LAB-NODE-04 (ARM) — when to include

Use **after** x86_64 paths work. Clear **disk space** on the Pi before `git fetch` / `uv sync`. Expect longer runs; keep `scan.max_workers: low`.

---

## 7. LAB-OP script and git health

`scripts/lab-op-sync-and-collect.ps1` runs `git pull --ff-only` on each host. If **local `main` diverges** from `origin/main`, the pull **fails** and **no** `homelab-host-report.sh` runs — fix the clone (merge/rebase/reset per your policy), then re-run. **Disk full** on a host blocks `git fetch` — free space first.

---

## 8. Full E2E checklist (ordered, pass/fail)

Use after **§1** host order. Tick when done on your lab sheet.

| Step | Action | Pass hint |
| ---- | ------ | ---------- |
| A | **Unblock git** on LAB-NODE-01, lab-node-02, LAB-NODE-03: `main` must fast-forward to `origin/main` (or document why not). | `git pull --ff-only` succeeds. |
| B | **LAB-NODE-04:** free disk space; then `git fetch` works. | No `No space left on device` on fetch. |
| C | On **LAB-NODE-01** **and** a **second** hub (e.g. **lab-node-02**): `deploy/lab-smoke-stack` → `docker compose up -d`; healthchecks green on **both**. | `docker compose ps` healthy on each; TCP `55432` / `33306` from LAN to each hub IP. |
| D | **Populate** is automatic from `init/postgres/*.sql` and `init/mariadb/*.sql` (including `02_*` linkage tables). | `psql`/`mysql` client shows `lab_guardians`, `lab_minors_synthetic`, `lab_phone_directory` rows. |
| E | **WORKSTATION:** Data Boar (container or Win) uses `config.lab-smoke.example.yaml` with hub **LAN IP**; scan both DB targets + optional FS mounts. | Session completes; findings for `lab_customers` / linkage tables; `dob_possible_minor` counters if minors seed triggers. |
| F | **lab-node-02:** `uv run` scan to same DB host:ports; optional dashboard `:8088`. | Same as E from Linux paths. |
| G | **LAB-NODE-03:** CLI scan over LAN; confirm **musl** wheels (PyMySQL/psycopg2) load. | No import errors; scan completes. |
| H | **LAB-NODE-04:** `scan.max_workers: 1`; last in Colleague-Nn. | Completes or documents timeout/OOM for runbook. |
| I | **Filesystem extras:** mount `tests/data/compressed` **and** `tests/data/homelab_synthetic` read-only; `scan_compressed: true`. | Findings in archives + text/CSV linkage files. |
| J | **Shares (optional):** SMB/NFS/sshfs/cloud-local path in `filesystem` target after OS mount. | Same as any FS target — verify hydrated files (not cloud placeholders). |

**Blocked today?** If LAB-OP logs show **diverging branches** or **disk full**, steps **A–B** must be done before meaningful host reports or fresh `uv sync` on those machines.

---

## 9. What the SQL seeds contain

| File | Contents |
| ---- | -------- |
| `init/*/01_lab_smoke.sql` | `lab_customers`, `lab_notes` — happy path, borderline, FP-bait, innocuous row. |
| `init/*/02_lab_smoke_linkage.sql` | `lab_guardians`, `lab_minors_synthetic` (DOB/idade column names for **possible minor** heuristics), `lab_phone_directory`, extra customer/note rows for **shared phone** linkage. |

Re-seed requires recreating volumes or running manual DDL on existing DBs — for a clean slate, `docker compose down -v` and `up -d` (destructive).

---

## 10. Related docs

- [WSL2_DATA_BOAR_DEV_TESTING.md](WSL2_DATA_BOAR_DEV_TESTING.md) — optional second execution surface on the Windows dev PC.
- [LAB_EXTERNAL_CONNECTIVITY_EVAL.md](LAB_EXTERNAL_CONNECTIVITY_EVAL.md) — public APIs and optional third-party read-only DBs (complements LAN smoke).
- [HOMELAB_VALIDATION.md](HOMELAB_VALIDATION.md) — baseline playbook.
- [HOMELAB_HOST_PACKAGE_INVENTORY.md](HOMELAB_HOST_PACKAGE_INVENTORY.md) — system packages for connectors.
- [TROUBLESHOOTING_MATRIX.md](../TROUBLESHOOTING_MATRIX.md) — DB and Docker networking.
- [USAGE.md](../USAGE.md) — `targets` and `file_scan` reference.
