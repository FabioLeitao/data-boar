# Data Boar

**Data Boar — baseado na tecnologia lgpd_crawler.** Descoberta e mapeamento de dados pessoais e sensíveis com consciência de conformidade na sua sopa de dados.

![Data Boar mascot](api/static/mascot/data_boar_mascote_color.svg)

**English:** [README.md](README.md) · [docs/USAGE.md](docs/USAGE.md)

---

## Para gestores e líderes de conformidade

Sua organização precisa saber **onde** estão os dados pessoais e sensíveis — para cumprir **LGPD**, **GDPR**, **CCPA**, **HIPAA**, **GLBA** e evitar surpresas custosas. O **Data Boar** ajuda a construir **consciência de conformidade** e a trazer à tona **possíveis violações** sem custo fora de controle: um único motor configurável que varre seus dados e reporta o que encontra, para que TI, cibersegurança, conformidade e DPOs possam agir com base em informação.

**O que trazemos à tona:** Além de PII óbvio (CPF, CNPJ — incluindo o novo formato alfanumérico, e-mail, telefone), usamos **IA** (ML e DL opcional) para detectar **categorias sensíveis** (saúde, religião, opinião política, biométrico, genético—LGPD Art. 5 II, GDPR Art. 9), **combinações de quasi-identificadores** (LGPD Art. 5, GDPR Recital 26) e **possíveis dados de menores** (LGPD Art. 14, GDPR Art. 8). Reconhecemos nomes regionais de documentos e sinalizamos identificadores ambíguos para confirmação manual, e revelamos exposição em **colunas legadas**, **exportações**, **dashboards** e **múltiplas fontes** em uma visão—para você enxergar lacunas que checagens manuais ou ferramentas só de regras costumam perder.

O risco real—**shadow IT** e além—costuma estar escondido em planilhas paralelas, pastas esquecidas, bancos legados, falta de padronização, fluxos confusos, aplicações mal documentadas, exceções e coleta excessiva de dados. O Data Boar segue farejando sua sopa de dados para trazer à tona esses ingredientes ocultos—incluindo arquivos renomeados ou mascarados e transporte ou armazenamento mais frágeis—para que conformidade e jurídico vejam o que de fato está lá, e não só a aparência. **Mídia rica hoje:** varreduras **opcionais de metadados**, **OCR em imagens** e arquivos de **legenda** ajudam a achar o que busca full-text simples costuma perder. **Horizonte (por fases, muitas vezes opt-in):** sinais mais fortes para **rastreadores embutidos**, **esteganografia** e **truques em documento** (microtexto, Unicode, objetos aninhados)—sem prometer detecção exaustiva até cada fatia existir no produto.

**Faminto pela sua sopa de dados:** Como um **javali**, aprofundamos em várias fontes e não paramos na superfície. Sejam quais forem os ingredientes—**arquivos**, **SQL**, **NoSQL**, **APIs**, **Power BI**, **Dataverse**, **SharePoint**, **SMB/NFS** e outros—estamos prontos para ingerir e digerir. **Não armazenamos nem exfiltramos** PII, apenas **metadados** (onde foi encontrado, tipo de padrão, sensibilidade), para você obter visibilidade para remediação sem mover dados. Para um resumo objetivo para equipes jurídicas e de conformidade, veja [Conformidade e jurídico](docs/COMPLIANCE_AND_LEGAL.pt_BR.md).

**Por que sustenta:** Um único motor, **via configuração** (regex, termos ML/DL, norm tags, overrides de recomendação) — sem mudar código para alinhar a diferentes frameworks. **Relatórios Excel**, **heatmaps** e **tendências** entre sessões; varreduras **agendáveis** via API. Suportamos **LGPD**, **GDPR**, **CCPA**, **HIPAA**, **GLBA** prontos; **amostras de config** para **UK GDPR**, **EU GDPR**, **Benelux**, **PIPEDA**, **POPIA**, **APPI**, **PCI-DSS** e outras regiões vêm com **orientação de frameworks** e ficam em **compliance-samples** (navegue a partir da tabela abaixo).

Idiomas e encodings legados são suportados; **timeouts configuráveis** e **endurecimento de segurança** (validação, headers, auditoria) estão em vigor. **Arquivos compactados:** varredura dentro de zip, tar, gz, 7z via config, CLI ou dashboard — detalhes e avisos de I/O estão em **USAGE** (tabela abaixo). A detecção opcional de **content-type** ajuda a encontrar arquivos renomeados ou mascarados (ex.: PDF disfarçado de .txt); visibilidade inicial de **cripto/transporte** (ex.: TLS vs texto puro) é coletada para bancos e APIs.

