# Conformidade e jurídico — resumo para liderança jurídica e de compliance

**English:** [COMPLIANCE_AND_LEGAL.md](COMPLIANCE_AND_LEGAL.md)

**Público principal:** **Jurídico**, **liderança de conformidade** e **DPOs** avaliando aderência, risco e evidências—not **operação diária de TI**. Para **YAML, limites de API, codificações e timeouts**, veja [COMPLIANCE_TECHNICAL_REFERENCE.pt_BR.md](COMPLIANCE_TECHNICAL_REFERENCE.pt_BR.md); para **config completa e comandos**, [USAGE.pt_BR.md](USAGE.pt_BR.md).

Esta página descreve **o que o Data Boar revela**, **o que não faz**, **com quais enquadramentos regulatórios** pode alinhar, **quais artefatos** apoiam auditoria, e como **serviços profissionais** ajudam a mapear a **sopa de dados** antes do produto **ingerir e digerir**.

---

## O que trazemos à tona (e sob quais dispositivos)

- **Dados pessoais e sensíveis:** Detecção de PII comum (ex.: CPF, e-mail, telefone) e **categorias especiais** no sentido da **LGPD art. 5º, II** e **GDPR art. 9** (saúde, religião, opinião política, biométrico, genético e afins).
- **Quasi-identificadores e risco de reidentificação:** Combinações que podem contribuir para identificar pessoas, em linha com **LGPD art. 5º** e **Recital 26 do GDPR**.
- **Possíveis dados relativos a menores:** Indicadores alinhados ao **LGPD art. 14** e **GDPR art. 8** (revisão humana pode ser necessária).
- **Identificadores regionais e ambíguos:** Rótulos específicos de documentos e campos ambíguos sinalizados para **confirmação manual** quando a automação não pode afirmar certeza.
- **Visibilidade multi-fonte:** Uma visão coerente da **sopa de dados** que a organização configurar—bancos, arquivos, APIs, sistemas de BI e colaboração e outros **conectores** descritos em alto nível em [COMPLIANCE_FRAMEWORKS.pt_BR.md](COMPLIANCE_FRAMEWORKS.pt_BR.md) e [TECH_GUIDE.pt_BR.md](TECH_GUIDE.pt_BR.md)—sem afirmar completude de todo legado até que os alvos estejam no escopo.
- **Disciplina de triagem em arquivos:** O motor pode **amostrar contexto suficiente** em arquivos textuais para aplicar critério—reduzindo fadiga de alertas onde o conteúdo parece **entretenimento ou boilerplate**, mantendo **correspondências fortes por padrão** em destaque para remediação. Há **roadmap** para metadados de **imagem, áudio e vídeo** (e OCR opcional) documentado para organizações cuja sopa inclui mídia rica; conectores de **RH/SST e sistemas de back-office** (SAP, ERP/CRM/folha) estão em [PLAN_ENTERPRISE_HR_SST_ERP_CONNECTORS.md](plans/PLAN_ENTERPRISE_HR_SST_ERP_CONNECTORS.md) e [PLAN_SAP_CONNECTOR.md](plans/PLAN_SAP_CONNECTOR.md).

---

## O que não fazemos

- **Não armazenamos nem exfiltramos conteúdo de PII** para fins de relatório: a ferramenta retém **metadados** (local, tipo de padrão, nível de sensibilidade, tags de framework) para **visibilidade e remediação** sem copiar dados pessoais para outro repositório. As planilhas descrevem **achados e recomendações**, não campos pessoais em bruto.

---

## Alinhamento regulatório: embutido e por configuração

