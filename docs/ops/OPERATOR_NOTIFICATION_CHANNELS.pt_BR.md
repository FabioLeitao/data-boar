# Canais de notificação do operador — vários meios de contato

**English:** [OPERATOR_NOTIFICATION_CHANNELS.md](OPERATOR_NOTIFICATION_CHANNELS.md)

**Objetivo:** Quando o **CI falha**, um **job longo termina** ou um **humano precisa voltar** ao Cursor, use **pelo menos dois canais independentes** para um não bloquear o outro (app em DND, conta errada, etc.). Este doc é **política + notas de integração** — **sem segredos** no repositório (tokens em variável de ambiente, `docs/private/` ou **secrets** do GitHub Actions).

**Âmbito:** Alertas para **mantenedor/operador** (você + automações). Notificações de **produto** (fim de scan, etc.) seguem o plano **Notifications** em [PLANS_TODO.md](../plans/PLANS_TODO.md) (ordem 6) — pode reutilizar a mesma lista de canais.

**Sequenciamento (mantenedor):** Por ora, **só o canal A** — app **GitHub** no celular + watch/e-mail nas configurações — **basta** para PRs, reviews, Dependabot, Security e **Actions com falha**. Ajuste em **GitHub → Configurações → Notificações** e no app oficial iOS/Android. Quando quiser **redundância** ou alertas no estilo “chat”, acrescente **B** (Slack) ou **C** (Telegram) conforme §1; **D** (Signal) segue **opcional** e com mais operação. **Este doc é o lembrete de integração** para esses próximos passos.

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
- **Descarregar no LAB‑OP:** Rodar a imagem Docker do Signal em **outra máquina do lab** (não no PC de dev) é um bom encaixe: o workstation manda **`curl`** (cabeçalhos + corpo JSON) para a API REST na LAN — o mesmo estilo de integração que **Uptime Kuma**. Trave o serviço na **rede privada**; URL/token só em **`docs/private/notify/`** (gitignored). Ver **[private.example/notify/README.md](../private.example/notify/README.md)** § *Signal on a different machine*.

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

## 7. Resumo fim do dia / fim do sprint (SMS, e-mail, chat)

**O que o assistente não faz:** O agente no Cursor **não** envia **SMS** nem **e-mail** para o seu celular ou caixa de entrada. Não há integração com operadora ou SMTP a partir do chat. Qualquer “aviso” precisa rodar no **seu** ambiente: **GitHub Actions**, um **servidor em casa** ou um **script** que você executa na máquina.

**O que dá para montar (padrão recomendado):**

| Parte | Opções |
| ----- | ------ |
| **Gatilho** | **`workflow_dispatch`** (“enviar resumo agora”), **cron** (ex.: dias úteis 18h no seu fuso) para fim do dia, ou **no merge de release** / regra de calendário para fim de sprint. |
| **Resumo curto** | Primeiras linhas de **`git log`** desde a última tag ou `--since=…`; opcional **`python scripts/plans-stats.py`** para contagens do painel de planos; um parágrafo com “principais ações / principais mudanças” (você ou um modelo preenche). |
| **Release notes** | Link para **`docs/releases/X.Y.Z.md`** no `main` (ou **artefato** do workflow); não colar segredos nem URLs internas. |
| **Progresso / visão PM** | Colar a tabela **Kanban** de [SPRINTS_AND_MILESTONES.pt_BR.md](../plans/SPRINTS_AND_MILESTONES.pt_BR.md) ou um bloco **Mermaid `gantt`** em **texto puro** na mensagem. O assistente pode **rascunhar** esse Markdown no chat; o **CI** envia — sem copiar na mão se o workflow montar o corpo. |
| **SMS** | API **HTTP** (ex.: **Twilio**); **secrets** no GitHub para credenciais; custo e conformidade são **seus**. |
| **E-mail** | SMTP via Action (ex.: **`dawidd6/action-send-mail`**) ou API REST do provedor; **secrets** para credenciais. |
| **Menos atrito** | **Telegram** `sendMessage` ou webhook do **Slack** (como nas §2–§4) — muitas vezes basta para “fim do dia” sem taxa de SMS. |

**Twilio (API de SMS — opcional):** **Twilio** é um provedor americano de **CPaaS** (*Communications Platform as a Service*): uma **API HTTP** para enviar **SMS** em vários países sem contrato direto com cada operadora — por isso aparece muito em tutoriais e combina com **GitHub Actions** ou um script **`curl`**. Em geral você paga **por mensagem** (e às vezes por **número de origem**); o valor depende do **país de destino** e do produto — use a página oficial de **[preços de SMS da Twilio](https://www.twilio.com/en-us/messaging/pricing)** (EN) para orçar, **não** um valor fixo neste documento. **Alternativas:** **AWS SNS**, **Vonage** ou **provedores locais** na sua região. Os dados trafegam na infra da Twilio (**EUA** e outros); separar regras de SMS **comercial** de avisos **operacionais pessoais**; envolver **jurídico / DPO** se a organização exigir.

**Separação de escopo:** resumos para **mantenedor** (esta seção) são distintos de notificações de **produto** (scan terminou, webhooks para inquilinos) — ver **Notifications** em [PLANS_TODO.md](../plans/PLANS_TODO.md) (ordem 6).

**Padrão local (Docker + volume):** Rode **signald** / **signal-cli** ou um cliente de SMS **no seu PC ou homelab**. Mapeie **credenciais e dados de sessão** no container com **volumes** apontando para um diretório **fora do Git** — por exemplo **`docs/private/notify/`**, criado a partir do modelo versionado **[private.example/notify/README.md](../private.example/notify/README.md)**. Coloque **`.env`**, estado do Signal e qualquer dado pessoal **só** aí. **Dispare** o envio com um **script que você executa** (ou agendador local); o repositório permanece sem segredos. **Outros colaboradores** repetem o **mesmo arranjo** em **`docs/private/notify/`** com **chaves e números próprios** — nada sensível circula pelo Git.

---

## 8. Documentos relacionados

- [private.example/notify/README.md](../private.example/notify/README.md) — modelo de layout local (copiar para `docs/private/notify/`).
- [BRANCH_AND_DOCKER_CLEANUP.md](BRANCH_AND_DOCKER_CLEANUP.md) — higiene; §7 remote legado.
- [CODE_PROTECTION_OPERATOR_PLAYBOOK.md](../CODE_PROTECTION_OPERATOR_PLAYBOOK.md) — faixa A.
- [REMOTES_AND_ORIGIN.md](REMOTES_AND_ORIGIN.md) — `origin` vs legado.
- Cursor: **`.cursor/rules/operator-notification-channels.mdc`** e **`.cursor/skills/operator-notification-channels/SKILL.md`**.

---

*Última atualização: padrão de resumo EOD/sprint (SMS/e-mail/chat via sua automação); multi-canal + gancho de KPI.*
