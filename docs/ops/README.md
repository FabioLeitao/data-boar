# Operator runbooks (`docs/ops/`)

This folder groups **maintainer / operator** procedural docs. **Product usage** docs (`USAGE`, `TESTING`, `DOCKER_SETUP`, etc.) stay under [`docs/`](../README.md) so app users are not sent through operator-only material.

**Languages:** Each runbook has an English file and a **pt-BR** twin (`*.pt_BR.md`). *Plan history under [`docs/plans/`](../plans/) is English-only.*

## Before you open a PR (operators)

1. Run **`.\scripts\check-all.ps1`** from the repo root on Windows (refreshes the plans dashboard, runs pre-commit, then full pytest). On Linux/macOS, run the same steps manually: `python scripts/plans-stats.py --write`, `uv run pre-commit run --all-files`, `uv run pytest -v -W error`.
1. **Do not** commit **`docs/private/`** (real homelab inventory; gitignored) or **`git add -f config.yaml`**. Use the tracked template **`docs/private.example/`** and policy **[PRIVATE_OPERATOR_NOTES.md](../PRIVATE_OPERATOR_NOTES.md)**.

### Chat shorthand: `pmo-view` (plan / PMO docs, Markdown preview)

**Token is English-only** (same for all session keywords—see **`AGENTS.md`** and **`.cursor/rules/session-mode-keywords.mdc`**). Type **`pmo-view`** exactly; you can write the rest of the message in pt-BR.

In Cursor chat, say **`pmo-view`** when you want the assistant to **surface plan and PMO-style docs** and remind you how to read them **rendered** (tables, Gantt/Mermaid).

- **You** open each file in the editor, then: **Windows / Linux:** `Ctrl+Shift+V` (Open Preview) or `Ctrl+K` then `V` (Preview to the Side). **macOS:** `Cmd+Shift+V` or `Cmd+K` then `V`.
- The assistant **cannot** switch your tab to Preview automatically—that is an editor gesture.
- **Typical files:** [`plans/PLANS_TODO.md`](../plans/PLANS_TODO.md), [`plans/SPRINTS_AND_MILESTONES.md`](../plans/SPRINTS_AND_MILESTONES.md) ([pt-BR](../plans/SPRINTS_AND_MILESTONES.pt_BR.md)), [`plans/TOKEN_AWARE_USAGE.md`](../plans/TOKEN_AWARE_USAGE.md), [COMMIT_AND_PR.md](COMMIT_AND_PR.md) ([pt-BR](COMMIT_AND_PR.pt_BR.md)), [OPERATOR_LAB_DOCUMENT_MAP.md](OPERATOR_LAB_DOCUMENT_MAP.md) ([pt-BR](OPERATOR_LAB_DOCUMENT_MAP.pt_BR.md)).

Defined in **`.cursor/rules/session-mode-keywords.mdc`**.

---

## Index

| Topic                                                | English                                                                      | Português (pt-BR)                                                                        |
| -----                                                | -------                                                                      | -----------------                                                                        |
| SonarQube (home lab, Docker, CI / IDE / MCP)         | [SONARQUBE_HOME_LAB.md](SONARQUBE_HOME_LAB.md)                               | [SONARQUBE_HOME_LAB.pt_BR.md](SONARQUBE_HOME_LAB.pt_BR.md)                               |
| Home lab — deploy smoke & data targets               | [HOMELAB_VALIDATION.md](HOMELAB_VALIDATION.md)                               | [HOMELAB_VALIDATION.pt_BR.md](HOMELAB_VALIDATION.pt_BR.md)                               |
| Commit conventions & PR hygiene                      | [COMMIT_AND_PR.md](COMMIT_AND_PR.md)                                         | [COMMIT_AND_PR.pt_BR.md](COMMIT_AND_PR.pt_BR.md)                                         |
| Remotes, `origin`, fork workflow                     | [REMOTES_AND_ORIGIN.md](REMOTES_AND_ORIGIN.md)                               | [REMOTES_AND_ORIGIN.pt_BR.md](REMOTES_AND_ORIGIN.pt_BR.md)                               |
| Branch + Docker cleanup (legacy remote §7)           | [BRANCH_AND_DOCKER_CLEANUP.md](BRANCH_AND_DOCKER_CLEANUP.md)                 | [BRANCH_AND_DOCKER_CLEANUP.pt_BR.md](BRANCH_AND_DOCKER_CLEANUP.pt_BR.md)                 |
| Operator notification channels                       | [OPERATOR_NOTIFICATION_CHANNELS.md](OPERATOR_NOTIFICATION_CHANNELS.md)       | [OPERATOR_NOTIFICATION_CHANNELS.pt_BR.md](OPERATOR_NOTIFICATION_CHANNELS.pt_BR.md)       |
| Operator / IT minimal permissions                    | [OPERATOR_IT_REQUIREMENTS.md](OPERATOR_IT_REQUIREMENTS.md)                   | [OPERATOR_IT_REQUIREMENTS.pt_BR.md](OPERATOR_IT_REQUIREMENTS.pt_BR.md)                   |
| Aggregated-identification practical tuning (Phase C) | [AGGREGATED_IDENTIFICATION_TUNING.md](AGGREGATED_IDENTIFICATION_TUNING.md)   | [AGGREGATED_IDENTIFICATION_TUNING.pt_BR.md](AGGREGATED_IDENTIFICATION_TUNING.pt_BR.md)   |
| Troubleshooting Docker deployment                    | [TROUBLESHOOTING_DOCKER_DEPLOYMENT.md](TROUBLESHOOTING_DOCKER_DEPLOYMENT.md) | [TROUBLESHOOTING_DOCKER_DEPLOYMENT.pt_BR.md](TROUBLESHOOTING_DOCKER_DEPLOYMENT.pt_BR.md) |

**Related (not in this folder):** [SECURITY.md](../SECURITY.md) / [SECURITY.pt_BR.md](../SECURITY.pt_BR.md) and [CODE_PROTECTION_OPERATOR_PLAYBOOK.md](../CODE_PROTECTION_OPERATOR_PLAYBOOK.md) / [CODE_PROTECTION_OPERATOR_PLAYBOOK.pt_BR.md](../CODE_PROTECTION_OPERATOR_PLAYBOOK.pt_BR.md) — security posture and **Priority band A** hardening next to the main security policy in [`docs/README.md`](../README.md).

---

## Link-audit checklist (after moving or renaming docs)

Use this when opening a PR such as **docs: cluster ops runbooks under docs/ops**.

- [ ] **[README.md](../README.md)** / **[README.pt_BR.md](../README.pt_BR.md)** — tables and bullets under **Internal and reference** / **Ops**.
- [ ] **Root [CONTRIBUTING.md](../../CONTRIBUTING.md)** — any `docs/…` paths touched by the move.
- [ ] **[`.cursor/rules/`](../../.cursor/rules/)** and **[`.cursor/skills/`](../../.cursor/skills/)** — deep links into `docs/` or `docs/ops/`.
- [ ] **Cross-doc links** inside moved files (`../`, `ops/`, `plans/`).
- [ ] **`docs/plans/*.md`** — relative links from `plans/` to `../ops/…` or `../CODE_PROTECTION…`.
- [ ] **Optional:** `rg` for the **old path** (e.g. `docs/HOMELAB_VALIDATION.md` without `ops/`) and fix stragglers.

**Do not** change `.github/` workflows, `sonar.sources`, or relocate root **SECURITY** / **CONTRIBUTING** unless the goal is explicitly to do so; prefer link updates only.

**Automation:** `uv run pytest tests/test_docs_markdown.py tests/test_markdown_lint.py`
