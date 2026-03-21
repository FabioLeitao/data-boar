# Inventário de pacotes nos hosts do homelab (Data Boar)

**Objetivo:** O repositório e o ambiente de IA **não** veem o que está instalado nas suas máquinas na LAN. Esta página lista o que a **documentação do Data Boar pressupõe** em Linux e aponta **comandos + script** para você gerar o inventário e, se quiser, colar saída **anonimizada** para análise de lacunas.

**Relacionado:** [HOMELAB_VALIDATION.pt_BR.md](HOMELAB_VALIDATION.pt_BR.md) · [TECH_GUIDE.pt_BR.md](../TECH_GUIDE.pt_BR.md) · [SECURITY.pt_BR.md](../../SECURITY.pt_BR.md)

**Documento completo (EN, tabelas e script):** [HOMELAB_HOST_PACKAGE_INVENTORY.md](HOMELAB_HOST_PACKAGE_INVENTORY.md)

---

## Resumo

- **Baseline Debian/Ubuntu (Zorin, guest Proxmox, etc.):** `python3.12`, `python3.12-venv`, `python3.12-dev`, `build-essential`, `libpq-dev`, `libssl-dev`, `libffi-dev`, `unixodbc-dev` — ver guia em inglês §1.
- **Dependências Python da aplicação:** `uv sync` / `pyproject.toml`; extras (`nosql`, etc.) conforme uso.
- **Inventário:** na raiz do repo, `bash scripts/homelab-host-report.sh` (Linux); envie saída **redigida** + papel do host + conectores que usa.
- **Go / Rust / Zig / Odin / Homebrew:** **opcionais** para o Data Boar (o produto é **Python 3.12+**); o script imprime versões se estiverem no `PATH`. Ver **§2.5** no EN.
