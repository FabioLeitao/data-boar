# Frameworks de compliance e extensibilidade

**English:** [COMPLIANCE_FRAMEWORKS.md](COMPLIANCE_FRAMEWORKS.md)

A aplicação auxilia times de DPO, segurança e compliance a descobrir e mapear dados pessoais ou sensíveis em linha com múltiplas regulamentações. Este documento descreve quais frameworks são referenciados explicitamente hoje, onde encontrar exemplos de configuração e como estender o suporte a outros (ex.: UK GDPR, PIPEDA, APPI, POPIA) sem alterar código.

## Regulamentações que já suportamos (embutidas e exemplos de config)

**Embutidas (prontas para uso):** O detector e os relatórios referenciam explicitamente **LGPD** (Brasil), **GDPR** (UE), **CCPA** (Califórnia), **HIPAA** (saúde EUA) e **GLBA** (financeiro EUA). Os achados usam essas norm tags e textos de recomendação por padrão.

**Exemplos de configuração:** Fornecemos exemplos de arquivos de config para alinhar a mais regulamentações sem mudar código:

- **[regex_overrides.example.yaml](regex_overrides.example.yaml)** – padrões regex customizados com `norm_tag` (ex.: LGPD Art. 5, CCPA). Copie e estenda para outros identificadores (ex.: NIN UK, SIN canadense) e defina `norm_tag` para seu framework.
- **Overrides de recomendação** – em [USAGE.pt_BR.md](USAGE.pt_BR.md) (seção de relatório) há `report.recommendation_overrides`: lista de `norm_tag_pattern`, `base_legal`, `risk`, `recommendation`, `priority`, `relevant_for`. Use para adaptar o texto do relatório a qualquer regulamentação (UK GDPR, PIPEDA, POPIA, APPI, PCI-DSS ou normas internas).
- **Termos ML/DL** – [SENSITIVITY_DETECTION.pt_BR.md](SENSITIVITY_DETECTION.pt_BR.md) e o config principal suportam `ml_patterns_file`, `dl_patterns_file` ou inline `sensitivity_detection.ml_terms` / `dl_terms` para adicionar termos por framework (ex.: “personal information”, “data subject”, “responsible party”) e melhorar detecção e rotulagem.

Amostras de config por regulamentação (UK GDPR, PIPEDA, POPIA, APPI, PCI-DSS) estão planejadas e serão documentadas da mesma forma. Até lá, você pode combinar os exemplos acima para obter compatibilidade com esses ou outros frameworks.

**Ajuda com ajuste fino:** Se sua organização precisar de **maior ou melhor compatibilidade** com uma regulamentação ou escopo de conformidade específico (ex.: VCDPA, CPA, regras setoriais), podemos ajudar—**criando arquivos de configuração sob medida** ou fazendo **pequenos ajustes no código**—quando você entrar em contato. Isso permite que potenciais clientes adotem a ferramenta para sua jurisdição ou expectativas de auditoria sem começar do zero.

## Referenciados explicitamente hoje (rótulos embutidos)

Os padrões regex embutidos e rótulos do relatório referem-se a estes frameworks (com valores de exemplo de `norm_tag`):

| Framework | Escopo                                      | Exemplo norm_tag (nos relatórios)   |
| --------- | ------------------------------------------- | ---------------------------------   |
| **LGPD**  | Brasil – Lei Geral de Proteção de Dados     | `LGPD Art. 5`                       |
| **GDPR**  | UE – General Data Protection Regulation     | `GDPR Art. 4(1)`                    |
| **CCPA**  | Califórnia – Consumer Privacy Act           | `CCPA`                              |
| **HIPAA** | EUA – Dados de saúde                        | Contexto saúde/seguros              |
| **GLBA**  | EUA – Serviços financeiros                  | `PCI/GLBA` (ex.: cartão de crédito) |

Os achados são armazenados com **`norm_tag`** e **`pattern_detected`** em formato livre; o relatório Excel os utiliza na aba **Recomendações** (Base legal, Risco, Recomendação, Prioridade, Relevante para).

## Extensibilidade

- **`norm_tag`** e **`pattern_detected`** são abertos: você pode defini-los para qualquer framework ou rótulo interno.
- **Overrides de regex:** Use [regex_overrides_file](SENSITIVITY_DETECTION.pt_BR.md) para adicionar padrões e definir `norm_tag` para ex. `"UK GDPR"`, `"PIPEDA s. 2"`, `"APPI"`, `"POPIA"` para que apareçam nos relatórios e recomendações.
- **Overrides de recomendação (config):** Use `report.recommendation_overrides` no config para personalizar "Base legal", "Relevante para" e demais textos de recomendação por padrão de `norm_tag` — assim UK GDPR, PIPEDA, APPI, POPIA ou normas customizadas recebem os rótulos e textos corretos sem mudar código. Veja [USAGE.pt_BR.md](USAGE.pt_BR.md) (seção de relatório) para um exemplo.
- **Conectores customizados:** Novas fontes de dados podem emitir achados com qualquer `norm_tag`; relatórios e recomendações usarão os overrides de config quando fornecidos, caso contrário os fallbacks embutidos.

Nenhuma alteração na lógica ou limiares do detector é necessária; a extensibilidade é via config e arquivos de override opcionais.

**Índice da documentação** (todos os tópicos, ambos os idiomas): [README.md](README.md) · [README.pt_BR.md](README.pt_BR.md). Para esquema de configuração e opções de relatório, veja [USAGE.pt_BR.md](USAGE.pt_BR.md) ([EN](USAGE.md)) e [TECH_GUIDE.pt_BR.md](TECH_GUIDE.pt_BR.md) ([EN](TECH_GUIDE.md)).
