# Plan: Dashboard / reports access control (roles & permissions)

**Status:** Not started (backlog — tracked from GitHub)

**Horizon / urgency:** `[H2]` / `[U2]` — after **Priority band A** and when multi-tenant / multi-user dashboard exposure is real, not before core scan stability.

**GitHub:** [Issue #86](https://github.com/FabioLeitao/data-boar/issues/86) (feature request; migrated narrative from Redmine-reports context).

**Synced with:** [PLANS_TODO.md](PLANS_TODO.md) (GitHub issues queue + recommended sequence).

---

## Problem statement

Today, anyone who can reach the web UI can open **dashboard**, **reports list**, and (subject to path safety) **report downloads** when `api.require_api_key` is **false** (typical lab / trusted-network installs). A **single shared API key** (when `require_api_key: true`) applies **globally** via middleware: it does **not** distinguish “may run scans” vs “may only view reports” vs “config admin”. For **zero-trust** or **segregation-of-duties** goals, **reverse-proxy** path rules help but do not encode **in-app** RBAC/RAC.

---

## Type of work

| Label        | Note                                                                 |
| ------------ | -------------------------------------------------------------------- |
| **Feature**  | Permission or role gate on `/reports`, `/report`, `/reports/{id}`, heatmaps as needed. |
| **Security UX** | Reduces accidental exposure of compliance artefacts to the wrong audience. |
| **Not a bug** | Current behaviour is documented as deployment-dependent; tightening is **opt-in**. |

---

## Workarounds (today — document, don’t block)

1. **Network / LB:** Restrict routes (`/reports`, `/report`, `/heatmap`) at reverse proxy; mTLS or VPN for admin paths.
2. **Global API key:** `api.require_api_key: true` — browsers need to send `X-API-Key` / `Authorization: Bearer` (clunky for pure HTML unless extended).
3. **Split listeners:** Internal bind for dashboard, no public ingress (Kubernetes `ClusterIP`, firewall).

See [SECURITY.md](../SECURITY.md), [USAGE.md](../USAGE.md), [TECH_GUIDE.md](../TECH_GUIDE.md) for deployment guidance.

---

## Target direction (phased — no IdP commitment in v1)

| Phase | Scope | Outcome |
| ----- | ----- | ------- |
| **0** | Docs only | Explicit matrix: which routes are unauthenticated by default; proxy recipes; link #86. |
| **1** | Config + middleware | Optional **route class** map: e.g. `public` / `authenticated` / `admin`; reuse or extend API key so **HTML** flows can pass key (header or **httpOnly cookie** set by operator-owned login page — out of scope for minimal slice). |
| **2** | Roles in config | Named roles (e.g. `scanner`, `reports_reader`, `config_admin`) and **allowlists** per route family; multiple keys or JWT claims (design TBD). |
| **3** | External IdP (optional) | OIDC / SSO groups mapped to roles — only if product moves to enterprise multi-user. |

**Non-goals for early phases:** Full user database, password reset flows, or replacing the operator’s IdP.

---

## Dependencies & sequencing

- **Depends on:** Stable report path safety (already hardened); optional alignment with **commercial licensing / JWT** work ([LICENSING_SPEC.md](../LICENSING_SPEC.md)) if roles are carried in tokens.
- **Conflicts with:** None; additive flags, default preserves today’s behaviour until enabled.
- **Token-aware:** Treat as **one plan file + one implementation slice per session**; start with Phase 0–1 only.

---

## Completion checklist (when implementing)

- [ ] USAGE + TECH_GUIDE + SECURITY (EN + pt-BR where paired) updated.
- [ ] Tests for new middleware or route guards (`tests/test_api_key.py` or new module).
- [ ] This file + [PLANS_TODO.md](PLANS_TODO.md) + [SPRINTS_AND_MILESTONES.md](SPRINTS_AND_MILESTONES.md) updated; close or update GitHub #86 when shipped.

---

## See also

- [PLAN_DASHBOARD_I18N.md](PLAN_DASHBOARD_I18N.md) — dashboard UX backlog (orthogonal).
- [PLAN_NOTIFICATIONS_OFFBAND_AND_SCAN_COMPLETE.md](PLAN_NOTIFICATIONS_OFFBAND_AND_SCAN_COMPLETE.md) — operator channels (complementary ops story).
