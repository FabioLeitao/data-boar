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

---

## 2. GitHub (recommended baseline)

- **Watch** the repository with a mix that includes **Actions** and **Security alerts** (as you prefer).
- **Failed workflow:** ensure branch protection / required checks so merges don’t skip CI; failures surface in the app and email/push.
- **Automation → human:** a scheduled or `workflow_dispatch` job can **open or comment on an Issue** (`gh issue create` / API) with a short summary; you get a **standard GitHub notification** on iPhone.

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

**Not blocking:** treat Signal as **tier D** after GitHub + one messaging webhook.

---

## 4. Slack vs Telegram (quick comparison)

|                      | Slack                                                 | Telegram                                                              |
| ---                  | ---                                                   | ---                                                                   |
| **Setup**            | Slack app → Incoming Webhook to channel               | BotFather → bot token; get `chat_id` once                             |
| **From Actions**     | `curl -X POST -d '{"text":"..."}' $SLACK_WEBHOOK_URL` | `<https://api.telegram.org/bot$TOKEN/sendMessage?chat_id=...&text=..>.` |
| **Personal vs team** | Good if you already live in Slack                     | Good for **direct-to-you** mobile push                                |

Implement **one generic “notify” step** in CI (bash/PowerShell) that posts the same payload to **multiple** endpoints if secrets exist (try Slack; on failure optionally try Telegram—avoid infinite loops).

---

## 5. Multi-channel pattern

1. **Primary:** GitHub (issue comment or failed check).
1. **Secondary:** Slack *or* Telegram (operator preference).
1. **Optional tertiary:** Signal (home lab only, until stable).

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

**What you can build (recommended pattern):**

| Piece | Options |
| ----- | ------- |
| **Trigger** | **`workflow_dispatch`** (“send digest now”), **cron** (e.g. weekdays 18:00 in your TZ) for EOD, or **on release merge** / calendar rule for sprint end. |
| **Short summary** | First lines of **`git log`** since last tag or `--since=…`; optional **`python scripts/plans-stats.py`** for plan-dashboard counts; one paragraph of “main actions / main changes” you or a template fills. |
| **Release notes** | Link to **`docs/releases/X.Y.Z.md`** on `main` (or attach as workflow **artifact**); avoid pasting secrets or internal URLs. |
| **Progress / PM view** | Paste the **Kanban** table from [SPRINTS_AND_MILESTONES.md](../plans/SPRINTS_AND_MILESTONES.md) or a **Mermaid `gantt`** block as **plain text** in the message. The agent can **draft** that Markdown in chat; **CI** sends it—you copy nothing manually if the workflow builds the body. |
| **SMS** | **Twilio** (or similar) **HTTP API** from Actions; store **Account SID / auth token / From** in GitHub **secrets**; costs and compliance are **yours**. |
| **Email** | SMTP via an Action (e.g. **`dawidd6/action-send-mail`**) or your provider’s REST API; **secrets** for credentials. |
| **Low-friction** | **Telegram** `sendMessage` or **Slack** webhook (same as §2–§4)—often enough for “end of day” without SMS fees. |

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
