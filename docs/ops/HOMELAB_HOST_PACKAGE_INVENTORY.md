# Homelab host package inventory (Data Boar)

**Purpose:** We **cannot** see what is installed on your machines from this repository or from the AI environment—no SSH to your LAN. This page lists what **Data Boar’s docs assume** on Linux, and gives **commands + a script** so **you** can capture inventory and (optionally) paste **redacted** output for a gap review.

**Related:** [HOMELAB_VALIDATION.md](HOMELAB_VALIDATION.md) · [TECH_GUIDE.md](../TECH_GUIDE.md) (install + connectors) · [SECURITY.md](../../SECURITY.md) (runtime prerequisites)

---

## 1. What the repo expects (baseline, not “what you have”)

These are **recommended** system packages for **Debian/Ubuntu / Zorin / Proxmox guests** when building native wheels and using common SQL drivers (from [TECH_GUIDE.md](../TECH_GUIDE.md) and [SECURITY.md](../../SECURITY.md)):

| Purpose                                 | Debian/Ubuntu packages (examples)                      |
| -------                                 | -----------------------------------                    |
| Python 3.12 + venv + headers            | `python3.12`, `python3.12-venv`, `python3.12-dev`      |
| Compiling some Python deps              | `build-essential`                                      |
| PostgreSQL client libs (psycopg2 build) | `libpq-dev`                                            |
| Generic TLS / FFI                       | `libssl-dev`, `libffi-dev`                             |
| ODBC (SQL Server and others via pyodbc) | `unixodbc-dev` (+ vendor ODBC driver where applicable) |

**Application Python deps** come from **`uv sync`** / `pyproject.toml` + **`uv.lock`**—not from `apt`. Optional extras:

- **NoSQL:** `uv pip install -e ".[nosql]"` (MongoDB, Redis)
- **Shares, compressed archives, big data, ML/DL, etc.:** see [TECH_GUIDE.md](../TECH_GUIDE.md) and `pyproject.toml` `[project.optional-dependencies]`

**Docker (lab §1.3–1.5):** `docker-ce` (or distro package), `containerd`; Swarm/Kubernetes are **your** choice—Data Boar only needs `docker build` / `docker run` (or equivalent in VM).

**Not in repo as hard deps:** Ansible, OpenTofu, Terraform, Prometheus, SonarQube, Lynis—these are **operator tools** you install when you run those workflows.

---

## 2. Optional system bits by connector (install only if you use that target)

| Connector                  | Typical extra system setup                                                                                                                  |
| ---------                  | --------------------------                                                                                                                  |
| **Oracle**                 | Oracle Instant Client + env (`LD_LIBRARY_PATH`) per Oracle docs                                                                             |
| **SQL Server**             | Microsoft ODBC Driver for Linux + `unixodbc`                                                                                                |
| **Snowflake / other ODBC** | Vendor ODBC driver + `unixodbc`                                                                                                             |
| **Void / Alpine (musl)**   | Same logical deps; package names differ (`xbps-install` / `apk add`); you may need more **build** packages for `cryptography`, `lxml`, etc. |

If you tell us **which connectors** you actually scan in lab, we can narrow the list.

---

## 2.5 Optional developer toolchains (Go, Rust, Zig, Odin, Homebrew)

**Data Boar itself is Python 3.12+** (`pyproject.toml` / `uv`). **Go, Rust, Zig, Odin, and Linuxbrew do not** need to be installed for **§1.1–1.2**, **Docker** builds, or normal connector tests. They are **nice for you** as a developer and for **adjacent** repos or experiments.

