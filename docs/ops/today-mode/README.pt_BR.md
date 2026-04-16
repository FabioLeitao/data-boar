# Modo “hoje” do operador (checklists datados)

**English:** [README.md](README.md)

**Objetivo:** Este diretório reúne **planos de dia com data** (`OPERATOR_TODAY_MODE_YYYY-MM-DD.md`), a **fila de carryover** e **como manter o “publicado” alinhado ao `pyproject.toml`** — para os checklists não ficarem defasados.

**Atalhos no chat:** escreve **`today-mode YYYY-MM-DD`** (token **só em inglês**); ver **`.cursor/rules/session-mode-keywords.mdc`**. Para **fim de bloco de trabalho ou saída do lab** (VeraCrypt / carryover / private stack opcional — não necessariamente fim do dia no calendário), usa **`block-close`**. Ritual manhã/fim de dia: **`scripts/operator-day-ritual.ps1`** (lista arquivos recentes nesta pasta).

---

## Companheiros canônicos (ler com frequência)

| Doc | Função |
| --- | ------ |
| [CARRYOVER.pt_BR.md](CARRYOVER.pt_BR.md) | **Fila viva** — promover, deferir ou fechar (sem backlog silencioso). |
| [PUBLISHED_SYNC.pt_BR.md](PUBLISHED_SYNC.pt_BR.md) | **GitHub Release + Docker Hub vs versão no repo** — atualizar após cada publish. |
| [SOCIAL_PUBLISH_AND_TODAY_MODE.pt_BR.md](SOCIAL_PUBLISH_AND_TODAY_MODE.pt_BR.md) | **Hub social privado + today-mode** — posts planeados, adiamentos, evidência ad-hoc; casa com **`docs/private/social_drafts/`** (gitignored). EN: [SOCIAL_PUBLISH_AND_TODAY_MODE.md](SOCIAL_PUBLISH_AND_TODAY_MODE.md). |
| [PRIVATE_OPERATOR_NOTES.pt_BR.md](../../PRIVATE_OPERATOR_NOTES.pt_BR.md) | Notas privadas de ritmo (`docs/private/…`) quando aplicável. |
| [OPERATOR_TODAY_MODE_TEMPLATE.pt_BR.md](OPERATOR_TODAY_MODE_TEMPLATE.pt_BR.md) | **Casca para copiar** dias novos (Bloco 0 + Fim do dia: **`block-close`** + VeraCrypt vs **`eod-sync`**). EN: [OPERATOR_TODAY_MODE_TEMPLATE.md](OPERATOR_TODAY_MODE_TEMPLATE.md). |

---

## Checklists datados (mais recente por último)

| Data | English | pt-BR |
| ---- | ------- | ----- |
| 2026-03-26 | [OPERATOR_TODAY_MODE_2026-03-26.md](OPERATOR_TODAY_MODE_2026-03-26.md) | [OPERATOR_TODAY_MODE_2026-03-26.pt_BR.md](OPERATOR_TODAY_MODE_2026-03-26.pt_BR.md) |
| 2026-03-27 | [OPERATOR_TODAY_MODE_2026-03-27.md](OPERATOR_TODAY_MODE_2026-03-27.md) | [OPERATOR_TODAY_MODE_2026-03-27.pt_BR.md](OPERATOR_TODAY_MODE_2026-03-27.pt_BR.md) |
| 2026-03-29 | [OPERATOR_TODAY_MODE_2026-03-29.md](OPERATOR_TODAY_MODE_2026-03-29.md) | [OPERATOR_TODAY_MODE_2026-03-29.pt_BR.md](OPERATOR_TODAY_MODE_2026-03-29.pt_BR.md) |
| 2026-03-30 | [OPERATOR_TODAY_MODE_2026-03-30.md](OPERATOR_TODAY_MODE_2026-03-30.md) | [OPERATOR_TODAY_MODE_2026-03-30.pt_BR.md](OPERATOR_TODAY_MODE_2026-03-30.pt_BR.md) |
| **2026-03-31** | [OPERATOR_TODAY_MODE_2026-03-31.md](OPERATOR_TODAY_MODE_2026-03-31.md) | [OPERATOR_TODAY_MODE_2026-03-31.pt_BR.md](OPERATOR_TODAY_MODE_2026-03-31.pt_BR.md) |
| **2026-04-01** | [OPERATOR_TODAY_MODE_2026-04-01.md](OPERATOR_TODAY_MODE_2026-04-01.md) | [OPERATOR_TODAY_MODE_2026-04-01.pt_BR.md](OPERATOR_TODAY_MODE_2026-04-01.pt_BR.md) |
| **2026-04-02** | [OPERATOR_TODAY_MODE_2026-04-02.md](OPERATOR_TODAY_MODE_2026-04-02.md) | [OPERATOR_TODAY_MODE_2026-04-02.pt_BR.md](OPERATOR_TODAY_MODE_2026-04-02.pt_BR.md) |
| 2026-04-06 | [OPERATOR_TODAY_MODE_2026-04-06.md](OPERATOR_TODAY_MODE_2026-04-06.md) | [English](OPERATOR_TODAY_MODE_2026-04-06.md) *(sem `.pt_BR.md`)* |
| 2026-04-08 | [OPERATOR_TODAY_MODE_2026-04-08.md](OPERATOR_TODAY_MODE_2026-04-08.md) | [English](OPERATOR_TODAY_MODE_2026-04-08.md) *(sem `.pt_BR.md`)* |
| 2026-04-09 | [OPERATOR_TODAY_MODE_2026-04-09.md](OPERATOR_TODAY_MODE_2026-04-09.md) | [English](OPERATOR_TODAY_MODE_2026-04-09.md) *(sem `.pt_BR.md`)* |
| **2026-04-10** | [OPERATOR_TODAY_MODE_2026-04-10.md](OPERATOR_TODAY_MODE_2026-04-10.md) | [OPERATOR_TODAY_MODE_2026-04-10.pt_BR.md](OPERATOR_TODAY_MODE_2026-04-10.pt_BR.md) |

Os blocos **WRB** para colar no e-mail ficam em **`docs/ops/WRB_DELTA_SNAPSHOT_*.md`**.

---

## Criar um dia novo

1. Copie **[OPERATOR_TODAY_MODE_TEMPLATE.pt_BR.md](OPERATOR_TODAY_MODE_TEMPLATE.pt_BR.md)** (ou a estrutura do **`OPERATOR_TODAY_MODE_*.md` mais recente**) e renomeie para **`OPERATOR_TODAY_MODE_YYYY-MM-DD.md`**. Mantenha o **item 5 do Bloco 0** e a linha de **Fim do dia** que emparelham **`block-close`** com VeraCrypt (**privado** **`docs/private/homelab/OPERATOR_VERACRYPT_SESSION_POLICY*.md`**) vs **`eod-sync`**.
1. Liga **`CARRYOVER.pt_BR.md`** e **`PUBLISHED_SYNC.pt_BR.md`** no Bloco 0 quando o dia mexer em release ou carryover.
1. Depois de um **publish real** (tag + GitHub Release + Docker Hub), atualiza **`PUBLISHED_SYNC.*`**, as linhas de release em **`docs/plans/PLANS_TODO.md`** se preciso, e **`python scripts/plans-stats.py --write`**.

---

## Navegação

- Índice pai: **[`docs/ops/README.pt_BR.md`](../README.pt_BR.md)** ([EN](../README.md)).
