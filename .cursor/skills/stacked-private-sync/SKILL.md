# Stacked private Git sync (`private-stack-sync`)

## When to use

The operator types **`private-stack-sync`** in chat, or wants a **repeatable close** for the **nested repo** under **`docs/private/`** (not GitHub `origin`) — analogous to **`eod-sync`** for the public tree.

## Steps

1. Optional **fresh-agent orientation:** **`docs/ops/OPERATOR_AGENT_COLD_START_LADDER.md`** ([pt-BR](../../docs/ops/OPERATOR_AGENT_COLD_START_LADDER.pt_BR.md)) — task router row for private stack. Then read **`docs/ops/PRIVATE_STACK_SYNC_RITUAL.md`** (and **`.pt_BR.md`** if the operator uses pt-BR).
2. From the **product repo root**, run **`scripts/private-git-sync.ps1`**; add **`-Push`** when the operator’s policy or request includes **all non-public mirrors** (configured **`lab-*`** remotes **and**, on Windows, push to a **bare `notes-sync.git` on the VeraCrypt-mounted drive** when present — the script probes **`Y:`** / **`Z:`**). When the operator asks to **align**, **verify drift**, or **sync** private history, **do not** ask redundant permission to include obvious backup targets — see **`operator-evidence-backup-no-rhetorical-asks.mdc`** and **[ADR 0040](../../../docs/adr/0040-assistant-private-stack-evidence-mirrors-default.md)**.
3. If the workflow uses **encrypted volumes** for that tree, remind the **mount → git → unmount** discipline from **`docs/ops/PRIVATE_LOCAL_VERSIONING.md`** and **private** homelab runbooks — **do not** paste passphrases or key material into chat.
4. If the operator’s **expected VeraCrypt mount** for private work is **missing**, treat it as an **anomaly** (see stub **§ Operator expectation** in **`docs/ops/PRIVATE_STACK_SYNC_RITUAL.md`**); suggest **private** runbooks and local vault — **do not** ask for volume passwords in chat to “fix” mount.
5. Confirm **no** secrets land in **tracked** files or public issues/PRs.

## Never

- Commit **`docs/private/`** into the **public** remote or paste **passwords / keyfiles / volume paths** into tracked Markdown.
- Claim SSH or LAN operations “completed” without the operator’s **actual** terminal success on their network.

## Related

- **`.cursor/rules/session-mode-keywords.mdc`** — **`private-stack-sync`** row
- **`scripts/operator-day-ritual.ps1`** — EOD hints for **`private-git-sync.ps1`**
- **Private homelab (EN + pt-BR pairs):** `docs/private/homelab/OPERATOR_VERACRYPT_SESSION_POLICY.md`, `LAB_OP_VERACRYPT_BW_ROLLOUT.md`, rollout logs — each `.md` links to **`.pt_BR.md`** and vice versa.
- **Private example:** **`docs/private.example/homelab/lab-op-vc-container-rsync.example.sh`** (placeholders only)
