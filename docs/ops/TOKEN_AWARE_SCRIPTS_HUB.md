# Token-aware scripts hub (map + coverage)

**Português (Brasil):** [TOKEN_AWARE_SCRIPTS_HUB.pt_BR.md](TOKEN_AWARE_SCRIPTS_HUB.pt_BR.md)

**Purpose:** One index of **PowerShell automation** under **`scripts/`** and how each area connects to **skills**, **rules**, **session keywords**, and **ops runbooks** — so we reuse prior work instead of re-discovering scripts each session.

**Not a duplicate of:** **`.cursor/skills/token-aware-automation/SKILL.md`** (daily commands) or **`.cursor/rules/session-mode-keywords.mdc`** (chat tokens). This file answers: *“what else exists, and where is it documented?”*

---

## 1. Golden path (every session)

| Script | Role | Wired to |
| ------ | ---- | -------- |
| `check-all.ps1` | Full gate | **`token-aware-automation`** SKILL, **`.cursor/rules/check-all-gate.mdc`**, `CONTRIBUTING.md` |
| `lint-only.ps1` | Docs/style only | Same |
| `quick-test.ps1` | Narrow pytest | Same |
| `preview-commit.ps1`, `commit-or-pr.ps1`, `create-pr.ps1` | Commit / PR | Same + **`docs/ops/COMMIT_AND_PR.md`** |
| `pr-merge-when-green.ps1` | Merge when CI green | **`.cursor/rules/agent-autonomous-merge-and-lab-ops.mdc`**, **`autonomous-merge-and-lab`** SKILL |
| `safe-workspace-snapshot.ps1` | Pre-commit snapshot | Session **`safe-commit`** |
| `smoke-maturity-assessment-poc.ps1` | Fast pytest subset (maturity POC gate 1) | [PLAN_MATURITY_SELF_ASSESSMENT_GRC_QUESTIONNAIRE.md](../plans/PLAN_MATURITY_SELF_ASSESSMENT_GRC_QUESTIONNAIRE.md), [SMOKE_MATURITY_ASSESSMENT_POC.md](SMOKE_MATURITY_ASSESSMENT_POC.md) |

---

## 2. PII / public tree / primary dev workstation

| Script | Role | Wired to |
| ------ | ---- | -------- |
| `pii-fresh-clone-audit.ps1` | Fresh clone + guards (Windows) | **`pii-fresh-clone-audit`** SKILL, **`docs/ops/PII_FRESH_CLONE_AUDIT.md`**, session **`pii-fresh-audit`**, **`PRIMARY_WINDOWS_WORKSTATION_PROTECTION.md`** |
| `new-b2-verify.ps1` | Username path segment audit (`C:\Users\...`) | **`docs/ops/PII_PUBLIC_TREE_OPERATOR_GUIDE.md`** |
| `run-pii-local-seeds-pickaxe.ps1` | Pickaxe over local seeds (Windows) | **`docs/private.example/scripts/README.md`**, PII guide |
| `run-pii-history-rewrite.ps1` | History rewrite (dangerous) | PII guide Part II — **not** for routine primary Windows dev PC; **`PRIMARY_WINDOWS_WORKSTATION_PROTECTION.md`** |
| `es-find.ps1` | Filename search (**`es.exe`**, optional **`-FallbackPowerShell`**) | **`everything-es-search`** SKILL, **`docs/ops/EVERYTHING_ES_PRIMARY_WINDOWS_DEV_LAB.md`**, session **`es-find`** |
| `social-x-pace-remind.ps1` | X editorial due rows vs gitignored `SOCIAL_HUB.md`; optional Slack POST | Session **`x-pace-check`**, **`x-posted`**; **`docs/ops/OPERATOR_NOTIFICATION_CHANNELS.md`** §6; private **`OPERATOR_X_PACE_AND_VALIDATION.pt_BR.md`** |
| `social_x_thread_lengths.py` | Validates fenced blocks under `## Thread pronta` in `2026*_x_*.md` (default max 279) | Private **`SOCIAL_HUB.md`**, **`X_PLATFORM_LIMITS_AND_PREMIUM.pt_BR.md`**; `uv run python scripts/social_x_thread_lengths.py` |

---

## 3. Homelab, lab-op, energy, network

