# Lab completão — brief for a fresh Cursor agent (copy-paste)

**Português (Brasil):** [LAB_COMPLETAO_FRESH_AGENT_BRIEF.pt_BR.md](LAB_COMPLETAO_FRESH_AGENT_BRIEF.pt_BR.md)

**Use when:** You open a **new chat** with **no prior context** and want the assistant to run **completão** the same way as the **repo contracts** (`lab-completao-workflow.mdc`, `LAB_COMPLETAO_RUNBOOK.md`).

## Preconditions (operator workstation)

- **Same** Windows dev PC, **same** repo clone, **Cursor integrated terminal** (not a remote “AI datacenter”).
- **`docs/private/homelab/lab-op-hosts.manifest.json`** present (copy from **`docs/private.example/homelab/lab-op-hosts.manifest.example.json`** when needed).
- **`ssh`** to manifest hosts works from that terminal (keys / `~/.ssh/config`).
- Optional: **narrow sudoers** for **`sudo -n`** on Linux hosts — see **`LAB_OP_PRIVILEGED_COLLECTION.md`** and gitignored **`LABOP_COMPLETÃO_SUDOERS*.md`**.

## Read first (order)

1. **[`AGENTS.md`](../../AGENTS.md)** — Quick index row **Lab completão** and session token **`completao`**.
2. **[`LAB_COMPLETAO_RUNBOOK.md`](LAB_COMPLETAO_RUNBOOK.md)** — contracts, scripts, **slice order**, capability coverage, automation + learnings.
3. **`.cursor/rules/lab-completao-workflow.mdc`** — always-on policy (SSH, **`-Privileged`**, no idle “may I SSH?” prompts, **L-series** protection, doc+code matrix, timeouts/FP-FN notes).

## Session token (English)

Type **`completao`** in chat so the session scope matches **`session-mode-keywords.mdc`**.

## First command (default)

From **repository root** on Windows:

```text
.\scripts\lab-completao-orchestrate.ps1 -Privileged
```

Then read **`docs/private/homelab/reports/`** (`completao_*_allhosts.log`, per-host `*_completao_host_smoke.log`).

## Sequential slices (do not skip without cause)

Follow **`LAB_COMPLETAO_RUNBOOK.md`** — **Recommended slice order**, **Capability coverage**, **Automation reuse and documented learnings**. Extended layers (synthetic data, DBs, scans, API key, JWT, WebAuthn, maturity POC, “secure by design” checks) use **smoke runbooks** and **docs** linked from that runbook (e.g. **`SMOKE_WEBAUTHN_JSON.md`**, **`SMOKE_MATURITY_ASSESSMENT_POC.md`**, **`SECURE_DASHBOARD_AUTH_AND_HTTPS_HOWTO.md`**, **`TECH_GUIDE.md`**). **English docs + code** are the behaviour source of truth.

## Do not

- Claim the assistant **cannot** reach the lab via **SSH from this PC** when **`ssh`** works for the operator — see **`homelab-ssh-via-terminal.mdc`**.
- Ask redundant **“may I use SSH / `-Privileged`?”** if the operator already asked for **completão** — see **`operator-direct-execution.mdc`**.
- Run **destructive** repo operations on the **primary Windows dev PC** (**L-series** role) — **`PRIMARY_WINDOWS_WORKSTATION_PROTECTION.md`**.
- Put **secrets**, **tokens**, or **LAN identifiers** in **public** GitHub; **private** notes only under **`docs/private/homelab/`**.

## Copy-paste block (operator → new chat)

```text
completao

You are in the data-boar repo on my Windows dev PC. Read AGENTS.md (Quick index: Lab completão), then docs/ops/LAB_COMPLETAO_RUNBOOK.md, and follow .cursor/rules/lab-completao-workflow.mdc. Use the integrated terminal — same SSH reachability as my shell.

1) From repo root run: .\scripts\lab-completao-orchestrate.ps1 -Privileged
2) Summarize docs/private/homelab/reports/ logs (no secrets in chat if sensitive).
3) Continue the runbook slice order: repo alignment if needed, per-host FS smoke, CLI/API/web, then POC smokes (WebAuthn, maturity assessment, secure dashboard) per docs/ops/SMOKE_*.md and TECH_GUIDE as applicable.

Do not ask redundant permission for SSH or -Privileged. Do not claim the lab is unreachable from this workspace. Protect my primary Windows dev workstation per docs/ops/PRIMARY_WINDOWS_WORKSTATION_PROTECTION.md. Document material findings (timeouts, latency, FP/FN vs synthetic, confidence on real paths) under docs/private/homelab/.

If something fails, print the actual error and what I must fix (e.g. sudoers, manifest, missing uv), then stop — I will fix and ask you to retry.
```

## Will a fresh agent “get it”?

**Mostly yes**, if: the **workspace** is this repo (so **`.cursor/rules/`** load), **`completao`** or the copy-paste block is used, and **preconditions** hold. **No** agent can **invent** SSH keys, **UDM** API access, or **sudoers** on hosts — those stay **operator-side**. The rules **reduce** mediocre “impossible LAN” answers; they **do not** replace **your** first-time setup or **secrets**.

## What could still improve

- Keep **`manifest.json`** and **private** YAML **up to date** as the lab grows.
- After each completão, **one line** in **`PLANS_TODO.md`** or an issue when a **product gap** is confirmed — closes the loop from **session notes** to **roadmap**.
