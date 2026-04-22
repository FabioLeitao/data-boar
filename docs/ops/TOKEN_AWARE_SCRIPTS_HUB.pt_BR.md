# Hub de scripts token-aware (mapa + cobertura)

**English:** [TOKEN_AWARE_SCRIPTS_HUB.md](TOKEN_AWARE_SCRIPTS_HUB.md)

**Objetivo:** Um índice da **automação PowerShell** em **`scripts/`** e como cada área liga a **skills**, **regras**, **palavras-chave de sessão** e **runbooks** — para reutilizar trabalho anterior em vez de redescobrir scripts a cada sessão.

**Não substitui:** **`.cursor/skills/token-aware-automation/SKILL.md`** (comandos do dia a dia) nem **`.cursor/rules/session-mode-keywords.mdc`** (tokens de chat). Este arquivo responde: *“o que mais existe, e onde está documentado?”*

---

## 1. Caminho de ouro (quase toda sessao)

| Script | Função | Ligado a |
| ------ | ---- | -------- |
| `check-all.ps1` | Gate completo | SKILL **`token-aware-automation`**, **`.cursor/rules/check-all-gate.mdc`**, `CONTRIBUTING.md` |
| `lint-only.ps1` | So lint/format | Igual |
| `quick-test.ps1` | Pytest focado | Igual |
| `preview-commit.ps1`, `commit-or-pr.ps1`, `create-pr.ps1` | Commit / PR | Igual + **`docs/ops/COMMIT_AND_PR.md`** |
| `pr-merge-when-green.ps1` | Merge com CI verde | **`.cursor/rules/agent-autonomous-merge-and-lab-ops.mdc`**, SKILL **`autonomous-merge-and-lab`** |
| `safe-workspace-snapshot.ps1` | Snapshot pre-commit | Palavra-chave **`safe-commit`** |
| `smoke-maturity-assessment-poc.ps1` | Subconjunto pytest rapido (gate 1 do POC de maturidade) | [PLAN_MATURITY_SELF_ASSESSMENT_GRC_QUESTIONNAIRE.md](../plans/PLAN_MATURITY_SELF_ASSESSMENT_GRC_QUESTIONNAIRE.md), [SMOKE_MATURITY_ASSESSMENT_POC.md](SMOKE_MATURITY_ASSESSMENT_POC.md) |

---

## 2. PII / árvore pública / estação principal de desenvolvimento

| Script | Função | Ligado a |
| ------ | ---- | -------- |
| `pii-fresh-clone-audit.ps1` | Clone fresco + guards (Windows) | SKILL **`pii-fresh-clone-audit`**, **`docs/ops/PII_FRESH_CLONE_AUDIT.md`**, **`pii-fresh-audit`**, **`PRIMARY_WINDOWS_WORKSTATION_PROTECTION.md`** |
| `new-b2-verify.ps1` | Auditoria de segmento de path de usuario | **`docs/ops/PII_PUBLIC_TREE_OPERATOR_GUIDE.md`** |
| `run-pii-local-seeds-pickaxe.ps1` | Pickaxe sobre seeds locais | **`docs/private.example/scripts/README.md`**, guia PII |
| `run-pii-history-rewrite.ps1` | Reescrita de histórico (perigoso) | Guia PII Parte II — **não** rotina no PC Windows principal de desenvolvimento; **`PRIMARY_WINDOWS_WORKSTATION_PROTECTION.md`** |
| `es-find.ps1` | Busca por nome (**`es.exe`**, opcional **`-FallbackPowerShell`**) | SKILL **`everything-es-search`**, **`docs/ops/EVERYTHING_ES_PRIMARY_WINDOWS_DEV_LAB.md`**, **`es-find`** |
| `social-x-pace-remind.ps1` | Linhas X em atraso vs `SOCIAL_HUB.md` (privado); Slack opcional | **`x-pace-check`**, **`x-posted`**; **`OPERATOR_NOTIFICATION_CHANNELS.md`** §6; privado **`OPERATOR_X_PACE_AND_VALIDATION.pt_BR.md`** |
| `social_x_thread_lengths.py` | Valida blocos em crases sob `## Thread pronta` em `2026*_x_*.md` (máx. 279 por defeito) | Privado **`SOCIAL_HUB.md`**, **`X_PLATFORM_LIMITS_AND_PREMIUM.pt_BR.md`**; `uv run python scripts/social_x_thread_lengths.py` |

---

## 3. Homelab, lab-op, energia, rede

