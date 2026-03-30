# Carryover do “today mode” (fila viva)

**English:** [CARRYOVER.md](CARRYOVER.md)

**Objetivo:** Uma **lista viva** de itens do operador que atravessam vários `OPERATOR_TODAY_MODE_*` datados. **Fecha, adia com data ou passa para `PLANS_TODO` / issue** — nada imortal sem dono.

**Relacionado:** **`carryover-sweep`** (manhã), **`eod-sync`** (fim do dia), **`docs/private/TODAY_MODE_CARRYOVER_AND_FOUNDER_RHYTHM.md`** (privado).

---

## Fila (edite a tabela abaixo no próprio documento)

| Item | Origem | Estado | Próximo passo / defer |
| ---- | ------ | ------ | ----- |
| E-mail **Wabbix WRB** | 2026-03-26 / 03-29 | ⬜ Pendente | Bloco: **`docs/ops/WRB_DELTA_SNAPSHOT_2026-03-26.pt_BR.md`** — enviar ou data em PLANS/privado |
| **Slack** prova de ping (PC + telemóvel) | 2026-03-27 | ⬜ Pendente | **`docs/ops/OPERATOR_NOTIFICATION_CHANNELS.pt_BR.md`** — alerta real ou nota **CHAN-OK** |
| PRs **Dependabot** (#134 pypdf, #143 grupo pip, #144 starlette) | 2026-03-29 / 30 | ⬜ Pendente | Sessão **`deps`**; **`gh pr checks`** + merge verde conforme **`SECURITY.md`** |
| **Branch protection** (checks obrigatórios) | 2026-03-26 opcional | ⬜ Opcional | Ativar quando quiseres CI/Semgrep obrigatórios em `main` |
| Fatia **Gemini Cold** (ex. G-26-04 + G-26-13) | `PLANS_TODO.md` | ⬜ Opcional | Um PR **`docs`**; itens mais seguros primeiro |
| Espreitar **`/help` vs `main.py`** | 2026-03-29 | ⬜ Quando houver flags | Após próxima flag CLI/dashboard — **`tests/test_operator_help_sync.py`** |

**Feito / arquivado (não reabrir sem trabalho novo):**

- **Tag `v1.6.7` + GitHub Release + Docker Hub** — enviado **2026-03-26** — ver [PUBLISHED_SYNC.pt_BR.md](PUBLISHED_SYNC.pt_BR.md).
- **Help-sync / OpenAPI / README `--host`** do passe 2026-03-27 — ver registro em [OPERATOR_TODAY_MODE_2026-03-27.pt_BR.md](OPERATOR_TODAY_MODE_2026-03-27.pt_BR.md).

---

## PR de organização (esta pasta)

Se tens **commits locais** que criaram **`docs/ops/today-mode/`**, fecha commits por tema (docs/workflow), corre **`.\scripts\lint-only.ps1`** ou **`check-all`**, depois merge em `main`.

---

## T14 + LMDE (em paralelo)

Instalação de hardware **fora do Git** — usa **[`docs/ops/LMDE7_T14_DEVELOPER_SETUP.pt_BR.md`](../LMDE7_T14_DEVELOPER_SETUP.pt_BR.md)** ([EN](../LMDE7_T14_DEVELOPER_SETUP.md)) quando o portátil estiver pronto para **uv**, **git**, chaves **SSH** e clone do repo.
