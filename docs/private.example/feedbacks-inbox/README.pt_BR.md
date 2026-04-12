# Caixa de entrada de feedbacks de parceiro / cliente — modelo (rastreado)

**English:** [README.md](README.md)

**Esta pasta é versionada** só como **esboço de política**. **Não** coloque PDFs Wabbix, exportações Gemini ou outros pacotes completos de revisão no Git.

## Onde ficam os arquivos (máquina do operador)

Crie **`docs/feedbacks, reviews, comments and criticism/`** na **raiz do repositório** (no mesmo nível que **`docs/`**). Esse caminho está no **`.gitignore`** — **não** fica embaixo de **`docs/private/`**.

- **Hábito:** coloque aí feedbacks de parceiros ou clientes (drops estilo WRB, análises Wabbix, exportações que não devem ir para o `origin`).
- **Conclusões destiladas** e IDs ficam em **planos** ou notas em **`docs/ops/`** depois de redigir — **nunca** cole tabelas confidenciais completas em issues nem em Markdown público.

## Espelho opcional (Git privado empilhado)

Se você usa um repositório **aninhado** em **`docs/private/`**, pode também manter comprovantes em **`docs/private/feedbacks_and_reviews/`** e commitar conforme **`docs/ops/PRIVATE_LOCAL_VERSIONING.pt_BR.md`** — ainda assim **nunca** envie esses arquivos para o remoto **do produto** no GitHub.

## Agentes (Cursor)

Quando o operador usar o token de sessão **`feedback-inbox`**, os assistentes fazem **`read_file`** / listam primeiro a pasta gitignored de drops. Se estiver **vazia**, diga isso. Se a **origem** (Wabbix vs Gemini vs outra) não estiver clara, **pergunte** antes de atribuir linhas em **`docs/plans/`** ou **`PLANS_TODO.md`**.

## Ver também

- **[PRIVATE_OPERATOR_NOTES.pt_BR.md](../../PRIVATE_OPERATOR_NOTES.pt_BR.md)** — caminho de feedback vs `docs/private/`.
- **`.cursor/rules/session-mode-keywords.mdc`** — linha **`feedback-inbox`**.
