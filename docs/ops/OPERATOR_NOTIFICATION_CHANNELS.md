# Operator notification channels — multi-path reachability

**Português (Brasil):** [OPERATOR_NOTIFICATION_CHANNELS.pt_BR.md](OPERATOR_NOTIFICATION_CHANNELS.pt_BR.md)

**Purpose:** When **CI fails**, **long jobs finish**, or a **human must return** to Cursor, prefer **at least two independent channels** so one outage (app blocked, DND, wrong account) does not block awareness. This doc is **policy + integration notes only**—**no secrets** in the repo (tokens in env, `docs/private/`, or GitHub **encrypted secrets**).

**Scope:** Maintainer / operator pings (you + agents automating checks). Product **tenant** notifications (scan-complete, etc.) stay in the main **Notifications** plan ([PLANS_TODO.md](../plans/PLANS_TODO.md) order 6)—reuse the same channel list where appropriate.

**Sequencing (maintainer):** **Channel A only**—GitHub **mobile app** plus watch/email settings—is **enough to start** for PRs, reviews, Dependabot, Security, and **failed Actions**. Tweak **GitHub → Settings → Notifications** and the official iOS/Android app. When you want **redundancy** or chat-native pings, add **B** (Slack) or **C** (Telegram) per §1; **D** (Signal) stays optional and higher-effort. This doc is the **integration reminder** for those next steps.

---

## 1. Recommended stack (least friction → most setup)

| Priority | Channel                       | Why                                                                                                                                    | Typical use                                                                                                                   |
| -------- | -------                       | ---                                                                                                                                    | -----------                                                                                                                   |
| **A**    | **GitHub**                    | Already tied to the repo; **mobile app** push for assignments, review requests, **failed workflow** runs, Dependabot, Security alerts. | Turn on notifications for **data-boar**; watch **Actions** failures; optional **Issue** opened by automation with `@mention`. |
| **B**    | **Slack** (workspace you use) | **Incoming webhook** (one URL) or bot; easy from GitHub Actions `curl`.                                                                | Single `#data-boar-ops` channel; webhook in repo secret `SLACK_WEBHOOK_URL`.                                                  |
| **C**    | **Telegram**                  | **HTTP Bot API**; one bot token + your **chat_id**; very small scripts.                                                                | BotFather → bot token as secret; post to yourself or a small group.                                                           |
| **D**    | **Signal**                    | Strong privacy; **higher ops cost** (linked device / `signal-cli` / community **signald** Docker images).                              | Optional; see §3. Respect **Signal Terms** and your jurisdiction.                                                             |

**Practical minimum:** **A + B** or **A + C** gives redundancy without Signal. **A** alone is acceptable if Slack/Telegram are off, but two channels reduce “I missed the only ping.”

### 1.1 Phased rollout: Slack first, Signal later (stay informed on both)

You can **hate the app** and still use **Slack** first—it is the **lowest-friction** path from **GitHub Actions** (incoming webhook, one secret). Then add **Signal** as a **second vendor** and **stronger privacy** layer so you are not dependent on a single chat provider or on GitHub alone.

| Phase | Channels      | Goal                                                                                                                                                                                                                   |
| ----- | --------      | ----                                                                                                                                                                                                                   |
| **1** | **A + B**     | GitHub push/email + **Slack** `#data-boar-ops` (or your channel): **manual ping** workflow, **CI failure** workflow (when `SLACK_WEBHOOK_URL` is set), optional same webhook in app config for scan-complete (USAGE).  |
| **2** | **A + B + D** | Keep Slack; add **Signal** via **home-lab HTTP bridge** (§3) + secret e.g. `SIGNAL_NOTIFY_URL` (or generic `NOTIFY_SECONDARY_URL`). Same workflow posts **the same short text** to both endpoints where secrets exist. |

