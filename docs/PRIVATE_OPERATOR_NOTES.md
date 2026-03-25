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

**Cursor / agents:** **`docs/private/`** is **workspace-local context** shared with the assistant on this machine: it is **excluded from Git / GitHub only**, not “hidden until `@`.” Agents should **`read_file`** paths under **`docs/private/`** when homelab, operator layout, or **`AGENT_LAB_ACCESS`** topics apply—**no** requirement to **`@`-mention** or keep files open (unless you add **`docs/private/`** to **`.cursorignore`**). Still **disclosure to Cursor’s product** per their terms; avoid plaintext production secrets in files.

---

## 2. Recommended layout (you create this locally)

Copy the **tracked template** from **`docs/private.example/`** into **`docs/private/`** (or create the same folders by hand). **Conventional Commits:** changes to **those tracked** policy/template files use scope **`docs(private-layout):`**; **LAB-OP** specifics stay **only** under **`docs/private/`** and never ship in **`private-layout`** commits.

| Path (local only)                                 | Use                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                           |
| -----------------                                 | ---                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                           |
| **`docs/private/homelab/`**                       | **Real** homelab catalog: hostnames, RFC1918 IPs, SSH users, `homelab-host-report.sh` outputs, UPS load lists, HVAC model numbers, UniFi VLAN IDs, solar logger IP, **redacted** API samples. **`AGENT_LAB_ACCESS.md`** — operator directive for LAN/DNS/SSH/API; agents **read it when relevant** (no **`@`** required).                                                                                                                                                                                                                                                     |
| **`docs/private/homelab/validation-log.md`**      | Dated §1–§2 pass/fail per host (optional filename).                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                           |
| **`docs/private/homelab/solar.md`**               | Inverter/datalogger models, portal names, **references** to Bitwarden for keys (not plaintext passwords).                                                                                                                                                                                                                                                                                                                                                                                                                                                                     |
| **`docs/private/homelab/iso-inventory.md`**       | Optional: list of `.iso` / `.img` paths (e.g. under `~/Downloads/iso` on a lab machine). **Captured by you** (SSH `ls`, `find`, or script output pasted/edited here)—not stored on GitHub.                                                                                                                                                                                                                                                                                                                                                                                    |
| **`docs/private/homelab/HARDWARE_CATALOG.md`**    | **Bird’s-eye** hardware / roles / power / solar summary merged from other private notes; **gaps** section for unchecked items.                                                                                                                                                                                                                                                                                                                                                                                                                                                |
| **`docs/private/homelab/LAB_TAXONOMY.md`**        | **LAB‑OP** (operator real homelab) vs **LAB‑PB** (public playbook) — use in chat to disambiguate.                                                                                                                                                                                                                                                                                                                                                                                                                                                                             |
| **`docs/private/homelab/OPERATOR_SYSTEM_MAP.md`** | **Master chart:** hardware + accessibility matrix + software inventory + Mermaid topology + doc index (agents **`read_file`** by default with homelab work).                                                                                                                                                                                                                                                                                                                                                                                                                  |
| **`docs/private/homelab/OPERATOR_RETEACH.md`**    | **Fill-in gaps** (B1–B6); agents **`read_file`** after **`OPERATOR_SYSTEM_MAP.md`**. **Tracked templates (no real facts):** **`docs/private.example/homelab/OPERATOR_RETEACH.md`** + **`.pt_BR.md`** — copy structure locally; Portuguese = **pt-BR** (see **`docs-pt-br-locale`** rule).                                                                                                                                                                                                                                                                                     |
| **`docs/private/author_info/`**                   | **Personal / career / education / certificates** (CV text, course progress, cert IDs, narrative history). Optional: **`ACADEMIC_NETWORK_FAMILY_ETHICS.pt_BR.md`** — ethical use of close-family ties in academic planning (private only). Optional: **`RECENT_OPERATOR_SYNC_INDEX.pt_BR.md`** — dated bullets linking to other private notes after high-value chat sessions (see **[OPERATOR_SESSION_CAPTURE_GUIDE.md](ops/OPERATOR_SESSION_CAPTURE_GUIDE.md)**). Same gitignore rules as homelab; split from **`homelab/`** so you can sync or exclude policies differently. |
| **`docs/private/commercial/`**                    | **Sensitive client-facing commercial strategy** (e.g. maturity-consulting pricing bands, partner economics, rate cards, proposal numbers). **Never** commit or publish; keep EN + pt-BR pairs here if useful. **Tracked** pointer: **`docs/private.example/commercial/README.md`**.                                                                                                                                                                                                                                                                                           |
| **`docs/private/operator_economics/`**            | **Operator-side** economics: home/lab OPEX (utilities, subscriptions), CapEx / shopping lists, runway notes — *your* cost base, not customer SOWs. Split from **`commercial/`** when you want clearer mental boundaries. **Tracked** pointer: **`docs/private.example/operator_economics/README.md`**.                                                                                                                                                                                                                                                                        |
| **Nested VCS under `docs/private/`**              | Optional **second repository** (usually **Git** via `git init` inside `docs/private/`) so private Markdown gets **local commits** and **backup remotes** (`file://`, NAS, self-hosted SSH) **without** attaching history to the **GitHub** product repo. **Tracked** policy: **[PRIVATE_LOCAL_VERSIONING.md](ops/PRIVATE_LOCAL_VERSIONING.md)** ([pt-BR](ops/PRIVATE_LOCAL_VERSIONING.pt_BR.md)).                                                                                                                                                                             |
| **`docs/private/`** (root of private)             | Optional catch-all: `WHAT_TO_SHARE_WITH_AGENT.md`, one-off exports—prefer **`homelab/`** vs **`author_info/`** vs **`operator_economics/`** when the topic is clear.                                                                                                                                                                                                                                                                                                                                                                                                          |

