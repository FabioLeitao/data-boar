# Operator today mode — 2026-04-16 (carryover + effective focus)

**Português (Brasil):** [OPERATOR_TODAY_MODE_2026-04-16.pt_BR.md](OPERATOR_TODAY_MODE_2026-04-16.pt_BR.md)

---

## Session QA / handoff (evening 2026-04-15 → morning readiness)

- **`origin/main`:** Merged **#186** (pytest **9.0.2 → 9.0.3**); pull on this machine if you have not since that merge.
- **CI on merged work:** Green on **#186** at merge time (Analyze, CodeQL, SBOM, Semgrep). **Uncommitted local edits** are **not** CI-verified until you commit and push — run **`.\scripts\check-all.ps1`** before any PR.
- **Planning / docs slice:** Enterprise discovery framed as **three complementary tracks** — [ADR 0024](../../adr/0024-enterprise-discovery-three-complementary-tracks.md); plans **PLAN_SCOPE_IMPORT_FROM_EXPORTS**, **PLAN_ADDITIONAL_DATA_SOUP_FORMATS** (narrative §), **PLAN_OPT_IN_NETWORK_PORT_SERVICE_HINTS** (worst-case zero inventory); **PLANS_TODO** / **PLANS_HUB** WIP bullets (**not** a legal promise).
- **Open PRs:** Run **`gh pr list --state open`** after wake — list may be empty if nothing new opened overnight.

---

## Block 0 — Morning reality check (10–15 min)

1. `git fetch origin` · `git status -sb` · `gh pr list --state open`
2. **`git pull origin main`** if behind.
3. **Working tree:** commit or branch the pending bundle (large WIP) when ready; **`check-all`** before push.
4. **Stacked private git:** if **`docs/private/`** has pending commits, **`.\scripts\private-git-sync.ps1`** per policy.

**Canonical rolling queue:** [CARRYOVER.md](CARRYOVER.md) · **Published truth:** [PUBLISHED_SYNC.md](PUBLISHED_SYNC.md)

---

## Carryover — (edit)

- [ ] Review uncommitted diff; group into coherent commits (plans + ADR + today-mode vs other WIP).
- [ ] (add items)

---

## End of day

- **`eod-sync`** or **`.\scripts\operator-day-ritual.ps1 -Mode Eod`**
- Prepare **`OPERATOR_TODAY_MODE_<next-date>.md`** when the day closes

---

## Quick references

- **ADR index:** [docs/adr/README.md](../../adr/README.md)
- Session keywords: **`.cursor/rules/session-mode-keywords.mdc`**