- **Já presentes em linguagem de detecção e relatórios:** **LGPD**, **GDPR**, **CCPA**, **HIPAA**, **GLBA** (referências de norma e texto de recomendação).
- **Outras jurisdições e políticas internas:** Muitos frameworks adicionais (ex. UK GDPR, PIPEDA, POPIA, APPI, PCI-DSS e perfis regionais) podem ser refletidos por **perfis de configuração**—ajustando conjuntos de padrões, rótulos e texto de relatório—**sem fork do produto**. O que “ajuste pequeno” significa na prática (arquivos, mesclagem) está documentado para times de implementação em [COMPLIANCE_FRAMEWORKS.pt_BR.md](COMPLIANCE_FRAMEWORKS.pt_BR.md). Itens de **roadmap** podem ampliar cobertura; veja [PLANS_TODO.md](plans/PLANS_TODO.md).

---

## Evidência e saídas (para auditoria e governança)

- **Relatórios Excel** por **sessão** de varredura: achados por fonte, campo/caminho, tipo de padrão, sensibilidade e texto de recomendação orientado a framework (base legal, risco, ação sugerida, prioridade quando configurado).
- **Heatmaps** e **visões de tendência** entre sessões para mostrar **evolução**, não só um instantâneo.
- **Execuções repetíveis** (incluindo automação via API) para alinhar ao **modelo operacional**; detalhe técnico de agendamento e limites: [COMPLIANCE_TECHNICAL_REFERENCE.pt_BR.md](COMPLIANCE_TECHNICAL_REFERENCE.pt_BR.md).

---

## Serviços profissionais: mapear a sopa de dados

Raramente a organização tem um inventário único e limpo de cada **ingrediente** da **sopa de dados**—cópias sombra, exportações legadas, modelos de BI e compartilhamentos ad hoc são frequentes. O **Data Boar** **ingere e digere** o que você apontar; **descobrir e priorizar** fontes, **afinar** tags de norma e linguagem de recomendação e **alinhar** expectativa jurídica ao escopo técnico costuma ser exercício **conjunto**.

Há **serviços contratados** (consultoria e ajustes finos) para apoiar: escopo de alvos, alinhamento de configuração ao **mix regulatório** e redução do tempo até confiança operacional—**sem substituir** DPO ou assessoria jurídica. Limites comerciais e de licenciamento: [LICENSING_OPEN_CORE_AND_COMMERCIAL.md](LICENSING_OPEN_CORE_AND_COMMERCIAL.md). **Contato** pelos canais que já utiliza com o mantenedor (ex.: GitHub, e-mail profissional)—sem obrigação.

---

## Próximos passos

| Necessidade | Documento |
| ----------- | --------- |
| **Resumo jurídico / compliance (esta página)** | Você está aqui |
| **TI: codificações, limites de API, timeouts, automação** | [COMPLIANCE_TECHNICAL_REFERENCE.pt_BR.md](COMPLIANCE_TECHNICAL_REFERENCE.pt_BR.md) ([EN](COMPLIANCE_TECHNICAL_REFERENCE.md)) |
| **Lista de frameworks e perfis de exemplo** | [COMPLIANCE_FRAMEWORKS.pt_BR.md](COMPLIANCE_FRAMEWORKS.pt_BR.md) · [COMPLIANCE_FRAMEWORKS.md](COMPLIANCE_FRAMEWORKS.md) |
| **Esquema de config, credenciais, CLI/API** | [USAGE.pt_BR.md](USAGE.pt_BR.md) · [USAGE.md](USAGE.md) |
| **Política de segurança** | [SECURITY.pt_BR.md](SECURITY.pt_BR.md) · [SECURITY.md](SECURITY.md) |
| **Instalação, conectores, deploy** | [TECH_GUIDE.pt_BR.md](TECH_GUIDE.pt_BR.md) · [TECH_GUIDE.md](TECH_GUIDE.md) |
| **Glossário** | [GLOSSARY.pt_BR.md](GLOSSARY.pt_BR.md) · [GLOSSARY.md](GLOSSARY.md) |
| **Índice completo da documentação** | [README.pt_BR.md](README.pt_BR.md) · [README.md](README.md) |
