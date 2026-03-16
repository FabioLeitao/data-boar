# Detecção de sensibilidade: termos de treino ML e DL

A aplicação usa um pipeline **híbrido** para classificar nomes de colunas e conteúdo amostrado como sensível ou não:

1. **Regex** – Padrões embutidos (CPF, CNPJ, e-mail, telefone, SSN, cartão de crédito, datas) mais overrides opcionais via arquivo de config.
1. **ML** – TF-IDF + RandomForest treinado em uma lista de termos **(texto, rótulo)** (sensível vs não sensível). Os termos vêm de arquivo ou da config inline.
1. **DL (opcional)** – Embeddings de sentenças + um classificador pequeno treinado nos seus termos. Usado quando a dependência opcional `sentence-transformers` está instalada e você fornece termos DL (arquivo ou inline). A confiança é combinada com a do ML (ex.: `max(ml_confidence, dl_confidence)`).

Você pode **definir as palavras de treino para ML e DL** no arquivo de config principal (inline) ou em arquivos YAML/JSON separados.

**English:** [SENSITIVITY_DETECTION.md](SENSITIVITY_DETECTION.md)

**Detecção de dados de menores:** A aplicação pode sinalizar possíveis dados de menores (colunas de DOB/idade) e aplicar tratamento diferenciado nos relatórios (LGPD Art. 14, GDPR Art. 8). O limite de idade (padrão 18) é configurável no arquivo de config externo. Consulte [MINOR_DETECTION.pt_BR.md](MINOR_DETECTION.pt_BR.md) para configuração e ajuste fino.

**Risco de identificação agregada / cruzada:** Quando várias categorias de quasi-identificadores (ex.: gênero, cargo, saúde, endereço, telefone) aparecem na **mesma tabela ou arquivo**, o gerador de relatório sinaliza isso como **caso especial** para DPO e compliance (LGPD Art. 5, GDPR Recital 26 – identificabilidade pela combinação de dados). O relatório Excel inclui a aba **"Cross-ref data – ident. risk"** listando cada caso (alvo, tabela/arquivo, colunas envolvidas, categorias, explicação) e uma recomendação de alta prioridade. Isso é opcional e configurável via `detection.aggregated_identification_enabled`, `aggregated_min_categories` e `quasi_identifier_mapping`. Consulte [PLAN_AGGREGATED_IDENTIFICATION.md](completed/PLAN_AGGREGATED_IDENTIFICATION.md) para o desenho e detalhes de config.

---

## Formatos de CNPJ (Brasil): numérico legado e alfanumérico

O **CNPJ** brasileiro (identificador de pessoa jurídica) usou historicamente um formato **apenas numérico**:

- 14 dígitos, opcionalmente formatados como `XX.XXX.XXX/XXXX-XX` (pontos, barra, hífen).

O projeto agora reconhece **ambos**:

- `LGPD_CNPJ` – formato legado, apenas numérico.
- `LGPD_CNPJ_ALNUM` – formato **alfanumérico** em que as 12 primeiras posições podem conter `A–Z` ou `0–9`, e as duas últimas posições permanecem como dígitos (check digits).

Ambos os padrões usam o mesmo `norm_tag` (`LGPD Art. 5`), portanto são tratados como identificadores sob a LGPD. Nesta etapa, o detector faz apenas **verificação de compatibilidade de formato** (regex); a **validação de dígito verificador** para CNPJ (numérico ou alfanumérico) e outros identificadores brasileiros (ex.: CPF, PIS/PASEP) é deixada propositalmente para uma **fase futura na lógica do detector**, para manter a camada de regex simples e fácil de estender.

## Chaves de config

| Chave                            | Descrição                                                                                                                                             |                                                                                |
| ---                              | ---                                                                                                                                                   |                                                                                |
| `ml_patterns_file`               | Caminho para arquivo YAML/JSON com termos de treino ML (lista de `{ text, label }`). Usado quando `sensitivity_detection.ml_terms` não está definido. |                                                                                |
| `dl_patterns_file`               | Caminho para arquivo YAML/JSON com termos de treino DL (mesmo formato). Usado quando `sensitivity_detection.dl_terms` não está definido.              |                                                                                |
| `sensitivity_detection`          | Seção opcional com termos inline (dispensa arquivo separado).                                                                                         |                                                                                |
| `sensitivity_detection.ml_terms` | Lista de `{ text: string, label: "sensitive" \                                                                                                        | "non_sensitive" }`. Substitui/complementa `ml_patterns_file` quando não vazia. |
| `sensitivity_detection.dl_terms` | Lista de `{ text: string, label: "sensitive" \                                                                                                        | "non_sensitive" }`. Substitui/complementa `dl_patterns_file` quando não vazia. |

