# Convenção de versão e checklist de bump

**English:** [VERSIONING.md](VERSIONING.md)

Este projeto usa o esquema **major.minor.build** (maior.menor.build), com **sufixos de pré-release** opcionais enquanto o trabalho ainda está em preparação:

- **major** – primeiro número (ex.: mudanças incompatíveis ou release maior)
- **minor** – segundo número (ex.: novas funcionalidades, compatível)
- **build** – terceiro número (ex.: correções, documentação, sem mudança de comportamento)
- **sufixo** (opcional) – marcador de estágio em minúsculo: `-beta` ou `-rc`

Exemplos:

- `1.3.2` significa major 1, minor 3, build 2 (número final publicável).
- `1.3.3-beta` significa trabalho de pré-release em andamento para o próximo build.
- `1.3.3-rc` significa release candidate (feature/código/docs/testes conectados; faltam os passos finais de publish).

---

## Regras de bump

| Tipo de bump | Regra                                                | Exemplo             |
| ---          | ---                                                  | ---                 |
| **Major**    | Aumentar o primeiro número; zerar minor e build      | `1.3.2` → **2.0.0** |
| **Minor**    | Manter major; aumentar o segundo número; zerar build | `1.3.2` → **1.4.0** |
| **Build**    | Manter major e minor; apenas aumentar o build        | `1.3.2` → **1.3.3** |

---

## Fluxo de pré-release (`-beta` / `-rc`) antes do publish final

Use sufixos em minúsculo de forma consistente:

| Estágio | Uso recomendado | Exemplo |
| --- | --- | --- |
| **`-beta`** | Mudanças relevantes de código/comportamento já começaram e estão rastreadas, mas ainda não são candidatas finais de release. | `1.6.8-beta` |
| **`-rc`** | Candidato pronto para validação final/coreografia de publish (testes verdes, docs sincronizados, release notes prontas, faltando merge/release). | `1.6.8-rc` |
| **final (sem sufixo)** | Número de release público (tag Git + GitHub Release + publish no Docker Hub). | `1.6.8` |

### Política prática

- Se uma fatia altera comportamento de forma relevante (API, lógica de detecção, saída de relatório, operação em runtime, postura de segurança), prefira mover a versão de trabalho para `X.Y.Z-beta`.
- Quando o pacote estiver materialmente pronto (código + testes + docs/release notes em forma), promova para `X.Y.Z-rc`.
- Remova o sufixo e publique `X.Y.Z` apenas no ciclo de release real (merge + tag + GitHub Release + publish Docker).
- Para escopo maior (ou quando solicitado explicitamente), publique com **minor bump**: `X.(Y+1).0` (sem sufixo no publish final).

---

## Versão de trabalho vs versão publicada (evitar confusão)

- **Versão de trabalho:** valor atual no `pyproject.toml` no branch (pode estar em `-beta`/`-rc` ou ainda sem release).
- **Versão publicada:** última tag Git + GitHub Release + tag do Docker Hub disponível para uso externo.
- Não assuma que são iguais; informe as duas explicitamente em release notes e pedidos de revisão.

---

## Onde a versão aparece (checklist ao dar bump)

Ao dar bump na versão, atualize **todos** os itens abaixo para manter o número consistente:

### 1. Fonte de verdade (obrigatório)

| Local                | O que alterar                                                                                                                                                                                                                                                                                     |
| ---                  | ---                                                                                                                                                                                                                                                                                               |
| **`pyproject.toml`** | Atualize a linha `version = "X.Y.Z"`. Ela é a **única fonte de verdade** do pacote instalado. A aplicação (página About, aba Report info, rodapé do heatmap, API `/about/json`) lê a versão dos metadados do pacote; atualizar o `pyproject.toml` e reinstalar é suficiente em tempo de execução. |

### 2. Fallback quando os metadados não estão disponíveis

| Local               | O que alterar                                                                                                                                                                          |
| ---                 | ---                                                                                                                                                                                    |
| **`core/about.py`** | Atualize a string de fallback em `get_about_info()` quando `importlib.metadata.version(...)` falhar (ex.: execução direta do código sem instalar). Ex.: `ver = "1.3.0"` → nova versão. |

### 3. Páginas de manual (man)

| Local                  | O que alterar                                                                                  |
| ---                    | ---                                                                                            |
| **`docs/data_boar.1`** | Na linha `.TH` (ex.: `"Data Boar 1.5.4"`), defina a versão para a nova.                        |
| **`docs/data_boar.5`** | Idem: atualize a versão na linha `.TH`. (Legado: `lgpd_crawler` é symlink de compatibilidade.) |

### 4. Deploy e Docker

| Local                       | O que alterar                                                                                                                 |
| ---                         | ---                                                                                                                           |
| **`docs/deploy/DEPLOY.md`** | Atualize os **exemplos** de tags de versão nos comandos de tag/push do Docker (ex.: `1.3.0` nos exemplos) para a nova versão. |

### 5. Documentação (EN e PT-BR)

| Local                          | O que alterar                                                                                                                                          |
| ---                            | ---                                                                                                                                                    |
| **`README.md`**                | Se o texto citar o número da versão atual (ex.: em exemplo de tag de imagem), atualize.                                                                |
| **`README.pt_BR.md`**          | Idem ao README.md para qualquer menção explícita à versão.                                                                                             |
| **`docs/USAGE.md`**            | Atualize qualquer referência explícita à versão, se houver.                                                                                            |
| **`docs/USAGE.pt_BR.md`**      | Idem ao USAGE.md.                                                                                                                                      |
| **`docs/plans/PLANS_TODO.md`** | Se houver nota de “versão atual” ou “app version” no “Current state” ou passo de publish de um plano, atualize ao lançar.                              |
| **Outros docs**                | Pesquise no repositório pela string da versão antiga (ex.: `1.3.0`) e atualize referências restantes em SECURITY.md, CONTRIBUTING.md ou release notes. |

### 6. Interface e relatórios (não é preciso editar se 1–2 forem feitos)

Estes exibem a versão **dinamicamente** a partir dos metadados do pacote (via `core/about.py`), portanto **não** precisam de edição manual ao dar bump:

- **Página About** (`api/templates/about.html`) – usa `{{ about.version }}`
- **Dashboard / Reports** – usam `{{ about.version }}`
- **Aba “Report info” do Excel** – `report/generator.py` usa `about["version"]`
- **Rodapé do heatmap PNG** – mesmo dicionário `about`
- **API `/about/json`** – mesmo dicionário `about`

Depois de atualizar o `pyproject.toml` (e opcionalmente `core/about.py`), reinstale o pacote (ex.: `uv sync` ou `pip install -e .`) para que a nova versão entre nos metadados; a interface e os relatórios passarão a exibi-la automaticamente.

---

## Resumo rápido

- **Formato:** `major.minor.build`
- **Sufixos de pré-release:** `-beta`, `-rc` em minúsculo (apenas estados de trabalho)
- **Bump major:** `X.Y.Z` → `(X+1).0.0`
- **Bump minor:** `X.Y.Z` → `X.(Y+1).0`
- **Bump build:** `X.Y.Z` → `X.Y.(Z+1)`
- **Fluxo de promoção:** `X.Y.Z-beta` → `X.Y.Z-rc` → `X.Y.Z` (publish final)
- **Checklist:** pyproject.toml → core/about.py → docs/data_boar.1, data_boar.5 → docs/deploy/DEPLOY.md → README (EN/PT-BR), USAGE (EN/PT-BR), PLANS_TODO → buscar no repositório pela string da versão antiga.

**English:** [VERSIONING.md](VERSIONING.md)
