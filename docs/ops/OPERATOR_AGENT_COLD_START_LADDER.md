# Operator + agent cold-start ladder (token-aware, low context)

**Português (Brasil):** [OPERATOR_AGENT_COLD_START_LADDER.pt_BR.md](OPERATOR_AGENT_COLD_START_LADDER.pt_BR.md)

## Purpose

Give a **single ordered path** so a **fresh chat** (no transcript memory) can still land on the **right hub first**, without re-reading all of [`AGENTS.md`](../../AGENTS.md). This page is **navigation + non-negotiables** only — behaviour stays in **code**, **TECH_GUIDE**, and linked runbooks.

## Read in this order (pick depth by task)

1. **This file** — task router + seven non-negotiables below.
2. **[`AGENTS.md`](../../AGENTS.md)** — Quick index table (theme → first doc); long bullets are the contract.
3. **[`CURSOR_AGENT_POLICY_HUB.md`](CURSOR_AGENT_POLICY_HUB.md)** — same themes with **clickable** paths into `.cursor/rules`, `.cursor/skills`, and `docs/ops/`.
4. **[`TOKEN_AWARE_SCRIPTS_HUB.md`](TOKEN_AWARE_SCRIPTS_HUB.md)** — which **`scripts/*.ps1`** map to keywords, skills, and runbooks.
5. **Lab / completão only:** **[`LAB_COMPLETAO_FRESH_AGENT_BRIEF.md`](LAB_COMPLETAO_FRESH_AGENT_BRIEF.md)** → **[`LAB_COMPLETAO_RUNBOOK.md`](LAB_COMPLETAO_RUNBOOK.md)** → **[`LAB_OP_HOST_PERSONAS.md`](LAB_OP_HOST_PERSONAS.md)** (ENT / PRO / edge / bridge + Ansible knobs).
6. **Private stack only:** **[`PRIVATE_STACK_SYNC_RITUAL.md`](PRIVATE_STACK_SYNC_RITUAL.md)** · **`scripts/private-git-sync.ps1`** (**`-Push`** when mirrors must align) · **[ADR 0040](../adr/0040-assistant-private-stack-evidence-mirrors-default.md)**.
7. **Where docs live (LAB-PB vs LAB-OP):** **[`OPERATOR_LAB_DOCUMENT_MAP.md`](OPERATOR_LAB_DOCUMENT_MAP.md)**.
8. **Session English tokens:** [`.cursor/rules/session-mode-keywords.mdc`](../../.cursor/rules/session-mode-keywords.mdc) — type tokens **exactly** (e.g. **`homelab`**, **`completao`**, **`legal-dossier-update`**, **`private-stack-sync`**, **`short`** / **`token-aware`**).

## Task router (one hop)

| If the operator wants… | Open first (then follow links inside) |
| ------------------------ | -------------------------------------- |
| **Ship code / fix CI** | **`TOKEN_AWARE_SCRIPTS_HUB`** §1 → **`check-all.ps1`**; **`AGENTS.md`** merge/PR bullets |
| **Which script / wrapper for this?** (avoid reinventing long shell) | **`repo-scripts-wrapper-ritual.mdc`** · **`TOKEN_AWARE_SCRIPTS_HUB`** · **`check-all-gate.mdc`** · **`token-aware-automation`** skill |
| **Docs / hubs / MAP** | **`doc-hubs-plans-sync`** skill · **`docs/README.md`** *Internal and reference* · paired **`*.pt_BR.md`** |
| **Lab smoke / completão** | **`COMPLETAO_OPERATOR_PROMPT_LIBRARY`** ( **`completao`** + **`tier:…`** ) · **`LAB_COMPLETAO_FRESH_AGENT_BRIEF`** · **`lab-completao-workflow.mdc`** · **`LAB_COMPLETAO_RUNBOOK`** · **`scripts/completao-chat-starter.ps1`** |
| **Ansible / Podman / personas** | **`LAB_OP_HOST_PERSONAS`** · **`ops/automation/ansible/README.md`** |
| **Homelab inventory / SSH batch** | Session token **`homelab`** · **`homelab-ssh-via-terminal.mdc`** · private **`lab-op-hosts.manifest.json`** (when present) · **`LAB_OP_PRIVILEGED_COLLECTION.md`** · **`OPERATOR_LAB_DOCUMENT_MAP`** · § *Token → rule latch (`homelab`)* below |
| **Stacked private Git close** | Session **`private-stack-sync`** · **`docs-private-workspace-context.mdc`** · **`PRIVATE_STACK_SYNC_RITUAL`** · **`private-git-sync.ps1`** · § *Token → rule latch (`private-stack-sync`)* below |
| **Private legal / labour evidence** (import, CAT/INSS-style updates, new paste) | Session token **`legal-dossier-update`** · **`dossier-update-on-evidence.mdc`** · private **`legal_dossier/`** + **`raw_pastes/`** · § *Token → rule latch (legal dossier)* below |
| **Recovery / “figure it out”** | **`operator-investigation-before-blocking.mdc`** · **`operator-recovery-investigation`** skill |
| **Gmail / webmail / social / inbox or attachment** (same dev PC as SSH; warm or cold + **Google SSO** when offered) | **`cursor-browser-social-sso-hygiene.mdc`** (*Contrato único* + *Gmail e webmail*) · **`operator-browser-warm-session.mdc`** · **`operator-direct-execution.mdc`** §5 — **try** MCP then **SSO click** before refusing; **only then** ask the operator to interact once; PDFs → **`docs/private/`** + **`read_file`** |

