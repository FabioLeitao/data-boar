# Laboratorio: "completão" vs CI / pytest

**English:** [LAB_COMPLETAO_RUNBOOK.md](LAB_COMPLETAO_RUNBOOK.md)

**Objetivo:** Definir o que é **completão** neste projeto: **rodar o produto** (CLI, API, web) nos **hosts do lab**, via **SSH**, com **registo** de resultados — não é a mesma coisa que só **`pytest`** ou **`.\scripts\check-all.ps1`** no PC de desenvolvimento.

**Relação:**

| Camada | O que é | Comando típico |
| ------ | ------- | ---------------- |
| **CI / unitários e guards** | Reproduzível, GitHub, sem segredos LAN | workflow **CI**, **pytest** |
| **Gate no PC dev** | Pre-commit + testes antes do merge | **`.\scripts\check-all.ps1`** |
| **Completão no lab** | Produto + runtime + LAN + BD opcional + HTTP opcional | **`lab-completao-host-smoke.sh`** por host; **`lab-completao-orchestrate.ps1`** no Windows |

**Checklist multi-host** (passos manuais A–M): [LAB_SMOKE_MULTI_HOST.pt_BR.md](LAB_SMOKE_MULTI_HOST.pt_BR.md).

## Scripts (rastreados)

1. **`scripts/lab-completao-host-smoke.sh`** (em **cada** host Linux, na raiz do clone) — `uv`, Docker/Podman, estado do compose em `deploy/lab-smoke-stack` se existir, HTTP opcional (`LAB_COMPLETAO_HEALTH_URL` / `--health-url`), import rápido do motor. **`--privileged`**: leitura com **`sudo -n`** (iptables/nft/ufw/fail2ban em modo snapshot).

2. **`scripts/lab-completao-orchestrate.ps1`** (no **PC Windows** do operador) — lê o manifest em **`docs/private/homelab/lab-op-hosts.manifest.json`**, SSH por host, corre o bash em cada **`repoPaths`**. Campo opcional **`completaoHealthUrl`**: depois do smoke por SSH, pedido HTTP a partir do PC dev. Gera logs em **`docs/private/homelab/reports/`**.

3. **Sudo sem senha (estreito)** — mesmo critério do **`homelab-host-report.sh`**: modelo em **`docs/private/homelab/LABOP_COMPLETÃO_SUDOERS.pt_BR.md`** (não commitar sudoers reais no GitHub).

4. **Template de sessão / lições** — **`docs/private/homelab/COMPLETAO_SESSION_TEMPLATE.pt_BR.md`**. Exemplos preenchidos: **`docs/private/homelab/COMPLETAO_SESSION_YYYY-MM-DD.md`** (só operador; nunca no GitHub público).

## O que este runbook **não** automatiza

- Abrir **firewall**, alterar **AIDE**/**auditd**/**USBGuard**/**sshguard**/**fail2ban**: decisão do operador; exceções de teste ficam em notas **privadas**.

## Arranque rápido

1. Garantir clone + **`uv`** em cada host; **`uv sync`** e extras conforme [TECH_GUIDE.pt_BR.md](../TECH_GUIDE.pt_BR.md) quando preciso.
2. No manifest, opcionalmente **`completaoHealthUrl`** por host (ex.: `http://<host-lan>:8088/health`).
3. Na raiz do repo no Windows: **`.\scripts\lab-completao-orchestrate.ps1`** (e **`-Privileged`** se o sudoers permitir).
4. Preencher o template privado; abrir issues / planos quando houver lacunas de produto.
