# Lab documentation map (LAB-PB vs LAB-OP)

**Purpose:** **Tracked** index so you can find **what lives where** after a busy sprint. **No** real hostnames, IPs, or credentials here — those stay **gitignored** under **`docs/private/`**.

**Português (Brasil):** [OPERATOR_LAB_DOCUMENT_MAP.pt_BR.md](OPERATOR_LAB_DOCUMENT_MAP.pt_BR.md)

---

## Taxonomy (short)

| Code | Meaning | Mnemonic |
| ---- | ------- | -------- |
| **LAB‑PB** | **Playbook** homelab — **public** guides for contributors and generic validation steps | **P**lay**B**ook · think **Pu**blic |
| **LAB‑OP** | **Operator** homelab — **your** real machines and access notes (**local only**) | **OP**erator — **name may be revisited** if confusing; see private **`LAB_TAXONOMY.md`** |

**Default in chat:** “homelab” usually means **LAB‑OP** for this workspace (agent reads **`docs/private/homelab/`**). Say **LAB‑PB** or **“playbook homelab”** when you mean **only** public docs.

---

## LAB‑PB — public (GitHub) — where to re-read

| Document | Role |
| -------- | ---- |
| **[HOMELAB_VALIDATION.md](HOMELAB_VALIDATION.md)** · [pt-BR](HOMELAB_VALIDATION.pt_BR.md) | Validation playbook, §9 multi-host, order **–1L** alignment |
| **[LAB_OP_MINIMAL_CONTAINER_STACK.md](LAB_OP_MINIMAL_CONTAINER_STACK.md)** · [pt-BR](LAB_OP_MINIMAL_CONTAINER_STACK.pt_BR.md) | Lab-op **Podman + k3s** minimal combo; §6 Wazuh, §7 Grafana/metrics/logs plan pointer |
| **[LMDE7_LAB-NODE-01_DEVELOPER_SETUP.md](LMDE7_LAB-NODE-01_DEVELOPER_SETUP.md)** · [pt-BR](LMDE7_LAB-NODE-01_DEVELOPER_SETUP.pt_BR.md) | ThinkPad **LAB-NODE-01 + LMDE 7**: concrete `apt`/`uv`/security steps |
| **[../plans/PLAN_LAB_OP_OBSERVABILITY_STACK.md](../plans/PLAN_LAB_OP_OBSERVABILITY_STACK.md)** · [pt-BR](../plans/PLAN_LAB_OP_OBSERVABILITY_STACK.pt_BR.md) | Optional lab-op sequence: Prometheus or Influx, Grafana, Loki or Graylog |
| **[CURSOR_UBUNTU_APPARMOR.md](CURSOR_UBUNTU_APPARMOR.md)** · [pt-BR](CURSOR_UBUNTU_APPARMOR.pt_BR.md) | Cursor on Ubuntu/Zorin with **AppArmor** (install, diagnose DENIED, `local/` overrides) |
| **[OS_COMPATIBILITY_TESTING_MATRIX.md](OS_COMPATIBILITY_TESTING_MATRIX.md)** | OS / musl / arch matrix for lab testing |
| **[PRIVATE_OPERATOR_NOTES.md](../PRIVATE_OPERATOR_NOTES.md)** · [pt-BR](../PRIVATE_OPERATOR_NOTES.pt_BR.md) | Policy: **`docs/private/`** layout, Git vs Cursor |
| **[../plans/PLANS_TODO.md](../plans/PLANS_TODO.md)** | Sequencing, **–1L** home lab smoke, tiers |
| **[../plans/TOKEN_AWARE_USAGE.md](../plans/TOKEN_AWARE_USAGE.md)** | Token-aware sessions, one-plan-per-session |
| **[DEPLOY.md](../deploy/DEPLOY.md)** · Docker **[README.md](../../scripts/docker/README.md)** | Deploy / image tags (generic) |
| **`AGENTS.md`** (repo root) · **`.cursor/rules/*.mdc`** | Agent defaults (homelab + private **`read_file`**) |
| **[../private.example/homelab/OPERATOR_RETEACH.md](../private.example/homelab/OPERATOR_RETEACH.md)** · [pt-BR](../private.example/homelab/OPERATOR_RETEACH.pt_BR.md) | **Template:** re-teach / gaps (**B1–B6**); **no** real hostnames — copy to **`docs/private/homelab/`** |
| **[../private.example/homelab/LAB_NETWORK_L3_DHCP_AND_CYBERSEC.md](../private.example/homelab/LAB_NETWORK_L3_DHCP_AND_CYBERSEC.md)** · [pt-BR](../private.example/homelab/LAB_NETWORK_L3_DHCP_AND_CYBERSEC.pt_BR.md) | **Template:** per-VLAN DHCP gateway/DNS, CyberSecure alignment, verification commands — copy to **`docs/private/homelab/`** and fill RFC1918 inventory locally |

