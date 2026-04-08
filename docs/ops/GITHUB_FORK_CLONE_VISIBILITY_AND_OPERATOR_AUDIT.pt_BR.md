# GitHub: visibilidade de fork, visibilidade de clone e o que você precisa fazer no seu lado

**English:** [GITHUB_FORK_CLONE_VISIBILITY_AND_OPERATOR_AUDIT.md](GITHUB_FORK_CLONE_VISIBILITY_AND_OPERATOR_AUDIT.md)

**Objetivo:** Dizer **com precisão** o que o GitHub expõe (e o que **não** expõe), para você **não assumir** que existe “lista de quem fez `git clone`.” Use junto de **[PII_DEFINITIVE_REMEDIATION.pt_BR.md](PII_DEFINITIVE_REMEDIATION.pt_BR.md)** para os passos de limpeza.

---

## 1. Forks — **auditáveis**

O GitHub expõe **forks públicos** de um repositório público. Dá para listar.

**GitHub CLI** (autenticado):

```bash
gh api repos/FabioLeitao/data-boar/forks --paginate --jq '.[] | {owner: .owner.login, full_name, pushed_at, updated_at}'
```

**Browser:** repositório → **Insights** → **Network** (grafo de forks), ou o contador de **Forks** na página inicial do repo.

**Quem pode ter cópia completa:** a base de objetos Git de cada fork no GitHub, até o dono apagar o fork ou alinhar com o seu `main` atual.

**Sua ação mínima:** identificar cada fork; avisar o dono se um fork desatualizado ainda carrega histórico pré-remediação — ele precisa apagar ou recriar / dar `reset` a partir do seu `main`; **você não apaga o fork de outra conta pelo seu login.**

---

## 2. `git clone` — **não** há auditoria por usuário no GitHub

Para repositório **público**, o GitHub **não** publica:

- lista de usuários do GitHub que rodaram `git clone`
- endereços IP de `git clone` anônimo
- inventário máquina a máquina de clones

**Por quê:** `git clone` em `https://github.com/...` ou `git@github.com:...` **não** gera um “registro de clones” que o dono do repo possa baixar por completo.

**O que existe para o dono (limitado):**

- **Insights → Traffic:** contagens **agregadas** de clones (ex.: por dia), **não** “quem.” A disponibilidade depende do produto GitHub e do seu papel no repo.
- **Stars / watchers** mostram contas que interagiram **nessas ações** — não são equivalentes a clone.

**Quem pode ter cópia completa:** qualquer pessoa que clonou enquanto o histórico antigo estava no `origin` (qualquer máquina, qualquer mirror). Você **não** obtém lista completa pelo GitHub.

**Sua ação mínima:** tratar “clones anônimos” como **fora do alcance** de auditoria exaustiva; focar em **forks visíveis**, **colaboradores que você conhece** e **máquinas que você controla** (ver §4).

---

## 3. Mirrors e CI

- **Mirrors de terceiros** (se existirem) ficam fora da lista de forks do GitHub.
- Checkouts do **GitHub Actions** são efêmeros; não substituem “quem tem clone local.”
- **Caches** longos em outro lugar (proxy corporativo, backup pessoal) não aparecem no GitHub.

---

## 4. Checklist mínimo — **só o que você precisa fazer aí**

| Passo | Ação |
| ----- | ---- |
| 1 | Rodar **`gh api .../forks`** (ou a UI web) e **anotar** cada `full_name` e `pushed_at`. |
| 2 | Para cada fork que ainda importa: **avisar o dono** — alinhar com o `main` atual ou apagar o fork (você não faz isso pelo login dele). |
| 3 | **Inventário de seus próprios dispositivos** onde você (ou quem você confia) clonou o repo: PC dev, notColleague-Soks, lab — **liste em notas privadas**, não neste doc público. Em cada um: `git fetch origin && git reset --hard origin/main` quando quiser igualar ao GitHub. |
| 4 | **Opcional:** abrir **Insights → Traffic** no GitHub (se disponível) só para **tendência** — não é lista de quem clonou. |
| 5 | Aceitar que **clones anônimos** de repo público **não** são auditáveis por completo; redução de risco é **histórico canônico reescrito + forks que você enxerga + máquinas conhecidas**. |

---

## 5. Documentos relacionados

- [PII_DEFINITIVE_REMEDIATION.pt_BR.md](PII_DEFINITIVE_REMEDIATION.pt_BR.md) — force-push, `filter-repo`, reset de clone.
- [PII_VERIFICATION_RUNBOOK.pt_BR.md](PII_VERIFICATION_RUNBOOK.pt_BR.md) — cadência e seeds locais (arquivos privados).
