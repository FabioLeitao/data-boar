# Limpeza de branches Git e imagens Docker (fluxo seguro)

**English:** [BRANCH_AND_DOCKER_CLEANUP.md](BRANCH_AND_DOCKER_CLEANUP.md)

**Objetivo:** Liberar espaço e reduzir ruído **sem** perder histórico que já está no `main`, e sem apagar trabalho não integrado. **Apagar uma branch não apaga commits** que já foram mergeados no `main` — eles permanecem no histórico. Só há risco para commits **exclusivos** no topo de uma branch **não mergeada**, se você apagá-la sem backup.

**Repositórios:** O trabalho cotidiano é no **`FabioLeitao/data-boar`** (`origin`). O remote **`python3-lgpd-crawler-legacy-and-history-only`** é legado; trate as branches dele separadamente.

---

## 1. Git: atualizar e ver o que é seguro apagar localmente

Na raiz do repositório:

```powershell
git fetch origin --prune
git branch --show-current
git branch --merged origin/main
git branch --no-merged origin/main
```

**Regras:**

- **Não apague** branches listadas em `--no-merged` sem revisar (work in progress ou abandonado de propósito).
- **Não apague** a branch em que você está; mude antes: `git checkout main`.
- Alinhe o `main` antes: `git pull origin main`.

**Apagar uma branch local mergeada:**

```powershell
git branch -d nome-da-branch
```

**Forçar** (só se aceitar perder commits não mergeados):

```powershell
git branch -D nome-da-branch
```

---

## 2. GitHub (`data-boar`): branches remotas obsoletas

```powershell
gh api repos/FabioLeitao/data-boar/branches --paginate -q ".[].name"
gh pr list --repo FabioLeitao/data-boar --state open
git fetch origin
git log origin/main..origin/NOME-DA-BRANCH
```

- Log **vazio** → em geral seguro apagar a branch remota (histórico já no `main`).
- Log **não vazio** → há commits únicos; faça merge ou cherry-pick antes, ou abandone de propósito.

**Apagar branch remota:**

```powershell
git push origin --delete NOME-DA-BRANCH
```

---

## 3. Docker: política de retenção (Data Boar)

Manter cerca de **dois** **digests** de imagem localmente, por exemplo:

1. `fabioleitao/data_boar:latest` ou a tag semver em uso (ex.: `1.6.2`).
2. **Uma versão anterior** para comparação ou rollback rápido.

Versões mais antigas podem ser removidas; use `docker pull` no Hub quando precisar de histórico.

```powershell
docker images --format "table {{.Repository}}\t{{.Tag}}\t{{.ID}}\t{{.CreatedSince}}\t{{.Size}}" | Select-String -Pattern "data_boar|fabioleitao/data_boar"
docker rmi fabioleitao/data_boar:TAG_ANTIGA
docker image prune -f
docker builder prune -f
```

---

## 4. Documentos relacionados

- [COMMIT_AND_PR.md](../COMMIT_AND_PR.md) · [REMOTES_AND_ORIGIN.md](../REMOTES_AND_ORIGIN.md) · [DOCKER_SETUP.md](../DOCKER_SETUP.md) · [HOMELAB_VALIDATION.md](../HOMELAB_VALIDATION.md) · [PLANS_TODO.md](../plans/PLANS_TODO.md)
