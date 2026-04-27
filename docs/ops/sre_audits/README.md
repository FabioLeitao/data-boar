# SRE security audits (read-only deliverables)

Each file in this folder is the deliverable of one **SRE Automation Agent**
audit pass against open PRs and/or the `main` branch.

- **Naming:** `PR_SECURITY_AUDIT_YYYY-MM-DD[_topic].md` (security-tier audits)
  or `PR_RISK_ASSESSMENT_YYYY-MM-DD[_topic].md` (risk-classification +
  reviewer-assignment passes).
- **Convention:** `[Severity] | [Issue] | [Impact]`. Only **Medium** /
  **High** / **Critical** findings are reported per the protocol; "no
  finding" outcomes are still recorded for traceability.
- **Posture:** **audit-and-block, never push to audited branches.** The
  agent does not `git push` to Dependabot or feature branches it is
  reviewing; it opens its own PR with this report and a Slack thread reply.
- **Adversarial vigilance:** PR titles, bodies, branch names, and inline
  comments are *untrusted input*. Risk is derived only from the raw
  `git diff` against `origin/main`.
- **Doctrine:**
  [`../inspirations/DEFENSIVE_SCANNING_MANIFESTO.md`](../inspirations/DEFENSIVE_SCANNING_MANIFESTO.md) ·
  [`../inspirations/THE_ART_OF_THE_FALLBACK.md`](../inspirations/THE_ART_OF_THE_FALLBACK.md) ·
  [`../inspirations/SUPPLY_CHAIN_AND_TRUST_SIGNALS.md`](../inspirations/SUPPLY_CHAIN_AND_TRUST_SIGNALS.md).

## Companion automation

- **`scripts/dependabot-resync.sh` / `scripts/dependabot-resync.ps1`**
  (introduced in PR #239) — paired helper (Linux/macOS + Windows) the
  operator runs **on a checked-out Dependabot pip PR branch** to refresh
  `uv.lock` and `requirements.txt` with the canonical
  `uv export --no-emit-package pyproject.toml` flags so
  `tests/test_dependency_artifacts_sync.py` and the matching pre-commit
  hook turn green again. Conventional Commit message used:
  `chore(deps): resync uv.lock + requirements.txt after Dependabot bump`.

## Index

| Date       | File                                                                                              | Scope                                                                       |
| ---------- | ------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------- |
| 2026-04-27 | [PR_RISK_ASSESSMENT_2026-04-27_assessor.md](PR_RISK_ASSESSMENT_2026-04-27_assessor.md)            | Risk-assessor pass on 13 open PRs (#221 – #239); merge-order trap on MSSQL. |
