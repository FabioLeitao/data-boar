# Operator secrets: Bitwarden (password manager as your vault)

**Purpose:** Explain how **Bitwarden** fits next to Data Boar’s **`pass_from_env` / `*_from_env`**, gitignored **`config.yaml`**, and the future **in-app vault** ([PLAN_SECRETS_VAULT.md](../plans/PLAN_SECRETS_VAULT.md)).

---

## Can Bitwarden be your “secrets repository”?

**Yes — as the system where *you* store and retrieve secrets.** It is **not** (today) wired into the app as automatic runtime injection.

| Layer                              | Role                                                                                                                                                                                                                             |
| -----                              | ----                                                                                                                                                                                                                             |
| **Bitwarden vault**                | **Human source of truth:** DB passwords, API keys, SNMP/auth material, vendor cloud keys, TLS passphrases, “where is my homelab VLAN doc” pointers.                                                                              |
| **Environment variables**          | **Runtime for Data Boar:** `pass_from_env`, `api_key_from_env`, etc. You **copy** from Bitwarden when starting the process, or use a **small launcher script** / container orchestrator that injects env from your secret store. |
| **Gitignored `config.yaml`**       | May still hold secrets locally; prefer **env** for anything you might accidentally paste; **never** commit.                                                                                                                      |
| **Phase B in-app vault** (planned) | **Application-embedded** encrypted store and `@vault:` references — a **different** mechanism from Bitwarden; both can coexist (Bitwarden = operator backup; in-app = server-local).                                             |

---

## Free tier vs paid (verify current plans on [bitwarden.com](https://bitwarden.com/pricing/))

**Free (personal)** is usually **enough** for a **solo** developer/operator to hold **all** project and homelab secrets: **unlimited passwords**, **sync**, **generator**, and **2FA on your Bitwarden account** (enable it).

**Paid tiers** often add value when:

- You want **TOTP codes inside the vault** next to each login (Premium-style feature — free users often use a **separate** authenticator app).
- **Bitwarden Authenticator** (e.g. **iPhone**): scans **QR** codes for **OTP/TOTP** and can **sync** with your Bitwarden account alongside passwords—one ecosystem across **browser extension**, **desktop**, and **mobile**. Exact capabilities (sync, item linking) depend on **current** Bitwarden product docs and **your** plan; verify on [bitwarden.com](https://bitwarden.com/pricing/) and the Authenticator help pages.
- You need **encrypted file attachments** (license blobs, small key backups) beyond what notes allow.
- You want **Families** / **Teams** / **Organizations** for **shared collections** (future collaborators or household).
- You want **emergency access**, **advanced 2FA**, or **directory integration** at org scale.

**When paid “makes sense for later development”:** If you add **teammates**, **shared lab** credentials, or you want **one** place for **TOTP + secrets** with audit-friendly sharing — not because Data Boar **requires** Bitwarden Premium to run.

---

## Practices that work well with this repo

1. **One item per logical secret** (e.g. “Lab Postgres read-only”) with **custom fields** for host, user, DB name, password.
1. **Secure Note** for long tokens or PEM blocks — paste into **local** env or file only; never into tracked Markdown.
1. **Bitwarden CLI (`bw`)** — after `bw unlock`, use **`BW_SESSION`** with short lifetime to script `bw get password …` into env for local runs. **Do not** commit session strings or master password.
1. **Master password** and **2FA recovery codes** — store recovery codes **offline** or in Bitwarden **printout flow** per Bitwarden guidance; not in **`docs/private/`** in plaintext next to the repo if the disk is shared (that whole tree is gitignored but still **local disk**).
1. **Authenticator + vault** — If you use **Bitwarden Authenticator** on **iOS/Android**, keep **screen lock** and **vault timeout** tight; OTPs are as sensitive as passwords for sites that rely on TOTP alone.

---

## Verify `bw` on each machine (no remote check from the repo)

**This repository and Cursor cannot SSH into your LAN** or read `/usr/local/bin` on your **Latitude** or **mini-PC**. Only **you** can confirm install paths.

**On each Linux host** (SSH or local terminal), run:

```bash
command -v bw && bw --version
```

- **If you see a path + version:** CLI is on **`PATH`** for that shell user.
- **If empty / “not found”:** not installed for that user, or installed outside **`PATH`** (e.g. `~/bin`, `~/.npm-global/bin`).

**Optional** (shows lock state; may echo **account email** — **redact** if you paste output):

```bash
bw status
```

**Debian/Ubuntu** (only if installed via `apt` / `.deb`):

```bash
dpkg-query -W -f='${Status}\t${Package}\t${Version}\n' bitwarden-cli 2>/dev/null || true
```

**Automated bundle:** [HOMELAB_HOST_PACKAGE_INVENTORY.md](HOMELAB_HOST_PACKAGE_INVENTORY.md) — run `scripts/homelab-host-report.sh` on **each** host; it prints a **`bw`** block when present.

**Windows (e.g. dev laptop):** If you use CLI there, check `where bw` in **cmd** or `Get-Command bw` in **PowerShell** after install.

---

## Homelab alignment

- **Internal** topology (VLANs, IPs): Bitwarden Secure Note **or** **`docs/private/homelab/`** — pick one system of record ([PRIVATE_OPERATOR_NOTES.md](../PRIVATE_OPERATOR_NOTES.md)).
- **Solar / inverter API keys:** Bitwarden + public docs only describe **where** to put keys, not the values ([HOMELAB_SOLAR_MONITORING_INTEGRATION.md](HOMELAB_SOLAR_MONITORING_INTEGRATION.md)).

---

## See also

- [SECURITY.md](../../SECURITY.md) — redaction, env-based secrets, `config.yaml` hygiene.
- [PLAN_SECRETS_VAULT.md](../plans/PLAN_SECRETS_VAULT.md) — Phase B in-app vault (separate track).
- [CONTRIBUTING.md](../../CONTRIBUTING.md) — do not commit credentials.

**Português (Brasil):** [OPERATOR_SECRETS_BITWARDEN.pt_BR.md](OPERATOR_SECRETS_BITWARDEN.pt_BR.md)