| Script | Role | Wired to |
| ------ | ---- | -------- |
| `lab-op.ps1` | SSH report / sync-collect | **`docs/ops/LAB_OP_SHORTHANDS.md`**, **`lab-op-systems-context.mdc`** |
| `lab-op-sync-and-collect.ps1` | Multi-host batch | **`autonomous-merge-and-lab`** SKILL, private manifest |
| `lab-completao-inventory-preflight.ps1` | Staleness check on private **`LAB_SOFTWARE_INVENTORY.md`** / **`OPERATOR_SYSTEM_MAP.md`**; optional **`lab-op-sync-and-collect.ps1`** | **`LAB_COMPLETAO_RUNBOOK.md`** (*Inventory freshness*); invoked by **`lab-completao-orchestrate.ps1`** by default |
| `lab-completao-orchestrate.ps1` | Lab “completão” (preflight + optional **`lab-op-git-ensure-ref`** when **`completaoTargetRef`** / **`-LabGitRef`** + SSH smoke per host + optional HTTP) | **`LAB_COMPLETAO_RUNBOOK.md`** (*Target git ref*), private manifest **`completaoTargetRef`**, **`completaoHealthUrl`**, optional **`completaoEngineMode`:** **`container`** / **`completaoSkipEngineImport`** (Swarm/Podman-only hosts) |
| `lab-op-git-ensure-ref.ps1` | Check or reset LAB clones to a tag / **`origin/main`** / branch tip | **`LAB_COMPLETAO_RUNBOOK.md`**; invoked by **`lab-completao-orchestrate.ps1`** when a target ref is set |
| `collect-homelab-report-remote.ps1`, `run-homelab-host-report-all.ps1` | Remote reports | **`HOMELAB_VALIDATION.md`**, private manifest |
| `lab-allow-data-boar-inbound.ps1`, `lab-allow-data-boar-inbound.sh` | Lab firewall allow for TCP 8088 (Windows / Linux) | **`DATA_BOAR_LAB_SECURITY_TOOLING.md`** |
| `lab-env-load.ps1` | Dot-source env for probes | **`lab-op-systems-context.mdc`** §3 |
| `growatt.ps1`, `enel.ps1`, `energy-report.ps1` | Solar / grid / correlation | **`homelab-lab-op-data`** SKILL, **`udm-scan`**, **`solar-snap`**, **`enel-check`**, **`energy-report`** keywords |
| `growatt-session-collect.ps1`, `enel-session-collect.ps1` | Session window refresh | **`session-aware-collect`** SKILL, **`session-collect`** keyword |
| `udm.ps1`, `snmp-udm-lab-probe*.ps1`, `udm-api-*.ps1` | UniFi / UDM | **`homelab-lab-op-data`** SKILL, **`udm-scan`** |
| `windows-dev-report.ps1` | Dev PC inventory | **`docs/ops/`** homelab matrix docs |

---

## 4. Talent / ATS (mostly `docs/private/commercial/`)

| Script | Role | Wired to |
| ------ | ---- | -------- |
| `talent.ps1` | Pool CLI (scan, import, review, …) | **`candidate-ats-evaluation`** SKILL, **`TALENT_SHORTHAND_HUB.pt_BR.md`** (private) |
| `candidate-dossier-scaffold.ps1` | Dossier files | Session **`talent-dossier`** |
| `ats.ps1`, `ats-candidate-import.ps1`, `ats-hub-export.ps1`, `ats-profile.ps1` | ATS pipeline helpers | Same skill; align with **`talent.ps1`** when choosing entry point |
| `normalize_pool_sync_snapshot.ps1` | Snapshot table text hygiene | Session **`talent-pool-sync`** |
| `generate_pool_sync_snapshot.py` | Generate pool snapshot markdown | Called from orchestration / pool workflow (see private hub) |
| `generate_talent_playbooks_v2.py` | LinkedIn playbooks v2 MD + pandoc exports | Private **`linkedin_peer_review/individual/v2/`** + **`ats_sli_hub/exports/v2/`** — see **`docs/private.example/commercial/ats_sli_hub/exports/README.md`** |

*Session keywords:* **`talent-dossier`**, **`talent-ats`**, **`talent-pool-sync`**, **`talent-map`**, **`talent-brief`**, **`talent-status`** — see **`session-mode-keywords.mdc`**.

---

## 5. Git / hygiene / release

