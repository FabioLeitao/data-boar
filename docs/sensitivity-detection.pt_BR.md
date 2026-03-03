# Detecção de sensibilidade: termos de treino ML e DL

A aplicação usa um pipeline **híbrido** para classificar nomes de colunas e conteúdo amostrado como sensível ou não:

1. **Regex** – Padrões embutidos (CPF, CNPJ, e-mail, telefone, SSN, cartão de crédito, datas) mais overrides opcionais via arquivo de config.
2. **ML** – TF-IDF + RandomForest treinado em uma lista de termos **(texto, rótulo)** (sensível vs não sensível). Os termos vêm de arquivo ou da config inline.
3. **DL (opcional)** – Embeddings de sentenças + um classificador pequeno treinado nos seus termos. Usado quando a dependência opcional `sentence-transformers` está instalada e você fornece termos DL (arquivo ou inline). A confiança é combinada com a do ML (ex.: `max(ml_confidence, dl_confidence)`).

Você pode **definir as palavras de treino para ML e DL** no arquivo de config principal (inline) ou em arquivos YAML/JSON separados.

**English:** [sensitivity-detection.md](sensitivity-detection.md)

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

## Resumo

- **Termos ML:** De `sensitivity_detection.ml_terms` (inline) ou `ml_patterns_file`. Usados pelo classificador TF-IDF + RandomForest.
- **Termos DL:** De `sensitivity_detection.dl_terms` (inline) ou `dl_patterns_file`. Usados pelo opcional embedding + classificador quando `.[dl]` está instalado.
- **Mesmo formato:** Ambos usam uma lista de `{ text, label }` com `label` = `sensitive` ou `non_sensitive` (ou `1` / `0`).
- **Inline sobrescreve arquivo:** Quando `ml_terms` ou `dl_terms` estão preenchidos no config, eles são usados no lugar do carregamento do arquivo correspondente.

Para overrides de regex (padrões customizados para valor), veja `regex_overrides_file` na configuração principal e [USAGE.md](USAGE.md) / [USAGE.pt_BR.md](USAGE.pt_BR.md).
