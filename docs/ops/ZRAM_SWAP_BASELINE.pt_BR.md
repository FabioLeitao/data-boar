# Baseline de swap com zram (LAB-OP friendly)

**English:** [ZRAM_SWAP_BASELINE.md](ZRAM_SWAP_BASELINE.md)

## Objetivo

Melhorar a responsividade em hosts com pouca RAM sem depender de um swap grande em disco.

## Automação (Ansible)

Role: `ops/automation/ansible/roles/t14_zram`

O padrão é **opt-in** (`t14_zram_enable=false`).

### Política de sizing

A role calcula `zram-size` com base na RAM do host:

- `t14_zram_size_percent` da RAM total
- limitado por `t14_zram_min_mb` e `t14_zram_max_mb`

## Validação

No host:

```bash
swapon --show
zramctl
```

