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

- [PII_VERIFICATION_RUNBOOK.pt_BR.md](PII_VERIFICATION_RUNBOOK.pt_BR.md) — cadência e grep manual.
- [COMMIT_AND_PR.pt_BR.md](COMMIT_AND_PR.pt_BR.md) — sem narrativas sensíveis em PR/commit.
- [ADR 0020](../adr/0020-ci-full-git-history-pii-gate.md) — gate de histórico completo na CI.
