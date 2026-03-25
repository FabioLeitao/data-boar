# Docker image release order: merge → build → bump → push

**Context:** After **PR #99**, the repo uses **`python:3.13-slim`** in the Dockerfile. Operators still need a **repeatable order** so Hub tags, app version, and Scout stay aligned. You prefer **small PRs**; this doc gives a default sequence and trade-offs.

**Related:** [scripts/docker/README.md](../../scripts/docker/README.md), [VERSIONING.md](../VERSIONING.md), [PLANS_TODO.md](../plans/PLANS_TODO.md) (orders **–1**, **–1b**), [HOMELAB_VALIDATION.md](HOMELAB_VALIDATION.md) (order **–1L** when the second environment is ready).

---

## Recommended default (PR-friendly, least confusion)

Use this when you want **one published image** to match **one released app version** (About page, report footer, `fabioleitao/data_boar:1.6.x`).

| Step         | Action                                                                                                                                                                                 |
| ----         | ------                                                                                                                                                                                 |
| 1. **Merge** | All **code** PRs on `main` (Dockerfile, fixes, etc.) — e.g. **#99** ✅                                                                                                                  |
| 2. **Merge** | **Version bump PR** (build `1.6.5` → `1.6.5` per [VERSIONING.md](../VERSIONING.md)) so `pyproject.toml` on `main` is the version you are releasing                                     |
| 3. **Pull**  | `git checkout main && git pull origin main`                                                                                                                                            |
| 4. **Build** | `.\scripts\docker-lab-build.ps1` (from repo root)                                                                                                                                      |
| 5. **Smoke** | Short `docker run` (see [DOCKER_SETUP.md](../DOCKER_SETUP.md) §7 / [DEPLOY.md](../deploy/DEPLOY.md))                                                                                   |
| 6. **Push**  | `.\scripts\docker-hub-publish.ps1 -SkipBuild` (after `docker login`) — tags **`:latest`** and **`:<semver from pyproject>`**, runs **`scout quickview`** + **`scout recommendations`** |
| 7. **Gate**  | `.\scripts\docker-scout-critical-gate.ps1 -Image fabioleitao/data_boar:latest` (fails only for **actionable** CRITICALs with a fixed version)                                          |
| 8. **Prune** | `.\scripts\docker-prune-local.ps1 -WhatIf` then without `-WhatIf` on the homelab                                                                                                       |

**Why version before build/push:** The image **`COPY . .`** includes `pyproject.toml`. Building **after** the bump PR means the running app **inside the container** reports the same version as the **Hub semver tag** you push.

---

## Variants (pros / cons)

### A — Version bump **before** push (recommended above)

- **Pros:** Hub **`fabioleitao/data_boar:1.6.5`** (example) matches **About / reports**; operators can trust tag = app version; one story for support.
- **Cons:** Two PRs (or two merges) before publish if Dockerfile and version ship separately; slightly more ceremony.

### B — Push image **first**, version bump **after**

- **Pros:** Fast validation on Hub (Scout on new digest) before you “stamp” a release number.
- **Cons:** Short window where **`:latest`** digest was built from **`main` still at the previous patch** (e.g. **1.6.3**) — confusing if someone checks **About** vs **Hub tag** the same day. Mitigation: bump **within the same session** or document “pre-release digest”.

### C — Single PR: Dockerfile + version bump together

- **Pros:** One merge, one build, one push — minimal overhead.
- **Cons:** Mixes “infra” and “release”; reviewers may prefer splitting for clarity; not always possible if version bump waits on QA.

### D — Bump without republishing (docs-only / pyproject-only)

- **Pros:** Rare; for pypi/git installs without Docker.
- **Cons:** **Do not** do this if Docker is the primary delivery — Hub would lag the declared version.

---

## A1 / A2 / S4 alignment (not paranoid, just ordered)

- **A1 (Dependabot / –1):** Keep **`pyproject.toml`**, **`uv.lock`**, **`requirements.txt`** aligned; run **`.\scripts\check-all.ps1`** before merge. Use **`.\scripts\maintenance-check.ps1`** for a quick Dependabot + Scout snapshot.
- **A2 (Scout / –1b):** After each **publish**, use **`docker-hub-publish.ps1`** (includes **recommendations**) or Hub UI. **#99** addressed **base image**; remaining counts often need **A1** (packages) + time.
- **Scout CRITICAL gate:** Use **`scripts/docker-scout-critical-gate.ps1`** to separate (a) actionable CRITICALs with a fixed version (**fail + treat now**) from (b) upstream **not fixed** CRITICALs (**document + monitor + rebuild cadence**).
- **S4:** With **#98** and **#99** on **`main`**, the next **S4-shaped** slice is **`pr/deps-security-refresh`** (or equivalent **–1** PR).
- **–1L (second environment):** Run **[HOMELAB_VALIDATION.md](HOMELAB_VALIDATION.md)** when the second machine is ready — **after** –1/–1b are acceptable; no need to block **merge/publish** on it.

---

*Last updated: after **PR #99** merged (`python:3.13-slim` on `main`).*
