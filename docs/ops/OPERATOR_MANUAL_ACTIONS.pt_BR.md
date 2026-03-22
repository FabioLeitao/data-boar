# Ações manuais do operador (evidências, homelab, estudo)

**Finalidade:** Um único documento rastreado para o **seu** trabalho que o agente não faz sozinho: capturar evidências, passos de homelab, fotos/saídas para contexto e **como** janelas de estudo/certificação convivem com readiness de produção. Sem segredos aqui—conteúdo sensível em **`docs/private/`** (gitignored).

**English:** [OPERATOR_MANUAL_ACTIONS.md](OPERATOR_MANUAL_ACTIONS.md)

---

## 1. Janela de estudo e certificação (2026)

- **Foco principal:** **Anthropic Academy** (cursos gratuitos no Skilljar; índice: [Anthropic courses](https://docs.claude.com/en/docs/resources/courses)) — sequência em [PORTFOLIO_AND_EVIDENCE_SOURCES.md](../plans/PORTFOLIO_AND_EVIDENCE_SOURCES.md) §3.0. **Cursor** é a **ferramenta de entrega**; **prova para stakeholders** = **releases + narrativa de compliance + este repositório**. **CCA** é **exame posterior** quando você atingir a barra de experiência da Anthropic — **sem** meta fixa em abril. Links: página CCA no Skilljar + [guia](https://aitoolsclub.com/how-to-become-a-claude-certified-architect-complete-guide/) não oficial.
- **Em paralelo (fio fino):** Manter a **faixa prioritária A** com **cadência mínima saudável** (Dependabot, Docker Scout, `check-all` antes de merges) para **M-TRUST** não degradar—ver [PLANS_TODO.md](../plans/PLANS_TODO.md) ordens **–1** / **–1b**.
- **Entrelaçar / depois do ritmo Academy:** **Cursos de cyber já pagos** (lista CWL em [PORTFOLIO_AND_EVIDENCE_SOURCES.md](../plans/PORTFOLIO_AND_EVIDENCE_SOURCES.md) §3.2), começando por **BTF** → **C3SA** como já recomendado.
- **Opcional:** **certificados de conclusão** de cursos terceiros (ex. Cursor em Coursera/Codecademy) para CV — **não** são credenciais oficiais Cursor/Anthropic.
- **Se uma tentativa de CCA não passar:** Tratar como **aprendizado**; anotações em `docs/private/`; **nova tentativa** depois — o preparo ainda apoia este repositório.

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
