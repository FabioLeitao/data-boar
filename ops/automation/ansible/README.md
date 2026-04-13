# Ansible hardening (LAB-OP friendly)

This folder provides **generic**, reviewable Ansible automation for workstation hardening and baseline provisioning.

## Policy (tracked vs private)

- Keep **hostnames, IPs, usernames, SSH fingerprints, and secrets** out of tracked files.
- Put real inventory in **gitignored** `docs/private/homelab/` (see repo policy).

## New playbooks (contributors)

Debian/Ubuntu installs can be blocked by **`apt-listbugs`** during unattended runs. Every play with `hosts:` must set:

`environment: "{{ labop_debian_unattended_apt_environment }}"`

(or `combine` with play-specific extras, as in `playbooks/t14-baseline.yml`). Defaults are in **`group_vars/all.yml`**. Repo CI fails if a tracked playbook under `playbooks/*.yml` omits `environment` on any play — see **`tests/test_ansible_playbooks_unattended_apt.py`** and **[CONTRIBUTING.md](../../CONTRIBUTING.md)**.

## Quick start

### Prerequisites on the T14 (target)

Run these **once** on the laptop (as `leitao`, with sudo):

1. **Clone** this repo (path expected by `scripts/t14-ansible-baseline.ps1`):

   ```bash
   mkdir -p ~/Projects/dev && cd ~/Projects/dev
   git clone <your-upstream-or-fork-url> data-boar
   ```

2. **Install Ansible** (Debian/LMDE package is enough for this playbook):

   ```bash
   sudo apt update
   sudo apt install -y ansible
   ansible-playbook --version
   ```

3. **Inventory:** from `ops/automation/ansible/`, copy the example and point `[t14]` at this host. The Windows helper script **rewrites** `[t14]` to `localhost` + `ansible_connection=local` when you run Ansible **on the T14 over SSH** (same pattern as `t14-ansible-baseline.ps1`).

   ```bash
   cd ~/Projects/dev/data-boar/ops/automation/ansible
   cp -f inventory.example.ini inventory.local.ini
   # Edit [t14] if you run from a different machine than localhost; for local runs use localhost as in the script.
   ```

### Run order

1) Create `inventory.local.ini` (see above).

2) **Warm sudo** on the target (one interactive password if needed):

```bash
sudo -v
```

3) Run the baseline playbook **from** `ops/automation/ansible` (this directory has `ansible.cfg` with `roles_path = roles`, same as `ANSIBLE_ROLES_PATH=./roles` in `t14-ansible-baseline.ps1`):

```bash
cd ~/Projects/dev/data-boar/ops/automation/ansible
ansible-playbook -i inventory.local.ini --ask-become-pass playbooks/t14-baseline.yml --diff
```

**Check mode (dry-run):** add `--check` before `--diff`.

### What the baseline installs (operator-facing)

- **`tmux`**: in `t14_baseline_packages` (terminal multiplexer; pairs with “sudo warm + tmux send-keys” workflows from the dev PC).
- **Bitwarden CLI (`bw`)**: **not** in Debian main — role `t14_bitwarden_cli` installs **`nodejs`** + **`npm`** from apt, then **`npm install -g @bitwarden/cli`**. Disable with `t14_install_bitwarden_cli: false` in playbook vars if you prefer another install method.

## Token-aware wrapper (Windows → SSH → Ansible on T14)

From Windows, the script runs Ansible **on the T14 over SSH** (`ssh -tt` so privilege escalation can use a TTY when needed). Ansible is invoked with **`--ask-become-pass`** (`-K`): you get a **BECOME password** prompt once **per `ansible-playbook` run** (so `-Apply` without `-SkipCheck` runs check then apply and may prompt twice). If your user has **passwordless sudo** for these tasks, pass **`-NoAskBecomePass`**.

```powershell
.\scripts\t14-ansible-baseline.ps1 -SshHost t14
```

To apply changes after a check pass:

```powershell
.\scripts\t14-ansible-baseline.ps1 -SshHost t14 -Apply
```

### Note (fewer prompts)

- **`-SkipCheck`** with **`-Apply`** skips the dry-run playbook and runs only the apply pass (one BECOME prompt).
- **Preferred end state** for unattended runs: a **restricted sudoers** rule (command-scoped) or **NOPASSWD** for the automation user, aligned with LAB-OP policy — then use **`-NoAskBecomePass`**.

