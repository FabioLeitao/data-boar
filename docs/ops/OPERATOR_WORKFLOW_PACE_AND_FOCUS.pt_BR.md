# Fluxo do operador: ritmo, foco e quando dividir o trabalho

**English:** [OPERATOR_WORKFLOW_PACE_AND_FOCUS.md](OPERATOR_WORKFLOW_PACE_AND_FOCUS.md)

**Objetivo:** Um lugar para **pensar** como avançar rápido rumo a demo → beta → produção **sem** regressões acidentais de qualidade, e como isso se relaciona com **Wabbix**, **palavras-chave de sessão** e ajuda **paralela** opcional. **Não** substitui `PLANS_TODO.md` nem `TOKEN_AWARE_USAGE.md`.

---

## 1. Retomar depois de uma pausa (o que verificar primeiro)

1. **Estado do Git:** `git fetch` + `git status` — branch alinhado com `main` se estiver no meio de merge.
2. **PRs abertos:** `gh pr list --state open` — fechar ou integrar PRs antes de abrir fatia grande nova.
3. **CI:** Verde no PR relevante (UI do GitHub ou `gh pr checks`).
4. **Secrets** (ex.: Slack): **Settings → Secrets and variables → Actions** — `SLACK_WEBHOOK_URL` definido; depois **Actions → Slack operator ping (manual)** para confirmar entrega.

O assistente **não** “lembra” do chat de ontem nem da RAM da sua máquina sem você colar saída ou rodar comandos nesta sessão.

---

## 2. Dois “subagentes” (código vs docs) — faz sentido?

| Abordagem                                                                                | Quando ajuda                                                 | Quando atrapalha                                                                                                                                                                         |
| ---------                                                                                | ----------                                                   | ----------------                                                                                                                                                                         |
| **Uma sessão Cursor + palavra-chave clara** (`feature`, `docs`, `houseclean`, `backlog`) | Um diff coerente, uma narrativa de PR, `check-all` por fatia | Sessões longas misturam assuntos se você não nomear o modo                                                                                                                               |
| **Subagentes Task** (explorar vs implementar)                                            | Exploração rápida em árvores grandes; isolamento em buscas   | Dois agentes podem sugerir edições sobrepostas; você ainda integra um branch                                                                                                             |
| **Divisão fixa “agente código” vs “agente docs”**                                        | Parece organizado                                            | **Na prática costuma ser pior:** contexto duplicado, instruções conflitantes, dois PRs brigando pelos mesmos arquivos; **regras/skills já** cobrem barra de qualidade e política de docs |

**Recomendação prática:** manter **um** fio de implementação por branch/PR. Usar **palavras-chave** para **escopo** da sessão. Usar **Task** para **exploração só leitura** ou pesquisa paralela, não como segundo autor no mesmo PR sem combinar (ex.: um branch só docs, outro só código, merge em ordem).

**Documentação vs código** num mesmo release: **commits separados** (`documentation` vs `feature`, conforme `execution-priority-and-pr-batching.mdc`), não dois “agentes” com memórias separadas.

---

## 3. Novos comandos no chat (taxonomia)

A tabela em **`.cursor/rules/session-mode-keywords.mdc`** é **pequena e só em inglês** de propósito. Multiplicar tokens (`wabbix-slice`, `demo-prep`, …) costuma **aumentar carga mental** (“qual token hoje?”).

**Prefira:**

- **`backlog`** + **item nomeado** na mensagem (“próxima linha Wabbix: API key segura por padrão”).
- **`feature`** + referência a **`PLANS_TODO.md`**.
- **`docs`** para passes só de documentação.

**Se** um dia entrar token novo, deve ser **um** escopo claro, na mesma tabela, e uso consistente — **não** sinônimo de modo que já existe.

---

## 4. Ritmo: Wabbix, crítico primeiro, token-aware, demo → prod

- **Ordem do backlog:** `docs/plans/PLANS_TODO.md` e o mapeamento Wabbix em `docs/plans/WABBIX_ANALISE_2026-03-23_EVOLUTIVA.md` (e `WABBIX_IN_REPO_BASELINE.md` para revisores).
- **Crítico primeiro:** segurança/regressão **bloqueante** e **CI verdadeiro** antes de refino cosmético.
- **Token-aware** (`TOKEN_AWARE_USAGE.md`): fatias pequenas com testes, não reescrita transversal num PR só.
- **Demo → beta → produção:** alinhar checklists (`HOMELAB_VALIDATION.md`, releases, `VERSIONING.md`) com o que **de fato** está no pitch/README; evitar prometer o que ainda está em `Deferred` no `PLANS_TODO.md`.

---

## 5. Estudo, certificação e exaustão

