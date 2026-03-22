# Ações manuais do operador (evidências, homelab, estudo)

**Finalidade:** Um único documento rastreado para o **seu** trabalho que o agente não faz sozinho: capturar evidências, passos de homelab, fotos/saídas para contexto e **como** janelas de estudo/certificação convivem com readiness de produção. Sem segredos aqui—conteúdo sensível em **`docs/private/`** (gitignored).

**English:** [OPERATOR_MANUAL_ACTIONS.md](OPERATOR_MANUAL_ACTIONS.md)

---

## 1. Janela de estudo e certificação (2026)

- **Prioridade até ~meados de abril de 2026:** **Claude Certified Architect (CCA)** — alinha com como você constrói com Claude (Agent SDK, MCP, Claude Code, desenho em estilo produção). Visão geral não oficial: [How to Become a Claude Certified Architect — guide](https://aitoolsclub.com/how-to-become-a-claude-certified-architect-complete-guide/). Preparação oficial: **Anthropic Academy** (Skilljar). Taxas e formato do exame seguem a Anthropic no registro.
- **Em paralelo (fio fino):** Manter a **faixa prioritária A** com **cadência mínima saudável** (Dependabot, Docker Scout, `check-all` antes de merges) para **M-TRUST** não degradar—ver [PLANS_TODO.md](../plans/PLANS_TODO.md) ordens **–1** / **–1b**.
- **Depois de meados de abril (ou após uma primeira tentativa de CCA):** Voltar o **foco principal de estudo** aos **cursos de cyber já pagos** (ex. lista CWL em [PORTFOLIO_AND_EVIDENCE_SOURCES.md](../plans/PORTFOLIO_AND_EVIDENCE_SOURCES.md) §3.2), começando por **BTF** → **C3SA** como já recomendado.
- **Se a primeira tentativa de exame não passar:** Tratar como **aprendizado**—você ainda ganha **profundidade de arquitetura e de ferramentas** útil para este repositório. Manter anotações em `docs/private/` e planejar **nova tentativa mais tarde no ano**, de forma oportunística junto com outros cursos; ajustar o preparo e tentar de novo—sem ciclo de culpa.

O racional de sequência também está em [SPRINTS_AND_MILESTONES.pt_BR.md](../plans/SPRINTS_AND_MILESTONES.pt_BR.md) §3.1 e [PORTFOLIO_AND_EVIDENCE_SOURCES.md](../plans/PORTFOLIO_AND_EVIDENCE_SOURCES.md) §3.0.

---

## 2. Evidências que você pode juntar para o agente (manual)

**Não** colar senhas ou chaves privadas no chat. Prefira:

| Ação | Onde guardar | Por quê |
| ---- | ------------ | ------- |
| Inventário de homelab (hosts, papéis, IPs redigidos se preciso) | `docs/private/homelab/` conforme [PRIVATE_OPERATOR_NOTES.md](../PRIVATE_OPERATOR_NOTES.md) | O agente pode `read_file` sem `@`. |
| Fotos de equipamento, rack, etiquetas (opcional) | Mesma árvore privada; descrever num `.md` o que cada imagem mostra | Contexto visual para topologia. |
| Saídas de CLI (`ssh`, `curl`, resumos de scan) | Colar numa nota datada em `docs/private/` ou log de sessão | Depuração reproduzível. |
| Conclusão de curso / certificado | PDF ou screenshot em `docs/private/`; acrescentar linha no PORTFOLIO §3 quando quiser no narrative de CV | Alinha tese/pitch. |

---

## 3. Homelab e validação

- **Critérios:** [HOMELAB_VALIDATION.pt_BR.md](HOMELAB_VALIDATION.pt_BR.md) §1–§12 ([EN](HOMELAB_VALIDATION.md)).
- **O que o agente pode fazer:** Sugerir comandos, ler docs **rastreados**, ler **`docs/private/`** quando você mantém—**não** SSH sozinho sem o seu terminal.
- **Snapshot para o chat:** Manter **`docs/private/WHAT_TO_SHARE_WITH_AGENT.md`** atualizado (não versionado). Layout e dicas: [PRIVATE_OPERATOR_NOTES.pt_BR.md](../PRIVATE_OPERATOR_NOTES.pt_BR.md), [docs/private.example/author_info/README.md](../private.example/author_info/README.md).

---

## Ver também

- [SPRINTS_AND_MILESTONES.pt_BR.md](../plans/SPRINTS_AND_MILESTONES.pt_BR.md) §3.1 — faixa de estudo no quadro de sprints
- [TOKEN_AWARE_USAGE.md](../plans/TOKEN_AWARE_USAGE.md) — disciplina estudo vs código no mesmo dia (doc EN; parcial pt-BR onde existir)
- [OPERATOR_LAB_DOCUMENT_MAP.pt_BR.md](OPERATOR_LAB_DOCUMENT_MAP.pt_BR.md) — onde cada doc de lab mora
