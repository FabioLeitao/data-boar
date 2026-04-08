# Remediação definitiva de PII e histórico sensível — runbook do operador

**English:** [PII_DEFINITIVE_REMEDIATION.md](PII_DEFINITIVE_REMEDIATION.md)

**Público:** Mantenedor / operador com permissão de push em `FabioLeitao/data-boar`, GitHub CLI ou browser, e `git-filter-repo` instalado.

**Objetivo:** Alinhar o **`main` canônico**, o **histórico Git**, a **CI** (`pii_history_guard --full-history`) e **todos os clones** (PC de desenvolvimento, hosts do lab, colaboradores) para que literais sensíveis não permaneçam acessíveis em blobs públicos ou mensagens de commit.

**O que a automação não faz por si:** apagar **forks de terceiros**, limpar **caches** externos ou provar que o **Wayback** não tem cópia — isso exige dono do fork, GitHub/suporte ou tempo.

---

## A. Pré-condições

1. **Backup:** `scripts/run-pii-history-rewrite.ps1` cria um **mirror** na pasta pai do repo antes de reescrever. Mantenha-o até o `main` estar verde e os clones atualizados.
2. **Ferramentas:** `git`, `git-filter-repo` no PATH, `uv` (testes), rede para `origin`.
3. **Árvore limpa** antes da reescrita: commit ou stash de alterações intencionais.

---

## B. Higiene no mesmo dia (sem reescrever histórico)

Quando você só precisa alinhar **arquivos rastreados atuais** e o guard **incremental**:

```powershell
cd C:\caminho\para\data-boar
git fetch origin
git pull origin main
uv sync
uv run pytest tests/test_pii_guard.py tests/test_talent_public_script_placeholders.py tests/test_talent_ps1_tracked_no_inline_pool.py -q
uv run python scripts/pii_history_guard.py
```

**Linux no lab** (sem `uv` no PATH): `python3 -m pytest …` se o pytest estiver instalado, ou instalar `uv` conforme documentação do projecto.

---

## C. Reescrita completa do histórico (destrutiva no remoto após push)

Correr **só** depois de integrar guards + regras de substituição no `main` (este repo inclui `scripts/filter_repo_pii_replacements.txt`).

1. **Commit** de todas as alterações rastreadas pretendidas (guards, substituições, docs).
2. Na raiz do repo:

```powershell
.\scripts\run-pii-history-rewrite.ps1
```

3. Inspecione o caminho **`data-boar-history-rewrite-*`** reportado. Se `pytest` e `pii_history_guard --full-history` estiverem verdes, você pode fazer push:

```powershell
.\scripts\run-pii-history-rewrite.ps1 -Push
```

4. **Imediatamente após qualquer force-push público:**
   - **Apagar branches remotas obsoletas** no GitHub que ainda apontem para SHAs **pré-reescrita** (senão a CI ou `pii_history_guard --full-history` ainda podem ver blobs antigos).
   - **Cada clone** (teu, lab, colaborador):

```bash
git fetch origin
git reset --hard origin/main
git fetch --prune
```

5. **Forks (ex.: colaborador):** o dono precisa **apagar o fork** ou **recriar / alinhar** com o `main` atual. Você não pode corrigir o object database do fork a partir do upstream.

---

## D. Matriz de verificação (após push)

| Verificação | Comando |
| ----------- | ------- |
| Guard do índice | `uv run pytest tests/test_pii_guard.py -q` |
| Placeholders talent | `uv run pytest tests/test_talent_public_script_placeholders.py tests/test_talent_ps1_tracked_no_inline_pool.py -q` |
| Histórico completo | `uv run python scripts/pii_history_guard.py --full-history` |
| Seeds opcionais | Manter seeds **privados** em `docs/private/security_audit/PII_LOCAL_SEEDS.txt` (fora do Git). Usar `git log --all -S "…"` só na máquina do mantenedor — ver [PII_VERIFICATION_RUNBOOK.pt_BR.md](PII_VERIFICATION_RUNBOOK.pt_BR.md). |

---

## E. Editar regras de substituição

- **Arquivo:** `scripts/filter_repo_pii_replacements.txt`
- **Formato:** substituições do `git filter-repo`; linhas `#` são comentários; `regex:…==>…` para padrões.
- **Depois de editar:** volte a rodar a **seção C** (reescrita + testes) antes do próximo force-push.

---

## F. Documentos relacionados

- [GITHUB_FORK_CLONE_VISIBILITY_AND_OPERATOR_AUDIT.pt_BR.md](GITHUB_FORK_CLONE_VISIBILITY_AND_OPERATOR_AUDIT.pt_BR.md) — o que o GitHub lista (forks) vs o que **não** lista (clone por usuário); checklist mínimo do operador.
- [PII_VERIFICATION_RUNBOOK.pt_BR.md](PII_VERIFICATION_RUNBOOK.pt_BR.md) — cadência e grep manual.
- [COMMIT_AND_PR.pt_BR.md](COMMIT_AND_PR.pt_BR.md) — sem narrativas sensíveis em PR/commit.
- [ADR 0020](../adr/0020-ci-full-git-history-pii-gate.md) — gate de histórico completo na CI.
- [COLLABORATION_TEAM.pt_BR.md](../COLLABORATION_TEAM.pt_BR.md) — fluxo fork / PR do colaborador.

---

## G. O que já está neste repositório (fecho de engenharia)

Isto **já está no `main`** no arco de higiene PII (não refazer salvo mudança de política):