**Commercial refinement (per client):** When you have **client-specific** project facts and **conditions found** on the ground, bring them in chat and/or under **`docs/private/`** only (never tracked). Use that input to **realign** **`docs/private/commercial/MATURITY_CONSULTING_PRICING_STUDY*.md`** toward a concrete **consulting** proposal and, if applicable, **licensing**—still **confidential**, not for GitHub.

**Enforcement:** **`tests/test_confidential_commercial_guard.py`** (CI + pre-commit) rejects **`git add -f`** of **`docs/private/`** and other index violations; Cursor rule **`confidential-commercial-never-tracked.mdc`**; skill **`confidential-commercial-layout`**.

**Rule:** Prefer **`homelab/`** for **physical/network** reality and **`author_info/`** for **person-shaped** facts so you can attach or exclude trees in backups/sync tools independently.

**CLI / session habit artifacts (`uptime`, `w`, `last`, `lastlog`, etc.):** Treat like inventory—**only** under **`docs/private/homelab/`** (e.g. **`reports/session-habit-YYYYMMDD.txt`** or a dated section in a private log). They expose **LAN IPs**, **usernames**, and **login rhythms**. **Do not** put them in **tracked** files, **issues**, or **PRs**. Pasting into **Cursor chat** for a one-off is your choice (subject to Cursor’s data handling); for **durable** reference, save **only** in **`docs/private/`**.

**Agents / Cursor:** **`docs/private/`** is **intentional workspace-only** context: **gitignored from GitHub**, but agents should **pull it in with `read_file`** when the task touches homelab, operator machines, **`P:`**, or project-private notes—**not** only when you **`@`** or leave tabs open. Keep **`WHAT_TO_SHARE_WITH_AGENT.md`** / **`homelab/`** current; still **never** commit **`docs/private/`**.

---

## 3. Public documentation policy (this repo)

**In tracked Markdown** (everything under `docs/` **except** `docs/private/`, plus `README`, `CONTRIBUTING`, etc.):

