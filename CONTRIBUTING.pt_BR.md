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

- **Estilo:** O repositório usa [EditorConfig](.editorconfig) (indentação, charset, fins de linha). Execute `uv run ruff check .` e `uv run ruff format --check .` (ou corrija com `uv run ruff format .`) antes do PR para que o job de lint do CI passe. **Recomendado:** instale os hooks do [pre-commit](https://pre-commit.com/) para que o Ruff (check + format) rode em todo commit: `uv sync` e depois `uv run pre-commit install`; veja `.pre-commit-config.yaml`.
- **Documentação:** Mantenha [README.md](README.md) e [docs/USAGE.md](docs/USAGE.md) em sincronia com o comportamento; atualize [README.pt_BR.md](README.pt_BR.md) e [docs/USAGE.pt_BR.md](docs/USAGE.pt_BR.md) para o português. Toda **nova** documentação voltada ao usuário deve existir em **inglês (canônico)** e **português brasileiro**; **arquivos de plano** podem ser apenas em inglês. Ao alterar docs para refletir atualizações da aplicação, **sincronize o outro idioma** (EN primeiro, depois pt-BR). Use seletor de idioma no topo de cada doc e links cruzados que ofereçam os dois idiomas (veja [docs/README.md](docs/README.md) — Política de documentação). **Após editar qualquer .md:** execute `uv run python scripts/fix_markdown_sonar.py` e `uv run pytest tests/test_markdown_lint.py -v -W error` para que as regras SonarQube/markdownlint (ex.: MD060 estilo de tabela) passem.
- **Segredos:** Nunca faça commit de credenciais ou PII real. Use `.env` ou `config.local.yaml` (ambos estão no `.gitignore`) e redija em issues/PRs.

## CI e higiene de dependências

- **CI:** O GitHub Actions executa testes e **auditoria de dependências** (`uv run pip-audit`) em todo push/PR para `main` (ou `master`). Os PRs devem resolver qualquer falha de auditoria (corrigir ou atualizar dependências vulneráveis) antes do merge. Quando o SonarQube/SonarCloud estiver habilitado (veja [docs/TESTING.md](docs/TESTING.md) ([pt-BR](docs/TESTING.pt_BR.md))), trate os problemas reportados para que o quality gate permaneça verde.
- **Dependências:** A fonte de verdade das bibliotecas é o **`pyproject.toml`** (toolchain uv). O arquivo **`uv.lock`** fixa a árvore exata de dependências resolvidas para que as instalações sejam reproduzíveis e os usuários fiquem protegidos de quebras acidentais quando uma dependência atualiza (“funcionou ontem”). Declare todas as dependências em **`pyproject.toml`** (prefira **versões mínimas `>=`**; use pin `==` só quando necessário). Ao adicionar ou alterar deps, execute `uv lock`, depois `uv export --no-emit-package pyproject.toml -o requirements.txt`, e faça commit de **pyproject.toml**, **uv.lock** e **requirements.txt**. Não edite `uv.lock` nem `requirements.txt` à mão para mudanças de versão. O CI executa `uv sync` (que usa o `uv.lock`) e em seguida `pip-audit`, ou seja, o ambiente bloqueado é o que é testado e auditado.
- **Dependabot / automação:** O Dependabot abre PRs semanais para pip e GitHub Actions. Ao aplicar uma atualização de dependência (ex.: de um PR do Dependabot), atualize primeiro o **`pyproject.toml`** (suba a versão mínima), execute `uv lock` e `uv export --no-emit-package pyproject.toml -o requirements.txt`, e faça commit dos três arquivos. Faça merge dos PRs de dependência somente após o CI (testes e auditoria) passar. O Dependabot ajuda a sinalizar quando atualizar; agir nesses PRs (ou antes de uma release estável) mantém o lockfile atualizado, compatível e seguro. Para PRs **de segurança** do Dependabot, usamos o SLA opcional em [SECURITY.md](SECURITY.md) ([pt-BR](SECURITY.pt_BR.md)) (Resposta de segurança).

## Histórico de releases e changelog

O histórico de releases é o **histórico de commits/PRs no git** mais as **notas de release versionadas em `docs/releases/`** (ex.: um arquivo por versão). Um arquivo CHANGELOG separado no repositório **não é obrigatório**; use `docs/releases/` e as tags para “onde estamos” e o progresso.

## Checklist de release (segurança)

Antes de marcar uma **release estável**, os mantenedores devem:

- **Lockfile e auditoria:** Execute `uv lock` para atualizar o lockfile a partir do `pyproject.toml` atual, depois `uv sync` e `uv run pip-audit`. Corrija ou atualize quaisquer achados altos/críticos; em seguida execute `uv export --no-emit-package pyproject.toml -o requirements.txt` e faça commit de **uv.lock** e **requirements.txt** para que a release seja reproduzível, compatível e segura. Isso protege o usuário de quebras acidentais e mantém a release em dependências auditadas.
- **Documentação:** Garanta que [SECURITY.md](SECURITY.md) ([pt-BR](SECURITY.pt_BR.md)) e [docs/SECURITY.md](docs/SECURITY.md) ([pt-BR](docs/security.pt_BR.md)) reflitam o comportamento atual (validação, headers, API key, política de logs).
- **Segredos e logs:** Confirme que não há API keys ou senhas em logs; permissões do arquivo de config e do ambiente restringem acesso a usuários confiáveis (veja [SECURITY.md](SECURITY.md) ([pt-BR](SECURITY.pt_BR.md))). Garanta que **permissões do arquivo de config** restrinjam leitura/escrita a usuários confiáveis e que **config.yaml** (e qualquer arquivo com segredos) **não seja commitado** (veja .gitignore). Ao adicionar ou alterar logs, não registre config bruto, corpo de requisição ou credenciais; texto de falha/exceção é redigido via `core.validation.redact_secrets_for_log` (regressão: `test_redact_secrets_for_log_*` em `tests/test_security.py`).

## Implantação e produção

- Use um arquivo de configuração dedicado (ex.: via `CONFIG_PATH`) e nunca faça commit dele. Execute `uv run pip-audit` antes de implantar.
- Para uso público ou multi-tenant, coloque a API atrás de um proxy reverso (HTTPS, rate limiting, autenticação) conforme descrito no README.

## Ver também

- **[docs/TESTING.md](docs/TESTING.md)** ([pt-BR](docs/TESTING.pt_BR.md)) — Módulos de teste, CI, SonarQube.
- **[docs/TOPOLOGY.md](docs/TOPOLOGY.md)** ([pt-BR](docs/TOPOLOGY.pt_BR.md)) — Topologia da aplicação (módulos, classes, fluxo de dados).
- **[docs/COMMIT_AND_PR.md](docs/COMMIT_AND_PR.md)** ([pt-BR](docs/COMMIT_AND_PR.pt_BR.md)) — Automação de commit e PR.
- **[docs/COMPLIANCE_FRAMEWORKS.md](docs/COMPLIANCE_FRAMEWORKS.md)** ([pt-BR](docs/COMPLIANCE_FRAMEWORKS.pt_BR.md)) — Rótulos de conformidade e extensibilidade.
- **[docs/COPYRIGHT_AND_TRADEMARK.pt_BR.md](docs/COPYRIGHT_AND_TRADEMARK.pt_BR.md)** ([EN](docs/COPYRIGHT_AND_TRADEMARK.md)) — Direitos autorais e marca (tornar oficial, registros). [NOTICE](NOTICE) para o aviso do projeto.
- Índice completo da documentação: [docs/README.pt_BR.md](docs/README.pt_BR.md) ([EN](docs/README.md)).

Se tiver dúvidas, abra uma discussão ou uma issue. Obrigado por contribuir.
