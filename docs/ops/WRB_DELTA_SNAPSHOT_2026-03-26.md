# WRB — delta snapshot for next mail (2026-03-26)

**Português (Brasil):** [WRB_DELTA_SNAPSHOT_2026-03-26.pt_BR.md](WRB_DELTA_SNAPSHOT_2026-03-26.pt_BR.md)

Paste the **paragraph below** into your Wabbix email **after** the master prompt in [WABBIX_REVIEW_REQUEST_GUIDELINE.md](WABBIX_REVIEW_REQUEST_GUIDELINE.md) (or merge into §2 in [WABBIX_WRB_REVIEW_AND_SEND.pt_BR.md](WABBIX_WRB_REVIEW_AND_SEND.pt_BR.md) before send). Update **commit hash** if you send after a new merge.

---

## Version truth (avoid confusion)

- **`pyproject.toml` / docs** on `main` already target **1.6.7** (see `docs/releases/1.6.7.md`).
- **Latest Git tag** in many clones is still **`v1.6.6`** until the maintainer runs **`git tag v1.6.7`** and pushes **GitHub Release** / **Docker Hub** per [DOCKER_IMAGE_RELEASE_ORDER.md](DOCKER_IMAGE_RELEASE_ORDER.md).
- Ask Wabbix to treat **“since last market delivery”** as **since `v1.6.6` tag** until **`v1.6.7`** exists, unless they confirm a newer tag on GitHub.

---

## English paste block (optional annex to the long request)

```text
Supplementary context (2026-03-26):

Since our last WRB cycle and since tag v1.6.6, main has accumulated (or will ship in the next merge) work including: CI lint job aligned with `pre-commit run --all-files` (Ruff, plans-stats --check, markdown, pt-BR locale, commercial guard); new local hook `plans-stats-check`; Semgrep workflow for Python SAST; ADR series 0000–0003 (origin baseline, MD029, operator docs, SBOM roadmap); docs/ops/WORKFLOW_DEFERRED_FOLLOWUPS; academic thesis guidance (ACADEMIC_USE_AND_THESIS + pt-BR); quality rule/skill updates; Slack operator ping verified.

Please keep the three time lenses separate. For “since last tagged release”, use v1.6.6 as baseline until v1.6.7 tag appears on GitHub, even if pyproject already reads 1.6.7 on main.
```

---

## Related

- [WABBIX_IN_REPO_BASELINE.md](WABBIX_IN_REPO_BASELINE.md) — paths for reviewers.
- [PLANS_TODO.md](../plans/PLANS_TODO.md) — backlog state.
