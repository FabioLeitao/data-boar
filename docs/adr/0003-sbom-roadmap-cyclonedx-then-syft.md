# ADR 0003: SBOM roadmap — CycloneDX (JSON) first, then Syft on Docker images

**Status:** Accepted

**Date:** 2026-03-26

## Context

A **Software Bill of Materials (SBOM)** improves **compliance** narratives and **incident response** (mapping CVEs to what shipped). The project already runs **`pip-audit`** in CI for known vulnerabilities; a **formal** SBOM adds a portable inventory for enterprises and for releases.

Two common outputs matter for this codebase:

1. **Python application** — resolved dependencies (best source: **`uv.lock`** / environment export).
1. **Published Docker image** — OS + Python layers include packages not visible from the lockfile alone.

## Decision

1. **Phase A (next):** Generate **CycloneDX JSON** with a **recent spec version** (e.g. 1.5+) from the **application** dependency set, attached as a **release artifact** or CI artifact on tagged releases. Prefer tooling that reads **`uv.lock`** or an **`uv export`** snapshot for fidelity.
1. **Phase B (soon after):** Add **Syft** (or equivalent) against the **published** **`fabioleitao/data_boar`** image (or internal tag) so the **image** SBOM complements the Python SBOM.
1. Document the **where to download** and **which tag** the SBOM belongs to in **[SECURITY.md](../../SECURITY.md)** and/or **[docs/RELEASE_INTEGRITY.md](../RELEASE_INTEGRITY.md)** when automation lands; keep secrets and internal registry URLs out of tracked docs.

## Consequences

- **Positive:** Clear story for procurement and security questionnaires; faster answers to “what shipped in 1.x.y?”.
- **Negative:** CI/release script maintenance; must regenerate when lockfile or base image changes.

## References

- [docs/QUALITY_WORKFLOW_RECOMMENDATIONS.md](../QUALITY_WORKFLOW_RECOMMENDATIONS.md) — SBOM section
- [SECURITY.md](../../SECURITY.md) — dependency and reporting context
- [docs/RELEASE_INTEGRITY.md](../RELEASE_INTEGRITY.md) — release integrity posture
