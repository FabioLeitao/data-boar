# Fluxo de dossiê de talento e snapshot de sincronização do pool

**English:** [TALENT_DOSSIER_AND_POOL_SYNC.md](TALENT_DOSSIER_AND_POOL_SYNC.md)

**Objetivo:** Descrever como transformar **PDFs de equipe** na árvore privada em **dossiês bilíngues de candidato** e atualizar o **snapshot de sincronização do pool**, sem precisar caçar o `scripts/` a cada sessão.

**Público:** Somente mantenedor / operador. **Não** commitar conteúdo real de `docs/private/`.

---

## Pré-requisitos (máquina local)

1. **PDFs** ficam em **`docs/private/team_info/`** (um PDF por pessoa; o nome do arquivo vira o slug do dossiê).
2. **Pasta de saída** existe ou será criada: **`docs/private/commercial/candidates/`**.
3. **Scaffold:** **`scripts/candidate-dossier-scaffold.ps1`** (rastreado no repositório).

Se esses caminhos não existirem, crie na máquina do operador apenas (veja **`docs/private.example/commercial/candidates/README.md`**).

---

## Atalho: `talent-dossier`

Faça dot-source do helper no PowerShell (opcional; inclua no **`$PROFILE`** para alias persistente):

```powershell
. "C:\caminho\para\python3-lgpd-crawler\scripts\talent-dossier.ps1"
```

**Resolução da raiz do repositório (nesta ordem):**

1. **`--repo-root <caminho>`** na linha de comando.
2. Variável de ambiente **`DATA_BOAR_REPO_ROOT`** (diretório do clone).
3. Pasta pai de **`scripts/`** onde está **`talent-dossier.ps1`** (padrão portátil).

---

## Subcomandos

| Subcomando | O que faz |
| ---------- | --------- |
| **`next`** (padrão) | Escolhe o primeiro PDF **pendente**: que ainda **não** tem **`slug.md`** e **`slug.pt_BR.md`** em `candidates/`. Roda o scaffold. Opcionalmente repete até não haver PDFs pendentes. |
| **`list`** / **`status`** | Lista PDFs pendentes e se cada um está **MISSING** ou **PARTIAL** (só um idioma). |
| **`network`** / **`export-network`** / **`exportmesh`** | Executa **`scripts/export_talent_relationship_mermaid.py`** para atualizar exportações do mapa de relacionamentos. |

---

## Flags comuns (`next`)

| Flag | Efeito |
| ---- | ------ |
| **`--advisor-remote`** | Repassa **`-AdvisorRemote`** ao scaffold (padrão remoto / não presencial em cliente). |
| **`--caution`** / **`--low-priority-caution`** | Repassa **`-LowPriorityCaution`** (guardrails extras no dossiê gerado). |
| **`--no-loop`** | Gera **um** dossiê e para (o padrão do **`next`** percorre todos os pendências). |
| **`--dry-run`** | Mostra o próximo PDF que seria processado; **não** grava arquivos. |
| **`--overwrite`** | Permite substituir `slug.md` / `slug.pt_BR.md` existentes (usar com cuidado). |
| **`--operator-relationship <TAG>`** | Repassado ao scaffold (tag manual de vínculo quando a inferência pelo nome não basta). |

**Exemplos:**

```powershell
talent-dossier next --advisor-remote --caution
talent-dossier list
talent-dossier next --no-loop --dry-run
```

---

## Snapshot de sincronização do pool

Depois que o **`next`** completa pelo menos uma geração em loop, o helper executa **`scripts/generate_pool_sync_snapshot.py`** para que **`docs/private/commercial/POOL_SYNC_SNAPSHOT_YYYY-MM-DD.md`** reflita PDFs vs arquivos de dossiê **naquela data**.

Você pode rodar o gerador manualmente:

```powershell
uv run python scripts/generate_pool_sync_snapshot.py --repo-root . --date 2026-04-02
```

---

## Scripts e documentos relacionados

| Item | Função |
| ---- | ------ |
| **`scripts/ats.ps1`** + **`scripts/ats-profile.ps1`** | Atalhos separados de **ATS / pool** (importar, escanear, listar). Não substituem a geração de dossiê; são complementares. |
| **`docs/TALENT_POOL_LEARNING_PATHS.pt_BR.md`** | **Arquétipos de papel** (A–F) públicos; sem dados pessoais. |
| **`docs/ops/LINKEDIN_ATS_PLAYBOOK.pt_BR.md`** | Playbook público **LinkedIn + ATS** (headline, habilidades, cadência, contexto de SSI). |
| **`docs/private.example/commercial/candidates/LEARNING_ROADMAP_TEMPLATE.md`** | Modelo de roteiro de aprendizado **privado** por pessoa (não commitado). |

---

## Revisão

| Data | Nota |
| ---- | ---- |
| 2026-04-02 | Runbook inicial; raiz do repo portátil para `talent-dossier.ps1`. |
