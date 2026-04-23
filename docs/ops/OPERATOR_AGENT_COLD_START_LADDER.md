# Operator + agent cold-start ladder (token-aware, low context)

**Português (Brasil):** [OPERATOR_AGENT_COLD_START_LADDER.pt_BR.md](OPERATOR_AGENT_COLD_START_LADDER.pt_BR.md)

## Purpose

Give a **single ordered path** so a **fresh chat** (no transcript memory) can still land on the **right hub first**, without re-reading all of [`AGENTS.md`](../../AGENTS.md). This page is **navigation + non-negotiables** only — behaviour stays in **code**, **TECH_GUIDE**, and linked runbooks.

## Read in this order (pick depth by task)

1. **This file** — task router + six rules below.
2. **[`AGENTS.md`](../../AGENTS.md)** — Quick index table (theme → first doc); long bullets are the contract.
3. **[`CURSOR_AGENT_POLICY_HUB.md`](CURSOR_AGENT_POLICY_HUB.md)** — same themes with **clickable** paths into `.cursor/rules`, `.cursor/skills`, and `docs/ops/`.
4. **[`TOKEN_AWARE_SCRIPTS_HUB.md`](TOKEN_AWARE_SCRIPTS_HUB.md)** — which **`scripts/*.ps1`** map to keywords, skills, and runbooks.
5. **Lab / completão only:** **[`LAB_COMPLETAO_FRESH_AGENT_BRIEF.md`](LAB_COMPLETAO_FRESH_AGENT_BRIEF.md)** → **[`LAB_COMPLETAO_RUNBOOK.md`](LAB_COMPLETAO_RUNBOOK.md)** → **[`LAB_OP_HOST_PERSONAS.md`](LAB_OP_HOST_PERSONAS.md)** (ENT / PRO / edge / bridge + Ansible knobs).
6. **Private stack only:** **[`PRIVATE_STACK_SYNC_RITUAL.md`](PRIVATE_STACK_SYNC_RITUAL.md)** · **`scripts/private-git-sync.ps1`** (**`-Push`** when mirrors must align) · **[ADR 0040](../adr/0040-assistant-private-stack-evidence-mirrors-default.md)**.
7. **Where docs live (LAB-PB vs LAB-OP):** **[`OPERATOR_LAB_DOCUMENT_MAP.md`](OPERATOR_LAB_DOCUMENT_MAP.md)**.
8. **Session English tokens:** [`.cursor/rules/session-mode-keywords.mdc`](../../.cursor/rules/session-mode-keywords.mdc) — type tokens **exactly** (e.g. **`completao`**, **`private-stack-sync`**, **`short`** / **`token-aware`**).

## Task router (one hop)

| If the operator wants… | Open first (then follow links inside) |
| ------------------------ | -------------------------------------- |
| **Ship code / fix CI** | **`TOKEN_AWARE_SCRIPTS_HUB`** §1 → **`check-all.ps1`**; **`AGENTS.md`** merge/PR bullets |
| **Which script / wrapper for this?** (avoid reinventing long shell) | **`repo-scripts-wrapper-ritual.mdc`** · **`TOKEN_AWARE_SCRIPTS_HUB`** · **`check-all-gate.mdc`** · **`token-aware-automation`** skill |
| **Docs / hubs / MAP** | **`doc-hubs-plans-sync`** skill · **`docs/README.md`** *Internal and reference* · paired **`*.pt_BR.md`** |
| **Lab smoke / completão** | **`COMPLETAO_OPERATOR_PROMPT_LIBRARY`** ( **`completao`** + **`tier:…`** ) · **`LAB_COMPLETAO_FRESH_AGENT_BRIEF`** · **`lab-completao-workflow.mdc`** · **`LAB_COMPLETAO_RUNBOOK`** · **`scripts/completao-chat-starter.ps1`** |
| **Ansible / Podman / personas** | **`LAB_OP_HOST_PERSONAS`** · **`ops/automation/ansible/README.md`** |
| **Homelab inventory / SSH batch** | Private **`lab-op-hosts.manifest.json`** (when present) · **`LAB_OP_PRIVILEGED_COLLECTION.md`** · **`OPERATOR_LAB_DOCUMENT_MAP`** |
| **Stacked private Git close** | **`PRIVATE_STACK_SYNC_RITUAL`** · **`private-git-sync.ps1`** |
| **Recovery / “figure it out”** | **`operator-investigation-before-blocking.mdc`** · **`operator-recovery-investigation`** skill |
| **Gmail / webmail / social / inbox or attachment** (same dev PC as SSH; warm or cold + **Google SSO** when offered) | **`cursor-browser-social-sso-hygiene.mdc`** (*Contrato único* + *Gmail e webmail*) · **`operator-browser-warm-session.mdc`** · **`operator-direct-execution.mdc`** §5 — **try** MCP then **SSO click** before refusing; **only then** ask the operator to interact once; PDFs → **`docs/private/`** + **`read_file`** |