**Valores de label:** `sensitive` ou `1` = sensível (dados pessoais/PII); `non_sensitive` ou `0` = não sensível.

---

## Formato do arquivo (YAML ou JSON)

Tanto `ml_patterns_file` quanto `dl_patterns_file` usam a mesma estrutura. Você pode apontar ambos para o mesmo arquivo se quiser que ML e DL usem os mesmos termos.

## Exemplo YAML

```yaml
# Lista de termos; cada um tem "text" e "label"
- text: "cpf"

  label: sensitive

- text: "email"

  label: sensitive

- text: "data de nascimento"

  label: sensitive

- text: "senha"

  label: sensitive

- text: "item_count"

  label: non_sensitive

- text: "config_file"

  label: non_sensitive
```

**Chave alternativa:** alguns configs usam `patterns` ou `terms` como chave raiz:

```yaml
patterns:

- text: "cpf"

    label: sensitive

- text: "email"

    label: sensitive

- text: "system_log"

    label: non_sensitive
```

## Exemplo JSON

```json
[
  { "text": "cpf", "label": "sensitive" },
  { "text": "email", "label": "sensitive" },
  { "text": "item_count", "label": "non_sensitive" }
]
```

---

## Identificação agregada: configuração e exemplos

Quando a **identificação agregada** está habilitada, o gerador de relatório agrupa achados por tabela (banco) ou arquivo (sistema de arquivos) e sinaliza casos em que **várias categorias de quasi-identificadores** (ex.: gênero, cargo, saúde, endereço, telefone) aparecem juntas, o que pode permitir reidentificação (LGPD Art. 5, GDPR Recital 26). O relatório Excel ganha a aba **"Cross-ref data – ident. risk"** e uma recomendação de alta prioridade.

| Chave                                         | Tipo    | Padrão   | Descrição                                                                                                                                                                                                                                                                                             |
| ---                                           | ---     | ---      | ---                                                                                                                                                                                                                                                                                                   |
| `detection.aggregated_identification_enabled` | boolean | **true** | Defina como `false` para desativar a agregação e a aba Cross-ref.                                                                                                                                                                                                                                     |
| `detection.aggregated_min_categories`         | inteiro | **2**    | Número mínimo de categorias distintas de quasi-identificadores em uma tabela/arquivo para sinalizar (ex.: 3 para mais rigor).                                                                                                                                                                         |
| `detection.quasi_identifier_mapping`          | lista   | **[]**   | Lista opcional de `{ column_pattern, category }` ou `{ pattern_detected, category }` para mapear colunas/padrões para `gender`, `job_position`, `health`, `address`, `phone`, `other`. Já existem mapeamentos padrão para nomes comuns (ex.: gender, sex, cargo, department, health, address, phone). |

## Exemplo: habilitar com mapeamento customizado e mínimo de 3 categorias

```yaml
# config.yaml
targets: []
report:
  output_dir: ./reports
detection:
  aggregated_identification_enabled: true
  aggregated_min_categories: 3
  quasi_identifier_mapping:

    - { column_pattern: "cargo", category: job_position }
    - { column_pattern: "departamento", category: job_position }
    - { pattern_detected: "PHONE_BR", category: phone }
    - { pattern_detected: "EMAIL", category: other }

```

**Como usar:** Execute um scan (CLI: `python main.py --config config.yaml` ou API: iniciar scan pelo dashboard). Em seguida gere o relatório (CLI: o relatório é gerado ao final do scan; API: baixe pela sessão). Se alguma tabela ou arquivo tiver pelo menos `aggregated_min_categories` categorias presentes, o relatório incluirá a aba **"Cross-ref data – ident. risk"** e uma linha de recomendação **AGGREGATED_IDENTIFICATION**.

**Para desativar:** Defina `detection.aggregated_identification_enabled: false` no config; a aba Cross-ref e a recomendação agregada não serão geradas.

---

## Termos inline no config principal

Você pode definir os termos de treino ML e DL diretamente no seu `config.yaml` (ou JSON) principal, na seção `sensitivity_detection`, sem arquivos separados.

