# Operator recovery investigation (SRE-style)

Use when the operator asks to **recover** content, **find** a lost file, **explain** what went wrong, or says **figure it out** / **te vira**. Goal: **blameless RCA** mindset + **exhaust local evidence** before declaring impossibility.

## Principles

1. **Facts first** — cite paths, commits, or command output; avoid guilt narratives.
2. **Try cheap tools first** — skim **`docs/ops/TOKEN_AWARE_SCRIPTS_HUB.md`** + **`.cursor/rules/repo-scripts-wrapper-ritual.mdc`** for an agreed **`scripts/*.ps1`** before a long ad-hoc shell; then list dirs, `grep`, `git log`, PDF text extract.
3. **Stacked private repo** — `docs/private/.git` holds history **off GitHub**; use `git -C docs/private`.
4. **No self-block on private** — read `docs/private/` per `agent-docs-private-read-access.mdc`.

## Checklist (order may vary)

- [ ] **Scope:** What artifact (About text, PDF, draft, config)? Approximate date or event?
- [ ] **Workspace sweep:** `Glob` / `grep` / PowerShell `Get-ChildItem -Recurse -Filter` under `docs/private/` subtrees likely for the domain (`author_info`, `commercial`, `legal_dossier`, `team_info`, `social_drafts`).
- [ ] **Windows filename search:** `scripts/es-find.ps1` or operator `es.exe` when the name is unknown (session keyword `es-find`); other flows may have their own hub-linked wrappers — check the hub row first.
- [ ] **Git (public tree):** `git log --oneline -20 -- path`, `git log -S"unique string" --all`.
- [ ] **Git (private stacked):** `git -C docs/private log --oneline -30`, `git -C docs/private log --name-only -- "*.pdf"` or relevant glob.
- [ ] **Binary profile exports:** LinkedIn PDF in `author_info/` or `legal_dossier/personal_assets/` → `uv run python` + `pypdf` extract to UTF-8 file, then read (do not paste full PII into **public** issues).
- [ ] **Browser MCP:** If live UI is required and MCP is enabled, `browser_navigate` + `browser_tabs list` — session may be warm; if login wall, report that **after** attempt.
- [ ] **Stop condition:** If still missing, report **attempt list** + **one** next step (operator pastes snippet, exports PDF, points to path).

## Anti-patterns

- Stopping at “I have no memory of the chat” **without** disk/git search.
- Claiming LinkedIn is unreachable **without** trying MCP or citing PDF-on-disk alternative.
- Apologizing in place of **running one more command**.

## References

- **`.cursor/rules/repo-scripts-wrapper-ritual.mdc`** — agreed automation before reinvention.
- **`docs/ops/TOKEN_AWARE_SCRIPTS_HUB.md`** — full script map.
- `AGENTS.md` — operator private layout, `es-find`, browser hygiene.
- `docs/ops/PRIVATE_LOCAL_VERSIONING.md` — stacked private repo.
- `docs/private.example/author_info/README.md` — career / LinkedIn export layout.
- `.cursor/rules/operator-investigation-before-blocking.mdc` — rule summary.
