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

### 1.1 Implantação em fases: Slack primeiro, Signal depois (não ficar desavisado)

Dá para **não gostar do app** e mesmo assim usar **Slack primeiro** — é o caminho **mais rápido** a partir do **GitHub Actions** (incoming webhook, um secret). Depois acrescentar **Signal** como **segundo fornecedor** e camada com **mais privacidade**, para não depender só de um chat nem só do GitHub.

| Fase  | Canais        | Objetivo                                                                                                                                                                                                                                             |
| ----  | ------        | --------                                                                                                                                                                                                                                             |
| **1** | **A + B**     | Push/e-mail do GitHub + **Slack** (`#data-boar-ops` ou outro): workflow de **ping manual**, workflow **CI falhou**, opcionalmente o mesmo webhook no Data Boar para fim de scan (USAGE).                                                             |
| **2** | **A + B + D** | Manter Slack; somar **Signal** via **ponte HTTP no homelab** (§3) + secret, por exemplo `SIGNAL_NOTIFY_URL` (ou `NOTIFY_SECONDARY_URL` genérico). O mesmo workflow manda **o mesmo texto curto** para os dois endpoints quando os secrets existirem. |

**Por que Slack e Signal juntos:** modos de falha independentes (queda do Slack vs sua ponte Signal vs app do GitHub). **Telegram (C)** continua opcional se quiser um terceiro; **não** é obrigatório para esse desenho.

**Esboço no CI:** um passo/script reutilizável: se `SLACK_WEBHOOK_URL` → `curl` no Slack; se `SIGNAL_NOTIFY_URL` → `curl` na REST do Signal na LAN (ou túnel); falha em um ramo **não** impede o outro (avisar no log e seguir).

---

## 2. GitHub (linha de base recomendada)

- **Watch** no repositório (Actions, Security conforme preferir).
- **Workflow falho:** checks obrigatórios evitam merge silencioso; falhas aparecem no app e e-mail/push.
- **Automação → humano:** job agendado pode **abrir/comentar Issue** (`gh issue create` / API); você recebe notificação **padrão** no iPhone.

**Cursor mobile (companion):** Útil para **chat leve / acompanhamento com o agente** longe do desktop. **Não** substitui o push do **GitHub** para **Actions com falha**, **Dependabot** ou **Security** — mantenha o **canal A** (app **GitHub** oficial + configurações de notificação).

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

### 4.1 Checklist Slack (canal B)