**Why both Slack and Signal:** Independent failure modes (Slack outage vs your Signal bridge vs GitHub app). **Telegram (C)** remains optional if you want a third chat vendor; it is not required for this pattern.

**CI sketch:** One reusable step/script: if `SLACK_WEBHOOK_URL` → `curl` Slack; if `SIGNAL_NOTIFY_URL` → `curl` Signal REST on LAN (or tunnel); failures on one branch **do not** block the other (log warning, continue).

---

## 2. GitHub (recommended baseline)

- **Watch** the repository with a mix that includes **Actions** and **Security alerts** (as you prefer).
- **Failed workflow:** ensure branch protection / required checks so merges don’t skip CI; failures surface in the app and email/push.
- **Automation → human:** a scheduled or `workflow_dispatch` job can **open or comment on an Issue** (`gh issue create` / API) with a short summary; you get a **standard GitHub notification** on iPhone.

**Cursor mobile (companion):** Useful for **lightweight chat / agent follow-up** when you are away from the desktop. It does **not** replace **GitHub** push notifications for **failed Actions**, **Dependabot**, or **Security**—keep **channel A** (official **GitHub** mobile app + notification settings) for those.

No custom server required; use **GITHUB_TOKEN** in Actions (permissions scoped in the workflow).

---

## 3. Signal (Docker / CLI — advanced)

Community setups often use **`signal-cli`** or **`signald`** (REST/gRPC) in **Docker**, with a **linked device** or number registration flow. Behaviour you described matches common patterns:

- Messages **from your linked identity** to **contacts** use normal delivery semantics.
- **Note to self** / “annotation” UX when messaging **your own** number or linked device can appear as a conversation with yourself—useful for **operator reminders** (same as many people use Telegram “Saved messages”).

## Caveats (read before investing):

- **Operational:** container restarts, pairing/QR, backups—plan for **recovery** if the linked session breaks.
- **Legal / ToS:** use only official or well-audited images; comply with **Signal** terms and local law.
- **Automation:** the agent in Cursor **cannot** hold your Signal session; only **your** runners (home server, laptop script, CI with secrets you control) should call the API.
- **LAB‑OP offload:** Running the Signal Docker image on **another lab machine** (not the dev PC) is a good fit: your workstation sends **`curl`** (headers + JSON body) to the REST API on the LAN—same integration style as **Uptime Kuma** webhooks. Lock the service to **private network**; store the URL/token only under **gitignored** `docs/private/notify/`. See **[private.example/notify/README.md](../private.example/notify/README.md)** § *Signal on a different machine*.

**Not blocking:** treat Signal as **tier D** after GitHub + one messaging webhook.

---

## 4. Slack vs Telegram (quick comparison)

|                      | Slack                                                 | Telegram                                                                |
| ---                  | ---                                                   | ---                                                                     |
| **Setup**            | Slack app → Incoming Webhook to channel               | BotFather → bot token; get `chat_id` once                               |
| **From Actions**     | `curl -X POST -d '{"text":"..."}' $SLACK_WEBHOOK_URL` | `<https://api.telegram.org/bot$TOKEN/sendMessage?chat_id=...&text=..>.` |
| **Personal vs team** | Good if you already live in Slack                     | Good for **direct-to-you** mobile push                                  |

Implement **one generic “notify” step** in CI (bash/PowerShell) that posts the same payload to **multiple** endpoints if secrets exist (try Slack; on failure optionally try Telegram—avoid infinite loops).

### 4.1 Slack setup checklist (channel B)

