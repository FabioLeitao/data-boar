# Completão — biblioteca de prompts do operador (taxonomia + arranques finos)

**English:** [COMPLETAO_OPERATOR_PROMPT_LIBRARY.md](COMPLETAO_OPERATOR_PROMPT_LIBRARY.md)

## Objetivo

Separar **três camadas** para não colar um bloco enorme em toda sessão:

1. **Token de sessão (inglês, só na linha 1):** **`completao`** — já definido em **`.cursor/rules/session-mode-keywords.mdc`** e no **[`AGENTS.md`](../../AGENTS.md)**.
2. **Atalho de *tier* (linha 2):** um **código curto** definido nesta página — diz ao assistente qual fatia e qual linha de comando preferir.
3. **Prosa pesada (opcional):** os blocos **A–E** completos no **[`LAB_COMPLETAO_FRESH_AGENT_BRIEF.md`](LAB_COMPLETAO_FRESH_AGENT_BRIEF.md)** — use quando mudar contratos ou precisar de desvio pontual.

**Automação:** na raiz do repo, **`.\scripts\completao-chat-starter.ps1`** imprime um arranque **mínimo** (duas linhas + comando opcional) para colar no Cursor. **`.\scripts\completao-chat-starter.ps1 -Help`** lista os *tiers*.

**Prompt longo privado:** se a narrativa tiver caminhos reais ou preferências, guarde só em **`docs/private/homelab/`** — modelo com placeholders: **[`../private.example/homelab/COMPLETAO_OPERATOR_PROMPT.example.md`](../private.example/homelab/COMPLETAO_OPERATOR_PROMPT.example.md)** (seguro para versionar).

## Taxonomia de *tier* (linha 2 depois de `completao`)

| Código de *tier* | Intenção | O assistente deve… |
| ---------------- | -------- | ------------------- |
| **`tier:smoke`** | Smoke padrão — só orquestrador; clones do LAB como estão salvo **`completaoTargetRef`** no manifest | Correr **`lab-completao-orchestrate.ps1 -Privileged`** (sem **`-LabGitRef`** salvo se você acrescentar na linha 3). |
| **`tier:smoke-main`** | Smoke reprodutível vs **`origin/main`** | Correr **`-LabGitRef origin/main`** (verificação **`lab-op-git-ensure-ref`** antes do smoke). |
| **`tier:smoke-tag`** | Fixar em tag **`vX.Y.Z`** | Correr **`-LabGitRef vX.Y.Z -SkipGitPullOnInventoryRefresh`** — ver **[`LAB_COMPLETAO_RUNBOOK.md`](LAB_COMPLETAO_RUNBOOK.md)** (*Target git ref*). |
| **`tier:followup-repo`** | Depois do smoke — *drift* de repo só leitura | Igual ao bloco **B** do **[`LAB_COMPLETAO_FRESH_AGENT_BRIEF.md`](LAB_COMPLETAO_FRESH_AGENT_BRIEF.md)** (**`lab-op-repo-status.ps1`**). |
| **`tier:followup-poc`** | Fatias pytest POC no Windows | Igual ao bloco **C**. |
| **`tier:followup-cli`** | Avaliação externa / CLI | Igual ao bloco **D** + **[`LAB_EXTERNAL_CONNECTIVITY_EVAL.md`](LAB_EXTERNAL_CONNECTIVITY_EVAL.md)**. |
| **`tier:evidence`** | Fechar notas para a próxima sessão | Igual ao bloco **E**. |

**Sintaxe:** linha 2 = uma linha de *tier*, ex. **`tier:smoke-main`**. Linhas 3+ opcionais: **`token-aware`**, **`short`**, flags pontuais. **Não** junte branch/versão na **linha 1** — a taxonomia de sessão está em **`session-mode-keywords.mdc`**.

## Arranque fino (exemplo para colar)

```text
completao

tier:smoke-main
```

Depois, na raiz do repo (você ou o assistente):

```powershell
.\scripts\lab-completao-orchestrate.ps1 -Privileged -LabGitRef origin/main
```

O assistente segue **`lab-completao-workflow.mdc`**, lê **`docs/private/homelab/reports/`** quando existir e **não** pede permissão redundante para SSH/**`-Privileged`**.

## Quando usar os blocos A–E completos

Use os blocos literais do **[`LAB_COMPLETAO_FRESH_AGENT_BRIEF.md`](LAB_COMPLETAO_FRESH_AGENT_BRIEF.md)** quando:

- Mudar semântica do **manifest**, caminhos de **sudoers** ou texto de **blast-radius**.
- Precisar de instrução **pontual** (um host, saltar inventário, etc.).
- Estiver a integrar um **humano** que ainda não confia na linha fina de *tier*.

## Ligações

- **Escada de arranque:** [OPERATOR_AGENT_COLD_START_LADDER.pt_BR.md](OPERATOR_AGENT_COLD_START_LADDER.pt_BR.md) ([EN](OPERATOR_AGENT_COLD_START_LADDER.md))
- **Personas:** [LAB_OP_HOST_PERSONAS.pt_BR.md](LAB_OP_HOST_PERSONAS.pt_BR.md) ([EN](LAB_OP_HOST_PERSONAS.md))
- **Runbook:** [LAB_COMPLETAO_RUNBOOK.pt_BR.md](LAB_COMPLETAO_RUNBOOK.pt_BR.md) ([EN](LAB_COMPLETAO_RUNBOOK.md))
- **Mapa de scripts:** [TOKEN_AWARE_SCRIPTS_HUB.pt_BR.md](TOKEN_AWARE_SCRIPTS_HUB.pt_BR.md) ([EN](TOKEN_AWARE_SCRIPTS_HUB.md))