1. No workspace Slack, crie um canal (ex.: **`#data-boar-ops`**).
1. Crie um [**Incoming Webhook**](https://api.slack.com/messaging/webhooks) (app no workspace → escolha o canal → copie a URL do webhook).
1. No GitHub: **Settings → Secrets and variables → Actions → New repository secret** — nome **`SLACK_WEBHOOK_URL`**, valor = essa URL.
1. **Teste:** **Actions → Slack operator ping (manual) → Run workflow** (mensagem opcional). Se o secret não existir, o job fica **skipped** (sem falha).
1. **CI / Semgrep falhou → Slack (fase 1):** workflow **`Slack CI failure notify`** (`.github/workflows/slack-ci-failure-notify.yml`) corre quando **`CI`** ou **`Semgrep`** termina com **`failure`** (push/PR para `main` ou `master`). Usa o **mesmo** `SLACK_WEBHOOK_URL`. A mensagem usa o **nome do workflow** que falhou (ex.: **Test (Python 3.13)** ou **Semgrep (OSS, Python)**). Sem secret → o job de notify fica **skipped**. *PRs de fork:* falhas podem ainda gerar ping — filtrar mais tarde se fizer barulho demais.
1. **Release publicada → Slack (opt-in):** workflow **`Slack release published notify`** (`.github/workflows/slack-release-published-notify.yml`) envia um resumo curto quando uma GitHub Release é publicada. Ative com a variável de repositório **`SLACK_NOTIFY_RELEASE_PUBLISHED=true`**.
1. **PR merged → Slack (opt-in):** workflow **`Slack PR merged notify`** (`.github/workflows/slack-pr-merged-notify.yml`) envia mensagem quando um PR é merged em `main`/`master`. Ative com **`SLACK_NOTIFY_PR_MERGED=true`**.
1. **Digest operacional (manual + agendado opt-in):** workflow **`Slack ops digest`** (`.github/workflows/slack-ops-digest.yml`) aceita `workflow_dispatch` e agendamento em dias úteis. O agendamento só roda com **`SLACK_NOTIFY_DAILY_DIGEST=true`**; o disparo manual funciona sempre que o secret existir.
1. **Produto / fim de scan:** reutilize a mesma URL no **`config.yaml`** ou env do Data Boar (ver [USAGE.pt_BR.md](../USAGE.pt_BR.md) — notificações ao operador); caminho separado dos workflows do Actions acima.
1. **Backlog (opcional):** digest agendado com [scripts/notify_webhook.py](../../scripts/notify_webhook.py) ou export KPI quando quiser resumos EOD/sprint (ver §7).

### 4.2 Webhook Slack — how-to do operador (pegar URL, guardar, conferir)

**Objetivo:** uma URL de **Incoming Webhook**, guardada como **`SLACK_WEBHOOK_URL`** no GitHub, usada por **`Slack operator ping (manual)`** e **`Slack CI failure notify`**.

#### A) Obter a URL do webhook (Slack, navegador)

1. Entre em [slack.com](https://slack.com) no workspace onde quer os alertas.
1. Abra **[Your Apps](https://api.slack.com/apps)** (`https://api.slack.com/apps`).
1. **Create New App** → **From scratch** → nome (ex.: **`Data Boar notifications`**) → escolha o **workspace** → **Create App**.
1. No menu lateral do app, **Incoming Webhooks** → ligue **Activate Incoming Webhooks** (**On**).
1. **Add New Webhook to Workspace** → escolha o canal (ex.: **`#data-boar-ops`**) → **Allow**.
1. Copie a **Webhook URL** — deve parecer `<https://hooks.slack.com/services/..>.`. **Não** publique em issue, PR nem chat público.

Se o workspace bloquear apps customizados, peça a um admin aprovação ou um fluxo alinhado à política da empresa.

#### B) Onde guardar (canônico + backup opcional)

| Onde                                                     | O que fazer                                                                                                                                                                                                | Por quê                                                                                                                                                                     |
| ----                                                     | -----------                                                                                                                                                                                                | -------                                                                                                                                                                     |
| **GitHub Actions (obrigatório para os workflows de CI)** | **Settings → Secrets and variables → Actions → New repository secret** → nome **`SLACK_WEBHOOK_URL`** (exatamente assim) → cole a URL → **Add secret**.                                                    | O Actions lê esse secret; nada vai parar em arquivo commitado.                                                                                                              |
| **Gerenciador de senhas (opcional)**                     | Ex.: nota segura no Bitwarden: título `GitHub SLACK_WEBHOOK_URL — <repo>`; mesma URL.                                                                                                                      | Recuperação se rotacionar o webhook ou recriar o secret. Ver [OPERATOR_SECRETS_BITWARDEN.md](OPERATOR_SECRETS_BITWARDEN.md) ([pt-BR](OPERATOR_SECRETS_BITWARDEN.pt_BR.md)). |
| **`config.yaml` / env (opcional, produto)**              | Só se quiser Slack no **fim de scan** num Data Boar a correr — mesma URL em **`notifications`** (ver [USAGE.pt_BR.md](../USAGE.pt_BR.md)). Prefira env ou config **gitignored**; **nunca** commitar a URL. | Caminho separado do GitHub Actions; pode ser o mesmo webhook.                                                                                                               |

**Não** guarde o webhook em: Markdown rastreado, print em ticket, ou só neste chat como única cópia.

#### C) Depois de pronto — onde olhar

| Verificação                  | Onde                                                              | “Certo”                                                                                                                                      |
| -----------                  | ----                                                              | --------                                                                                                                                     |
| Secret existe                | GitHub → **Settings → Secrets and variables → Actions**           | **`SLACK_WEBHOOK_URL`** na lista (valor **oculto** — normal).                                                                                |
| Ping manual                  | **Actions** → **Slack operator ping (manual)** → **Run workflow** | Job **com sucesso** (não **skipped**). **Skipped** costuma ser secret ausente/nome errado ou workflows ainda não na branch que o GitHub usa. |
| Mensagem chegou              | Slack → canal de ops                                              | Mensagem nova com o texto enviado (ou o padrão).                                                                                             |
| CI / Semgrep falhou (depois) | Após falha real do **`CI`** ou **`Semgrep`**                      | Run **Slack CI failure notify**; no Slack, texto **“Data Boar — &lt;nome do workflow&gt; falhou”** com link para o run.                      |

Se o job manual ficar **skipped**, confira o nome **`SLACK_WEBHOOK_URL`** e se `.github/workflows/slack-operator-ping.yml` está na branch padrão (ou na branch onde você dispara o Actions).

---

## 5. Padrão multi-canal

1. **Primário:** GitHub (comentário em Issue ou check falho).
1. **Secundário:** Slack *ou* Telegram.
1. **Terciário opcional:** Signal (homelab até estabilizar).
1. **Redundância reforçada:** **Slack + Signal ao mesmo tempo** (ver §1.1)—mesmo payload nos dois quando quiser **dois fornecedores de chat** além do GitHub.

**Não** commitar webhooks nem tokens; usar **secrets** do GitHub e/ou `.env` no `.gitignore`.

---

## 6. KPI snapshot + notificar (opcional)

Script base: [scripts/kpi-export.py](../../scripts/kpi-export.py) (requer `gh auth`). **Extensão em backlog:**

- Workflow **semanal** ou `workflow_dispatch`: gerar `kpi_snapshot.md`, **artefato**, ou enviar trecho ao Slack/Telegram.
- Evitar commit de snapshots com dados sensíveis; retenção curta de artefatos.

Ver [PLAN_READINESS_AND_OPERATIONS.md](../plans/PLAN_READINESS_AND_OPERATIONS.md) §4.7.

---

## 7. Resumo fim do dia / fim do sprint (SMS, e-mail, chat)

**O que o assistente não faz:** O agente no Cursor **não** envia **SMS** nem **e-mail** para o seu celular ou caixa de entrada. Não há integração com operadora ou SMTP a partir do chat. Qualquer “aviso” precisa rodar no **seu** ambiente: **GitHub Actions**, um **servidor em casa** ou um **script** que você executa na máquina.

## O que dá para montar (padrão recomendado):

| Parte                    | Opções                                                                                                                                                                                                                                                                                          |
| -----                    | ------                                                                                                                                                                                                                                                                                          |
| **Gatilho**              | **`workflow_dispatch`** (“enviar resumo agora”), **cron** (ex.: dias úteis 18h no seu fuso) para fim do dia, ou **no merge de release** / regra de calendário para fim de sprint.                                                                                                               |
| **Resumo curto**         | Primeiras linhas de **`git log`** desde a última tag ou `--since=…`; opcional **`python scripts/plans-stats.py`** para contagens do painel de planos; um parágrafo com “principais ações / principais mudanças” (você ou um modelo preenche).                                                   |
| **Release notes**        | Link para **`docs/releases/X.Y.Z.md`** no `main` (ou **artefato** do workflow); não colar segredos nem URLs internas.                                                                                                                                                                           |
| **Progresso / visão PM** | Colar a tabela **Kanban** de [SPRINTS_AND_MILESTONES.pt_BR.md](../plans/SPRINTS_AND_MILESTONES.pt_BR.md) ou um bloco **Mermaid `gantt`** em **texto puro** na mensagem. O assistente pode **rascunhar** esse Markdown no chat; o **CI** envia — sem copiar na mão se o workflow montar o corpo. |
| **SMS**                  | API **HTTP** (ex.: **Twilio**); **secrets** no GitHub para credenciais; custo e conformidade são **seus**.                                                                                                                                                                                      |
| **E-mail**               | SMTP via Action (ex.: **`dawidd6/action-send-mail`**) ou API REST do provedor; **secrets** para credenciais.                                                                                                                                                                                    |
| **Menos atrito**         | **Telegram** `sendMessage` ou webhook do **Slack** (como nas §2–§4) — muitas vezes basta para “fim do dia” sem taxa de SMS.                                                                                                                                                                     |

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