## Exemplo: termos ML e DL inline

```yaml
# config.yaml
targets: []
file_scan:
  extensions: [.txt, .csv, .pdf]
  recursive: true
report:
  output_dir: .

# Termos de treino para sensibilidade (ML = TF-IDF + RandomForest; DL = embeddings + classificador quando .[dl] instalado)
sensitivity_detection:
  ml_terms:

    - { text: "cpf", label: sensitive }
    - { text: "email", label: sensitive }
    - { text: "senha", label: sensitive }
    - { text: "data de nascimento", label: sensitive }
    - { text: "item_count", label: non_sensitive }
    - { text: "system_log", label: non_sensitive }

  dl_terms:

    - { text: "customer name", label: sensitive }
    - { text: "health record", label: sensitive }
    - { text: "salary", label: sensitive }
    - { text: "internal id", label: non_sensitive }
    - { text: "cache key", label: non_sensitive }

```

Se você definir **apenas** `ml_terms` (ou apenas `dl_terms`), o outro continua usando arquivo ou padrões embutidos: o ML usa `ml_patterns_file` ou termos embutidos quando `ml_terms` está vazio; o DL só é usado quando `dl_terms` ou `dl_patterns_file` é fornecido e o pacote opcional `sentence-transformers` está instalado.

---

## Usando apenas arquivos (sem inline)

```yaml
# config.yaml
ml_patterns_file: config/ml_terms.yaml
dl_patterns_file: config/dl_terms.yaml
# ... resto do config
```

Ou use o mesmo arquivo para os dois:

```yaml
ml_patterns_file: config/sensitivity_terms.yaml
dl_patterns_file: config/sensitivity_terms.yaml
```

---

## Habilitando o backend DL

A etapa DL usa **embeddings de sentenças** (ex.: `sentence-transformers/all-MiniLM-L6-v2`) e treina um classificador pequeno nos seus termos DL na inicialização. Instale a dependência opcional:

```bash
uv pip install -e ".[dl]"
# ou
pip install -e ".[dl]"
```

Isso instala o `sentence-transformers` (e suas dependências). Se `.[dl]` não estiver instalado, o pipeline continua rodando com **regex + ML**; a etapa DL é ignorada e a confiança vem apenas do ML.

---

## Exemplo: arquivo de termos compartilhado

Crie por exemplo `config/sensitivity_terms.yaml` (ou copie de [sensitivity_terms.example.yaml](sensitivity_terms.example.yaml)):

```yaml

- text: "cpf"

  label: sensitive

- text: "cnpj"

  label: sensitive

- text: "email"

  label: sensitive

- text: "telefone"

  label: sensitive

- text: "data de nascimento"

  label: sensitive

- text: "nome completo"

  label: sensitive

- text: "senha"

  label: sensitive

- text: "salário"

  label: sensitive

- text: "health record"

  label: sensitive

- text: "item_count"

  label: non_sensitive

- text: "config_file"

  label: non_sensitive

- text: "temp_data"

  label: non_sensitive

- text: "lyrics"

  label: non_sensitive

- text: "tablature"

  label: non_sensitive
```

Referencie no config:

```yaml
ml_patterns_file: config/sensitivity_terms.yaml
dl_patterns_file: config/sensitivity_terms.yaml
```

---

## Categorias sensíveis (saúde, religião, política, etc.)

A aplicação já inclui um **subconjunto** dessas categorias nos termos ML de fábrica (DEFAULT_ML_TERMS em `core/detector.py`), de modo que a detecção imediata inclui, por exemplo, religião, filiação política, gênero, biométrico, genético, raça, sindicato, PEP e vida sexual. Para detectar **mais dados pessoais sensíveis** (LGPD Art. 5 II, 11; GDPR Art. 9)—como CID/ICD (códigos de diagnóstico), gênero, religião, filiação política, PEP, raça/cor da pele, filiação sindical, dados genéticos/biométricos, vida sexual, saúde/deficiência—adicione ou estenda termos de treino via `ml_patterns_file` / `dl_patterns_file` ou `sensitivity_detection.ml_terms` / `sensitivity_detection.dl_terms`.

