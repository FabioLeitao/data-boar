# Follow-ups de workflow e cadeia de suprimentos (mergulho adiado)

**English:** [WORKFLOW_DEFERRED_FOLLOWUPS.md](WORKFLOW_DEFERRED_FOLLOWUPS.md)

Backlog **curto** de itens **úteis** falados em sessões de mantenedor mas **não** totalmente fechados no mesmo passo que alinhar pre-commit/CI. Use este arquivo para não perder o fio; promova itens para **`docs/plans/`** quando virarem trabalho ativo.

---

## Já melhor no repositório (contexto)

- O **lint da CI** executa **`uv run pre-commit run --all-files`**, alinhado ao **`.pre-commit-config.yaml`** (inclui **`plans-stats.py --check`**).
- **Local:** **`uv run pre-commit install`** faz os mesmos hooks rodarem no **`git commit`** (uma vez por clone).
- **ADRs:** [docs/adr/README.pt_BR.md](../adr/README.pt_BR.md) — inclui MD029, docs do operador, roadmap SBOM.

---

## Ainda a aprofundar (por prioridade)

| Tópico | Nota |
| ------ | ---- |
| **Branch protection** | Ativar no GitHub quando os **checks obrigatórios** estiverem estáveis: **CI** (Test, Lint/pre-commit, Audit, Bandit) mais **Semgrep** (e política **CodeQL** se for bloqueante no merge). Ver [QUALITY_WORKFLOW_RECOMMENDATIONS.md](../QUALITY_WORKFLOW_RECOMMENDATIONS.md) §9. |
| **SBOM** | **CycloneDX JSON** a partir do lockfile primeiro, depois **Syft** na imagem Docker — [ADR 0003](../adr/0003-sbom-roadmap-cyclonedx-then-syft.md) (EN). |
| **Auto-merge Dependabot** | Só com checks rígidos e política clara; evitar merge de deps sem olhar PRs de segurança. |
| **GitHub Environments** | Para secrets de deploy / aprovações se houver releases em estágios. |
| **Retenção de artefatos / attestations** | Proveniência estilo SLSA se clientes enterprise pedirem; opcional. |
| **Auditoria agendada** | Workflow semanal opcional **`pip-audit`** como lembrete (não substitui CI em push). |
| **CODEOWNERS** | Para **`api/`**, **`core/`**, **`SECURITY.md`** se contribuidores externos crescerem. |
| **mypy** | Tipagem gradual; não é gate de merge até triagem — [QUALITY_WORKFLOW_RECOMMENDATIONS.md](../QUALITY_WORKFLOW_RECOMMENDATIONS.md) §5. |

---

## Lembrete de release (1.6.7 e próxima)

- A versão **in-repo** **`1.6.7`** está em **`pyproject.toml`** e **`docs/releases/1.6.7.md`**; a **tag Git** **`v1.6.7`** pode atrasar até o operador publicar.
- Antes da **próxima** tag: **`.\scripts\check-all.ps1`**, atualizar **`plans-stats`** se **`PLANS_TODO.md`** mudou, confirmar Docker Hub / checklist em [DOCKER_IMAGE_RELEASE_ORDER.md](DOCKER_IMAGE_RELEASE_ORDER.md).

---

## Relacionado

- [OPERATOR_NOTIFICATION_CHANNELS.pt_BR.md](OPERATOR_NOTIFICATION_CHANNELS.pt_BR.md)
- [COMMIT_AND_PR.pt_BR.md](COMMIT_AND_PR.pt_BR.md)
