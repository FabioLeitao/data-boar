# Published release vs repo version (anti-stale)

**Português (Brasil):** [PUBLISHED_SYNC.pt_BR.md](PUBLISHED_SYNC.pt_BR.md)

**Purpose:** After you cut a **Git tag**, **GitHub Release**, or **Docker Hub** push, dated “today mode” files and **PLANS** tables can still say “operator pending” elsewhere. This page is the **short reconciliation record**: refresh it when reality changes.

---

## Last verified (operator or agent)

| Field | Value |
| ----- | ----- |
| **Verified** | **2026-04-22** |
| **`pyproject.toml` on `main`** | **1.7.2+safe** (golden / **v1.7.2-safe** tag; next pre-release bump follows [VERSIONING.md](../VERSIONING.md)) |
| **GitHub Release Latest** | [**v1.7.2-safe**](https://github.com/FabioLeitao/data-boar/releases/tag/v1.7.2-safe) (notes: **`docs/releases/1.7.2-safe.md`**, **`CHANGELOG.md`**) |
| **Docker Hub** | **`fabioleitao/data_boar:v1.7.2-safe`** + **`latest`** (same digest) — `sha256:8cb0d3ff549b46d2bbb519874790a8a43531b7da8b6801601f87ff0e1965cf95`; **Full description** from **[`docs/ops/DOCKER_HUB_REPOSITORY_DESCRIPTION.md`](../DOCKER_HUB_REPOSITORY_DESCRIPTION.md)** |
| **Next public version** (when `main` has a new bundle) | **1.7.2** — follow **`docs/VERSIONING.md`** + **`docs/releases/`** |

---

## How to re-check (copy/paste)

From repo root (needs **`gh`** auth + network):

```bash
git fetch origin --tags
git tag -l "v1.6.*" --sort=-version:refname | head -5
grep -n '^version' pyproject.toml
gh release list --repo FabioLeitao/data-boar --limit 5
```

Docker Hub: confirm **`v1.7.2-safe`** and **`latest`** on [hub.docker.com/r/fabioleitao/data_boar/tags](https://hub.docker.com/r/fabioleitao/data_boar/tags) or the Registry API; **Full description** matches **[`docs/ops/DOCKER_HUB_REPOSITORY_DESCRIPTION.md`](../DOCKER_HUB_REPOSITORY_DESCRIPTION.md)**. **GitHub:** **`v1.7.2-safe`** Release exists.

---

## When to update this file

- **Immediately after** tag + GitHub Release + Docker push for a new version.
- **Optionally** on a slow week: confirm row still true so carryover tables do not resurrect **done** work.
- **Always** align **`docs/plans/PLANS_TODO.md`** release bullets if they still say “in-repo / operator pending” for the same number.

Automation note: **`tests/test_about_version_matches_pyproject.py`** guards **`pyproject.toml`** ↔ runtime/man `.TH`; it does **not** query GitHub or Hub — human or agent verification stays here.
