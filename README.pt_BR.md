# Data Boar

![Data Boar mascot](api/static/mascot/data_boar_mascote_color.svg)

**English:** [README.md](README.md) · [docs/USAGE.md](docs/USAGE.md)

---

## Para gestores e líderes de conformidade

Sua organização precisa saber **onde** estão os dados pessoais e sensíveis—para cumprir **LGPD**, **GDPR**, **CCPA**, **HIPAA**, **GLBA** e evitar surpresas custosas. Auditorias em larga escala e descoberta manual costumam ser **caras e consumir muito tempo**. O **Data Boar** ajuda a construir **consciência de conformidade** e a trazer à tona **possíveis violações**—inclusive as que passam fácil despercebidas—sem custo fora de controle: um único motor configurável que fuça seus dados e reporta o que encontra, para que TI, cibersegurança e conformidade, junto com DPOs, possam agir com base em informação e reduzir o risco de penalidades.

**O que trazemos à tona:** Além de PII óbvio (CPF, e-mail, telefone etc.), o Data Boar usa **IA** (aprendizado de máquina e deep learning opcional) para detectar **categorias sensíveis** (saúde, religião, opinião política, biométrico, genético e outras sob LGPD Art. 5 II e GDPR Art. 9), **combinações de quasi-identificadores** que podem reidentificar pessoas (LGPD Art. 5, GDPR Recital 26) e **possíveis dados de menores** (LGPD Art. 14, GDPR Art. 8). Ele pode revelar exposição em **colunas legadas**, **exportações**, **dashboards** e **múltiplas fontes** em uma única visão—para você enxergar lacunas que checagens manuais ou ferramentas só baseadas em regras costumam perder.

Como um **javali**, ele é **faminto e tenaz**: não para de buscar, aprofunda em várias fontes e não fica na superfície. É resistente o bastante para ambientes heterogêneos. O Data Boar está pronto para **ingerir e digerir sua “sopa de dados”**—quaisquer que sejam os ingredientes. Quando configurado e autorizado corretamente, pode varrer **arquivos locais e remotos**, **bancos SQL** (PostgreSQL, MySQL, SQL Server, Oracle, Snowflake e outros), **NoSQL** (MongoDB, Redis), **APIs**, **dashboards**, **Power BI**, **Dataverse**, **SharePoint**, **WebDAV**, **SMB/NFS** e outras fontes. Ele **não armazena nem exfiltra** conteúdo pessoal ou sensível—apenas **metadados** (onde foi encontrado, tipo de padrão, nível de sensibilidade). Assim você obtém **visibilidade para maturidade e remediação** sem mover nem copiar PII.

**Por que sustenta:** Um único motor para muitas fontes; ajuste **via configuração** (regex, termos ML/DL, norm tags, overrides de recomendação) para alinhar a diferentes frameworks sem mudar código; **relatórios Excel** e **heatmaps** com tendências entre sessões; varreduras **agendáveis** via API para monitoramento contínuo. Já oferecemos suporte direto a **LGPD**, **GDPR**, **CCPA**, **HIPAA** e **GLBA** e fornecemos **exemplos de configuração** (ex.: [regex overrides](docs/regex_overrides.example.yaml), overrides de recomendação no [USAGE](docs/USAGE.pt_BR.md)) para estender a **UK GDPR**, **PIPEDA**, **POPIA**, **APPI**, **PCI-DSS** ou normas customizadas. Se sua regulamentação ou escopo de conformidade exigir ajuste fino, **podemos ajudar**—criando arquivos de config sob medida ou fazendo pequenos ajustes no código—para melhor compatibilidade quando você entrar em contato. As **prioridades de roadmap** incluem endurecimento de segurança, timeouts configuráveis, amostras de conformidade adicionais (UK GDPR, PIPEDA, POPIA, APPI, PCI-DSS), varredura opcional dentro de arquivos compactados, validação de criptografia e controles e SAP e outras fontes empresariais (ex.: ServiceNow, Salesforce)—para o produto seguir evoluindo em direção aos controles que seus auditores esperam.

