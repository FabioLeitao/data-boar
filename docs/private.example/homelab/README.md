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

2. In **this** private README, record **only** the alias name and role (no secrets):

   | Role        | SSH `Host` alias (local to dev PC) | Notes                          |
   | ----------- | ---------------------------------- | ------------------------------ |
   | Lab server  | `latitude-lab`                     | Zorin; reports / Docker / ISOs |

3. Agents **`read_file`** this README and **`AGENT_LAB_ACCESS.md`** when homelab work applies (**`@` optional**). Then use **`ssh latitude-lab 'command'`** from the integrated terminal.

**Do not** copy **private keys** or **passwords** into `docs/private/`. Use **key-based** login; keep passphrases in your OS keychain / agent.

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

## Validation log

- YYYY-MM-DD: host X — §1.1–1.2 pass/fail — …

## Solar (optional)

- Inverter model, app name, Bitwarden item for API ref — or use `solar.md` next to this file.

## ISO inventory (optional)

- Copy or maintain **`iso-inventory.md`** here — list of `.iso` / `.img` under `~/Downloads/iso` (or your path). **Gitignored** if under `docs/private/homelab/` in the repo clone. Optional: `sha256sum` lines for integrity after pCloud sync.