## Six non-negotiables (do not “forget” on fresh chats)

1. **`docs/private/`** exists in workspace → **`read_file` / `list_dir` is allowed**; **never** paste secrets or LAN identifiers into **tracked** files or public PRs (**`PRIVATE_OPERATOR_NOTES.md`**).
2. **Primary Windows dev PC canonical clone** — **no** routine **`clean-slate`**, **`git filter-repo`**, or **`git reset --hard`** on the product tree (**`PRIMARY_WINDOWS_WORKSTATION_PROTECTION.md`**).
3. **`completao`** — use **`lab-completao-orchestrate.ps1 -Privileged`** from repo root when in scope; **manifest** sets **`completaoEngineMode` / `completaoSkipEngineImport`** for container-only hosts (**`LAB_COMPLETAO_RUNBOOK`**).
4. **Advice on merge / PR / “what’s next”** — **`git fetch`** first (**`git-pr-sync-before-advice.mdc`**).
5. **Private mirrors** — when sync is obvious, run **`private-git-sync.ps1 -Push`** and **report** concrete SSH/mount errors (**ADR 0040**, **`operator-evidence-backup-no-rhetorical-asks.mdc`**).
6. **Portuguese prose defaults to pt-BR** — tracked **`*.pt_BR.md`**, private Portuguese Markdown under **`docs/private/`**, and assistant-authored PT paragraphs must **not** drift to **pt-PT** “by accident.” Exceptions only per **`.cursor/rules/docs-locale-pt-br-contract.mdc`**. Run **`uv run pytest tests/test_docs_pt_br_locale.py -v`** after substantive pt-BR doc edits.

## Product vs operator map (concern-first)

Compliance and capability questions for **buyers / DPO / CISO** start at **[`MAP.md`](../MAP.md)** ([pt-BR](../MAP.pt_BR.md)), not under `docs/plans/` (external-tier rule: **ADR 0004**).

## Related (mental map, not duplicates)

| Artifact | Role |
| -------- | ---- |
| **`AGENTS.md`** | Canonical long-form assistant contract |
| **`CURSOR_AGENT_POLICY_HUB.md`** | Phase B — same index, clickable |
| **`TOKEN_AWARE_SCRIPTS_HUB.md`** | Script ↔ keyword ↔ skill map |
| **`OPERATOR_LAB_DOCUMENT_MAP.md`** | LAB-PB vs LAB-OP index |
| **`LAB_OP_HOST_PERSONAS.md`** | T14 / Latitude / pi / mini-bt **intent** vs automation |
| **`COMPLETAO_OPERATOR_PROMPT_LIBRARY.md`** | **`completao`** + **`tier:`** chat taxonomy + **`completao-chat-starter.ps1`** |

When you add a **new recurring theme**, add **one row** to **`AGENTS.md` Quick index** and **`CURSOR_AGENT_POLICY_HUB`** in the **same change**.
