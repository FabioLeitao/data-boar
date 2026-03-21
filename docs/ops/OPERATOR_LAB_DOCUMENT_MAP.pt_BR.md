# Mapa da documentação do lab (LAB-PB vs LAB-OP)

**Objetivo:** Índice **versionado** para achar **o que fica onde**. **Sem** hostnames reais, IPs ou credenciais — isso fica em **`docs/private/`** (gitignored).

**English:** [OPERATOR_LAB_DOCUMENT_MAP.md](OPERATOR_LAB_DOCUMENT_MAP.md)

---

## Taxonomia (resumo)

| Código | Significado | Mnemónico |
| ------ | ----------- | --------- |
| **LAB‑PB** | Homelab **Playbook** — guias **públicos** | **P**lay**B**ook · **Pu**blic |
| **LAB‑OP** | Homelab **operador** — **a sua** infra real (**só local**) | **OP**erador — nome pode ser revisto; ver **`LAB_TAXONOMY.md`** em `docs/private/homelab/` |

**No chat:** “homelab” costuma ser **LAB‑OP**. Diga **LAB‑PB** ou “playbook homelab” para **só** docs públicos.

---

## LAB‑PB — público (GitHub)

| Documento | Função |
| --------- | ------ |
| **[HOMELAB_VALIDATION.md](HOMELAB_VALIDATION.md)** · [pt-BR](HOMELAB_VALIDATION.pt_BR.md) | Playbook de validação, §9 multi-host, ordem **–1L** |
| **[OS_COMPATIBILITY_TESTING_MATRIX.md](OS_COMPATIBILITY_TESTING_MATRIX.md)** | Matriz de SO / musl / arch |
| **[PRIVATE_OPERATOR_NOTES.md](../PRIVATE_OPERATOR_NOTES.md)** | Política `docs/private/` |
| **[../plans/PLANS_TODO.md](../plans/PLANS_TODO.md)** | Sequência e tiers |
| **[../plans/TOKEN_AWARE_USAGE.md](../plans/TOKEN_AWARE_USAGE.md)** | Sessões token-aware |
| **`AGENTS.md`** · **`.cursor/rules/`** | Comportamento do agente |

---

## LAB‑OP — privado (local, **não** no GitHub)

**Pasta:** **`docs/private/homelab/`** (e raiz de **`docs/private/`** para notas soltas).

| Ficheiro em `homelab/` | Função |
| ---------------------- | ------ |
| **`LAB_TAXONOMY.md`** | LAB‑PB vs LAB‑OP; lembrete para rever nome LAB‑OP |
| **`OPERATOR_SYSTEM_MAP.md`** | Mapa mestre (hardware + acessos + software) |
| **`AGENT_LAB_ACCESS.md`** | SSH, API, `P:`, relatórios |
| **`OPERATOR_RETEACH.md`** | Lacunas B1–B6 |
| **`HARDWARE_CATALOG.md`** | Foco hardware |
| **`iso-inventory.md`** | Inventário de ISOs |

**Raiz `docs/private/`:** também **`CONTEXT_ACADEMIC_AND_FAMILY.md`** (trabalho [redacted] + planos académicos — preencher quando quiser).

**Modelo:** **`docs/private.example/`** → copiar para **`docs/private/`**.

---

## Matizar + GTD (token-aware)

- Sessões curtas: um alvo por vez — ver **[TOKEN_AWARE_USAGE.md](../plans/TOKEN_AWARE_USAGE.md)**.
- Toolchains / Selenium / bibliotecas no LAB‑OP: atualizar **`OPERATOR_SYSTEM_MAP.md`** §4 e **`WHAT_TO_SHARE_WITH_AGENT.md`** conforme for instalando.
