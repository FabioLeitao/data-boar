# Ansible hardening (LAB-OP friendly)

This folder provides **generic**, reviewable Ansible automation for workstation hardening and baseline provisioning.

## Policy (tracked vs private)

- Keep **hostnames, IPs, usernames, SSH fingerprints, and secrets** out of tracked files.
- Put real inventory in **gitignored** `docs/private/homelab/` (see repo policy).

## Quick start

1) Create a local inventory (example):

```bash
cp inventory.example.ini inventory.local.ini
```

1) One interactive step (sudo warm-up):

On the target host (or in an SSH session), run:

```bash
sudo -v
```

1) Run the baseline playbook (example):

```bash
ANSIBLE_ROLES_PATH=./roles ansible-playbook -i inventory.local.ini playbooks/t14-baseline.yml --diff
```

## Token-aware wrapper (Windows → SSH → Ansible on T14)

If you want minimal toil from Windows (one password prompt, then automation), use:

```powershell
.\scripts\t14-ansible-baseline.ps1 -SshHost t14
```

To apply changes after a check pass:

```powershell
.\scripts\t14-ansible-baseline.ps1 -SshHost t14 -Apply
```

### Note (toil reduction, zero prompts)

- **Current workaround**: keep `sudo` warm on the target with `sudo -v` (extends the timeout for a few minutes).
- **Preferred end state**: a **restricted sudoers rule** (guardrailed, command-scoped) to allow the baseline automation to run **without prompts** when explicitly requested, aligned with the LAB-OP privileged-collection approach.

## What this does (safe-default)

- Installs baseline packages (auditing, diagnostics, operator utilities)
- Sets host banners (`/etc/issue`, `/etc/issue.net`, `/etc/banner.net`) via `figlet`/`toilet` (SSHD banner is opt-in)
- Installs `lynis` and writes a baseline `/etc/lynis/default.prf` with **comment-only** skip suggestions (opt-in by uncommenting)
- Enables firewall defaults (UFW) where appropriate
- Enables and configures `fail2ban` (SSH only) with conservative settings (optional `ignoreip` via inventory)
- Installs `aide` and `auditd` with a reviewable baseline (host-specific exceptions should stay private)
- Optional: enables zram-based swap (host-dependent sizing; opt-in)
- Ensures SSH hardening defaults (no root login; password auth off) **only if you opt-in**

## Post-automation validation (checklist)

After a `CHECK` + `APPLY`, run the quick validation checklist:

- `POST_AUTOMATION_VALIDATION.pt_BR.md`

## Important

Hardening is **contextual**. Before enabling any network-facing service, ensure the host is on the intended VLAN/segment and you understand the access model.

## Banners (figlet/toilet)

By default we generate a generic banner suitable for multiple hosts and environments:

- `/etc/banner.net`: full ASCII banner (best for SSH)
- `/etc/issue`, `/etc/issue.net`: short, non-sensitive banner (best for local console/tty)

To enable SSH banner, set `t14_banner_enable_sshd_banner=true` in your inventory/group vars.
