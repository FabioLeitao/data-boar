# Planos consolidados – to-dos sequenciais

**English:** [PLANS_TODO.md](PLANS_TODO.md)

Este documento é a **fonte única de verdade** para o status dos planos do projeto e permanece em **`docs/`** o tempo todo. Lista **objetivos incompletos** dos planos ativos e os **to-dos sequenciais recomendados** para alcançá-los. Os documentos de planos concluídos (detalhes de design e to-do) são arquivados em **`docs/completed/`** para referência; os links abaixo apontam para esses arquivos.

Todas as etapas devem ser **não destrutivas**, **sem regressão** e **sem impacto de performance**; cada etapa deve ser **testada** e **segura** antes de ser marcada como feita.

**Status dos planos:** Melhorias de conformidade corporativa ✅ Completo · Detecção de dados de menores ✅ Completo · Identificação agregada ✅ Completo · Categorias sensíveis ML/DL ✅ Completo · Rate limiting e concorrência ✅ Completo · Endurecimento e segurança web ✅ Completo · Logo e naming ⬜ Em progresso · **Dashboard i18n (interface web multilíngue)** ⬜ Em consideração

---

## Plano: Dashboard i18n (interface web multilíngue) ⬜ **Em consideração**

**Fonte:** [docs/PLAN_DASHBOARD_I18N.md](PLAN_DASHBOARD_I18N.md)

**Status:** Ainda não há abordagem definida. O plano descreve **opções e recomendações** (path-prefix vs query/cookie, JSON vs gettext, complexidade). **Não há lista de to-dos aqui até que a abordagem seja escolhida;** depois disso, os passos concretos serão adicionados a esta seção e ao arquivo do plano.

---

## Plano: Logo e recomendações de naming ⬜ **Em progresso**

**Fonte:** [docs/PLAN_LOGO_AND_NAMING.md](PLAN_LOGO_AND_NAMING.md)

**Progresso:** Marque cada to-do como feito aqui e no arquivo do plano quando for realmente concluído.

Objetivo: Logo livre de problemas de direitos autorais (web, favicon, opcional no relatório), integração na aplicação e recomendações de naming (ex.: compliance_crawler). O usuário decide quais opções aplicar.

| #   | To-do                                                                                                                             | Status    | Notas                                    |
| --- | ---                                                                                                                               | ---       | ---                                      |
| 1   | Decidir conceito de logo (A–D) e cores; produzir logo mestre (SVG) e exportar PNG web (32/64 px) e favicon (ICO ou 16/32 PNG)      | ⬜ Pendente | Livre de direitos, escala para 16 px   |
| 2   | Colocar assets em `api/static/`: favicon.ico (e/ou favicon-32.png), logo.svg, logo-64.png                                         | ⬜ Pendente | Opcional: logo-report-48.png para Excel  |
| 3   | Adicionar link(s) de favicon em `api/templates/base.html` (`<link rel="icon">`)                                                   | ⬜ Pendente | Ícone do navegador/aba                   |
| 4   | (Opcional) Adicionar logo à página About e opcionalmente ao cabeçalho do Dashboard/Reports                                       | ⬜ Pendente | about.html, dashboard.html, reports.html |
| 5   | Verificar disponibilidade do nome escolhido (ex.: compliance_crawler) no PyPI e na web                                            | ⬜ Pendente | Evitar conflitos com produtos existentes |
| 6   | Decidir nome de exibição e/ou renomear pacote; se mudar, atualizar `core/about.py` e/ou `pyproject.toml` e docs conforme VERSIONING.md | ⬜ Pendente | Só nome de exibição = sem renomear pacote |
| 7   | (Opcional) Inserir logo na planilha Report info do Excel via `report/generator.py`                                               | ⬜ Pendente | Imagem openpyxl em célula fixa           |
| 8   | (Opcional) Adicionar logo ao rodapé do PNG do heatmap em `_create_heatmap`                                                        | ⬜ Pendente | Imagem pequena via matplotlib            |

---

## Plano: Melhorias de conformidade corporativa ✅ **Completo**

**Fonte:** `.cursor/plans/corporate_compliance_improvements_plan_b209453a.plan.md`

**Progresso:** Todos os to-dos abaixo estão concluídos. Este plano está **fechado** para implementação; use esta seção apenas como referência ao estado atual da aplicação.

