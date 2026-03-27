# Pacote para revisão por LLM externa (Gemini) — fluxo seguro

**English:** [GEMINI_PUBLIC_BUNDLE_REVIEW.md](GEMINI_PUBLIC_BUNDLE_REVIEW.md)

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

- Pacotes antigos sem marcadores: `scripts/audit_concatenated_markdown.py`.
- Política de notificação: [OPERATOR_NOTIFICATION_CHANNELS.pt_BR.md](OPERATOR_NOTIFICATION_CHANNELS.pt_BR.md).
