# Troubleshooting: Credentials and authentication

**Português (Brasil):** [TROUBLESHOOTING_CREDENTIALS_AND_AUTH.pt_BR.md](TROUBLESHOOTING_CREDENTIALS_AND_AUTH.pt_BR.md)

**See also:** [TROUBLESHOOTING.md](TROUBLESHOOTING.md) (overview and quick hints).

This document helps you fix **auth_failed** / **authentication_failed** and avoid **conflicting credentials** (e.g. API key in both header and request body). It covers database credentials, REST/API (Basic, Bearer, API key, OAuth2), and Data Boar’s own API key when enabled.

---

## 1. What the report shows

- **Reason:** `auth_failed` or `authentication_failed`.
- **Details:** Often the raw message from the server (e.g. "401 Unauthorized", "invalid_client", "login failed").
- **Suggested next step:** "Verify username/password, tokens or OAuth client credentials, and check for account lockouts or IP restrictions."

If that is not enough, use the sections below.

---

## 2. Conflicting credentials (header vs body)

**Scenario:** You configure an API key (or Bearer token) in **two places**: e.g. in the target’s `headers` and also in the request body or in another auth block. Some servers reject requests when the same credential appears twice or when header and body disagree.

### 2.1 What to look for

- 401/403 even though the credential is correct when tested with curl.
- Config has both `headers: { "X-API-Key": "..." }` and a body or auth section that sends the same key.
- Config has `bearer` (or similar) and also a custom header with the same token.

### 2.2 What to avoid

- **Do not** send the same API key in both a header and in the request body unless the API explicitly allows it.
- **Do not** set both Basic auth and Bearer for the same target unless the API expects both (rare).
- For Data Boar’s **own** API (when `api.require_api_key: true`): send the key **only** in `X-API-Key` or `Authorization: Bearer <key>`, not in both with different values.

### 2.3 Steps to fix

1. Choose **one** auth method per target: either `headers` with the key, or the target’s `auth` / `bearer` / `api_key` option (see [USAGE.md](USAGE.md)).
1. Remove the duplicate from the other place and re-run.
1. If the API requires a key in a specific header (e.g. `X-API-Key`), use only that in config; do not add the same value to the body.

---

## 3. Database (SQL, NoSQL) auth failed

**Scenario:** Target type `database`; reason `auth_failed`.

### 3.1 Checklist

- **User/password:** Correct in config (`user`, `pass` or `password`). No extra spaces; special characters in password may need to be URL-encoded in connection strings (see [SECURITY.md](../SECURITY.md) and connector docs).
- **Account locked or expired:** DB admin may have locked the account or expired the password. Use a dedicated read-only account for the scanner.
- **Host-based access:** Some DBs allow only certain hosts. Ensure the audit host/container IP (or range) is allowed.
- **SSL/TLS:** If the server requires SSL, the driver and connection string must enable it (e.g. `sslmode=require` for PostgreSQL). Wrong SSL mode can yield "auth failed" or connection errors.

### 3.2 Steps to fix

- Verify credentials with a client (e.g. `psql`, `mysql`) from the same host/container that runs Data Boar.
- Unlock the account or create a new read-only user for the scanner.
- Add the audit host/container to the DB server’s allowed hosts; fix SSL in config if required.

---

## 4. REST/API (Basic, Bearer, API key, OAuth2)

**Scenario:** Target type `api` or REST; reason `auth_failed`.

### 4.1 Basic / Bearer / API key

- **Basic:** `user` and `pass` in config; sent as `Authorization: Basic base64(user:pass)`. Ensure no confusion with a separate API key header.
- **Bearer:** Token in `bearer` or `token`; sent as `Authorization: Bearer <token>`. Token must be valid and not expired.
- **API key in header:** Often `X-API-Key` or `Authorization: ApiKey <key>`. Set **only** in the target’s `headers` (or the connector’s documented key field), not also in body.
- **Conflict:** If the API expects the key in the body, use only the body parameter; remove it from headers (or vice versa). See section 2 above.

### 4.2 OAuth2 (e.g. Power BI, Dataverse)

- **Client credentials:** `tenant_id`, `client_id`, `client_secret` (or equivalent in config). The app requests a token from the IdP and sends it as Bearer. Wrong tenant/client/secret yields "invalid_client" or 401.
- **What to check:** Tenant ID (GUID), client ID (GUID), secret value and expiry; app registration has the right permissions (e.g. read for Power BI/Dataverse). No conflicting extra headers with another token.
- **Steps to fix:** Verify in Azure (or your IdP) that the app registration is correct and the secret has not expired; fix config and re-run. Do not send the same token in both the OAuth flow and a custom header.

---

## 5. Data Boar API key (when enabled)

When `api.require_api_key: true`, clients must send the key in **one** of:

- `X-API-Key: <key>`
- `Authorization: Bearer <key>`

**Do not** send both with different values. `GET /health` remains public and does not require the key.

---

## 6. Account lockouts and IP restrictions

- **Lockout:** Too many failed logins can lock the account. Wait for unlock or ask the admin to unlock; then fix the credential in config so the next run succeeds.
- **IP restrictions:** The IdP or API may allow only certain IPs. Ensure the audit host/container IP is allowed (or use a VPN/allowlisted exit).

---

**Documentation index:** [README.md](README.md) · [README.pt_BR.md](README.pt_BR.md). **Overview:** [TROUBLESHOOTING.md](TROUBLESHOOTING.md).
