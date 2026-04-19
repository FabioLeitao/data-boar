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

   **Optional collections** (only if you set **`t14_toolchain_acl_extra_groups`** for role **`t14_toolchain_restrict`** — POSIX ACLs via **`ansible.posix.acl`**):

   ```bash
   ansible-galaxy collection install -r collections/requirements.yml
   ```

3. **Inventory:** from `ops/automation/ansible/`, copy the example and point `[t14]` at this host. The Windows helper script **rewrites** `[t14]` to `localhost` + `ansible_connection=local` when you run Ansible **on the T14 over SSH** (same pattern as `t14-ansible-baseline.ps1`).

   ```bash
   cd ~/Projects/dev/data-boar/ops/automation/ansible
   cp -f inventory.example.ini inventory.local.ini
   # Edit [t14] if you run from a different machine than localhost; for local runs use localhost as in the script.
   ```

### Run order

1) Create `inventory.local.ini` (see above).

2) **Preflight (recommended):** from the **repo root**, run **`scripts/t14-ansible-preflight.sh`** — checks Ansible, inventory, sudo, **`/etc/apt/sources.list.d/docker.list`** mode, and **`bw`**. Fixes many “walking in circles” issues before a long playbook run.

```bash
cd ~/Projects/dev/data-boar
bash scripts/t14-ansible-preflight.sh
```

**`bw` missing / `command-not-found` suggests `bundlewrap`:** run **`bash scripts/t14-bitwarden-cli-bootstrap.sh`** from the repo root (fixes **`docker.list`** perms if needed, installs **Node/npm**, **`npm install -g @bitwarden/cli`**, fixes **`@bitwarden`** permissions, writes **`/etc/profile.d/zz-local-bin.sh`** and the **tmux** **`PATH`** block in **`/etc/bash.bashrc`**). Then **`source /etc/bash.bashrc`** or open a **new tmux pane** and run **`bw login`**.

3) **Warm sudo** on the target (one interactive password if needed):

```bash
sudo -v
```

4) Run the baseline playbook **from** `ops/automation/ansible` (this directory has `ansible.cfg` with `roles_path = roles`, same as `ANSIBLE_ROLES_PATH=./roles` in `t14-ansible-baseline.ps1`):

```bash
cd ~/Projects/dev/data-boar/ops/automation/ansible
ansible-playbook -i inventory.local.ini --ask-become-pass playbooks/t14-baseline.yml --diff
```

**Running ON the T14 (not from Windows/SSH):** `inventory.local.ini` must use **`localhost ansible_connection=local`** under `[t14]` (see **`inventory.example.ini`** pattern **A**). If `[t14]` points at SSH while you are already on the laptop, or connection is ambiguous, become/sudo prompts can misbehave.

**Check mode (dry-run):** add `--check` before `--diff`.

#### BECOME password: `Duplicate become password prompt` / `Sorry, try again`

- **Wrong sudo password:** `sudo` prints **`Sorry, try again.`**; on some Ansible versions the next prompt then fails with **`Duplicate become password prompt encountered`**. Fix: run **`sudo -v`** and confirm the password **outside** Ansible, then re-run the playbook (type the BECOME password carefully once).
- **Non-interactive alternative (same shell only):** `ANSIBLE_BECOME_PASS='yourpassword' ansible-playbook ...` **without** `--ask-become-pass` — avoids the interactive prompt bug; **risk:** shell history and process list — prefer **`read -s`** + export in a throwaway shell, or **NOPASSWD** sudo for your user (see **`t14-ansible-baseline.ps1 -NoAskBecomePass`** when applicable).

### What the baseline installs (operator-facing)

