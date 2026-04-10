# Private lab scripts (template)

**Portuguese (operator):** after you copy **`docs/private.example/`** into **`docs/private/`**, see **`docs/private/scripts/README.pt_BR.md`** for the full narrative (hostnames, rounds, seeds).

## `clean-slate.sh.example`

- **Purpose:** Destructive reset of a local `data-boar` clone on a **Linux** lab machine, then re-clone and run **`scripts/pii_history_guard.py --full-history`**.
- **Install:** Copy to **`docs/private/scripts/clean-slate.sh`** (private git), customize if needed, then install to **`~/clean-slate.sh`** on each host you control.
- **Tracked copy:** **`clean-slate.sh.example`** (this folder) — no operator-specific literals.
- **Seeds:** Align **`docs/private/security_audit/PII_LOCAL_SEEDS.txt`** with **`docs/private.example/security_audit/PII_LOCAL_SEEDS.example.txt`**; the script can copy seeds to **`~/.config/PII/PII_LOCAL_SEEDS.txt`** when the private path exists inside the clone.
- **Public runbooks** use generic SSH examples (**`lab-op`**); **real** host aliases belong in **`docs/private/homelab/`** only.

## Related

- **`docs/ops/PII_PUBLIC_TREE_OPERATOR_GUIDE.md`** — Sections **H.9** (script) and **H.10** (assistant / self-audit — no chat simulation; fresh clone validates guards).
- **`scripts/pii-fresh-clone-audit.ps1`** + **`docs/ops/PII_FRESH_CLONE_AUDIT.md`** — Windows **non-destructive** temp clone + full-history PII guard (session keyword **`pii-fresh-audit`**); does not replace Linux **`clean-slate.sh`** when you need seeds + private tree refresh.
- **`scripts/run-pii-local-seeds-pickaxe.ps1`** — Windows pickaxe over seeds (separate from this bash flow)
