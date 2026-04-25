# Escada de arranque operador + agente (token-aware, pouco contexto)

**English:** [OPERATOR_AGENT_COLD_START_LADDER.md](OPERATOR_AGENT_COLD_START_LADDER.md)

## Objetivo

Oferecer **um caminho ordenado** para um **chat novo** (sem memória do transcript) ainda assim chegar ao **hub certo primeiro**, sem reler o [`AGENTS.md`](../../AGENTS.md) inteiro. Esta página é só **navegação + regras mínimas** — o comportamento continua no **código**, **TECH_GUIDE** e runbooks ligados.

## Ordem de leitura (profundidade conforme a tarefa)

1. **Este arquivo** — router de tarefas + sete regras inegociáveis abaixo.
2. **[`AGENTS.md`](../../AGENTS.md)** — tabela Quick index (tema → primeiro doc); os bullets longos são o contrato.
3. **[`CURSOR_AGENT_POLICY_HUB.pt_BR.md`](CURSOR_AGENT_POLICY_HUB.pt_BR.md)** — os mesmos temas com caminhos **clicáveis** para `.cursor/rules`, `.cursor/skills` e `docs/ops/`.
4. **[`TOKEN_AWARE_SCRIPTS_HUB.pt_BR.md`](TOKEN_AWARE_SCRIPTS_HUB.pt_BR.md)** — que **`scripts/*.ps1`** ligam a keywords, skills e runbooks.
5. **Só lab / completão:** **[`LAB_COMPLETAO_FRESH_AGENT_BRIEF.pt_BR.md`](LAB_COMPLETAO_FRESH_AGENT_BRIEF.pt_BR.md)** → **[`LAB_COMPLETAO_RUNBOOK.pt_BR.md`](LAB_COMPLETAO_RUNBOOK.pt_BR.md)** → **[`LAB_OP_HOST_PERSONAS.pt_BR.md`](LAB_OP_HOST_PERSONAS.pt_BR.md)** (ENT / PRO / edge / ponte + knobs Ansible).
6. **Só stack privado:** **[`PRIVATE_STACK_SYNC_RITUAL.pt_BR.md`](PRIVATE_STACK_SYNC_RITUAL.pt_BR.md)** · **`scripts/private-git-sync.ps1`** (**`-Push`** quando os espelhos têm de alinhar) · **[ADR 0040](../adr/0040-assistant-private-stack-evidence-mirrors-default.md)** (EN).
7. **Onde vivem os docs (LAB-PB vs LAB-OP):** **[`OPERATOR_LAB_DOCUMENT_MAP.pt_BR.md`](OPERATOR_LAB_DOCUMENT_MAP.pt_BR.md)**.
8. **Tokens de sessão em inglês:** [`.cursor/rules/session-mode-keywords.mdc`](../../.cursor/rules/session-mode-keywords.mdc) — escrever os tokens **exatamente** (ex.: **`completao`**, **`legal-dossier-update`**, **`private-stack-sync`**, **`short`** / **`token-aware`**).

## Router de tarefas (um salto)

