# Operator help sync — backlog checklist

**Purpose:** Keep every **surface** where operators learn about flags and options aligned with the real implementation. This doc is a **reminder / audit list**, not the canonical reference (see `docs/USAGE.md`, `docs/data_boar.1`, web `/help`, OpenAPI).

**When to use:** Say **`docs`** + “operator help audit” in a session, or run through this after adding CLI flags, API bodies, or dashboard controls.

**Automation:** Extend **`tests/operator_help_sync_manifest.py`** when adding operator-visible behaviour; run **`uv run pytest tests/test_operator_help_sync.py`**. Cursor rule **`.cursor/rules/operator-help-sync.mdc`** applies when editing listed paths; skill **`.cursor/skills/operator-help-sync/SKILL.md`** summarises the workflow for agents.

## Surfaces to keep in sync

| Surface                | Location / how                            | Notes                                                                                                                              |
| -------                | --------------                            | -----                                                                                                                              |
| **CLI `--help`**       | `main.py` (`argparse`)                    | Source of truth for flags; contract tests in `tests/test_operator_help_sync.py` + manifest `tests/operator_help_sync_manifest.py`. |
| **Man page**           | `docs/data_boar.1`                        | Synopsis + `.SH OPTIONS`; install path varies by distro/package.                                                                   |
| **USAGE (EN + pt-BR)** | `docs/USAGE.md`, `docs/USAGE.pt_BR.md`    | Tables and “REST API server” sections must match bind/port resolution (`core/host_resolution.py`).                                 |
| **README quick start** | `README.md`, `README.pt_BR.md`            | At least link to USAGE for full flags; mention `--host` when discussing exposure.                                                  |
| **Web in-app help**    | Dashboard `/help` templates / static copy | Should not contradict USAGE for scan options and API entrypoints.                                                                  |
| **OpenAPI / Swagger**  | `api/routes` and related                  | Request bodies (e.g. `/scan` JSON) and documented query params.                                                                    |
| **Deploy / security**  | `docs/deploy/DEPLOY*.md`, `SECURITY.md`   | Binding, `API_HOST`, reverse proxy — consistent with loopback-by-default story.                                                    |

## Resolution order (API bind)

Documented in code: **`main.py --host`** → **`api.host`** → **`API_HOST`** → default **`127.0.0.1`**. Any new override (e.g. another env var) must update `core/host_resolution.py`, USAGE, man, and this table if we publish it.

## Done recently (changelog)

- **2026-03:** Wired **`--host`** into CLI (`main.py`) and extended man + USAGE; added regression test for `--help` listing core flags; corrected USAGE binding text (was incorrectly implying default `0.0.0.0` for `main.py --web`).
- **2026-03 (sync pass):** **`docs/data_boar.5`** — `file_scan.scan_compressed` / `use_content_type`, **`api.host`** / `API_HOST` / CLI precedence; man §1 cross-ref line updated. **`api/templates/help.html`** — `uv run`, one-shot vs `--web`, bind order, `--reset-data` warning, config YAML comments; **dashboard** link to Help for CLI parity on scan options.
- **2026-03-25:** Dashboard transport — **`--https-cert-file`**, **`--https-key-file`**, **`--allow-insecure-http`**; `GET /status` + `/health` **`dashboard_transport`**; **`tests/operator_help_sync_manifest.py`** markers; Docker **`CMD`** explicit plaintext for default image.
- **2026-03-25 (API key hardening):** When **`api.require_api_key`** is true but no key is resolved, **`main.py --web`** exits **2**; API returns **503** on protected routes; **`GET /health`** stays public. Docs: **USAGE** (EN/pt-BR), root **SECURITY**, **`docs/SECURITY*`**, **`docs/ops/API_KEY_FROM_ENV_OPERATOR_STEPS.md`**, **`SECURE_BY_DEFAULT_BLOCKERS_AND_MIGRATION*`**. Tests: **`tests/test_api_key.py`**, **`tests/test_host_resolution.py`**.
- **2026-03-25 (technician how-to):** **`docs/ops/SECURE_DASHBOARD_AUTH_AND_HTTPS_HOWTO.md`** + **`.pt_BR.md`** — end-to-end API key + HTTPS (Let’s Encrypt, lab self-signed, Docker); indexed in **`docs/README.md`**, **`docs/ops/README.md`**, linked from root **SECURITY**, **USAGE**, **API_KEY_FROM_ENV**, **SECURE_BY_DEFAULT**.
- **2026-03-30 (carryover / houseclean):** Web **`/help`** vs **`main.py`** — no new CLI flags since the 2026-03-25 dashboard transport pass; **`uv run pytest tests/test_operator_help_sync.py`** green; **`api/templates/help.html`** still documents bind order, TLS/plaintext, and one-shot toggles consistent with **`tests/operator_help_sync_manifest.py`**.

## Next verification pass (objective code ↔ docs)

After realignment work on CLI/API/help surfaces, from the repo root:

```bash
uv run pytest tests/test_operator_help_sync.py -v
```

Then re-walk **Follow-ups** below (OpenAPI vs `POST /scan` bodies, README **`--host`** when discussing exposure, web **`/help`** after new flags). This is the **objective** sync gate agreed post-realignment—run before treating the slice as complete.

## Follow-ups (optional)

- [ ] Pass over **OpenAPI** descriptions vs actual `POST /scan` / `POST /start` bodies (content-type, compressed, etc.).
- [ ] **README** one-liner: mention `--host` when describing LAN/Docker-less runs (partially done in quick start).
- [ ] Re-diff **Web `/help`** after each new CLI flag or dashboard control.
