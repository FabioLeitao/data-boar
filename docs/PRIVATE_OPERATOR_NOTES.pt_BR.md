# Notas privadas do operador (fora do Git / GitHub)

**Objetivo:** Onde guardar **dados reais** do homelab (hostnames, IPs, inventário) vs. documentação **pública** genérica.

**Documento completo (EN):** [PRIVATE_OPERATOR_NOTES.md](PRIVATE_OPERATOR_NOTES.md)

## Resumo

- **`docs/private/`** está no **`.gitignore`** — **não** vai para o GitHub. Confirme com `git check-ignore -v docs/private/…`.
- **`docs/private/homelab/`** — inventário **real** (rede, hosts, **alias SSH `Host`** para o portátil/servidor de lab, UPS, solar, opcional **`iso-inventory.md`**). **Fluxo por defeito:** o assistente corre **`ssh <alias> '…'`** no **terminal integrado** deste PC (não tem rede própria à sua LAN); **não** commitar `~/.ssh/config` nem chaves.
- **`docs/private/author_info/`** — dados **pessoais** (CV, formação, certificações, histórico de carreira); separado do homelab para políticas de backup/sync diferentes.
- **Modelo versionado:** copie de **`docs/private.example/`** (inclui **`homelab/`** e **`author_info/`**).
- **Agentes / Cursor:** `docs/private/` é **contexto do workspace** (fora do GitHub), não “só se `@`”. O assistente deve usar **`read_file`** em caminhos relevantes (ex. **`homelab/AGENT_LAB_ACCESS.md`**) em tarefas de homelab / API / `P:` — **`@` opcional**. Conteúdo pode ir para a stack do Cursor (ver termos). **Palavras-passe / chaves:** **Bitwarden** + placeholders.
- **Partilhar:** manter **`WHAT_TO_SHARE_WITH_AGENT.md`** e **`homelab/`** atualizados. Para **exigir** só com `@`, usar **`.cursorignore`** em `docs/private/` — **não** é o defeito deste repo.
- **`docs/private/homelab/OPERATOR_SYSTEM_MAP.md`** — mapa mestre: hardware + acessos + software + diagrama Mermaid (gitignored).
- **`docs/private/homelab/OPERATOR_RETEACH.md`** — lacunas (B1–B6); **`read_file`** após o mapa (gitignored).
- **Windows — disco `P:` (pCloud):** no mesmo PC do Cursor, o assistente pode listar/ler **`P:\...`** no terminal ou com caminhos absolutos se o cliente pCloud estiver montado; **não** commitar caminhos reais em ficheiros rastreados.
- **Lint Markdown privado (opcional):** `uv run pytest --include-private` e `fix_markdown_sonar.py --include-private` — [TESTING.md](TESTING.md).
- **Documentação rastreada:** só papéis genéricos; **sem** links Markdown para caminhos dentro de `docs/private/`; **sem** IPs/hostnames reais em ficheiros públicos.
