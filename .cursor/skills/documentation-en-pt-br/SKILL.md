---
name: documentation-en-pt-br
description: Apply when creating or updating user-facing documentation. Ensures new docs exist in English and Brazilian Portuguese (except plan files), code is source of truth, EN is canonical, index and language switchers are updated. Docs must be navigable (no dead ends) and must always link EN ↔ pt-BR when both exist.
---

# Documentation: EN + pt-BR and source of truth

Use this skill when **creating or editing** user-facing documentation (docs/, README, SECURITY, CONTRIBUTING, deploy, testing, observability, etc.) so that docs stay in sync, both languages are covered, and operators can navigate and learn how to use the app and what it is capable of doing.

## Source of truth (order)

1. **Code and application behaviour** – Config, API, CLI, and capabilities are the deepest source of truth. Docs must describe what the app actually does.
2. **English (EN)** – The canonical written source. Update EN first when behaviour or options change; EN must accurately reflect the code.
3. **Brazilian Portuguese (pt-BR)** – Translation of the EN doc; same structure and coverage. Sync pt-BR after updating EN.

## Navigability (no dead ends)

Documentation must be **navigable to and from** other documents:

- **Avoid dead ends:** Every doc should link out to related docs (usage, deploy, testing, troubleshooting, compliance, etc.) where a topic is mentioned, so readers do not get stuck on a page with no way to discover more.
- **Goal:** Make it easy for **operators** to learn how to use the app, what it is capable of doing, and how to get it working properly. Use the **docs/README.md** index and in-doc cross-links so readers can move between topics and languages.

## EN ↔ pt-BR links (required when both exist)

Whenever a doc has a **pt-BR** version (as it should for all user-facing docs except plan files), **both directions** are required:

- **EN doc:** At the top, add `**Português (Brasil):** [Filename.pt_BR.md](Filename.pt_BR.md)` (or path-relative).
- **pt-BR doc:** At the top, add `**English:** [Filename.md](Filename.md)` (or path-relative).

When you cross-link to **another** doc that has both languages, provide both links (e.g. `[DEPLOY.md](deploy/DEPLOY.md) ([pt-BR](deploy/DEPLOY.pt_BR.md))` from an EN doc, and the inverse from a pt-BR doc). So EN always links to pt-BR and pt-BR always links to EN; no reader should hit a dead end in one language only.

## When adding a new documentation file

**Exception:** Plan files (`docs/PLAN_*.md`, `docs/PLANS_TODO.md`, `docs/completed/`, `.cursor/plans/`) may be English-only.

For all other new docs (guides, reference, deploy, testing, observability, etc.):

1. **Create the English file first** under `docs/` (or root if it is README, SECURITY, etc.). Start with `# Title` (MD041); add language switcher at top: `**Português (Brasil):** [Filename.pt_BR.md](Filename.pt_BR.md)`.
2. **Add the doc to docs/README.md** in the appropriate table (Usage, Deploy, Internal, etc.). Include both EN and pt-BR links in the row once pt-BR exists.
3. **Create the pt-BR file** with the same structure and sections. Top line: `**English:** [Filename.md](Filename.md)`. Keep coverage and structure aligned with EN.
4. **Run markdown fix and lint:** `uv run python scripts/fix_markdown_sonar.py` then `uv run pytest tests/test_markdown_lint.py -v -W error`. Restore semantic list numbering (1. 2. 3.) by hand if the fix script changed step lists. Fix MD024 (unique headings), MD022/MD032/MD041/MD026 as needed (see markdown-lint rule and quality skill).

## When updating existing documentation

1. Change **code or behaviour** first if the doc is reflecting a feature change.
2. Update the **English** doc so it matches the application.
3. **Sync the pt-BR** file: same sections, same meaning; update links and examples as needed.
4. Run the markdown fix script and lint test; fix any new violations.

## Alignment with project

- **Rule:** `.cursor/rules/docs-policy.mdc` – same policy (EN + pt-BR, switcher, index); apply when editing docs.
- **Index:** `docs/README.md` – Documentation policy and tables for all topics and languages.
- **Markdown quality:** `.cursor/rules/markdown-lint.mdc` and `.cursor/skills/quality-sonarqube-codeql/SKILL.md` – MD022, MD026, MD032, MD041, MD024, MD060 so new and updated docs pass the lint test.
