# Licensing specification (runtime)

Technical specification for **optional** commercial enforcement. Default is **open** mode (no token required).

## Modes

| Mode | Config / env | Behaviour |
| ---- | ------------ | ---------- |
| `open` | `licensing.mode: open` or unset; `DATA_BOAR_LICENSE_MODE=open` | Full functionality; license token optional; status shows **OPEN** |
| `enforced` | `licensing.mode: enforced` or `DATA_BOAR_LICENSE_MODE=enforced` | Valid signed token required for ingest/digest; invalid/expired/revoked/tampered states block scans |

Environment variables override YAML when set:

- `DATA_BOAR_LICENSE_MODE` — `open` | `enforced`
- `DATA_BOAR_LICENSE_PATH` — path to JWT file (`.lic`)
- `DATA_BOAR_LICENSE_PUBLIC_KEY_PATH` — PEM file with **Ed25519 public** key (verify only)
- `DATA_BOAR_LICENSE_PUBLIC_KEY_PEM` — inline PEM (alternative to path; dev/CI only)
- `DATA_BOAR_LICENSE_REVOCATION_PATH` — JSON file listing revoked license IDs
- `DATA_BOAR_RELEASE_MANIFEST_PATH` — optional JSON manifest for integrity (see [RELEASE_INTEGRITY.md](RELEASE_INTEGRITY.md))
- `DATA_BOAR_EXPECTED_BUILD_DIGEST` — optional hex SHA-256; if set, compared to embedded build digest

## YAML (`config.yaml`)

```yaml
licensing:
  mode: open                    # open | enforced
  public_key_path: ""           # Ed25519 public PEM
  license_path: ""              # signed JWT file
  revocation_list_path: ""      # optional JSON revoke list
  manifest_path: ""             # optional release manifest
  machine_bind_strict: false    # if true, token mfp must match host fingerprint
```

## License JWT payload (claims)

Signed with **Ed25519** (JWS `EdDSA`). Standard claims:

| Claim | Meaning |
| ----- | ------- |
| `sub` | License ID (unique) |
| `iat` | Issued-at (unix) |
| `exp` | Expiration (unix) |

Custom claims (namespaced to avoid collisions):

| Claim | Type | Meaning |
| ----- | ---- | ------- |
| `dbcid` | string | Customer ID |
| `dbcname` | string | Customer display name |
| `dbenv` | string | Target environment: `production`, `qa`, `uat`, `homologation`, `debug`, `trial` |
| `dbmfp` | string | Expected machine fingerprint (hex SHA-256); empty = any host |
| `dbtrial` | bool | Trial / POC: cap report rows and watermark |
| `dbmaxrows` | int | Max data rows in report when trial (e.g. 15) |
| `dbissuer` | string | Issuer operator id (e.g. SSH key fingerprint or email) |
| `dbkid` | string | Signing key id for rotation |
| `dbgrace` | int | Grace period end (unix); after `exp`, still **GRACE** until this time |

## Lifecycle states

| State | Meaning |
| ----- | ------- |
| `OPEN` | Enforcement off; community / dev build |
| `VALID` | Token signature OK, not expired (or in grace), not revoked, machine OK |
| `GRACE` | Past `exp` but before `dbgrace` |
| `EXPIRED` | Past grace |
| `REVOKED` | License ID on revocation list |
| `UNLICENSED` | Enforced but no token or unreadable token |
| `INVALID` | Bad signature or malformed JWT |
| `MACHINE_MISMATCH` | `dbmfp` set and does not match host |
| `TAMPERED` | Release integrity / manifest check failed |
| `CRACKED` | Reserved for future anti-tamper signals (e.g. bytecode check failures) |

## Machine fingerprint

Computed as **SHA-256** hex over a stable string built from:

- Hostname (short)
- Optional: `DATA_BOAR_MACHINE_SEED` (set in deployment for Docker/VM stability)

Docker: set `DATA_BOAR_MACHINE_SEED` to a deployment-specific secret so containers on the same image share one licensed fingerprint.

## Revocation file format

JSON:

```json
{
  "revoked_license_ids": ["license-uuid-1", "license-uuid-2"]
}
```

## Trial / POC behaviour

When `dbtrial` is true:

- Scan may run (if otherwise valid) but **report generation** caps findings to `dbmaxrows` and appends synthetic “teaser” rows (watermarked).
- Logs and Report info sheet state **TRIAL**.

## Blocking rule

When mode is **enforced** and state is not `VALID` or `GRACE` (and not `OPEN`):

- **CLI**: `start_audit` raises `LicenseBlockedError`; message printed to stderr.
- **API**: `POST /scan`, `POST /start`, `POST /scan_database` return **403** with `detail.license_state`.

Health and About still respond so operators can see **why** the system is restricted.

## Future extensions (planning reminder — partner tiers / consulting SKUs)

When you **change or harden licensing** for IP and profitability, you may introduce **separate commercial programs** (e.g. **direct end-customer** vs **partner / pro / enterprise**—exact names and contracts TBD with counsel). One goal: allow **partners** to use a **partner-level** entitlement to serve **their customers’** engagements without collapsing into the same SKU as a single-tenant end user.

**Not implemented today.** Possible directions (to be validated legally and product-wise):

| Idea | Notes |
| ---- | ----- |
| **Custom JWT claims** | e.g. `dbprogram` or `dbtier` (`direct` \| `partner` \| `enterprise`, …) and optional `dbmax_customers` / `dbconsulting_allowed`—names illustrative only. |
| **Enforcement** | `LicenseGuard` and report metadata would read claims and block or watermark **unauthorised** consulting or multi-customer use. |
| **Issuance** | Private issuer (`tools/license-studio` or successor) issues different token **templates** per SKU; audit log records program/tier. |

Keep this section in sync with [LICENSING_OPEN_CORE_AND_COMMERCIAL.md](LICENSING_OPEN_CORE_AND_COMMERCIAL.md) (“Future product tiers”). **Do not add claims to production tokens until contracts and pricing are defined.**
