# Changelog

Human-readable summary of user-facing changes. **Detailed release notes:** [docs/releases/](docs/releases/) (full checklists, Docker publish commands, GitHub Release text).

## Unreleased (`main`)

- **Agent cold-start (phase 1 — homelab reachability):** **[`OPERATOR_AGENT_COLD_START_LADDER`](docs/ops/OPERATOR_AGENT_COLD_START_LADDER.md)** (+ pt-BR) adds a **7th** non-negotiable (**integrated terminal on the dev PC = same LAN / `ssh` reachability** as the operator shell); **`AGENTS.md`** Quick index and **`CURSOR_AGENT_POLICY_HUB`** homelab rows cross-link ladder §7 with **`homelab-ssh-via-terminal.mdc`**.
- **Cross-platform dev gates:** **`scripts/quick-test.sh`**, **`scripts/lint-only.sh`**, **`scripts/pre-commit-and-tests.sh`** mirror the **`.ps1`** twins; contract **[`docs/ops/SCRIPTS_CROSS_PLATFORM_PAIRING.md`](docs/ops/SCRIPTS_CROSS_PLATFORM_PAIRING.md)** (+ pt-BR) + **`.cursor/rules/repo-scripts-wrapper-ritual.mdc`**; hubs (**`TOKEN_AWARE_SCRIPTS_HUB`**, **`OPERATOR_LAB_DOCUMENT_MAP`**, **`docs/ops/README`**, **`CONTRIBUTING`**, **`check-all-gate.mdc`**, skill **`token-aware-automation`**).
- **Linux / macOS gate:** **`scripts/check-all.sh`** mirrors **`check-all.ps1`** (gatekeeper when **`pwsh`** is on PATH, **plans-stats --write**, **pre-commit** with Ruff retry, **pytest**; **`--skip-pre-commit`**, **`--include-version-smoke`**). Documented in **`CONTRIBUTING`**, **`docs/ops/README`**, **`TOKEN_AWARE_SCRIPTS_HUB`**, **`.cursor/rules/check-all-gate.mdc`**, skill **`token-aware-automation`**.
- **Next working line:** **`1.7.4-beta`** (or next planned pre-release) on **`main`** per [VERSIONING.md](docs/VERSIONING.md) after publish choreography (maintainers: **release-publish-sequencing** rule in-repo). **Published** stable baseline remains **1.7.3** / tag **`v1.7.3`** until the next ship.
- **LAB-OP sudoers / Podman wrapper:** **`lab-node-01_labop_sudoers`** and **`LAB_OP_PRIVILEGED_COLLECTION`** now allowlist **both** **`/bin/bash`** and **`/usr/bin/bash`** (literal **`sudo`** argv match). **`lab-node-01-ansible-labop-podman-apply.sh`** picks an existing bash for **`sudo -n`**, prepends the operator’s **`~/.local/bin`** for **`ansible-playbook`** under **`secure_path`**, and errors clearly if still missing. **`lab-node-01_podman`** role: avoid **`ansible_env`** injection deprecation by reading **`ansible_facts['ansible_env']`**.
- **Void Linux (LAB-NODE-03):** **`lab-node-01_podman`** uses **`xbps-install`** (not **`apt`**) so **`--check`** no longer requires **`python3-apt`**; **`scripts/labop-share-client-install.sh`** installs **`fuse-sshfs`** instead of the non-existent **`sshfs`** package name on Void.
- **Constrained LAB hosts:** optional gitignored marker **`.labop-skip-lab-node-01-podman`** at repo root makes **`lab-node-01-ansible-labop-podman-apply.sh`** pass **`-e lab-node-01_install_podman=false`** (sudoers still only **`--check` / `--apply`**). **`lab-node-01-podman.yml`** no longer hard-forces **`lab-node-01_install_podman: true`** at play level.
- **Lab-OP personas hub:** **[LAB_OP_HOST_PERSONAS.md](docs/ops/LAB_OP_HOST_PERSONAS.md)** (+ pt-BR) links **ENT / PRO / edge / bridge** intent to Ansible, completão manifest fields, and private evidence; **[LAB_COMPLETAO_RUNBOOK.md](docs/ops/LAB_COMPLETAO_RUNBOOK.md)** heterogeneous matrix points here; indexed from **`docs/ops/README.md`**, **`docs/README.md`**, **`OPERATOR_LAB_DOCUMENT_MAP`**, **`ops/automation/ansible/README.md`**, and **`docs/private.example/homelab/README.md`**.
- **Ansible:** **`.gitignore`** now excludes **`ops/automation/ansible/inventory.local.ini`** (operator copy from **`inventory.example.ini`**; no real targets in public Git).
- **Agent cold-start ladder:** **[OPERATOR_AGENT_COLD_START_LADDER.md](docs/ops/OPERATOR_AGENT_COLD_START_LADDER.md)** (+ pt-BR) — one-screen ordered path (hubs + task router + five non-negotiables) for **fresh / token-aware** sessions; wired from **`AGENTS.md`**, **`CURSOR_AGENT_POLICY_HUB`**, **`TOKEN_AWARE_SCRIPTS_HUB`**, **`LAB_COMPLETAO_FRESH_AGENT_BRIEF`**, **`OPERATOR_LAB_DOCUMENT_MAP`**, **`MAP`**, and **`docs/README`**; cross-links from **`LAB_OP_HOST_PERSONAS`** and **`PRIVATE_STACK_SYNC_RITUAL`**. **`scripts/private-git-sync.ps1`:** probe **`Y:`** / **`Z:`** bare repos only when the **drive root** exists (avoids `Join-Path` errors when the letter is not mounted); **`lab-*` push** uses **`$LASTEXITCODE`** without piping **`git push`** so SSH MOTD on stderr does not false-warn.
- **Completão prompt taxonomy:** **[COMPLETAO_OPERATOR_PROMPT_LIBRARY.md](docs/ops/COMPLETAO_OPERATOR_PROMPT_LIBRARY.md)** (+ pt-BR) defines **`completao`** + **`tier:…`** line-2 codes (smoke, smoke-main, smoke-tag, follow-up slices, evidence); **`scripts/completao-chat-starter.ps1`** prints a minimal paste block (**`-Help`** lists tiers); private long-form template **[`docs/private.example/homelab/COMPLETAO_OPERATOR_PROMPT.example.md`](docs/private.example/homelab/COMPLETAO_OPERATOR_PROMPT.example.md)**; wired from **`LAB_COMPLETAO_FRESH_AGENT_BRIEF`**, **`OPERATOR_SESSION_SHORTHANDS`**, **`TOKEN_AWARE_SCRIPTS_HUB`**, **`OPERATOR_LAB_DOCUMENT_MAP`**, **`docs/ops/README`**, **`docs/README`**, **`private.example/homelab/README`**, and **`lab-completao-workflow.mdc`**.
- **Completão 1.7.3 master checklist (archived):** **[COMPLETAO_MESTRE_RELEASE_CHECKLIST_PROMPT.md](docs/ops/COMPLETAO_MESTRE_RELEASE_CHECKLIST_PROMPT.md)** (+ pt-BR) stores the full SRE phases 0–4 prompt verbatim + policy footnotes (sensitive reports path, canonical corpus script); library adds **`tier:release-master-v1-7-3`**; **`completao-chat-starter.ps1`** **`ValidateSet`** includes it; hubs (**`TOKEN_AWARE_SCRIPTS_HUB`**, **`OPERATOR_LAB_DOCUMENT_MAP`**, **`docs/ops/README`**, **`docs/README`**) and **`lab-completao-workflow.mdc`** cross-link.
- **Completão release-master automation:** **`completao-chat-starter.ps1`** adds **`-Tier release-master -ReleaseSemver …`** (optional **`-GitTag`**) printing **`semver:`** / **`tag:`** lines and resolving **`COMPLETAO_MESTRE_RELEASE_CHECKLIST_PROMPT_<semver>.md`** when present, else the canonical **`COMPLETAO_MESTRE_RELEASE_CHECKLIST_PROMPT.md`**; **`COMPLETAO_OPERATOR_PROMPT_LIBRARY`** + **`lab-completao-workflow.mdc`** document the parametric tier.

