# Private operator notes (not on Git / GitHub)

**Purpose:** Define where **real** homelab inventory, hostnames, LAN details, and personal snapshots live, and how that differs from **public** documentation.

---

## 1. Safety: ignored by Git

The entire tree **`docs/private/`** is listed in **`.gitignore`**. Files you create there are **not** committed, **not** pushed to GitHub, and **not** part of the public repo clone for other contributors.

## Verify anytime:

```bash
git check-ignore -v docs/private/anything.md
# expect: .gitignore:...    docs/private/anything.md
```

**Cursor / agents:** May still read `docs/private/` **if** you open files or the workspace includes them—treat that as **local** disclosure to the tool, not “published to Git.”

---

## 2. Recommended layout (you create this locally)

Copy the **tracked template** from **`docs/private.example/`** into **`docs/private/`** (or create the same folders by hand):

| Path (local only)                            | Use                                                                                                                                                                                        |
| -----------------                            | ---                                                                                                                                                                                        |
| **`docs/private/homelab/`**                  | **Real** descriptions: hostnames, RFC1918 IPs, SSH users, `homelab-host-report.sh` outputs, UPS load lists, HVAC model numbers, UniFi VLAN IDs, solar logger IP, **redacted** API samples. |
| **`docs/private/homelab/validation-log.md`** | Dated §1–§2 pass/fail per host (optional filename).                                                                                                                                        |
| **`docs/private/homelab/solar.md`**          | Inverter/datalogger models, portal names, **references** to Bitwarden for keys (not plaintext passwords).                                                                                  |
| **`docs/private/`** (root of private)        | Optional catch-all: `WHAT_TO_SHARE_WITH_AGENT.md`, CV, certs, thesis PDFs—anything personal.                                                                                               |

**Rule:** Prefer **`homelab/`** for anything that maps your **physical/network** reality so it is easy to exclude from pCloud sync or backups if you ever split policies.

---

## 3. Public documentation policy (this repo)

**In tracked Markdown** (everything under `docs/` **except** `docs/private/`, plus `README`, `CONTRIBUTING`, etc.):

- Use **generic roles**: “primary Linux lab laptop,” “Windows + WSL dev workstation,” “x86 tower with Proxmox,” “musl mini-PC.”
- Use **placeholders**: `you@<hostname>`, `http://<your-sonar-host>:9000`, `*.example.com`.
- Do **not** paste **real hostnames, LAN IPs, Wi‑Fi PSKs, serials, or home paths** (`/home/you/...`, `C:\Users\...`).
- Do **not** add **Markdown links** to paths under `docs/private/...` in public files—those links **404** for everyone else on GitHub and **enumerate** filenames. Instead, write: *“Store specifics in your **gitignored** `docs/private/homelab/` tree (see **PRIVATE_OPERATOR_NOTES.md**).”*

**Example classes** (wattage, RAM era) may appear in public docs as **illustrative** only—your **exact** make/model belongs under **`docs/private/homelab/`**.

---

## 4. Related tracked docs

- [CONTRIBUTING.md](../CONTRIBUTING.md) — public repo hygiene.
- [SECURITY.md](../SECURITY.md) — secrets and `config.yaml`.
- [HOMELAB_VALIDATION.md](ops/HOMELAB_VALIDATION.md) — **playbook** (generic); real results → private `homelab/`.

**Template to copy:** [private.example/README.md](private.example/README.md)

**Português (Brasil):** [PRIVATE_OPERATOR_NOTES.pt_BR.md](PRIVATE_OPERATOR_NOTES.pt_BR.md)
