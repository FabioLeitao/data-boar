# Colaboração em equipe (Cursor + Git) — guia para mantenedor e contribuidor

**English:** [COLLABORATION_TEAM.md](COLLABORATION_TEAM.md)

Este guia resume **como trabalhar em conjunto** (ex.: **Fabio** como mantenedor e **Ivan** como colaborador) com **coesão**: fluxo Git, identidade nos commits, limites do assistente no Cursor e **o que configurar** no repositório (rules, `AGENTS.md`, hábitos).

**Relacionado:** [CONTRIBUTING.pt_BR.md](../CONTRIBUTING.pt_BR.md), [docs/ops/COMMIT_AND_PR.pt_BR.md](ops/COMMIT_AND_PR.pt_BR.md), [AGENTS.md](../AGENTS.md), [docs/plans/TOKEN_AWARE_USAGE.md](plans/TOKEN_AWARE_USAGE.md). Regra Cursor: **`.cursor/rules/collaboration-maintainer-contributor.mdc`**.

---

## 1. Fork vs um só repositório — o que faz sentido

| Abordagem | Vantagens | Desvantagens |
| --------- | --------- | ------------- |
| **Fork** (contribuidor com cópia sob o próprio usuário no GitHub) | Fluxo “open source” claro; bom enquanto o colaborador **aprende**; PRs do fork → repo canônico. | Exige **sincronizar** com o upstream com frequência (`fetch` + merge/rebase). |
| **Colaborador no repo canônico** (convite GitHub com permissão de escrita) | Um `origin`, menos atrito; branches `feature/…` e PRs **no mesmo repo**. | Exige confiança e disciplina de branch (não commitar direto em `main` sem combinar). |

**Sugestão prática:** começar com **fork + PR**; quando o ritmo ficar alto, **adicionar o colaborador no repositório canônico** e manter a mesma regra: **branch por tarefa** + **PR** + revisão.

**Repo canônico:** use a URL que vocês adotarem (ex.: organização ou usuário do mantenedor). Nos exemplos abaixo, `UPSTREAM_URL` é um placeholder — substituam pela URL real do remoto **oficial**.

---

## 2. Git e GitHub sabem quem commitou; o Cursor não adivinha sozinho

- **`user.name` / `user.email`** em cada máquina definem o **autor do commit**. No GitHub, isso aparece no histórico e nos PRs.
- O **assistente no Cursor** não recebe um sinal confiável do tipo “quem está no teclado”. Ele vê o **workspace**, ficheiros e o que escrevem no chat.
- **Conclusão:** coesão vem de **processo** (branches, PRs, issues) + **documentação** (`AGENTS.md`, este guia, opcionalmente labels no GitHub), não de “memória mágica” do modelo.

---

## 3. Separar “tarefas do mantenedor” vs “tarefas do colaborador”

| Mecanismo | Uso |
| --------- | --- |
| **Issues / Projects no GitHub** | Assignee **Fabio** vs **Ivan**; labels `owner:maintainer`, `owner:contributor` (ou nomes que preferirem). |
| **Nomes de branch** | Ex.: `ivan/descricao-curta`, `fabio/descricao-curta` ou só `feature/…` com assignee na PR. |
| **`docs/private/`** (gitignored) | Notas **só do mantenedor** / LAB-OP **reais** — **não** entram no clone público do colaborador da mesma forma; evita misturar “chores” pessoais com o que o Ivan precisa ler. |
| **Planos (`docs/plans/`)** | Podem continuar **só em inglês** por política do repo; quem implementa marca progresso em PR + `PLANS_TODO.md` quando fizer sentido. |

---

## 4. Comandos Git concretos

### 4.1 Colaborador (Ivan) — clone do **fork** (primeira vez)

```bash
git clone https://github.com/IVAN_USER/nome-do-fork.git
cd nome-do-fork
git remote add upstream UPSTREAM_URL
git remote -v
```

`UPSTREAM_URL` = URL HTTPS ou SSH do repositório **canônico** do Fabio.

### 4.2 Colaborador — identidade Git (obrigatório em cada máquina)

```bash
git config user.name "Nome que aparece no GitHub"
git config user.email "email@que-consta-no-GitHub"
```

Confirmação:

```bash
git config --get user.name
git config --get user.email
```

### 4.3 Colaborador — começar trabalho novo

```bash
git fetch upstream
git checkout main
git merge upstream/main
# ou: git rebase upstream/main
git checkout -b ivan/minha-feature
```

### 4.4 Colaborador — antes de abrir PR

```bash
git fetch upstream
git merge upstream/main
# resolver conflitos se houver
uv sync
uv run pytest -v -W error
git push origin ivan/minha-feature
```

No GitHub: **Open Pull Request** do fork **→** repositório canônico (`upstream`).

### 4.5 Mantenedor (Fabio) — alinhar `main` local