| Item | Onde / comportamento |
| ---- | ---------------------- |
| Scan do índice + caminhos | `tests/test_pii_guard.py` — arquivos rastreados; prefixos permitidos incluem `docs/private.example/` etc. |
| Scan de histórico completo | `scripts/pii_history_guard.py` — ignora linhas `+` sob `docs/private.example/`; placeholder LinkedIn com crase em Markdown; regex SSH ignora estilo `user@myserver.example.com` |
| Placeholders talent | `tests/test_talent_public_script_placeholders.py`, `tests/test_talent_ps1_tracked_no_inline_pool.py` |
| Arquivo de regras `filter-repo` | `scripts/filter_repo_pii_replacements.txt` — válido para `--replace-text` / `--replace-message` |
| Automação de reescrita | `scripts/run-pii-history-rewrite.ps1` — nova reescrita só se mudar regras |
| CI | Workflows correm `pii_history_guard --full-history` após testes (ver ADR 0020) |
| Docs de ops | Este arquivo, [GITHUB_FORK_CLONE_VISIBILITY_AND_OPERATOR_AUDIT.pt_BR.md](GITHUB_FORK_CLONE_VISIBILITY_AND_OPERATOR_AUDIT.pt_BR.md), ligações a partir de [PII_VERIFICATION_RUNBOOK.pt_BR.md](PII_VERIFICATION_RUNBOOK.pt_BR.md) |

**Não substitui:** backups privados teus, revisão externa (ex.: WRB), nem apagar o fork do colaborador.

---

## H. Checklist do operador — executar (assumido obrigatório até estar feito)

Ordem sugerida. **Nenhum passo é opcional** se quiseres fecho organizacional, não só “testes verdes num portátil.”

### H.1 Gate completo no PC Windows (clone canónico)

```powershell
cd C:\caminho\para\data-boar
git fetch origin
git pull origin main
.\scripts\check-all.ps1
```

Se falhar, corrige ou abre PR com âmbito fechado antes de declarar higiene de release completa.

### H.2 Confirmar CI no GitHub

1. Abrir `https://github.com/FabioLeitao/data-boar/actions`
2. Confirmar que o último workflow no **`main`** está **verde** (todos os jobs).

### H.3 Lab e clones secundários (máquinas que você controla)

Em **cada** host onde `data-boar` está clonado (ex.: Latitude, pi3b, T14, mini-bt quando acessível):

```bash
cd ~/Projects/dev/data-boar   # ou o teu caminho real
git fetch origin
git reset --hard origin/main
git fetch --prune
```

Depois correr os mesmos guards da **seção D** com `python3` se não houver `uv`:

```bash
python3 scripts/pii_history_guard.py --full-history
```

Instalar `uv` nesses hosts quando fizer sentido para igualar ao Windows.

### H.4 Fork do colaborador (fork público conhecido)

1. Listar forks:

```bash
gh api repos/FabioLeitao/data-boar/forks --paginate --jq '.[] | {owner: .owner.login, full_name, pushed_at, updated_at}'
```

2. **Você** contacta o dono do fork: histórico upstream / guards mudaram; ele deve **apagar o fork** ou **voltar a sincronizar** com o `main` atual (ver [GITHUB_FORK_CLONE_VISIBILITY_AND_OPERATOR_AUDIT.pt_BR.md](GITHUB_FORK_CLONE_VISIBILITY_AND_OPERATOR_AUDIT.pt_BR.md) e [COLLABORATION_TEAM.pt_BR.md](../COLLABORATION_TEAM.pt_BR.md)).

3. **Você não pode** apagar o fork da conta dele pelo seu login.

### H.5 Varredura na UI do GitHub (issues, PRs, discussions)

A automação **não** reescreve corpos de issue/PR. **Manualmente** pesquisa no repositório no GitHub por padrões que te importem (nomes, caminhos, palavras-chave de caso) e edita ou abre follow-up. **Não** colocar narrativa sensível em issues públicas daqui para a frente ([COMMIT_AND_PR.pt_BR.md](COMMIT_AND_PR.pt_BR.md)).

### H.6 Revisão externa (WRB ou equivalente)

- Usar runbooks e docs de produto **rastreados** como evidência.
- **Não** colar conteúdo do dossier, seeds privados ou detalhes de LAN em issues públicas ou formulários de revisão.

### H.7 Backups privados e estado da aplicação

- Comparar **offline** os seus backups ao comportamento atual **fora** deste repositório; nenhum assistente ou CI audita discos que não estejam no seu fluxo de trabalho.

### H.8 Directórios temporários de clone (higiene)

- Apagar clones temporários criados para inspecionar forks (ex.: `%TEMP%`, `/tmp`) quando o espaço ou a disciplina o exigirem.

### H.9 Opcional: `clean-slate.sh` no lab (Latitude)

Se usares `~/clean-slate.sh`: é **destrutivo** (remove o `data-boar` local e volta a clonar). Só corre quando aceitares re-download completo e o custo de `git grep` com seeds. Garante `~/.config/PII/PII_LOCAL_SEEDS.txt` antes de depender desse script.

---

## I. Impossível sem ti (limites duros)

| Limite | Porquê |
| ------ | ------ |
| Apagar ou repor o **fork de outra pessoa** | Permissões GitHub |
| **Lista de todos os usuários** que fizeram `git clone` | O GitHub não expõe isso em repos públicos |
| Provar que **Wayback** / cache / mirror de terceiros está limpo | Fora do âmbito do repo |
| **Resultado da WRB** | Processo humano |
| Verificar **bytes de backup privado** | Acesso físico / cofre |
| **mini-bt** (ou outro host) offline | Rede / energia |
| Narrativa **jurídica / RH** | Fora deste runbook |