| Script | Função | Ligado a |
| ------ | ---- | -------- |
| `lab-op.ps1` | SSH report / sync-collect | **`docs/ops/LAB_OP_SHORTHANDS.md`**, **`lab-op-systems-context.mdc`** |
| `lab-op-sync-and-collect.ps1` | Batch multi-host | SKILL **`autonomous-merge-and-lab`**, manifest privado |
| `lab-completao-inventory-preflight.ps1` | Verificação de idade dos privados **`LAB_SOFTWARE_INVENTORY.md`** / **`OPERATOR_SYSTEM_MAP.md`**; opcional **`lab-op-sync-and-collect.ps1`** | **`LAB_COMPLETAO_RUNBOOK.pt_BR.md`** (*Frescura do inventário*); o **`lab-completao-orchestrate.ps1`** chama por defeito |
| `lab-completao-orchestrate.ps1` | Completão no lab (preflight + smoke SSH por host + HTTP opcional) | **`LAB_COMPLETAO_RUNBOOK.pt_BR.md`**, manifest com **`completaoHealthUrl`**, opcional **`completaoEngineMode`:** **`container`** / **`completaoSkipEngineImport`** (hosts só Swarm/Podman) |
| `collect-homelab-report-remote.ps1`, `run-homelab-host-report-all.ps1` | Reports remotos | **`HOMELAB_VALIDATION.md`**, manifest privado |
| `lab-allow-data-boar-inbound.ps1`, `lab-allow-data-boar-inbound.sh` | Liberar firewall de lab (TCP 8088) Windows / Linux | **`DATA_BOAR_LAB_SECURITY_TOOLING.pt_BR.md`** |
| `lab-env-load.ps1` | Dot-source env para probes | **`lab-op-systems-context.mdc`** §3 |
| `growatt.ps1`, `enel.ps1`, `energy-report.ps1` | Solar / rede / correlação | SKILL **`homelab-lab-op-data`**, **`solar-snap`**, **`enel-check`**, **`energy-report`**, **`LAB-ROUTER-01-scan`** |
| `growatt-session-collect.ps1`, `enel-session-collect.ps1` | Janela de sessão | SKILL **`session-aware-collect`**, **`session-collect`** |
| `LAB-ROUTER-01.ps1`, `snmp-LAB-ROUTER-01-lab-probe*.ps1`, `LAB-ROUTER-01-api-*.ps1` | UniFi / LAB-ROUTER-01 | SKILL **`homelab-lab-op-data`**, **`LAB-ROUTER-01-scan`** |
| `windows-dev-report.ps1` | Inventário do PC dev | Matriz homelab em **`docs/ops/`** |

---

## 4. Talent / ATS (maioria em `docs/private/commercial/`)

| Script | Função | Ligado a |
| ------ | ---- | -------- |
| `talent.ps1` | CLI do pool | SKILL **`candidate-ats-evaluation`**, **`TALENT_SHORTHAND_HUB.pt_BR.md`** (privado) |
| `candidate-dossier-scaffold.ps1` | Scaffold de dossier | **`talent-dossier`** |
| `ats.ps1`, `ats-candidate-import.ps1`, `ats-hub-export.ps1`, `ats-profile.ps1` | Helpers ATS | Mesma skill; alinhar com **`talent.ps1`** ao escolher entry point |
| `normalize_pool_sync_snapshot.ps1` | Higiene de texto da tabela snapshot | **`talent-pool-sync`** |
| `generate_pool_sync_snapshot.py` | Gera markdown de snapshot | Fluxo do pool (ver hub privado) |
| `generate_talent_playbooks_v2.py` | Playbooks v2 LinkedIn (MD + export pandoc) | Privado **`linkedin_peer_review/individual/v2/`** + **`ats_sli_hub/exports/v2/`** — ver **`docs/private.example/commercial/ats_sli_hub/exports/README.md`** |

*Palavras-chave de sessão:* **`talent-dossier`**, **`talent-ats`**, **`talent-pool-sync`**, **`talent-map`**, **`talent-brief`**, **`talent-status`** — ver **`session-mode-keywords.mdc`**.

---

## 5. Git / higiene / release

