# Modo “hoje” do operador — 2026-03-26 (manhã)

**English:** [OPERATOR_TODAY_MODE_2026-03-26.md](OPERATOR_TODAY_MODE_2026-03-26.md)

**Objetivo:** Foco num ecrã para **o dia a seguir** à sessão longa de **2026-03-25**: fechar a árvore aberta, **CI verde**, **história de versão correta**, e-mail **Wabbix**.

---

## Progresso já feito (2026-03-25 — resumo antes de dormir)

| Área                | Resultado                                                                                                                                                                    |
| ----                | ---------                                                                                                                                                                    |
| **CI / pre-commit** | Job de lint executa **`uv run pre-commit run --all-files`**; **`.pre-commit-config.yaml`** com **`plans-stats-check`**; **CONTRIBUTING** recomenda **`pre-commit install`**. |
| **Docs / ADR**      | **0000–0003** em `docs/adr/`; **WORKFLOW_DEFERRED_FOLLOWUPS** (EN + pt-BR); **ACADEMIC_USE_AND_THESIS** (EN + pt-BR) no índice `docs/README`.                                |
| **Qualidade**       | Regra/skill **quality-sonarqube** alinhadas; **check-all-gate** menciona âmbito do pre-commit.                                                                               |
| **Wabbix**          | Guideline ajustado para **tag vs pyproject**; **WRB_DELTA_SNAPSHOT_2026-03-26** pronto para colar.                                                                           |
| **Versão**          | **Sem 1.6.8.** String no repo **1.6.7**; **tag** ainda **v1.6.6** até publicares — próximo passo é **tag + release**, não outro bump.                                        |

---

## Hoje (2026-03-26) — ordem sugerida

1. **`git status`** — rever âmbito; partir em commits se fizer sentido (`ci:` vs `docs:`).
1. **`.\scripts\check-all.ps1`** — tudo verde antes do push (ou `-SkipPreCommit` se já correste pre-commit).
1. **Commit + PR** (ou push direto se a política permitir) — merge para `main`.
1. **Tag `v1.6.7`** no commit de release e **GitHub Release** + **Docker** conforme checklist interno — *isto completa* o que `docs/releases/1.6.7.md` já descreve.
1. **Manhã: Wabbix** — enviar WRB com o guideline + bloco em [WRB_DELTA_SNAPSHOT_2026-03-26.pt_BR.md](WRB_DELTA_SNAPSHOT_2026-03-26.pt_BR.md).

---

## Opcional

- **Branch protection:** ativar checks obrigatórios depois deste merge estar verde (Semgrep + CI).
- **SBOM (CycloneDX):** seguir [ADR 0003](../adr/0003-sbom-roadmap-cyclonedx-then-syft.md) noutro PR.

---

## Atalho no chat

Diz ao agente: **`today-mode 2026-03-26`** ou abra este arquivo.
