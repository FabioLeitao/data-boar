# Internal tooling (private use only)

This directory is a **bootstrap** for a **compiled** license-issuance utility. It is **not** part of the supported open-core runtime path.

## Operational rules

1. **Copy** this tree into a **separate private Git repository** (neutral name). Do **not** push signing keys, operator blobs, or production audit databases to any host you do not trust.
1. **Never** ship this tool inside Docker images, `.deb` packages, or customer deliverables.
1. Keep **documentation for issuance ceremonies** in `docs/private/` or an offline runbook—not in the public app repo.

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

## 🛡️ Protocolo de Custódia de Chaves (Estilo Gibson)

O `license-studio` não é um brinquedo; é a prensa que assina a confiança do produto.

- **Isolamento de Ar (Air-gapping):** As chaves Ed25519 devem ser geradas em ambiente offline. Se a chave tocou a internet sem criptografia de hardware, considere-a comprometida.
- **Assinatura de Commit:** Não confunda sua chave de desenvolvedor com a chave de emissão de licenças. São ferramentas de calibres diferentes para propósitos diferentes.
- **Verificabilidade:** Todo binário `studio` deve ter seu hash conferido antes da execução em estações de trabalho autorizadas.

## Legal

Issuance policy and customer contracts are **not** defined in this folder; see legal counsel and `docs/LICENSING_OPEN_CORE_AND_COMMERCIAL.md` in the product repository.
