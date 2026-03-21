# Notas privadas do operador (fora do Git / GitHub)

**Idioma:** Texto deste resumo em **português do Brasil (pt-BR)** — vocabulário brasileiro (**arquivo**, **compartilhar**, **seção**, **padrão** em TI), não português europeu (*ficheiro*, *partilhar*, *secção*, *por defeito*).

**Objetivo:** Onde guardar **dados reais** do homelab (hostnames, IPs, inventário) vs. documentação **pública** genérica.

**Documento completo (EN):** [PRIVATE_OPERATOR_NOTES.md](PRIVATE_OPERATOR_NOTES.md)

- **Mapa LAB-PB / LAB-OP (rastreado):** [OPERATOR_LAB_DOCUMENT_MAP.pt_BR.md](ops/OPERATOR_LAB_DOCUMENT_MAP.pt_BR.md)

## Resumo

- **Idioma no chat (preferência):** respostas em **pt-BR conciso**; **inglês** para caminhos do repo, tipos de commit, nomes de código/API/CLI e termos técnicos habituais em EN. Pode **alternar pt-BR e EN na mesma frase** — o assistente acompanha. Para **poupar tokens:** diga **`short`** ou **`token-aware`** (mantém-se **em inglês**, como os outros atalhos).
- **Atalhos / taxonomia de sessão só em inglês:** use as palavras tal qual: **`deps`**, **`feature`**, **`homelab`**, **`docs`**, **`houseclean`**, **`backlog`**, **`pmo-view`**, etc. O resto da frase pode ser pt-BR. Regras em **`.cursor/rules/session-mode-keywords.mdc`** ficam **só em EN**. Detalhe: **§5.1** em [PRIVATE_OPERATOR_NOTES.md](PRIVATE_OPERATOR_NOTES.md); **[AGENTS.md](../AGENTS.md)** (primeiros bullets).
- **`docs/private/`** está no **`.gitignore`** — **não** vai para o GitHub. Confirme com `git check-ignore -v docs/private/…`.
- **`docs/private/homelab/`** — inventário **real** (rede, hosts, **alias SSH `Host`** para o portátil/servidor de lab, UPS, solar, opcional **`iso-inventory.md`**). **Fluxo padrão:** o assistente **executa** **`ssh <alias> '…'`** no **terminal integrado** deste PC (não tem rede própria à sua LAN); **não** commitar `~/.ssh/config` nem chaves.
- **`docs/private/author_info/`** — dados **pessoais** (CV, formação, certificações, histórico de carreira); separado do homelab para políticas de backup/sync diferentes.
- **Modelo versionado:** copie de **`docs/private.example/`** (inclui **`homelab/`** e **`author_info/`**).
- **Agentes / Cursor:** `docs/private/` é **contexto do workspace** (fora do GitHub), não “só se `@`”. O assistente deve usar **`read_file`** em caminhos relevantes (ex. **`homelab/AGENT_LAB_ACCESS.md`**) em tarefas de homelab / API / `P:` — **`@` opcional**. Conteúdo pode ir para a stack do Cursor (ver termos). **Palavras-passe / chaves:** **Bitwarden** + placeholders.
- **Compartilhar contexto:** manter **`WHAT_TO_SHARE_WITH_AGENT.md`** e **`homelab/`** atualizados. Para **exigir** só com `@`, usar **`.cursorignore`** em `docs/private/` — **não** é o **padrão** deste repo.
- **`docs/private/homelab/OPERATOR_SYSTEM_MAP.md`** — mapa mestre: hardware + acessos + software + diagrama Mermaid (gitignored).
- **`docs/private/homelab/OPERATOR_RETEACH.md`** — lacunas (B1–B6); **`read_file`** após o mapa (gitignored).
- **Windows — disco `P:` (pCloud):** no mesmo PC do Cursor, o assistente pode listar/ler **`P:\...`** no terminal ou com caminhos absolutos se o cliente pCloud estiver montado; **não** commitar caminhos reais em **arquivos** rastreados.
- **Lint Markdown privado (opcional):** `uv run pytest --include-private` e `fix_markdown_sonar.py --include-private` — [TESTING.md](TESTING.md).
- **Documentação rastreada:** só papéis genéricos; **sem** links Markdown para caminhos dentro de `docs/private/`; **sem** IPs/hostnames reais em **arquivos** públicos.
