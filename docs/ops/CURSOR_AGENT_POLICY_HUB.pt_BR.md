# Hub de políticas Cursor / agente (só mapa)

**English:** [CURSOR_AGENT_POLICY_HUB.md](CURSOR_AGENT_POLICY_HUB.md)

Esta página é a **fase B de consolidação**: o mesmo mapa **tema → primeiro lugar a olhar** que o **Quick index** no [`AGENTS.md`](../../AGENTS.md) na raiz, mas com **caminhos clicáveis** para rules, skills e docs de operador. **Não** substitui os bullets narrativos no [`AGENTS.md`](../../AGENTS.md)—atualize **as duas** tabelas (Quick index e esta) quando acrescentar uma linha de política.

## Quick index (com links)

| Tema | Onde olhar primeiro |
| ---- | ------------------- |
| **`.cursor/` / `.vscode/` / `.github/` / caches** — o que é versionado vs gitignore | [CURSOR_AND_EDITOR_ARTIFACTS.pt_BR.md](CURSOR_AND_EDITOR_ARTIFACTS.pt_BR.md) |
| Leitura de **`docs/private/`** / nunca bloquear o agente | [Primeiro bullet do `AGENTS.md` depois do Quick index](../../AGENTS.md) · [`.cursor/rules/agent-docs-private-read-access.mdc`](../../.cursor/rules/agent-docs-private-read-access.mdc) · [`docs/PRIVATE_OPERATOR_NOTES.md`](../PRIVATE_OPERATOR_NOTES.md) |
| Chat **pt-BR** / locale (PT em `docs/private/` = pt-BR; prosa só EN → `en-US`) | [`.cursor/rules/operator-chat-language.mdc`](../../.cursor/rules/operator-chat-language.mdc) · [`.cursor/rules/operator-chat-language-pt-br.mdc`](../../.cursor/rules/operator-chat-language-pt-br.mdc) · [`.cursor/rules/docs-pt-br-locale.mdc`](../../.cursor/rules/docs-pt-br-locale.mdc) · [`.cursor/skills/operator-dialogue-pt-br/SKILL.md`](../../.cursor/skills/operator-dialogue-pt-br/SKILL.md) |
| **Palavras-chave de sessão** (deps, feature, `es-find`, …) | [`.cursor/rules/session-mode-keywords.mdc`](../../.cursor/rules/session-mode-keywords.mdc) |
| **PII / segredos / árvore pública** | [`.cursor/rules/private-pii-never-public.mdc`](../../.cursor/rules/private-pii-never-public.mdc) · [`PII_PUBLIC_TREE_OPERATOR_GUIDE.md`](PII_PUBLIC_TREE_OPERATOR_GUIDE.md) · fluxo **`pii-fresh-audit`** (ver [`AGENTS.md`](../../AGENTS.md)) |
| **Comercial / confidencial** | [`.cursor/rules/confidential-commercial-never-tracked.mdc`](../../.cursor/rules/confidential-commercial-never-tracked.mdc) |
| **GitHub / PR / merge** | [`.cursor/rules/git-pr-sync-before-advice.mdc`](../../.cursor/rules/git-pr-sync-before-advice.mdc) · [`CONTRIBUTING.md`](../../CONTRIBUTING.md) · [`COMMIT_AND_PR.md`](COMMIT_AND_PR.md) |
| **Ordem de publicação de release** (tag + GitHub + Hub antes do beta no `main`) | [`.cursor/rules/release-publish-sequencing.mdc`](../../.cursor/rules/release-publish-sequencing.mdc) · [`VERSIONING.md`](../VERSIONING.md) (*Assistente / automacao*) · palavra de sessao **`release-ritual`** |
| **Investigação / recuperação (“descobre aí”)** | [`.cursor/rules/operator-investigation-before-blocking.mdc`](../../.cursor/rules/operator-investigation-before-blocking.mdc) · [`.cursor/skills/operator-recovery-investigation/SKILL.md`](../../.cursor/skills/operator-recovery-investigation/SKILL.md) |
| **Browser Cursor / SSO / separadores** | [`.cursor/rules/cursor-browser-social-sso-hygiene.mdc`](../../.cursor/rules/cursor-browser-social-sso-hygiene.mdc) · [`.cursor/skills/cursor-browser-social-session/SKILL.md`](../../.cursor/skills/cursor-browser-social-session/SKILL.md) |
| **Homelab / SSH / LAN** | [`.cursor/rules/homelab-ssh-via-terminal.mdc`](../../.cursor/rules/homelab-ssh-via-terminal.mdc) · [`docs/private/homelab/AGENT_LAB_ACCESS.md`](../private/homelab/AGENT_LAB_ACCESS.md) (quando existir) |
| **Merge autónomo / LAB-OP** | [`.cursor/rules/agent-autonomous-merge-and-lab-ops.mdc`](../../.cursor/rules/agent-autonomous-merge-and-lab-ops.mdc) |
| **Ritual de sessão do assistente** (`main` sincronizado, stack privado, próximos passos) | [`AGENTS.md`](../../AGENTS.md) (*Assistant session ritual*) · [`.cursor/rules/agent-session-ritual-sync-main-and-private-stack.mdc`](../../.cursor/rules/agent-session-ritual-sync-main-and-private-stack.mdc) · [`PRIVATE_STACK_SYNC_RITUAL.md`](PRIVATE_STACK_SYNC_RITUAL.md) |
| **“Hoje” situacional** (relógio da estação, âncora do today-mode) | [`AGENTS.md`](../../AGENTS.md) (*Workstation calendar clock*) · [`today-mode/README.pt_BR.md`](today-mode/README.pt_BR.md) (*Para assistentes*) · [`.cursor/rules/agent-session-ritual-sync-main-and-private-stack.mdc`](../../.cursor/rules/agent-session-ritual-sync-main-and-private-stack.mdc) |
| **Prioridade de execução / lotes de PR** | [`.cursor/rules/execution-priority-and-pr-batching.mdc`](../../.cursor/rules/execution-priority-and-pr-batching.mdc) · [`docs/plans/PLANS_TODO.md`](../plans/PLANS_TODO.md) |
| **Carreira / LinkedIn (privado)** | [`.cursor/rules/operator-career-private-layout.mdc`](../../.cursor/rules/operator-career-private-layout.mdc) · [`docs/private/author_info/career/README.pt_BR.md`](../private/author_info/career/README.pt_BR.md) |
| **Git empilhado em `docs/private/`** | [`PRIVATE_LOCAL_VERSIONING.md`](PRIVATE_LOCAL_VERSIONING.md) · mini-plano [`docs/private/ops/CURSOR_CONSOLIDATION_MINI_PLAN.pt_BR.md`](../private/ops/CURSOR_CONSOLIDATION_MINI_PLAN.pt_BR.md) |
| **Risco / não destrutivo vs destrutivo** | Parágrafo **Risk posture** no [`AGENTS.md`](../../AGENTS.md) (logo abaixo da tabela Quick index) |
| **Execução direta** (pedido claro de fechar — evitar confirmação redundante) | [`.cursor/rules/operator-direct-execution.mdc`](../../.cursor/rules/operator-direct-execution.mdc) |
| **Verdade em publicação** (sem inventar datas/fatos; **capturar permalinks** quando der) | [`.cursor/rules/publication-truthfulness-no-invented-facts.mdc`](../../.cursor/rules/publication-truthfulness-no-invented-facts.mdc) · [`docs/private/social_drafts/editorial/SOCIAL_HUB.md`](../private/social_drafts/editorial/SOCIAL_HUB.md) (*Política de data* + inventário) |

## Runbooks relacionados

- [`OPERATOR_SESSION_SHORTHANDS.md`](OPERATOR_SESSION_SHORTHANDS.md) — palavras-chave de sessão e índice `lab-op`
- [`TOKEN_AWARE_SCRIPTS_HUB.md`](TOKEN_AWARE_SCRIPTS_HUB.md) — scripts alinhados a keywords / skills
- [`OPERATOR_LAB_DOCUMENT_MAP.md`](OPERATOR_LAB_DOCUMENT_MAP.md) — mapa de docs de lab e agente
