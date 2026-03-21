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
| **[OS_COMPATIBILITY_TESTING_MATRIX.md](OS_COMPATIBILITY_TESTING_MATRIX.md)** | OS / musl / arch matrix for lab testing |
| **[PRIVATE_OPERATOR_NOTES.md](../PRIVATE_OPERATOR_NOTES.md)** · [pt-BR](../PRIVATE_OPERATOR_NOTES.pt_BR.md) | Policy: **`docs/private/`** layout, Git vs Cursor |
| **[../plans/PLANS_TODO.md](../plans/PLANS_TODO.md)** | Sequencing, **–1L** home lab smoke, tiers |
| **[../plans/TOKEN_AWARE_USAGE.md](../plans/TOKEN_AWARE_USAGE.md)** | Token-aware sessions, one-plan-per-session |
| **[DEPLOY.md](../deploy/DEPLOY.md)** · Docker **[README.md](../../scripts/docker/README.md)** | Deploy / image tags (generic) |
| **`AGENTS.md`** (repo root) · **`.cursor/rules/*.mdc`** | Agent defaults (homelab + private **`read_file`**) |

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

**Also private (repo root of `docs/private/`):** **`WHAT_TO_SHARE_WITH_AGENT.md`**, **`SOLAR_SYSTEM_NOTES.md`**, **`From Docker hub list of repositories.md`**, **`Learning_and_certs.md`**, **`CONTEXT_ACADEMIC_AND_FAMILY.md`** (spouse work + long-term academic links — **you** fill when ready), optional **`reports/*.xlsx`**, scratch **`.txt`** files — keep or migrate into **`homelab/`** over time.

**Template to bootstrap:** **`docs/private.example/`** → copy into **`docs/private/`**.

---

## Maturity + GTD (token-aware)

- **Small sessions:** one of — fill **`OPERATOR_RETEACH.md`**, or one **HOMELAB_VALIDATION** section on LAB‑OP, or one **PLANS_TODO** row. See **[TOKEN_AWARE_USAGE.md](../plans/TOKEN_AWARE_USAGE.md)**.
- **Software / toolchains (LAB‑OP):** extend **`OPERATOR_SYSTEM_MAP.md` §4** (and **`WHAT_TO_SHARE`** toolchain table on L14) when you add **Selenium**, extra **Python extras**, lab browsers, etc. — **no** secrets in files.
- **Tracked product plans** for **Selenium QA**, **synthetic data**, etc. remain in **`docs/plans/`**; LAB‑OP is **where you run** them.

---

## Related

- **[../PRIVATE_OPERATOR_NOTES.md](../PRIVATE_OPERATOR_NOTES.md)** §2 — full private path table  
- **Homelab validation** “done” criteria: [HOMELAB_VALIDATION.md §12](HOMELAB_VALIDATION.md#12-when-you-are-done-with-a-lab-pass)
