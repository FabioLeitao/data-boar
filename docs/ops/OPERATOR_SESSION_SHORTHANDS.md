# Operator session shorthands (taxonomy)

**pt-BR:** [OPERATOR_SESSION_SHORTHANDS.pt_BR.md](OPERATOR_SESSION_SHORTHANDS.pt_BR.md)

## Canonical source

The **English-only** keyword table lives in **`.cursor/rules/session-mode-keywords.mdc`**. **`AGENTS.md`** should list the **same** tokens in the **same order**; if they diverge, trust **`session-mode-keywords.mdc`** for scope and scripts.

## LAB-OP SSH example host

Tracked examples and scripts use the SSH alias **`latitude`** for the Linux lab server (Zorin; Docker, reports). Configure **`Host latitude`** in your dev PC’s **`~/.ssh/config`** so it matches **DNS/mDNS on the LAN** (and **ed25519** keys as pre-authorized on the host). See **`docs/private.example/homelab/README.md`**.

## Related

- [LAB_OP_SHORTHANDS.md](LAB_OP_SHORTHANDS.md) ([pt-BR](LAB_OP_SHORTHANDS.pt_BR.md)) — `lab-op.ps1` actions
- [TOKEN_AWARE_USAGE.md](../plans/TOKEN_AWARE_USAGE.md) — token-aware pacing
