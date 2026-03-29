# Dashboard i18n and multi-language web UI

**Status:** **Target architecture agreed** — implementation **deferred** until higher-priority product slices ship; milestones and sequencing below are **planning only** until scheduled.

**Synced with:** [PLANS_TODO.md](PLANS_TODO.md), [SPRINTS_AND_MILESTONES.md](SPRINTS_AND_MILESTONES.md), [PLAN_DASHBOARD_REPORTS_ACCESS_CONTROL.md](PLAN_DASHBOARD_REPORTS_ACCESS_CONTROL.md) (**#86**). **Future public website** (marketing + doc hub) should **reuse the same locale model** (path prefix, cookie, `Accept-Language`, JSON catalogs) — see [PLAN_WEBSITE_AND_DOCS_I18N_FUTURE.md](PLAN_WEBSITE_AND_DOCS_I18N_FUTURE.md) §2.2.

## When implementing: update docs and tests; then update PLANS_TODO.md, sprints, and this file.

**Goal:** Dashboard HTML (`/`, `/config`, `/reports`, `/help`, `/about`, …) in **`en`** + **`pt-BR`** first, optional **`es`** / **`fr`**, and a **fifth “market” locale** when demand appears — with **cookie → `Accept-Language` → configured fallback**, **path-prefixed** URLs, **JSON** message catalogs (**no gettext in v1**), and **unchanged** JSON API semantics (`/status`, `/scan`, …).

---

## Target architecture (anti-footgun notes)

| Decision             | Choice                                                                                                                                                                                                                                     | Why / later migration                                                                                                                                                                                                 |
| --------             | ------                                                                                                                                                                                                                                     | ---------------------                                                                                                                                                                                                 |
| **HTML URLs**        | **Path prefix** — e.g. `/en/`, `/pt-br/`, `/es/`, `/fr/` (slugs configurable; map to BCP 47 in config).                                                                                                                                    | Bookmarkable; adding a language = new JSON + slug + switcher entry. **RBAC (#86)** should target **the same** path pattern from day one of implementation — see meshing § below.                                      |
| **API**              | **No locale prefix**; stable JSON keys and values as today.                                                                                                                                                                                | Keeps **clients, scripts, and tests** simple. Optional later: localized **human** `detail` strings — not v1.                                                                                                          |
| **Strings**          | **`api/locales/{tag}.json`** (or agreed path) + **`t(key)`** in Jinja; inject a **subset** into pages for `dashboard.js`.                                                                                                                  | **Abstraction:** implement `t()` as “load JSON dict” now; a later swap to gettext can **keep the same helper signature** if keys stay stable. Avoid baking English sentences as *only* msgids until you need gettext. |
| **Default locale**   | **(1)** Valid **preference cookie** → **(2)** **`Accept-Language`** vs `supported_locales` → **(3)** **`default_locale`** in config (fallback often `en`).                                                                                 | User does **not** re-pick language every visit.                                                                                                                                                                       |
| **Catalog size**     | **Long-term cap ~5** shipped UI locales (`en`, `pt-BR`, + optional `es`, `fr`, + one **token** slot). **gettext** reconsider only if **many** locales or **heavy** translator workflow — typically **not** for months/years at this scale. | JSON + **CI key-parity** checks across locale files stays token- and maintainer-friendly.                                                                                                                             |
| **Plurals / gender** | Prefer **label + number** patterns in copy to limit grammar pain; if rich phrases appear later, consider **ICU MessageFormat in JSON** or migrate string layer — **without** changing URL or API design.                                   | Avoids locking out Japanese etc. when you add them.                                                                                                                                                                   |

### Scripts, data encodings, and demand-driven locales (customer reminder)

- **Scanned content** is handled as **Unicode** end-to-end (e.g. **Cyrillic**, **CJK / Japanese**, **Arabic script**, RTL where viewers support it). **Legacy byte encodings** for configs and pattern files are a separate concern—see [COMPLIANCE_FRAMEWORKS.md](../COMPLIANCE_FRAMEWORKS.md#multi-language-multi-encoding-and-multi-regional-operation) and [USAGE.md](../USAGE.md#file-encoding-config-and-pattern-files). **Sniffing and heuristics** for specific corpora can be **tuned** (config, patterns, connectors); **consulting** is available when IT, security, compliance, or DPO teams need a **custom profile**.
- **Dashboard HTML and full doc translations** in additional locales (e.g. **es**, **fr**, **ja**, **ru**, **ar**) are **short- to mid-term** roadmap items **after** **M-LOCALE-V1** (`en` + `pt-BR` first), bundled with other product priorities—not a promise of simultaneous ship for every script. **Sponsorship or strong demand** can reprioritise a locale.
- **Illustrative backlog** (not shipped; order TBD): **East / Southeast Asia** — **Mandarin** / **Cantonese** (and other **Chinese** written forms), **Korean**, **Indonesian**, **Thai**, **Vietnamese**, **Filipino**; **South Asia** — **Hindi**, **Bengali**, **Tamil**, other **Indic** scripts as needed; **Africa / Middle East** — **Amharic** / **Ethiopic**, **Swahili**, further **Arabic** variants; **Europe** — **Catalan**, **Basque**, **Galician**, other **co-official** languages. **YAML compliance samples** for matching jurisdictions track the same **demand-led** cadence as UI strings—public **README** summarizes direction without internal filenames.
- **Expanding shipped locales** beyond the **~5-slot** long-term cap (the **“token”** market slot in the table above) stays **deliberately demand-driven** so JSON catalog maintenance and **CI key parity** stay tractable.
- **Public input:** GitHub **issues / discussions** are welcome to flag **locale, charset, or compliance-sample gaps**. **Commercial consulting** can accelerate tailored UI copy, YAML samples, or integration work where the open defaults are insufficient.

---

## Meshing with dashboard reports RBAC (issue #86)

**Different concerns:** i18n = **which language**; #86 = **who may access** which routes.

**Same code paths:** `api/routes.py`, templates, middleware stack.

### Planning rule

Before **either** implementation PR changes route shape:

1. Produce a **short URL + middleware order diagram** (can live in this section or in **#86** plan — keep cross-links). Include: unprefixed API; prefixed HTML; where **API key** runs; where **locale** is resolved; where **route class / RBAC** runs (exact order TBD in design pass — typically: normalize path → optional API key → locale for HTML → RBAC for resource class).

1. **Recommended implementation order (when work actually starts):**
   - **Slice A — Locale skeleton:** introduce `/{locale}/…` for HTML with **`en`** + **`pt-BR`** JSON and negotiation; **no** RBAC behaviour change yet (defaults unchanged).
   - **Slice B — #86 Phase 0–1:** docs + optional middleware on **that same** path layout (avoid gating `/reports` on legacy paths then re-gating on prefixed paths in a second refactor).
   - **Slice C — #86 Phase 2+** and **optional `es`/`fr`/token locale** as separate PRs.

**Higher rework cost (avoid unless security forces it):** ship #86 only on **legacy** unprefixed paths, then add locale prefix later — implies **second** pass on every guard and link.

---

## Milestones (planning — not calendar dates)

| ID                | Name                             | Type          | Done when                                                                                                                                                          |
| --                | ----                             | ----          | ---------                                                                                                                                                          |
| **D-WEB**         | **Dashboard web surface design** | Doc / diagram | URL map + middleware order agreed; cross-linked from **#86** plan; no feature code required.                                                                       |
| **M-LOCALE-V1**   | **Locale v1 on `main`**          | Code          | Path-prefixed HTML; `en` + `pt-BR` JSON; cookie + `Accept-Language` + config fallback; switcher; tests; USAGE/TECH_GUIDE touch; CI key parity for shipped locales. |
| **M-LOCALE-PLUS** | **Optional locales**             | Code          | `es` and/or `fr` and/or fifth market locale — same mechanics; still no gettext unless reprioritised.                                                               |

**Sprint placement:** **D-WEB** can run in a **buffer** sprint or **ahead of** the first implementation slice; **M-LOCALE-V1** is **Tier 4 / H2** alongside **#86** — see [PLANS_TODO.md](PLANS_TODO.md) and [SPRINTS_AND_MILESTONES.md](SPRINTS_AND_MILESTONES.md) §4.2. **Do not** schedule **M-LOCALE-V1** until explicit priority after current Tier-2 / integration work unless the operator promotes it.

---

## Implementation checklist (execute only when scheduled)

1. **Config:** `supported_locales`, `default_locale`, cookie name/TTL; document in USAGE + pt-BR (+ TECH_GUIDE if needed).
1. **Middleware:** Negotiation for unprefixed `/` → `/{best}/…`; register HTML under prefix; **leave API routes unprefixed**.
1. **Locales:** JSON files per locale; `t(key)` + missing-key fallback (e.g. English).
1. **Templates:** Replace hard-coded copy; footer **switcher** + **Set-Cookie** on choice.
1. **JS:** `dashboard.js` strings from server-injected map; align keys with JSON.
1. **Tests:** Redirect order; one template or key-resolution test; update operator-help sync manifest if `/help` paths change.
1. **CI:** Script or test: **key sets match** across all **shipped** locale JSON files.
1. **#86:** Apply RBAC / route classes to **prefixed** HTML paths per joint diagram.

---

## Current state (baseline)

- **Routes:** HTML at `/`, `/config`, `/reports`, `/help`, `/about` ([api/routes.py](../api/routes.py)); API endpoints locale-agnostic.
- **Templates:** English hard-coded in Jinja.
- **JS:** [api/static/dashboard.js](../api/static/dashboard.js) — a few visible strings.

---

## Options reference (historical)

Earlier comparisons of path vs query/cookie and JSON vs gettext remain valid for **edge cases**; **target stack** is fixed in § Target architecture above unless the operator explicitly revisits this file.

---

## See also

- [PLAN_DASHBOARD_REPORTS_ACCESS_CONTROL.md](PLAN_DASHBOARD_REPORTS_ACCESS_CONTROL.md) — **#86**; **coordinate** D-WEB and route order.
- [PLAN_WEBSITE_AND_DOCS_I18N_FUTURE.md](PLAN_WEBSITE_AND_DOCS_I18N_FUTURE.md) — public marketing site (separate from in-app dashboard).
