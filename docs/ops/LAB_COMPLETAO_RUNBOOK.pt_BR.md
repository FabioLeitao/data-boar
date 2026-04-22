# Laboratório: "completão" vs CI / pytest

**English:** [LAB_COMPLETAO_RUNBOOK.md](LAB_COMPLETAO_RUNBOOK.md)

**Objetivo:** Definir o que é **completão** neste projeto: **rodar o produto** (CLI, API, web) nos **hosts do lab**, via **SSH**, com **registro** de resultados — não é a mesma coisa que só **`pytest`** ou **`.\scripts\check-all.ps1`** no PC de desenvolvimento.

**Chat novo no Cursor / zero contexto:** Use **[LAB_COMPLETAO_FRESH_AGENT_BRIEF.pt_BR.md](LAB_COMPLETAO_FRESH_AGENT_BRIEF.pt_BR.md)** — prompts copy-paste (**só smoke** vs **estendido**), checklists opcionais, blocos de follow-up **B–E**, pré-condições e âmbito honesto (o que os scripts fazem vs o que depende de config do operador).

## Contrato assistente + operador (Cursor)

- **Acesso:** O assistente executa **`ssh`**, scripts e **`curl`** no **terminal integrado do Cursor** no **PC Windows do operador** — **mesma LAN e configuração SSH** que o shell do operador (ver **`homelab-ssh-via-terminal.mdc`**). Não tratar o “assistente” como rede separada.
- **Orquestração por padrão:** Ao pedir **completão** ou usar o token **`completao`**, o assistente deve executar **`.\scripts\lab-completao-orchestrate.ps1 -Privileged`** na raiz do repo, salvo se optar por não usar. Registros: **`docs/private/homelab/reports/`**.
- **Probes privilegiados:** **`sudo -n`** no script de smoke exige **sudoers estreito** em cada Linux (modelo em **`LABOP_COMPLETÃO_SUDOERS*.md`** gitignored). **`sudo -v` no tmux** aquece sudo **para aquele TTY**, não automaticamente para **`ssh host 'sudo …'`** não interativo — para **`-Privileged`** fiável, **alinhe** sudoers com o modelo.
- **Em falha:** Se **`sudo -n`** ou SSH falhar, o assistente **lembra o operador** de atualizar sudoers / agente SSH / sudo interativo conforme preciso e **executa de novo** os testes — ver **`lab-completao-workflow.mdc`**.

- **Âmbito “datacenter de testes” no lab:** Para **completão**, o assistente **pode** instalar **dependências em falta**, corrigir **portas** da app/compose, acrescentar regras **estreitas** **lab-op↔lab-op** no **firewall** ou **VLAN** (via **`ufw`**, **`nftables`**, **`LAB-ROUTER-01.ps1`** quando houver credenciais), e ajustar **SELinux**/**AppArmor**/**fail2ban**/**sshguard**/**USBGuard**/**AIDE**/**auditd** (etc.) só com **least privilege** e intenção **reversível** — política completa: **`lab-completao-workflow.mdc`**. Registre alterações em **`docs/private/homelab/`**; **nunca** commits públicos com **segredos** ou **detalhes LAN**.

