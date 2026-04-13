# ADR 0008: Docker CE (official repo) + Compose plugin + Swarm as primary lab container runtime

**Status:** Accepted
**Date:** 2026-04-03

## Context

The lab-op environment (ThinkPad T14 running LMDE 7 / Debian Trixie) needs a container runtime to:

1. Build and run the **Data Boar** Docker image locally during development.
2. Test multi-service compositions (detector + database + dashboard) via `docker compose`.
3. Optionally test **Swarm stack deployments** (`docker stack deploy`) as a lightweight
   simulation of multi-node orchestration without full Kubernetes overhead.
4. Eventually hand off reproducible container procedures to collaborators (team members).

Three options were evaluated:

| Option | Pros | Cons |
|---|---|---|
| **`docker.io` (Debian apt)** | Simple install, no extra repo | Lags Docker Inc releases by months; no compose plugin |
| **`docker-ce` (official Docker repo)** | Latest stable, compose plugin included, buildx included | Extra GPG/repo step |
| **Podman only** | Rootless, daemon-free, OCI-compatible | `docker compose` compatibility requires `podman-compose` shim; some edge cases; team unfamiliar |
| **k3s / k8s** | Full orchestration | 300–500 MB RAM idle; heavy for a developer workstation; overkill for single-service testing |

The project team (small, mostly Linux + Docker background) already has existing `Dockerfile` and
`docker-compose.yml` infrastructure targeting Docker semantics. Swarm is used in the lab to test
`docker stack deploy` workflows and overlay networks without spinning up full Kubernetes.

## Decision

1. **Primary runtime:** install `docker-ce` from the **official Docker apt repository** (`download.docker.com/linux/debian`)
   with `docker-compose-plugin` and `docker-buildx-plugin` — not `docker.io` from Debian repositories.
2. **Compose:** use `docker compose` (plugin) as the canonical compose interface; `docker-compose` (v1 Python) is not used.
3. **Swarm:** **on by default** in **`t14-baseline.yml`** and **`t14_docker_ce`** defaults (`t14_docker_swarm_init: true`)
   so **`docker service`** / **`docker stack deploy`** work on a single-node manager without manual **`docker swarm init`**.
   Set **`t14_docker_swarm_init: false`** in inventory on hosts that must stay in non-Swarm mode only.
4. **Podman:** installed alongside Docker as a secondary, rootless alternative via the `t14_podman` Ansible role,
   but not aliased to `docker` by default — `t14_podman_docker_alias: false`.
5. **k3s:** opt-in only via `t14_k3s` Ansible role (`t14_install_k3s: false`). Not recommended on the T14
   unless the goal is to test Kubernetes-specific workflows (Helm charts, NetworkPolicy, namespaces).
6. **daemon.json baseline:** `live-restore: true`, `overlay2` storage driver, custom address pool
   (`172.30.0.0/16`) to avoid collision with lab LAN (`192.168.x.x`), and log rotation (20 MB × 5 files).

## Consequences

- **Positive:** Consistent `docker compose` interface for all team members; latest engine features; compose-plugin
  replaces the deprecated Python `docker-compose` without a separate install step; Swarm initialized by default for service/stack workflows (opt-out per host).
- **Positive:** Podman provides an escape hatch for rootless scenarios (CI, restricted environments) without
  losing Docker compatibility for the main development loop.
- **Negative:** Requires adding the Docker GPG key and apt source — one extra step in fresh installs (automated
  by the `t14_docker_ce` Ansible role).
- **Negative:** Two container runtimes in parallel (Docker + Podman) could create confusion if a developer
  runs `podman` commands and then inspects with `docker ps`. Mitigated by not setting the `docker` alias.
- **Watch:** `docker.io` vs `docker-ce` package conflicts — if both are installed, the Ansible role should
  detect and prefer `docker-ce`. A future task may add an explicit conflict guard.

## References

- [docs/ops/LMDE7_T14_DEVELOPER_SETUP.pt_BR.md](../ops/LMDE7_T14_DEVELOPER_SETUP.pt_BR.md) §7.1–§7.3
- [ops/automation/ansible/roles/t14_docker_ce/](../../ops/automation/ansible/roles/t14_docker_ce/)
- [ops/automation/ansible/roles/t14_podman/](../../ops/automation/ansible/roles/t14_podman/)
- [ops/automation/ansible/roles/t14_k3s/](../../ops/automation/ansible/roles/t14_k3s/)
- [ops/automation/ansible/playbooks/t14-baseline.yml](../../ops/automation/ansible/playbooks/t14-baseline.yml)
