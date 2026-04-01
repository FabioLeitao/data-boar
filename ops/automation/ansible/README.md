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

2) Run the baseline playbook (example):

```bash
ansible-playbook -i inventory.local.ini playbooks/t14-baseline.yml --diff
```

## What this does (safe-default)

- Installs baseline packages (auditing, diagnostics, operator utilities)
- Enables firewall defaults (UFW) where appropriate
- Enables and configures `fail2ban` (SSH only) with conservative settings
- Ensures SSH hardening defaults (no root login; password auth off) **only if you opt-in**

## Important

Hardening is **contextual**. Before enabling any network-facing service, ensure the host is on the intended VLAN/segment and you understand the access model.

