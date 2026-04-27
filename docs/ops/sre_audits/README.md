# SRE security audits (read-only deliverables)

Each file in this folder is the deliverable of one **SRE Automation Agent**
audit pass against open PRs and/or the `main` branch.

- **Naming:** `PR_SECURITY_AUDIT_YYYY-MM-DD.md` (one file per audit pass).
- **Convention:** `[Severity] | [Issue] | [Impact]`. Only **Medium** /
  **High** / **Critical** findings are reported per the protocol; "no
  finding" outcomes are still recorded for traceability.
- **Posture:** **audit-and-block, never push to audited branches.** The
  agent does not `git push` to Dependabot or feature branches it is
  reviewing; it opens its own PR with this report and a Slack thread reply.
- **Doctrine:**
  [`../inspirations/DEFENSIVE_SCANNING_MANIFESTO.md`](../inspirations/DEFENSIVE_SCANNING_MANIFESTO.md) ·
  [`../inspirations/THE_ART_OF_THE_FALLBACK.md`](../inspirations/THE_ART_OF_THE_FALLBACK.md) ·
  [`../inspirations/SUPPLY_CHAIN_AND_TRUST_SIGNALS.md`](../inspirations/SUPPLY_CHAIN_AND_TRUST_SIGNALS.md).

## Index

| Date       | File                                                       | Scope                                       |
| ---------- | ---------------------------------------------------------- | ------------------------------------------- |
| 2026-04-27 | [PR_SECURITY_AUDIT_2026-04-27.md](PR_SECURITY_AUDIT_2026-04-27.md) | All five open PRs (1 cargo, 4 pip Dependabot). |