- **Wrappers + sudoers + sem perguntas ociosas:** Preferir **`lab-completao-orchestrate.ps1 -Privileged`** e os restantes scripts do repo (ver **`LAB_OP_PRIVILEGED_COLLECTION.pt_BR.md`**, modelo gitignored **`LABOP_COMPLETÃO_SUDOERS*.md`**) para **sudo estreito sem senha** nos probes. **Não** voltar a pedir permissão para o fluxo acordado SSH/**`-Privileged`**. **Proteger** o **PC Windows principal de desenvolvimento** (papel **L-series**, **`PRIMARY_WINDOWS_WORKSTATION_PROTECTION.pt_BR.md`**) e o clone **canônico**; **outros** hosts no manifesto e imagens **Docker** podem ser **resincronizados** com **`origin`** / Hub para testes.

### Raio de explosão (contrato — não confundir alvos)

| Alvo | Política Git / repo | Porquê |
| ---- | -------------------- | ------ |
| **PC dev principal** (ThinkPad **L-series**, workspace Cursor, clone **canônico**) | **Nunca** **`git reset --hard`**, **`git clean -fdx`**, **`clean-slate`** ou reescrita de histórico na árvore **principal**. Fluxo normal: **`git pull`**, merge, branch, stash. | Continuidade de evidências — **`PRIMARY_WINDOWS_WORKSTATION_PROTECTION.pt_BR.md`**. |
| Hosts **LAB-OP** no **`lab-op-hosts.manifest.json`** (cada **`repoPaths`** por SSH) | **Seguro** alinhar com **`git fetch`**, **`git pull --ff-only`**, **`lab-op-git-align-main.ps1`**, **`lab-op-git-ensure-ref`**, **`-AlignLabClonesToLabGitRef`** — afeta **só** clones **remotos**, **não** a árvore do PC dev principal. | Clones de lab são **descartáveis** para teste; alinhar com o GitHub **não** é o mesmo risco do PC dev principal. |
| **Imagens de contêiner** (Docker / **Swarm** / **Podman** / **Kubernetes**) | **Puxar de novo** do **Docker Hub** (ou registry configurado); **`docker pull`**, atualizar stack/serviço, prune — **normal** no lab. | Imagens são **reproduzíveis** a partir do registry — não equivalem a destruir o Git canônico no PC dev principal. |

- **Mapa de inventário LAB-OP (hardware + software):** Antes de interpretar resultados do smoke, o assistente deve **`read_file`** no **`docs/private/homelab/OPERATOR_SYSTEM_MAP.md`** e na matriz **`LAB_SOFTWARE_INVENTORY.md`** quando existirem (**`docs-private-workspace-context.mdc`**). O **`lab-completao-orchestrate.ps1`** corre primeiro o **`scripts/lab-completao-inventory-preflight.ps1`** (frescura por defeito **15 dias**): se faltar arquivo ou estiver velho, corre **`lab-op-sync-and-collect.ps1`** para atualizar telemetria **`homelab-host-report`** em **`docs/private/homelab/reports/`** — depois **fundir** nos `.md` e atualizar data **as-of** (ver *Frescura do inventário* abaixo). Desligar: **`-SkipInventoryPreflight`**; ajustar dias: **`-InventoryMaxAgeDays N`**.

**Relação:**

| Camada | O que é | Comando típico |
| ------ | ------- | ---------------- |
| **CI / unitários e guards** | Reproduzível, GitHub, sem segredos LAN | workflow **CI**, **pytest** |
| **Gate no PC dev** | Pre-commit + testes antes do merge | **`.\scripts\check-all.ps1`** |
| **Completão no lab** | Produto + runtime + LAN + BD opcional + HTTP opcional | **`lab-completao-host-smoke.sh`** por host; **`lab-completao-orchestrate.ps1`** no Windows |

**Checklist multi-host** (passos manuais A–M): [LAB_SMOKE_MULTI_HOST.pt_BR.md](LAB_SMOKE_MULTI_HOST.pt_BR.md).

## Frescura do inventário (antes / durante completão)

**Porquê:** Hardware muda raramente; **versões de software** (Python, Docker, pacotes) mudam com frequência e influenciam decisões (ex.: só contêiner vs **`uv`** nativo, builds de conectores). Inventários privados desatualizados aumentam interpretações erradas.

1. **Automação rastreada:** **`scripts/lab-completao-inventory-preflight.ps1`** verifica **`docs/private/homelab/LAB_SOFTWARE_INVENTORY.md`** e **`OPERATOR_SYSTEM_MAP.md`**. Por arquivo: linha **`<!-- lab-op-inventory-as-of: YYYY-MM-DD -->`** ou **`**Lab inventory as-of:** YYYY-MM-DD`** (ou *Inventário … as-of* em pt-BR), senão **data de modificação** do arquivo.
2. **Limiar por defeito:** **15 dias** (`-MaxAgeDays` / **`-InventoryMaxAgeDays`** no orchestrator). Se **em falta ou velho**, **`lab-completao-orchestrate.ps1`** corre **`lab-op-sync-and-collect.ps1`** (mesmo manifesto) salvo **`-SkipInventoryPreflight`**. **`-SkipGitPullOnInventoryRefresh`** só se quiseres relatórios **sem** **`git pull`** nos clones do lab.
3. **Depois da telemetria:** o **`lab-op-sync-and-collect`** **não** reescreve os inventários — **atualiza** as matrizes a partir do `*_labop_sync_collect.log` mais recente e define **as-of** no topo para o próximo check de idade.
4. **Preflight manual:** `.\scripts\lab-completao-inventory-preflight.ps1 -AutoRefresh` (mesmos defaults).

## Ref Git alvo para completão reproduzível (clones LAB-OP)

O smoke no host executa **`scripts/lab-completao-host-smoke.sh`** a partir de cada checkout em **`repoPaths`**. Se esses clones estiverem em commits arbitrários, a corrida **não** é comparável ao CI, a um gate de release nem a outra sessão — estás a exercitar **o commit que estiver checked out**.

1. **Declarar uma ref:** chave opcional na raiz do manifesto privado **`completaoTargetRef`** em **`docs/private/homelab/lab-op-hosts.manifest.json`** (ver **`docs/private.example/homelab/lab-op-hosts.manifest.example.json`**) e/ou passar **`-LabGitRef`** a **`lab-completao-orchestrate.ps1`**. O CLI **`-LabGitRef`** tem prioridade quando não está vazio; senão usa-se o valor do manifesto.
2. **Verificar antes do smoke:** Quando há ref definida e **não** passas **`-SkipLabGitRefCheck`**, o orchestrator corre **`scripts/lab-op-git-ensure-ref.ps1`** em modo **Check** (depois do preflight de inventário, antes do smoke por SSH). Faz **`git fetch`** em cada clone (fetch de **branch** precisa concluir com sucesso; fetch de **tags** é melhor esforço para que “would clobber existing tag” **não** aborte o bash remoto antes das linhas **`LABOP_REF_*`** — ver cabeçalho do script) e **falha** se **`HEAD`** não for o commit resolvido para essa ref (`main` / `origin/main` → ponta de **`origin/main`**; tags de release, nomes de branch e SHAs completos suportados). Registos: **`docs/private/homelab/reports/lab_op_git_ensure_ref_*.log`**.
3. **Tags de release vs refresh de inventário:** **`lab-op-sync-and-collect.ps1`** (quando o markdown de inventário está velho) faz **`git pull --ff-only`** nos clones do lab, avançando-os para o **`main`** mais recente. Isso pode **quebrar** um pin em **`vX.Y.Z`**. Ao testar uma **tag**, passa **`-SkipGitPullOnInventoryRefresh`** em **`lab-completao-orchestrate.ps1`** para o refresh não mover os clones antes do **ensure-ref**; atualiza inventários privados manualmente se preciso.
4. **Alinhar / reset só no LAB:** **`lab-op-git-ensure-ref.ps1 -Mode Reset`**, **`lab-op-git-align-main.ps1`**, ou **`lab-completao-orchestrate.ps1 -AlignLabClonesToLabGitRef`** com **`-LabGitRef`** (ou **`completaoTargetRef`**) aplicam-se **só** aos **`repoPaths`** nos hosts SSH do manifesto — **nunca** ao clone **canônico** no **PC principal**. Mesma classe de risco que **`lab-op-git-align-main.ps1`** nesses clones remotos (descarta commits locais no lab / **detached HEAD** em tag).

## Cobertura de capacidades (documentação + código como fonte de verdade)

**Objetivo:** Aprender o comportamento **observado** em relação ao que está **documentado** — docs em **inglês** e **código** são canônicos ([README.md](../README.md)). O completão deve **exercitar** (conforme recursos do lab): **armazenamento remoto** (NFS, SSHFS, SMB/CIFS — mounts no SO e/ou caminhos de conector segundo [TECH_GUIDE.pt_BR.md](../TECH_GUIDE.pt_BR.md)); **bases de dados** ([deploy/lab-smoke-stack](../deploy/lab-smoke-stack/), conectores em [ADDING_CONNECTORS.pt_BR.md](../ADDING_CONNECTORS.pt_BR.md)); **tipos/extensões de arquivo**, **arquivos ocultos** / nomes **dot**, **pacotes compactados**; **local vs remoto**; **“discoverables”** alinhados a LGPD como **linguagem de detecção** ([COMPLIANCE_AND_LEGAL.pt_BR.md](../COMPLIANCE_AND_LEGAL.pt_BR.md) — **não** é parecer jurídico); **sensibilidade ML/DL** ([SENSITIVITY_DETECTION.pt_BR.md](../SENSITIVITY_DETECTION.pt_BR.md), [TESTING.pt_BR.md](../TESTING.pt_BR.md)); **relatórios** e **dashboard**; **POC** — questionário de maturidade ([SMOKE_MATURITY_ASSESSMENT_POC.pt_BR.md](SMOKE_MATURITY_ASSESSMENT_POC.pt_BR.md)), **WebAuthn/FIDO2** JSON RP ([SMOKE_WEBAUTHN_JSON.pt_BR.md](SMOKE_WEBAUTHN_JSON.pt_BR.md), [SECURE_DASHBOARD_AUTH_AND_HTTPS_HOWTO.pt_BR.md](SECURE_DASHBOARD_AUTH_AND_HTTPS_HOWTO.pt_BR.md), [ADR 0033](../adr/0033-webauthn-open-relying-party-json-endpoints.md)). Afirmações **secure-by-design** devem alinhar com [SECURITY.pt_BR.md](../SECURITY.pt_BR.md) e o que **rodou na prática**. Anote **passo / lacuna / desvio** em notas **privadas** de sessão (`docs/private/homelab/`) — **política:** **`.cursor/rules/lab-completao-workflow.mdc`** (matriz de capacidades).

## Scripts (rastreados)

1. **`scripts/lab-completao-host-smoke.sh`** (em **cada** host Linux, na raiz do clone) — `uv`, Docker/Podman, estado do compose em `deploy/lab-smoke-stack` se existir, HTTP opcional (`LAB_COMPLETAO_HEALTH_URL` / `--health-url`), import rápido do motor salvo **`--skip-engine-import`** (ou **`LAB_COMPLETAO_SKIP_ENGINE_IMPORT=1`**) — ver **Hosts só com contêiner** abaixo. **`--privileged`**: leitura com **`sudo -n`** (iptables/nft/ufw/fail2ban em modo snapshot).

2. **`scripts/lab-completao-orchestrate.ps1`** (no **PC Windows** do operador) — lê o manifest em **`docs/private/homelab/lab-op-hosts.manifest.json`**; **`completaoTargetRef`** opcional na raiz ou CLI **`-LabGitRef`** dispara **`lab-op-git-ensure-ref.ps1`** antes do smoke salvo **`-SkipLabGitRefCheck`**; SSH por host, executa o bash em cada **`repoPaths`**. Campo opcional **`completaoHealthUrl`**: depois do smoke por SSH, pedido HTTP a partir do PC dev. Campos opcionais **`completaoEngineMode`:** **`container`** ou **`completaoSkipEngineImport`:** **`true`** passam **`--skip-engine-import`** ao smoke (hosts **Docker Swarm** / **só Podman** sem **`uv`** no metal); gera logs em **`docs/private/homelab/reports/`**.

3. **Sudo sem senha (estreito)** — mesmo critério do **`homelab-host-report.sh`**: modelo em **`docs/private/homelab/LABOP_COMPLETÃO_SUDOERS.pt_BR.md`** (não commitar sudoers reais no GitHub).

4. **Template de sessão / lições** — **`docs/private/homelab/COMPLETAO_SESSION_TEMPLATE.pt_BR.md`**. Exemplos preenchidos: **`docs/private/homelab/COMPLETAO_SESSION_YYYY-MM-DD.md`** (só operador; nunca no GitHub público).

5. **`scripts/lab-op-repo-status.ps1`** — **`git fetch`** + **`git status -sb`** em cada **`repoPaths`** (sem reset). Opcional **`-PullFfOnly`** para **`git pull --ff-only`**. Use **antes** do orchestrate quando aparecer **`MISSING_SCRIPT`** (clone desatualizado vs **`main`**).

6. **`scripts/lab-op-git-ensure-ref.ps1`** — em cada host, **`git fetch`** em cada clone **`repoPaths`**, depois **Check** (falha se **`HEAD`** ≠ ref resolvida) ou **Reset** (checkout/reset destrutivo para coincidir com a ref). Usado automaticamente por **`lab-completao-orchestrate.ps1`** quando **`completaoTargetRef`** / **`-LabGitRef`** está definido — ver *Ref Git alvo para completão reproduzível* acima.

7. **`scripts/lab-op-git-align-main.ps1`** — **`git fetch`** + **`git reset --hard origin/main`** em cada **`repoPaths`**. **Destrutivo** (descarta commits locais no clone). Para refs que não sejam **`main`** (ex.: tags de release), preferir **`lab-op-git-ensure-ref.ps1 -Mode Reset`**.

8. **Ansible (opcional):** **`ops/automation/ansible/playbooks/lab-op-data-boar-git-sync.yml`** — alinhamento com inventário **`[lab_op_data_boar]`**.

9. **Modelos de filesystem (rastreados):** **`docs/private.example/homelab/config.lab-fs-varlog.example.yaml`**, **`config.lab-fs-home-leitao.example.yaml`** — executar **`main.py` no mesmo host** que os caminhos; criar pastas de relatório/SQLite antes; **`/var/log`** pode dar **permissão negada** em alguns arquivos.

10. **MongoDB:** **`driver: mongodb`**; **`pymongo`** com **`uv sync --extra nosql`**. Subir stack: **`docker compose -f docker-compose.yml -f docker-compose.mongo.yml up -d`** em **`deploy/lab-smoke-stack`** (porta típica **27018**). Se o Mongo estiver parado, o alvo falha como **unreachable**, não como **unsupported**.

## Hosts só com contêiner (Docker Swarm, stack Podman, sem `uv` no metal)

Alguns equipamentos do lab são **orquestração** ou **política**: o operador corre o Data Boar **só** via **Docker** / **Podman** / **Docker Swarm** (stack ou serviço) e **não** depende de **`uv`** no host para checks por SSH. Isso é **postura válida** de completão se estiver no manifesto privado — o assistente **não** deve tratar “`uv` não está no PATH” nesses hosts como defeito a “corrigir” instalando Python no metal.

1. Em **`docs/private/homelab/lab-op-hosts.manifest.json`**, defina **`completaoEngineMode`** como **`container`** **ou** **`completaoSkipEngineImport`** como **`true`** para esse **`sshHost`**. O **`lab-completao-orchestrate.ps1`** passa **`--skip-engine-import`**; o smoke registra uma linha **skipped** explícita para **`import core.engine`** em vez de falha implícita.
2. **Critérios de sucesso** nesses hosts: CLI do runtime de contêiner OK, opcional **`deploy/lab-smoke-stack`** **`compose ps`** quando usares compose aí, e/ou **`completaoHealthUrl`** (ex.: **8088** publicado) com **200** a partir do PC dev.
3. **Scans de FS / CLI** em caminhos desse host ainda precisam de **algum** runtime (ex.: **`uv run`** dentro de contêiner com bind mount, ou outro caminho documentado). O smoke do host **não** substitui isso — anotar nas notas privadas qual abordagem usaste.

Ver **`docs/private.example/homelab/lab-op-hosts.manifest.example.json`** para campos opcionais.

## Ordem de fatias recomendada (um host de cada vez)

1. **Ref alvo (recomendado para corridas comparáveis):** definir **`completaoTargetRef`** (ex.: **`origin/main`** ou **`vX.Y.Z`**) e/ou **`-LabGitRef`** em **`lab-completao-orchestrate.ps1`**; usar **`-SkipGitPullOnInventoryRefresh`** ao fixar uma **tag**. Opcional: **`lab-op-repo-status.ps1`** (inspecionar), depois **`lab-op-git-align-main.ps1`**, **`lab-op-git-ensure-ref.ps1`** ou **`git pull --ff-only`** quando aceitares reset **destrutivo** ou fast-forward nos clones LAB.
2. **Smoke no host:** **`lab-completao-orchestrate.ps1`** até desaparecer **`MISSING_SCRIPT`** e, em hosts **nativos**, o import do motor funcionar. Hosts **só contêiner** (manifest **`completaoEngineMode`:** **`container`** ou **`completaoSkipEngineImport`:** **`true`**) **saltam** o import no metal; validar **Docker/Podman/Swarm** + **`completaoHealthUrl`**.
3. **FS `/var/log`:** copiar o modelo, executar **`main.py`** **naquele Linux**.
4. **FS home:** idem com **`config.lab-fs-home-leitao.example.yaml`** (ajustar usuário se preciso).
5. **Completão CLI no PC dev** com YAML privado (BD no hub + FS sintético no repo) — ver **`docs/ops/LAB_EXTERNAL_CONNECTIVITY_EVAL.md`**.
6. **API / web:** subir **`main.py --web`**; **`curl`** em **`/health`**; browser; opcional **`completaoHealthUrl`** no manifesto.

## Limite de automação vs remediação assistida

- Os **scripts** (`lab-completao-orchestrate`, host-smoke) **por si** **não** abrem **firewalls** nem relaxam **LSM**/ferramentas de integridade — **só** **inspecionam** e **registram**.
- Quando o operador pede **completão** e **quer** **desbloquear** testes, o assistente **pode aplicar** correções **estreitas**, no **âmbito lab-op**, com **least privilege** (pacotes, portas, **`ufw`**/**nft**, UniFi via **`LAB-ROUTER-01.ps1`** se existir, contêineres, mounts **NFS**/**SMB**/**SSHFS** conforme o produto) segundo **`lab-completao-workflow.mdc`**. **Pergunte ao operador** antes de mudanças **amplas** ou **irreversíveis** de hardening.
- **Prontidão para produção** continua **iterativa**: repetir completão, issues, patches, executar de novo.

## Reutilização de automação e registro de aprendizados

- **Codificar o que repetir:** Quando um passo do completão for **repetível**, acrescentar ou alargar **`scripts/`**, **Ansible** em **`ops/automation/ansible/`**, ou campos no **manifesto** — hub: **[TOKEN_AWARE_SCRIPTS_HUB.md](TOKEN_AWARE_SCRIPTS_HUB.md)**; política: **`lab-completao-workflow.mdc`** (*Automation reuse + documented learnings*).
- **Registrar sinais** em notas **privadas** (`docs/private/homelab/`, modelo **`COMPLETAO_SESSION_TEMPLATE.pt_BR.md`**): **timeouts**, duração **de relógio**, **lentidão** inesperada, **FP/FN** face a **sintéticos** com verdade conhecida (relatório vs esperado), **confiança** em caminhos **reais** (ex.: árvores de log do sistema, amostras em diretório de usuário), **latência** em **APIs públicas** / **SSH** / hosts **com poucos recursos** vs máquinas mais rápidas, e desvios **docs/defaults**. Isto alimenta **`PLANS_TODO.md`** / **issues** — **sem** PII cru no Git público.

## Arranque rápido

1. Em hosts onde você roda o produto **no metal**, garantir clone + **`uv`** (muitas vezes **`~/.local/bin/uv`** — o smoke antecede isso ao **`PATH`**); **`uv sync`** e **`uv sync --extra nosql`** se houver alvos Mongo; outros extras conforme [TECH_GUIDE.pt_BR.md](../TECH_GUIDE.pt_BR.md). Em hosts **só contêiner** (gestor Swarm, só Podman, etc.), definir **`completaoEngineMode`:** **`container`** (ou **`completaoSkipEngineImport`:** **`true`**) e basear-se em HTTP / compose / stack — **não** assumir **`uv`** no host.
2. No manifest, opcionalmente **`completaoTargetRef`**, **`completaoHealthUrl`**, **`completaoEngineMode`**, **`completaoSkipEngineImport`** — ver exemplo em **`docs/private.example/homelab/lab-op-hosts.manifest.example.json`**.
3. Na raiz do repo no Windows: **`.\scripts\lab-completao-orchestrate.ps1 -Privileged`** (padrão para completão orientado pelo assistente; omite **`-Privileged`** só se precisar evitar probes privilegiados).
4. Preencher o template privado (**timeouts**, **FP/FN**, **latência**, **confiança**); abrir issues / planos quando houver lacunas de produto.
