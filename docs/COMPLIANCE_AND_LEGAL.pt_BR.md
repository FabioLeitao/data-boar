# Conformidade e jurídico — resumo para liderança jurídica e de compliance

**English:** [COMPLIANCE_AND_LEGAL.md](COMPLIANCE_AND_LEGAL.md)

**Público principal:** **Jurídico**, **liderança de conformidade** e **DPOs** avaliando aderência, risco e evidências — **não** a **operação diária de TI** nem a parametrização técnica cotidiana. Para **YAML, limites de API, codificações e timeouts**, veja [COMPLIANCE_TECHNICAL_REFERENCE.pt_BR.md](COMPLIANCE_TECHNICAL_REFERENCE.pt_BR.md); para **config completa e comandos**, [USAGE.pt_BR.md](USAGE.pt_BR.md).

Esta página descreve **o que o Data Boar revela**, **o que não faz**, **com quais enquadramentos regulatórios** pode alinhar, **quais artefatos** apoiam auditoria, e como **serviços profissionais** ajudam a mapear a **sopa de dados** antes do produto **ingerir e digerir**.

---

## O que trazemos à tona (e sob quais dispositivos)

- **Dados pessoais e sensíveis:** Detecção de PII comum (ex.: CPF, e-mail, telefone) e **categorias especiais** no sentido da **LGPD art. 5º, II** e **GDPR art. 9** (saúde, religião, opinião política, biométrico, genético e afins).
- **Quasi-identificadores e risco de reidentificação:** Combinações que podem contribuir para identificar pessoas, em linha com **LGPD art. 5º** e **Recital 26 do GDPR**.
- **Possíveis dados relativos a menores:** Indicadores alinhados ao **LGPD art. 14** e **GDPR art. 8** (revisão humana pode ser necessária).
- **Identificadores regionais e ambíguos:** Rótulos específicos de documentos e campos ambíguos sinalizados para **confirmação manual** quando a automação não pode afirmar certeza.
- **Visibilidade multi-fonte:** Uma visão coerente da **sopa de dados** que a organização configurar—bancos, arquivos, APIs, sistemas de BI e colaboração e outros **conectores** descritos em alto nível em [COMPLIANCE_FRAMEWORKS.pt_BR.md](COMPLIANCE_FRAMEWORKS.pt_BR.md) e [TECH_GUIDE.pt_BR.md](TECH_GUIDE.pt_BR.md)—sem afirmar completude de todo legado até que os alvos estejam no escopo.
- **Triagem em arquivos e mídia:** O motor pode **amostrar contexto suficiente** em arquivos textuais para aplicar critério—reduzindo fadiga de alertas onde o conteúdo parece **entretenimento ou boilerplate**, mantendo **correspondências fortes por padrão** em destaque para remediação. Em alvos de arquivo, o tratamento **opcional** de mídia rica inclui **metadados** (ex.: EXIF, ID3, tags de container), **OCR opcional** em imagens e texto de **legendas** em arquivos sidecar quando configurado — dentro de limites de amostragem e dependências opcionais (veja [USAGE.pt_BR.md](USAGE.pt_BR.md) e [COMPLIANCE_TECHNICAL_REFERENCE.pt_BR.md](COMPLIANCE_TECHNICAL_REFERENCE.pt_BR.md)). **Esteganografia**, análise completa quadro a quadro de mídia, **heurísticas de rastreadores / web bugs** (incluindo padrões típicos de redes sociais e anúncios em material educacional de segurança) e detecção sistemática de **ocultação na camada de documento** (ex.: texto microscópico ou de baixo contraste, estrutura oculta, truques de Unicode, objetos embutidos muito aninhados) **não** são descritos como exaustivos hoje; ficam em **fases futuras opt-in** — veja [TECH_GUIDE.pt_BR.md](TECH_GUIDE.pt_BR.md) e [COMPLIANCE_TECHNICAL_REFERENCE.pt_BR.md](COMPLIANCE_TECHNICAL_REFERENCE.pt_BR.md) quanto ao que está disponível hoje — para manter relatórios proporcionados, limitar cópia de dados sensíveis e evitar CPU/I/O sem limite.

---

## O que não fazemos

- **Não armazenamos nem exfiltramos conteúdo de PII** para fins de relatório: a ferramenta retém **metadados** (local, tipo de padrão, nível de sensibilidade, tags de framework) para **visibilidade e remediação** sem copiar dados pessoais para outro repositório. As planilhas descrevem **achados e recomendações**, não campos pessoais em bruto.

---

## Alinhamento regulatório: embutido e por configuração

- **Já presentes em linguagem de detecção e relatórios:** **LGPD**, **GDPR**, **CCPA**, **HIPAA**, **GLBA** (referências de norma e texto de recomendação).
- **Outras jurisdições e políticas internas:** Muitos frameworks adicionais (ex. UK GDPR, PIPEDA, POPIA, APPI, PCI-DSS e perfis regionais) podem ser refletidos por **perfis de configuração**—ajustando conjuntos de padrões, rótulos e texto de relatório—**sem fork do produto**. O que “ajuste pequeno” significa na prática (arquivos, mesclagem) está documentado para times de implementação em [COMPLIANCE_FRAMEWORKS.pt_BR.md](COMPLIANCE_FRAMEWORKS.pt_BR.md). Itens de **roadmap** seguem ampliando cobertura ao longo do tempo.
- **Idiomas (resumo):** **Dados** já podem trazer muitos **scripts** nos achados e relatórios (**Unicode**); **localizações** do **dashboard** e da **documentação** para além de **inglês** e **português do Brasil** são **faseadas** conforme **demanda**, junto com **amostras regionais de compliance** quando fizer sentido — uma lista **não técnica** de **direção** (sem promessa de release) está no parágrafo **Roadmap — internacionalização** do [README.pt_BR.md](../README.pt_BR.md).

