# Notas privadas do operador (fora do Git / GitHub)

**Objetivo:** Onde guardar **dados reais** do homelab (hostnames, IPs, inventário) vs. documentação **pública** genérica.

**Documento completo (EN):** [PRIVATE_OPERATOR_NOTES.md](PRIVATE_OPERATOR_NOTES.md)

## Resumo

- **`docs/private/`** está no **`.gitignore`** — **não** vai para o GitHub. Confirme com `git check-ignore -v docs/private/…`.
- **Recomendado:** subpasta local **`docs/private/homelab/`** para tudo que descreve **a sua** rede e máquinas; modelo em **[private.example/](private.example/README.md)**.
- **Documentação rastreada:** só papéis genéricos e exemplos ilustrativos; **sem** links Markdown para ficheiros dentro de `docs/private/`; **sem** IPs/hostnames reais.
