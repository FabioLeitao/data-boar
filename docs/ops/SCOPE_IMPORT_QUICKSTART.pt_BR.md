# Importação de escopo — início rápido (planilha ou memória)

**English:** [SCOPE_IMPORT_QUICKSTART.md](SCOPE_IMPORT_QUICKSTART.md)

Use quando ainda **não** há exportação GLPI / CMDB — só lista de workshop, e-mail ou o que a equipe lembra. O fluxo técnico continua sendo **CSV → fragmento YAML**; colunas e tipos em [USAGE.pt_BR.md](../USAGE.pt_BR.md#scope-import-csv-fragment).

## Caminho para quem não é de TI (Excel / LibreOffice)

1. Abra uma planilha nova.
1. Copie a **linha de cabeçalho** de [`deploy/scope_import.example.csv`](../../deploy/scope_import.example.csv) (a que começa com `type,`).
1. Inclua **uma linha por fonte** (banco, pasta ou compartilhamento). Use `name` para um rótulo curto, se ajudar. Em `type`, use valores suportados hoje: por exemplo `filesystem`, `postgresql`, `smb`, `nfs`, `mysql` — detalhes no USAGE.
1. **Não** digite senhas na planilha; use `pass_from_env` com o nome da variável de ambiente que você vai definir no servidor.
1. **Salvar como** → **CSV UTF-8** (separado por vírgula). Se o programa só oferecer “CSV (delimitado por vírgulas)”, prefira exportação **UTF-8** no Excel ou LibreOffice para não quebrar acentos.
1. Na máquina com o repositório execute: `uv run python scripts/scope_import_csv.py caminho/para/sua.csv -o targets.fragment.yaml`
1. **Revise** `targets.fragment.yaml`, mescle a lista `targets:` no `config.yaml` real e defina as variáveis de ambiente para `pass_from_env` / `user_from_env`.

## Privacidade

Trate o CSV como **inventário interno de infraestrutura** (permissões, sem repositório público). Mesma disciplina que [SECURITY.md](../../SECURITY.md) para config.

## Depois: GLPI ou outros exports

Colunas específicas de fornecedor serão mapeadas para o mesmo esquema canônico num adaptador futuro; o fluxo continua **exportação → limpeza no formato CSV → `scope_import_csv.py`**.
