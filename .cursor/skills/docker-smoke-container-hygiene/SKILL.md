---
name: docker-smoke-container-hygiene
description: >-
  After local Data Boar Docker smoke tests, keep at most one or two named containers,
  remove throwaway ones, and document cleanup. Use when creating containers, running
  lab validation, or closing a session that used docker run/compose for data_boar.
---

# Docker smoke container hygiene (Data Boar)

## When to use

- You (or the operator) ran `docker build`, `docker run`, or `docker compose` for **Data Boar** (`data_boar` image, `data-boar-*` names).
- The session is ending or you are about to open a PR after smoke verification.
- Docker Desktop is accumulating stopped containers from repeated tests.

## Instructions

1. **Inventory** local Data Boar-related containers (name filter is enough for most cases):
   - `docker ps -a` and look for `data-boar`, `data_boar`, or compose project service names from `deploy/`.
2. **Retention policy**
   - **Normal:** keep **one** container (or one compose stack) for day-to-day dev.
   - **A/B or regression:** keep **at most two** intentionally named containers (e.g. different tags or configs). Anything else is **throwaway**.
3. **Cleanup suggestion** (confirm with the operator before `rm -f`):
   - Stop: `docker stop <name>`
   - Remove: `docker rm <name>`
   - Compose: `docker compose -f deploy/docker-compose.yml … down` (add override file if used).
4. **Document** in the session or PR description if smoke was run and **which** container name/tag was kept, so the next run does not spawn duplicates.
5. **Agents:** do not delete containers autonomously; **propose** commands and remind the operator to keep only 1–2 instances unless A/B is required.

## Rationale

Stale containers confuse port mappings (`8088`), volume mounts, and Scout/quickview workflows; they also waste disk. A single explicit policy matches [docs/DOCKER_SETUP.md](../../../docs/DOCKER_SETUP.md) §7 and [docs/HOMELAB_VALIDATION.md](../../../docs/HOMELAB_VALIDATION.md).
