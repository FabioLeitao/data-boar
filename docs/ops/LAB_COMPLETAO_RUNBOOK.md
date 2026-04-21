# Lab “completão” vs CI / pytest

**Português (Brasil):** [LAB_COMPLETAO_RUNBOOK.pt_BR.md](LAB_COMPLETAO_RUNBOOK.pt_BR.md)

**Purpose:** Define what **completão** means in this project: **running the product** (CLI, API, web) on **lab hosts**, across **SSH**, with **documented** outcomes — not the same thing as **`pytest`** or **`.\scripts\check-all.ps1`** on the dev PC alone.

**Relationship:**

| Layer | What it is | Typical command |
| ----- | ---------- | ---------------- |
| **CI / unit & guards** | Reproducible, GitHub-hosted, no LAN secrets | `CI` workflow, `pytest` |
| **Dev PC gate** | Full local hook bundle + tests before merge | `.\scripts\check-all.ps1` |
| **Lab completão** | Product + runtime + LAN + optional DB stack + optional HTTP | `scripts/lab-completao-host-smoke.sh` per host; `scripts/lab-completao-orchestrate.ps1` from Windows |

**Canonical multi-host checklist** (manual steps A–M): [LAB_SMOKE_MULTI_HOST.md](LAB_SMOKE_MULTI_HOST.md).

## Scripts (tracked)

1. **`scripts/lab-completao-host-smoke.sh`** (run **on each Linux lab host**, from repo root): `uv`, `docker` / `podman`, `deploy/lab-smoke-stack` compose `ps` if present, optional **`LAB_COMPLETAO_HEALTH_URL`** or **`--health-url`** for `/health`, quick **`import core.engine`**. **`--privileged`**: read-only snapshots via **`sudo -n`** (iptables/nft/ufw/fail2ban-related) — skips if sudo cannot run non-interactively.

2. **`scripts/lab-completao-orchestrate.ps1`** (run **on the Windows dev PC**): reads **`docs/private/homelab/lab-op-hosts.manifest.json`** (same idea as **`lab-op-sync-and-collect.ps1`**); SSH to each **`sshHost`**, runs the bash script for each **`repoPaths`** entry; optional per-host **`completaoHealthUrl`**: after SSH smoke, **`Invoke-WebRequest`** from the dev PC (LAN client view); writes **`docs/private/homelab/reports/completao_<timestamp>_allhosts.log`** plus per-host `*_completao_host_smoke.log`.

3. **Passwordless sudo (narrow)** — same discipline as **`homelab-host-report.sh`**: template under **gitignored** **`docs/private/homelab/LABOP_COMPLETÃO_SUDOERS.pt_BR.md`**. Do **not** commit real sudoers content to GitHub.

4. **Session log / lessons template** — **`docs/private/homelab/COMPLETAO_SESSION_TEMPLATE.pt_BR.md`** (gitignored private tree): date, host, pass/fail, value, lessons learned. Filled examples stay under **`docs/private/homelab/`** as **`COMPLETAO_SESSION_YYYY-MM-DD.md`** (operator-only; never public GitHub).

5. **`scripts/lab-op-repo-status.ps1`** (Windows): **`git fetch`** + **`git status -sb`** on each **`repoPaths`** (no reset). Optional **`-PullFfOnly`** for **`git pull --ff-only`** when the clone is strictly behind. **Start here** when orchestrate reports **`MISSING_SCRIPT`** — usually the clone is older than **`main`**.

6. **`scripts/lab-op-git-align-main.ps1`** (Windows): for each host in the same manifest, **`git fetch`** + **`git reset --hard origin/main`** on each **`repoPaths`** entry. **Destructive** (drops local commits on the clone); use when LAB-OP trees must match GitHub **`main`** and you accept losing local-only commits on those clones.

7. **Ansible (optional):** **`ops/automation/ansible/playbooks/lab-op-data-boar-git-sync.yml`** — alignment via group **`lab_op_data_boar`** in a local inventory (see **`inventory.example.ini`**). Reproducible when Ansible is already part of your operator workflow.

8. **Filesystem templates (tracked, copy to private or `~` on Linux):** **`docs/private.example/homelab/config.lab-fs-varlog.example.yaml`**, **`config.lab-fs-home-leitao.example.yaml`** — run **`main.py`** **on the same host** as the paths (SSH + `export PATH=$HOME/.local/bin:$PATH`; **`mkdir -p`** report/sqlite dirs first). **`/var/log`** may emit **`permission_denied`** for non-root users on some files — expected.

9. **MongoDB in completão:** connector **`driver: mongodb`**; install **`pymongo`** with **`uv sync --extra nosql`**. Bring up the optional stack: **`deploy/lab-smoke-stack`**: **`docker compose -f docker-compose.yml -f docker-compose.mongo.yml up -d`** (published port **27018** by default). If Mongo is down, the target fails as **unreachable**, not **unsupported**.

## Recommended slice order (one host at a time)

1. **Align clones:** **`lab-op-repo-status.ps1`** (inspect) then **`lab-op-git-align-main.ps1`** or manual merge only when you accept **destructive** reset on that clone.
2. **Host smoke:** **`lab-completao-orchestrate.ps1`** (or **`lab-completao-host-smoke.sh`** over SSH) until **`MISSING_SCRIPT`** is gone and **`import core.engine`** succeeds.
3. **FS `/var/log`:** copy **`config.lab-fs-varlog.example.yaml`**, run **`uv run python main.py --config …`** **on that Linux host** (not from Windows unless paths are mounted).
4. **FS home tree:** same with **`config.lab-fs-home-leitao.example.yaml`** (adjust username if not **`leitao`**).
5. **CLI completão** from the dev PC with a **private** YAML (DBs on a hub + synthetic FS under the repo) — see **`docs/ops/LAB_EXTERNAL_CONNECTIVITY_EVAL.md`** and private **`config.complete-eval.yaml`** pattern.
6. **API / web:** start **`main.py --web`** on a host; **`curl http://<host>:8088/health`** from another LAN machine; then browser. Add **`completaoHealthUrl`** to the manifest for orchestrate to probe from Windows.

## What this runbook does *not* automate

- Opening **firewall** holes, changing **AIDE**/**auditd**/**USBGuard**/**sshguard**/**fail2ban** policy: **operator decision**; document narrow test exceptions in **private** notes if you apply them.
- **Production readiness** is an **iterative** outcome: repeat completão, file issues, patch code/docs, re-run.

## Quick start

1. Ensure each lab host has the repo clone and **`uv`** (often **`~/.local/bin/uv`** — **`lab-completao-host-smoke.sh`** prepends that to **`PATH`**); run **`uv sync`** and **`uv sync --extra nosql`** if Mongo targets are in your YAML (and [TECH_GUIDE.md](../TECH_GUIDE.md) extras for compressed/shares as needed).
2. Optional manifest fields: **`docs/private.example/homelab/lab-op-hosts.manifest.example.json`** (`completaoHealthUrl`).
3. From repo root on Windows: **`.\scripts\lab-completao-orchestrate.ps1`** (add **`-Privileged`** if sudoers allow non-interactive privileged probes on Linux).
4. Append lessons to the private template; link findings to **`PLANS_TODO.md`** / issues when product gaps appear.
