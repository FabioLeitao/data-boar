# Cursor / agent policy hub (map only)

**Português (Brasil):** [CURSOR_AGENT_POLICY_HUB.pt_BR.md](CURSOR_AGENT_POLICY_HUB.pt_BR.md)

This page is **consolidation phase B**: the same **theme → first place to look** map as the **Quick index** in root [`AGENTS.md`](../../AGENTS.md), but with **clickable paths** into rules, skills, and operator docs. It does **not** replace narrative bullets in [`AGENTS.md`](../../AGENTS.md)—update **both** the Quick index table and this table when you add a new policy row.

## Quick index (linked)

| Theme | Where to look first |
| ----- | ------------------- |
| **`docs/private/`** read access / never self-block | [First `AGENTS.md` bullet after the Quick index](../../AGENTS.md) · [`.cursor/rules/agent-docs-private-read-access.mdc`](../../.cursor/rules/agent-docs-private-read-access.mdc) · [`docs/PRIVATE_OPERATOR_NOTES.md`](../PRIVATE_OPERATOR_NOTES.md) |
| Chat **pt-BR** / locale (private `docs/private/` Portuguese = pt-BR; explicit EN prose → `en-US`) | [`.cursor/rules/operator-chat-language.mdc`](../../.cursor/rules/operator-chat-language.mdc) · [`.cursor/rules/operator-chat-language-pt-br.mdc`](../../.cursor/rules/operator-chat-language-pt-br.mdc) · [`.cursor/rules/docs-pt-br-locale.mdc`](../../.cursor/rules/docs-pt-br-locale.mdc) · [`.cursor/skills/operator-dialogue-pt-br/SKILL.md`](../../.cursor/skills/operator-dialogue-pt-br/SKILL.md) |
| **Session keywords** (deps, feature, `es-find`, …) | [`.cursor/rules/session-mode-keywords.mdc`](../../.cursor/rules/session-mode-keywords.mdc) |
| **PII / secrets / public tree** | [`.cursor/rules/private-pii-never-public.mdc`](../../.cursor/rules/private-pii-never-public.mdc) · [`PII_PUBLIC_TREE_OPERATOR_GUIDE.md`](PII_PUBLIC_TREE_OPERATOR_GUIDE.md) · **`pii-fresh-audit`** flow (see [`AGENTS.md`](../../AGENTS.md)) |
| **Commercial / confidential** | [`.cursor/rules/confidential-commercial-never-tracked.mdc`](../../.cursor/rules/confidential-commercial-never-tracked.mdc) |
| **GitHub / PR / merge advice** | [`.cursor/rules/git-pr-sync-before-advice.mdc`](../../.cursor/rules/git-pr-sync-before-advice.mdc) · [`CONTRIBUTING.md`](../../CONTRIBUTING.md) · [`COMMIT_AND_PR.md`](COMMIT_AND_PR.md) |
| **Investigation / recovery (“figure it out”)** | [`.cursor/rules/operator-investigation-before-blocking.mdc`](../../.cursor/rules/operator-investigation-before-blocking.mdc) · [`.cursor/skills/operator-recovery-investigation/SKILL.md`](../../.cursor/skills/operator-recovery-investigation/SKILL.md) |
| **Cursor browser / SSO / tabs** | [`.cursor/rules/cursor-browser-social-sso-hygiene.mdc`](../../.cursor/rules/cursor-browser-social-sso-hygiene.mdc) · [`.cursor/skills/cursor-browser-social-session/SKILL.md`](../../.cursor/skills/cursor-browser-social-session/SKILL.md) |
| **Homelab / SSH / LAN** | [`.cursor/rules/homelab-ssh-via-terminal.mdc`](../../.cursor/rules/homelab-ssh-via-terminal.mdc) · [`docs/private/homelab/AGENT_LAB_ACCESS.md`](../private/homelab/AGENT_LAB_ACCESS.md) (when present) |
| **Autonomous merge / LAB-OP** | [`.cursor/rules/agent-autonomous-merge-and-lab-ops.mdc`](../../.cursor/rules/agent-autonomous-merge-and-lab-ops.mdc) |
| **Execution priority / PR batching** | [`.cursor/rules/execution-priority-and-pr-batching.mdc`](../../.cursor/rules/execution-priority-and-pr-batching.mdc) · [`docs/plans/PLANS_TODO.md`](../plans/PLANS_TODO.md) |
| **Operator career / LinkedIn layout (private)** | [`.cursor/rules/operator-career-private-layout.mdc`](../../.cursor/rules/operator-career-private-layout.mdc) · [`docs/private/author_info/career/README.pt_BR.md`](../private/author_info/career/README.pt_BR.md) |
| **Private stacked git** | [`PRIVATE_LOCAL_VERSIONING.md`](PRIVATE_LOCAL_VERSIONING.md) · mini-plan [`docs/private/ops/CURSOR_CONSOLIDATION_MINI_PLAN.pt_BR.md`](../private/ops/CURSOR_CONSOLIDATION_MINI_PLAN.pt_BR.md) |
| **Risk / non-destructive vs destructive** | **Risk posture** paragraph in [`AGENTS.md`](../../AGENTS.md) (immediately under the Quick index table) |

## Related operator runbooks

- [`OPERATOR_SESSION_SHORTHANDS.md`](OPERATOR_SESSION_SHORTHANDS.md) — session tokens and `lab-op` index
- [`TOKEN_AWARE_SCRIPTS_HUB.md`](TOKEN_AWARE_SCRIPTS_HUB.md) — scripts mapped to keywords / skills
- [`OPERATOR_LAB_DOCUMENT_MAP.md`](OPERATOR_LAB_DOCUMENT_MAP.md) — lab and agent doc layout
