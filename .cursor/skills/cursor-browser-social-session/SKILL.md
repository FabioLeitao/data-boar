# Skill: Cursor browser — SSO social + higiene de separadores

## When to use

- Tasks that open **Patreon, LinkedIn, X, YouTube, Threads**, or other third-party UIs in the **Cursor embedded browser** (MCP `cursor-ide-browser`).
- After **research, validation, profile copy-paste review, or post visibility checks** — before ending the assistant turn.

## Workflow

1. **Login**
   - If you see **Google / Apple / SSO** and the operator uses that identity: click through **Continue with Google** (or equivalent) instead of asking for email/password in chat.
   - If login wall blocks automation: tell the operator to log in manually once; then re-snapshot.
   - **Never** ask for or repeat passwords in chat; never commit secrets.

2. **Do the task**
   - Follow existing rules (e.g. `x-posted`, `operator-sli-check`, Patreon copy in `docs/private/author_info/`).

3. **Cleanup (default)**
   - Call **`browser_tabs`** with `action: "list"` if unsure how many tabs are open.
   - Close tabs that are **done** for this task: **`browser_tabs`** with `action: "close"` (and `index` if closing a non-current tab).
   - **Exception:** operator explicitly says to keep a site open for their next manual step — skip closing that tab or ask once.

4. **Warm sessions**
   - You cannot promise the next chat will still be logged in. Document outcomes in private notes if needed; operator may leave one tab logged in on purpose.
   - **Operator policy (Data Boar):** The operator **authorizes** LinkedIn/social review via this browser when asked—**do not** refuse because “there is no LinkedIn API” (no public API ≠ no UI access). If login fails, ask the operator to re-warm SSO; private: **`docs/private/commercial/ats_sli_hub/LIVE_LINKEDIN_REFRESH_POLICY.pt_BR.md`**.

## References

- Rule: **`.cursor/rules/cursor-browser-social-sso-hygiene.mdc`** (always on).
- MCP: `cursor-ide-browser` — `browser_navigate`, `browser_snapshot`, `browser_tabs` (list / close).
