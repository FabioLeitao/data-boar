# Frameworks de compliance e extensibilidade

**English:** [COMPLIANCE_FRAMEWORKS.md](COMPLIANCE_FRAMEWORKS.md)

A aplicação auxilia times de DPO, segurança e compliance a descobrir e mapear dados pessoais ou sensíveis em linha com múltiplas regulamentações. Este documento descreve quais frameworks são referenciados explicitamente hoje, onde encontrar exemplos de configuração e como estender o suporte a outros (ex.: UK GDPR, PIPEDA, APPI, POPIA) sem alterar código.

## Regulamentações que já suportamos (embutidas e exemplos de config)

**Embutidas (prontas para uso):** O detector e os relatórios referenciam explicitamente **LGPD** (Brasil), **GDPR** (UE), **CCPA** (Califórnia), **HIPAA** (saúde EUA) e **GLBA** (financeiro EUA). Os achados usam essas norm tags e textos de recomendação por padrão.

**Exemplos de configuração:** Fornecemos exemplos de arquivos de config para alinhar a mais regulamentações sem mudar código:

- **[regex_overrides.example.yaml](regex_overrides.example.yaml)** – padrões regex customizados com `norm_tag` (ex.: LGPD Art. 5, CCPA). Copie e estenda para outros identificadores (ex.: NIN UK, SIN canadense) e defina `norm_tag` para seu framework.
- **Overrides de recomendação** – em [USAGE.pt_BR.md](USAGE.pt_BR.md) (seção de relatório) há `report.recommendation_overrides`: lista de `norm_tag_pattern`, `base_legal`, `risk`, `recommendation`, `priority`, `relevant_for`. Use para adaptar o texto do relatório a qualquer regulamentação (UK GDPR, PIPEDA, POPIA, APPI, PCI-DSS ou normas internas).
- **Termos ML/DL** – [SENSITIVITY_DETECTION.pt_BR.md](SENSITIVITY_DETECTION.pt_BR.md) e o config principal suportam `ml_patterns_file`, `dl_patterns_file` ou inline `sensitivity_detection.ml_terms` / `dl_terms` para adicionar termos por framework (ex.: “personal information”, “data subject”, “responsible party”) e melhorar detecção e rotulagem.

**Amostras de conformidade (um perfil por regulamento):** Amostras de config para **LGPD** (Brasil), **UK GDPR**, **PIPEDA**, **POPIA**, **APPI** e **PCI-DSS** estão em [compliance-samples/](compliance-samples/). Cada amostra é um único arquivo YAML com padrões regex, termos ML e recommendation overrides para esse framework. Use-as assim:

1. **Regex e termos ML:** Defina `regex_overrides_file` e `ml_patterns_file` no seu config principal com o caminho do arquivo da amostra (o mesmo arquivo pode ser usado para ambos; as amostras usam as chaves `regex` e `terms`).
1. **Recommendation overrides:** Copie a lista `recommendation_overrides` da amostra para o seu config em `report.recommendation_overrides` (mescle com overrides existentes, se houver).

**Amostras disponíveis:** [compliance-sample-lgpd.yaml](compliance-samples/compliance-sample-lgpd.yaml) – LGPD (Brasil); termos **bilíngues PT-BR + EN** (ex.: "documento oficial" / "official document", "CNH" / "Driver License") para implantações brasileiras. [compliance-sample-uk_gdpr.yaml](compliance-samples/compliance-sample-uk_gdpr.yaml) – UK GDPR (Reino Unido pós-Brexit, alinhado à ICO). Mais amostras (EU GDPR, Benelux, PIPEDA, POPIA, APPI, PCI-DSS e opcionais regionais) serão adicionadas no mesmo formato. Para **idioma e público-alvo** (ex.: PIPEDA → EN + FR no Canadá), veja o [README de compliance-samples](compliance-samples/README.pt_BR.md).

---

## Operação multilíngue, multi-encoding e multirregional {#operação-multilíngue-multi-encoding-e-multirregional}

Seja qual for o **idioma**, **encoding** ou **região** da sua sopa de dados, a aplicação foi pensada para lidar com isso: você pode rodar varreduras e relatórios de conformidade no idioma e encoding da sua região sem quebrar em produção.

### O que é suportado

- **Múltiplos idiomas em termos e relatórios:** As amostras de conformidade podem incluir termos no(s) idioma(s) da região alvo (ex.: EN+FR para PIPEDA/Canadá, PT-BR+EN para LGPD/Brasil, japonês ou árabe para APAC/MENA). O relatório Excel e o texto de recomendação suportam **Unicode** (ex.: base_legal e recommendation em japonês, árabe ou caracteres acentuados).
- **Múltiplos encodings para config e arquivos de padrões:** O **arquivo de config principal** é lido com **auto-detecção** (UTF-8, UTF-8 com BOM, ANSI Windows/cp1252, Latin-1), carregando mesmo quando salvo em encoding legado. Os **arquivos de padrões** (regex overrides, termos ML/DL) usam o encoding definido por **`pattern_files_encoding`** no seu config (padrão **`utf-8`**). Defina como `cp1252` ou `latin_1` apenas quando seus arquivos de padrões ou amostras estiverem salvos nesse encoding.
- **Múltiplas regiões:** Use a amostra de conformidade que corresponda à sua região ou regulamento (LGPD, UK GDPR, EU GDPR, Benelux, PIPEDA, POPIA, APPI, PCI-DSS ou amostras regionais opcionais). Cada amostra é um único arquivo YAML; você aponta o config para ela e mescla os recommendation overrides.

### Como habilitar e operar

1. **Escolha a amostra certa para sua região**
   Veja a tabela no [README de compliance-samples](compliance-samples/README.pt_BR.md) e a seção “Idioma e público-alvo”. Exemplos: Brasil → LGPD (PT-BR+EN); Canadá → PIPEDA (EN+FR); Reino Unido → UK GDPR; EEE → EU GDPR; Benelux → amostra Benelux; Japão → APPI; África do Sul → POPIA.

2. **Salve config e amostras em UTF-8 (recomendado)**
   Salvar tudo em **UTF-8** evita problemas de encoding com termos multilíngues. O config principal ainda será carregado se estiver em outro encoding (auto-detecção).

3. **Defina os caminhos e o encoding no config**
   No seu `config.yaml` (ou `config.json`) principal:

   ```yaml
   # Opcional: só se seus arquivos de padrões/amostras NÃO estiverem em UTF-8 (ex.: legado cp1252)
   pattern_files_encoding: utf-8

   regex_overrides_file: docs/compliance-samples/compliance-sample-pipeda.yaml
   ml_patterns_file: docs/compliance-samples/compliance-sample-pipeda.yaml
   ```

   Depois mescle os **`recommendation_overrides`** da amostra no seu config em `report.recommendation_overrides` (veja [USAGE.pt_BR](USAGE.pt_BR.md) seção de relatório).

4. **Execute a varredura**
   Use o CLI ou a API como de costume. Os achados usarão as norm tags e o texto de recomendação da amostra; o relatório Excel exibirá Unicode corretamente.

Para todas as opções de encoding e exemplos, veja [USAGE – File encoding](USAGE.md#file-encoding-config-and-pattern-files) (EN) e [USAGE.pt_BR – Encoding de arquivos](USAGE.pt_BR.md#file-encoding-config-and-pattern-files) (pt-BR).

---

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
