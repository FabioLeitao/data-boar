# Atalhos de sessão do operador (taxonomia)

**English:** [OPERATOR_SESSION_SHORTHANDS.md](OPERATOR_SESSION_SHORTHANDS.md)

## Fonte canônica

A tabela de palavras-chave **só em inglês** está em **`.cursor/rules/session-mode-keywords.mdc`**. O **`AGENTS.md`** deve listar os **mesmos** tokens na **mesma ordem**; se divergirem, use **`session-mode-keywords.mdc`** como referência de escopo e scripts.

**Mapa script ↔ skill / palavra-chave (mais amplo que só keywords):** **[TOKEN_AWARE_SCRIPTS_HUB.pt_BR.md](TOKEN_AWARE_SCRIPTS_HUB.pt_BR.md)** · [EN](TOKEN_AWARE_SCRIPTS_HUB.md).

## Exemplo de host SSH no LAB-OP

Exemplos versionados e scripts usam o alias SSH **`lab-op`** para o servidor Linux do lab (Docker, reports). Configure **`Host lab-op`** no **`~/.ssh/config`** do PC de desenvolvimento para resolver na LAN (DNS ou mDNS) e usar chaves **ed25519** já autorizadas no host. Nomes reais de máquina ficam **só** em **`docs/private/homelab/`**. Ver **`docs/private.example/homelab/README.md`**.

## Relacionado

- [LAB_OP_SHORTHANDS.pt_BR.md](LAB_OP_SHORTHANDS.pt_BR.md) · [EN](LAB_OP_SHORTHANDS.md) — ações do `lab-op.ps1`
- [PII_FRESH_CLONE_AUDIT.pt_BR.md](PII_FRESH_CLONE_AUDIT.pt_BR.md) · [EN](PII_FRESH_CLONE_AUDIT.md) — **`pii-fresh-audit`** + `pii-fresh-clone-audit.ps1`
- [EVERYTHING_ES_PRIMARY_WINDOWS_DEV_LAB.pt_BR.md](EVERYTHING_ES_PRIMARY_WINDOWS_DEV_LAB.pt_BR.md) · [EN](EVERYTHING_ES_PRIMARY_WINDOWS_DEV_LAB.md) — **`es-find`** + `es-find.ps1` (Windows (PC principal de desenvolvimento); nao Linux **lab-op**)
- [PRIMARY_WINDOWS_WORKSTATION_PROTECTION.pt_BR.md](PRIMARY_WINDOWS_WORKSTATION_PROTECTION.pt_BR.md) · [EN](PRIMARY_WINDOWS_WORKSTATION_PROTECTION.md) — sem operações destrutivas no repo no PC principal; `es-find` / auditorias PII em temp só leitura ou só em `%TEMP%`
- [TOKEN_AWARE_USAGE.md](../plans/TOKEN_AWARE_USAGE.md) — ritmo token-aware
