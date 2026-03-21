# Windows dev laptop: extra WSL distros and lab matrix

**Purpose:** Use **one physical Windows laptop** as **several Linux-like environments**: **WSL2** guests add cheap rows to the [HOMELAB_VALIDATION.md](HOMELAB_VALIDATION.md) §9 matrix **without** extra hardware—**if** **disk**, **RAM**, and **CPU** stay comfortable.

**Related:** [HOMELAB_VALIDATION.md](HOMELAB_VALIDATION.md) · [HOMELAB_HOST_PACKAGE_INVENTORY.md](HOMELAB_HOST_PACKAGE_INVENTORY.md) · [TECH_GUIDE.md](../TECH_GUIDE.md) · [DOCKER_SETUP.md](../DOCKER_SETUP.md)

**Hardware picture (operator):** Plan for **three laptops** in total: **(1)** Windows + WSL **dev**, **(2)** **native Linux** lab, **(3)** **optional spare** laptop. **Exact models** live in **gitignored** `docs/private/homelab/` ([PRIVATE_OPERATOR_NOTES.md](../PRIVATE_OPERATOR_NOTES.md)). WSL extras apply to **(1)** only.

---

## 1. What you already get without new distros

| Layer                             | Typical use for Data Boar                                                                                                             |
| -----                             | -------------------------                                                                                                             |
| **Windows** (native)              | **Go / Rust / Zig / Odin** on `PATH`, **Docker Desktop**, editors, browser                                                            |
| **WSL2 Debian** (or your default) | **`uv sync`**, **`pytest`**, closest to **Linux** docs; keep repo clone under **Linux filesystem** (`~/...`) not `/mnt/c/...` for I/O |
| **Docker Desktop → WSL2**         | **`docker-desktop`** distro in `wsl -l -v`; builds/runs **Linux containers**                                                          |

That is already **two** Linux-ish backends (Debian + Docker’s utility distro) plus Windows native.

---

## 2. When to add *more* WSL distros

**Do add** if you want **targeted** checks without new metal:

- **Ubuntu 22.04 / 24.04** — glibc parity with **Zorin/Ubuntu** docs; good “second opinion” vs Debian Trixie/sid.
- **openSUSE** or **Fedora** (if available in `wsl --list --online`) — lighter touch on **RPM**/`dnf` family before a full **Alma/Fedora** VM.

## Costs:

- **Disk:** each distro is a **VHDX** (often **2–15+ GB** as you install packages); check free space on **`C:`**.
- **RAM:** all WSL2 VMs share host memory; cap with **`%UserProfile%\.wslconfig`** (see §4).
- **Operator time:** duplicate **`uv sync`**, **Docker** setup per distro if you run §1 there.

**Skip** if **`C:`** is tight or **16 GB RAM** feels tight with **Docker + IDE + browser** already.

---

## 3. Install another distro (examples)

```powershell
wsl --list --online          # choose a name from the list
wsl --install -d Ubuntu-24.04
```

After first boot: **`sudo apt update`**, install **`git`**, **`python3.12`** (or distro default + see [OS_COMPATIBILITY_TESTING_MATRIX.md](OS_COMPATIBILITY_TESTING_MATRIX.md)), **`uv`**, then clone the repo **inside** that distro and run [HOMELAB_VALIDATION.md](HOMELAB_VALIDATION.md) **§1.1–1.2** (+ **§2**).

---

## 4. Limit WSL2 resource use (`.wslconfig`)

Create or edit **`C:\Users\<you>\.wslconfig`** to avoid starving Windows when running **multiple** distros + Docker:

```ini
[wsl2]
memory=8GB
processors=4
swap=8GB
```

Tune to **your** machine (e.g. **16–40 GB RAM** class laptops). **Restart WSL:** `wsl --shutdown` then open a distro again.

---

## 5. Inventory script (this PC)

From repo root:

```powershell
pwsh -File scripts/windows-dev-report.ps1
```

Captures **`wsl -l -v`**, **Go/Rust/uv/Docker/zig/odin`** when on **`PATH`**, **vswhere** output (**`-prerelease`** so **Visual Studio Insiders** shows up), and **`C:`** free space. **Redact** hostnames if you paste output.

---

## 6. Relationship to Data Boar

- **Production runtime** of the app remains **Python 3.12+** in **Linux containers** or **Linux/Windows** venv—**not** Go/Rust unless we add a **native** component later.
- **Extra WSL distros** = **compatibility confidence** and **practice** for [§9](HOMELAB_VALIDATION.md#9-multi-host-linux-optional-matrix-dns-ssh-different-distros); they **do not** replace **real** second hardware (Latitude, Pi, Proxmox guest) for **NIC/firewall/Swarm** behaviour.

---

## 7. See also

- [HOMELAB_HOST_PACKAGE_INVENTORY.md §2.5](HOMELAB_HOST_PACKAGE_INVENTORY.md#25-optional-developer-toolchains-go-rust-zig-odin-homebrew) — Go/Rust/Zig/Odin are **optional** for the Python app.

**Português (Brasil):** [WINDOWS_WSL_MULTI_DISTRO_LAB.pt_BR.md](WINDOWS_WSL_MULTI_DISTRO_LAB.pt_BR.md)
