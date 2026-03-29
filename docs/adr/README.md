# Architecture Decision Records (ADR)

**Português (Brasil):** [README.pt_BR.md](README.pt_BR.md)

Short, durable notes that capture **why** the project chose an approach—not only *what* the code does. They complement the **documentation index** ([README.md](../README.md) — *Internal and reference* lists the planning tree) for backlog context, and [TESTING.md](../TESTING.md) (what CI enforces).

## Convention

| Item         | Rule                                                                                                                                                                                               |
| -----------  | ------------------------------------------------------------------------------------------------------------------------------------                                                               |
| **Location** | This folder: **`docs/adr/`**                                                                                                                                                                       |
| **Naming**   | **`0000-...`** optional **baseline / meta** (e.g. origin); **`0001-short-kebab-title.md`**, **`0002-...`** for substantive decisions — increment for each new ADR; title stays stable after merge. |
| **Language** | **Numbered ADR files (`0000-*.md`, `0001-*.md`, …) are English-only** (canonical text, like plan files under `docs/plans/`). This README has pt-BR.                                                |
| **Format**   | Prefer sections: **Context**, **Decision**, **Consequences**, **References** (MADR-style is fine). Keep to one or two screens.                                                                     |
| **When**     | Security-relevant behaviour, doc/tooling trade-offs that keep biting contributors, or anything you do not want refactored away silently.                                                           |

## Index

| ADR   | Title                                                                                                            | Status   |
| ----- | ---------------------------------------------------------------------------------------------------------------- | -------- |
| 0000  | [Project origin and ADR baseline](0000-project-origin-and-adr-baseline.md)                                       | Accepted |
| 0001  | [Markdown fix script, MD029, and semantic step lists](0001-markdown-fix-script-md029-and-semantic-step-lists.md) | Accepted |
| 0002  | [Operator-facing security and technical docs](0002-operator-facing-security-and-technical-docs.md)               | Accepted |
| 0003  | [SBOM roadmap — CycloneDX then Syft](0003-sbom-roadmap-cyclonedx-then-syft.md)                                   | Accepted |

## Related docs

- [CONTRIBUTING.md](../../CONTRIBUTING.md) — contributor workflow; links MD029 and the fix script.
- [SECURITY.md](../../SECURITY.md) · [docs/TECH_GUIDE.md](../TECH_GUIDE.md) — operator entry points ([ADR 0002](0002-operator-facing-security-and-technical-docs.md)).
- [QUALITY_WORKFLOW_RECOMMENDATIONS.md](../QUALITY_WORKFLOW_RECOMMENDATIONS.md) — §6 (MD029), §7 (ADRs), SBOM.
- [docs/ops/WORKFLOW_DEFERRED_FOLLOWUPS.md](../ops/WORKFLOW_DEFERRED_FOLLOWUPS.md) — deferred workflow/supply-chain notes.
- [.cursor/rules/markdown-lint.mdc](../../.cursor/rules/markdown-lint.mdc) — when to run `fix_markdown_sonar.py` and post-script renumbering.

## Documentation index

See [docs/README.md](../README.md) for the full documentation map.
