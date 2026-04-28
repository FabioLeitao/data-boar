# Audit protocol — workbench, ritual, and integrity

**Português (Brasil):** [AUDIT_PROTOCOL.pt_BR.md](AUDIT_PROTOCOL.pt_BR.md)

This document is the **durable register** for operator–agent agreements about **how** we keep the repo trustworthy: a clean **workbench** (only tools that work and are wired), **ritual** changes (process contracts), and **integrity** when someone asks to bypass quality gates.

It complements (does not replace) **[`TOKEN_AWARE_SCRIPTS_HUB.md`](TOKEN_AWARE_SCRIPTS_HUB.md)** (what exists under `scripts/`), **[`CONTRIBUTING.md`](../../CONTRIBUTING.md)** / **[`COMMIT_AND_PR.md`](COMMIT_AND_PR.md)** (PR and merge discipline), and **[`PII_PUBLIC_TREE_OPERATOR_GUIDE.md`](PII_PUBLIC_TREE_OPERATOR_GUIDE.md)** (public-tree safety).

---

## 1. Workbench rule (Adam Savage bench)

**Principle:** A tool that does not work, is not documented, and is not reachable from skills, rules, tests, or operator runbooks **does not stay on the bench**.

| Action | When |
| ------ | ---- |
| **Remove** | No `rg` hits outside the file itself (and no CI/test dependency); duplicate superseded wrapper; broken script with no maintainer path. |
| **Wire** | Script stays: add a row to **`TOKEN_AWARE_SCRIPTS_HUB.md`** (and **`.pt_BR.md`**) or link from an existing runbook / skill / test so the next session finds it. |
| **Quarantine** | Experimental: keep only with an explicit note in this file **§3 Changelog** and a hub row under **Niche / advanced** (or move to `docs/private/` operator-only copy if it must never ship on `origin`). |

**Discovery command (assistants):** from repo root, search for the basename, e.g. `rg -F "script-name.ps1"` and `rg -F "script_name.py"`.

---

## 2. Ritual and contract changes (must be logged here)

Log a row in **§3 Changelog** **before** closing a chat or PR that:

- Adds, removes, or renames a **session keyword** (`.cursor/rules/session-mode-keywords.mdc`).
- Changes **always-on** or high-impact **Cursor rules** (`.cursor/rules/*.mdc`) that define operator–agent contract.
- Changes the **check-all** / **pre-commit** / **CI** gate shape (what runs before merge).
- Introduces a new **“golden path”** script or deprecates one (see **`check-all-gate.mdc`**).

Each changelog row: **date (ISO)**, **change**, **where** (paths), **risk** (none / low / medium), **follow-up** (if any).

---

## 3. Changelog

| Date | Change | Where | Risk | Follow-up |
| ---- | ------ | ----- | ---- | --------- |
| 2026-04-28 | Established this protocol; **workbench cleanup**: removed `scripts/qa_kill_scan.py`, `scripts/export_legal_cartas_advogado_pdf.py`, `scripts/check_name_availability.py` (no in-repo references; one-off / duplicate of private workflows); **documented** `strip_workstation_codename_public_index.py` and `replace_public_workstation_codename_token.py` in **`TOKEN_AWARE_SCRIPTS_HUB.md`**. | This file; `scripts/`; `TOKEN_AWARE_SCRIPTS_HUB*.md` | Low | Prefer **`check-all`** before merge; full gate unchanged. |

---

## 4. NASA doctrine and “integrity warning”

**Doctrine (informal):** Treat flight rules seriously: **do not skip** agreed verification (**`check-all`**, **`pre-commit`**, **`pytest`**, PII guards) on `origin` without an explicit, scoped maintainer decision recorded in a PR or here.

**Integrity warning (assistants):** If the Founder (or any operator) asks for something that **violates** that doctrine—for example **merge without CI**, **commit while guards are red**, **`--no-verify`**, **disable a safety test**, or **bypass PII policy**—the assistant must:

1. **Pause** and output a short **Integrity warning**: what was asked, which rule or gate it breaks, and the **safe default** (run the gate, fix the failure, or narrow the scope).
2. **Not** present a skipped gate as “done” in chat or in tracked docs.
3. **Proceed** with the risky path **only** if the operator replies with an **explicit** exception for that scope (and the assistant still records it in **§3 Changelog** when the exception becomes repo policy or habit).

This section does **not** block **lab-only** or **primary-dev-PC–isolated** flows already documented elsewhere (e.g. **`PRIMARY_WINDOWS_WORKSTATION_PROTECTION.md`**, **`PII_PUBLIC_TREE_OPERATOR_GUIDE.md`**); it blocks **silent** quality bypasses on the **public** integration path.

---

## Related

- **[`TOKEN_AWARE_SCRIPTS_HUB.md`](TOKEN_AWARE_SCRIPTS_HUB.md)** — script inventory and wiring
- **[`.cursor/rules/repo-scripts-wrapper-ritual.mdc`](../../.cursor/rules/repo-scripts-wrapper-ritual.mdc)** — use documented wrappers first
- **[`CURSOR_AGENT_POLICY_HUB.md`](CURSOR_AGENT_POLICY_HUB.md)** — map to rules and skills
