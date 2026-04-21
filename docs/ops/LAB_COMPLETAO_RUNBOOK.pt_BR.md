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

5. **`scripts/lab-op-repo-status.ps1`** — **`git fetch`** + **`git status -sb`** em cada **`repoPaths`** (sem reset). Opcional **`-PullFfOnly`** para **`git pull --ff-only`**. Use **antes** do orchestrate quando aparecer **`MISSING_SCRIPT`** (clone desatualizado vs **`main`**).

6. **`scripts/lab-op-git-align-main.ps1`** — **`git fetch`** + **`git reset --hard origin/main`** em cada **`repoPaths`**. **Destrutivo** (descarta commits locais no clone).

7. **Ansible (opcional):** **`ops/automation/ansible/playbooks/lab-op-data-boar-git-sync.yml`** — alinhamento com inventário **`[lab_op_data_boar]`**.

8. **Modelos de filesystem (rastreados):** **`docs/private.example/homelab/config.lab-fs-varlog.example.yaml`**, **`config.lab-fs-home-leitao.example.yaml`** — correr **`main.py` no mesmo host** que os caminhos; criar pastas de relatório/SQLite antes; **`/var/log`** pode dar **permissão negada** em alguns arquivos.

9. **MongoDB:** **`driver: mongodb`**; **`pymongo`** com **`uv sync --extra nosql`**. Subir stack: **`docker compose -f docker-compose.yml -f docker-compose.mongo.yml up -d`** em **`deploy/lab-smoke-stack`** (porta típica **27018**). Se o Mongo estiver parado, o alvo falha como **unreachable**, não como **unsupported**.

## Ordem de fatias recomendada (um host de cada vez)

1. **Alinhar clones:** **`lab-op-repo-status.ps1`** (inspecionar), depois **`lab-op-git-align-main.ps1`** só se aceitar reset **destrutivo**.
2. **Smoke no host:** **`lab-completao-orchestrate.ps1`** até desaparecer **`MISSING_SCRIPT`** e o import do motor funcionar.
3. **FS `/var/log`:** copiar o modelo, correr **`main.py`** **naquele Linux**.
4. **FS home:** idem com **`config.lab-fs-home-leitao.example.yaml`** (ajustar utilizador se preciso).
5. **Completão CLI no PC dev** com YAML privado (BD no hub + FS sintético no repo) — ver **`docs/ops/LAB_EXTERNAL_CONNECTIVITY_EVAL.md`**.
6. **API / web:** subir **`main.py --web`**; **`curl`** em **`/health`**; browser; opcional **`completaoHealthUrl`** no manifesto.

## O que este runbook **não** automatiza

- Abrir **firewall**, alterar **AIDE**/**auditd**/**USBGuard**/**sshguard**/**fail2ban**: decisão do operador; exceções de teste ficam em notas **privadas**.

## Arranque rápido

1. Garantir clone + **`uv`** em cada host (muitas vezes **`~/.local/bin/uv`** — o smoke script antecede isso ao **`PATH`**); **`uv sync`** e **`uv sync --extra nosql`** se houver alvos Mongo; outros extras conforme [TECH_GUIDE.pt_BR.md](../TECH_GUIDE.pt_BR.md).
2. No manifest, opcionalmente **`completaoHealthUrl`** por host (ex.: `http://<host-lan>:8088/health`).
3. Na raiz do repo no Windows: **`.\scripts\lab-completao-orchestrate.ps1`** (e **`-Privileged`** se o sudoers permitir).
4. Preencher o template privado; abrir issues / planos quando houver lacunas de produto.
