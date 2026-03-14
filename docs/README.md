# Documentation index

**Português (Brasil):** [README.pt_BR.md](README.pt_BR.md)

This folder centralizes **application documentation**. Repository root keeps the files that GitHub and tooling expect (e.g. **README.md**, **SECURITY.md**, **CONTRIBUTING.md**, **CODE_OF_CONDUCT.md**, **LICENSE**). Use this index to find guides in **English** and **Português (Brasil)** and to jump between languages.

## Documentation policy

- **English (EN)** is the **canonical** source: it represents the true capabilities, features, arguments, config, and behaviour of the application. When behaviour or options change, update the English doc first.
- **Brazilian Portuguese (pt-BR)** must be **kept in sync** with the English version. Each pt-BR file is a translation of its English counterpart (same structure and coverage).
- **New documentation:** Any **new** documentation file (user-facing guides, reference, legal/copyright, deploy, testing, etc.) must exist in **both English and Brazilian Portuguese**. Exception: **plan files** (e.g. under `docs/`, `docs/completed/`, or `.cursor/plans/`) may be **English-only** to keep track of history and progress; when a plan drives changes to the application, update the **other docs** (README, USAGE, etc.) in **both languages** so they reflect the new behaviour.
- **When you update docs** to reflect application changes, **sync the other language** too: edit the EN doc first, then update the corresponding pt-BR file so structure and coverage stay aligned.
- **Language switcher:** Every documentation file that has a translation must have at the **top** (right after the title or in the first line) a clear link to the other language, e.g.
- In EN files: `**Português (Brasil):** [Filename.pt_BR.md](Filename.pt_BR.md)`
- In pt-BR files: `**English:** [Filename.md](Filename.md)`
- **Discoverability:** When a doc mentions a topic that has its own dedicated doc (e.g. deploy, Docker, Kubernetes, testing, topology, commit/PR, compliance), it should **link to that doc**; if that doc exists in both languages, provide **both links** (e.g. `[DEPLOY.md](deploy/DEPLOY.md) ([pt-BR](deploy/DEPLOY.pt_BR.md))`) so the user can switch language easily. The main index is this [README](README.md).

## Root (do not move)

These stay at repo root for GitHub and automation:

| Document         | English                                     | Português (pt-BR)                                       |
| ---------------- | ----------------------------                | ------------------------------------                    |
| Readme           | [README.md](../README.md)                   | [README.pt_BR.md](../README.pt_BR.md)                   |
| License          | [LICENSE](../LICENSE)                       | —                                                        |
| Notice (copyright) | [NOTICE](../NOTICE)                       | —                                                        |
| Security         | [SECURITY.md](../SECURITY.md)               | [SECURITY.pt_BR.md](../SECURITY.pt_BR.md)               |
| Contributing     | [CONTRIBUTING.md](../CONTRIBUTING.md)       | [CONTRIBUTING.pt_BR.md](../CONTRIBUTING.pt_BR.md)       |
| Code of conduct  | [CODE_OF_CONDUCT.md](../CODE_OF_CONDUCT.md) | [CODE_OF_CONDUCT.pt_BR.md](../CODE_OF_CONDUCT.pt_BR.md) |

## Usage and configuration

| Topic                                        | English                                              | Português (pt-BR)                                                |
| ------------------                           | --------------------------                           | ------------------------------                                   |
| Usage (CLI, API)                             | [USAGE.md](USAGE.md)                                 | [USAGE.pt_BR.md](USAGE.pt_BR.md)                                 |
| Sensitivity (ML/DL)                          | [sensitivity-detection.md](sensitivity-detection.md) | [sensitivity-detection.pt_BR.md](sensitivity-detection.pt_BR.md) |
| Minor detection                              | [minor-detection.md](minor-detection.md)             | [minor-detection.pt_BR.md](minor-detection.pt_BR.md)             |
| Security (fixes, tests, technician guidance) | [security.md](security.md)                           | [security.pt_BR.md](security.pt_BR.md)                           |
| Versioning                                   | [VERSIONING.md](VERSIONING.md)                       | [VERSIONING.pt_BR.md](VERSIONING.pt_BR.md)                       |
| Adding connectors                            | [ADDING_CONNECTORS.md](ADDING_CONNECTORS.md)         | [ADDING_CONNECTORS.pt_BR.md](ADDING_CONNECTORS.pt_BR.md)         |
| Compliance                                   | [compliance-frameworks.md](compliance-frameworks.md) | [compliance-frameworks.pt_BR.md](compliance-frameworks.pt_BR.md) |

## Deploy and Docker

| Topic                           | English                              | Português (pt-BR)                                |
| ------------                    | ----------------------------         | ------------------------------------             |
| Deploy guide                    | [deploy/DEPLOY.md](deploy/DEPLOY.md) | [deploy/DEPLOY.pt_BR.md](deploy/DEPLOY.pt_BR.md) |
| Docker setup (MCP, build, push) | [DOCKER_SETUP.md](DOCKER_SETUP.md)   | [DOCKER_SETUP.pt_BR.md](DOCKER_SETUP.pt_BR.md)   |

Deploy assets (Compose, Kubernetes, config examples) remain in the [deploy/](../deploy/) folder; see [deploy/README.md](../deploy/README.md) for pointers to the deploy docs above.

## Internal and reference

| Topic           | English                              | Português (pt-BR)                                |
| --------------- | -----------------------------        | ------------------------------------             |
| Testing         | [TESTING.md](TESTING.md)             | [TESTING.pt_BR.md](TESTING.pt_BR.md)             |
| Topology        | [TOPOLOGY.md](TOPOLOGY.md)           | [TOPOLOGY.pt_BR.md](TOPOLOGY.pt_BR.md)           |
| Commit and PR   | [COMMIT_AND_PR.md](COMMIT_AND_PR.md) | [COMMIT_AND_PR.pt_BR.md](COMMIT_AND_PR.pt_BR.md) |
| Copyright and trademark | [COPYRIGHT_AND_TRADEMARK.md](COPYRIGHT_AND_TRADEMARK.md) | [COPYRIGHT_AND_TRADEMARK.pt_BR.md](COPYRIGHT_AND_TRADEMARK.pt_BR.md) |

- [PLANS_TODO.md](PLANS_TODO.md) ([pt-BR](PLANS_TODO.pt_BR.md)) — Plan status and current app state (single source of truth for open-plan to-dos).
- [releases/](releases/) — Release notes (e.g. 1.5.0, 1.4.3, 1.4.0).
- [completed/](completed/) — Archived completed plans and the implementation checklist ([NEXT_STEPS.md](completed/NEXT_STEPS.md) ([pt-BR](completed/NEXT_STEPS.pt_BR.md)), all items Done.

Man pages: `docs/lgpd_crawler.1` (command), `docs/lgpd_crawler.5` (config and file formats). Install with symlinks so both names work; view with `man data_boar` or `man lgpd_crawler`, and `man 5 data_boar` or `man 5 lgpd_crawler` (see root README).