- **`tmux`**: in `t14_baseline_packages` (terminal multiplexer; pairs with “sudo warm + tmux send-keys” workflows from the dev PC).
- **Bitwarden CLI (`bw`)**: **not** in Debian main — role `t14_bitwarden_cli` installs **`build-essential`** + **`nodejs`** + **`npm`** from apt (per [Bitwarden CLI help](https://bitwarden.com/help/cli/), Linux **`npm`** may need the build toolchain), then **`npm install -g @bitwarden/cli`**. If **`/etc/apt/sources.list.d/docker.list`** already exists (e.g. partial Docker CE setup), the role sets **`0644`** **`root:root`** so user-space apt helpers do not hit **Errno 13**. After install, **`bw`** is under **`/usr/local/bin`**; the role **asserts** that path exists, then runs **`bw --version`** as the resolved operator user. It also adds **`/etc/profile.d/zz-local-bin.sh`** and a **`blockinfile`** in **`/etc/bash.bashrc`** so **`tmux`** and other **non-login** interactive shells see **`PATH`**. Debian’s **`command-not-found`** may wrongly suggest **`bundlewrap`** for `bw` — ignore; use **`/usr/local/bin/bw`** or open a **new tmux pane** after the playbook. Disable the role with `t14_install_bitwarden_cli: false` if you use another install method.
- **Operator groups + `tshark`**: role **`t14_operator_supplementary_groups`** (after Docker CE) installs **`tshark`**, adds the **resolved operator login** (see **`t14_operator_target_user`** in **`group_vars/all.yml`**) to **`docker`**, **`wireshark`**, **`dialout`**, **`plugdev`**, **`systemd-journal`**, then runs **`grpconv`** and **`grpck -r`** (set **`t14_operator_grpck_strict: false`** if **`grpck`** fails on a host with pre-existing group-file issues). On **`localhost`** or when running **`sudo ansible-playbook`**, set **`t14_operator_target_user=yourlogin`** in **`[t14:vars]`** so groups are not applied to **`root`** by mistake.
- **Toolchain restriction (`comp`)**: role **`t14_toolchain_restrict`** is **off by default**. When **`t14_toolchain_restrict_enabled=true`**, it ensures group **`comp`** (configurable), finds matching **`/usr/bin/x86_64-linux-gnu-*`** compiler/tool binaries, and applies **`ansible.builtin.file`** (`root` + group, mode **`0754`**, **`follow: true`**). Optional **`t14_toolchain_acl_extra_groups`** adds extra **POSIX ACL** group lines (**`rx`**) via **`ansible.posix.acl`** — install **`collections/requirements.yml`** first. **`apt`** upgrades can restore vendor modes; re-run the playbook after compiler package updates. Add human users to **`comp`** separately (e.g. **`usermod -aG comp`**), or extend automation in private inventory.

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
- Sets host banners (`/etc/issue`, `/etc/issue.net`, `/etc/banner.net`) via `figlet`/`toilet`; **`t14_sshd_labop`** adds **`Banner /etc/banner.net`** in **`sshd_config.d`** when that file exists (after **`t14_banners`**)
- Installs `lynis` and writes a baseline `/etc/lynis/default.prf` with **comment-only** skip suggestions (opt-in by uncommenting)
- Enables firewall defaults (UFW) where appropriate
- Enables and configures `fail2ban` (SSH only) with conservative settings (optional `ignoreip` via inventory)
- Installs `aide` and `auditd` with a reviewable baseline (host-specific exceptions should stay private)
- Optional: enables zram-based swap (host-dependent sizing; opt-in)
- **`t14_sshd_labop`**: sshd hardening via **`/etc/ssh/sshd_config.d/90-labop-hardening.conf`** (validated with **`sshd -t`** before reload). Default **`t14_sshd_profile=dev`** keeps **TCP + agent forwarding** for daily work; set **`strict`** for a Latitude-style lockdown (no forwarding). **`PasswordAuthentication`** is **not** forced by default — set **`t14_sshd_password_authentication=no`** in inventory only after pubkey access is confirmed.
- **`t14_login_defs`**: **`/etc/login.defs`** — **`UMASK`**, **`HOME_MODE`**, **`PASS_*`**, **`LOGIN_RETRIES`**, **`ENCRYPT_METHOD SHA512`**, **`SHA_CRYPT_*` rounds** (override in inventory if policy differs).
- **`t14_shell_umask`**: **`umask 027`** in **`/etc/profile`** and **`/etc/bash.bashrc`** (marked block).
- **`t14_limits_labop`**: **`/etc/security/limits.d/50-labop.conf`** — core dumps off (**`* soft/hard core 0`**).
- **Docker CE** (official repo) **+ Compose plugin** are **on by default** in **`t14-baseline.yml`** so **`docker`** and **`ctop`** work after one playbook run. **`t14_operator_supplementary_groups`** runs after **`t14_docker_ce`**: installs **`tshark`**, adds the **resolved operator login** to **`docker`** (when Docker CE is enabled), **`wireshark`**, **`dialout`**, **`plugdev`**, **`systemd-journal`**, and merges **`t14_operator_group_users_extra`** plus legacy **`t14_docker_socket_group_users_extra`**. Resolution order: non-empty **`t14_operator_target_user`**, else **`SUDO_USER`**, else **`ansible_user`** / **`ansible_user_id`**. **Log out and back in** (or **`newgrp`** with the new group name in the current shell) so new groups apply. Disable the whole block with **`t14_operator_groups_enabled: false`**. **Swarm** is **initialized by default**; set **`t14_docker_swarm_init: false`** to skip. Set **`t14_install_docker_ce: false`** to skip Docker entirely. **Podman** and **k3s** stay **opt-in**.

## Post-automation validation (checklist)

After a `CHECK` + `APPLY`, run the quick validation checklist:

- `POST_AUTOMATION_VALIDATION.pt_BR.md`

## Troubleshooting

- **`Duplicate become password prompt` / `Sorry, try again` (Gathering Facts):** Usually **wrong sudo password** on the first prompt, then Ansible gets stuck. Confirm with **`sudo -v`**, use **`inventory.local.ini`** pattern **`localhost ansible_connection=local`** when running **on** the T14, and see **BECOME password** above.

- **`Permission denied: '/etc/apt/sources.list.d/docker.list'`** (often Python **`WARNING:root:`**): The list file should be **`0644`** **`root:root`**. The **`t14_docker_ce`** role enforces that after adding the repo; if the file was created elsewhere, run **`sudo chmod 644 /etc/apt/sources.list.d/docker.list`** or re-run the playbook.

- **`apt-listbugs` / exit code 10 / `Failure running script /usr/bin/apt-listbugs`:** Debian’s `apt-listbugs` runs before installs and **aborts** when it finds bugs (e.g. a transitive package like `openipmi`). This is not an Ansible or hardware failure. Baseline plays use **`labop_debian_unattended_apt_environment`** from **`group_vars/all.yml`** (`APT_LISTBUGS_FRONTEND=none`; see `man apt-listbugs`) so unattended installs can finish. Interactive `apt` on the machine still uses your normal listbugs behavior.

- **Snapper missing / `Unit snapper.service could not be found` / no `/.snapshots`:** The **`t14_snapper`** role only installs Snapper and runs **`snapper create-config`** when **root (`/`) is btrfs** (detected with **`findmnt`**; the playbook uses **`head -n1`** because some layouts print **more than one** `FSTYPE` line). On **ext4**, Ansible cannot create btrfs snapshots — reinstall or migrate `/` to btrfs first. **LMDE with `subvol=@` on `/` is still btrfs**; if the role skipped before, older detection used **`stat`** and could mis-detect — re-run the baseline after updating this repo. Snapper uses **`snapper-timeline.timer`** / **`snapper-cleanup.timer`**, not `snapper.service`. Set **`t14_snapper_enabled: false`** to silence the role on non-btrfs hosts.

- **Snapper `setmntent failed` / `Detecting filesystem type failed`:** `snapper create-config` autodetection can fail under Ansible (and sometimes in minimal environments). The role passes **`-f btrfs`** (see **`t14_snapper_create_config_fstype`** in defaults). If it still fails, run **`snapper -c root create-config -f btrfs /`** manually once, then re-run the play.

- **Snapper `TIMELINE_*` must be `yes`/`no`:** Per **`snapper-configs(5)`**, **`TIMELINE_CREATE`** and **`TIMELINE_CLEANUP`** accept **`yes`** or **`no`** only. If a past run wrote **`TRUE`**, fix the lines in **`/etc/snapper/configs/<name>`** or re-run the baseline after updating this repo.

- **UFW / `Failed to connect to system scope bus`:** The **`t14_ufw`** role applies **`ufw --force enable`** before touching **systemctl**, so the firewall should still activate. The follow-up **systemd** task is best-effort (`ignore_errors`). **`t14_fail2ban`** tries **`ansible.builtin.service`** first; if that fails (no D-Bus), it falls back to **`/etc/init.d/fail2ban`** or **`fail2ban-client`** so the play does not stop. Other roles use **`failed_when: false`** on **`service`** / **`systemd`** where appropriate. Fix the bus when you can, then re-run or run **`sudo systemctl enable --now …`** for native units. Check **`systemctl is-system-running`**, **`systemctl status dbus`**, and **`ls -l /run/dbus/system_bus_socket`**.

- **`org.freedesktop.systemd1` / `DBus.Error.TimedOut` / GUI cannot reboot / `snapper` D-Bus errors:** Often the system bus is up but **activation of systemd-backed services times out**. Journal may show **`Unknown group "power" in message bus configuration file`** — **`thermald`** ships **`/usr/share/dbus-1/system.d/org.freedesktop.thermald.conf`** with **`<policy group="power">`**; if **`/etc/group`** has no **`power`** line, fix with **`sudo groupadd -r power`** (then **`sudo systemctl reload dbus`** or reboot). After **`systemctl is-system-running`** is **`running`**, **`snapper create-config`** and normal **`systemctl`** should work again.

- **`Already up to date` but the T14 still runs old Ansible YAML:** The fix lives in **`git`** on **`main`** — confirm with **`git log -1 --oneline`** after **`git pull`**. If your dev machine had the change but **`git push`** did not run, the laptop will not see it.

- **`bw` / Bitwarden CLI: command not found or Permission denied:** Global **`npm install -g @bitwarden/cli`** puts **`bw`** under **`/usr/local/bin`**. If **`bw`** is missing from **`PATH`**, open a new login shell (role installs **`/etc/profile.d/zz-local-bin.sh`**). **`t14_bitwarden_cli`** also fixes **`@bitwarden`** permissions under **`/usr/local/lib/node_modules`** so your user can execute **`bw`** — **re-run the baseline** after pulling this repo; do not rely on one-off **`chmod`**.

- **`ctop` / `docker: command not found`:** If you disabled Docker in inventory, re-enable **`t14_install_docker_ce: true`** or run the **`t14_docker_ce`** role. The default **`t14-baseline.yml`** enables Docker CE; **`docker.io`** from Debian main is **not** used by this role.

- **`docker.service` fails / journal: `live-restore daemon configuration is incompatible with swarm mode`:** The baseline enables **Swarm** by default (`t14_docker_swarm_init: true`). **`live-restore: true`** in **`/etc/docker/daemon.json`** cannot be combined with Swarm (Docker 29+). Role defaults no longer set **`live-restore`**; if an older run wrote it, remove the key or set **`live-restore: false`**, then **`sudo systemctl restart docker`**. Alternative: **`t14_docker_swarm_init: false`** and leave Swarm if you only need **`docker compose`** (see playbook vars).

- **`permission denied` on **`docker.sock`**, **`ctop`**, **`tshark` / capture:** Role **`t14_operator_supplementary_groups`** adds the **resolved operator login** (override with **`t14_operator_target_user`**) to **`docker`**, **`wireshark`**, and other standard groups (see defaults). **Log out and back in** after the play. Extra users: **`t14_operator_group_users_extra`** (or legacy **`t14_docker_socket_group_users_extra`**). Disable all supplementary group membership with **`t14_operator_groups_enabled: false`**. Skip **`tshark`** install with **`t14_operator_install_tshark: false`**. Add **`kvm`**, **`libvirt`**, etc. via **`t14_operator_supplementary_group_names_extra`** only after those groups exist (install **`qemu-system-x86`** / **`libvirt-clients`** first).

- **`docker swarm init` / advertise address on multi-NIC hosts:** The role runs plain **`docker swarm init`** when Swarm state is **`inactive`**. If initialization fails because Docker cannot pick an address, set **`t14_docker_swarm_init: false`** and initialize once with **`docker swarm init --advertise-addr <stable-ip>`**, or extend the role privately with **`--advertise-addr`** (not in baseline).

- **`sshd -t` fails after updating `t14_sshd_labop`:** The merged config is invalid (conflicting directives, bad path in **`Banner`**, etc.). Fix the drop-in or main **`sshd_config`**, then re-run. Temporarily set **`t14_sshd_labop_enable=false`** only to unblock, then restore.

- **`gigi Release` / Docker apt on **LMDE**:** **`ansible_distribution_release`** is a **Mint** codename (**`gigi`**, **`faye`**) while **`download.docker.com/linux/debian`** only publishes **Debian** suites. The **`t14_docker_ce`** role maps **`gigi` → `trixie`** and **`faye` → `bookworm`**. Override with **`t14_docker_apt_dist_override`** (e.g. **`trixie`**) if your base Debian drifts. If **`apt update`** also warns about **`packages.linuxmint.com`** InRelease, that is separate from Docker — check network, mirrors, or Mint updates.

- **`grpck` fails:** The **`t14_operator_supplementary_groups`** role runs **`grpconv`** then **`grpck -r`**. Fix **`/etc/group`** / **`/etc/gshadow`** inconsistencies on the host, or set **`t14_operator_grpck_strict: false`** to skip failing the play (not recommended). Disable both with **`t14_operator_run_grpconv_grpck: false`**.

## Important

Hardening is **contextual**. Before enabling any network-facing service, ensure the host is on the intended VLAN/segment and you understand the access model.

## Banners (figlet/toilet)

By default we generate a generic banner suitable for multiple hosts and environments:

- `/etc/banner.net`: full ASCII banner (best for SSH)
- `/etc/issue`, `/etc/issue.net`: short, non-sensitive banner (best for local console/tty)

To enable SSH banner, set `t14_banner_enable_sshd_banner=true` in your inventory/group vars.
