# Stacked private repo — end-of-session ritual (operator)

**Português (Brasil):** [PRIVATE_STACK_SYNC_RITUAL.pt_BR.md](PRIVATE_STACK_SYNC_RITUAL.pt_BR.md)

**Purpose:** A **calm, repeatable** close for the **nested Git** under **`docs/private/`** (never GitHub `origin`), analogous in spirit to the public-repo **`eod-sync`** ritual but **only** for private history and backups.

**Session keyword (English-only):** **`private-stack-sync`** — see **`.cursor/rules/session-mode-keywords.mdc`**.

---

## What it is not

- **Not** a substitute for **`check-all`**, **`preview-commit`**, or **public** `main` hygiene.
- **Not** a place for **passwords**, **volume passphrases**, **keyfiles**, or **LAN-specific paths** in tracked files — those stay in **gitignored** notes or operator vaults.

---

## Typical flow (high level)

1. When the private tree has meaningful edits, ensure **`docs/private/`** is in a state you are willing to record (same idea as “honest commit” on `main`).
2. From the **product repo root**, run **`scripts/private-git-sync.ps1`** (optional **`-Push`** if your policy pushes the stacked repo to **non-GitHub** remotes).
3. If your workflow uses **encrypted local storage** for that tree, follow the **mount → work → unmount** discipline documented in **`docs/ops/PRIVATE_LOCAL_VERSIONING.md`** and your **private** homelab runbooks (not duplicated here).

### Operator expectation (generic — no drive letters or paths here)

During private-tree work, the operator may rely on a **VeraCrypt-mounted drive** staying available so the nested private tree remains writable and backup/sync routines stay valid. If that mount is **missing when expected**, treat it as a **workflow anomaly** and recover using **private** runbooks and vault-local secrets — **never** paste volume credentials into chat or into **tracked** files.

---

## References

- **`docs/ops/PRIVATE_LOCAL_VERSIONING.md`** — nested Git pattern and safety.
- **`scripts/private-git-sync.ps1`** — feedback inbox mirror + commit + optional push.
- **`docs/PRIVATE_OPERATOR_NOTES.md`** — layout and confidentiality.
- **Skill:** **`.cursor/skills/stacked-private-sync/SKILL.md`**.