- Use **generic roles**: “primary Linux lab laptop,” “Windows + WSL dev workstation,” “x86 tower with Proxmox,” “musl mini-PC.”
- Use **placeholders**: `you@<hostname>`, `http://<your-sonar-host>:9000`, `*.example.com`.
- Do **not** paste **real hostnames, LAN IPs, Wi‑Fi PSKs, serials, or home paths** (`/home/you/...`, `C:\Users\...`), or **raw `last` / `lastlog` / `w` / `uptime`** output (same sensitivity—store under **`docs/private/homelab/`** if you need to keep it).
- Do **not** add **Markdown links** to paths under `docs/private/...` in public files—those links **404** for everyone else on GitHub and **enumerate** filenames. Instead, write: *“Store specifics in your **gitignored** `docs/private/homelab/` tree (see **PRIVATE_OPERATOR_NOTES.md**).”*

**Example classes** (wattage, RAM era) may appear in public docs as **illustrative** only—your **exact** make/model belongs under **`docs/private/homelab/`**.

---

## 4. Homelab server access (SSH — default workflow)

The assistant **does not** have a separate network connection to your house. It **can** still work on the homelab (e.g. **Latitude** as a server) by running **`ssh` in the Cursor integrated terminal on your dev workstation**, using **your** SSH client, keys, and `~/.ssh/config` (PowerShell, **WSL**, or **Git SSH** — whichever you use day to day).

## Default expectation (this repo / this operator):

1. **Document a `Host` alias** under **`docs/private/homelab/`** (see **[private.example/homelab/README.md](private.example/homelab/README.md)**) — e.g. `Host latitude-lab` with `HostName`, `User`, `IdentityFile` / agent — **gitignored**, never committed.
1. When you ask the assistant to **list files, pull reports, check Docker, or run diagnostics** on that machine, it should use commands like **`ssh latitude-lab '…'`** (or non-interactive flags you prefer) **from the project terminal**, not assume files appear magically in the workspace.
1. **You** must have **LAN or VPN reachability** from the dev PC to the homelab; **key-based auth** is strongly preferred so sessions are non-interactive where possible.
1. If a command fails with “connection refused” / “timed out” / “Permission denied”, fix **network, `sshd`, user, keys** on your side — the assistant can only suggest checks (`ssh -G latitude-lab`, `ping`, etc.).

This replaces any older wording that implied “the model cannot touch the lab” without also saying **“use SSH from the dev terminal.”**

---

## 5. Sharing with the AI assistant (Cursor, local context)

**Goal:** Let the assistant help with **layout, concepts, runbooks, SSH/API patterns**—without putting that material on **GitHub**.

### 5.1 Chat language (pt-BR default, EN for technical tokens)

**Preference (this operator):** Assistants should answer in **concise Brazilian Portuguese (pt-BR)** for narrative—not **Portuguese of Portugal (pt-PT)** (e.g. use **arquivo**, **compartilhar**, **seção**, **padrão** for software defaults). Keep **English** where it is standard in engineering: file paths, commit types, symbol names, flags, and citations of English-only plan rows.

**Code-switching:** You may mix **pt-BR and English in the same message** (even mid-thought); the assistant should follow without forcing a single language for the whole reply.

**Cost / tokens:** Brevity matters more than the choice of human language—avoid repeating the same point in two languages unless you ask for a bilingual summary. Say **short** or **token-aware** when you want minimal length.

**Shorthand / taxonomy (English only):** Session keywords are **fixed English tokens**: `deps`, `feature`, `homelab`, `docs`, `houseclean`, `backlog`, `pmo-view`, and the brevity cues `short`, `token-aware`. Use them **exactly** in chat; do not ask for localized aliases in `.cursor/rules/`. **`.cursor/rules/session-mode-keywords.mdc`** and this taxonomy table stay **English-only**; pt-BR is for surrounding explanation, not the tokens.

**Agent entry point:** **`AGENTS.md`** (chat language + shorthand bullets) encodes this for Cursor/Copilot.

