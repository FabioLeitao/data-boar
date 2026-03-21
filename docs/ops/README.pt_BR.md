# Runbooks do operador (`docs/ops/`)

Esta pasta reúne documentação **procedural** para mantenedor/operador. Documentação de **uso do produto** (`USAGE`, `TESTING`, `DOCKER_SETUP`, etc.) permanece em [`docs/`](../README.pt_BR.md) para não misturar fluxos de usuário da aplicação com material operacional.

**Idiomas:** Cada runbook tem versão em inglês e **pt-BR** (`*.pt_BR.md`). *O histórico de planos em [`docs/plans/`](../plans/) é apenas em inglês.*

## Antes de abrir um PR (operadores)

1. Execute **`.\scripts\check-all.ps1`** na raiz do repositório no Windows (atualiza o dashboard dos planos, pre-commit e pytest completo). Em Linux/macOS, faça o equivalente: `python scripts/plans-stats.py --write`, `uv run pre-commit run --all-files`, `uv run pytest -v -W error`.
1. **Não** versionar **`docs/private/`** (inventário real do lab; ignorado pelo git) nem **`git add -f config.yaml`**. Use o modelo versionado **`docs/private.example/`** e a política **[PRIVATE_OPERATOR_NOTES.pt_BR.md](../PRIVATE_OPERATOR_NOTES.pt_BR.md)**.

---

## Índice

| Tópico                                            | English                                                                      | Português (pt-BR)                                                                        |
| ------                                            | -------                                                                      | -----------------                                                                        |
| SonarQube (home lab, Docker, CI / IDE / MCP)      | [SONARQUBE_HOME_LAB.md](SONARQUBE_HOME_LAB.md)                               | [SONARQUBE_HOME_LAB.pt_BR.md](SONARQUBE_HOME_LAB.pt_BR.md)                               |
| Home lab — smoke de deploy e alvos de dados       | [HOMELAB_VALIDATION.md](HOMELAB_VALIDATION.md)                               | [HOMELAB_VALIDATION.pt_BR.md](HOMELAB_VALIDATION.pt_BR.md)                               |
| Convenções de commit e PR                         | [COMMIT_AND_PR.md](COMMIT_AND_PR.md)                                         | [COMMIT_AND_PR.pt_BR.md](COMMIT_AND_PR.pt_BR.md)                                         |
| Remotes, `origin`, fluxo de fork                  | [REMOTES_AND_ORIGIN.md](REMOTES_AND_ORIGIN.md)                               | [REMOTES_AND_ORIGIN.pt_BR.md](REMOTES_AND_ORIGIN.pt_BR.md)                               |
| Limpeza de branches + Docker (remote legado §7)   | [BRANCH_AND_DOCKER_CLEANUP.md](BRANCH_AND_DOCKER_CLEANUP.md)                 | [BRANCH_AND_DOCKER_CLEANUP.pt_BR.md](BRANCH_AND_DOCKER_CLEANUP.pt_BR.md)                 |
| Canais de notificação ao operador                 | [OPERATOR_NOTIFICATION_CHANNELS.md](OPERATOR_NOTIFICATION_CHANNELS.md)       | [OPERATOR_NOTIFICATION_CHANNELS.pt_BR.md](OPERATOR_NOTIFICATION_CHANNELS.pt_BR.md)       |
| Operador / TI (permissões mínimas)                | [OPERATOR_IT_REQUIREMENTS.md](OPERATOR_IT_REQUIREMENTS.md)                   | [OPERATOR_IT_REQUIREMENTS.pt_BR.md](OPERATOR_IT_REQUIREMENTS.pt_BR.md)                   |
| Ajuste prático de identificação agregada (Fase C) | [AGGREGATED_IDENTIFICATION_TUNING.md](AGGREGATED_IDENTIFICATION_TUNING.md)   | [AGGREGATED_IDENTIFICATION_TUNING.pt_BR.md](AGGREGATED_IDENTIFICATION_TUNING.pt_BR.md)   |
| Resolução de problemas — implantação Docker       | [TROUBLESHOOTING_DOCKER_DEPLOYMENT.md](TROUBLESHOOTING_DOCKER_DEPLOYMENT.md) | [TROUBLESHOOTING_DOCKER_DEPLOYMENT.pt_BR.md](TROUBLESHOOTING_DOCKER_DEPLOYMENT.pt_BR.md) |

**Relacionado (fora desta pasta):** [SECURITY.md](../SECURITY.md) / [SECURITY.pt_BR.md](../SECURITY.pt_BR.md) e [CODE_PROTECTION_OPERATOR_PLAYBOOK.md](../CODE_PROTECTION_OPERATOR_PLAYBOOK.md) / [CODE_PROTECTION_OPERATOR_PLAYBOOK.pt_BR.md](../CODE_PROTECTION_OPERATOR_PLAYBOOK.pt_BR.md) — postura de segurança e endurecimento **Priority band A**, listados junto da política principal em [`docs/README.pt_BR.md`](../README.pt_BR.md).

---

## Checklist de auditoria de links (após mover ou renomear docs)

Use ao abrir um PR do tipo **docs: cluster ops runbooks under docs/ops**.

- [ ] **[README.md](../README.md)** / **[README.pt_BR.md](../README.pt_BR.md)** — tabelas em **Uso** / **Interno** e ponteiros a **ops/**.
- [ ] **Raiz [CONTRIBUTING.md](../../CONTRIBUTING.md)** — caminhos `docs/…` afetados.
- [ ] **[`.cursor/rules/`](../../.cursor/rules/)** e **[`.cursor/skills/`](../../.cursor/skills/)** — links para `docs/` ou `docs/ops/`.
- [ ] **Links entre docs** dentro dos arquivos movidos (`../`, `ops/`, `plans/`).
- [ ] **`docs/plans/*.md`** — links relativos de `plans/` para `../ops/…` ou `../CODE_PROTECTION…`.
- [ ] **Opcional:** `rg` pelo **caminho antigo** e corrigir resíduos.

**Não** alterar `.github/`, `sonar.sources` nem a disposição de **SECURITY** / **CONTRIBUTING** na raiz, salvo objetivo explícito; preferir só atualização de links.

**Automatização:** `uv run pytest tests/test_docs_markdown.py tests/test_markdown_lint.py`
