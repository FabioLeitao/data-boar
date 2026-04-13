# ThinkPad T14 — finish LAB-OP baseline (Ansible) and secret-session workflow

**Português (Brasil):** [T14_BASELINE_COMPLETION.pt_BR.md](T14_BASELINE_COMPLETION.pt_BR.md)

This runbook ties together **repeatable host hardening** (Ansible in this repo) and **operator habits** (sudo credential, Bitwarden CLI, optional VeraCrypt) without putting secrets in Git.

## 1. Finish the Ansible baseline (on the T14)

1. **Sync the repo:** `git pull` in your clone of `data-boar`.
2. **Inventory:** `ops/automation/ansible/inventory.local.ini` must include **`localhost ansible_connection=local`** under `[t14]` when you run the playbook **on the laptop itself** (not from another PC over SSH).
3. **Preflight:** from the repo root, run **`bash scripts/t14-ansible-preflight.sh`** — checks Ansible, inventory, sudo, `docker.list` permissions, and `bw` presence.
4. **Sudo:** `sudo -v` so the password prompt succeeds before a long run.
5. **Apply:** from `ops/automation/ansible/`, run **`ansible-playbook -i inventory.local.ini --ask-become-pass playbooks/t14-baseline.yml --diff`** (see **[ops/automation/ansible/README.md](../../ops/automation/ansible/README.md)** for troubleshooting).

After a successful run, **`bw`** should be available as **`/usr/local/bin/bw`** (and **`/etc/profile.d/zz-local-bin.sh`** adds `/usr/local/bin` to `PATH` in login shells). Open a **new login shell** or `source /etc/profile.d/zz-local-bin.sh` if `bw` is still not found.

## 2. Session warm-up: sudo + Bitwarden CLI (no VeraCrypt)

Typical order:

1. **`export PATH="/usr/local/bin:$PATH"`** (or source **`profile.d`** as above).
2. **`sudo -v`** — refreshes sudo timestamp; avoids mid-task password prompts during installs or mounts.
3. **`bw login`** (once per machine) / **`bw unlock`** — then **`export BW_SESSION=…`** as documented by Bitwarden for your shell.

**Note:** Debian **`command-not-found`** may suggest **`bundlewrap`** when you type **`bw`** — ignore; use the full path **`/usr/local/bin/bw`** if needed.

## 3. VeraCrypt + stacked private repo (operator-only)

Paths, keyfiles, and container locations are **not** duplicated here (they belong in **gitignored** notes). After baseline and `bw` work, follow the operator’s **VeraCrypt + private Git** guide under **`docs/private/homelab/`** (e.g. **`VERACRYPT_PRIVATE_REPO_SETUP.pt_BR.md`**, section **6.6** for the T14 flow: baseline → sudo warm → `bw` → mount).

## 4. Related docs

- **[LMDE7_T14_DEVELOPER_SETUP.md](LMDE7_T14_DEVELOPER_SETUP.md)** — full T14 + LMDE preparation (dual boot, packages, uv, etc.).
- **[ops/automation/ansible/README.md](../../ops/automation/ansible/README.md)** — baseline playbook, inventory, BECOME issues.
- **`scripts/t14-ansible-preflight.sh`** — preflight checks.
- **`scripts/t14-session-warm.sh`** — optional: PATH + `sudo -v` + reminder for `bw` (safe to commit; no secrets).
