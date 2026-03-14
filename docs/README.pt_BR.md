# Índice da documentação

**English:** [README.md](README.md)

Esta pasta centraliza a **documentação da aplicação**. A raiz do repositório mantém os arquivos que o GitHub e as ferramentas esperam (ex.: **README.md**, **SECURITY.md**, **CONTRIBUTING.md**, **CODE_OF_CONDUCT.md**, **LICENSE**). Use este índice para encontrar guias em **inglês** e **português (Brasil)** e para alternar entre idiomas.

## Política de documentação

- **Local:** A documentação da aplicação (guias para o usuário, referência, marca, planos, releases) fica em **docs/**. A raiz do repositório mantém apenas o que o GitHub e a automação esperam: README, SECURITY, CONTRIBUTING, CODE_OF_CONDUCT, LICENSE, NOTICE. Não mova esses arquivos. READMEs de módulo que são apenas ponteiros (ex.: [deploy/README.md](../deploy/README.md), [tests/README.md](../tests/README.md)) ou avisos de obsoleto ao lado do código (ex.: database/, scanners/) podem permanecer ao lado do código. **.github/** e **.cursor/** permanecem onde o GitHub e o Cursor esperam. Novos docs substantivos (ex.: mascote, candidatos a logo, guias de funcionalidade) ficam em **docs/** e devem ser linkados neste índice.
- **Inglês (EN)** é a **fonte canônica**: representa as capacidades, funcionalidades, argumentos, config e comportamento reais da aplicação. Quando o comportamento ou as opções mudarem, atualize primeiro o doc em inglês.
- **Português brasileiro (pt-BR)** deve ser **mantido em sincronia** com a versão em inglês. Cada arquivo pt-BR é a tradução do seu par em inglês (mesma estrutura e cobertura).
- **Nova documentação:** Qualquer **novo** arquivo de documentação (guias para o usuário, referência, legal/direitos autorais, deploy, testes, etc.) deve existir em **inglês e português brasileiro**. Exceção: **arquivos de plano** (ex.: em `docs/`, `docs/completed/` ou `.cursor/plans/`) podem ser **apenas em inglês** para manter o histórico e o progresso; quando um plano gerar mudanças na aplicação, atualize as **demais docs** (README, USAGE, etc.) nos **dois idiomas** para refletir o novo comportamento.
- **Ao atualizar docs** para refletir mudanças na aplicação, **sincronize o outro idioma**: edite primeiro o doc em EN, depois atualize o arquivo pt-BR correspondente para manter estrutura e cobertura alinhadas.
- **Seletor de idioma:** Todo arquivo de documentação que tiver tradução deve ter no **topo** (logo após o título ou na primeira linha) um link claro para o outro idioma, ex.:
- Nos arquivos EN: `**Português (Brasil):** [Nome.pt_BR.md](Nome.pt_BR.md)`
- Nos arquivos pt-BR: `**English:** [Nome.md](Nome.md)`
- **Descoberta:** Quando um doc mencionar um tópico que tem doc próprio (ex.: deploy, Docker, Kubernetes, testes, topologia, commit/PR, conformidade), deve **linkar para esse doc**; se esse doc existir nos dois idiomas, forneça **os dois links** (ex.: `[DEPLOY.md](deploy/DEPLOY.md) ([pt-BR](deploy/DEPLOY.pt_BR.md))`) para o usuário alternar com facilidade. O índice principal é este [README](README.md).

## Raiz (não mover)

Estes permanecem na raiz do repositório para o GitHub e a automação:

| Documento          | English                                     | Português (pt-BR)                                       |
| ------------------ | ----------------------------                | ------------------------------------                    |
| Readme             | [README.md](../README.md)                   | [README.pt_BR.md](../README.pt_BR.md)                   |
| License            | [LICENSE](../LICENSE)                       | —                                                       |
| Notice (copyright) | [NOTICE](../NOTICE)                         | —                                                       |
| Security           | [SECURITY.md](../SECURITY.md)               | [SECURITY.pt_BR.md](../SECURITY.pt_BR.md)               |
| Contributing       | [CONTRIBUTING.md](../CONTRIBUTING.md)       | [CONTRIBUTING.pt_BR.md](../CONTRIBUTING.pt_BR.md)       |
| Code of conduct    | [CODE_OF_CONDUCT.md](../CODE_OF_CONDUCT.md) | [CODE_OF_CONDUCT.pt_BR.md](../CODE_OF_CONDUCT.pt_BR.md) |

## Uso e configuração

| Tópico                                                | English                                              | Português (pt-BR)                                                |
| --------------------                                  | --------------------------                           | ------------------------------                                   |
| Uso (CLI, API)                                        | [USAGE.md](USAGE.md)                                 | [USAGE.pt_BR.md](USAGE.pt_BR.md)                                 |
| Sensibilidade (ML/DL)                                 | [sensitivity-detection.md](sensitivity-detection.md) | [sensitivity-detection.pt_BR.md](sensitivity-detection.pt_BR.md) |
| Detecção minor                                        | [minor-detection.md](minor-detection.md)             | [minor-detection.pt_BR.md](minor-detection.pt_BR.md)             |
| Segurança (correções, testes, orientações ao técnico) | [security.md](security.md)                           | [security.pt_BR.md](security.pt_BR.md)                           |
| Versionamento                                         | [VERSIONING.md](VERSIONING.md)                       | [VERSIONING.pt_BR.md](VERSIONING.pt_BR.md)                       |
| Adicionar conectores                                  | [ADDING_CONNECTORS.md](ADDING_CONNECTORS.md)         | [ADDING_CONNECTORS.pt_BR.md](ADDING_CONNECTORS.pt_BR.md)         |
| Conformidade                                          | [compliance-frameworks.md](compliance-frameworks.md) | [compliance-frameworks.pt_BR.md](compliance-frameworks.pt_BR.md) |

## Deploy e Docker

| Tópico                          | English                              | Português (pt-BR)                                |
| -------------------------       | ----------------------------         | ------------------------------------             |
| Guia de deploy                  | [deploy/DEPLOY.md](deploy/DEPLOY.md) | [deploy/DEPLOY.pt_BR.md](deploy/DEPLOY.pt_BR.md) |
| Docker setup (MCP, build, push) | [DOCKER_SETUP.md](DOCKER_SETUP.md)   | [DOCKER_SETUP.pt_BR.md](DOCKER_SETUP.pt_BR.md)   |

Os artefatos de deploy (Compose, Kubernetes, exemplos de config) ficam na pasta [deploy/](../deploy/); veja [deploy/README.md](../deploy/README.md) para ponteiros aos docs de deploy acima.

## Marca e recursos visuais

| Tópico            | English                                              |
| ------            | ---------------------------------------------------- |
| Ativos do mascote | [mascot.md](mascot.md)                               |
| Candidatos a logo | [logo-candidates.md](logo-candidates.md)             |

## Esses docs são apenas em inglês (referência para recursos em api/static/).

## Interno e referência

| Tópico                    | English                                                  | Português (pt-BR)                                                    |
| ----------------------    | ------------------------------------                     | ------------------------------------                                 |
| Testes                    | [TESTING.md](TESTING.md)                                 | [TESTING.pt_BR.md](TESTING.pt_BR.md)                                 |
| Topologia                 | [TOPOLOGY.md](TOPOLOGY.md)                               | [TOPOLOGY.pt_BR.md](TOPOLOGY.pt_BR.md)                               |
| Commit e PR               | [COMMIT_AND_PR.md](COMMIT_AND_PR.md)                     | [COMMIT_AND_PR.pt_BR.md](COMMIT_AND_PR.pt_BR.md)                     |
| Direitos autorais e marca | [COPYRIGHT_AND_TRADEMARK.md](COPYRIGHT_AND_TRADEMARK.md) | [COPYRIGHT_AND_TRADEMARK.pt_BR.md](COPYRIGHT_AND_TRADEMARK.pt_BR.md) |

- [PLANS_TODO.md](PLANS_TODO.md) — Status dos planos e estado atual da aplicação (fonte única de verdade para os to-dos dos planos abertos). *Arquivos de plano são apenas em inglês para histórico; a documentação para o operador é EN + pt-BR.*
- [releases/](releases/) — Notas de release (ex.: 1.5.0, 1.4.3, 1.4.0).
- [completed/](completed/) — Planos concluídos arquivados e o checklist de implementação ([NEXT_STEPS.md](completed/NEXT_STEPS.md)), todos os itens Feitos.

Man pages: `docs/lgpd_crawler.1` (comando), `docs/lgpd_crawler.5` (config e formatos de arquivo). Instale com symlinks para que os dois nomes funcionem; visualize com `man data_boar` ou `man lgpd_crawler`, e `man 5 data_boar` ou `man 5 lgpd_crawler` (veja o README na raiz).
