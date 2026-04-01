# zram swap baseline (LAB-OP friendly)

**pt-BR:** [ZRAM_SWAP_BASELINE.pt_BR.md](ZRAM_SWAP_BASELINE.pt_BR.md)

## Goal

Improve responsiveness on memory-constrained hosts without forcing a large disk swap.

## Automation (Ansible)

Role: `ops/automation/ansible/roles/t14_zram`

Safe default is **opt-in** (`t14_zram_enable=false`).

### Sizing policy

The role computes `zram-size` based on host RAM:

- `t14_zram_size_percent` of total RAM
- bounded by `t14_zram_min_mb` and `t14_zram_max_mb`

## Validation

On the host:

```bash
swapon --show
zramctl
```

