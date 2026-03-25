# Homelab — real inventory (copy to `docs/private/homelab/`)

After copying this file to **`docs/private/homelab/README.md`**, replace placeholders. **Never commit** `docs/private/`.

## SSH — how the assistant reaches this host

The AI **cannot** open your LAN by itself. **Default:** it runs **`ssh`** from **your** Cursor terminal on the dev PC, using **your** `~/.ssh/config` (Windows OpenSSH, WSL, or Git’s `ssh`).

1. Add a **`Host`** block on the machine where Cursor’s terminal runs (usually **not** in the repo):

   ```sshconfig
   Host latitude-lab
     HostName <LAN-or-VPN-IP-or-mDNS>
     User <your-linux-user>
     IdentityFile ~/.ssh/id_ed25519
   ```

1. In **this** private README, record **only** the alias name and role (no secrets):

| Role        | SSH `Host` alias (local to dev PC) | Notes                          |
| ----------- | ---------------------------------- | ------------------------------ |
| Lab server  | `latitude-lab`                     | Zorin; reports / Docker / ISOs |

1. Agents **`read_file`** this README and **`AGENT_LAB_ACCESS.md`** when homelab work applies (**`@` optional**). Then use **`ssh latitude-lab 'command'`** from the integrated terminal.

**Do not** copy **private keys** or **passwords** into `docs/private/`. Use **key-based** login; keep passphrases in your OS keychain / agent.

**SNMP / API tokens (UniFi, etc.):** See **[CREDENTIALS_AND_LAB_SECRETS.md](CREDENTIALS_AND_LAB_SECRETS.md)** ([pt-BR](CREDENTIALS_AND_LAB_SECRETS.pt_BR.md)) — session env vars, vault, gitignored `.env`; never paste into chat. **Extra SNMP targets (switch, Linux):** [SNMP_LAB_TARGETS.md](SNMP_LAB_TARGETS.md) ([pt-BR](SNMP_LAB_TARGETS.pt_BR.md)).

**Future — syslog + detection (when lab hardware is ready):** [OBSERVABILITY_SYSLOG_DETECTION_CHECKLIST.md](OBSERVABILITY_SYSLOG_DETECTION_CHECKLIST.md) ([pt-BR](OBSERVABILITY_SYSLOG_DETECTION_CHECKLIST.pt_BR.md)) — ties to [PLAN_LAB_OP_OBSERVABILITY_STACK.md](../../plans/PLAN_LAB_OP_OBSERVABILITY_STACK.md).

**Operator — AI access, security rationale, blue-team cadence:** [OPERATOR_AI_LAB_ACCESS_AND_BLUE_TEAM_RUNBOOK.md](OPERATOR_AI_LAB_ACCESS_AND_BLUE_TEAM_RUNBOOK.md) ([pt-BR](OPERATOR_AI_LAB_ACCESS_AND_BLUE_TEAM_RUNBOOK.pt_BR.md)) — copy to `docs/private/homelab/` and add site-specific notes (no secrets in git).

**L3 / DHCP / DNS / CyberSecure (UniFi):** [LAB_NETWORK_L3_DHCP_AND_CYBERSEC.md](LAB_NETWORK_L3_DHCP_AND_CYBERSEC.md) ([pt-BR](LAB_NETWORK_L3_DHCP_AND_CYBERSEC.pt_BR.md)) — per-VLAN gateway and DNS intent, honeypot alignment, verification commands; fill the private inventory table only under `docs/private/homelab/`.

**Sequenced lab plan (firewall → access → Loki → Wazuh):** [PLAN_LAB_FIREWALL_ACCESS_AND_OBSERVABILITY.md](../../plans/PLAN_LAB_FIREWALL_ACCESS_AND_OBSERVABILITY.md) ([pt-BR](../../plans/PLAN_LAB_FIREWALL_ACCESS_AND_OBSERVABILITY.pt_BR.md)) in `docs/plans/` — sprint checklist ties to [PLAN_LAB_OP_OBSERVABILITY_STACK.md](../../plans/PLAN_LAB_OP_OBSERVABILITY_STACK.md).

