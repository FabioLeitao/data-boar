# Private notes — template (tracked in Git)

**This folder is versioned** so new clones get a **layout to copy**. Your **real** notes must live under **`docs/private/`**, which is **gitignored** — copy like this:

```bash
# From repo root (Linux/macOS/Git Bash)
mkdir -p docs/private/homelab
cp docs/private.example/homelab/README.md docs/private/homelab/
```

```powershell
# Windows (PowerShell, repo root)
New-Item -ItemType Directory -Force -Path docs/private/homelab | Out-Null
Copy-Item docs/private.example/homelab/README.md docs/private/homelab/
```

Then edit files **only** under `docs/private/` — Git ignores that tree (`git check-ignore -v docs/private/homelab/README.md`).

**Policy:** Read **[PRIVATE_OPERATOR_NOTES.md](../PRIVATE_OPERATOR_NOTES.md)** (tracked).
