# Conformidade e jurídico — resumo para equipes jurídicas e de conformidade

**English:** [COMPLIANCE_AND_LEGAL.md](COMPLIANCE_AND_LEGAL.md)

Este documento traz um resumo objetivo para **jurídico**, **conformidade** e **DPO**: o que a aplicação traz à tona, o que ela não faz, quais frameworks são suportados, onde está a evidência e onde encontrar detalhes técnicos e de segurança.

---

## O que trazemos à tona (e sob quais dispositivos)

- **Dados pessoais e sensíveis:** Detecção de PII (ex.: CPF, e-mail, telefone) e de **categorias sensíveis** sob **LGPD Art. 5 II** e **GDPR Art. 9** (saúde, religião, opinião política, biométrico, genético e afins).
- **Quasi-identificadores e risco de reidentificação:** Combinações que podem reidentificar pessoas, em linha com **LGPD Art. 5** e **GDPR Recital 26**.
- **Possíveis dados de menores:** Indicadores de dados relativos a menores, em linha com **LGPD Art. 14** e **GDPR Art. 8**.
- **Identificadores regionais e ambíguos:** Nomes regionais de documentos (ex.: carte bleue, carte vitale na França) e identificadores ambíguos (ex.: doc_id) sinalizados para confirmação manual.
- **Visibilidade multi-fonte:** Exposição em colunas legadas, exportações, dashboards e múltiplas fontes em uma visão; suporte a arquivos, SQL, NoSQL, APIs, Power BI, Dataverse, SharePoint, SMB/NFS e outros conectores (veja [TECH_GUIDE](TECH_GUIDE.pt_BR.md)).

---

## O que não fazemos

- **Não armazenamos nem exfiltramos PII:** A aplicação não armazena nem exfiltra *conteúdo* pessoal ou sensível. Ela retém apenas **metadados** (onde foi encontrado, tipo de padrão, nível de sensibilidade) para você obter visibilidade para maturidade e remediação sem mover nem copiar PII. Relatórios e heatmaps contêm achados e recomendações, não dados pessoais em bruto.

---

## Frameworks suportados e amostras de configuração

- **Integrados (prontos):** LGPD, GDPR, CCPA, HIPAA, GLBA (norm tags e texto de recomendação nos relatórios).
- **Amostras de config (prontas para uso):** UK GDPR, EU GDPR, Benelux, PIPEDA, POPIA, APPI, PCI-DSS e outros frameworks regionais (ex.: Filipinas, Austrália, Singapura, UAE, Argentina, Quênia, Índia, Turquia) estão em [compliance-samples/](compliance-samples/). Cada amostra é um arquivo YAML (padrões regex, termos ML, overrides de recomendação) para alinhar a um framework sem mudar código. Lista completa e uso: [COMPLIANCE_FRAMEWORKS.pt_BR.md](COMPLIANCE_FRAMEWORKS.pt_BR.md).

---

## Evidência e saídas

- **Relatórios Excel** por sessão de varredura: achados por alvo, coluna, tipo de padrão, nível de sensibilidade e texto de recomendação por framework (base legal, risco, recomendação, prioridade).
- **Heatmaps** e **tendências** entre sessões (esta execução vs anteriores) para evolução no tempo.
- Varreduras **agendáveis** via API interna para monitoramento contínuo; relatórios e heatmaps são o rastro de auditoria.

---

## Segurança, encodings e operação

- **Segurança:** Validação de entradas (ex.: tenant/technician), limite de tamanho do body (API) e política de logging (sem API keys, senhas ou connection strings nos logs). Veja [SECURITY.pt_BR.md](SECURITY.pt_BR.md) ([EN](SECURITY.md)).
- **Encodings e idiomas:** Config e arquivos de padrão suportam UTF-8 (recomendado), UTF-8 com BOM ou encodings legados (ex.: ANSI Windows, Latin-1); o config principal é lido com auto-detecção. Termos e relatórios podem seguir o idioma da sua região. Veja [USAGE.pt_BR.md](USAGE.pt_BR.md#file-encoding-config-and-pattern-files) ([EN](USAGE.md)).
- **Timeouts:** Timeouts configuráveis (global e por alvo) para uma fonte lenta não travar a execução.

---

## Ajuste fino e suporte

Se sua regulamentação ou escopo exigir ajuste específico (ex.: norm tags, texto de recomendação ou conjuntos de padrões customizados), podemos ajudar com configs sob medida ou pequenos ajustes no código. Entre em contato para discutir.

---

## Próximos passos

| Necessidade                                    | Documento                                                                                                               |
| -------------                                  | -----------                                                                                                             |
| Esquema de config, credenciais, exemplos       | [USAGE.pt_BR.md](USAGE.pt_BR.md) · [USAGE.md](USAGE.md)                                                                 |
| Lista de frameworks e como usar amostras       | [COMPLIANCE_FRAMEWORKS.pt_BR.md](COMPLIANCE_FRAMEWORKS.pt_BR.md) · [COMPLIANCE_FRAMEWORKS.md](COMPLIANCE_FRAMEWORKS.md) |
| Segurança (correções, logging, limite de body) | [SECURITY.pt_BR.md](SECURITY.pt_BR.md) · [SECURITY.md](SECURITY.md)                                                     |
| Instalação, execução, conectores, deploy       | [TECH_GUIDE.pt_BR.md](TECH_GUIDE.pt_BR.md) · [TECH_GUIDE.md](TECH_GUIDE.md)                                             |
| Índice completo da documentação                | [README.pt_BR.md](README.pt_BR.md) · [README.md](README.md)                                                             |
