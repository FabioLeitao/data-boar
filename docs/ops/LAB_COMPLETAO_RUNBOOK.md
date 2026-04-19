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

4. **Session log / lessons template** — **`docs/private/homelab/COMPLETAO_SESSION_TEMPLATE.pt_BR.md`** (gitignored private tree): date, host, pass/fail, value, lessons learned.

## What this runbook does *not* automate

- Opening **firewall** holes, changing **AIDE**/**auditd**/**USBGuard**/**sshguard**/**fail2ban** policy: **operator decision**; document narrow test exceptions in **private** notes if you apply them.
- **Production readiness** is an **iterative** outcome: repeat completão, file issues, patch code/docs, re-run.

## Quick start

1. Ensure each lab host has the repo clone and **`uv`**; run **`uv sync`** (and extras per [TECH_GUIDE.md](../TECH_GUIDE.md)) as needed once.
2. Optional manifest fields: **`docs/private.example/homelab/lab-op-hosts.manifest.example.json`** (`completaoHealthUrl`).
3. From repo root on Windows: **`.\scripts\lab-completao-orchestrate.ps1`** (add **`-Privileged`** if sudoers allow non-interactive privileged probes on Linux).
4. Append lessons to the private template; link findings to **`PLANS_TODO.md`** / issues when product gaps appear.
