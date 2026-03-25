# Amostras de conformidade

**English:** [README.md](README.md)

Arquivos de configuração de exemplo para habilitar **frameworks de conformidade adicionais** com o mesmo fluxo de varredura e relatório. Copie os blocos relevantes para seu config principal ou defina `regex_overrides_file` / `ml_patterns_file` e mescle os `report.recommendation_overrides` do sample. Para como usar e como cada framework mapeia para o config, veja [COMPLIANCE_FRAMEWORKS.md](../COMPLIANCE_FRAMEWORKS.md) ([pt-BR](../COMPLIANCE_FRAMEWORKS.pt_BR.md)).

## Arquivos de amostra (um por regulamento)

| Arquivo                                        | Finalidade                                                                                                                                                      |
| ---------                                      | ------------                                                                                                                                                    |
| **compliance-sample-lgpd.yaml**                | LGPD (Brasil): termos bilíngues PT-BR + EN (ex.: documento oficial / official document, RG, CNH / Driver License); regex RG/CEP; para implantações brasileiras. |
| **compliance-sample-uk_gdpr.yaml**             | UK GDPR (Reino Unido pós-Brexit + semelhante à UE): norm_tag e recommendation overrides alinhados à ICO e disposições britânicas.                               |
| **compliance-sample-eu_gdpr.yaml**             | EU GDPR (EEE): Art. 4(1) Reg. UE 2016/679, EDPB, autoridades nacionais; termos opcionais EN + DE/FR.                                                            |
| **compliance-sample-benelux.yaml**             | Benelux (BE, NL, LU): base EU GDPR + IDs nacionais (BSN, NISS, ID Luxemburgo) e overrides para DPAs nacionais; termos EN + NL/FR.                               |
| **compliance-sample-pipeda.yaml**              | PIPEDA (Canadá, setor privado federal): informação pessoal, consentimento e identificadores canadenses (ex.: SIN).                                              |
| **compliance-sample-popia.yaml**               | POPIA (África do Sul): responsável pelo tratamento, informação pessoal e identificadores sul-africanos.                                                         |
| **compliance-sample-appi.yaml**                | APPI (Japão): informação pessoal e dados pessoais retidos; termos e overrides alinhados à PPC.                                                                  |
| **compliance-sample-pci_dss.yaml**             | PCI-DSS (dados de cartão de pagamento): padrões de cartão/financeiro e recommendation overrides para comerciantes e avaliadores.                                |
| **compliance-sample-us_ftc_coppa.yaml**        | EUA FTC COPPA (privacidade online de crianças): termos e overrides de **mapeamento técnico**; sem verificação de idade nem aconselhamento jurídico.             |
| **compliance-sample-us_ca_ab2273_caadca.yaml** | Califórnia AB 2273 (Age-Appropriate Design): **rotulagem** para escopo voluntário; aplicabilidade exige assessoria jurídica.                                    |
| **compliance-sample-us_co_cpa_minors.yaml**    | Colorado CPA — contextos com menores de 18 anos: **norm tags técnicos**; não estabelece “menor conhecido” no sentido jurídico.                                  |

**Lista completa** de amostras por região: [COMPLIANCE_FRAMEWORKS.pt_BR.md](../COMPLIANCE_FRAMEWORKS.pt_BR.md#amostras-de-conformidade) ([EN](../COMPLIANCE_FRAMEWORKS.md#compliance-samples)). Cada amostra é autocontida (regex overrides, termos ML, recommendation overrides); novas regiões seguem o mesmo formato — veja [PLAN_ADDITIONAL_COMPLIANCE_SAMPLES.md](../plans/PLAN_ADDITIONAL_COMPLIANCE_SAMPLES.md).

### Idioma e público-alvo

Ao escolher ou criar uma amostra, considere o(s) **idioma(s)** da região alvo para que nomes de colunas e rótulos nos dados sejam detectados:

| Regulamento / região             | Idioma(s) recomendado(s) para termos e rótulos                                                           |
| --------------------             | ------------------------------------------------                                                         |
| **LGPD (Brasil)**                | Português (BR) e inglês (ex.: "documento oficial" e "official document", "CNH" e "Driver License").      |
| **PIPEDA (Canadá)**              | Inglês e francês (ex.: "personal information" e "renseignements personnels") ao varrer dados canadenses. |
| **UK GDPR**                      | Inglês.                                                                                                  |
| **EU GDPR (EEE)**                | Inglês; opcional alemão/francês para dados multilingues na UE.                                           |
| **Benelux (BE, NL, LU)**         | Inglês mais holandês e/ou francês (ex.: BSN, NISS, nomes de coluna de ID nacional).                      |
| **POPIA (África do Sul)**        | Inglês; adicione idiomas locais nos termos se seus dados usarem.                                         |
| **APPI (Japão)**                 | Japonês e/ou inglês conforme os nomes de colunas.                                                        |
| **PCI-DSS**                      | Inglês.                                                                                                  |
| **Filipinas (DPA)**              | Inglês.                                                                                                  |
| **Austrália / NZ**               | Inglês.                                                                                                  |
| **Singapura (PDPA)**             | Inglês.                                                                                                  |
| **UAE / Arábia Saudita (PDPL)**  | Inglês; opcional árabe para nomes de colunas.                                                            |
| **Argentina / Colômbia / Chile** | Espanhol e inglês (ex.: datos personales / personal data).                                               |
| **Quênia / Nigéria**             | Inglês.                                                                                                  |
| **Marrocos**                     | Francês e/ou árabe conforme relevante.                                                                   |
| **Índia (DPDP)**                 | Inglês.                                                                                                  |
| **Turquia (KVKK)**               | Turco e inglês (ex.: kişisel veri / personal data).                                                      |
| **Suíça (FADP)**                 | Inglês; opcional DE/FR/IT.                                                                               |
| **EUA (COPPA, AB 2273, CO CPA)** | Inglês (implantações e programas de privacidade nos EUA).                                                |

Documente no cabeçalho da amostra ou em [COMPLIANCE_FRAMEWORKS](../COMPLIANCE_FRAMEWORKS.pt_BR.md) quando uma amostra incluir termos em mais de um idioma. Veja também a regra **.cursor/rules/compliance-samples-language.mdc**.

**Para autores:** Use YAML em **aspas duplas** nos valores de `pattern` em regex com **barras invertidas escapadas** (ex.: `pattern: "\\b[A-Z]{2}\\s?\\d{6}\\s?[A-D]\\b"`). Isso evita erros de linter "Invalid escape sequence" e carrega corretamente; o valor passado ao motor de regex é `\b`, `\s`, `\d` como desejado. Não use aspas simples nem `\d`/`\s` sem escape em aspas duplas. Os testes em `tests/test_compliance_samples.py` validam a estrutura e que o detector carrega cada amostra.
