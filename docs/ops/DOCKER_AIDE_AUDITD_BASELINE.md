# Docker CE + AIDE + auditd baseline (LAB-OP friendly)

**pt-BR:** [DOCKER_AIDE_AUDITD_BASELINE.pt_BR.md](DOCKER_AIDE_AUDITD_BASELINE.pt_BR.md)

## What we learned from LAB-OP hosts

- `lab-node-02` runs **Docker Engine (CE)** and has **Swarm active** (single-node manager).
- `LAB-NODE-04` has **AIDE** configured under `/etc/aide/` and **auditd rules** under `/etc/audit/rules.d/`.

## Automation

- Docker CE: `ops/automation/ansible/roles/lab-node-01_docker_ce`
  - `lab-node-01_install_docker_ce=false` by default
  - optional: write `/etc/docker/daemon.json`
  - optional: `docker swarm init`
- AIDE: `ops/automation/ansible/roles/lab-node-01_aide`
- auditd: `ops/automation/ansible/roles/lab-node-01_auditd`

## Policy for exceptions

Keep allowlists/ignores **commented** until confirmed, and store host-specific details in `docs/private/homelab/`.

