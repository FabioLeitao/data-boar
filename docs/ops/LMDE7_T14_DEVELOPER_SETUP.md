# ThinkPad T14 + LMDE 7 — developer setup (Data Boar)

**Português (Brasil):** **canonical concrete steps** — **[LMDE7_T14_DEVELOPER_SETUP.pt_BR.md](LMDE7_T14_DEVELOPER_SETUP.pt_BR.md)** (§0–§8: updates, security, Python/`uv`/pytest, optional Podman/Docker, final checklist; **§9** = related links). **Prerequisite:** LMDE 7 must **already boot** on the T14; **USB installer / disk partitioning** are **out of scope** here (see Mint LMDE + Lenovo UEFI docs), then start at **§0** in the pt-BR file.

**Summary:** LMDE 7 is **Debian 13–based**; use the same `apt` package names as [TECH_GUIDE.md](../TECH_GUIDE.md) (Python 3.12, `build-essential`, `libpq-dev`, `libssl-dev`, `libffi-dev`, `unixodbc-dev`), install **`uv`**, run **`uv sync`** / **`pytest`** in the repo, optional **Podman** per [LAB_OP_MINIMAL_CONTAINER_STACK.md](LAB_OP_MINIMAL_CONTAINER_STACK.md). Security baseline: **`ufw`**, **`unattended-upgrades`**, **`fwupd`** for ThinkPad firmware.

For firewall, SSH, and Data Boar port **8088** notes, follow the Portuguese doc (operator LAN subnets are site-specific).

**After the laptop is ready:** optional lab-op instrumentation sequence (Grafana, Prometheus, Loki, Graylog, Influx) — **[PLAN_LAB_OP_OBSERVABILITY_STACK.md](../plans/PLAN_LAB_OP_OBSERVABILITY_STACK.md)**.
