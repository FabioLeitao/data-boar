# Homelab — real inventory (copy to `docs/private/homelab/`)

After copying this file to **`docs/private/homelab/README.md`**, replace placeholders. **Never commit** `docs/private/`.

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
