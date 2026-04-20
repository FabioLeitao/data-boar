# Changelog

Human-readable summary of user-facing changes. **Detailed release notes:** [docs/releases/](docs/releases/) (full checklists, Docker publish commands, GitHub Release text).

## 1.7.1-beta (2026-04-08) — pre-release

- **Not a stable release:** `main` is ahead of **1.7.0**; use **1.7.0** on Docker Hub / GitHub Releases for production parity until **1.7.1** ships.
- **Dashboard (web):** path-prefixed HTML locales (**`en`** / **`pt-BR`**), negotiation (cookie, `Accept-Language`, config), JSON catalogs, localized dashboard JS strings.
- **API / posture:** **`enterprise_surface`** on **`GET /status`** and **`GET /health`** (transport + license trust + global API-key surface; RBAC still not per-route).
- See [docs/releases/1.7.1-beta.md](docs/releases/1.7.1-beta.md).

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
