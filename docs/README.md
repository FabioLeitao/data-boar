# Documentation index

**Português (Brasil):** [README.pt_BR.md](README.pt_BR.md)

This folder centralizes **application documentation**. Repository root keeps the files that GitHub and tooling expect (e.g. **README.md**, **SECURITY.md**, **CONTRIBUTING.md**, **CODE_OF_CONDUCT.md**, **LICENSE**). Use this index to find guides in **English** and **Português (Brasil)** and to jump between languages. **Browse the tables below by topic**; each row links to the English and Português (Brasil) version when available, so you can reach every document and switch language at any time.

## Documentation policy

- **Location:** Application documentation (user-facing guides, reference, branding, plans, releases) lives under **docs/**. The repo root keeps only what GitHub and automation expect: README, SECURITY, CONTRIBUTING, CODE_OF_CONDUCT, LICENSE, NOTICE. Do not move those. Module-level READMEs that are mere pointers (e.g. [deploy/README.md](../deploy/README.md), [tests/README.md](../tests/README.md)) or deprecated notices next to code (e.g. database/, scanners/) may stay beside the code. **.github/** and **.cursor/** stay where GitHub and Cursor expect them. New substantive docs (e.g. mascot, logo candidates, feature guides) belong in **docs/** and should be linked from this index.
- **English (EN)** is the **canonical** source: it represents the true capabilities, features, arguments, config, and behaviour of the application. When behaviour or options change, update the English doc first.
- **Brazilian Portuguese (pt-BR)** must be **kept in sync** with the English version. Each pt-BR file is a translation of its English counterpart (same structure and coverage).
- **New documentation:** Any **new** documentation file (user-facing guides, reference, legal/copyright, deploy, testing, etc.) must exist in **both English and Brazilian Portuguese**. Exception: **plan files** (e.g. under `docs/plans/`, `docs/plans/completed/`, or `.cursor/plans/`) may be **English-only** to keep track of history and progress; when a plan drives changes to the application, update the **other docs** (README, USAGE, etc.) in **both languages** so they reflect the new behaviour.
- **When you update docs** to reflect application changes, **sync the other language** too: edit the EN doc first, then update the corresponding pt-BR file so structure and coverage stay aligned.
- **Language switcher:** Every documentation file that has a translation must have at the **top** (right after the title or in the first line) a clear link to the other language, e.g.
- In EN files: `**Português (Brasil):** [Filename.pt_BR.md](Filename.pt_BR.md)`
- In pt-BR files: `**English:** [Filename.md](Filename.md)`
- **Discoverability:** When a doc mentions a topic that has its own dedicated doc (e.g. deploy, Docker, Kubernetes, testing, topology, commit/PR, compliance), it should **link to that doc**; if that doc exists in both languages, provide **both links** (e.g. `[DEPLOY.md](deploy/DEPLOY.md) ([pt-BR](deploy/DEPLOY.pt_BR.md))`) so the user can switch language easily. The main index is this [README](README.md).

## Root (do not move)

These stay at repo root for GitHub and automation:

| Document           | English                                     | Português (pt-BR)                                       |
| ----------------   | ----------------------------                | ------------------------------------                    |
| Readme             | [README.md](../README.md)                   | [README.pt_BR.md](../README.pt_BR.md)                   |
| License            | [LICENSE](../LICENSE)                       | —                                                       |
| Notice (copyright) | [NOTICE](../NOTICE)                         | —                                                       |
| Security           | [SECURITY.md](../SECURITY.md)               | [SECURITY.pt_BR.md](../SECURITY.pt_BR.md)               |
| Contributing       | [CONTRIBUTING.md](../CONTRIBUTING.md)       | [CONTRIBUTING.pt_BR.md](../CONTRIBUTING.pt_BR.md)       |
| Code of conduct    | [CODE_OF_CONDUCT.md](../CODE_OF_CONDUCT.md) | [CODE_OF_CONDUCT.pt_BR.md](../CODE_OF_CONDUCT.pt_BR.md) |

## Usage and configuration

| Topic                                               | English                                              | Português (pt-BR)                                                |
| ------------------                                  | --------------------------                           | ------------------------------                                   |
| Technical guide (install, run, CLI/API, connectors) | [TECH_GUIDE.md](TECH_GUIDE.md)                       | [TECH_GUIDE.pt_BR.md](TECH_GUIDE.pt_BR.md)                       |
| Usage (CLI, API)                                    | [USAGE.md](USAGE.md)                                 | [USAGE.pt_BR.md](USAGE.pt_BR.md)                                 |
| Sensitivity (ML/DL)                                 | [SENSITIVITY_DETECTION.md](SENSITIVITY_DETECTION.md) | [SENSITIVITY_DETECTION.pt_BR.md](SENSITIVITY_DETECTION.pt_BR.md) |
| Minor detection                                     | [MINOR_DETECTION.md](MINOR_DETECTION.md)             | [MINOR_DETECTION.pt_BR.md](MINOR_DETECTION.pt_BR.md)             |
| Security (fixes, tests, technician guidance)        | [SECURITY.md](SECURITY.md)                           | [SECURITY.pt_BR.md](SECURITY.pt_BR.md)                           |
| Versioning                                          | [VERSIONING.md](VERSIONING.md)                       | [VERSIONING.pt_BR.md](VERSIONING.pt_BR.md)                       |
| Adding connectors                                   | [ADDING_CONNECTORS.md](ADDING_CONNECTORS.md)         | [ADDING_CONNECTORS.pt_BR.md](ADDING_CONNECTORS.pt_BR.md)         |
| Compliance                                          | [COMPLIANCE_FRAMEWORKS.md](COMPLIANCE_FRAMEWORKS.md) | [COMPLIANCE_FRAMEWORKS.pt_BR.md](COMPLIANCE_FRAMEWORKS.pt_BR.md) |
| Glossary (terms)                                    | [GLOSSARY.md](GLOSSARY.md)                           | [GLOSSARY.pt_BR.md](GLOSSARY.pt_BR.md)                           |

## Deploy and Docker

| Topic                           | English                              | Português (pt-BR)                                |
| ------------                    | ----------------------------         | ------------------------------------             |
| Deploy guide                    | [deploy/DEPLOY.md](deploy/DEPLOY.md) | [deploy/DEPLOY.pt_BR.md](deploy/DEPLOY.pt_BR.md) |
| Docker setup (MCP, build, push) | [DOCKER_SETUP.md](DOCKER_SETUP.md)   | [DOCKER_SETUP.pt_BR.md](DOCKER_SETUP.pt_BR.md)   |

Deploy assets (Compose, Kubernetes, config examples) remain in the [deploy/](../deploy/) folder; see [deploy/README.md](../deploy/README.md) for pointers to the deploy docs above.

## Branding and assets

| Topic           | English                                    |
| -------         | ------------------------------------------ |
| Mascot assets   | [MASCOT.md](MASCOT.md)                     |
| Logo candidates | [LOGO_CANDIDATES.md](LOGO_CANDIDATES.md)   |

## These docs are EN-only (reference for assets in api/static/)

## Internal and reference

| Topic                   | English                                                  | Português (pt-BR)                                                    |
| ---------------         | -----------------------------                            | ------------------------------------                                 |
| Testing                 | [TESTING.md](TESTING.md)                                 | [TESTING.pt_BR.md](TESTING.pt_BR.md)                                 |
| Topology                | [TOPOLOGY.md](TOPOLOGY.md)                               | [TOPOLOGY.pt_BR.md](TOPOLOGY.pt_BR.md)                               |
| Commit and PR           | [COMMIT_AND_PR.md](COMMIT_AND_PR.md)                     | [COMMIT_AND_PR.pt_BR.md](COMMIT_AND_PR.pt_BR.md)                     |
| Remotes and origin      | [REMOTES_AND_ORIGIN.md](REMOTES_AND_ORIGIN.md)           | [REMOTES_AND_ORIGIN.pt_BR.md](REMOTES_AND_ORIGIN.pt_BR.md)           |
| Troubleshooting         | [TROUBLESHOOTING.md](TROUBLESHOOTING.md)                 | [TROUBLESHOOTING.pt_BR.md](TROUBLESHOOTING.pt_BR.md)                 |
| Copyright and trademark | [COPYRIGHT_AND_TRADEMARK.md](COPYRIGHT_AND_TRADEMARK.md) | [COPYRIGHT_AND_TRADEMARK.pt_BR.md](COPYRIGHT_AND_TRADEMARK.pt_BR.md) |
| Observability and SRE   | [OBSERVABILITY_SRE.md](OBSERVABILITY_SRE.md)             | [OBSERVABILITY_SRE.pt_BR.md](OBSERVABILITY_SRE.pt_BR.md)             |

- [plans/PLANS_TODO.md](plans/PLANS_TODO.md) — Plan status and current app state (single source of truth for open-plan to-dos). *Plan files are EN-only for history; operator docs are EN + pt-BR.*
- [releases/](releases/) — Release notes (e.g. 1.5.3, 1.5.2, 1.5.1, 1.5.0, 1.4.3).
- [plans/completed/](plans/completed/) — Archived completed plans and the implementation checklist ([NEXT_STEPS.md](plans/completed/NEXT_STEPS.md)), all items Done.

Man pages: `docs/lgpd_crawler.1` (command), `docs/lgpd_crawler.5` (config and file formats). Install with symlinks so both names work; view with `man data_boar` or `man lgpd_crawler`, and `man 5 data_boar` or `man 5 lgpd_crawler` (see root README).
