# Contribuindo para o python3-lgpd-crawler

**English:** [CONTRIBUTING.md](CONTRIBUTING.md)

Obrigado por considerar contribuir. Este documento cobre a configuração local, o fluxo de trabalho e as boas práticas para que você possa executar o app, os testes e abrir alterações com segurança.

## Início rápido (desenvolvimento)

1. **Clone e entre no repositório**

   ```bash
   git clone https://github.com/YOUR_ORG/python3-lgpd-crawler.git
   cd python3-lgpd-crawler
   ```

1. **Use Python 3.12+**

   O projeto usa Python 3.12 e 3.13. Veja [SECURITY.md](SECURITY.md) ([pt-BR](SECURITY.pt_BR.md)) para as versões suportadas.

1. **Instale as dependências com uv (recomendado)**

   ```bash
   uv sync
   ```

   Ou com pip em um virtualenv: `pip install -e .`

1. **Execute os testes**

   ```bash
   uv run pytest -v -W error
   ```

   Todos os testes devem passar sem erros ou avisos. Veja [docs/TESTING.md](docs/TESTING.md) ([pt-BR](docs/TESTING.pt_BR.md)) para o que cada módulo de teste cobre e como executar subconjuntos.

1. **Execute a aplicação**

   ```bash
   uv run python main.py --config config.yaml
   uv run python main.py --config config.yaml --web --port 8088
   ```

## Fluxo de trabalho

- **Bugs e funcionalidades:** Abra uma issue usando os modelos [Bug report](.github/ISSUE_TEMPLATE/bug_report.md) ou [Feature request](.github/ISSUE_TEMPLATE/feature_request.md).
- **Segurança:** Não publique detalhes de exploração em público. Use o modelo [Security issue](.github/ISSUE_TEMPLATE/security.md) (apenas em alto nível) ou o processo em [SECURITY.md](SECURITY.md) ([pt-BR](SECURITY.pt_BR.md)).
- **Pull requests:** Use o [modelo de PR](.github/PULL_REQUEST_TEMPLATE.md). Garanta que os testes passem (`uv run pytest -v -W error`; veja [docs/TESTING.md](docs/TESTING.md) ([pt-BR](docs/TESTING.pt_BR.md))) e que docs/README sejam atualizados quando o comportamento ou a configuração mudar.

### Reduzir conflitos de merge

- **Faça merge ou rebase de `main` na sua branch antes de abrir um PR.** Execute `git fetch origin main` e depois `git merge origin/main` (ou `git rebase origin/main`) e resolva conflitos localmente. Assim o PR permanece integrável e os revisores veem um diff limpo.
- **`report/generator.py`:** A lógica de escrita das planilhas está em `_write_excel_sheets` e helpers (`_build_report_info`, `_build_executive_summary_rows`, etc.). Ao adicionar ou alterar planilhas Excel, atualize esses helpers em vez de colocar a lógica dentro de `generate_report`. Isso mantém a mesma estrutura do `main` e evita os conflitos de merge que tivemos quando o main tinha código inline e a branch tinha o refactor.

## Código e documentação

- **Estilo:** O repositório usa [EditorConfig](.editorconfig) (indentação, charset, fins de linha). Manter o estilo Python consistente (ex.: com Ruff ou Black) é incentivado.
- **Documentação:** Mantenha [README.md](README.md) e [docs/USAGE.md](docs/USAGE.md) em sincronia com o comportamento; atualize [README.pt_BR.md](README.pt_BR.md) e [docs/USAGE.pt_BR.md](docs/USAGE.pt_BR.md) para o português. Toda **nova** documentação voltada ao usuário deve existir em **inglês (canônico)** e **português brasileiro**; **arquivos de plano** podem ser apenas em inglês. Ao alterar docs para refletir atualizações da aplicação, **sincronize o outro idioma** (EN primeiro, depois pt-BR). Use seletor de idioma no topo de cada doc e links cruzados que ofereçam os dois idiomas (veja [docs/README.md](docs/README.md) — Política de documentação). **Após editar qualquer .md:** execute `uv run python scripts/fix_markdown_sonar.py` e `uv run pytest tests/test_markdown_lint.py -v -W error` para que as regras SonarQube/markdownlint (ex.: MD060 estilo de tabela) passem.
- **Segredos:** Nunca faça commit de credenciais ou PII real. Use `.env` ou `config.local.yaml` (ambos estão no `.gitignore`) e redija em issues/PRs.