**Shopping list + power (private only):** [LAB_OP_SHOPPING_LIST_COVER_NOTE.md](LAB_OP_SHOPPING_LIST_COVER_NOTE.md) — full list with indicative prices stays under **`docs/private/homelab/LAB_OP_SHOPPING_LIST_AND_POWER.md`** (gitignored). **Urgent:** meter / breaker / panel photos for safe UPS and Enel planning.

**CLI / session habit dumps (private only):** If you keep **`uptime`**, **`w`**, **`last`**, **`lastlog`**, or similar for planning or incident review, store under **`docs/private/homelab/reports/`** (or a dated `.txt`) — not in tracked docs, issues, or PRs (LAN IPs and login patterns). See **`docs/PRIVATE_OPERATOR_NOTES.md`** (EN) / **`.pt_BR.md`**.

### Windows: pCloud as `P:` (optional)

If you sync the same tree to **Linux** (`~/pCloudDrive`) and **Windows** (**`P:`**), note that here (e.g. “reports copy also under `P:\Backups\…`”). The assistant can use **`P:\…`** from the **Cursor terminal on Windows** when pCloud is mounted—still **gitignore** any paths you write in this file.

## Hosts

| Role | Hostname (LAN)   | OS | Notes |
| ---- | ---------------- | -- | ----- |
| …    | …                | …  | …     |

**Secondary laptop (parallel runner):** If you use a **modern business laptop** (e.g. ThinkPad T14 Gen 4) for burst Docker/pytest work, record **exact MTM** (e.g. `21HE`), CPU, RAM, disk, and whether it runs **native Linux** or **Win11+WSL2** here—**never** in the public repo.

## Network

- UDM-SE: management URL (private), VLAN IDs, …
- UPS: what is plugged into the Attiv (W measured)

## Security posture (optional but recommended)

Maintain **`LAB_SECURITY_POSTURE.md`** next to this README (copy from a filled `docs/private/homelab/` tree or create empty from scratch): WAN/NAT assumptions, **`sshd -T`** / **UFW** / **Fail2ban** / **`nft list ruleset`** snapshots per host, and a short **improvement backlog**. Tracked index: **`docs/ops/OPERATOR_LAB_DOCUMENT_MAP.md`** (LAB‑PB vs LAB‑OP).

## LAB-OP doc language pairs (policy)

- **[I18N_LAB_OP.md](I18N_LAB_OP.md)** · [pt-BR](I18N_LAB_OP.pt_BR.md) — when to use **`File.md`** vs **`File.pt_BR.md`** under your private `homelab/` tree (gitignored).

## Operator re-teach template (EN + pt-BR)

Tracked **placeholders** (copy structure into private `homelab/`, then fill with **your** facts — **never** commit `docs/private/`):

- **[OPERATOR_RETEACH.md](OPERATOR_RETEACH.md)** (English)
- **[OPERATOR_RETEACH.pt_BR.md](OPERATOR_RETEACH.pt_BR.md)** (Brazilian Portuguese)

Your private tree may keep **one** file (e.g. only pt-BR) or **both**; either way, follow **`.cursor/rules/docs-pt-br-locale.mdc`** for Portuguese prose. **`*.pt_BR.md`** under **`docs/private/`** is included in **`tests/test_docs_pt_br_locale.py`** when the folder exists (same idea as markdown lint). Store **`homelab-host-report`** output under **`reports/`** as **`<HOST>_<YYYYMMDD_HHMM>_homelab_host_report.log`** (see **[reports/README.md](reports/README.md)**; include **WSL** under a distinct **HOST** name) for merge into **`LAB_SOFTWARE_INVENTORY.md`**. From Windows: **`scripts/collect-homelab-report-remote.ps1`**. For **POST /scan** + poll **`/status`**, use **`scripts/poll_dashboard_scan.py`** (`--base` / `DATA_BOAR_BASE`), not a hardcoded host script.

## Validation log

- YYYY-MM-DD: host X — §1.1–1.2 pass/fail — …

## Solar (optional)

- Inverter model, app name, Bitwarden item for API ref — or use `solar.md` next to this file.

## ISO inventory (optional)

- Copy or maintain **`iso-inventory.md`** here — list of `.iso` / `.img` under `~/Downloads/iso` (or your path). **Gitignored** if under `docs/private/homelab/` in the repo clone. Optional: `sha256sum` lines for integrity after pCloud sync.