(To-dos e estado conforme [PLANS_TODO.md](PLANS_TODO.md) — Phase 6 optional API key implementada e documentada.)

---

## Plano: Detecção e tratamento diferencial de dados de menores ✅ **Completo**

**Fonte:** [docs/completed/PLAN_MINOR_DATA_DETECTION.md](completed/PLAN_MINOR_DATA_DETECTION.md)

**Progresso:** Todos os to-dos abaixo estão concluídos. Este plano está **fechado** para implementação.

Objetivo: Detectar quando os dados podem se referir a menores (ex.: idade a partir de data de nascimento), tratar com máxima sensibilidade, cruzar com nome/documentos oficiais/saúde e, opcionalmente, escanear colunas relacionadas; expor no relatório com tratamento diferencial (LGPD Art. 14, GDPR Art. 8).

(To-dos completos conforme [PLANS_TODO.md](PLANS_TODO.md).)

---

## Plano: Dados agregados / cross-referenciados – risco de identificação ✅ **Completo**

**Fonte:** [docs/completed/PLAN_AGGREGATED_IDENTIFICATION.md](completed/PLAN_AGGREGATED_IDENTIFICATION.md)

**Progresso:** Todos os to-dos estão concluídos. Este plano está **fechado** para implementação.

Objetivo: Cruzar informações de múltiplas fontes/colunas (gênero, cargo, saúde, endereço, telefone, etc.) que **em conjunto** podem identificar indivíduos; tratar como pessoal/sensível e reportar como **caso especial** para DPO/conformidade.

(To-dos completos conforme [PLANS_TODO.md](PLANS_TODO.md).)

---

## Plano: Categorias sensíveis ML/DL (CID, gênero, religião, política, PEP, raça, sindicato, genético, biométrico, vida sexual) ✅ **Completo**

**Fonte:** [docs/completed/PLAN_SENSITIVE_CATEGORIES_ML_DL.md](completed/PLAN_SENSITIVE_CATEGORIES_ML_DL.md)

**Progresso:** Todos os to-dos estão concluídos. Este plano está **fechado** para implementação.

(To-dos completos conforme [PLANS_TODO.md](PLANS_TODO.md).)

---

## Plano: Rate limiting e salvaguardas de concorrência ✅ **Completo**

**Fonte:** [docs/completed/PLAN_RATE_LIMIT_SCANS.md](completed/PLAN_RATE_LIMIT_SCANS.md)

**Progresso:** Todos os to-dos estão concluídos. Este plano está **fechado** para implementação.

(To-dos completos conforme [PLANS_TODO.md](PLANS_TODO.md).)

---

## Plano: Endurecimento e melhorias de segurança web ✅ **Completo**

**Fonte:** [docs/completed/PLAN_WEB_HARDENING_SECURITY.md](completed/PLAN_WEB_HARDENING_SECURITY.md)

Objetivo: Endurecer a superfície web do LGPD crawler (CSP, cabeçalhos e orientação de deploy) sem regredir o comportamento atual.

(To-dos completos conforme [PLANS_TODO.md](PLANS_TODO.md).)

---

## Outros planos (referência)

- **LGPD Audit Full Implementation** (`lgpd_audit_solution_full_implementation_*.plan.md`): Sem to-dos granulares no plano; objetivos em grande parte refletidos no código atual. Nenhuma lista sequencial de to-dos a adicionar aqui.
- **Privacy-audit-scanner** (`privacy-audit-scanner_*.plan.md`): Descreve um layout de pacote diferente (`dataguardian/`). O repositório atual é `python3-lgpd-crawler` com `core/`, `api/`, `report/`, `connectors/`. Os to-dos desses planos mapeiam para componentes existentes; considere **apenas referência** a menos que se adote essa estrutura.

---

## Como usar esta lista

1. **Execute os to-dos em ordem** (1 → 2 → … → 7).
1. **Marque como feito** quando a etapa estiver implementada, os testes passarem e o comportamento for verificado.
1. **Após cada etapa:** execute `uv run pytest -W error` para garantir que não há regressão.
1. **Etapa de publicação:** atualize README/USAGE/SECURITY e versão conforme necessário; construa e envie a imagem Docker; mantenha EN/pt-BR alinhados.

---

*Última sincronização com os arquivos de plano e o código. Atualize este doc ao concluir etapas ou quando os planos mudarem.*
