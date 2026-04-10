# Docker Hub — repository description (copy/paste source)

**Purpose:** The [Docker Hub UI](https://hub.docker.com/r/fabioleitao/data_boar) **Short description** and **Full description** are **not** stored in Git. This file is the **canonical text** to paste after each release so Hub stays aligned with **`pyproject.toml`**, [docs/deploy/DEPLOY.md](../deploy/DEPLOY.md), and [docs/releases/](../releases/).

**When to update:** Immediately after you push **`fabioleitao/data_boar:<semver>`** and **`latest`** (see [DOCKER_IMAGE_RELEASE_ORDER.md](DOCKER_IMAGE_RELEASE_ORDER.md)). Bump the **`Current release`** line below to match [CHANGELOG.md](../../CHANGELOG.md) / **`pyproject.toml`**.

**Portuguese pointer:** [DOCKER_HUB_REPOSITORY_DESCRIPTION.pt_BR.md](DOCKER_HUB_REPOSITORY_DESCRIPTION.pt_BR.md)

---

## Short description (Docker Hub field — ~100 characters)

Use one line (adjust version when you bump):

```text
Data Boar — PII/sensitive data discovery (LGPD/GDPR-aware). OSS by Fabio Leitao. Tags: latest, 1.6.8. Docs on GitHub.
```

---

## Full description (Docker Hub — Markdown)

Copy from the block below into **Repository → Edit** on Docker Hub.

<!-- markdownlint-disable MD040 MD031 -->

````markdown
## Data Boar

**Compliance-aware discovery** of personal and sensitive data across databases, files, APIs, and more — **data soup** in, structured findings out. Open-source Python stack with optional ML/DL; aligns with **LGPD**, **GDPR**, **CCPA**, and other frameworks via config.

**Current release (image build):** **1.6.8** — same app version as the **`1.6.8`** image tag when published from that release. **`latest`** tracks the most recent Hub push. Always confirm **tags on Hub** match **[GitHub Releases](https://github.com/FabioLeitao/data-boar/releases)** before telling customers a version number.

### Copyright and maintainer

- **Author / copyright:** **Fabio Leitao** — [LICENSE](https://github.com/FabioLeitao/data-boar/blob/main/LICENSE) (BSD-3-Clause).
- **Professional profile:** Add your LinkedIn URL in the Hub **Full description** editor when publishing (do not embed personal profile URLs in this tracked file).
- **Security:** Vulnerability reporting — [SECURITY.md](https://github.com/FabioLeitao/data-boar/blob/main/SECURITY.md).

### Supported tags

- **`fabioleitao/data_boar:latest`** — newest published build
- **`fabioleitao/data_boar:1.6.8`** — pinned semver (example; older semvers may remain pullable)

### Quick start (web API + dashboard on port 8088)

Prepare a directory with `config.yaml` and mount it at `/data`:

```bash
docker pull fabioleitao/data_boar:latest
docker run -d -p 8088:8088 -v "$(pwd)/data:/data" -e CONFIG_PATH=/data/config.yaml fabioleitao/data_boar:latest
```

Create `data/config.yaml` from the repo’s `deploy/config.example.yaml` if you do not have one.

### CLI one-shot (override container command)

Use **`python main.py`** (legacy `run.py` was removed in 1.6.7):

```bash
docker run --rm -v "$(pwd)/data:/data" fabioleitao/data_boar:latest \
  python main.py --config /data/config.yaml
```

### Documentation

- **Usage / CLI / config:** [https://github.com/FabioLeitao/data-boar/blob/main/docs/USAGE.md](https://github.com/FabioLeitao/data-boar/blob/main/docs/USAGE.md)
- **Deploy (Docker Compose, Swarm, Kubernetes):** [https://github.com/FabioLeitao/data-boar/blob/main/docs/deploy/DEPLOY.md](https://github.com/FabioLeitao/data-boar/blob/main/docs/deploy/DEPLOY.md)
- **Releases:** [https://github.com/FabioLeitao/data-boar/releases](https://github.com/FabioLeitao/data-boar/releases)

**Source:** [https://github.com/FabioLeitao/data-boar](https://github.com/FabioLeitao/data-boar)
````

<!-- markdownlint-enable MD040 -->

---

## Maintainer checklist (anti-drift)

1. Push image tags per [DOCKER_IMAGE_RELEASE_ORDER.md](DOCKER_IMAGE_RELEASE_ORDER.md).
1. Paste **Short** + **Full** description from this file into Hub (update **semver**, **Current release**, and **Short description** line if the one-liner mentions the version).
1. Refresh [today-mode/PUBLISHED_SYNC.md](today-mode/PUBLISHED_SYNC.md) ([pt-BR](today-mode/PUBLISHED_SYNC.pt_BR.md)).
1. Sweep **customer-facing** copy: [README.md](../../README.md) / [README.pt_BR.md](../../README.pt_BR.md) **Current release** line, [VERSIONING.md](../VERSIONING.md) checklist, milestone/social drafts that cite a version (see **§ Distribution** in VERSIONING).
