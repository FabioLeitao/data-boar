# Detecção de sensibilidade: termos de treino ML e DL

A aplicação usa um pipeline **híbrido** para classificar nomes de colunas e conteúdo amostrado como sensível ou não:

1. **Regex** – Padrões embutidos (CPF, CNPJ, e-mail, telefone, SSN, cartão de crédito, datas) mais overrides opcionais via arquivo de config.
2. **ML** – TF-IDF + RandomForest treinado em uma lista de termos **(texto, rótulo)** (sensível vs não sensível). Os termos vêm de arquivo ou da config inline.
3. **DL (opcional)** – Embeddings de sentenças + um classificador pequeno treinado nos seus termos. Usado quando a dependência opcional `sentence-transformers` está instalada e você fornece termos DL (arquivo ou inline). A confiança é combinada com a do ML (ex.: `max(ml_confidence, dl_confidence)`).

Você pode **definir as palavras de treino para ML e DL** no arquivo de config principal (inline) ou em arquivos YAML/JSON separados.

**English:** [sensitivity-detection.md](sensitivity-detection.md)

**Detecção de dados de menores:** A aplicação pode sinalizar possíveis dados de menores (colunas de DOB/idade) e aplicar tratamento diferenciado nos relatórios (LGPD Art. 14, GDPR Art. 8). O limite de idade (padrão 18) é configurável no arquivo de config externo. Consulte [minor-detection.pt_BR.md](minor-detection.pt_BR.md) para configuração e ajuste fino.

---

## Chaves de config

| Chave | Descrição |
|-------|-----------|
| `ml_patterns_file` | Caminho para arquivo YAML/JSON com termos de treino ML (lista de `{ text, label }`). Usado quando `sensitivity_detection.ml_terms` não está definido. |
| `dl_patterns_file` | Caminho para arquivo YAML/JSON com termos de treino DL (mesmo formato). Usado quando `sensitivity_detection.dl_terms` não está definido. |
| `sensitivity_detection` | Seção opcional com termos inline (dispensa arquivo separado). |
| `sensitivity_detection.ml_terms` | Lista de `{ text: string, label: "sensitive" \| "non_sensitive" }`. Substitui/complementa `ml_patterns_file` quando não vazia. |
| `sensitivity_detection.dl_terms` | Lista de `{ text: string, label: "sensitive" \| "non_sensitive" }`. Substitui/complementa `dl_patterns_file` quando não vazia. |

**Valores de label:** `sensitive` ou `1` = sensível (dados pessoais/PII); `non_sensitive` ou `0` = não sensível.

---

## Formato do arquivo (YAML ou JSON)

Tanto `ml_patterns_file` quanto `dl_patterns_file` usam a mesma estrutura. Você pode apontar ambos para o mesmo arquivo se quiser que ML e DL usem os mesmos termos.

**Exemplo YAML:**

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

**Exemplo JSON:**

```json
[
  { "text": "cpf", "label": "sensitive" },
  { "text": "email", "label": "sensitive" },
  { "text": "item_count", "label": "non_sensitive" }
]
```

---

## Termos inline no config principal

Você pode definir os termos de treino ML e DL diretamente no seu `config.yaml` (ou JSON) principal, na seção `sensitivity_detection`, sem arquivos separados.

**Exemplo: termos ML e DL inline**

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

Para detectar **dados pessoais sensíveis adicionais** (LGPD Art. 5 II, 11; GDPR Art. 9)—como CID/ICD (códigos de diagnóstico), gênero, religião, filiação política, PEP, raça/cor da pele, filiação sindical, dados genéticos/biométricos, vida sexual, saúde/deficiência—adicione termos de treino dessas categorias à sua lista de termos ML/DL.

- **Plano e tabela de categorias:** [PLAN_SENSITIVE_CATEGORIES_ML_DL.md](PLAN_SENSITIVE_CATEGORIES_ML_DL.md)
- **Arquivo de exemplo pronto para uso:** [sensitivity_terms_sensitive_categories.example.yaml](sensitivity_terms_sensitive_categories.example.yaml)

