# Plan: Security hardening and vulnerability closure

**Status:** Not started
**Synced with:** [docs/PLANS_TODO.md](PLANS_TODO.md) (central to-do list)

*When implementing steps: update docs and tests; then update PLANS_TODO.md and this file.*

This plan recommends steps to close security gaps, reduce abuse and data-extraction risk, keep dependencies secure, and follow best practices—**without causing regressions or breaking the app**. Each step should be tested and validated before marking done.

---

## Goals

- **Vulnerabilities and gaps:** Address any remaining or newly identified vulnerabilities (input validation, output encoding, secrets, logging).
- **Abuse and data extraction:** Ensure the app cannot be abused (rate limits, auth, request bounds) and that sensitive data cannot be extracted by unauthorized callers.
- **Dependencies:** Use secure, up-to-date library versions; integrate audits into CI and release process.
- **Best practices:** Align with OWASP-style guidance, secure defaults, and deploy hardening already documented in SECURITY.md and docs/deploy.

All steps are **additive or configurable** where possible; avoid breaking existing deployments or tests.

---

## Current state (summary)

- **Already in place:** SQL injection resistance (identifier escaping, ORM), path traversal protection (session_id validation), credential encoding in URLs, `yaml.safe_load` for config, optional API key, rate limiting (concurrent + interval), security headers (CSP, X-Frame-Options, HSTS when HTTPS), config endpoint protected when API key required. See [SECURITY.md](../SECURITY.md) and [docs/security.md](security.md).
- **Gaps to consider:** Input validation/sanitization for tenant and technician (length, characters) when stored and later shown in reports/UI; request body size limits; ensuring no secrets in logs; dependency audit cadence and lockfile; optional stricter CSP; optional scan payload limits.

---

## 1. Input validation and output safety (prevent abuse and data extraction)

| #   | To-do                                                                                                                                                                                                                                                                                            | Status     | Notes                                                                                                                                                                                   |
| --- | -------------------------------------------------------------------------------------------------------------------------------------                                                                                                                                                            | ---------- | -----                                                                                                                                                                                   |
| 1.1 | **Tenant / technician validation:** Add optional max length (e.g. 256 chars) and allowlist of characters (printable, no control chars) for `tenant` and `technician` in ScanStartBody, SessionTenantUpdate, SessionTechnicianUpdate, and config-driven scan. Store trimmed/sanitized value only. | ⬜ Pending  | Prevents oversized or control-char payloads; reduces risk if values are ever rendered in HTML/Excel. Add tests; keep backward compatible (e.g. strip only, or configurable max length). |
| 1.2 | **Request body size limit:** Ensure FastAPI/ASGI request body size is bounded (e.g. 1 MB for JSON config save and scan start body) to prevent DoS via huge payloads. Document in SECURITY.md.                                                                                                    | ⬜ Pending  | FastAPI/Uvicorn may have defaults; confirm and document or set explicitly.                                                                                                              |
| 1.3 | **Logging:** Audit code paths that log request data, config, or errors; ensure API key, passwords, and connection strings are never logged. Add a regression test or checklist.                                                                                                                  | ⬜ Pending  | Align with SECURITY.md (“do not log the key”).                                                                                                                                          |

---

## 2. Dependencies (secure and up-to-date libraries)

| #   | To-do                                                                                                                                                                      | Status     | Notes                                                                                           |
| --- | -------------------------------------------------------------------------------------------------------------------------------------                                      | ---------- | -----                                                                                           |
| 2.1 | **pip-audit in CI:** Confirm `uv run pip-audit` runs on every push/PR (already in `.github/workflows/ci.yml`). Fix any new findings before release.                        | ⬜ Pending  | Verify audit job runs and document that PRs must resolve audit failures.                        |
| 2.2 | **Dependabot:** Keep weekly pip and github-actions updates enabled; when merging, update `pyproject.toml` first, then `uv pip compile pyproject.toml -o requirements.txt`. | ⬜ Pending  | Already configured; add a short “Release checklist” item: run audit and resolve before tagging. |
| 2.3 | **Minimum versions:** Prefer `>=` in pyproject.toml for security patches; pin `==` only where necessary for reproducibility. Document in SECURITY.md or CONTRIBUTING.      | ⬜ Pending  | Already the case; document as policy so new deps follow.                                        |
| 2.4 | **Optional: lockfile audit:** If introducing a lockfile (e.g. `uv.lock`), run `pip-audit` against the locked environment in CI so upgrades are audited before merge.       | ⬜ Pending  | Only if project adopts lockfile; otherwise current approach (sync + audit) is sufficient.       |

---

## 3. Application and API hardening (abuse and extraction prevention)

| #   | To-do                                                                                                                                                                                                                                                                                       | Status     | Notes                                                                                                                |
| --- | -------------------------------------------------------------------------------------------------------------------------------------                                                                                                                                                       | ---------- | -----                                                                                                                |
| 3.1 | **Rate limiting:** Already implemented (concurrent scans, min interval). Document recommended production values and that rate_limit is the first line of defense against scan abuse.                                                                                                        | ⬜ Pending  | USAGE and SECURITY already mention it; add one sentence that disabling or relaxing rate limits increases abuse risk. |
| 3.2 | **API key:** When `require_api_key` is true, /config and other sensitive endpoints are protected. Recommend in docs that production deployments set `require_api_key: true` and use a strong key from env.                                                                                  | ⬜ Pending  | SECURITY.md already states this; ensure USAGE and deploy docs repeat the recommendation.                             |
| 3.3 | **Report/heatmap access:** Confirm that report and heatmap download endpoints only return data for validated `session_id` and that no enumeration or info leakage occurs (e.g. 404 vs 403). Current design (validate session_id, then generate or 404) is acceptable; document as intended. | ⬜ Pending  | No code change required if current behavior is correct; add one bullet to docs/security.md.                          |
| 3.4 | **Optional scan payload limits:** If the API or config ever accepts very large target lists or patterns, consider documenting or enforcing a reasonable limit (e.g. max targets per scan) to avoid resource exhaustion.                                                                     | ⬜ Pending  | Only if such limits are missing; assess current config/API and add only if needed.                                   |

