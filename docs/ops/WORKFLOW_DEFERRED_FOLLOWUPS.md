# Workflow and supply-chain follow-ups (deferred deep dive)

**Português (Brasil):** [WORKFLOW_DEFERRED_FOLLOWUPS.pt_BR.md](WORKFLOW_DEFERRED_FOLLOWUPS.pt_BR.md)

Short backlog of **useful** items mentioned in maintainer sessions but **not** fully implemented in the same pass as pre-commit/CI alignment. Use this file so nothing important is lost; promote items to **`docs/plans/`** when they become active work.

---

## Already improved in-repo (context)

- **CI lint** runs **`uv run pre-commit run --all-files`**, matching **`.pre-commit-config.yaml`** (including **`plans-stats.py --check`**).
- **Local:** **`uv run pre-commit install`** runs the same hooks on **`git commit`** (one-time per clone).
- **ADRs:** [docs/adr/README.md](../adr/README.md) — includes MD029, operator docs, SBOM roadmap.

---

## Still to deepen (pick by priority)

| Topic | Note |
| ----- | ---- |
| **Branch protection** | Enable in GitHub when **required checks** are stable: **CI** (Test, Lint/pre-commit, Audit, Bandit) plus **Semgrep** (and **CodeQL** policy if you treat it as merge-blocking). See [QUALITY_WORKFLOW_RECOMMENDATIONS.md](../QUALITY_WORKFLOW_RECOMMENDATIONS.md) §9. |
| **SBOM** | **CycloneDX JSON** from lockfile first, then **Syft** on the Docker image — [ADR 0003](../adr/0003-sbom-roadmap-cyclonedx-then-syft.md). |
| **Dependabot auto-merge** | Only with strict checks and clear policy; avoid merging deps without human glance on security PRs. |
| **GitHub Environments** | For future deploy secrets / approval gates if you add staged releases. |
| **Artifact retention / attestations** | SLSA-style provenance if enterprise customers ask; optional. |
| **Scheduled audit** | Optional weekly **`pip-audit`** workflow as a reminder (does not replace push-triggered CI). |
| **CODEOWNERS** | For **`api/`**, **`core/`**, **`SECURITY.md`** when external contributors grow. |
| **mypy** | Gradual typing; not a merge gate until triage — [QUALITY_WORKFLOW_RECOMMENDATIONS.md](../QUALITY_WORKFLOW_RECOMMENDATIONS.md) §5. |

---

## Release reminder (1.6.7 and next)

- **In-repo version** **`1.6.7`** is documented in **`pyproject.toml`** and **`docs/releases/1.6.7.md`**; **Git tag** **`v1.6.7`** may lag until the operator publishes.
- Before the **next** tag: run **`.\scripts\check-all.ps1`**, refresh **`plans-stats`** if **`PLANS_TODO.md`** changed, confirm Docker Hub / release checklist in [DOCKER_IMAGE_RELEASE_ORDER.md](DOCKER_IMAGE_RELEASE_ORDER.md).

---

## Related

- [OPERATOR_NOTIFICATION_CHANNELS.md](OPERATOR_NOTIFICATION_CHANNELS.md) — Slack + GitHub redundancy
- [COMMIT_AND_PR.md](COMMIT_AND_PR.md) — PR workflow
