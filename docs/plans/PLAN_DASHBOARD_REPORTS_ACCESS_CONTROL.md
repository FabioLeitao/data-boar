# Plan: Dashboard / reports access control (roles & permissions)

**Status:** Not started (backlog — tracked from GitHub)

**Horizon / urgency:** `[H2]` / `[U2]` — after **Priority band A** and when multi-tenant / multi-user dashboard exposure is real, not before core scan stability.

**GitHub:** [Issue #86](https://github.com/FabioLeitao/data-boar/issues/86) (feature request; migrated narrative from Redmine-reports context).

**Synced with:** [PLANS_TODO.md](PLANS_TODO.md) (GitHub issues queue + recommended sequence).

**Cluster (same code paths, different goals):** This plan is the **authorisation / exposure** slice for the HTML app. **[PLAN_DASHBOARD_I18N.md](PLAN_DASHBOARD_I18N.md)** is the **locale** slice. They are **not duplicates**: merging them into one document would blur acceptance criteria (security vs translation). Do **entangle sequencing**: any work that changes **route layout** (e.g. `/{locale}/reports`) or **middleware stack** should consider both plans in the same sprint **design** pass—even if implementation stays in separate PRs. See **§ Relationship to other plans** below.

---

## Problem statement

Today, anyone who can reach the web UI can open **dashboard**, **reports list**, and (subject to path safety) **report downloads** when `api.require_api_key` is **false** (typical lab / trusted-network installs). A **single shared API key** (when `require_api_key: true`) applies **globally** via middleware: it does **not** distinguish “may run scans” vs “may only view reports” vs “config admin”. For **zero-trust** or **segregation-of-duties** goals, **reverse-proxy** path rules help but do not encode **in-app** RBAC/RAC.

---

## Type of work

| Label           | Note                                                                                   |
| ------------    | --------------------------------------------------------------------                   |
| **Feature**     | Permission or role gate on `/reports`, `/report`, `/reports/{id}`, heatmaps as needed. |
| **Security UX** | Reduces accidental exposure of compliance artefacts to the wrong audience.             |
| **Not a bug**   | Current behaviour is documented as deployment-dependent; tightening is **opt-in**.     |

---

## Workarounds (today — document, don’t block)

1. **Network / LB:** Restrict routes (`/reports`, `/report`, `/heatmap`) at reverse proxy; mTLS or VPN for admin paths.
1. **Global API key:** `api.require_api_key: true` — browsers need to send `X-API-Key` / `Authorization: Bearer` (clunky for pure HTML unless extended).
1. **Split listeners:** Internal bind for dashboard, no public ingress (Kubernetes `ClusterIP`, firewall).

See [SECURITY.md](../SECURITY.md), [USAGE.md](../USAGE.md), [TECH_GUIDE.md](../TECH_GUIDE.md) for deployment guidance.

---

## Target direction (phased — no IdP commitment in v1)

| Phase | Scope                   | Outcome                                                                                                                                                                                                                            |
| ----- | -----                   | -------                                                                                                                                                                                                                            |
| **0** | Docs only               | Explicit matrix: which routes are unauthenticated by default; proxy recipes; link #86.                                                                                                                                             |
| **1** | Config + middleware     | Optional **route class** map: e.g. `public` / `authenticated` / `admin`; reuse or extend API key so **HTML** flows can pass key (header or **httpOnly cookie** set by operator-owned login page — out of scope for minimal slice). |
| **2** | Roles in config         | Named roles (e.g. `scanner`, `reports_reader`, `config_admin`) and **allowlists** per route family; multiple keys or JWT claims (design TBD).                                                                                      |
| **3** | External IdP (optional) | OIDC / SSO groups mapped to roles — only if product moves to enterprise multi-user.                                                                                                                                                |

**Non-goals for early phases:** Full user database, password reset flows, or replacing the operator’s IdP.

---

## Dependencies & sequencing

- **Depends on:** Stable report path safety (already hardened); optional alignment with **commercial licensing / JWT** work ([LICENSING_SPEC.md](../LICENSING_SPEC.md)) if roles are carried in tokens.
- **Conflicts with:** None; additive flags, default preserves today’s behaviour until enabled.
- **Token-aware:** Treat as **one plan file + one implementation slice per session**; start with Phase 0–1 only.

### Sequencing with dashboard i18n ([PLAN_DASHBOARD_I18N.md](PLAN_DASHBOARD_I18N.md))

**Shared risk:** Changing HTML routes **twice** (once unprefixed for RBAC, again for `/{locale}/…`) wastes review and tokens.

| Step               | Track                    | Action                                                                                                                                                                                                                                                                   |
| ----               | -----                    | ------                                                                                                                                                                                                                                                                   |
| **D-WEB**          | Both                     | **Design-only:** URL map + **middleware order** (API key, locale resolution for HTML, route-class / RBAC). Cross-link between this file and the i18n plan.                                                                                                               |
| **Implementation** | i18n first (recommended) | **M-LOCALE-V1:** path-prefixed HTML + `en` / `pt-BR` JSON + negotiation; **no** new RBAC semantics required on first merge if defaults unchanged.                                                                                                                        |
| **Implementation** | #86                      | Phase **0** (docs) can ship anytime. Phase **1+** gates should target the **same prefixed paths** as i18n (e.g. `/{locale}/reports`), not legacy unprefixed HTML — unless a **security exception** forces early guards on old paths (then budget a **migration** slice). |

Details and anti-footgun rules: **PLAN_DASHBOARD_I18N.md** § *Meshing with dashboard reports RBAC*.

---

## Completion checklist (when implementing)

- [ ] USAGE + TECH_GUIDE + SECURITY (EN + pt-BR where paired) updated.
- [ ] Tests for new middleware or route guards (`tests/test_api_key.py` or new module).
- [ ] This file + [PLANS_TODO.md](PLANS_TODO.md) + [SPRINTS_AND_MILESTONES.md](SPRINTS_AND_MILESTONES.md) updated; close or update GitHub #86 when shipped.

---

## Relationship to other plans (entangled, not merged)

| Plan / doc                                                                       | Overlap                                                                              | How to treat it                                                                                                                                                                                                          |
| ----------                                                                       | -------                                                                              | ----------------                                                                                                                                                                                                         |
| [PLAN_DASHBOARD_I18N.md](PLAN_DASHBOARD_I18N.md)                                 | Same routes and templates (`/`, `/reports`, …).                                      | **Coordinate:** **D-WEB** design checkpoint first; then implement **locale prefix** before or with **Phase 1+** RBAC on **prefixed** paths — see **§ Sequencing with dashboard i18n** above. i18n does not replace RBAC. |
| [LICENSING_SPEC.md](../LICENSING_SPEC.md) / commercial JWT                       | Product **license** claims (`dbtier`, …) vs **session** roles (`reports_reader`, …). | **Optional convergence** in a far enterprise phase: both might read JWT-shaped claims; keep **specs separate** until requirements are explicit—no need to fold this plan into licensing docs.                            |
| [completed/PLAN_RATE_LIMIT_SCANS.md](completed/PLAN_RATE_LIMIT_SCANS.md)         | GET `/reports`, `/heatmap` intentionally not rate-limited for reads.                 | **Compatible:** RBAC restricts *who*; rate limits restrict *how hard*. Changing either should mention the other in release notes.                                                                                        |
| [PLAN_SELENIUM_QA_TEST_SUITE.md](PLAN_SELENIUM_QA_TEST_SUITE.md)                 | Future E2E on dashboard flows.                                                       | When RBAC lands, QA plan should add cases for **forbidden** vs **allowed** roles on `/reports`.                                                                                                                          |
| [SECURITY.md](../SECURITY.md), [USAGE.md](../USAGE.md)                           | Deployment and `api.require_api_key`.                                                | **Phase 0** of this plan extends those docs; no separate “security plan” file required.                                                                                                                                  |
| [PLAN_OPERATOR_API_KEY_FIRST_AUTH_UX.md](PLAN_OPERATOR_API_KEY_FIRST_AUTH_UX.md) | Reducing JWT/manual-Bearer **toil** before RBAC complexity.                          | Exploratory spike: env + API key patterns for automation; **coordinate** if HTML flows need cookie/header UX (Phase 1 here).                                                                                             |

**Why keep a dedicated plan file:** Issue [#86](https://github.com/FabioLeitao/data-boar/issues/86) is a **trackable product ask** with its own phases and completion checklist. Folding it only into i18n or licensing would hide it from the **GitHub issues queue** table in [PLANS_TODO.md](PLANS_TODO.md).

---

## See also

- [PLAN_DASHBOARD_I18N.md](PLAN_DASHBOARD_I18N.md) — locale (orthogonal concern; coordinate route/middleware design).
- [PLAN_NOTIFICATIONS_OFFBAND_AND_SCAN_COMPLETE.md](PLAN_NOTIFICATIONS_OFFBAND_AND_SCAN_COMPLETE.md) — operator channels (complementary ops story).