## 1.7.3 (2026-04-22)

- Maintenance release to establish stable versioning baseline post-sanitization.
- **Stable semver baseline** after **`1.7.2+safe` / `v1.7.2-safe`**: normalised **PEP 440** **`1.7.3`** for PyPI, docs, and Docker **`1.7.3`** + **`latest`**. Checklist: [docs/releases/1.7.3.md](docs/releases/1.7.3.md).

## 1.7.2+safe (2026-04-22) — Security & Sanitization (Golden / Clean Slate)

**Distribution milestone.** Package version **`1.7.2+safe`** is **PEP 440** (local segment `safe`); **Git** and **Docker Hub** use tag **`v1.7.2-safe`** for parity with the validated slim image.

- **Sanitized publish surface:** **Docker Hub** now standardises on **`fabioleitao/data_boar:v1.7.2-safe`** and **`latest`** (single digest); **all prior Hub tags for this repository were removed** — do not pin deprecated tags in runbooks.
- **Git / history narrative:** Positions the repo after **PII-sensitive history remediation**; external consumers should clone from **`v1.7.2-safe`** onward for the clean baseline story.
- **Feature baseline:** Same application line as **1.7.1** plus subsequent `main` development (WebAuthn phases, RBAC **#86** Phase 2, data-soup Tier 1 + stego hints, etc.); see **1.7.1** below for feature notes. Full operator checklist: [docs/releases/1.7.2-safe.md](docs/releases/1.7.2-safe.md).

### Carryover (was `1.7.2-beta` on `main` before this tag)

- **Dashboard auth (Phase 1a — WebAuthn JSON core):** Optional **`api.webauthn`** + **`DATA_BOAR_WEBAUTHN_TOKEN_SECRET`** — [ADR 0033](docs/adr/0033-webauthn-open-relying-party-json-endpoints.md), `tests/test_webauthn_rp.py`, **`scripts/smoke-webauthn-json.ps1`** + [SMOKE_WEBAUTHN_JSON.md](docs/ops/SMOKE_WEBAUTHN_JSON.md). Default **disabled**.
- **Dashboard auth (Phase 1b — HTML session + CSRF minimal):** WebAuthn session + CSRF on gated routes — `tests/test_webauthn_html_gate.py`, `tests/test_html_csrf.py`.
- **Dashboard RBAC (Phase 2 — GitHub [#86](https://github.com/FabioLeitao/data-boar/issues/86)):** Optional **`api.rbac.enabled`** — `tests/test_rbac.py`. **Phase 3** (enterprise SSO/OIDC) remains future work.
- **Filesystem “data soup” Tier 1 + stego hints:** **`SUPPORTED_EXTENSIONS`** + **`file_scan.scan_for_stego`** / CLI **`--scan-stego`**; import fix in **`connectors/filesystem_connector._read_text_sample`** for **`RICH_MEDIA_SCAN_EXTENSIONS`**.

## 1.7.1 (2026-04-21)

- **Scope import (CSV):** `scripts/scope_import_csv.py` + `config/scope_import_csv.py` emit a YAML **`targets`** fragment from a canonical CSV for operator review and merge; see [USAGE.md](docs/USAGE.md#scope-import-from-csv-config-fragment), `deploy/scope_import.example.csv`, [docs/ops/SCOPE_IMPORT_QUICKSTART.md](docs/ops/SCOPE_IMPORT_QUICKSTART.md), [PLAN_SCOPE_IMPORT_FROM_EXPORTS.md](docs/plans/PLAN_SCOPE_IMPORT_FROM_EXPORTS.md).
- **Ops (maturity POC):** [docs/ops/SMOKE_MATURITY_ASSESSMENT_POC.md](docs/ops/SMOKE_MATURITY_ASSESSMENT_POC.md) (+ pt-BR) documents **autonomous** pytest smoke (`scripts/smoke-maturity-assessment-poc.ps1`) and **manual** browser/integrity steps for the **POC ready** checklist; indexed from [docs/ops/README.md](docs/ops/README.md).
- **Dashboard (maturity POC):** `GET /{locale}/assessment` shows a **recent submissions** table (per **batch**, newest first) when the SQLite DB has stored answers; links reuse the post-submit summary URL and CSV export. Documented in [ADR 0032](docs/adr/0032-maturity-assessment-batch-history-sqlite.md). Per-tenant RBAC for this list remains **[#86](https://github.com/FabioLeitao/data-boar/issues/86)** follow-up.
- **Licensing / maturity POC:** API tests assert **`licensing.mode: enforced`** + JWT **`dbtier`** (community vs pro) gates `/{locale}/assessment` (and export) consistent with YAML `effective_tier` override — see `tests/test_api_assessment_poc.py` (`test_assessment_enforced_jwt_dbtier_*`).

## 1.7.0 (2026-04-17)

- **Minor release:** detector **format hints** (REST JSON scalars, **email**/**UUID** `VARCHAR` hints), **HEIC** / Apple images when optional deps are present; reporting/security fixes (heatmap path guard, report import hygiene).
- **Compliance & docs:** **GLOSSARY** and **COMPLIANCE_AND_LEGAL** expanded (US healthcare adjacency, **Corporate-Entity-C/WRB**, **VBA** disambiguation, minors/criminal-record **context** — not legal conclusions); alignment with **ADR 0025** evidence positioning.
- **Repository:** PII guards, CI/deps, Semgrep/Bandit posture; operator **Ansible**/homelab scripts and runbooks (see [docs/releases/1.7.0.md](docs/releases/1.7.0.md) for full checklist).

## 1.6.8 (2026-04-02)

- **Ops automation:** added reusable token-aware wrappers for session bootstrap, progress snapshots, and external review package generation (`scripts/auto-mode-session-pack.ps1`, `scripts/progress-snapshot.ps1`, `scripts/external-review-pack.ps1`).
- **Review reliability:** hardened Gemini bundle verification logic to avoid false mismatches when marker-like text appears inside documentation examples (`scripts/export_public_gemini_bundle.py`).
- **Runbooks and governance:** expanded today/next-day/carryover discipline, reinforced Corporate-Entity-C/Gemini source-of-truth framing, and added Time Machine USB recovery and repurpose playbook for urgent storage/backup recovery.
- **Hardening and lab-op docs:** integrated LMDE/LAB-NODE-01 and Ansible hardening baselines, validation checklists, and CAPEX/OPEX planning outputs aligned to current roadmap.

## 1.6.7 (2026-03-25)

- **Removed** legacy **`run.py`**. Use **`python main.py`** only, with the correct **bind** flags (`--host`, `api.host`, `API_HOST`) and **dashboard transport** (`--https-cert-file` / `--https-key-file`, or `--allow-insecure-http` / `api.allow_insecure_http`). See [docs/releases/1.6.7.md](docs/releases/1.6.7.md) and [docs/USAGE.md](docs/USAGE.md).
- **Docs / tooling:** `docs/USAGE.md` (+ pt-BR), `sonar-project.properties`, `docs/plans/completed/NEXT_STEPS.md` updated accordingly.

## Earlier versions

See [docs/releases/](docs/releases/) (e.g. `1.6.6.md`, `1.6.5.md`, …).
