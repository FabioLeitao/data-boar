# Pacote para revisão por LLM externa (Gemini) — fluxo seguro

**English:** [GEMINI_PUBLIC_BUNDLE_REVIEW.md](GEMINI_PUBLIC_BUNDLE_REVIEW.md)

**Depois de um incidente com `cat`:** passos de recuperação e o script meta Windows **`scripts/recovery-doc-bundle-sanity.ps1`** — **[DOC_BUNDLE_RECOVERY_PLAYBOOK.pt_BR.md](DOC_BUNDLE_RECOVERY_PLAYBOOK.pt_BR.md)** ([EN](DOC_BUNDLE_RECOVERY_PLAYBOOK.md)).

## Autoridade (Gemini vs Git + testes)

Revisão por LLM externa (ex.: Gemini sobre a saída do **`export_public_gemini_bundle.py`**) é **triagem em lote opcional** — não um relatório de auditoria isolado nem substituto de **histórico `git`**, **CI** ou **pytest**. Trate como outros **insumos externos** (ex.: digests estilo Wabbix / WRB): úteis para **priorizar**, sempre abaixo de checagens reproduzíveis. No repositório: **`--verify`** na exportação do pacote, helpers **`audit_concat_*`** quando usar, **`recovery-doc-bundle-sanity.ps1`** e o **playbook de recuperação** quando o pacote correr mal.

Este runbook evita erros do tipo **`cat *.md` manual**: o pacote vem só de **`git ls-files`**, **exclui** **`docs/private/`** e envolve cada arquivo assim:

```text
--- FILE: caminho/relativo/ao/repo ---
<conteúdo exato do arquivo>
```

## Gerar o pacote (recomendado)

Na raiz do repositório:

```bash
uv run python scripts/export_public_gemini_bundle.py \
  --output docs/private/gemini_bundles/public_bundle_$(date -I).txt \
  --compliance-yaml \
  --verify
```

Atalho em Linux/macOS:

```bash
./scripts/export_public_gemini_bundle.sh -o /tmp/public_bundle.txt --compliance-yaml --verify
```

**Destino:** guarde o arquivo sob **`docs/private/...`** (gitignored) para não correr risco de commit.

## Prompt sugerido para o Gemini (copiar/colar)

Anexe **só** o pacote; não misture notas privadas.

```text
Você revisa documentação técnica pública e YAML de CI de um produto open source (Data Boar — auditoria / deteção de sensibilidade).

Entrada: um único texto com secções que começam com:
--- FILE: <caminho> ---
seguido do corpo do arquivo. Não assuma arquivos privados ou não publicados.

Tarefas:
1) Problemas P0/P1/P2 (onboarding, segurança, contradições, limites, footguns de CI).
2) Nos YAML de amostra: risco operacional e manutenção (sem parecer jurídico).
3) Não invente funcionalidades; na dúvida diga “confirmar no código”.

Formato de saída:
## Resumo executivo (máx. 5 bullets)
## P0
## P1
## P2
## Perguntas que os docs não respondem
```

## Automação relacionada

- Pacotes antigos sem marcadores: `scripts/audit_concatenated_markdown.py` (divisão por H1 ou `--cat-order` por bytes).
- **Heurística de “peças do puzzle” (janela deslizante):** `scripts/audit_concat_sliding_window.py` indexa **todas** as janelas de *N* linhas nos `*.md` / `*.yaml` / `*.yml` rastreados e marca quais linhas do teu **blob concatenado** coincidem com **alguma** janela do repositório. Trechos **sem cobertura** podem ser cola entre arquivos, edição manual ou texto que **já não existe** no disco — **não** provam perda (linhas genéricas e limites de janela geram ruído). Exemplo:

  ```bash
  uv run python scripts/audit_concat_sliding_window.py \
    -i docs/private/mess_concatenated_gemini_sanity_check/sobre-data-boar.md \
    --window 25 --strip-bundle-markers --show-sample-matches 15
  ```

  Opcional: `--rstrip-lines` se houver diferença só de espaços no fim da linha; `--include-private-corpus` só se quiseres incluir `docs/private/**` no corpus. `--fail-if-uncovered-pct-above 0` sai com código ≠ 0 se restar **alguma** linha sem cobertura (gate rígido; em blobs reais costuma ser barulhento demais).
  **Várias janelas:** `--sweep-windows 12,15,18,22,25,30` imprime uma tabela comparativa (repetir com `--rstrip-lines` para comparar barreiras de whitespace). Ver **[DOC_BUNDLE_RECOVERY_PLAYBOOK.pt_BR.md](DOC_BUNDLE_RECOVERY_PLAYBOOK.pt_BR.md)** § Várias passagens.

- Política de notificação: [OPERATOR_NOTIFICATION_CHANNELS.pt_BR.md](OPERATOR_NOTIFICATION_CHANNELS.pt_BR.md).