| Toolchain                    | Role vs this repo                                                                                                                                                                                                                                       |
| ---------                    | -----------------                                                                                                                                                                                                                                       |
| **Go**                       | Useful for **sidecars**, small CLIs, or infra tools; **no** Go source in Data Boar today.                                                                                                                                                               |
| **Rust**                     | Same; **only** becomes relevant here if we ever ship a **Rust extension** for Python (**PyO3** / **maturin**)—**not** on the current critical path. Some **Python wheels** ship prebuilt binaries; you rarely need `rustc` unless building from source. |
| **Zig / Odin**               | Great for **systems learning** and personal tools; **no** expectation for Data Boar operators.                                                                                                                                                          |
| **Homebrew** (**linuxbrew**) | Parallel to **`apt`**/**`xbps`**; can install **newer** dev tools on distros with stale packages—keep mental track of **two** package worlds (`brew` vs distro) to avoid PATH confusion.                                                                |

**When extra languages *would* make sense for the product:** a **proven** bottleneck (e.g. a hot path measured in prod), a **security** boundary (small audited binary), or a **mandatory** integration SDK only available in native code—until then, **stay Python-first** to match CI, docs, and onboarding.

**Quick capture (optional):** `go version`, `rustc --version`, `zig version`, `odin version`, `brew --version` — reported by `homelab-host-report.sh` in the **optional toolchains** block.

---

## 3. Capture inventory on each host (manual one-liners)

Run on **each** machine (Proxmox **node**, each **VM**, laptop, Pi, etc.). **Redact** IPs, hostnames, and user paths before sharing in chat.

## OS / kernel

```bash
cat /etc/os-release 2>/dev/null; uname -a
```

## CPU / memory (rough capacity planning)

```bash
nproc 2>/dev/null; free -h 2>/dev/null
```

## Python / uv

```bash
command -v python3 && python3 --version
command -v uv && uv --version
```

## Docker

```bash
command -v docker && docker version
docker info 2>/dev/null | head -30   # optional; may show swarm — redact if needed
```

## Bitwarden CLI (optional)

```bash
command -v bw && bw --version
```

## Debian/Ubuntu: installed packages (filtered)

```bash
dpkg-query -W -f='${Package}\t${Version}\n' \
  python3.12 python3.12-venv python3.12-dev build-essential \
  libpq-dev libssl-dev libffi-dev unixodbc-dev \
  docker-ce docker.io containerd lynis bitwarden-cli 2>/dev/null || true
# Full list (large): dpkg -l > dpkg-l.txt
```

## Void Linux

```bash
xbps-query -l | grep -E 'python3|docker|uv|build-essential|openssl|lynis' || xbps-query -l
```

## Alpine

```bash
apk info -e python3 py3-pip docker docker-cli 2>/dev/null; apk list -I 2>/dev/null | head -80
```

---

## 4. Automated bundle script (Linux)

From the **repo root** on a machine that has the repo (or copy the script only):

```bash
bash scripts/homelab-host-report.sh
```

The script prints **`bw` (Bitwarden CLI)** when it is on **`PATH`** (path + `bw --version`). It does **not** run `bw status` (that can include your **email** in JSON—run manually if needed, redact before sharing).

Save stdout to a file, **redact**, then share if you want a structured review.

---

## 5. What to send back (if you want “do I miss anything?”)

1. **Host role** (e.g. primary Zorin, musl mini-PC, Pi, Proxmox guest Debian 12).
1. **Output** of `homelab-host-report.sh` (redacted) **or** the one-liners above.
1. **Which Data Boar features you use** on that host: filesystem only / Postgres / MSSQL / Docker image only / ML / DL / etc.

Then we can say “install X” or “optional Y for connector Z”—without guessing.

---

## 6. Proxmox-specific note

- **Hypervisor (pve):** inventory the **node** separately from each **VM/LXC**.
- **Guests:** treat each Linux guest like any other row in [HOMELAB_VALIDATION §9](HOMELAB_VALIDATION.md#9-multi-host-linux-optional-matrix-dns-ssh-different-distros)—Python/`uv`/Docker are installed **inside** the guest unless you deliberately run from the host.

---

**Português (Brasil):** [HOMELAB_HOST_PACKAGE_INVENTORY.pt_BR.md](HOMELAB_HOST_PACKAGE_INVENTORY.pt_BR.md)
