# Atalhos de sessão do operador (taxonomia)

**English:** [OPERATOR_SESSION_SHORTHANDS.md](OPERATOR_SESSION_SHORTHANDS.md)

## Fonte canônica

A tabela de palavras-chave **só em inglês** está em **`.cursor/rules/session-mode-keywords.mdc`**. O **`AGENTS.md`** deve listar os **mesmos** tokens na **mesma ordem**; se divergirem, use **`session-mode-keywords.mdc`** como referência de escopo e scripts.

## Exemplo de host SSH no LAB-OP

Exemplos versionados e scripts usam o alias SSH **`lab-node-02`** para o servidor Linux do lab (Zorin; Docker, reports). Configure **`Host lab-node-02`** no **`~/.ssh/config`** do PC de desenvolvimento para coincidir com **DNS/mDNS na LAN** (e chaves **ed25519** já autorizadas no host). Ver **`docs/private.example/homelab/README.md`**.

## Relacionado

- [LAB_OP_SHORTHANDS.pt_BR.md](LAB_OP_SHORTHANDS.pt_BR.md) · [EN](LAB_OP_SHORTHANDS.md) — ações do `lab-op.ps1`
- [TOKEN_AWARE_USAGE.md](../plans/TOKEN_AWARE_USAGE.md) — ritmo token-aware
