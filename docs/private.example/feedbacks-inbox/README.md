# Partner / client feedback inbox — blueprint (tracked)

**Português (Brasil):** [README.pt_BR.md](README.pt_BR.md)

**This folder is versioned** as a **policy stub only**. **Do not** put raw Wabbix PDFs, Gemini dumps, or other full review payloads in Git.

## Where drops live (operator machine)

Create **`docs/feedbacks, reviews, comments and criticism/`** at the **repo root** (same level as **`docs/`**). That path is **gitignored** — it is **not** under **`docs/private/`**.

- **Habit:** paste incoming partner or client feedback there (WRB-style drops, Wabbix analyses, exports you do not want on `origin`).
- **Distilled** conclusions and IDs belong in **tracked** plans or ops notes after you redact — never paste full confidential tables into issues or public Markdown.

## Optional mirror (stacked private Git)

If you use a **nested** repository under **`docs/private/`**, you may also keep receipts under **`docs/private/feedbacks_and_reviews/`** and commit there per **`docs/ops/PRIVATE_LOCAL_VERSIONING.md`** — still **never** push those files to the **product** GitHub remote.

## Agents (Cursor)

When the operator uses the **`feedback-inbox`** session keyword, assistants **`read_file`** / list the gitignored drop folder first. If it is **empty**, say so. If **origin** (Wabbix vs Gemini vs other) is unclear, **ask** before attributing rows in **`docs/plans/`** or **`PLANS_TODO.md`**.

## See also

- **[PRIVATE_OPERATOR_NOTES.md](../../PRIVATE_OPERATOR_NOTES.md)** — feedback path vs `docs/private/`.
- **`.cursor/rules/session-mode-keywords.mdc`** — **`feedback-inbox`** row.
