# Pasta `config/` — ilustração JSON legada

**English:** [README.md](README.md)

O arquivo **`config.json`** nesta pasta serve para mostrar o formato **legado** que o carregador ainda aceita:

- **`databases`** no topo: lista de ligações (mapeada para alvos `type: database`).
- **`file_scan.directories`**: lista de pastas (cada uma vira um alvo `type: filesystem`).

**Para trabalho novo, prefira YAML** — é mais simples de comentar, revisar e mesclar. Um **único modelo completo** (várias seções + blocos opcionais comentados) está em **`deploy/samples/config.starter-lgpd-eval.yaml`**. Quem entra por **`docs/`** pode seguir **[docs/samples/README.pt_BR.md](../docs/samples/README.pt_BR.md)** (mesmos links em um só lugar).

O modelo mínimo para contêiner é **`deploy/config.example.yaml`** (`targets: []`).

**Não** use **`config.json`** como modelo de produção: credenciais reais devem ir para variáveis de ambiente (`pass_from_env`, etc.) e caminhos reais apenas em arquivos **não** commitados (veja `.gitignore` na raiz e [CONTRIBUTING.md](../CONTRIBUTING.md)).