### Token → rule → wrapper latch (**`completao`**)

Use this **first message shape** so a **situational** **`lab-completao-workflow.mdc`** still binds (globs **or** explicit `@`), without re-loading it on every unrelated chat:

1. Line 1: English token **`completao`** (optional same message: **`short`** / **`token-aware`** for terse narration).
2. Line 2: **`tier:…`** exactly as in **`COMPLETAO_OPERATOR_PROMPT_LIBRARY.md`** (tiers, smoke vs release-master, evidence). Paste block: **`.\scripts\completao-chat-starter.ps1 -Help`** or run with **`-Tier …`** to print lines to copy.
3. If the thread is **not** already touching **`scripts/lab-completao*`** or **`docs/ops/LAB_COMPLETAO*`**, **attach** **`.cursor/rules/lab-completao-workflow.mdc`** via **`@`** so the full workflow rule is in context.
3a. When the blocker is **`ssh` / LAN reachability / `sudo -n` vs tmux`** rather than orchestrator flags alone, **`read_file`** **`.cursor/rules/homelab-ssh-via-terminal.mdc`** (or **`@homelab-ssh-via-terminal.mdc`**) even if **`lab-completao-workflow.mdc`** is already open.
4. **Default automation (operator runs, assistant interprets logs):** from repo root **`.\scripts\lab-completao-orchestrate.ps1 -Privileged`** — then **`read_file`** / summarize under **`docs/private/homelab/reports/`** per **`LAB_COMPLETAO_RUNBOOK.md`**. Do **not** replace the orchestrator with ad-hoc one-off **`ssh`** unless the operator explicitly opts out.

### Token → rule latch (**`homelab`**)

Keep **`homelab-ssh-via-terminal.mdc`** **situational** but **binding** for **LAN / `ssh` / same-PC-as-operator** semantics:

1. Line 1: English token **`homelab`** (optional **`short`** / **`token-aware`**).
2. **`read_file`** **`.cursor/rules/homelab-ssh-via-terminal.mdc`** — use **`@homelab-ssh-via-terminal.mdc`** if the editor has not already attached it (paths outside the rule globs will not auto-load it).
3. Then **`docs/ops/HOMELAB_VALIDATION.md`** (+ **`.pt_BR.md`** when needed) and private **`docs/private/homelab/AGENT_LAB_ACCESS.md`** when present — **never** paste real hostnames or LAN identifiers into **tracked** files or public PRs.

### Token → rule latch (**`legal-dossier-update`**)

For **private legal / labour evidence** under **`docs/private/legal_dossier/`** or **`docs/private/raw_pastes/`**, keep the heavy rule **situational** but **binding** when you need it:

1. Line 1: English token **`legal-dossier-update`** (optional **`short`** / **`token-aware`**).
2. **`read_file`** **`.cursor/rules/dossier-update-on-evidence.mdc`** — use **`@dossier-update-on-evidence.mdc`** if the editor has not already attached it (paths outside the rule globs will not auto-load it).
3. Execute the **ordered** checklist inside that rule (index → executive summary → risk doc if applicable → **`OPERATOR_RETEACH.md`** → stacked **`docs/private/`** git + **`private-git-sync.ps1`** when policy says so).
4. **Never** put party names, docket numbers, or LAN identifiers into **tracked** product docs, issues, or PRs.

### Token → rule latch (**`private-stack-sync`** + **`docs/private/`** read cadence)

For **stacked private Git** and **`docs/private/`** hygiene, keep **`docs-private-workspace-context.mdc`** **situational** but **binding** when you run the close ritual:

1. Line 1: English token **`private-stack-sync`** (optional **`short`** / **`token-aware`**).
2. **`read_file`** **`.cursor/rules/docs-private-workspace-context.mdc`** — use **`@docs-private-workspace-context.mdc`** if globs did not load it ( **`agent-docs-private-read-access.mdc`** is still **always-on** for **never self-block** ).
3. **`read_file`** **`docs/ops/PRIVATE_STACK_SYNC_RITUAL.md`** (+ **`.pt_BR.md`** when used), then **`.\scripts\private-git-sync.ps1`** (**`-Push`** when mirrors must align) per **ADR 0040** / **`operator-evidence-backup-no-rhetorical-asks.mdc`**.
4. **Never** paste passphrases, keyfiles, or private paths into **tracked** files or public PRs.

## Seven non-negotiables (do not “forget” on fresh chats)

1. **`docs/private/`** exists in workspace → **`read_file` / `list_dir` is allowed**; **never** paste secrets or LAN identifiers into **tracked** files or public PRs (**`PRIVATE_OPERATOR_NOTES.md`**). Expanded read-order + **`.cursorignore`** opt-out: situational **`docs-private-workspace-context.mdc`** — use **`private-stack-sync`** or **`@docs-private-workspace-context.mdc`** in **fresh** threads; **never self-block** remains **`agent-docs-private-read-access.mdc`** (**always-on**).
2. **Primary Windows dev PC canonical clone** — **no** routine **`clean-slate`**, **`git filter-repo`**, or **`git reset --hard`** on the product tree (**`PRIMARY_WINDOWS_WORKSTATION_PROTECTION.md`**).
3. **`completao`** — use **`lab-completao-orchestrate.ps1 -Privileged`** from repo root when in scope; **manifest** sets **`completaoEngineMode` / `completaoSkipEngineImport`** for container-only hosts (**`LAB_COMPLETAO_RUNBOOK`**).
4. **Advice on merge / PR / “what’s next”** — **`git fetch`** first (**`git-pr-sync-before-advice.mdc`**).
5. **Private mirrors** — when sync is obvious, run **`private-git-sync.ps1 -Push`** and **report** concrete SSH/mount errors (**ADR 0040**, **`operator-evidence-backup-no-rhetorical-asks.mdc`**).
6. **Portuguese prose defaults to pt-BR** — tracked **`*.pt_BR.md`**, private Portuguese Markdown under **`docs/private/`**, and assistant-authored PT paragraphs must **not** drift to **pt-PT** “by accident.” Exceptions only per **`.cursor/rules/docs-locale-pt-br-contract.mdc`**. Run **`uv run pytest tests/test_docs_pt_br_locale.py -v`** after substantive pt-BR doc edits.
7. **Homelab / LAB-OP reachability from the integrated terminal** — on the **operator dev PC**, Cursor’s integrated terminal is the **same machine and LAN** as your normal shell for **`ssh`**, **`scp`**, **`curl` to lab HTTP**, etc. (**`homelab-ssh-via-terminal.mdc`**). Before claiming **“no remote access”** or **“I cannot reach lab hosts”**, **`read_file`** **`docs/private/homelab/AGENT_LAB_ACCESS.md`** (when present) and use **SSH `Host` aliases / manifest paths** from private docs — do **not** invent real hostnames, IPs, or home paths in **tracked** files. A laptop prompt like **`user@LAB-NODE-02-…` in chat** is **not** proof the assistant lacks **`ssh`** to manifest hosts from this workspace.

## Product vs operator map (concern-first)

Compliance and capability questions for **buyers / DPO / CISO** start at **[`MAP.md`](../MAP.md)** ([pt-BR](../MAP.pt_BR.md)), not under `docs/plans/` (external-tier rule: **ADR 0004**).

## Related (mental map, not duplicates)

| Artifact | Role |
| -------- | ---- |
| **`AGENTS.md`** | Canonical long-form assistant contract |
| **`CURSOR_AGENT_POLICY_HUB.md`** | Phase B — same index, clickable |
| **`TOKEN_AWARE_SCRIPTS_HUB.md`** | Script ↔ keyword ↔ skill map |
| **`OPERATOR_LAB_DOCUMENT_MAP.md`** | LAB-PB vs LAB-OP index |
| **`LAB_OP_HOST_PERSONAS.md`** | LAB-NODE-01 / LAB-NODE-02 / pi / LAB-NODE-03 **intent** vs automation |
| **`COMPLETAO_OPERATOR_PROMPT_LIBRARY.md`** | **`completao`** + **`tier:`** chat taxonomy + **`completao-chat-starter.ps1`** |

When you add a **new recurring theme**, add **one row** to **`AGENTS.md` Quick index** and **`CURSOR_AGENT_POLICY_HUB`** in the **same change**.
