# Escada de arranque operador + agente (token-aware, pouco contexto)

**English:** [OPERATOR_AGENT_COLD_START_LADDER.md](OPERATOR_AGENT_COLD_START_LADDER.md)

## Objetivo

Oferecer **um caminho ordenado** para um **chat novo** (sem memória do transcript) ainda assim chegar ao **hub certo primeiro**, sem reler o [`AGENTS.md`](../../AGENTS.md) inteiro. Esta página é só **navegação + regras mínimas** — o comportamento continua no **código**, **TECH_GUIDE** e runbooks ligados.

## Ordem de leitura (profundidade conforme a tarefa)

1. **Este arquivo** — router de tarefas + cinco regras abaixo.
2. **[`AGENTS.md`](../../AGENTS.md)** — tabela Quick index (tema → primeiro doc); os bullets longos são o contrato.
3. **[`CURSOR_AGENT_POLICY_HUB.pt_BR.md`](CURSOR_AGENT_POLICY_HUB.pt_BR.md)** — os mesmos temas com caminhos **clicáveis** para `.cursor/rules`, `.cursor/skills` e `docs/ops/`.
4. **[`TOKEN_AWARE_SCRIPTS_HUB.pt_BR.md`](TOKEN_AWARE_SCRIPTS_HUB.pt_BR.md)** — que **`scripts/*.ps1`** ligam a keywords, skills e runbooks.
5. **Só lab / completão:** **[`LAB_COMPLETAO_FRESH_AGENT_BRIEF.pt_BR.md`](LAB_COMPLETAO_FRESH_AGENT_BRIEF.pt_BR.md)** → **[`LAB_COMPLETAO_RUNBOOK.pt_BR.md`](LAB_COMPLETAO_RUNBOOK.pt_BR.md)** → **[`LAB_OP_HOST_PERSONAS.pt_BR.md`](LAB_OP_HOST_PERSONAS.pt_BR.md)** (ENT / PRO / edge / ponte + knobs Ansible).
6. **Só stack privado:** **[`PRIVATE_STACK_SYNC_RITUAL.pt_BR.md`](PRIVATE_STACK_SYNC_RITUAL.pt_BR.md)** · **`scripts/private-git-sync.ps1`** (**`-Push`** quando os espelhos têm de alinhar) · **[ADR 0040](../adr/0040-assistant-private-stack-evidence-mirrors-default.md)** (EN).
7. **Onde vivem os docs (LAB-PB vs LAB-OP):** **[`OPERATOR_LAB_DOCUMENT_MAP.pt_BR.md`](OPERATOR_LAB_DOCUMENT_MAP.pt_BR.md)**.
8. **Tokens de sessão em inglês:** [`.cursor/rules/session-mode-keywords.mdc`](../../.cursor/rules/session-mode-keywords.mdc) — escrever os tokens **exatamente** (ex.: **`completao`**, **`private-stack-sync`**, **`short`** / **`token-aware`**).

## Router de tarefas (um salto)

| Se o operador quer… | Abrir primeiro (depois seguir links lá dentro) |
| ------------------- | ----------------------------------------------- |
| **Entregar código / corrigir CI** | **`TOKEN_AWARE_SCRIPTS_HUB`** §1 → **`check-all.ps1`**; bullets de merge/PR no **`AGENTS.md`** |
| **Docs / hubs / MAP** | skill **`doc-hubs-plans-sync`** · **`docs/README.md`** *Interno e referência* · par **`*.pt_BR.md`** |
| **Smoke de lab / completão** | **`COMPLETAO_OPERATOR_PROMPT_LIBRARY`** (**`completao`** + **`tier:…`**) · **`LAB_COMPLETAO_FRESH_AGENT_BRIEF`** · **`lab-completao-workflow.mdc`** · **`LAB_COMPLETAO_RUNBOOK`** · **`scripts/completao-chat-starter.ps1`** |
| **Ansible / Podman / personas** | **`LAB_OP_HOST_PERSONAS`** · **`ops/automation/ansible/README.md`** |
| **Inventário homelab / lote SSH** | **`lab-op-hosts.manifest.json`** em `docs/private/` (se existir) · **`LAB_OP_PRIVILEGED_COLLECTION.md`** · **`OPERATOR_LAB_DOCUMENT_MAP`** |
| **Fecho do Git empilhado em `docs/private/`** | **`PRIVATE_STACK_SYNC_RITUAL`** · **`private-git-sync.ps1`** |
| **Recuperação / “descobre aí”** | **`operator-investigation-before-blocking.mdc`** · skill **`operator-recovery-investigation`** |

## Cinco coisas inegociáveis (não “esquecer” em chat novo)

1. **`docs/private/`** existe no workspace → **`read_file` / `list_dir` é permitido**; **nunca** colar segredos ou identificadores de LAN em arquivos **versionados** ou PRs públicos (**`PRIVATE_OPERATOR_NOTES.md`**).
2. **Clone canónico no PC dev Windows principal** — **sem** **`clean-slate`**, **`git filter-repo`** ou **`git reset --hard`** de rotina na árvore do produto (**`PRIMARY_WINDOWS_WORKSTATION_PROTECTION.md`**).
3. **`completao`** — quando couber no âmbito, usar **`lab-completao-orchestrate.ps1 -Privileged`** na raiz do repo; o **manifest** define **`completaoEngineMode` / `completaoSkipEngineImport`** para hosts só contêiner (**`LAB_COMPLETAO_RUNBOOK`**).
4. **Conselho sobre merge / PR / “o que segue”** — **`git fetch`** primeiro (**`git-pr-sync-before-advice.mdc`**).
5. **Espelhos privados** — quando o sync é óbvio, correr **`private-git-sync.ps1 -Push`** e **reportar** erros concretos de SSH/mount (**ADR 0040**, **`operator-evidence-backup-no-rhetorical-asks.mdc`**).

## Produto vs operador (por preocupação)

Perguntas de compliance e capacidade para **compradores / DPO / CISO** começam no **[`MAP.pt_BR.md`](../MAP.pt_BR.md)** ([EN](../MAP.md)), não em `docs/plans/` (regra de tier externo: **ADR 0004**).

## Relacionados (mapa mental, não duplicar)

| Artefato | Função |
| -------- | ------ |
| **`AGENTS.md`** | Contrato longo canônico do assistente |
| **`CURSOR_AGENT_POLICY_HUB`** | Fase B — mesmo índice, clicável |
| **`TOKEN_AWARE_SCRIPTS_HUB`** | Mapa script ↔ keyword ↔ skill |
| **`OPERATOR_LAB_DOCUMENT_MAP`** | Índice LAB-PB vs LAB-OP |
| **`LAB_OP_HOST_PERSONAS`** | Intenção LAB-NODE-01 / LAB-NODE-02 / pi / LAB-NODE-03 vs automação |
| **`COMPLETAO_OPERATOR_PROMPT_LIBRARY.md`** | Taxonomia de chat **`completao`** + **`tier:`** + **`completao-chat-starter.ps1`** |

Ao acrescentar um **tema recorrente novo**, incluir **uma linha** no Quick index do **`AGENTS.md`** e no **`CURSOR_AGENT_POLICY_HUB`** na **mesma alteração**.
