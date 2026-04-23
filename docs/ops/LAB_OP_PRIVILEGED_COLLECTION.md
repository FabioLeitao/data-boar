# LAB-OP privileged collection (safe-by-default)

**pt-BR:** [LAB_OP_PRIVILEGED_COLLECTION.pt_BR.md](LAB_OP_PRIVILEGED_COLLECTION.pt_BR.md)

## Goal

Enable **operator-controlled**, **guardrailed** privileged collection for LAB-OP inventory and hardening readiness — without normalizing broad `NOPASSWD` sudo.

## How it works

The host report script supports opt-in flags:

- `bash scripts/homelab-host-report.sh` (default, no sudo)
- `bash scripts/homelab-host-report.sh --privileged` (best-effort `sudo -n`)
- `bash scripts/homelab-host-report.sh --privileged --deep` (heavier checks, still best-effort)

On Windows (operator PC), you can run all hosts from a manifest:

- `.\scripts\run-homelab-host-report-all.ps1`
- `.\scripts\run-homelab-host-report-all.ps1 -Privileged`
- `.\scripts\run-homelab-host-report-all.ps1 -Privileged -Deep`
- Shorthand wrapper (taxonomy): `.\scripts\lab-op.ps1 -Action report-all -Privileged -Deep`

If you want **zero prompts** (true non-interactive runs), prefer the **repo-path** runner:

- `.\scripts\lab-op-sync-and-collect.ps1 -SkipGitPull -Privileged -Deep`

This runs the report as `bash scripts/homelab-host-report.sh ...` **inside the repo path** listed for each host in the manifest (stable path for sudoers allowlists).

## Recommended sudoers pattern (restricted)

If you want passwordless collection, do it **surgically**:

- allow a single command (the report script) with fixed arguments
- do not allow editing tools, shells, or globbing commands

### Example (template — replace placeholders)

1) On the host, create a sudoers include:

```bash
sudo visudo -f /etc/sudoers.d/labop-host-report
```

2) Paste (replace `LEITAO_USER` and `REPO_PATH`):

```text
# Allow only the LAB-OP host report to run without a password.
# Replace:
# - LEITAO_USER: your Linux username (e.g. leitao)
# - REPO_PATH: absolute path to the repo clone on that host (no spaces preferred)

Cmnd_Alias LABOP_HOST_REPORT = /bin/bash REPO_PATH/scripts/homelab-host-report.sh --privileged, \
                               /bin/bash REPO_PATH/scripts/homelab-host-report.sh --privileged --deep

LEITAO_USER ALL=(root) NOPASSWD: LABOP_HOST_REPORT
```

3) Validate:

```bash
sudo -l
sudo -n /bin/bash REPO_PATH/scripts/homelab-host-report.sh --privileged | head -20
```

### One-time setup checklist (per host)

1) Ensure the repo exists at a stable path on that host (example):

```bash
ls -la "$HOME/Projects/dev/data-boar/scripts/homelab-host-report.sh"
```

2) Create the sudoers include (restricted) and validate:

```bash
sudo visudo -f /etc/sudoers.d/labop-host-report
sudo -l
sudo -n /bin/bash "$HOME/Projects/dev/data-boar/scripts/homelab-host-report.sh" --privileged --deep | head -40
```

3) From the Windows operator PC, run an all-host privileged collection **without prompts**:

```powershell
.\scripts\lab-op-sync-and-collect.ps1 -SkipGitPull -Privileged -Deep
```

## Ansible Podman apply (same narrow NOPASSWD discipline)

To avoid **BECOME** password prompts when installing **only** Podman via
`playbooks/lab-node-01-podman.yml`, extend the sudoers include with **fixed** commands for
`scripts/lab-node-01-ansible-labop-podman-apply.sh` (same spirit as `homelab-host-report.sh`).
The Ansible role **`lab-node-01_labop_sudoers`** writes **`LABOP_HOST_REPORT`** and
**`LABOP_ANSIBLE_PODMAN`** together when **`lab-node-01_labop_sudoers_enable: true`**.

Example merge (replace `LEITAO_USER` / `REPO_PATH`):

```text
Cmnd_Alias LABOP_ANSIBLE_PODMAN = /bin/bash REPO_PATH/scripts/lab-node-01-ansible-labop-podman-apply.sh --apply, \
                                  /bin/bash REPO_PATH/scripts/lab-node-01-ansible-labop-podman-apply.sh --check

LEITAO_USER ALL=(root) NOPASSWD: LABOP_HOST_REPORT, LABOP_ANSIBLE_PODMAN
```

On the host (after `visudo -cf`):

```bash
sudo -n /bin/bash "$HOME/Projects/dev/data-boar/scripts/lab-node-01-ansible-labop-podman-apply.sh" --check
sudo -n /bin/bash "$HOME/Projects/dev/data-boar/scripts/lab-node-01-ansible-labop-podman-apply.sh" --apply
```

From Windows (**non-interactive** SSH; no Ansible `-K` prompt):

```powershell
.\scripts\lab-node-01-ansible-baseline.ps1 -SshHost lab-node-01 -Apply -SkipCheck -PodmanOnly -NoAskBecomePass
```

Requires **`ansible-playbook`** on the target and the sudoers lines above.

## Guardrails

- Prefer removing the sudoers file after the collection window if you don't need it long term.
- Never use `NOPASSWD: ALL`.
- Keep hostnames, IPs and secrets out of tracked docs; store raw logs under `docs/private/homelab/reports/`.

