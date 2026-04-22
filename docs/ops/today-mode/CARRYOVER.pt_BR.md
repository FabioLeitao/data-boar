# Carryover do “today mode” (fila viva)

**English:** [CARRYOVER.md](CARRYOVER.md)

**Objetivo:** Uma **lista viva** de itens do operador que atravessam vários `OPERATOR_TODAY_MODE_*` datados. **Fecha, adia com data ou passa para `PLANS_TODO` / issue** — nada imortal sem dono.

**Relacionado:** **`carryover-sweep`** (manhã), **`eod-sync`** (fim do dia), **`docs/private/TODAY_MODE_CARRYOVER_AND_FOUNDER_RHYTHM.md`** (privado).

---

## Fila (edite a tabela abaixo no próprio documento)

| Item | Origem | Estado | Próximo passo / defer |
| ---- | ------ | ------ | ----- |
| **1.7.0 publicado; correção CI `ci.yml` (Sonar); testadores beta (IDENTIDADE_COLABORADOR_A / IDENTIDADE_COLABORADOR_B) testes sintéticos; smoke lab-op** | [OPERATOR_TODAY_MODE_2026-04-17.pt_BR.md](OPERATOR_TODAY_MODE_2026-04-17.pt_BR.md) | ⬜ Pendente | **`gh run list --workflow ci.yml`** verde em `main`; **`git pull`**; briefing curto para testadores; opcional **`lab-op-sync-and-collect.ps1`** / **`docker pull`** `1.7.0` — [PUBLISHED_SYNC.pt_BR.md](PUBLISHED_SYNC.pt_BR.md) |
| **Preparação 1.6.9 + portões Corporate-Entity-C (Dependabot → CodeQL → Sonar? → Scout → check-all)** | [OPERATOR_TODAY_MODE_2026-04-16.pt_BR.md](OPERATOR_TODAY_MODE_2026-04-16.pt_BR.md) | ⬜ Substituído pela frente 1.7.0 | Linha antiga — fechar quando **2026-04-17** estiver ok; **Corporate-Entity-C** segue [Corporate-Entity-C_REVIEW_REQUEST_GUIDELINE.md](../Corporate-Entity-C_REVIEW_REQUEST_GUIDELINE.md) |
| Fechar gate de release **1.6.8** (nota + testes + decisão publish/defer) | 2026-04-02 | ⬜ Pendente | Seguir `OPERATOR_TODAY_MODE_2026-04-02.pt_BR.md` Bloco C; se adiar, registrar data-alvo explícita |
| Rodada externa **WRB + Gemini** com framing "código é verdade" | 2026-04-02 | ⬜ Pendente | Enviar WRB com 3 lentes temporais e gerar bundle Gemini com `--verify`; triar em `PLAN_GEMINI_FEEDBACK_TRIAGE.md` |
| Snapshot quantitativo (hoje / 3 dias / 7 dias) com split por frente | 2026-04-02 | ⬜ Pendente | Rodar `.\scripts\progress-snapshot.ps1 -OutputMarkdown docs/private/progress/progress_snapshot_2026-04-02.md` |
| LinkedIn/ATS do fundador (perfil completo) | 2026-04-02 | ⬜ Pendente | Aplicar seção nova no playbook private (`LINKEDIN_ATS_AND_POSITIONING_PLAYBOOK.pt_BR.md`) com headline + about + evidências |
| Recuperação de dados Time Machine (disco USB) para virar backup externo P0 | 2026-04-02 | ⬜ Pendente | Seguir `docs/ops/TIME_MACHINE_USB_RECOVERY_AND_REPURPOSE.pt_BR.md` (forense read-only -> cópia -> wipe -> novo backup) |
| E-mail **Corporate-Entity-C WRB** | 2026-03-26 / 03-29 / 03-31 | ⬜ Pendente | Bloco: **`docs/ops/WRB_DELTA_SNAPSHOT_2026-03-31.pt_BR.md`** — enviar hoje ou adiar com data em PLANS/privado |
| **Slack** prova de ping (PC + telemóvel) | 2026-03-27 | ✅ Feito | Canal founder-only confirmado; ping recebido no desktop + celular (**CHAN-OK**) |
| PRs **Dependabot** (#134 pypdf, #144 starlette, #147 grupo pip) | 2026-03-29 / 30 / 03-31 | ✅ Feito | Mergeado (verde + mergeable). Próximo: manter olho em novos PRs e seguir `SECURITY.md` |
| **Branch protection** (checks obrigatórios) | 2026-03-26 opcional | ⬜ Opcional | Ativar quando quiser CI/Semgrep obrigatórios em `main` |
| Fatia **Gemini Cold** (ex. G-26-04 + G-26-13) | `PLANS_TODO.md` | ⬜ Opcional | Um PR **`docs`**; itens mais seguros primeiro |
| Espreitar **`/help` vs `main.py`** | 2026-03-29 | ⬜ Quando houver flags | Após próxima flag CLI/dashboard — **`tests/test_operator_help_sync.py`** |

**Feito / arquivado (não reabrir sem trabalho novo):**

- **Tag `v1.6.7` + GitHub Release + Docker Hub** — enviado **2026-03-26** — ver [PUBLISHED_SYNC.pt_BR.md](PUBLISHED_SYNC.pt_BR.md).
- **Help-sync / OpenAPI / README `--host`** do passe 2026-03-27 — ver registro em [OPERATOR_TODAY_MODE_2026-03-27.pt_BR.md](OPERATOR_TODAY_MODE_2026-03-27.pt_BR.md).

---

## PR de organização (esta pasta)

Se tens **commits locais** que criaram **`docs/ops/today-mode/`**, fecha commits por tema (docs/workflow), corre **`.\scripts\lint-only.ps1`** ou **`check-all`**, depois merge em `main`.

---

## LAB-NODE-01 + LMDE (em paralelo)

Instalação de hardware **fora do Git** — usa **[`docs/ops/LMDE7_LAB-NODE-01_DEVELOPER_SETUP.pt_BR.md`](../LMDE7_LAB-NODE-01_DEVELOPER_SETUP.pt_BR.md)** ([EN](../LMDE7_LAB-NODE-01_DEVELOPER_SETUP.md)) quando o portátil estiver pronto para **uv**, **git**, chaves **SSH** e clone do repo.