Copie esse arquivo (ou mescle suas entradas) em `ml_patterns_file` / `dl_patterns_file`, ou em `sensitivity_detection.ml_terms` / `sensitivity_detection.dl_terms`. Você pode usar `report.recommendation_overrides` para que achados nessas categorias tenham a Base legal, Risco e Prioridade corretos no relatório (veja o plano para exemplos).

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

| Campo | Obrigatório | Descrição |
|-------|-------------|-----------|
| `name` | Sim | Identificador curto do padrão (ex.: `RG_BR`, `PLATE_BR`). Aparece nos relatórios como `pattern_detected`. |
| `pattern` | Sim | Expressão regular (sintaxe Python `re`). É aplicada ao nome da coluna + amostra. Use strings cruas; prefira `\b` para limites de palavra. |
| `norm_tag` | Não | Rótulo para conformidade/relatório (ex.: `LGPD Art. 5`, `Custom`). Padrão: `"Custom"`. Você pode definir qualquer rótulo de framework (ex.: "UK GDPR", "PIPEDA s. 2", "APPI", "POPIA") para os achados aparecerem sob essa norma nos relatórios e recomendações; veja [Frameworks de conformidade e extensibilidade](compliance-frameworks.pt_BR.md). |

Você pode usar uma lista na raiz ou uma chave `patterns` ou `regex` com a lista. Você pode copiar de [regex_overrides.example.yaml](regex_overrides.example.yaml) e editar.

**Exemplo YAML:**

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

**Exemplo JSON:**

```json
[
  { "name": "RG_BR", "pattern": "\\b\\d{1,2}\\.?\\d{3}\\.?\\d{3}-?[0-9Xx]\\b", "norm_tag": "LGPD Art. 5" },
  { "name": "PLATE_BR", "pattern": "\\b[A-Z]{3}-?\\d{4}\\b", "norm_tag": "Personal data context" }
]
```

### Padrões embutidos (referência)

A aplicação já inclui estes padrões; não é preciso redefini-los a menos que queira alterar o regex ou o norm tag.

| Nome | Descrição | Norm tag |
|------|-----------|----------|
| `LGPD_CPF` | CPF brasileiro (11 dígitos, opcional pontos/traço) | LGPD Art. 5 |
| `LGPD_CNPJ` | CNPJ brasileiro (14 dígitos, formatação opcional) | LGPD Art. 5 |
| `EMAIL` | Endereço de e-mail | GDPR Art. 4(1) |
| `CREDIT_CARD` | Cartão 16 dígitos (espaços/traços opcionais) | PCI/GLBA |
| `PHONE_BR` | Telefone BR (+55, DDD opcional) | LGPD Art. 5 |
| `CCPA_SSN` | SSN EUA (XXX-XX-XXXX) | CCPA |
| `DATE_DMY` | Data d/m/a (ex.: 31/12/2024) | Personal data context |

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

## Resumo

- **Termos ML:** De `sensitivity_detection.ml_terms` (inline) ou `ml_patterns_file`. Usados pelo classificador TF-IDF + RandomForest.
- **Termos DL:** De `sensitivity_detection.dl_terms` (inline) ou `dl_patterns_file`. Usados pelo opcional embedding + classificador quando `.[dl]` está instalado.
- **Mesmo formato:** Ambos usam uma lista de `{ text, label }` com `label` = `sensitive` ou `non_sensitive` (ou `1` / `0`).
- **Inline sobrescreve arquivo:** Quando `ml_terms` ou `dl_terms` estão preenchidos no config, eles são usados no lugar do carregamento do arquivo correspondente.

**Padrões regex:** Use `regex_overrides_file` no config principal para adicionar ou sobrescrever padrões de detecção por valor (veja [Padrões regex customizados](#padrões-regex-customizados-detectar-novos-dados-pessoaissensíveis) acima).
