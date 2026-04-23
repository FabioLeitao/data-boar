# Completão — operator prompt library (taxonomy + thin starters)

**Português (Brasil):** [COMPLETAO_OPERATOR_PROMPT_LIBRARY.pt_BR.md](COMPLETAO_OPERATOR_PROMPT_LIBRARY.pt_BR.md)

## Purpose

Separate **three layers** so you do not paste a wall of text every session:

1. **Session token (English, line 1 only):** **`completao`** — already defined in **`.cursor/rules/session-mode-keywords.mdc`** and **[`AGENTS.md`](../../AGENTS.md)**.
2. **Tier shorthand (line 2):** a **short code** this document defines — tells the assistant which slice and which script line to prefer.
3. **Heavy prose (optional):** the full **copy-paste blocks A–E** in **[`LAB_COMPLETAO_FRESH_AGENT_BRIEF.md`](LAB_COMPLETAO_FRESH_AGENT_BRIEF.md)** — use when you change contracts or need a one-off deviation.

**Automation:** from repo root, **`.\scripts\completao-chat-starter.ps1`** prints a **minimal** two-line starter (and optional command line) you can paste into Cursor. **`.\scripts\completao-chat-starter.ps1 -Help`** lists tiers.

**Private custom prompt:** if your long narrative must mention real paths or preferences, keep a copy under **`docs/private/homelab/`** only — start from **[`../private.example/homelab/COMPLETAO_OPERATOR_PROMPT.example.md`](../private.example/homelab/COMPLETAO_OPERATOR_PROMPT.example.md)** (placeholders, safe to track).

## Tier taxonomy (line 2 after `completao`)

| Tier code | Intent | Assistant should… |
| --------- | ------ | ------------------- |
| **`tier:smoke`** | Default smoke — orchestrator only; LAB clones as checked out unless manifest sets **`completaoTargetRef`** | Run **`lab-completao-orchestrate.ps1 -Privileged`** (no **`-LabGitRef`** unless you add it in line 3). |
| **`tier:smoke-main`** | Repro smoke vs **`origin/main`** | Run **`-LabGitRef origin/main`** ( **`lab-op-git-ensure-ref`** check before smoke). |
| **`tier:smoke-tag`** | Pin to release tag **`vX.Y.Z`** | Run **`-LabGitRef vX.Y.Z -SkipGitPullOnInventoryRefresh`** — see **[`LAB_COMPLETAO_RUNBOOK.md`](LAB_COMPLETAO_RUNBOOK.md)** (*Target git ref*). |
| **`tier:followup-repo`** | After smoke — read-only repo drift | Match **[`LAB_COMPLETAO_FRESH_AGENT_BRIEF.md`](LAB_COMPLETAO_FRESH_AGENT_BRIEF.md)** block **B** ( **`lab-op-repo-status.ps1`** ). |
| **`tier:followup-poc`** | Windows pytest POC slices | Match block **C** ( **`smoke-maturity-assessment-poc.ps1`**, **`smoke-webauthn-json.ps1`** ). |
| **`tier:followup-cli`** | External eval / CLI | Match block **D** + **[`LAB_EXTERNAL_CONNECTIVITY_EVAL.md`](LAB_EXTERNAL_CONNECTIVITY_EVAL.md)**. |
| **`tier:evidence`** | Close notes for next session | Match block **E**. |

**Syntax:** line 2 is exactly one tier line, e.g. **`tier:smoke-main`**. Optional line 3+: extra constraints (**`token-aware`**, **`short`**, one-off flags). Do **not** append branch/version on **line 1** — taxonomy is **`session-mode-keywords.mdc`**.

## Thin starter (example paste)

```text
completao

tier:smoke-main
```

Then run from repo root (assistant or you):

```powershell
.\scripts\lab-completao-orchestrate.ps1 -Privileged -LabGitRef origin/main
```

The assistant still follows **`lab-completao-workflow.mdc`**, reads **`docs/private/homelab/reports/`** when present, and does **not** ask redundant SSH/**`-Privileged`** permission.

## When to use the full blocks A–E

Use **[`LAB_COMPLETAO_FRESH_AGENT_BRIEF.md`](LAB_COMPLETAO_FRESH_AGENT_BRIEF.md)** verbatim blocks when:

- You change **manifest** semantics, **sudoers** paths, or **blast-radius** wording.
- You need a **one-off** instruction (single host, skip inventory, etc.).
- You are onboarding a **human** who does not yet trust the thin tier line.

## Cross-links

- **Cold-start ladder:** [OPERATOR_AGENT_COLD_START_LADDER.md](OPERATOR_AGENT_COLD_START_LADDER.md) ([pt-BR](OPERATOR_AGENT_COLD_START_LADDER.pt_BR.md))
- **Personas (ENT / PRO / edge / bridge):** [LAB_OP_HOST_PERSONAS.md](LAB_OP_HOST_PERSONAS.md) ([pt-BR](LAB_OP_HOST_PERSONAS.pt_BR.md))
- **Runbook:** [LAB_COMPLETAO_RUNBOOK.md](LAB_COMPLETAO_RUNBOOK.md) ([pt-BR](LAB_COMPLETAO_RUNBOOK.pt_BR.md))
- **Script map:** [TOKEN_AWARE_SCRIPTS_HUB.md](TOKEN_AWARE_SCRIPTS_HUB.md) ([pt-BR](TOKEN_AWARE_SCRIPTS_HUB.pt_BR.md))
