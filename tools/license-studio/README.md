# Internal tooling (private use only)

This directory is a **bootstrap** for a **compiled** license-issuance utility. It is **not** part of the supported open-core runtime path.

## Operational rules

1. **Copy** this tree into a **separate private Git repository** (neutral name). Do **not** push signing keys, operator blobs, or production audit databases to any host you do not trust.
2. **Never** ship this tool inside Docker images, `.deb` packages, or customer deliverables.
3. Keep **documentation for issuance ceremonies** in `docs/private/` or an offline runbook—not in the public app repo.

## Build (Go)

```bash
cd tools/license-studio
go build -o studio ./cmd/studio
```

## Commands (v0)

- `studio sign -key ed25519-private.pem -claims claims.json` — print a signed JWT (stdout). Pipe to `license.lic` on the licensed host.

## Audit database (SQLite)

Create locally with the SQL schema (no secrets in repo):

```bash
sqlite3 path/to/audit.sqlite < schema/audit.sql
```

Insert rows from your operational procedures (shell script, DBA tool, or a future internal binary).

`claims.json` must include at least `sub`, `exp`, `iat` (unix seconds). Optional: `dbcid`, `dbcname`, `dbenv`, `dbmfp`, `dbtrial`, `dbmaxrows`, `dbissuer`, `dbkid`, `dbgrace` (see `docs/LICENSING_SPEC.md` in the main app repo).

## Security

- Generate **Ed25519** keys offline; store private key in Bitwarden / HSM / hardware token as policy dictates.
- Use a **different** key than your **Git commit-signing** key.
- Restrict `studio` binary execution to authorized workstations (MDM, filesystem ACLs).

## Legal

Issuance policy and customer contracts are **not** defined in this folder; see legal counsel and `docs/LICENSING_OPEN_CORE_AND_COMMERCIAL.md` in the product repository.
