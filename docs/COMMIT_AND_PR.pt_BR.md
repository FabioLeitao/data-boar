# Fluxo de commit e PR (estilo Agent Review Panel)

**English:** [COMMIT_AND_PR.md](COMMIT_AND_PR.md)

Quando você pede ao agente para **visualizar**, **fazer commit local** ou **criar um PR** com uma descrição curta e tópicos, ele usa o mesmo fluxo do antigo “Agent Review Panel” do Cursor: revisar alterações, opcionalmente selecionar arquivos, depois escolher commit ou abrir o PR no navegador com o formulário pré-preenchido. Antes de dar push, ele faz **fetch** e **rebase-pull** se o branch estiver atrás do remoto, preservando histórico linear e evitando sobrescritas acidentais.

## O que o agente faz quando você pede

- **“Visualizar”** ou **“Mostre o que seria commitado”**: lista os arquivos que seriam incluídos (excluindo `audit_results.db`), mostra um resumo do diff (`git diff --stat`) e o **título e corpo em tópicos** propostos. **Não faz stage nem commit.** Em seguida você pode dizer “Commit local” ou “Criar PR”.

- **“Commit local”** (opcionalmente: “… com mensagem: …”): dá stage em todos os arquivos alterados **exceto** `audit_results.db`, monta um **título** e **corpo em tópicos** a partir das alterações (ou usa o que você disse) e executa `git commit -m "<título>" -m "<corpo>"`.

- **“Criar PR”** (opcionalmente: “… com descrição: …” ou “… no branch X”): se houver alterações não commitadas, faz stage (ou só `-IncludeFiles` se indicado) e commit. Se não houver alterações não commitadas mas houver commits locais não enviados, usa esses commits para o PR. **Antes do push:** executa `git fetch origin` e, se o branch estiver **atrás** do remoto, executa `git pull --rebase origin <branch>`. Em seguida faz **push** do branch atual para `origin` e **abre o PR no navegador padrão** com título e descrição **pré-preenchidos** (via `gh pr create --web` ou página de compare do GitHub se `gh` não estiver instalado).

## Selecionar quais arquivos incluir

Você pode limitar o commit/PR a arquivos específicos com **`-IncludeFiles`** (separados por vírgula ou array). O script então faz stage apenas desses caminhos.

- **Visualize primeiro:** execute com `-Action Preview` para ver os arquivos candidatos e o título/corpo proposto.
- **Depois:** execute com `-Action Commit` ou `-Action PR` e, se quiser incluir só alguns arquivos, adicione `-IncludeFiles "path1","path2"`.

## Fazer manualmente

Na raiz do repositório (PowerShell):

```powershell
# Apenas visualizar (sem commit)
.\scripts\commit-or-pr.ps1 -Action Preview -Title "Seu título" -Body "Tópico um`nTópico dois"

# Apenas commit
.\scripts\commit-or-pr.ps1 -Action Commit -Title "Título curto" -Body "Tópico um`nTópico dois"

# Criar PR no branch atual (commit, push, abrir PR no navegador)
.\scripts\commit-or-pr.ps1 -Action PR -Title "Título curto" -Body "Tópicos..."

# Criar PR incluindo apenas arquivos selecionados
.\scripts\commit-or-pr.ps1 -Action PR -IncludeFiles "README.md","scripts/commit-or-pr.ps1" -Title "Título" -Body "Tópicos..."

# Criar PR em um branch novo ou existente
.\scripts\commit-or-pr.ps1 -Action PR -Branch "feature/minha-alteracao" -Title "Título" -Body "Tópicos..."
```

- **Push** usa seu remote e chaves SSH normais do Git.
- **Navegador:** Com `gh` instalado e autenticado, o formulário de PR abre com título e descrição preenchidos; basta confirmar e clicar em “Create pull request”.

## Requisitos

- **Git** e (para PR) **SSH** ou HTTPS com push para o GitHub.
- **GitHub CLI (`gh`)** e `gh auth login` para a melhor experiência: o formulário de PR abre pré-preenchido no navegador. Se `gh` não estiver disponível, o script ainda abre a página de compare para você criar o PR manualmente.

## Notas

- O script **respeita `.gitignore`**: usa `git check-ignore` para que apenas caminhos não ignorados sejam colocados em stage ou commitados (ex.: `audit_results.db`, relatórios, `__pycache__` nunca são incluídos).
- O agente **não** tem acesso às suas credenciais; ele executa `git` e `gh` no seu ambiente, então seu SSH e `gh auth` são usados.
