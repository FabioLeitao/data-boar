# Frameworks de compliance e extensibilidade

**English:** [compliance-frameworks.md](compliance-frameworks.md)

A aplicação auxilia times de DPO, segurança e compliance a descobrir e mapear dados pessoais ou sensíveis em linha com múltiplas regulamentações. Este documento descreve quais frameworks são referenciados explicitamente hoje e como estender o suporte a outros (ex.: UK GDPR, PIPEDA, APPI, POPIA) sem alterar código.

## Referenciados explicitamente hoje

Os padrões regex embutidos e rótulos do relatório referem-se a estes frameworks (com valores de exemplo de `norm_tag`):

| Framework | Escopo                                      | Exemplo norm_tag (nos relatórios) |
| --------- | ------------------------------------------- | --------------------------------- |
| **LGPD**  | Brasil – Lei Geral de Proteção de Dados     | `LGPD Art. 5`                     |
| **GDPR**  | UE – General Data Protection Regulation     | `GDPR Art. 4(1)`                  |
| **CCPA**  | Califórnia – Consumer Privacy Act           | `CCPA`                            |
| **HIPAA** | EUA – Dados de saúde                        | Contexto saúde/seguros            |
| **GLBA**  | EUA – Serviços financeiros                  | `PCI/GLBA` (ex.: cartão de crédito) |

Os achados são armazenados com **`norm_tag`** e **`pattern_detected`** em formato livre; o relatório Excel os utiliza na aba **Recomendações** (Base legal, Risco, Recomendação, Prioridade, Relevante para).

## Extensibilidade

- **`norm_tag`** e **`pattern_detected`** são abertos: você pode defini-los para qualquer framework ou rótulo interno.
- **Overrides de regex:** Use [regex_overrides_file](sensitivity-detection.pt_BR.md) para adicionar padrões e definir `norm_tag` para ex. `"UK GDPR"`, `"PIPEDA s. 2"`, `"APPI"`, `"POPIA"` para que apareçam nos relatórios e recomendações.
- **Overrides de recomendação (config):** Use `report.recommendation_overrides` no config para personalizar "Base legal", "Relevante para" e demais textos de recomendação por padrão de `norm_tag` — assim UK GDPR, PIPEDA, APPI, POPIA ou normas customizadas recebem os rótulos e textos corretos sem mudar código. Veja [USAGE.pt_BR.md](USAGE.pt_BR.md) (seção de relatório) para um exemplo.
- **Conectores customizados:** Novas fontes de dados podem emitir achados com qualquer `norm_tag`; relatórios e recomendações usarão os overrides de config quando fornecidos, caso contrário os fallbacks embutidos.

Nenhuma alteração na lógica ou limiares do detector é necessária; a extensibilidade é via config e arquivos de override opcionais.