1. In your Slack workspace, create a channel (e.g. **`#data-boar-ops`**).
1. Create an [**Incoming Webhook**](https://api.slack.com/messaging/webhooks) for your workspace (Slack app → choose channel → copy the webhook URL).
1. On GitHub: **Settings → Secrets and variables → Actions → New repository secret** — name **`SLACK_WEBHOOK_URL`**, value = the webhook URL.
1. **Smoke test:** **Actions → Slack operator ping (manual) → Run workflow** (optional custom message). If the secret is unset, the job is **skipped** (no failure).
1. **CI / Semgrep failure ping (phase 1):** workflow **`Slack CI failure notify`** (`.github/workflows/slack-ci-failure-notify.yml`) runs when **`CI`** or **`Semgrep`** finishes with **`failure`** (push/PR to `main` or `master`). Uses the **same** `SLACK_WEBHOOK_URL`. If the secret is unset, the notify job is **skipped**. The Slack line uses the failing workflow’s display name (e.g. **Test (Python 3.13)** or **Semgrep (OSS, Python)**). *Fork PRs:* failures may still produce a ping—reduce noise later (branch filters) if needed.
1. **Release published ping (opt-in):** workflow **`Slack release published notify`** (`.github/workflows/slack-release-published-notify.yml`) posts a short message when a GitHub Release is published. Toggle with repo variable **`SLACK_NOTIFY_RELEASE_PUBLISHED=true`**.
1. **PR merged ping (opt-in):** workflow **`Slack PR merged notify`** (`.github/workflows/slack-pr-merged-notify.yml`) posts when a PR is merged into `main`/`master`. Toggle with **`SLACK_NOTIFY_PR_MERGED=true`**.
1. **Ops digest (manual + scheduled opt-in):** workflow **`Slack ops digest`** (`.github/workflows/slack-ops-digest.yml`) supports `workflow_dispatch` and weekday schedule. Scheduled posts are enabled only with **`SLACK_NOTIFY_DAILY_DIGEST=true`**; manual dispatch always works when secret exists.
1. **Product / scan-complete:** reuse the same webhook URL in Data Boar **`config.yaml`** or env (see [USAGE.md](../USAGE.md) — operator notifications); separate from Actions workflows above.
1. **Backlog (optional):** scheduled digest via [scripts/notify_webhook.py](../../scripts/notify_webhook.py) or KPI export once you want EOD/sprint summaries (see §7).

### 4.2 Slack incoming webhook — operator how-to (grab URL, store it, verify)

**Goal:** One Incoming Webhook URL, stored as **`SLACK_WEBHOOK_URL`** on GitHub, used by **`Slack operator ping (manual)`** and **`Slack CI failure notify`**.

#### A) Get the webhook URL (Slack, browser)

1. Sign in at [slack.com](https://slack.com) with the workspace you use for ops alerts.
1. Open **[Your Apps](https://api.slack.com/apps)** (`https://api.slack.com/apps`).
1. **Create New App** → **From scratch** → name it (e.g. **`Data Boar notifications`**) → choose your **workspace** → **Create App**.
1. In the app settings sidebar, open **Incoming Webhooks** → turn **Activate Incoming Webhooks** **On**.
1. Click **Add New Webhook to Workspace** → pick the channel (e.g. **`#data-boar-ops`**) → **Allow**.
1. Copy the **Webhook URL** — it must look like `<https://hooks.slack.com/services/..>.` (three path segments). **Do not** share it in issues, PRs, or public chat.

If your workspace blocks custom apps, ask a workspace admin to approve app install or create the webhook using a policy-compliant process.

#### B) Where to save it (canonical + optional backup)

| Store                                            | What you do                                                                                                                                                                                                     | Why                                                                                                                                                                           |
| -----                                            | -----------                                                                                                                                                                                                     | ---                                                                                                                                                                           |
| **GitHub Actions (required for CI workflows)**   | Repo **Settings → Secrets and variables → Actions → New repository secret** → name **`SLACK_WEBHOOK_URL`** (exact spelling) → paste URL → **Add secret**.                                                       | Actions reads this secret; nothing hits the repo files.                                                                                                                       |
| **Password manager (optional)**                  | e.g. Bitwarden **secure note**: title `GitHub SLACK_WEBHOOK_URL — <repo name>`; paste the same URL.                                                                                                             | Recovery if you rotate the webhook or recreate the secret. See [OPERATOR_SECRETS_BITWARDEN.md](OPERATOR_SECRETS_BITWARDEN.md) ([pt-BR](OPERATOR_SECRETS_BITWARDEN.pt_BR.md)). |
| **`config.yaml` / env (optional, product path)** | Only if you want **scan-complete** Slack from a running Data Boar instance — same URL in **`notifications`** (see [USAGE.md](../USAGE.md)). Use env or a **gitignored** local config; **never** commit the URL. | Separate from GitHub Actions; same webhook is allowed.                                                                                                                        |

**Do not** save the webhook in: committed Markdown, `docs/private/` **if** that tree syncs somewhere risky without encryption, screenshots in tickets, or this chat as the only copy.

#### C) After you’re done — where to look (sanity checks)

| Check                     | Where                                                                            | What “good” looks like                                                                                                                       |
| -----                     | -----                                                                            | ----------------------                                                                                                                       |
| Secret exists             | GitHub → **Settings → Secrets and variables → Actions**                          | **`SLACK_WEBHOOK_URL`** listed (value is **hidden**; that’s normal).                                                                         |
| Manual ping works         | **Actions** → **Slack operator ping (manual)** → **Run workflow** → open the run | Job **succeeded** (not **skipped**). **Skipped** usually means secret missing/misnamed or workflows not on the branch GitHub runs.           |
| Message arrived           | Slack → your ops channel                                                         | New message with the text you sent (or the default ping line).                                                                               |
| CI / Semgrep failure path | After a real **`CI`** or **`Semgrep`** failure (or a test branch)                | **Actions** shows **Slack CI failure notify** run; Slack shows **“Data Boar — &lt;workflow name&gt; falhou”** with a link to the failed run. |

If **manual** job is **skipped**, confirm the secret name is exactly **`SLACK_WEBHOOK_URL`** and that `.github/workflows/slack-operator-ping.yml` is on the default branch (or the branch you run Actions from).

---

## 5. Multi-channel pattern

1. **Primary:** GitHub (issue comment or failed check).
1. **Secondary:** Slack *or* Telegram (operator preference).
1. **Optional tertiary:** Signal (home lab only, until stable).
1. **Redundancy upgrade:** **Slack + Signal together** (see §1.1)—same payload to both when you want **two chat vendors** plus GitHub.

**Do not** store webhooks or bot tokens in git; use **GitHub Actions secrets** and/or a local `.env` listed in `.gitignore`.

---

## 6. Optional KPI snapshot + notify

Baseline script: [scripts/kpi-export.py](../../scripts/kpi-export.py) (needs `gh auth`). **Optional extension (backlog):**

- **Weekly** `workflow_dispatch` or cron workflow: run `python scripts/kpi-export.py --out kpi_snapshot.md`, upload as **artifact**, or post excerpt to Slack/Telegram.
- **Do not** commit snapshots with live URLs if they’re sensitive; keep artifacts **retention short** or post summary only.

See [PLAN_READINESS_AND_OPERATIONS.md](../plans/PLAN_READINESS_AND_OPERATIONS.md) §4.7.

---

## 7. End-of-day / end-of-sprint digest (SMS, email, chat)

**What the AI cannot do:** The Cursor agent **does not** send **SMS** or **email** to your phone or inbox. There is no built-in carrier/SMTP integration from chat. Anything that “pings” you must run in **your** environment: **GitHub Actions**, a **home server**, or a **script** you execute locally.

## What you can build (recommended pattern):

| Piece                  | Options                                                                                                                                                                                                                                                                                    |
| -----                  | -------                                                                                                                                                                                                                                                                                    |
| **Trigger**            | **`workflow_dispatch`** (“send digest now”), **cron** (e.g. weekdays 18:00 in your TZ) for EOD, or **on release merge** / calendar rule for sprint end.                                                                                                                                    |
| **Short summary**      | First lines of **`git log`** since last tag or `--since=…`; optional **`python scripts/plans-stats.py`** for plan-dashboard counts; one paragraph of “main actions / main changes” you or a template fills.                                                                                |
| **Release notes**      | Link to **`docs/releases/X.Y.Z.md`** on `main` (or attach as workflow **artifact**); avoid pasting secrets or internal URLs.                                                                                                                                                               |
| **Progress / PM view** | Paste the **Kanban** table from [SPRINTS_AND_MILESTONES.md](../plans/SPRINTS_AND_MILESTONES.md) or a **Mermaid `gantt`** block as **plain text** in the message. The agent can **draft** that Markdown in chat; **CI** sends it—you copy nothing manually if the workflow builds the body. |
| **SMS**                | **Twilio** (or similar) **HTTP API** from Actions; store **Account SID / auth token / From** in GitHub **secrets**; costs and compliance are **yours**.                                                                                                                                    |
| **Email**              | SMTP via an Action (e.g. **`dawidd6/action-send-mail`**) or your provider’s REST API; **secrets** for credentials.                                                                                                                                                                         |
| **Low-friction**       | **Telegram** `sendMessage` or **Slack** webhook (same as §2–§4)—often enough for “end of day” without SMS fees.                                                                                                                                                                            |

**Twilio (SMS API — optional):** **Twilio** is a US-based **CPaaS** (*Communications Platform as a Service*) vendor: one **HTTP API** to send **SMS** across many countries without a direct contract with each mobile operator—why it appears often in tutorials and pairs well with **GitHub Actions** or a **`curl`** script. You typically pay **per message** (and sometimes for a **sender number**); rates depend on **destination country** and product—use the official **[Twilio SMS pricing](https://www.twilio.com/en-us/messaging/pricing)** page for a current quote, not a fixed number in this doc. **Alternatives:** **AWS SNS**, **Vonage**, or **local carriers** in your region. Data is processed on **US** (and other) Twilio infrastructure; separate **marketing** SMS rules from **personal operational** pings; involve **counsel / DPO** if your org needs that check.

**Scope split:** Maintainer **digests** (this section) are separate from **product** notifications (scan finished, webhooks to tenants)—see **Notifications** in [PLANS_TODO.md](../plans/PLANS_TODO.md) (order 6).

**Local-first pattern (Docker + bind mount):** Run **signald** / **signal-cli** or an SMS client **on your workstation or homelab**. Map **credentials and session data** into the container with **volumes** pointing at a **gitignored** directory—e.g. create **`docs/private/notify/`** using the tracked blueprint **[private.example/notify/README.md](../private.example/notify/README.md)**. Put **`.env`**, Signal state, and anything personal **only** there. **Trigger** delivery with a **script you execute** (or a local scheduler); the repo stays free of secrets. **Other contributors** replicate the **same layout** under **their** `docs/private/notify/` with **their** own keys and numbers—nothing sensitive is shared through Git.

---

## 8. Related docs

- [private.example/notify/README.md](../private.example/notify/README.md) — local notify layout (copy to `docs/private/notify/`).
- [BRANCH_AND_DOCKER_CLEANUP.md](BRANCH_AND_DOCKER_CLEANUP.md) — hygiene; §7 legacy remote.
- [CODE_PROTECTION_OPERATOR_PLAYBOOK.md](../CODE_PROTECTION_OPERATOR_PLAYBOOK.md) — Priority band A.
- [REMOTES_AND_ORIGIN.md](REMOTES_AND_ORIGIN.md) — `origin` vs legacy remote.
- Cursor: **`.cursor/rules/operator-notification-channels.mdc`** + **`.cursor/skills/operator-notification-channels/SKILL.md`** (agents editing workflows / KPI notify).

---

*Last updated: EOD/sprint digest pattern (SMS/email/chat via your automation); multi-channel + KPI hook.*
