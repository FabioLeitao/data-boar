---
name: operator-notification-channels
description: >-
  When implementing CI pings, KPI exports, or operator alerts, use at least two channels
  (GitHub + Slack or Telegram), keep secrets out of git, and treat Signal as optional tier D.
---

# Operator notification channels

## When to use

- Adding or editing **GitHub Actions** that should alert a human (failures, long jobs, KPI runs).
- Discussing **Slack, Telegram, Signal, or GitHub mobile** for “reach the operator.”
- Extending **scripts/kpi-export.py** automation with notify-on-complete.

## Instructions

1. Read **[docs/ops/OPERATOR_NOTIFICATION_CHANNELS.md](../../../docs/ops/OPERATOR_NOTIFICATION_CHANNELS.md)** (EN + pt-BR sibling).
1. **Tier A:** GitHub (watch, failed workflows, Issue `@mention`).
1. **Tier B/C:** Slack incoming webhook **or** Telegram Bot API—**never** commit URLs/tokens; use `${{ secrets.* }}` or gitignored `.env`. Repo workflows: **`Slack operator ping (manual)`** (`slack-operator-ping.yml`) and **`Slack CI failure notify`** (`slack-ci-failure-notify.yml`) both use **`SLACK_WEBHOOK_URL`**; jobs skip if unset.
1. **Tier D:** Signal (`signal-cli` / **signald** in Docker)—only after A+(B|C); operator must own pairing and ToS compliance.
1. For **KPI:** optional scheduled `workflow_dispatch` + artifact or chat summary per [PLAN_READINESS_AND_OPERATIONS.md](../../../docs/plans/PLAN_READINESS_AND_OPERATIONS.md) §4.7.

## Legacy Git + cleanup

- **Legacy remote tidy:** [docs/ops/BRANCH_AND_DOCKER_CLEANUP.md](../../../docs/ops/BRANCH_AND_DOCKER_CLEANUP.md) §7 (`python3-lgpd-crawler-legacy-and-history-only`, not python2).
