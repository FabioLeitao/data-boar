# Notas privadas do operador (fora do Git / GitHub)

**Objetivo:** Onde guardar **dados reais** do homelab (hostnames, IPs, inventário) vs. documentação **pública** genérica.

**Documento completo (EN):** [PRIVATE_OPERATOR_NOTES.md](PRIVATE_OPERATOR_NOTES.md)

## Resumo

- **`docs/private/`** está no **`.gitignore`** — **não** vai para o GitHub. Confirme com `git check-ignore -v docs/private/…`.
- **`docs/private/homelab/`** — inventário **real** (rede, hosts, UPS, solar, opcional **`iso-inventory.md`** com listagem de ISOs que **você** capturou por SSH/`ls`/script no portátil de lab — nunca versionado no GitHub).
- **`docs/private/author_info/`** — dados **pessoais** (CV, formação, certificações, histórico de carreira); separado do homelab para políticas de backup/sync diferentes.
- **Modelo versionado:** copie de **`docs/private.example/`** (inclui **`homelab/`** e **`author_info/`**).
- **Agentes / Cursor:** só “veem” `docs/private/` se **abrir** os ficheiros ou estiverem no workspace — divulgação local intencional; pode manter **`WHAT_TO_SHARE_WITH_AGENT.md`** na raiz de `docs/private/` com o que o assistente pode assumir.
- **Documentação rastreada:** só papéis genéricos; **sem** links Markdown para caminhos dentro de `docs/private/`; **sem** IPs/hostnames reais em ficheiros públicos.