- **Plano e tabela de categorias:** [PLAN_SENSITIVE_CATEGORIES_ML_DL.md](completed/PLAN_SENSITIVE_CATEGORIES_ML_DL.md)
- **Arquivo de exemplo pronto para uso:** [sensitivity_terms_sensitive_categories.example.yaml](sensitivity_terms_sensitive_categories.example.yaml)

Copie esse arquivo (ou mescle suas entradas) em `ml_patterns_file` / `dl_patterns_file`, ou em `sensitivity_detection.ml_terms` / `sensitivity_detection.dl_terms`. Você pode usar `report.recommendation_overrides` para que achados nessas categorias tenham a Base legal, Risco e Prioridade corretos no relatório. Exemplo completo (saúde, religião, política, PEP, raça, sindicato, genético, biométrico, vida sexual) em [USAGE.pt_BR.md](USAGE.pt_BR.md) (Notas sobre configuração); [USAGE.md](USAGE.md) (English).

---

## Padrões regex customizados (detectar novos dados pessoais/sensíveis)

O detector aplica **padrões regex** ao texto combinado (nome da coluna + amostra do conteúdo). Os padrões embutidos cobrem CPF, CNPJ, e-mail, telefone, SSN, cartão de crédito e datas. Para que a aplicação se atente a **novos valores possivelmente pessoais ou sensíveis** (ex.: RG, placa de veículo, número de plano de saúde, outros IDs por país), você adiciona **padrões customizados** via um arquivo e aponta o config para ele.

### Onde configurar

No arquivo de config principal (`config.yaml` ou JSON), defina a chave **`regex_overrides_file`** com o caminho de um arquivo YAML ou JSON que lista seus padrões. O caminho pode ser absoluto ou relativo ao diretório de trabalho do processo. A aplicação carrega esse arquivo na inicialização e **mescla** seus padrões aos embutidos (nomes iguais aos embutidos são sobrescritos pelos seus).

```yaml
# config.yaml
regex_overrides_file: config/regex_overrides.yaml
# ... resto do config (targets, file_scan, report, etc.)
```

Se `regex_overrides_file` for omitido ou o arquivo não existir, apenas os padrões embutidos são usados.

### Formato do arquivo

O arquivo deve conter uma **lista de objetos**, cada um com:

| Campo      | Obrigatório | Descrição                                                                                                                                                                                                                                                                                                                                             |
| ---        | ---         | ---                                                                                                                                                                                                                                                                                                                                                   |
| `name`     | Sim         | Identificador curto do padrão (ex.: `RG_BR`, `PLATE_BR`). Aparece nos relatórios como `pattern_detected`.                                                                                                                                                                                                                                             |
| `pattern`  | Sim         | Expressão regular (sintaxe Python `re`). É aplicada ao nome da coluna + amostra. Use strings cruas; prefira `\b` para limites de palavra.                                                                                                                                                                                                             |
| `norm_tag` | Não         | Rótulo para conformidade/relatório (ex.: `LGPD Art. 5`, `Custom`). Padrão: `"Custom"`. Você pode definir qualquer rótulo de framework (ex.: "UK GDPR", "PIPEDA s. 2", "APPI", "POPIA") para os achados aparecerem sob essa norma nos relatórios e recomendações; veja [Frameworks de conformidade e extensibilidade](COMPLIANCE_FRAMEWORKS.pt_BR.md). |

Você pode usar uma lista na raiz ou uma chave `patterns` ou `regex` com a lista. Você pode copiar de [regex_overrides.example.yaml](regex_overrides.example.yaml) e editar. Use YAML em **aspas duplas** para os valores de `pattern` com **barras invertidas escapadas** (ex.: `"\\b\\d{5}"`) para que linters e loaders não reportem sequências de escape inválidas; veja `.cursor/rules/yaml-regex-patterns.mdc`.

## Exemplo YAML (regex overrides)

```yaml
# config/regex_overrides.yaml
- name: "RG_BR"

  pattern: "\b\d{1,2}\.?\d{3}\.?\d{3}-?[0-9Xx]\b"
  norm_tag: "LGPD Art. 5"

- name: "PLATE_BR"

  pattern: "\b[A-Z]{3}-?\d{4}\b"
  norm_tag: "Personal data context"

- name: "HEALTH_PLAN_ID"

  pattern: "\b\d{6,14}\b"
  norm_tag: "Health/insurance context"
```

## Exemplo JSON (regex overrides)

