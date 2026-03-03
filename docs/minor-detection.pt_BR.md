# Detecção de dados de menores: configuração e ajuste fino

A aplicação pode detectar quando os dados coletados podem se referir a **menores de idade** (por exemplo, idade ou data de nascimento em colunas) e tratá-los com **máxima sensibilidade**, com tratamento diferenciado nos relatórios (LGPD Art. 14, GDPR Art. 8). Esta página descreve como **configurar e ajustar** a funcionalidade pelo **arquivo de configuração externo**, sem alterar código da aplicação.

**English:** [minor-detection.md](minor-detection.md)

---

## O que é detectado

- **Nomes de colunas** que sugerem data de nascimento ou idade, em **inglês e português brasileiro**, incluindo siglas (ex.: DOB, DDN, NASC, idade, age).
- **Valores amostrados**: idades numéricas (ex.: `17`) ou datas que, interpretadas como data de nascimento, impliquem idade abaixo do **limite** configurável (padrão **18**). Esses achados são sinalizados como **possível dado de menor** (`DOB_POSSIBLE_MINOR`) e recebem uma recomendação de alta prioridade no relatório.

Consulte [PLAN_MINOR_DATA_DETECTION.md](PLAN_MINOR_DATA_DETECTION.md) para o desenho completo e a lista de nomes/formatos de coluna.

---

## Arquivo de config: onde e o quê

O **limite de idade menor/maior de idade** é definido no **arquivo de configuração principal** (ex.: `config.yaml` ou o arquivo indicado por `CONFIG_PATH`). Não é necessário alterar código.

| Chave | Tipo | Padrão | Descrição |
|-------|------|--------|-----------|
| `detection.minor_age_threshold` | inteiro | **18** | Idade abaixo deste valor (inclusive) é tratada como possível menor. Use ex.: 21 se sua política tratar pessoas com menos de 21 anos como menores. |
| `detection.minor_full_scan` | booleano | false | Reservado para uso futuro (varredura completa da coluna quando houver indicação de menor). |
| `detection.minor_cross_reference` | booleano | true | Reservado para uso futuro (cruzamento com nome/doc/saúde na mesma linha). |

Se a seção **`detection`** for **omitida**, o limite permanece **18** e a aplicação se comporta como antes (sem erros). Incluir a seção permite ajustar o limite sem quebrar execuções existentes.

---

## Como ajustar e refinar

### 1. Usar o padrão (18)

Não faça nada: omita a seção `detection`. Qualquer pessoa com menos de 18 anos (por idade ou inferida pela data de nascimento) será sinalizada como possível menor.

### 2. Aumentar o limite (ex.: política under-21)

Se sua organização trata pessoas com menos de 21 anos como menores, defina o limite em 21 no arquivo de config:

```yaml
# config.yaml
targets: []
report:
  output_dir: .
sqlite_path: audit_results.db

detection:
  minor_age_threshold: 21
```

Em seguida execute a auditoria como de costume (`python main.py --config config.yaml` ou pela API). Colunas que pareçam de idade/DOB com valores que indiquem idade &lt; 21 serão sinalizadas como possível menor.

### 3. Reduzir o limite (ex.: apenas crianças pequenas)

Para sinalizar apenas idades bem baixas (ex.: menores de 14), defina:

```yaml
detection:
  minor_age_threshold: 14
```

### 4. Exemplo completo com outras opções

```yaml
targets:
  - name: meu-banco
    type: database
    host: localhost
    database: app_db
    # ...
file_scan:
  extensions: [.csv, .xlsx, .txt]
  recursive: true
report:
  output_dir: ./reports
  min_sensitivity: LOW

# Opcional: possível dado de menor (LGPD Art. 14, GDPR Art. 8)
detection:
  minor_age_threshold: 18   # padrão; altere para 21 (ou outro) se necessário
  minor_full_scan: false    # reservado
  minor_cross_reference: true   # reservado

sqlite_path: audit_results.db
scan:
  max_workers: 1
```

---

## Nomes e formatos de coluna reconhecidos

O detector procura nomes de coluna (e conteúdo amostrado) que indiquem **DOB ou idade**. Nomes reconhecidos incluem:

| Conceito | Inglês | Português brasileiro | Siglas |
|----------|--------|----------------------|--------|
| Data de nascimento | date of birth, birth date, birthdate | data de nascimento, nascimento, data de nasc. | DOB, DDN, DN, NASC, DTN |
| Idade | age, person age | idade, idade_atual, idade_pessoa, faixa etária | AGE, IDD |

**Formatos de data** no texto amostrado: `dd/mm/yyyy`, `yyyy-mm-dd`, `mm/dd/yyyy` (e variantes comuns). **Idade numérica**: inteiros na amostra (ex.: 0–120) quando o nome da coluna sugere idade.

Se o nome da coluna **não** sugerir DOB ou idade, um valor como `17` ou uma data na amostra **não** dispara sozinho o possível-menor (evita falsos positivos em colunas genéricas numéricas/de data).

---

## Relatório e recomendações

Achados sinalizados como possível menor recebem:

- **Sensibilidade:** HIGH  
- **Padrão:** `DOB_POSSIBLE_MINOR` (possivelmente combinado com outros padrões)  
- **Norm tag:** LGPD Art. 14 – possível dado de menor; GDPR Art. 8  

No relatório Excel, a aba **Recommendations** inclui uma linha dedicada a possível dado de menor com **prioridade máxima** (CRÍTICA) e texto de tratamento diferenciado (consentimento, armazenamento, uso, compartilhamento, responsabilidade dos pais). Essa linha aparece **em primeiro** na aba de Recomendações. Consulte [PLAN_MINOR_DATA_DETECTION.md](PLAN_MINOR_DATA_DETECTION.md) e o gerador de relatório para o texto exato.

---

## Documentação relacionada

- [PLAN_MINOR_DATA_DETECTION.md](PLAN_MINOR_DATA_DETECTION.md) – Plano, desenho e status dos to-dos.  
- [sensitivity-detection.pt_BR.md](sensitivity-detection.pt_BR.md) – Detecção de sensibilidade ML/DL e regex.  
- [USAGE.pt_BR.md](USAGE.pt_BR.md) – Configuração geral e uso da API.
