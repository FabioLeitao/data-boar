# Dashboard i18n and multi-language web UI

**Status:** Under consideration (no approach decided yet)  
**Synced with:** [docs/PLANS_TODO.md](PLANS_TODO.md) (central plan status)

Goal: allow users to use the web dashboard (and related pages) in **Brazilian Portuguese** and, in the future, other languages — with a clear way to switch language (e.g. footer link, optional flag) and without breaking existing behaviour or tests.

This document sets out **options and recommendations** for you to decide on. **There is no fixed to-do list yet;** once you choose an approach, the concrete steps and to-dos can be added to this plan and to [PLANS_TODO.md](PLANS_TODO.md).

---

## Current state

- **Routes:** HTML pages at `/`, `/config`, `/reports`, `/help`, `/about` ([api/routes.py](../api/routes.py)); API endpoints (`/status`, `/scan`, `/report`, `/reports/{session_id}`, etc.) are locale-agnostic.
- **Templates:** [api/templates/base.html](../api/templates/base.html), dashboard, reports, config, help, about — all copy is hard-coded English.
- **JS:** [api/static/dashboard.js](../api/static/dashboard.js) has a few user-visible strings (e.g. Running, Idle, Starting…, Error).

No i18n/l10n exists in the web UI today.

---

## Options and recommendations (for decision)

### 1. How to represent locale in the UI (routing)

| Option | Description | Pros | Cons |
|--------|-------------|------|------|
| **Path prefix** (e.g. `/en/`, `/pt-br/`) | HTML pages live under `/{locale}/`; API stays at current paths. | Bookmarkable per language; clear URL = language; adding a new language is a new prefix + locale file. | All internal links and redirects must include locale; route registration changes. |
| **Query or cookie** (e.g. `?lang=pt-BR` or cookie) | Same URLs; locale from query param or cookie; templates/JS read it. | Fewer route changes; same URLs for all languages. | Not bookmarkable per language unless you force `?lang=` everywhere; less obvious for “add another language”. |

**Recommendation (to decide):** Path prefix is usually better for clarity and adding languages later; query/cookie is simpler to implement initially but messier for multiple locales.

### 2. How to store and apply translations

| Option | Description | Pros | Cons |
|--------|-------------|------|------|
| **JSON locale files** (e.g. `api/locales/en.json`, `pt_BR.json`) + template helper `t(key)` + inject subset for JS | One JSON per language; templates and JS use the same keys. | No gettext toolchain; easy to add a language (new file + route prefix); keys can be injected into the page for JS. | All strings must be keyed; you maintain the JSON files. |
| **gettext (.po/.mo)** | Standard gettext with extract/compile. | Familiar, scalable for large apps, good tooling. | Requires extract/compile workflow; JS needs a separate approach; more setup. |

**Recommendation (to decide):** JSON + `t(key)` is a good fit for the current size and keeps adding a language to “new JSON + prefix”; gettext is better if you expect many languages and heavy reuse.

### 3. Language switcher and discoverability

- **Placement:** e.g. footer in [base.html](../api/templates/base.html) so every page offers a way to change language.
- **Content:** Link to the same logical page in the other locale (e.g. from `/pt-br/reports` to `/en/reports`), with label (e.g. “English”, “Português (Brasil)”) and optionally a small flag or icon for quick recognition.
- **Default:** Root `/` can redirect to `/en/` or, if you want, to a locale inferred from `Accept-Language` (optional).

### 4. Complexity (rough guide)

- **Path prefix + JSON + footer switcher:** medium (route and template changes, locale loading, link generation).
- **Query/cookie only:** low–medium (no path change; need to pass locale everywhere and optionally remember it).
- **Full gettext:** medium–high (toolchain + template changes + JS strategy).

---

## Possible next steps (only after you decide)

Once you have chosen:

- **Routing:** path prefix vs query/cookie (and, if path, default locale and redirect rule),
- **Translations:** JSON vs gettext (and, if JSON, where files live and how JS gets them),
- **Switcher:** where it goes (e.g. footer), whether to use flags/icons,

then:

1. Add a **concrete to-do list** to this plan (and to [PLANS_TODO.md](PLANS_TODO.md)) for the chosen approach.
2. Implement step by step, with tests and docs updated as in other plans.

Until then, this plan remains **under consideration** with no committed to-dos.