---

## 4. TLS, headers, and client security

| #   | To-do                                                                                                                                                                        | Status     | Notes                                                                                          |
| --- | -------------------------------------------------------------------------------------------------------------------------------------                                        | ---------- | -----                                                                                          |
| 4.1 | **SSL/TLS (S4423):** Any use of `ssl.create_default_context()` must set `minimum_version = ssl.TLSVersion.TLSv1_2`. Enforced by test in `tests/test_sonarqube_python.py`.    | ✅ Done     | Already fixed in `scripts/check_name_availability.py`; test prevents regression.               |
| 4.2 | **Security headers:** CSP, X-Frame-Options, HSTS (when HTTPS), Referrer-Policy, Permissions-Policy are set in `api/routes.py`. No change unless a new header is recommended. | ⬜ N/A      | Document in this plan that current set is sufficient; optional stricter CSP is in deploy docs. |
| 4.3 | **HTTPS in production:** Document that TLS should be terminated at reverse proxy; app respects X-Forwarded-Proto for HSTS. Already in SECURITY.md.                           | ⬜ N/A      | No code change.                                                                                |

---

## 5. Deployment and operations

| #   | To-do                                                                                                                                                                                                                           | Status     | Notes                                                                                                           |
| --- | -------------------------------------------------------------------------------------------------------------------------------------                                                                                           | ---------- | -----                                                                                                           |
| 5.1 | **Deploy hardening:** DEPLOY.md already includes optional securityContext, NetworkPolicy, PDB. Ensure SECURITY.md and USAGE reference “Security and hardening” in deploy docs.                                                  | ⬜ Pending  | Cross-check links; add one line in SECURITY.md if missing.                                                      |
| 5.2 | **Secrets:** Config and env may contain DB passwords and API keys. Document that config file permissions and env handling must restrict access to trusted users; never commit secrets.                                          | ⬜ Pending  | SECURITY.md and docs already mention this; reinforce in “Release checklist” or OPERATIONS if such a doc exists. |
| 5.3 | **WAF / reverse proxy:** State explicitly that for internet-facing deployments, a reverse proxy with TLS and (optionally) WAF is recommended; app-level API key and rate limiting complement but do not replace proxy security. | ⬜ Pending  | Already in SECURITY.md; confirm and leave as is.                                                                |

---

## 6. Testing and regression

| #   | To-do                                                                                                                                                                                                                   | Status     | Notes                                                                                            |
| --- | -------------------------------------------------------------------------------------------------------------------------------------                                                                                   | ---------- | -----                                                                                            |
| 6.1 | **Security tests:** `tests/test_security.py` covers SQL injection, path traversal, credential encoding, safe_load, config endpoint. Keep these green; add tests for any new validation (e.g. tenant/technician length). | ⬜ Pending  | For 1.1, add test that oversized or invalid tenant/technician is rejected or truncated per spec. |
| 6.2 | **S4423 regression:** `test_ssl_create_default_context_uses_minimum_tls_version` in test_sonarqube_python.py ensures no new use of default context without minimum TLS.                                                 | ✅ Done     | Already in place.                                                                                |
| 6.3 | **No regressions:** Before marking any step done, run `uv run pytest -v -W error` and relevant security tests.                                                                                                          | ⬜ Pending  | Apply to every step in this plan.                                                                |

---

## 7. Documentation and checklist

| #   | To-do                                                                                                                                                                                 | Status     | Notes                                                                           |
| --- | -------------------------------------------------------------------------------------------------------------------------------------                                                 | ---------- | -----                                                                           |
| 7.1 | **Release checklist:** Add a “Security” section: run `pip-audit`, fix any high/critical findings, ensure SECURITY.md and docs/security.md are up to date, confirm no secrets in logs. | ⬜ Pending  | Can live in CONTRIBUTING.md, docs/TESTING.md, or a short RELEASE.md.            |
| 7.2 | **docs/security.md:** After implementing 1.1–1.3, add one line each for tenant/technician validation, body size, and logging policy so technicians know what is enforced.             | ⬜ Pending  | Keeps technician guidance in sync.                                              |
| 7.3 | **SECURITY.md:** Ensure “Resistance to common vulnerabilities” and “Keeping dependencies up to date” reflect current state and reference this plan where appropriate.                 | ⬜ Pending  | Optional: add “See also docs/PLAN_SECURITY_HARDENING.md for planned hardening.” |

---

## Order of execution (recommended)

1. **Low-risk, high-value:** 2.1, 2.2, 2.3 (audit and dependency policy); 5.1, 5.2, 5.3 (docs only).
1. **Input and request safety:** 1.1 (tenant/technician validation + test 6.1), then 1.2 (body size), then 1.3 (logging audit).
1. **Documentation:** 3.1, 3.2, 3.3, 3.4; then 7.1, 7.2, 7.3.

---

## Out of scope (by design)

- **Authentication beyond API key:** Full OAuth2/OIDC or per-user auth is out of scope; proxy or IdP remains the recommended place for that.
- **Code signing / SBOM:** Not in this plan; can be a separate improvement.
- **Penetration testing:** Recommended for production deployments but not part of this implementation plan.

---

*Last updated: plan created. Update this doc when completing steps or when new security recommendations are adopted.*
