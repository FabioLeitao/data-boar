# Plan: Dashboard / reports access control (roles & permissions)

**Status:** Not started (backlog — tracked from GitHub)

**Horizon / urgency:** `[H2]` / `[U2]` — after **Priority band A** and when multi-tenant / multi-user dashboard exposure is real, not before core scan stability.

**GitHub:** [Issue #86](https://github.com/FabioLeitao/data-boar/issues/86) (feature request; migrated narrative from Redmine-reports context).

**Where to read this topic:** This file is the **single planning source** for dashboard **access control**, **RBAC**, and **identity sequencing** (passwordless WebAuthn first, enterprise **SSO/OIDC** later). Related operator runbooks: [SECURE_DASHBOARD_AUTH_AND_HTTPS_HOWTO.md](../ops/SECURE_DASHBOARD_AUTH_AND_HTTPS_HOWTO.md) (API key + TLS today), [PLAN_OPERATOR_API_KEY_FIRST_AUTH_UX.md](PLAN_OPERATOR_API_KEY_FIRST_AUTH_UX.md) (ergonomics spike).

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

## Target direction (phased — identity sequencing)

**Principle:** Ship **standards-based passwordless (FIDO2 / WebAuthn / passkeys)** as the **first in-app identity** path for humans, with **[Bitwarden Passwordless.dev](https://bitwarden.com/products/passwordless/)** as the **minimum** supported integration target (SDK + hosted API) so teams already on Bitwarden can align operationally. **Enterprise SSO** (Azure AD, Google Workspace, Okta, AWS IAM Identity Center–compatible OIDC, etc.) is a **later** phase: many mid-market customers do not have mature IdP rollout yet; passwordless in-product closes that gap.

**Alternative implementation:** The same WebAuthn flows can be implemented with **open-source** libraries (e.g. `py_webauthn` server-side) if a deployment must avoid a vendor dependency; acceptance criteria stay **interoperable passkeys**, not Bitwarden-exclusive.

| Phase | Scope | Outcome |
| ----- | ----- | ------- |
| **0** | Docs + **D-WEB** | Route matrix (what is public vs protected); proxy recipes; **middleware order** diagram with [PLAN_DASHBOARD_I18N.md](PLAN_DASHBOARD_I18N.md) (`API key` → `locale` for HTML → `session` → `RBAC`). |
| **1** | **Session + passwordless (minimum)** | **HTTPS required** for WebAuthn. After successful WebAuthn (via Passwordless.dev or equivalent), issue **opaque server session** (**httpOnly cookie** + CSRF strategy) or short-lived internal JWT **separate** from commercial license JWT. **Global `api.require_api_key`** can remain for automation / break-glass; **browser** flows use session. |
| **2** | **RBAC** | Named roles (`scanner`, `reports_reader`, `config_admin`, …) bound to **authenticated subject**; route/resource gates on prefixed HTML paths; optional machine keys for API with role claims (design TBD). |
| **3** | **Enterprise SSO (optional)** | **OIDC** (SAML later if needed): map IdP groups → product roles; **coexist** with passwordless (e.g. local passkeys for break-glass, SSO for staff). |

**Non-goals for v1 of Phase 1–2:** Password **storage** as primary factor (passkeys first); full **SCIM** provisioning; replacing customer IdP — **SSO is additive in Phase 3**.

---

## Demo / beta vs production-ready (passwordless path)

**Already in product today (baseline):** Optional global API key, TLS/plain-HTTP posture, rate limits, security headers — see [SECURITY.md](../SECURITY.md), [SECURE_DASHBOARD_AUTH_AND_HTTPS_HOWTO.md](../ops/SECURE_DASHBOARD_AUTH_AND_HTTPS_HOWTO.md).

| Gate | Demo / internal beta | Production-ready (passwordless minimum) |
| ---- | -------------------- | ---------------------------------------- |
| **Transport** | HTTPS with trusted cert (or lab-only exception documented) | **HTTPS everywhere** user-facing; HSTS where appropriate; no mixed-content WebAuthn |
| **Identity** | Shared API key or VPN-only dashboard | **WebAuthn** enrollment + login; session invalidation; **account recovery** policy (recovery codes / admin reset — TBD) |
| **Bitwarden / Passwordless.dev** | Dev tenant + test application | **Secrets** (API keys) via env / vault; **tenant** lifecycle documented; monitoring for API availability |
| **RBAC** | Single admin role or feature flags off | Roles enforced in middleware; **403** on forbidden routes; audit log entries for **sign-in** and **sensitive actions** (stretch) |
| **Data** | Single SQLite, single org | Backup/restore story; multi-user rows if needed; **no PII** in logs for WebAuthn assertions (handle per provider docs) |
| **Ops** | Manual deploy | Runbook: rotate sessions, revoke passkeys, disaster recovery; **Docker/K8s** secrets for Passwordless.dev keys |

**Beta exit criteria (suggested):** All **production-ready** rows satisfied in a **staging** environment; penetration-test pass on session + WebAuthn flows; operator docs (EN + pt-BR) updated.

---

## Mapping (earlier draft → current phases)

- **Route classes** (`public` / `authenticated` / `admin`) are implemented **inside** new **Phase 1–2** once **sessions** exist (not as “API key only” for HTML).
- **Old “Phase 3 IdP”** is now **explicitly** enterprise **SSO/OIDC** after passwordless + RBAC are stable.

---

## Dependencies & sequencing

- **Depends on:** Stable report path safety (already hardened); optional alignment with **commercial licensing / JWT** work ([LICENSING_SPEC.md](../LICENSING_SPEC.md)) if roles are carried in tokens.
- **Conflicts with:** None; additive flags, default preserves today’s behaviour until enabled.
- **Token-aware:** Treat as **one plan file + one implementation slice per session**; start with Phase 0–1 only.

### Sequencing with dashboard i18n ([PLAN_DASHBOARD_I18N.md](PLAN_DASHBOARD_I18N.md))

**Shared risk:** Changing HTML routes **twice** (once unprefixed for RBAC, again for `/{locale}/…`) wastes review and tokens.

| Step               | Track                    | Action                                                                                                                                                                                                                                                                   |
| ----               | -----                    | ------                                                                                                                                                                                                                                                                   |
| **D-WEB**          | Both                     | **Design-only:** URL map + **middleware order** (optional API key for automation, **session** for browser after WebAuthn, locale resolution for HTML, route-class / RBAC). Cross-link between this file and the i18n plan.                                                                                                               |
| **Implementation** | i18n first (recommended) | **M-LOCALE-V1:** path-prefixed HTML + `en` / `pt-BR` JSON + negotiation; **no** new RBAC semantics required on first merge if defaults unchanged.                                                                                                                        |
| **Implementation** | #86                      | Phase **0** (docs) can ship anytime. Phase **1+** gates should target the **same prefixed paths** as i18n (e.g. `/{locale}/reports`), not legacy unprefixed HTML — unless a **security exception** forces early guards on old paths (then budget a **migration** slice). |

Details and anti-footgun rules: **PLAN_DASHBOARD_I18N.md** § *Meshing with dashboard reports RBAC*.

---

## Completion checklist (when implementing)

- [ ] USAGE + TECH_GUIDE + SECURITY (EN + pt-BR where paired) updated.
- [ ] Tests for new middleware or route guards (`tests/test_api_key.py` or new module); **WebAuthn** flows covered (happy path + invalid assertion) if Phase 1 ships.
- [ ] Session cookies: **httpOnly**, **Secure**, **SameSite** policy documented; CSRF strategy for mutating routes.
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

- [SPRINTS_AND_MILESTONES.md](SPRINTS_AND_MILESTONES.md) §4.1 (*Identity: edge OIDC vs in-app passwordless*) and §5 (*Composing milestones*) — how **#86** fits the **M-ACCESS** story next to proxy-only patterns.
- [Bitwarden Passwordless.dev](https://bitwarden.com/products/passwordless/) — reference **minimum** integration for FIDO2 / WebAuthn / passkeys (product marketing + docs links from there).
- [PLAN_DASHBOARD_I18N.md](PLAN_DASHBOARD_I18N.md) — locale (orthogonal concern; coordinate route/middleware design).
- [PLAN_NOTIFICATIONS_OFFBAND_AND_SCAN_COMPLETE.md](PLAN_NOTIFICATIONS_OFFBAND_AND_SCAN_COMPLETE.md) — operator channels (complementary ops story).