| Script | Função | Ligado a |
| ------ | ---- | -------- |
| `git-progress-recap.ps1`, `progress-snapshot.ps1` | Progresso / recap | Ritual do operador; **`eod-sync`** / **`git-pr-sync-before-advice.mdc`** |
| `git-cleanup-merged-gone-branches.ps1` | Limpeza de branches | **`docs/ops/BRANCH_AND_DOCKER_CLEANUP.md`**, modo **`houseclean`** |
| `pr-hygiene-remind.ps1` | Lembrete de PR | **`houseclean`**, PRs abertos |
| `recovery-doc-bundle-sanity.ps1` | Recuperação de bundle de docs | **`check-all-gate.mdc`**, **`DOC_BUNDLE_RECOVERY_PLAYBOOK.md`** |
| `new-adr.ps1` | Scaffold de ADR | **`AGENTS.md`**, **`docs/adr/README.md`** |
| `pre-commit-and-tests.ps1` | Wrapper fino | Preferir **`check-all.ps1`** salvo subset necessario |
| `private-git-sync.ps1` | Repo privado empilhado | **`docs/ops/PRIVATE_LOCAL_VERSIONING.md`**, **`PRIVATE_STACK_SYNC_RITUAL.md`**, sessao **`private-stack-sync`**, **`PRIVATE_OPERATOR_NOTES.md`** |
| `license-smoke.ps1`, `version-readiness-smoke.ps1`, `release-integrity-check.ps1` | Checks de release | **`docs/releases/`**, **`VERSIONING.md`** |
| `generate-sbom.ps1` | SBOM | **`WORKFLOW_DEFERRED_FOLLOWUPS.md`**, docs de seguranca |
| `gitlab-mirror-health-check.ps1` | Saúde do mirror | **`GITLAB_GITHUB_MIRROR.md`** |
| `docker-lab-build.ps1`, `docker-hub-pull.ps1`, `docker-prune-local.ps1`, `docker-scout-critical-gate.ps1` | Docker lab / Hub / Scout | SKILL **`docker-smoke-container-hygiene`**, **`token-aware-automation`** |

---

## 6. Dia do operador / sessao / iCloud

| Script | Função | Ligado a |
| ------ | ---- | -------- |
| `operator-day-ritual.ps1` | Manha / fim do dia | **`carryover-sweep`**, **`eod-sync`** |
| `session-collect.ps1` | Janela de cookies / sessao | SKILL **`session-aware-collect`**, **`session-collect`** |
| `icloud-photos-fetch-range.ps1` | Fetch iCloud por intervalo | Linha **`session-collect`** (iCloud) |

---

## 7. Nicho / avançado (usar quando a tarefa combinar)

| Script | Funcao | Nota |
| ------ | ---- | ---- |
| `external-review-pack.ps1` | Pacote para revisão externa | **`feedback-inbox`**, **`GEMINI_PUBLIC_BUNDLE_REVIEW.md`** |
| `auto-mode-session-pack.ps1` | Pacote de sessao | Experimentos de workflow |
| `lab-node-01-ansible-baseline.ps1` | Baseline Ansible | Provisionamento (detalhes privados) |
| `unifi-ssh-deep-audit.ps1` | SSH profundo UniFi | Alto sinal; LAN — só notas **privadas** |
| `linkedin-review-batch.ps1` | Batch LinkedIn | Talent / social; saídas privadas |
| `gh-ensure-default.ps1` | Branch default no GitHub | Setup pontual |

---

## 8. Economia privada do operador (não é automação de produto)

Scripts como **`household-finance.ps1`**, **`claro.ps1`**, **`aguas.ps1`**, **`leste.ps1`** são fluxos **só do operador**; não precisam de skills Cursor. Uso e saídas em **`docs/private/`** / cofre — não em PRs ou evidência rastreada.

---

## 9. Lacunas de cobertura (próximos passos — sem explodir tokens)

| Lacuna | Sugestao |
| --- | --- |
| **`new-b2-verify.ps1`** fora da tabela do SKILL **`token-aware-automation`** | Uma linha apontando para **`PII_PUBLIC_TREE_OPERATOR_GUIDE.md`** (opcional). |
| **`operator-day-ritual.ps1`** so via palavras-chave | Suficiente; este hub so liga. |
| **Divisao ATS** (`ats*.ps1` vs `talent.ps1`) | Documentar entry point preferido no SKILL **`candidate-ats-evaluation`** na proxima mudanca ATS. |
| **Trio de release** | Mini-tabela opcional em **`docs/releases/`** — nao nova palavra-chave de sessao. |
| **`talent-pool-sync`** e scripts do pool | Texto da keyword alinhado a **`generate_pool_sync_snapshot.py`** + **`normalize_pool_sync_snapshot.ps1`** (**`session-mode-keywords.mdc`**). |

**Política:** **`OPERATOR_WORKFLOW_PACE_AND_FOCUS.md`** §3 — evitar muitos tokens novos; preferir **`backlog` + item nomeado** ou este **hub** para descoberta.

---

## Relacionado

- **`.cursor/skills/token-aware-automation/SKILL.md`**
- **`docs/plans/TOKEN_AWARE_USAGE.md`**
- **`docs/ops/OPERATOR_SESSION_SHORTHANDS.md`**
