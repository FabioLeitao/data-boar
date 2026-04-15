# Social drafts — template (tracked)

**Purpose:** Point operators to a **private** hub for social post status and drafts.

**Brand + mascot:** [BRAND_AND_MASCOT.md](BRAND_AND_MASCOT.md) — Data Boar name, 🐗, *data soup* vocabulary.

**Real content:** lives only under **`docs/private/`** in your local tree (gitignored from GitHub `origin`). Create the layout you need there; use this folder as a **tracked** model.

**Tracked stub:** [SOCIAL_HUB.example.md](SOCIAL_HUB.example.md) — empty table + column meanings; no real URLs.

**Policy:** Do not commit real engagement metrics, client names, or unpublished strategy to the public repo. Copy [SOCIAL_HUB.example.md](SOCIAL_HUB.example.md) into your private tree when you start from scratch.

**Posting windows (home office / clock times):** tracked stub only — [OPERATOR_SOCIAL_POSTING_WINDOWS.example.md](OPERATOR_SOCIAL_POSTING_WINDOWS.example.md). Real policy lives in gitignored **`docs/private/social_drafts/OPERATOR_SOCIAL_POSTING_WINDOWS.pt_BR.md`**.

**Social character limits (all networks):** private **`docs/private/social_drafts/SOCIAL_NETWORK_LIMITS_AND_POLICIES.pt_BR.md`** — inventory from Gravatar + Instagram/Threads/LinkedIn/X/TikTok/etc.

**X (Twitter) only:** private **`docs/private/social_drafts/X_PLATFORM_LIMITS_AND_PREMIUM.pt_BR.md`** (free 280 vs Premium “longer posts”); local check: **`scripts/social_x_thread_lengths.py`** (gitignored `*_x_*.md` drafts).

**pt-BR locale (CI):** tracked mirror **[2026-04-09_instagram_databoar_patreon_apoio_oss.example.md](2026-04-09_instagram_databoar_patreon_apoio_oss.example.md)** — Portuguese body must stay aligned with the private draft **`docs/private/social_drafts/2026-04-09_instagram_databoar_patreon_apoio_oss.md`**; `tests/test_docs_pt_br_locale.py` scans the `.example.md` path on every CI run.
