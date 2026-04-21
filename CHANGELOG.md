# Changelog

Human-readable summary of user-facing changes. **Detailed release notes:** [docs/releases/](docs/releases/) (full checklists, Docker publish commands, GitHub Release text).

## Unreleased (`main`)

- **Development:** Pre-release **`1.7.2-beta`** on `main`. Release planning: **one** primary slice per patch (**POC ready** for maturity assessment **or** scope-import vendor work **or** another small governance item)—see [PLANS_TODO.md](docs/plans/PLANS_TODO.md). **Plans:** scope import **Phase D** marked complete in [PLAN_SCOPE_IMPORT_FROM_EXPORTS.md](docs/plans/PLAN_SCOPE_IMPORT_FROM_EXPORTS.md) (operator docs + quickstart + privacy alignment). **Maturity POC:** [PLAN_MATURITY_SELF_ASSESSMENT_GRC_QUESTIONNAIRE.md](docs/plans/PLAN_MATURITY_SELF_ASSESSMENT_GRC_QUESTIONNAIRE.md) + [SMOKE_MATURITY_ASSESSMENT_POC.md](docs/ops/SMOKE_MATURITY_ASSESSMENT_POC.md) now spell out **autonomous (CI/smoke) vs operator (browser §D)** closure; [LICENSING_SPEC.md](docs/LICENSING_SPEC.md) links **`dbtier`** to POC regression tests.
- **Dashboard auth (Phase 1a — WebAuthn JSON core):** Optional **`api.webauthn`** + **`DATA_BOAR_WEBAUTHN_TOKEN_SECRET`** enable **vendor-neutral** passkey JSON endpoints under **`/auth/webauthn/`** (PyPI **`webauthn`**), SQLite table **`webauthn_credentials`**, signed session cookie — [ADR 0033](docs/adr/0033-webauthn-open-relying-party-json-endpoints.md). Expanded pytest coverage (`tests/test_webauthn_rp.py`); operator subset **`scripts/smoke-webauthn-json.ps1`** + [SMOKE_WEBAUTHN_JSON.md](docs/ops/SMOKE_WEBAUTHN_JSON.md). **Not** HTML login enforcement yet (**[#86](https://github.com/FabioLeitao/data-boar/issues/86)** Phase 1b+); default **disabled**.

## 1.7.1 (2026-04-21)

- **Scope import (CSV):** `scripts/scope_import_csv.py` + `config/scope_import_csv.py` emit a YAML **`targets`** fragment from a canonical CSV for operator review and merge; see [USAGE.md](docs/USAGE.md#scope-import-from-csv-config-fragment), `deploy/scope_import.example.csv`, [docs/ops/SCOPE_IMPORT_QUICKSTART.md](docs/ops/SCOPE_IMPORT_QUICKSTART.md), [PLAN_SCOPE_IMPORT_FROM_EXPORTS.md](docs/plans/PLAN_SCOPE_IMPORT_FROM_EXPORTS.md).
- **Ops (maturity POC):** [docs/ops/SMOKE_MATURITY_ASSESSMENT_POC.md](docs/ops/SMOKE_MATURITY_ASSESSMENT_POC.md) (+ pt-BR) documents **autonomous** pytest smoke (`scripts/smoke-maturity-assessment-poc.ps1`) and **manual** browser/integrity steps for the **POC ready** checklist; indexed from [docs/ops/README.md](docs/ops/README.md).
- **Dashboard (maturity POC):** `GET /{locale}/assessment` shows a **recent submissions** table (per **batch**, newest first) when the SQLite DB has stored answers; links reuse the post-submit summary URL and CSV export. Documented in [ADR 0032](docs/adr/0032-maturity-assessment-batch-history-sqlite.md). Per-tenant RBAC for this list remains **[#86](https://github.com/FabioLeitao/data-boar/issues/86)** follow-up.
- **Licensing / maturity POC:** API tests assert **`licensing.mode: enforced`** + JWT **`dbtier`** (community vs pro) gates `/{locale}/assessment` (and export) consistent with YAML `effective_tier` override — see `tests/test_api_assessment_poc.py` (`test_assessment_enforced_jwt_dbtier_*`).

## 1.7.0 (2026-04-17)

- **Minor release:** detector **format hints** (REST JSON scalars, **email**/**UUID** `VARCHAR` hints), **HEIC** / Apple images when optional deps are present; reporting/security fixes (heatmap path guard, report import hygiene).
- **Compliance & docs:** **GLOSSARY** and **COMPLIANCE_AND_LEGAL** expanded (US healthcare adjacency, **Wabbix/WRB**, **VBA** disambiguation, minors/criminal-record **context** — not legal conclusions); alignment with **ADR 0025** evidence positioning.
- **Repository:** PII guards, CI/deps, Semgrep/Bandit posture; operator **Ansible**/homelab scripts and runbooks (see [docs/releases/1.7.0.md](docs/releases/1.7.0.md) for full checklist).

## 1.6.8 (2026-04-02)

- **Ops automation:** added reusable token-aware wrappers for session bootstrap, progress snapshots, and external review package generation (`scripts/auto-mode-session-pack.ps1`, `scripts/progress-snapshot.ps1`, `scripts/external-review-pack.ps1`).
- **Review reliability:** hardened Gemini bundle verification logic to avoid false mismatches when marker-like text appears inside documentation examples (`scripts/export_public_gemini_bundle.py`).
- **Runbooks and governance:** expanded today/next-day/carryover discipline, reinforced Wabbix/Gemini source-of-truth framing, and added Time Machine USB recovery and repurpose playbook for urgent storage/backup recovery.
- **Hardening and lab-op docs:** integrated LMDE/T14 and Ansible hardening baselines, validation checklists, and CAPEX/OPEX planning outputs aligned to current roadmap.

## 1.6.7 (2026-03-25)

- **Removed** legacy **`run.py`**. Use **`python main.py`** only, with the correct **bind** flags (`--host`, `api.host`, `API_HOST`) and **dashboard transport** (`--https-cert-file` / `--https-key-file`, or `--allow-insecure-http` / `api.allow_insecure_http`). See [docs/releases/1.6.7.md](docs/releases/1.6.7.md) and [docs/USAGE.md](docs/USAGE.md).
- **Docs / tooling:** `docs/USAGE.md` (+ pt-BR), `sonar-project.properties`, `docs/plans/completed/NEXT_STEPS.md` updated accordingly.

## Earlier versions

See [docs/releases/](docs/releases/) (e.g. `1.6.6.md`, `1.6.5.md`, …).