## What this does (safe-default)

- Installs baseline packages (auditing, diagnostics, operator utilities; includes **`tmux`**, GUI terminal **`tilix`**, and common CLI tools)
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

## Troubleshooting

- **`apt-listbugs` / exit code 10 / `Failure running script /usr/bin/apt-listbugs`:** Debian’s `apt-listbugs` runs before installs and **aborts** when it finds bugs (e.g. a transitive package like `openipmi`). This is not an Ansible or hardware failure. Baseline plays use **`labop_debian_unattended_apt_environment`** from **`group_vars/all.yml`** (`APT_LISTBUGS_FRONTEND=none`; see `man apt-listbugs`) so unattended installs can finish. Interactive `apt` on the machine still uses your normal listbugs behavior.

- **Snapper missing / `Unit snapper.service could not be found` / no `/.snapshots`:** The **`t14_snapper`** role only installs Snapper and runs **`snapper create-config`** when **root (`/`) is btrfs** (detected with **`findmnt`**; the playbook uses **`head -n1`** because some layouts print **more than one** `FSTYPE` line). On **ext4**, Ansible cannot create btrfs snapshots — reinstall or migrate `/` to btrfs first. **LMDE with `subvol=@` on `/` is still btrfs**; if the role skipped before, older detection used **`stat`** and could mis-detect — re-run the baseline after updating this repo. Snapper uses **`snapper-timeline.timer`** / **`snapper-cleanup.timer`**, not `snapper.service`. Set **`t14_snapper_enabled: false`** to silence the role on non-btrfs hosts.

- **Snapper `setmntent failed` / `Detecting filesystem type failed`:** `snapper create-config` autodetection can fail under Ansible (and sometimes in minimal environments). The role passes **`-f btrfs`** (see **`t14_snapper_create_config_fstype`** in defaults). If it still fails, run **`snapper -c root create-config -f btrfs /`** manually once, then re-run the play.

- **UFW / `Failed to connect to system scope bus`:** The **`t14_ufw`** role applies **`ufw --force enable`** before touching **systemctl**, so the firewall should still activate. The follow-up **systemd** task is best-effort (`ignore_errors`). **`t14_fail2ban`** tries **`ansible.builtin.service`** first; if that fails (no D-Bus), it falls back to **`/etc/init.d/fail2ban`** or **`fail2ban-client`** so the play does not stop. Other roles use **`failed_when: false`** on **`service`** / **`systemd`** where appropriate. Fix the bus when you can, then re-run or run **`sudo systemctl enable --now …`** for native units. Check **`systemctl is-system-running`**, **`systemctl status dbus`**, and **`ls -l /run/dbus/system_bus_socket`**.

- **`org.freedesktop.systemd1` / `DBus.Error.TimedOut` / GUI cannot reboot / `snapper` D-Bus errors:** Often the system bus is up but **activation of systemd-backed services times out**. Journal may show **`Unknown group "power" in message bus configuration file`** — **`thermald`** ships **`/usr/share/dbus-1/system.d/org.freedesktop.thermald.conf`** with **`<policy group="power">`**; if **`/etc/group`** has no **`power`** line, fix with **`sudo groupadd -r power`** (then **`sudo systemctl reload dbus`** or reboot). After **`systemctl is-system-running`** is **`running`**, **`snapper create-config`** and normal **`systemctl`** should work again.

- **`Already up to date` but the T14 still runs old Ansible YAML:** The fix lives in **`git`** on **`main`** — confirm with **`git log -1 --oneline`** after **`git pull`**. If your dev machine had the change but **`git push`** did not run, the laptop will not see it.

## Important

Hardening is **contextual**. Before enabling any network-facing service, ensure the host is on the intended VLAN/segment and you understand the access model.

## Banners (figlet/toilet)

By default we generate a generic banner suitable for multiple hosts and environments:

- `/etc/banner.net`: full ASCII banner (best for SSH)
- `/etc/issue`, `/etc/issue.net`: short, non-sensitive banner (best for local console/tty)

To enable SSH banner, set `t14_banner_enable_sshd_banner=true` in your inventory/group vars.
