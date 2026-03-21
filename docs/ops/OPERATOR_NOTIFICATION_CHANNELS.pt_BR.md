# Canais de notificação do operador — vários meios de contato

**English:** [OPERATOR_NOTIFICATION_CHANNELS.md](OPERATOR_NOTIFICATION_CHANNELS.md)

**Objetivo:** Quando o **CI falha**, um **job longo termina** ou um **humano precisa voltar** ao Cursor, use **pelo menos dois canais independentes** para um não bloquear o outro (app em DND, conta errada, etc.). Este doc é **política + notas de integração** — **sem segredos** no repositório (tokens em variável de ambiente, `docs/private/` ou **secrets** do GitHub Actions).

**Âmbito:** Alertas para **mantenedor/operador** (você + automações). Notificações de **produto** (fim de scan, etc.) seguem o plano **Notifications** em [PLANS_TODO.md](../plans/PLANS_TODO.md) (ordem 6) — pode reutilizar a mesma lista de canais.

---

## 1. Pilha recomendada (menos atrito → mais montagem)

| Prioridade | Canal        | Por quê                                                                                                      | Uso típico                                                                                             |
| ---------- | -----        | -------                                                                                                      | -----------                                                                                            |
| **A**      | **GitHub**   | Já ligado ao repositório; **app móvel** para assign, review, **workflow falho**, Dependabot, Security.       | Watch em **data-boar**; falhas em **Actions**; opcional **Issue** aberta por automação com `@mention`. |
| **B**      | **Slack**    | **Webhook** ou bot; fácil com `curl` no GitHub Actions.                                                      | Canal `#data-boar-ops`; secret `SLACK_WEBHOOK_URL`.                                                    |
| **C**      | **Telegram** | **Bot API HTTP**; token + **chat_id**; scripts pequenos.                                                     | BotFather → token como secret; mensagem para você ou grupo.                                            |
| **D**      | **Signal**   | Privacidade forte; **mais operação** (dispositivo vinculado / `signal-cli` / imagens **signald** em Docker). | Opcional; ver §3. Respeite **Termos do Signal** e a legislação local.                                  |

**Mínimo prático:** **A + B** ou **A + C**. **Só A** já ajuda; dois canais reduzem “perdi o único ping”.

---

## 2. GitHub (linha de base recomendada)

- **Watch** no repositório (Actions, Security conforme preferir).
- **Workflow falho:** checks obrigatórios evitam merge silencioso; falhas aparecem no app e e-mail/push.
- **Automação → humano:** job agendado pode **abrir/comentar Issue** (`gh issue create` / API); você recebe notificação **padrão** no iPhone.

Use **GITHUB_TOKEN** no Actions (permissões no workflow).

---

## 3. Signal (Docker / CLI — avançado)

Configurações comuns usam **`signal-cli`** ou **`signald`** em **Docker**, com **dispositivo vinculado** ou fluxo de registro. O comportamento que descreveu (mensagens como **sua** identidade; “anotação” ao enviar para si / conversa consigo) é um padrão conhecido para **lembretes do operador** (análogo a “mensagens salvas” no Telegram).

### Riscos / cuidados

- **Operacional:** reinícios do container, pareamento/QR, recuperação de sessão.
- **Legal / ToS:** imagens auditadas; cumprimento dos termos do Signal.
- **Automação:** o agente no Cursor **não** guarda a sessão Signal; só **runners seus** (servidor em casa, script no laptop, CI com secrets **seus**) devem chamar a API.

**Não bloqueante:** trate Signal como **tier D** depois de GitHub + um webhook de mensagens.

---

## 4. Slack vs Telegram (comparação rápida)

|                         | Slack                        | Telegram                                   |
| ---                     | ---                          | ---                                        |
| **Montagem**            | App Slack → Incoming Webhook | BotFather → token; obter `chat_id` uma vez |
| **A partir do Actions** | `curl` POST JSON no webhook  | `sendMessage` na API do bot                |
| **Uso**                 | Bom se você já vive no Slack | Bom para **push direto** no celular        |

Um passo genérico “notify” pode tentar **Slack** e, se falhar, **Telegram** (sem loops infinitos).

---

## 5. Padrão multi-canal

1. **Primário:** GitHub (comentário em Issue ou check falho).
1. **Secundário:** Slack *ou* Telegram.
1. **Terciário opcional:** Signal (homelab até estabilizar).

**Não** commitar webhooks nem tokens; usar **secrets** do GitHub e/ou `.env` no `.gitignore`.

---

## 6. KPI snapshot + notificar (opcional)

Script base: [scripts/kpi-export.py](../../scripts/kpi-export.py) (requer `gh auth`). **Extensão em backlog:**

- Workflow **semanal** ou `workflow_dispatch`: gerar `kpi_snapshot.md`, **artefato**, ou enviar trecho ao Slack/Telegram.
- Evitar commit de snapshots com dados sensíveis; retenção curta de artefactos.

Ver [PLAN_READINESS_AND_OPERATIONS.md](../plans/PLAN_READINESS_AND_OPERATIONS.md) §4.7.

---

## 7. Documentos relacionados

- [BRANCH_AND_DOCKER_CLEANUP.md](ops/BRANCH_AND_DOCKER_CLEANUP.md) — higiene; §7 remote legado.
- [CODE_PROTECTION_OPERATOR_PLAYBOOK.md](../CODE_PROTECTION_OPERATOR_PLAYBOOK.md) — faixa A.
- [REMOTES_AND_ORIGIN.md](REMOTES_AND_ORIGIN.md) — `origin` vs legado.
- Cursor: **`.cursor/rules/operator-notification-channels.mdc`** e **`.cursor/skills/operator-notification-channels/SKILL.md`**.

---

*Última atualização: backlog ops — notificações multi-canal (Signal/Telegram/Slack/GitHub) + gancho de KPI.*