**Farejando com critério no rastro de arquivos:** Leituras de texto plano usam um **orçamento configurável de caracteres** para que o motor veja estrutura de verdade — não só um pedaço inútil — antes de decidir; conteúdo em **formato de entretenimento** (ex.: cifras, letras, trechos típicos de README de projeto aberto) encaminha **sugestões ruidosas de ML** para uma **faixa de revisão**, em vez de lotar o relatório com falsos alarmes “certos”, enquanto **achados fortes por padrão** (documentos, dados de pagamento, PII clara) seguem prioritários para triagem.

**Foco de roadmap:** cobertura mais profunda de **mídia** e **documentos** (“ingredientes ocultos”), taxonomia **Tier 3b / Tier 4**, conectores de **armazenamento de objetos em nuvem** (classe S3, Azure Blob, GCS), conectores **enterprise / back-office**, validação de **cripto/controles**, refinamento da **detecção**, **notificações** ao fim da varredura / fora de banda (vários canais, cópia opcional ao tenant; **desligadas por padrão**) e padrões de **acesso ao dashboard/API**. Operadores podem ler o snapshot **`runtime_trust`** em **`GET /status`** para saber se ambiente/config em execução parece **confiável, degradado ou não confiável** em automação e laboratório. **Cadeia de suprimentos de dependências:** **lockfile** versionado, **auditoria de dependências** (`pip-audit`) na CI e **Dependabot** para Python e GitHub Actions reduzem risco de **CVEs conhecidos** no caminho **PyPI**; artefatos **SBOM** em release estão previstos ([ADR 0003](docs/adr/0003-sbom-roadmap-cyclonedx-then-syft.md)). O alinhamento com **ISO/IEC 27701** (PIMS), **SOC 2** e **FELCA** (mapeamento de dados de menores) está documentado; seguimos ampliando o suporte a normas auditáveis e regionais. Contextos **nos EUA** sobre privacidade de **crianças e menores** (perfis de amostra opcionais para enquadramento **FTC COPPA**, **Califórnia AB 2273**, **Colorado CPA / menores de 18**) apoiam preparação de auditoria e revisão liderada pelo DPO **em nível técnico** apenas—**não** são aconselhamento jurídico nem prova de idade. Para detalhes de framework e do que já existe vs fases futuras, use o hub de navegação abaixo (e [Conformidade e jurídico](docs/COMPLIANCE_AND_LEGAL.pt_BR.md)).

**Roadmap — internacionalização e profundidade regional:** O **javali** já **fareja** **dados** **Unicode** (muitos scripts no conteúdo); **textos do dashboard** e **documentação versionada** **ainda não** cobrem todos os mercados em **UI** completa. **Não** reivindicamos localização plena para tudo abaixo **hoje** — a lista mostra **direção**, **sem ordem fixa** nem promessa de data, conforme **demanda** e **relevância regulatória**: **Ásia Oriental e Sudeste Asiático** (ex.: **mandarim** / **cantonês** e outras formas **chinesas**, **japonês**, **coreano**, **indonésio**, **tailandês**, **vietnamita**, **filipino**, **hindi** e outros **scripts índicos**), **Oriente Médio** e **África** (ex.: mais contextos em **árabe**, **etíope** / **amárico** (script **etiópico**) e **âmbitos africanos** de idiomas e privacidade conforme parceiros precisarem), **Europa** além dos grandes idiomas (**catalão**, **basco**, **galego** e outras línguas **cooficiais** ou regionais), além de **amostras YAML de compliance** quando a jurisdição justificar. Prioridades podem subir via **issues no GitHub** ou **serviços profissionais** — a **sopa** ganha **ingredientes** ao longo do tempo, não todos de uma vez.

**Convidamos você a entrar em contato** para ver como o Data Boar pode apoiar sua jornada de conformidade. **Serviços profissionais** opcionais — apoio para mapear a **sopa de dados** e afinar a configuração ao seu mix regulatório — estão resumidos na seção *Serviços profissionais* da página **Conformidade e jurídico** linkada acima.

**Cenários típicos:** Preparação para auditoria ou pedido do regulador; mapeamento de dados antes de migração ou implantação de DLP; conscientização de conformidade sem war room completo.