---

## LAB‑OP — private (local, **not** on GitHub)

**Root:** **`docs/private/`** (see **`git check-ignore -v`**). **Homelab slice:** **`docs/private/homelab/`**.

| File (under `homelab/`) | Role |
| ----------------------- | ---- |
| **`LAB_TAXONOMY.md`** | LAB‑PB vs LAB‑OP; **LAB‑OP rename reminder** |
| **`OPERATOR_SYSTEM_MAP.md`** | Bird’s-eye: hardware + access matrix + software + Mermaid |
| **`AGENT_LAB_ACCESS.md`** | SSH, API port, `P:`, `scp` reports — **how** to reach LAB‑OP |
| **`OPERATOR_RETEACH.md`** | **Gaps** checklist (B1–B6) — fill when you have energy |
| **`HARDWARE_CATALOG.md`** | Hardware-focused summary (points to system map) |
| **`iso-inventory.md`** | ISO paths on lab Linux host |
| **`LAB_SECURITY_POSTURE.md`** | LAB‑OP **security inventory**: WAN posture, **sshd**/UFW/Fail2ban/nftables snapshots, **improvement backlog** (operator-maintained; not on GitHub) |
| **`LAB_SOFTWARE_INVENTORY.md`** | LAB‑OP **software/runtime matrix** (Python, Docker, Data Boar paths, **TBD** gaps); refresh with **`scripts/homelab-host-report.sh`** per Linux host |
| **`reports/*.log`** | Timestamped **`homelab-host-report.sh`** captures (kernel/sys/block sample + packages); use **`scripts/collect-homelab-report-remote.ps1`** from Windows or `tee` on-host — see **`docs/private.example/homelab/reports/README.md`** |
| **`lab-op-hosts.manifest.json`** | **Local only** (copy from **`docs/private.example/homelab/lab-op-hosts.manifest.example.json`**): SSH `Host` aliases + Linux **`repoPaths`** for **`scripts/lab-op-sync-and-collect.ps1`** |
| **`CREDENTIALS_AND_LAB_SECRETS.md`** (copy from **`docs/private.example/homelab/`**) | Policy for SNMP/API secrets: env / vault / gitignored `.env` — **never** chat paste |
| **`LAB_NETWORK_L3_DHCP_AND_CYBERSEC.md`** (copy from **`docs/private.example/homelab/`**) | Per-VLAN default gateway + DNS notes, CyberSecure honeypot row, verification commands — **no** live subnet table in git |

**Also private (repo root of `docs/private/`):** **`WHAT_TO_SHARE_WITH_AGENT.md`**, **`SOLAR_SYSTEM_NOTES.md`**, **`From Docker hub list of repositories.md`**, **`Learning_and_certs.md`**, **`CONTEXT_ACADEMIC_AND_FAMILY.md`** (spouse work + long-term academic links — **you** fill when ready), optional **`reports/*.xlsx`**, scratch **`.txt`** files — keep or migrate into **`homelab/`** over time.

**Template to bootstrap:** **`docs/private.example/`** → copy into **`docs/private/`**.

---

## Maturity + GTD (token-aware)

- **Small sessions:** one of — fill **`OPERATOR_RETEACH.md`**, or one **HOMELAB_VALIDATION** section on LAB‑OP, or one **PLANS_TODO** row. See **[TOKEN_AWARE_USAGE.md](../plans/TOKEN_AWARE_USAGE.md)**.
- **Software / toolColleague-Nns (LAB‑OP):** extend **`LAB_SOFTWARE_INVENTORY.md`** + **`OPERATOR_SYSTEM_MAP.md` §4** (and **`WHAT_TO_SHARE`** toolColleague-Nn table on WORKSTATION) when you add **Selenium**, extra **Python extras**, lab browsers, etc. — **no** secrets in files.
- **Tracked product plans** for **Selenium QA**, **synthetic data**, etc. remain in **`docs/plans/`**; LAB‑OP is **where you run** them.

---

## Related

- **[../PRIVATE_OPERATOR_NOTES.md](../PRIVATE_OPERATOR_NOTES.md)** §2 — full private path table
- **Homelab validation** “done” criteria: [HOMELAB_VALIDATION.md §12](HOMELAB_VALIDATION.md#12-when-you-are-done-with-a-lab-pass)