| Se o operador quer… | Abrir primeiro (depois seguir links lá dentro) |
| ------------------- | ----------------------------------------------- |
| **Entregar código / corrigir CI** | **`TOKEN_AWARE_SCRIPTS_HUB`** §1 → **`check-all.ps1`**; bullets de merge/PR no **`AGENTS.md`** |
| **Qual script / wrapper usar?** (evitar reinventar shell longo) | **`repo-scripts-wrapper-ritual.mdc`** · **`TOKEN_AWARE_SCRIPTS_HUB`** · **`check-all-gate.mdc`** · skill **`token-aware-automation`** |
| **Docs / hubs / MAP** | skill **`doc-hubs-plans-sync`** · **`docs/README.md`** *Interno e referência* · par **`*.pt_BR.md`** |
| **Smoke de lab / completão** | **`COMPLETAO_OPERATOR_PROMPT_LIBRARY`** (**`completao`** + **`tier:…`**) · **`LAB_COMPLETAO_FRESH_AGENT_BRIEF`** · **`lab-completao-workflow.mdc`** · **`LAB_COMPLETAO_RUNBOOK`** · **`scripts/completao-chat-starter.ps1`** |
| **Ansible / Podman / personas** | **`LAB_OP_HOST_PERSONAS`** · **`ops/automation/ansible/README.md`** |
| **Inventário homelab / lote SSH** | **`lab-op-hosts.manifest.json`** em `docs/private/` (se existir) · **`LAB_OP_PRIVILEGED_COLLECTION.md`** · **`OPERATOR_LAB_DOCUMENT_MAP`** |
| **Fecho do Git empilhado em `docs/private/`** | **`PRIVATE_STACK_SYNC_RITUAL`** · **`private-git-sync.ps1`** |
| **Evidência jurídica / trabalhista privada** (importação, atualizações tipo CAT/INSS, novo paste) | Token de sessão **`legal-dossier-update`** · **`dossier-update-on-evidence.mdc`** · **`legal_dossier/`** + **`raw_pastes/`** em `docs/private/` · § *Presilha token → regra (dossiê jurídico)* abaixo |
| **Recuperação / “descobre aí”** | **`operator-investigation-before-blocking.mdc`** · skill **`operator-recovery-investigation`** |
| **Gmail / webmail / redes / caixa ou anexo** (mesmo PC que **SSH**; sessão quente ou fria + **SSO Google** quando o site oferecer) | **`cursor-browser-social-sso-hygiene.mdc`** (*Contrato único* + *Gmail e webmail*) · **`operator-browser-warm-session.mdc`** · **`operator-direct-execution.mdc`** §5 — **tentar** MCP e clique **SSO** antes de negar; **só depois** pedir interação humana uma vez; PDFs → **`docs/private/`** + **`read_file`** |

### Presilha token → regra → wrapper (**`completao`**)

Use este **formato da primeira mensagem** para que um **`lab-completao-workflow.mdc`** **situacional** ainda “pegue” (via **globs** ou **`@`** explícito), sem recarregar a regra em todo chat irrelevante:

1. Linha 1: token em inglês **`completao`** (opcional na mesma mensagem: **`short`** / **`token-aware`** para narrativa curta).
2. Linha 2: **`tier:…`** exatamente como em **`COMPLETAO_OPERATOR_PROMPT_LIBRARY.md`**. Bloco para colar: **`.\scripts\completao-chat-starter.ps1 -Help`** ou correr com **`-Tier …`** para imprimir linhas copiáveis.
3. Se o fio **não** estiver a mexer em **`scripts/lab-completao*`** nem **`docs/ops/LAB_COMPLETAO*`**, **anexar** **`.cursor/rules/lab-completao-workflow.mdc`** com **`@`** para trazer a regra completa para o contexto.
4. **Automação por omissão (operador corre, assistente interpreta logs):** na raiz do repo **`.\scripts\lab-completao-orchestrate.ps1 -Privileged`** — depois **`read_file`** / resumir em **`docs/private/homelab/reports/`** conforme **`LAB_COMPLETAO_RUNBOOK.md`**. **Não** substituir o orquestrador por **`ssh`** ad hoc salvo se o operador optar explicitamente por isso.

### Presilha token → regra (**`legal-dossier-update`**)

Para **evidência jurídica / trabalhista** em **`docs/private/legal_dossier/`** ou **`docs/private/raw_pastes/`**, mantém a regra pesada **situacional**, mas **vinculante** quando precisas dela:

1. Linha 1: token em inglês **`legal-dossier-update`** (opcional **`short`** / **`token-aware`**).
2. **`read_file`** em **`.cursor/rules/dossier-update-on-evidence.mdc`** — usar **`@dossier-update-on-evidence.mdc`** se o editor ainda não anexou a regra (caminhos fora dos **globs** não carregam sozinhos).
3. Executar a **checklist ordenada** dentro dessa regra (índice → sumário executivo → risco se aplicável → **`OPERATOR_RETEACH.md`** → Git empilhado em **`docs/private/`** + **`private-git-sync.ps1`** quando a política pedir).
4. **Nunca** colocar nomes de partes, números de autos ou identificadores de LAN em **docs versionados**, issues ou PRs públicos.

