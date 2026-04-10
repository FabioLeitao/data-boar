# Baseline Docker CE + AIDE + auditd (LAB-OP friendly)

**English:** [DOCKER_AIDE_AUDITD_BASELINE.md](DOCKER_AIDE_AUDITD_BASELINE.md)

## O que aprendemos com hosts do LAB-OP

- O **host x86_64 principal lab-op** roda **Docker Engine (CE)** com **Swarm ativo** (manager single-node).
- Um **SBC ARM secundário** no lab tem **AIDE** em `/etc/aide/` e regras de **auditd** em `/etc/audit/rules.d/`. (Nomes de máquina ficam só em **`docs/private/homelab/`**.)

## Automação

- Docker CE: `ops/automation/ansible/roles/t14_docker_ce`
  - `t14_install_docker_ce=false` por padrão
  - opcional: escrever `/etc/docker/daemon.json`
  - opcional: `docker swarm init`
- AIDE: `ops/automation/ansible/roles/t14_aide`
- auditd: `ops/automation/ansible/roles/t14_auditd`

## Política de exceções

Mantenha allowlists/ignores **comentados** até confirmar e guarde detalhes por host em `docs/private/homelab/`.

