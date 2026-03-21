# Plan (future): public website, marketing depth, and extra doc languages

**Status:** ⬜ **Reminder / backlog** — not scheduled. Revisit when the product is **closer to production-ready** (e.g. after **M-LAB**, stable **M-TRUST**, and a clear GTM slice).

**Purpose:** Capture intent so we do not forget: a **stronger public surface** (site + optional extra languages) aligned with **branding** (Data Boar / dashBOARd, data soup narrative) and **trust** (releases, docs, use cases).

---

## 1. Documentation in additional human languages

- **Today:** User-facing docs are **English (canonical)** + **Brazilian Portuguese (pt-BR)** per [docs-policy](../../.cursor/rules/docs-policy.mdc).
- **Later (evaluate):** Add languages that match **markets or compliance narratives** you care about — e.g. **Spanish (es)** for LatAm, **Japanese (ja)** if there is a concrete channel or partner demand. Each new language implies **ongoing sync** cost with EN; treat as a **deliberate** decision, not a one-off translation burst.
- **Mechanics (when ready):** Mirror the existing EN ↔ pt-BR pattern: language switchers, index rows in `docs/README.md`, and a rule for which files are translated (product docs yes; `docs/plans/` may stay EN-only).

---

## 2. Full descriptive / marketing website (possibly multilingual)

**Goal:** A **dedicated site** (not only GitHub README) for **discovery**, **pitch**, and **credibility** — similar in *role* to how serious projects present themselves (e.g. **FreeBSD**, **Ubuntu**, **Snort**, **pfSense**): clear value prop, downloads/releases, docs entry points, and community or commercial CTA. **Form** (static vs CMS, exact layout) is TBD; **content pillars** should include:

| Pillar | Notes |
| ------ | ----- |
| **Pitch** | Decision-maker narrative; optional **longer** “deep pitch” page. |
| **Use cases** | Sectors, scan/report stories, compliance framing (without overclaiming). |
| **How-tos** | Short guided paths that link into **canonical** `docs/` (USAGE, DEPLOY) so we do not fork truth. |
| **Documentation hub** | Links or embedded paths to **version-synced** docs (same major/minor as releases). |
| **Releases** | Prominent links to **GitHub Releases**, **Docker Hub** tags, and `docs/releases/`. |
| **Branding** | Mascot, dashBOARd sub-brand, visual consistency with [COPYRIGHT_AND_TRADEMARK.md](../COPYRIGHT_AND_TRADEMARK.md) guidance. |

**Hosting:** See [HOSTING_AND_WEBSITE_OPTIONS.md](../HOSTING_AND_WEBSITE_OPTIONS.md) (static site options). Keep **no secrets** on the public site.

**i18n on the site:** If the site is multilingual, define **which locales** ship first and how they stay aligned with EN source copy (same discipline as repo docs).

---

## 3. Dependencies and sequencing (high level)

1. **Stable product story** — version cadence, support posture, and what we promise publicly.
2. **Legal / trademark** — counsel pass on public claims and name use where needed.
3. **Content owner** — who approves site copy and translations.
4. **Automation** — optional CI to publish from a `website/` repo or branch; link checker for docs URLs.

---

## 4. Related tracked material

- [HOSTING_AND_WEBSITE_OPTIONS.md](../HOSTING_AND_WEBSITE_OPTIONS.md) — hosting memo.
- [LICENSING_OPEN_CORE_AND_COMMERCIAL.md](../LICENSING_OPEN_CORE_AND_COMMERCIAL.md) — pitch and open-core boundary.
- [PLANS_TODO.md](PLANS_TODO.md) — backlog pointer to this file.
- [README.md](../../README.md) — current public entry point until a site exists.

---

## 5. When to activate

Promote this from “reminder” to a **sprint-sized** initiative when:

- Homelab / second-environment confidence is in a good state (**–1L** / **M-LAB**), and
- Priority band **A** hygiene is not blocking, and
- You have bandwidth for **ongoing** translation + site maintenance.

Until then, **no obligation** to implement; this file is the **memory hook**.