## Sete coisas inegociáveis (não “esquecer” em chat novo)

1. **`docs/private/`** existe no workspace → **`read_file` / `list_dir` é permitido**; **nunca** colar segredos ou identificadores de LAN em arquivos **versionados** ou PRs públicos (**`PRIVATE_OPERATOR_NOTES.md`**).
2. **Clone canônico no PC dev Windows principal** — **sem** **`clean-slate`**, **`git filter-repo`** ou **`git reset --hard`** de rotina na árvore do produto (**`PRIMARY_WINDOWS_WORKSTATION_PROTECTION.md`**).
3. **`completao`** — quando couber no âmbito, usar **`lab-completao-orchestrate.ps1 -Privileged`** na raiz do repo; o **manifest** define **`completaoEngineMode` / `completaoSkipEngineImport`** para hosts só contêiner (**`LAB_COMPLETAO_RUNBOOK`**).
4. **Conselho sobre merge / PR / “o que segue”** — **`git fetch`** primeiro (**`git-pr-sync-before-advice.mdc`**).
5. **Espelhos privados** — quando o sync é óbvio, correr **`private-git-sync.ps1 -Push`** e **reportar** erros concretos de SSH/mount (**ADR 0040**, **`operator-evidence-backup-no-rhetorical-asks.mdc`**).
6. **Prosa em português = pt-BR por padrão** — **`*.pt_BR.md`**, Markdown em PT em **`docs/private/`** e parágrafos que o assistente escreve **não** podem ir para **pt-PT** “sem querer.” Exceções só conforme **`.cursor/rules/docs-locale-pt-br-contract.mdc`**. Depois de edições grandes em pt-BR, rodar **`uv run pytest tests/test_docs_pt_br_locale.py -v`**.
7. **Alcance homelab / LAB-OP a partir do terminal integrado** — no **PC de dev**, o terminal integrado do Cursor é a **mesma máquina e LAN** que o teu shell habitual para **`ssh`**, **`scp`**, **`curl` HTTP no lab**, etc. (**`homelab-ssh-via-terminal.mdc`**). Antes de dizer **“sem acesso remoto”** ou **“não consigo chegar nos hosts do lab”**, usar **`read_file`** em **`docs/private/homelab/AGENT_LAB_ACCESS.md`** (se existir) e seguir **aliases `Host` do SSH / caminhos do manifest** nos docs privados — **não** inventar hostnames reais, IPs nem caminhos de `$HOME` em arquivos **versionados**. Um prompt de notebook tipo **`usuario@Latitude-…` no chat** **não** prova que o assistente **não** possa usar **`ssh`** para hosts do manifest a partir deste workspace.

## Produto vs operador (por preocupação)

Perguntas de compliance e capacidade para **compradores / DPO / CISO** começam no **[`MAP.pt_BR.md`](../MAP.pt_BR.md)** ([EN](../MAP.md)), não em `docs/plans/` (regra de tier externo: **ADR 0004**).

## Relacionados (mapa mental, não duplicar)

| Artefato | Função |
| -------- | ------ |
| **`AGENTS.md`** | Contrato longo canônico do assistente |
| **`CURSOR_AGENT_POLICY_HUB`** | Fase B — mesmo índice, clicável |
| **`TOKEN_AWARE_SCRIPTS_HUB`** | Mapa script ↔ keyword ↔ skill |
| **`OPERATOR_LAB_DOCUMENT_MAP`** | Índice LAB-PB vs LAB-OP |
| **`LAB_OP_HOST_PERSONAS`** | Intenção T14 / Latitude / pi / mini-bt vs automação |
| **`COMPLETAO_OPERATOR_PROMPT_LIBRARY.md`** | Taxonomia de chat **`completao`** + **`tier:`** + **`completao-chat-starter.ps1`** |

Ao acrescentar um **tema recorrente novo**, incluir **uma linha** no Quick index do **`AGENTS.md`** e no **`CURSOR_AGENT_POLICY_HUB`** na **mesma alteração**.