**EUA — privacidade de crianças e menores (apenas mapeamento técnico):** Amostras YAML opcionais apoiam trabalho de inventário **técnico** e **operacional** (ex.: revisão do DPO, preparação para auditoria ou delimitação de escopo com assessoria jurídica)—incluindo enquadramentos associados à **COPPA federal (regra FTC)**, à **Califórnia AB 2273** e às regras do **Colorado CPA** que afetam consumidores com menos de 18 anos. **Não** é aconselhamento jurídico, **não** é verificação de idade nem prova de consentimento parental e **não** determina se determinada lei se aplica. Nomes de arquivos e passos de mesclagem: [COMPLIANCE_FRAMEWORKS.pt_BR.md](COMPLIANCE_FRAMEWORKS.pt_BR.md) e [compliance-samples/](compliance-samples/).

---

## Evidência e saídas (para auditoria e governança)

- **Relatórios Excel** por **sessão** de varredura: achados por fonte, campo/caminho, tipo de padrão, sensibilidade e texto de recomendação orientado a framework (base legal, risco, ação sugerida, prioridade quando configurado).
- **Heatmaps** e **visões de tendência** entre sessões para mostrar **evolução**, não só um instantâneo.
- **Execuções repetíveis** (incluindo automação via API) para alinhar ao **modelo operacional**; detalhe técnico de agendamento e limites: [COMPLIANCE_TECHNICAL_REFERENCE.pt_BR.md](COMPLIANCE_TECHNICAL_REFERENCE.pt_BR.md).
- **Sinais ao operador (opcional, webhooks):** Com `notifications` habilitado na configuração, a aplicação pode enviar um **resumo curto** ao concluir uma varredura (ex.: Slack, Teams, Telegram ou URL genérica), inclusive **vários canais** ou **cópia ao tenant** quando configurado — **padrão desligado**; é conveniência operacional e **não substitui** os relatórios Excel nem constitui prova jurídica por si só. Detalhes: [USAGE.pt_BR.md — Notificações ao operador](USAGE.pt_BR.md#notificações-ao-operador-opcional).
- **Identidade de build e postura de runtime (operadores):** os relatórios registram a **versão da aplicação** na folha “Report info”; há plano para exibir de forma explícita **release vs desenvolvimento** e, opcionalmente, **sinais de integridade** para ambientes enterprise (sem alteração do alcance jurídico até implementar). Para **checagens operacionais** de implantação (não prova jurídica por si só), a API **`GET /status`** inclui um snapshot **`runtime_trust`** que resume se a configuração/ambiente em execução está aderente ao esperado (ex.: overrides locais inesperados).

---

## Serviços profissionais: mapear a sopa de dados

Raramente a organização tem um inventário único e limpo de cada **ingrediente** da **sopa de dados**—cópias sombra, exportações legadas, modelos de BI e compartilhamentos ad hoc são frequentes. O **Data Boar** **ingere e digere** o que você apontar; **descobrir e priorizar** fontes, **afinar** tags de norma e linguagem de recomendação e **alinhar** expectativa jurídica ao escopo técnico costuma ser exercício **conjunto**.

Há **serviços contratados** (consultoria e ajustes finos) para apoiar: escopo de alvos, alinhamento de configuração ao **mix regulatório** e redução do tempo até confiança operacional—**sem substituir** DPO ou assessoria jurídica. Limites comerciais e de licenciamento: [LICENSING_OPEN_CORE_AND_COMMERCIAL.md](LICENSING_OPEN_CORE_AND_COMMERCIAL.md). **Contato** pelos canais que já utiliza com o mantenedor (ex.: GitHub, e-mail profissional)—sem obrigação.

---

## Próximos passos

| Necessidade                                               | Documento                                                                                                                    |
| -----------                                               | ---------                                                                                                                    |
| **Resumo jurídico / compliance (esta página)**            | Você está aqui                                                                                                               |
| **TI: codificações, limites de API, timeouts, automação** | [COMPLIANCE_TECHNICAL_REFERENCE.pt_BR.md](COMPLIANCE_TECHNICAL_REFERENCE.pt_BR.md) ([EN](COMPLIANCE_TECHNICAL_REFERENCE.md)) |
| **Lista de frameworks e perfis de exemplo**               | [COMPLIANCE_FRAMEWORKS.pt_BR.md](COMPLIANCE_FRAMEWORKS.pt_BR.md) · [COMPLIANCE_FRAMEWORKS.md](COMPLIANCE_FRAMEWORKS.md)      |
| **Esquema de config, credenciais, CLI/API**               | [USAGE.pt_BR.md](USAGE.pt_BR.md) · [USAGE.md](USAGE.md)                                                                      |
| **Política de segurança**                                 | [SECURITY.pt_BR.md](SECURITY.pt_BR.md) · [SECURITY.md](SECURITY.md)                                                          |
| **Instalação, conectores, deploy**                        | [TECH_GUIDE.pt_BR.md](TECH_GUIDE.pt_BR.md) · [TECH_GUIDE.md](TECH_GUIDE.md)                                                  |
| **Glossário**                                             | [GLOSSARY.pt_BR.md](GLOSSARY.pt_BR.md) · [GLOSSARY.md](GLOSSARY.md)                                                          |
| **Índice completo da documentação**                       | [README.pt_BR.md](README.pt_BR.md) · [README.md](README.md)                                                                  |