| Script | Role | Wired to |
| ------ | ---- | -------- |
| `git-progress-recap.ps1`, `progress-snapshot.ps1` | Progress / recap | Operator ritual; pair with **`eod-sync`** / **`git-pr-sync-before-advice.mdc`** |
| `git-cleanup-merged-gone-branches.ps1` | Branch cleanup | **`docs/ops/BRANCH_AND_DOCKER_CLEANUP.md`**, **`houseclean`** mode |
| `pr-hygiene-remind.ps1` | PR reminder | **`houseclean`**, open PR discipline |
| `recovery-doc-bundle-sanity.ps1` | Doc bundle recovery | **`check-all-gate.mdc`**, **`DOC_BUNDLE_RECOVERY_PLAYBOOK.md`** |
| `new-adr.ps1` | ADR scaffold | **`AGENTS.md`** ADR habit, **`docs/adr/README.md`** |
| `pre-commit-and-tests.ps1` | Thin wrapper | Prefer **`check-all.ps1`** unless you need the subset |
| `private-git-sync.ps1` | Nested private repo | **`docs/ops/PRIVATE_LOCAL_VERSIONING.md`**, **`PRIVATE_STACK_SYNC_RITUAL.md`**, session **`private-stack-sync`**, **`PRIVATE_OPERATOR_NOTES.md`** |
| `license-smoke.ps1`, `version-readiness-smoke.ps1`, `release-integrity-check.ps1` | Release checks | **`docs/releases/`**, **`VERSIONING.md`** |
| `generate-sbom.ps1` | SBOM | **`WORKFLOW_DEFERRED_FOLLOWUPS.md`**, security docs |
| `gitlab-mirror-health-check.ps1` | Mirror health | **`GITLAB_GITHUB_MIRROR.md`** |
| `docker-lab-build.ps1`, `docker-hub-pull.ps1`, `docker-prune-local.ps1`, `docker-scout-critical-gate.ps1` | Docker lab / Hub / Scout | **`docker-smoke-container-hygiene`** SKILL, **`token-aware-automation`** SKILL |

---

## 6. Operator day / session / iCloud

| Script | Role | Wired to |
| ------ | ---- | -------- |
| `operator-day-ritual.ps1` | Morning / EOD | Sessions **`carryover-sweep`**, **`eod-sync`** |
| `session-collect.ps1` | Cookie / session window | **`session-aware-collect`** SKILL, **`session-collect`** keyword |
| `icloud-photos-fetch-range.ps1` | iCloud range fetch | **`session-collect`** row (iCloud) |

---

## 7. Niche / advanced (use when the task matches)

| Script | Role | Note |
| ------ | ---- | ---- |
| `external-review-pack.ps1` | Pack for external review | Pair with **`feedback-inbox`**, **`GEMINI_PUBLIC_BUNDLE_REVIEW.md`** |
| `auto-mode-session-pack.ps1` | Session pack | Operator workflow experiments |
| `t14-ansible-baseline.ps1` | Ansible baseline | Lab host provisioning (private details stay private) |
| `unifi-ssh-deep-audit.ps1` | Deep UniFi SSH | High signal; LAN-specific — **private** notes only |
| `linkedin-review-batch.ps1` | LinkedIn batch | Talent / social; keep outputs private |
| `gh-ensure-default.ps1` | GitHub default branch | One-off setup |

---

## 8. Operator-private economics (not “product” automation)

Scripts such as **`household-finance.ps1`**, **`claro.ps1`**, **`aguas.ps1`**, **`leste.ps1`** are for **operator-only** workflows; they do not need Cursor skills. Keep usage and outputs in **`docs/private/`** / vault — not in PRs or tracked evidence.

---

## 9. Coverage gaps (good next steps — without exploding tokens)

| Gap | Suggestion |
| --- | ---------- |
| **`new-b2-verify.ps1`** not in **`token-aware-automation`** table | Add one row pointing to **`PII_PUBLIC_TREE_OPERATOR_GUIDE.md`** (optional; avoids duplicating this hub). |
| **`operator-day-ritual.ps1`** only via keywords | Enough; link from this hub only. |
| **ATS split** (`ats*.ps1` vs `talent.ps1`) | Document preferred entry in **`candidate-ats-evaluation`** SKILL next time ATS changes. |
| **Release trio** (`license-smoke`, `version-readiness-smoke`, `release-integrity-check`) | Optional mini-table in **`docs/releases/`** README — not a new session keyword. |
| **`talent-pool-sync`** keyword historically cited **`talent-pool-sync-snapshot.ps1`** | Repo uses **`scripts/generate_pool_sync_snapshot.py`** + **`scripts/normalize_pool_sync_snapshot.ps1`**; keyword row updated to match (**`session-mode-keywords.mdc`**). |

**Policy:** **`OPERATOR_WORKFLOW_PACE_AND_FOCUS.md`** §3 — avoid adding many new chat tokens; prefer **`backlog` + named item** or this **hub** for discovery.

---

## Related

- **`.cursor/skills/token-aware-automation/SKILL.md`**
- **`docs/plans/TOKEN_AWARE_USAGE.md`**
- **`docs/ops/OPERATOR_SESSION_SHORTHANDS.md`**
