# Scope import quickstart (spreadsheet or memory)

**Português (Brasil):** [SCOPE_IMPORT_QUICKSTART.pt_BR.md](SCOPE_IMPORT_QUICKSTART.pt_BR.md)

Use this when you have **no** GLPI / CMDB export yet — only a workshop list, email thread, or “what we remember.” The machine-readable path is still **CSV → YAML fragment**; see [USAGE.md](../USAGE.md#scope-import-from-csv-config-fragment) for columns and types.

## Non-technical path (Excel / LibreOffice)

1. Open a new spreadsheet.
1. Copy the **header row** from [`deploy/scope_import.example.csv`](../../deploy/scope_import.example.csv) (the line that starts with `type,`).
1. Add **one row per source** (database, folder, or share). Put a short label in `name` if helpful. For `type`, use values the product understands today: e.g. `filesystem`, `postgresql`, `smb`, `nfs`, `mysql` — details in USAGE.
1. **Do not** type passwords in the sheet; use `pass_from_env` with an env var name you will set on the server.
1. **Save As** → **CSV UTF-8** (comma-separated). If the tool offers “CSV (comma delimited)” only, prefer LibreOffice or Excel **UTF-8** export so accents do not break.
1. On the machine with the repo run: `uv run python scripts/scope_import_csv.py path/to/your.csv -o targets.fragment.yaml`
1. **Review** `targets.fragment.yaml`, merge the `targets:` list into your real `config.yaml`, then set environment variables for any `pass_from_env` / `user_from_env` names.

## Privacy

Treat the CSV like **internal infrastructure inventory** (permissions, no public repos). Same discipline as [SECURITY.md](../../SECURITY.md) for config.

## Later: GLPI or other exports

Vendor-specific columns will map to the same canonical schema in a future adapter; the workflow stays **export → CSV-shaped cleanup → `scope_import_csv.py`**.