> **Release atual:** 1.6.7. Resumo: [CHANGELOG.md](CHANGELOG.md). Notas completas: [docs/releases/](docs/releases/) e a [página de Releases no GitHub](https://github.com/FabioLeitao/data-boar/releases).
> **Documentação:** Este README e o `docs/USAGE.pt_BR.md` são as referências em português. Quando funcionalidades ou opções mudarem, atualize **ambos** os idiomas para mantê-los sincronizados.

---

## Visão técnica

O Data Boar roda como auditoria **CLI de execução única** ou como **API REST** (porta padrão 8088) com dashboard web. Você configura **alvos** (bancos, filesystems, APIs, shares, Power BI, Dataverse) e **detecção de sensibilidade** (regex + ML, DL opcional) em um único arquivo de config **YAML ou JSON**. Ele grava achados e metadados de sessão em um banco **SQLite** local e gera **relatórios Excel** e um **heatmap PNG** por sessão.

Se você precisa de:

- **Frameworks de conformidade, amostras, resumo jurídico (DPOs, compras):** [COMPLIANCE_FRAMEWORKS.pt_BR.md](docs/COMPLIANCE_FRAMEWORKS.pt_BR.md) · [COMPLIANCE_AND_LEGAL.pt_BR.md](docs/COMPLIANCE_AND_LEGAL.pt_BR.md) · [compliance-samples/](docs/compliance-samples/) ([índice de amostras](docs/COMPLIANCE_FRAMEWORKS.pt_BR.md#amostras-de-conformidade))
- **Direção do produto e cadência de releases:** [docs/releases/](docs/releases/) · [GitHub Releases](https://github.com/FabioLeitao/data-boar/releases)
- **Instalação, execução, referência CLI/API, conectores, deploy:** [Guia técnico (pt-BR)](docs/TECH_GUIDE.pt_BR.md) · [Technical guide (EN)](docs/TECH_GUIDE.md)
- **Esquema de configuração, credenciais, exemplos:** [USAGE.pt_BR.md](docs/USAGE.pt_BR.md) · [USAGE.md](docs/USAGE.md)
- **Deploy (Docker, Compose, Kubernetes):** [deploy/DEPLOY.pt_BR.md](docs/deploy/DEPLOY.pt_BR.md) · [deploy/DEPLOY.md](docs/deploy/DEPLOY.md)
- **Detecção de sensibilidade (termos ML/DL):** [SENSITIVITY_DETECTION.pt_BR.md](docs/SENSITIVITY_DETECTION.pt_BR.md) · [SENSITIVITY_DETECTION.md](docs/SENSITIVITY_DETECTION.md)
- **Testes, segurança, contribuição:** [docs/TESTING.pt_BR.md](docs/TESTING.pt_BR.md) · [SECURITY.pt_BR.md](SECURITY.pt_BR.md) · [CONTRIBUTING.pt_BR.md](CONTRIBUTING.pt_BR.md)

**Início rápido (na raiz do repositório):** Em **Linux nativo (sem Docker)**, instale as bibliotecas de sistema **antes** de `uv sync` — veja [Guia técnico — Requisitos e preparação do ambiente](docs/TECH_GUIDE.pt_BR.md#requisitos-e-preparação-do-ambiente) (o exemplo com `apt` inclui `libpq-dev`, `unixodbc-dev` e cabeçalhos relacionados; acrescente `default-libmysqlclient-dev` se for compilar **mysqlclient**). Depois `uv sync` → prepare `config.yaml` (veja `deploy/config.example.yaml` e [USAGE](docs/USAGE.pt_BR.md)) → `uv run python main.py --config config.yaml` para execução única, ou `uv run python main.py --config config.yaml --web --allow-insecure-http` para API/dashboard em HTTP texto plano (bind padrão `127.0.0.1`, ex. <http://127.0.0.1:8088/>; para TLS use `--https-cert-file` / `--https-key-file`; use `--host 0.0.0.0` só com controles de rede). Lista de flags: `uv run python main.py --help`. **Não commite** o `config.yaml` da raiz (`.gitignore`); pode conter caminhos da LAN e segredos—veja a seção **Higiene do repositório público** em [CONTRIBUTING.pt_BR.md](CONTRIBUTING.pt_BR.md).

**Índice completo da documentação** (todos os tópicos e idiomas): [docs/README.md](docs/README.md) · [docs/README.pt_BR.md](docs/README.pt_BR.md).

**Glossário** (termos e linguagem de domínio): [docs/GLOSSARY.pt_BR.md](docs/GLOSSARY.pt_BR.md) · [docs/GLOSSARY.md](docs/GLOSSARY.md).

**Licença e direitos autorais:** [LICENSE](LICENSE) · [NOTICE](NOTICE) · [docs/COPYRIGHT_AND_TRADEMARK.pt_BR.md](docs/COPYRIGHT_AND_TRADEMARK.pt_BR.md) ([EN](docs/COPYRIGHT_AND_TRADEMARK.md)).