- Cadência **CWL / cyber** está no **`study-check`** e em `docs/plans/PORTFOLIO_AND_EVIDENCE_SOURCES.md` (seção 3.x).
- **Blue team / certificação** **não** é token separado no Cursor — use **`study-check`** para ritmo e guarde **marcos pessoais** (datas, módulos) em **`docs/private/`** ou calendário para o assistente **quando você colar ou pedir**.
- **Pausas naturais:** depois de `check-all` verde, PR mergeado ou fim do dia — trocar de contexto (estudo vs código) é **deliberado**, não falta de foco.

---

## 6. IDE / OOM / hardware

**Travamento ou OOM** no Cursor costuma ser **pressão de memória local** (chat grande, muitos arquivos, extensões). Mais **RAM** no notebook ajuda; **mensagens menores**, **fechar** abas e **dividir** o trabalho em sessões também ajuda. **Não** é julgamento sobre o projeto ou sobre seu ritmo.

---

## 7. Próximos passos concretos (checklist do operador)

1. **Higiene de PR:** listar PRs abertos; mergear ou fechar os obsoletos **depois** de CI verde / `check-all` na branch certa.
2. **Slack:** com `SLACK_WEBHOOK_URL` definido, rodar **Actions → Slack operator ping (manual)** uma vez; confirmar no canal.
3. **Loop Wabbix:** responder com **evidências** (caminhos em `WABBIX_IN_REPO_BASELINE.md`); escolher **uma** linha seguinte na tabela evolutiva como fatia **`feature`** ou **`backlog`** bem definida.
4. **Demo:** reler `PLANS_TODO.md` e `SPRINTS_AND_MILESTONES.md`; uma passagem **homelab** com `HOMELAB_VALIDATION.md` antes de chamar o build de “pronto para demo”.
5. **Próxima sessão:** começar com **`pmo-view`** ou colar a seção relevante de **`PLANS_TODO.md`** para alinhar prioridade.

---

## 8. Slack AFK + falha de CI (canal B)

Quando estiver **longe do teclado**, **GitHub mobile (canal A)** + **Slack (canal B)** dão redundância: falhas de CI e pings manuais chegam sem precisares ficar no Cursor.

- **Setup:** [OPERATOR_NOTIFICATION_CHANNELS.pt_BR.md](OPERATOR_NOTIFICATION_CHANNELS.pt_BR.md) §4.1 — `SLACK_WEBHOOK_URL` nos secrets; **Actions → Slack operator ping (manual)** para smoke; **Slack CI failure notify** quando o workflow **CI** termina com **failure** (mesmo secret).
- **Produto / scan-complete:** reutilização opcional do webhook na app (USAGE) — separado dos Actions.
- **Checklist de conclusão:** secret definido → ping manual OK → (opcional) validar o notify com uma falha de CI de teste ou confiar no YAML + secret.

---

## 9. Auto-merge do GitHub (recomendação)

**Padrão: manter auto-merge desligado** no fluxo habitual. Preferir merge **explícito** com checks verdes e PR **mergeable**, usando **`pr-merge-when-green.ps1`** ou revisão humana — alinha entrega deliberada, sem cerimônia desnecessária e sem merges surpresa.

**Quando pode ajudar:** PRs mecânicos de baixo risco (ex. **Dependabot** já triado), com checks obrigatórios — ativar **por PR** na UI, não como hábito global.

**Por evitar auto-merge cego:** PRs de feature beneficiam de **olhar final**; CI não apanha todo o risco semântico.

---

## 10. Palavras-chave de sessão e “subagents” (onde está documentado)

- **Tokens em inglês** (`feature`, `docs`, `backlog`, `study-check`, `pmo-view`, …): **`.cursor/rules/session-mode-keywords.mdc`** (tabela canônica).
- **Código vs docs vs Task só exploração:** esta seção §2 e [TOKEN_AWARE_USAGE.md](../plans/TOKEN_AWARE_USAGE.md).

---

## 11. Documentação relacionada

- [COMMIT_AND_PR.pt_BR.md](COMMIT_AND_PR.pt_BR.md) — PR, merge, nota sobre auto-merge.
- [TOKEN_AWARE_USAGE.md](../plans/TOKEN_AWARE_USAGE.md) — fatias token-aware.
- [WABBIX_ANALISE_2026-03-23_EVOLUTIVA.md](../plans/WABBIX_ANALISE_2026-03-23_EVOLUTIVA.md) — temas priorizados.
- [OPERATOR_NOTIFICATION_CHANNELS.pt_BR.md](OPERATOR_NOTIFICATION_CHANNELS.pt_BR.md) — Slack + canal A (GitHub).