Os relatórios cobrem **múltiplas sessões de varredura**, com **tendências** (esta execução vs anteriores), **recomendações** com base nos achados, **heatmaps** e evolução no tempo. Você pode **agendar varreduras** por scripts ou orquestradores que chamam a **API interna**, permitindo monitoramento contínuo de conformidade. A ferramenta é **flexível**: dá para ajustá-la a outras checagens de conformidade alterando a **configuração** (regex, termos ML/DL, norm tags, overrides de recomendação)—sem mudar código em muitos cenários. Ajuda **TI, cibersegurança, conformidade e DPOs** a trabalhar juntos para entender a exposição e tomar as ações adequadas conforme as normas que você adota.

**Convidamos você a entrar em contato** para ver como o Data Boar pode apoiar sua jornada de conformidade.

**Cenários típicos:** Preparação para auditoria ou pedido do regulador; mapeamento de dados antes de migração ou implantação de DLP; conscientização de conformidade sem war room completo.

> **Release atual:** 1.5.3. Notas de release: [docs/releases/](docs/releases/) e a [página de Releases no GitHub](https://github.com/FabioLeitao/data-boar/releases).
> **Documentação:** Este README e o `docs/USAGE.pt_BR.md` são as referências em português. Quando funcionalidades ou opções mudarem, atualize **ambos** os idiomas para mantê-los sincronizados.

---

## Visão técnica

O Data Boar roda como auditoria **CLI de execução única** ou como **API REST** (porta padrão 8088) com dashboard web. Você configura **alvos** (bancos, filesystems, APIs, shares, Power BI, Dataverse) e **detecção de sensibilidade** (regex + ML, DL opcional) em um único arquivo de config **YAML ou JSON**. Ele grava achados e metadados de sessão em um banco **SQLite** local e gera **relatórios Excel** e um **heatmap PNG** por sessão.

| Se você precisa de…                                          | Veja                                                                                                                                     |
| -------------------                                          | -----                                                                                                                                    |
| Instalação, execução, referência CLI/API, conectores, deploy | [Guia técnico (pt-BR)](docs/TECH_GUIDE.pt_BR.md) · [Technical guide (EN)](docs/TECH_GUIDE.md)                                            |
| Esquema de configuração, credenciais, exemplos               | [USAGE.pt_BR.md](docs/USAGE.pt_BR.md) · [USAGE.md](docs/USAGE.md)                                                                        |
| Deploy (Docker, Compose, Kubernetes)                         | [deploy/DEPLOY.pt_BR.md](docs/deploy/DEPLOY.pt_BR.md) · [deploy/DEPLOY.md](docs/deploy/DEPLOY.md)                                        |
| Detecção de sensibilidade (termos ML/DL)                     | [SENSITIVITY_DETECTION.pt_BR.md](docs/SENSITIVITY_DETECTION.pt_BR.md) · [SENSITIVITY_DETECTION.md](docs/SENSITIVITY_DETECTION.md)        |
| Testes, segurança, contribuição                              | [docs/TESTING.pt_BR.md](docs/TESTING.pt_BR.md) · [SECURITY.pt_BR.md](SECURITY.pt_BR.md) · [CONTRIBUTING.pt_BR.md](CONTRIBUTING.pt_BR.md) |

**Início rápido (na raiz do repositório):** `uv sync` → prepare `config.yaml` (veja `deploy/config.example.yaml` e [USAGE](docs/USAGE.pt_BR.md)) → `uv run python main.py --config config.yaml` para execução única, ou `uv run python main.py --config config.yaml --web` para a API e o dashboard em <http://localhost:8088/>.

**Índice completo da documentação** (todos os tópicos e idiomas): [docs/README.md](docs/README.md) · [docs/README.pt_BR.md](docs/README.pt_BR.md).

**Licença e direitos autorais:** [LICENSE](LICENSE) · [NOTICE](NOTICE) · [docs/COPYRIGHT_AND_TRADEMARK.pt_BR.md](docs/COPYRIGHT_AND_TRADEMARK.pt_BR.md) ([EN](docs/COPYRIGHT_AND_TRADEMARK.md)).
