# Operator session shorthands (taxonomy)

**pt-BR:** [OPERATOR_SESSION_SHORTHANDS.pt_BR.md](OPERATOR_SESSION_SHORTHANDS.pt_BR.md)

## Canonical source

The **English-only** keyword table lives in **`.cursor/rules/session-mode-keywords.mdc`**. **`AGENTS.md`** should list the **same** tokens in the **same order**; if they diverge, trust **`session-mode-keywords.mdc`** for scope and scripts.

**Script ↔ skill / keyword map (broader than keywords alone):** **[TOKEN_AWARE_SCRIPTS_HUB.md](TOKEN_AWARE_SCRIPTS_HUB.md)** ([pt-BR](TOKEN_AWARE_SCRIPTS_HUB.pt_BR.md)).

## LAB-OP SSH example host

Tracked examples and scripts use the SSH alias **`lab-op`** for the Linux lab server (Docker, reports). Configure **`Host lab-op`** in your dev PC’s **`~/.ssh/config`** so it resolves on your LAN (DNS or mDNS) and uses **ed25519** keys as pre-authorized on the host. Real machine names stay **only** under **`docs/private/homelab/`**. See **`docs/private.example/homelab/README.md`**.

## Related

- [LAB_OP_SHORTHANDS.md](LAB_OP_SHORTHANDS.md) ([pt-BR](LAB_OP_SHORTHANDS.pt_BR.md)) — `lab-op.ps1` actions
- [PII_FRESH_CLONE_AUDIT.md](PII_FRESH_CLONE_AUDIT.md) ([pt-BR](PII_FRESH_CLONE_AUDIT.pt_BR.md)) — **`pii-fresh-audit`** + `pii-fresh-clone-audit.ps1`
- [EVERYTHING_ES_PRIMARY_WINDOWS_DEV_LAB.md](EVERYTHING_ES_PRIMARY_WINDOWS_DEV_LAB.md) ([pt-BR](EVERYTHING_ES_PRIMARY_WINDOWS_DEV_LAB.pt_BR.md)) — **`es-find`** + `es-find.ps1` (Windows primary dev PC; not Linux **lab-op**)
- [PRIMARY_WINDOWS_WORKSTATION_PROTECTION.md](PRIMARY_WINDOWS_WORKSTATION_PROTECTION.md) ([pt-BR](PRIMARY_WINDOWS_WORKSTATION_PROTECTION.pt_BR.md)) — no destructive repo ops on primary dev PC; `es-find` / temp PII audits are read-only or temp-only
- [TOKEN_AWARE_USAGE.md](../plans/TOKEN_AWARE_USAGE.md) — token-aware pacing