## CI e higiene de dependências

- **CI:** O GitHub Actions executa testes e **auditoria de dependências** (`uv run pip-audit`) em todo push/PR para `main` (ou `master`). Os PRs devem resolver qualquer falha de auditoria (corrigir ou atualizar dependências vulneráveis) antes do merge. Quando o SonarQube/SonarCloud estiver habilitado (veja [docs/TESTING.md](docs/TESTING.md) ([pt-BR](docs/TESTING.pt_BR.md))), trate os problemas reportados para que o quality gate permaneça verde.
- **Dependências:** A fonte de verdade das bibliotecas é o **`pyproject.toml`** (toolchain uv); pip e **`requirements.txt`** são derivados. Declare todas as dependências de runtime e de desenvolvimento em **`pyproject.toml`**. Prefira **versões mínimas (`>=`)** para que correções de segurança se apliquem; use pin exato (`==`) apenas quando necessário para reprodutibilidade. Ao adicionar ou alterar dependências, execute `uv sync` e regenere o lockfile com `uv pip compile pyproject.toml -o requirements.txt`. Não edite o `requirements.txt` à mão para mudanças de versão.
- **Dependabot / automação:** Ao aplicar uma atualização de dependência (ex.: de um PR do Dependabot), atualize primeiro o **`pyproject.toml`** (suba a versão mínima do pacote), execute `uv pip compile pyproject.toml -o requirements.txt` e faça commit dos dois arquivos. Faça merge dos PRs de dependência somente após o CI (testes e auditoria) passar.

## Checklist de release (segurança)

Antes de marcar uma release, os mantenedores devem:

- **Auditoria de dependências:** Execute `uv sync`, depois `uv run pip-audit`. Corrija ou atualize quaisquer achados altos/críticos antes do release.
- **Documentação:** Garanta que [SECURITY.md](SECURITY.md) ([pt-BR](SECURITY.pt_BR.md)) e [docs/security.md](docs/security.md) ([pt-BR](docs/security.pt_BR.md)) reflitam o comportamento atual (validação, headers, API key, política de logs).
- **Segredos:** Confirme que não há API keys ou senhas em logs; permissões do arquivo de config e do ambiente restringem acesso a usuários confiáveis (veja [SECURITY.md](SECURITY.md) ([pt-BR](SECURITY.pt_BR.md))).

## Implantação e produção

- Use um arquivo de configuração dedicado (ex.: via `CONFIG_PATH`) e nunca faça commit dele. Execute `uv run pip-audit` antes de implantar.
- Para uso público ou multi-tenant, coloque a API atrás de um proxy reverso (HTTPS, rate limiting, autenticação) conforme descrito no README.

## Ver também

- **[docs/TESTING.md](docs/TESTING.md)** ([pt-BR](docs/TESTING.pt_BR.md)) — Módulos de teste, CI, SonarQube.
- **[docs/TOPOLOGY.md](docs/TOPOLOGY.md)** ([pt-BR](docs/TOPOLOGY.pt_BR.md)) — Topologia da aplicação (módulos, classes, fluxo de dados).
- **[docs/COMMIT_AND_PR.md](docs/COMMIT_AND_PR.md)** ([pt-BR](docs/COMMIT_AND_PR.pt_BR.md)) — Automação de commit e PR.
- **[docs/compliance-frameworks.md](docs/compliance-frameworks.md)** ([pt-BR](docs/compliance-frameworks.pt_BR.md)) — Rótulos de conformidade e extensibilidade.
- **[docs/COPYRIGHT_AND_TRADEMARK.pt_BR.md](docs/COPYRIGHT_AND_TRADEMARK.pt_BR.md)** ([EN](docs/COPYRIGHT_AND_TRADEMARK.md)) — Direitos autorais e marca (tornar oficial, registros). [NOTICE](NOTICE) para o aviso do projeto.
- Índice completo da documentação: [docs/README.pt_BR.md](docs/README.pt_BR.md) ([EN](docs/README.md)).

Se tiver dúvidas, abra uma discussão ou uma issue. Obrigado por contribuir.
