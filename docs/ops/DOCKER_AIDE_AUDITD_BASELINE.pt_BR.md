# Baseline Docker CE + AIDE + auditd (LAB-OP friendly)

**English:** [DOCKER_AIDE_AUDITD_BASELINE.md](DOCKER_AIDE_AUDITD_BASELINE.md)

## O que aprendemos com hosts do LAB-OP

- `lab-node-02` roda **Docker Engine (CE)** e tem **Swarm ativo** (manager single-node).
- `LAB-NODE-04` tem **AIDE** em `/etc/aide/` e regras de **auditd** em `/etc/audit/rules.d/`.

## Automação

- Docker CE: `ops/automation/ansible/roles/lab-node-01_docker_ce`
  - `lab-node-01_install_docker_ce=false` por padrão
  - opcional: escrever `/etc/docker/daemon.json`
  - opcional: `docker swarm init`
- AIDE: `ops/automation/ansible/roles/lab-node-01_aide`
- auditd: `ops/automation/ansible/roles/lab-node-01_auditd`

## Política de exceções

Mantenha allowlists/ignores **comentados** até confirmar e guarde detalhes por host em `docs/private/homelab/`.

