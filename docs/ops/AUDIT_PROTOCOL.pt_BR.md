**English:** [AUDIT_PROTOCOL.md](AUDIT_PROTOCOL.md)

# Protocolo de auditoria — bancada, ritual e integridade

Este arquivo é o **registro durável** dos acordos operador–agente sobre **como** mantemos o repositório confiável: **bancada** limpa (só ferramentas que funcionam e estão ligadas a algum fluxo), mudanças de **ritual** (contratos de processo) e **integridade** quando alguém pede para contornar barreiras de qualidade.

Complementa (não substitui) **[`TOKEN_AWARE_SCRIPTS_HUB.pt_BR.md`](TOKEN_AWARE_SCRIPTS_HUB.pt_BR.md)** (o que existe em **`scripts/`**), **[`CONTRIBUTING.md`](../../CONTRIBUTING.md)** / **[`COMMIT_AND_PR.pt_BR.md`](COMMIT_AND_PR.pt_BR.md)** (disciplina de PR e merge) e **[`PII_PUBLIC_TREE_OPERATOR_GUIDE.pt_BR.md`](PII_PUBLIC_TREE_OPERATOR_GUIDE.pt_BR.md)** (segurança da árvore pública).

---

## 1. Regra da bancada (bancada estilo Adam Savage)

**Princípio:** Ferramenta que **não funciona**, **não está documentada** e **não é alcançável** a partir de skills, rules, testes ou runbooks do operador **não fica na bancada**.

| Ação | Quando |
| ---- | ------ |
| **Remover** | Nenhum hit de `rg` fora do próprio arquivo (e sem dependência em CI/teste); wrapper duplicado e obsoleto; script quebrado sem caminho de manutenção. |
| **Amarrar (wire)** | O script fica: inclua linha em **`TOKEN_AWARE_SCRIPTS_HUB.md`** (e **`.pt_BR.md`**) ou link em runbook / skill / teste existente para a próxima sessão achar. |
| **Quarentena** | Experimental: só com nota explícita neste arquivo na **§3 Changelog** e linha no hub em **Nicho / avançado** (ou cópia só em **`docs/private/`** se não puder ir para o `origin`). |

**Comando de descoberta (assistentes):** na raiz do repo, busque pelo basename, por exemplo `rg -F "nome-do-script.ps1"` e `rg -F "nome_script.py"`.

---

## 2. Mudanças de ritual ou contrato (registrar aqui antes de fechar o chat)

Registre uma linha na **§3 Changelog** **antes** de encerrar o chat ou o PR que:

- Adiciona, remove ou renomeia **palavra-chave de sessão** (`.cursor/rules/session-mode-keywords.mdc`).
- Altera rules **always-on** ou de alto impacto em **`.cursor/rules/*.mdc`** que definem contrato operador–agente.
- Muda o formato do **gate** **check-all** / **pre-commit** / **CI** (o que roda antes do merge).
- Introduz novo script de **caminho de ouro** ou deprecia um (ver **`check-all-gate.mdc`**).

Cada linha do changelog: **data (ISO)**, **mudança**, **onde** (caminhos), **risco** (nenhum / baixo / médio), **follow-up** (se houver).

---

## 3. Changelog

| Data | Mudança | Onde | Risco | Follow-up |
| ---- | ------- | ---- | ----- | --------- |
| 2026-04-28 | Criação deste protocolo; **limpeza da bancada**: remoção de `scripts/qa_kill_scan.py`, `scripts/export_legal_cartas_advogado_pdf.py`, `scripts/check_name_availability.py` (sem referências no repo; one-off / fluxo que pertence a **`docs/private/`**); **documentação** de `strip_workstation_codename_public_index.py` e `replace_public_workstation_codename_token.py` em **`TOKEN_AWARE_SCRIPTS_HUB.md`**. | Este arquivo; `scripts/`; `TOKEN_AWARE_SCRIPTS_HUB*.md` | Baixo | Preferir **`check-all`** antes do merge; gate completo inalterado. |

---

## 4. Doutrina NASA e “warning de integridade”

**Doutrina (informal):** Tratar regras de voo a sério: **não pular** a verificação acordada (**`check-all`**, **`pre-commit`**, **`pytest`**, guardas de PII) no `origin` sem decisão explícita de mantenedor registrada em PR ou aqui.

**Warning de integridade (assistentes):** Se o Founder (ou outro operador) pedir algo que **viole** essa doutrina — por exemplo **merge sem CI**, **commit com guardas vermelhos**, **`--no-verify`**, **desativar teste de segurança** ou **burlar política de PII** — o assistente deve:

1. **Parar** e emitir um **warning de integridade** curto: o que foi pedido, qual regra ou gate quebra, e o **caminho seguro** (rodar o gate, corrigir a falha ou estreitar o escopo).
2. **Não** descrever um gate contornado como “feito” no chat nem em docs rastreados.
3. **Só seguir** o caminho arriscado se o operador responder com **exceção explícita** para aquele escopo (e o assistente ainda registra em **§3 Changelog** quando a exceção virar política ou hábito do repo).

Esta seção **não** bloqueia fluxos **só lab** ou **isolados no PC de desenvolvimento** já documentados em outros lugares (por exemplo **`PRIMARY_WINDOWS_WORKSTATION_PROTECTION.md`**, **`PII_PUBLIC_TREE_OPERATOR_GUIDE.md`**); ela bloqueia **bypass silencioso** de qualidade no caminho **público** de integração.

---

## Relacionado

- **[`TOKEN_AWARE_SCRIPTS_HUB.pt_BR.md`](TOKEN_AWARE_SCRIPTS_HUB.pt_BR.md)** — inventário e ligação dos scripts
- **[`.cursor/rules/repo-scripts-wrapper-ritual.mdc`](../../.cursor/rules/repo-scripts-wrapper-ritual.mdc)** — preferir wrappers documentados primeiro
- **[`CURSOR_AGENT_POLICY_HUB.pt_BR.md`](CURSOR_AGENT_POLICY_HUB.pt_BR.md)** — mapa de rules e skills