```json
[
  { "name": "RG_BR", "pattern": "\\b\\d{1,2}\\.?\\d{3}\\.?\\d{3}-?[0-9Xx]\\b", "norm_tag": "LGPD Art. 5" },
  { "name": "PLATE_BR", "pattern": "\\b[A-Z]{3}-?\\d{4}\\b", "norm_tag": "Personal data context" }
]
```

### Padrões embutidos (referência)

A aplicação já inclui estes padrões; não é preciso redefini-los a menos que queira alterar o regex ou o norm tag.

| Nome          | Descrição                                          | Norm tag              |
| ---           | ---                                                | ---                   |
| `LGPD_CPF`    | CPF brasileiro (11 dígitos, opcional pontos/traço) | LGPD Art. 5           |
| `LGPD_CNPJ`   | CNPJ brasileiro (14 dígitos, formatação opcional)  | LGPD Art. 5           |
| `EMAIL`       | Endereço de e-mail                                 | GDPR Art. 4(1)        |
| `CREDIT_CARD` | Cartão 16 dígitos (espaços/traços opcionais)       | PCI/GLBA              |
| `PHONE_BR`    | Telefone BR (+55, DDD opcional)                    | LGPD Art. 5           |
| `CCPA_SSN`    | SSN EUA (XXX-XX-XXXX)                              | CCPA                  |
| `DATE_DMY`    | Data d/m/a (ex.: 31/12/2024)                       | Personal data context |

### Exemplos de padrões adicionais úteis

- **RG (Brasil):** formato varia por estado; uma forma comum é dígitos com pontos opcionais e dígito ou X no final:

  `\b\d{1,2}\.?\d{3}\.?\d{3}-?[0-9Xx]\b`

- **Placa de veículo Brasil (antiga):** `AAA-9999`:

  `\b[A-Z]{3}-?\d{4}\b`

- **Placa Mercosul:** `AAA9A99`:

  `\b[A-Z]{3}\d[A-Z]\d{2}\b`

- **ID numérico genérico (ex. plano de saúde):** cuidado com o tamanho para evitar falsos positivos; ex. 8–14 dígitos:

  `\b\d{8,14}\b` (use só quando o contexto for adequado; combine com ML/DL se possível).

- **Telefone EUA:** `(XXX) XXX-XXXX` ou `XXX-XXX-XXXX`:

  `\b\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b`

- **CEP (Brasil):** `99999-999`:

  `\b\d{5}-?\d{3}\b`

Quando um padrão customizado der match no nome da coluna ou no texto amostrado, o achado é reportado com sensibilidade **HIGH** (ou MEDIUM em contexto de letras/cifras para padrões fracos), com `pattern_detected` igual ao seu `name` e `norm_tag` no relatório.

### Resumo

- **Configurar:** Defina `regex_overrides_file` no config principal com o caminho do seu arquivo YAML/JSON.
- **Formato:** Lista de `{ name, pattern, norm_tag }`; `norm_tag` opcional (padrão `"Custom"`).
- **Efeito:** Seus padrões são mesclados aos embutidos; qualquer match em (nome da coluna + amostra) é sinalizado. Use padrões precisos e limites de palavra para reduzir falsos positivos.
- **ML/DL:** Para contexto (ex.: “este nome de coluna sugere PII”), use os [termos de treino ML/DL](#config-keys) além do regex.

---

## Resumo do documento

- **Termos ML:** De `sensitivity_detection.ml_terms` (inline) ou `ml_patterns_file`. Usados pelo classificador TF-IDF + RandomForest.
- **Termos DL:** De `sensitivity_detection.dl_terms` (inline) ou `dl_patterns_file`. Usados pelo opcional embedding + classificador quando `.[dl]` está instalado.
- **Mesmo formato:** Ambos usam uma lista de `{ text, label }` com `label` = `sensitive` ou `non_sensitive` (ou `1` / `0`).
- **Inline sobrescreve arquivo:** Quando `ml_terms` ou `dl_terms` estão preenchidos no config, eles são usados no lugar do carregamento do arquivo correspondente.

**Padrões regex:** Use `regex_overrides_file` no config principal para adicionar ou sobrescrever padrões de detecção por valor (veja [Padrões regex customizados](#padrões-regex-customizados-detectar-novos-dados-pessoaissensíveis) acima).

**Índice da documentação** (todos os tópicos, ambos os idiomas): [README.md](README.md) · [README.pt_BR.md](README.pt_BR.md).
