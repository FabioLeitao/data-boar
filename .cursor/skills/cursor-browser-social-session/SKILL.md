# Skill: Cursor browser — SSO social + higiene de separadores

## When to use

- Tasks that open **Patreon, LinkedIn, X, YouTube, Threads**, **Instagram**, **Docker Hub** (repository **General** / **Edit**, overview Markdown, **Tags**), **GitHub.com** web UI when `gh` is not enough, or other third-party UIs in the **Cursor embedded browser** (MCP `cursor-ide-browser`).
- After **research, validation, profile copy-paste review, or post visibility checks** — before ending the assistant turn.
- **SOCIAL_HUB reconciliation:** Operator says a post is already published (e.g. IG1 / Patreon+OSS) — **open the profile or post URL with a warm session**, snapshot, compare to `SOCIAL_HUB.md` row + draft `.md`. **Do not** say the assistant cannot see the feed without trying `browser_navigate` + `browser_snapshot` first (rule: **`.cursor/rules/cursor-browser-social-sso-hygiene.mdc`** § SOCIAL_HUB).

## Workflow

1. **Login**
   - If you see **Google / Apple / SSO** and the operator uses that identity: click through **Continue with Google** (or equivalent) instead of asking for email/password in chat.
   - **Do not** ask “may I authenticate?” / “do you grant browser access?” **before** this attempt — operator policy is **try SSO first** (same for **Docker Hub** as for social).
   - If login wall blocks automation: tell the operator to log in manually once; then re-snapshot.
   - **Never** ask for or repeat passwords in chat; never commit secrets.

2. **Do the task**
   - Follow existing rules (e.g. `x-posted`, `operator-sli-check`, Patreon copy in `docs/private/author_info/`).

3. **Cleanup (default — operator agreement: save RAM, keep warm logins)**
   - If **`browser_lock`** was used: **`unlock`** when all browser actions for this turn are done (per MCP server instructions).
   - Call **`browser_tabs`** with `action: "list"` if unsure how many tabs are open.
   - Close tabs that are **done** for this task: **`browser_tabs`** with `action: "close"` (and `index` if closing a non-current tab). **Goal:** free **RAM** from idle embedded-browser tabs — do **not** skip this at end of task unless the operator asked to keep tabs open.
   - **Do not** end “warm sessions” on the networks: **no** navigating to logout, **no** clearing site data/cookies to “clean up”. Closing a tab is not logging out; the embedded profile keeps login state for the next session.
   - **Exception:** operator explicitly says to keep a site open for their next manual step — skip closing that tab or ask once.

4. **Warm sessions**
   - You cannot promise the next chat will still be logged in. Document outcomes in private notes if needed; operator may leave one tab logged in on purpose.
   - **Operator policy (Data Boar):** The operator **affirms** the assistant **has and will have** access to **social networks** and **operator dashboards that use Google / SSO** (including **Docker Hub**) via **cursor-ide-browser** when the session is **warm**. If **cold**, try **Google / SSO** on the site first; if that fails, ask the operator to log in once or leave a tab warm—**do not** refuse because “there is no API” (no public API ≠ no UI access). Applies to **LinkedIn, FacColleague-Sok, X, Threads, Instagram**, Patreon, **hub.docker.com**, etc. Private: **`docs/private/commercial/ats_sli_hub/LIVE_LINKEDIN_REFRESH_POLICY.pt_BR.md`** (LinkedIn focus).

## References

- Rule: **`.cursor/rules/cursor-browser-social-sso-hygiene.mdc`** (always on).
- MCP: `cursor-ide-browser` — `browser_navigate`, `browser_snapshot`, `browser_tabs` (list / close).