| Layer                   | What happens                                                                                                                                                                                                                                                                                                                                              |
| -----                   | ------------                                                                                                                                                                                                                                                                                                                                              |
| **Git / GitHub**        | **`docs/private/`** is **gitignored** — not committed, not pushed. **Never** paste private paths or secrets into **issues, PR descriptions, or tracked files.**                                                                                                                                                                                           |
| **Cursor / chat**       | The assistant may use **`read_file`** on **`docs/private/`** when relevant—**shared workspace secret vs GitHub only**; **`@` / open tab optional**, not the default gate. Plus editor context and chat. **Disclosure to Cursor’s stack** per their terms—avoid plaintext **passwords / production keys** in files; prefer **Bitwarden** and placeholders. |
| **pCloud / other sync** | Same as today: convenient for **you** across machines, **not** a secrets vault. On **Windows**, the synced folder is often drive **`P:`** (see **`docs/private/WHAT_TO_SHARE_WITH_AGENT.md`** if you use that layout).                                                                                                                                    |

### Windows: `P:` (pCloud on the dev PC)

The assistant runs on **your** workstation. If **pCloud** maps the sync root to **`P:`**, the assistant can **`dir` / `Get-ChildItem P:\`** and **read files** under **`P:\...`** in-session (terminal or tools)—same as any local path. **Requirements:** pCloud client **running** and drive **mounted**; Cursor must allow access to that path (if a command fails with “path not found,” check the client). **Do not** record operator-specific **`P:\...`** paths in **Git-tracked** Markdown; keep them in **`docs/private/`** or mention them only in chat.

## Default (this operator / repo):

1. **`docs/private/`** — **Not on GitHub**; **is** normal workspace context for the assistant. Agents **`read_file`** **`docs/private/homelab/AGENT_LAB_ACCESS.md`** (and other private paths as needed) when homelab, Data Boar on LAN, **`P:`**, or operator inventory applies—**without** requiring you to **`@`** or open files.
1. **Stable narrative** — Keep **`WHAT_TO_SHARE_WITH_AGENT.md`** and **`homelab/`** updated; the assistant loads them **on demand** via tools, not only via **`@`**.
1. **Minimal paste** — For one-off extras, paste redacted snippets in chat if you prefer.
1. **Tracked repo** — **Patterns** only in public docs; **real hostnames/IPs** only under **`docs/private/`** or chat, never in commits.
1. **Stricter boundary (opt-in)** — To **force** “only when `@`,” add **`docs/private/`** to **`.cursorignore`** (not the default here).

**Homelab:** See **§4** — SSH/API details in **`docs/private/homelab/`**; agents read **`AGENT_LAB_ACCESS.md`** when doing lab work.

**Lint private Markdown locally** (optional): `uv run pytest --include-private` and `uv run python scripts/fix_markdown_sonar.py --include-private` — see [TESTING.md](TESTING.md).

---

## 6. Related tracked docs

- **[PRIVATE_LOCAL_VERSIONING.md](ops/PRIVATE_LOCAL_VERSIONING.md)** ([pt-BR](ops/PRIVATE_LOCAL_VERSIONING.pt_BR.md)) — optional **nested Git** (or other local VCS) for `docs/private/` **without** GitHub.
- **[OPERATOR_LAB_DOCUMENT_MAP.md](ops/OPERATOR_LAB_DOCUMENT_MAP.md)** ([pt-BR](ops/OPERATOR_LAB_DOCUMENT_MAP.pt_BR.md)) — **LAB‑PB vs LAB‑OP**: where every lab-related doc lives (public index + private filenames).
- [CONTRIBUTING.md](../CONTRIBUTING.md) — public repo hygiene.
- [SECURITY.md](../SECURITY.md) — secrets and `config.yaml`.
- [HOMELAB_VALIDATION.md](ops/HOMELAB_VALIDATION.md) — **playbook** (generic); real results → private `homelab/`.

**Template to copy:** [private.example/README.md](private.example/README.md)

**Português (Brasil):** [PRIVATE_OPERATOR_NOTES.pt_BR.md](PRIVATE_OPERATOR_NOTES.pt_BR.md)