```bash
git checkout main
git pull origin main
```

### 4.6 Mantenedor — adicionar remote do fork do Ivan (opcional, para `fetch` da branch dele)

```bash
git remote add ivan https://github.com/IVAN_USER/nome-do-fork.git
git fetch ivan
git checkout -b review/ivan-feature ivan/ivan/minha-feature
```

(Ajustar nome da branch conforme o Ivan empurrou.)

### 4.7 Quando ambos trabalham no **mesmo** repo (colaborador convidado)

```bash
git clone UPSTREAM_URL
cd repositorio
git config user.name "..."
git config user.email "..."
git checkout main
git pull origin main
git checkout -b ivan/minha-feature
# ... commits ...
git push -u origin ivan/minha-feature
```

Política: **PR obrigatório** para `main` (branch protection no GitHub, se possível).

---

## 5. Comandos úteis de verificação (ambos)

```bash
git status
git log -3 --oneline
gh pr list --state open
```

(`gh` exige [GitHub CLI](https://cli.github.com/) autenticado.)

---

## 6. Prompts sugeridos para o Cursor (copiar e adaptar)

**No início de uma sessão (colaborador):**

> Estou no papel de **contribuidor** (Ivan). Branch atual: `ivan/…`. O mantenedor é o Fabio. Segue [AGENTS.md](AGENTS.md) e [CONTRIBUTING.pt_BR.md](../CONTRIBUTING.pt_BR.md). Não assumas acesso a `docs/private/`. Proponha alterações em commits pequenos e compatíveis com PR único para a feature X.

**No início de uma sessão (mantenedor):**

> Sou o **mantenedor**. Posso referir políticas em `docs/private/` apenas em notas locais — não sugerir colar segredos ou IPs reais em ficheiros rastreados. Prioridade: alinhar com [docs/plans/PLANS_TODO.md](plans/PLANS_TODO.md) e [`.cursor/rules/execution-priority-and-pr-batching.mdc`](../.cursor/rules/execution-priority-and-pr-batching.mdc).

**Para reduzir interferência entre pessoas:**

> Esta tarefa é **só para o colaborador Ivan** (documentação de onboarding). Não mistures com itens de homelab ou estudo do mantenedor.

**Antes de merge/release:**

> Rode a sugestão de verificação: `uv run pytest -v -W error` e, se aplicável, `scripts/check-all.ps1`. Confirma estado do Git com `git fetch` e `git status`.

**Token-aware (sessão curta):**

> **short** — uma só fatia: [descrever]. Sem expandir para outros planos.

---

## 7. Rules, skills e guidelines no repositório

| Artefato | Função |
| -------- | ------ |
| **[`AGENTS.md`](../AGENTS.md)** | Contrato global do assistente: idioma, segredos, homelab, Git/PR, testes. **Ambos** devem ler uma vez; o Ivan segue o mesmo ficheiro ao clonar. |
| **[`.cursor/rules/`](../.cursor/rules/)** | Regras automáticas ou por contexto (ex.: `git-pr-sync-before-advice.mdc`, `execution-priority-and-pr-batching.mdc`). **Colaboração:** `collaboration-maintainer-contributor.mdc`. |
| **[`.cursor/skills/`](../.cursor/skills/)** | Playbooks longos (Docker, token-aware, etc.). Use quando a tarefa combinar. |
| **[`CONTRIBUTING.md`](../CONTRIBUTING.md)** / **[`CONTRIBUTING.pt_BR.md`](../CONTRIBUTING.pt_BR.md)** | Fluxo de contribuição e testes. |
| **Este ficheiro** | Papéis, comandos e prompts — **maturidade de equipe** sem substituir o CONTRIBUTING. |

### 7.1 Ajustes opcionais quando a equipe crescer

1. **Branch protection** em `main` (ex.: exigir PR, status de CI).
2. **`CODEOWNERS`** (`.github/CODEOWNERS`) para pedir revisão automática do mantenedor em pastas críticas.
3. **Issue templates** no GitHub (“bug”, “feature”, “doc”) com checklist de testes.
4. Nova rule **`.mdc`** só se houver **regra repetida** que o CONTRIBUTING não cubra (mantê-las **curtas**).

---

## 8. O que **não** fazer

- Colocar **tokens, senhas, URLs internas com segredos** em Markdown rastreado ou em rules.
- Depender do assistente para saber **quem** está no PC sem declarar no chat ou sem Git configurado.
- Trabalhar semanas em `main` desatualizado sem `fetch upstream` / `pull`.

---

## 9. Revisão do documento

| Data | Nota |
| ---- | ---- |
| 2026-03-01 | Versão inicial (Fabio + Ivan, fork ou repo único, comandos, prompts, rules). |

Atualizem esta tabela quando mudarem URL canônica, política de branch ou nomes dos remotes.
