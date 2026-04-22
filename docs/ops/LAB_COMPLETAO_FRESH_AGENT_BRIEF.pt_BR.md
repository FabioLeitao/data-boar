# Completão no lab — brief para agente Cursor novo (copy-paste)

**English:** [LAB_COMPLETAO_FRESH_AGENT_BRIEF.md](LAB_COMPLETAO_FRESH_AGENT_BRIEF.md)

**Quando usar:** Quando você abre um **chat novo** **sem contexto** e **quer** que o assistente **execute** o **completão** como nos **contratos** do repo (`lab-completao-workflow.mdc`, `LAB_COMPLETAO_RUNBOOK.md`).

## Pré-condições (estação do operador)

- **Mesmo** PC Windows de desenvolvimento, **mesmo** clone, **terminal integrado do Cursor** (não um “datacenter de IA” à parte).
- **`docs/private/homelab/lab-op-hosts.manifest.json`** presente (cópia a partir de **`docs/private.example/homelab/lab-op-hosts.manifest.example.json`** quando preciso). Em hosts em que o Data Boar corre **só** via **Docker Swarm / Podman** (sem **`uv`** no metal), defina **`completaoEngineMode`:** **`container`** (ou **`completaoSkipEngineImport`:** **`true`**) para o smoke **não** tratar **`uv`** ausente como falha — ver **`LAB_COMPLETAO_RUNBOOK.md`** (*Container-only lab hosts* / *Hosts só com contêiner*).
- **`ssh`** para os hosts do manifesto funciona nesse terminal (chaves / `~/.ssh/config`).
- Opcional: **sudoers estreito** para **`sudo -n`** nos Linux — ver **`LAB_OP_PRIVILEGED_COLLECTION.pt_BR.md`** e **`LABOP_COMPLETÃO_SUDOERS*.md`** (gitignored).

## Ler primeiro (ordem)

1. **[`AGENTS.md`](../../AGENTS.md)** — linha do Quick index **Completão no lab** e token **`completao`**.
2. **[`LAB_COMPLETAO_RUNBOOK.md`](LAB_COMPLETAO_RUNBOOK.md)** — contratos, scripts, **ordem de fatias**, cobertura de capacidades, automação + aprendizados.
3. **`.cursor/rules/lab-completao-workflow.mdc`** — política sempre ativa (SSH, **`-Privileged`**, sem perguntas ociosas sobre SSH, proteção **L-series**, matriz doc+código, timeouts/FP-FN).

## Token de sessão (inglês)

**Escreva** **`completao`** no chat para alinhar o âmbito a **`session-mode-keywords.mdc`**.

## Antes do orchestrator (automático)

O **`lab-completao-orchestrate.ps1`** corre primeiro o **`lab-completao-inventory-preflight.ps1`** (frescura **15 dias** por defeito nos privados **`LAB_SOFTWARE_INVENTORY.md`** + **`OPERATOR_SYSTEM_MAP.md`**; dispara **`lab-op-sync-and-collect.ps1`** se estiver velho). **Leia** esses inventários quando existirem para alinhar o smoke ao **mapa** documentado — **`LAB_COMPLETAO_RUNBOOK.md`** (*Inventory freshness* / *Frescura do inventário*). Desligar: **`-SkipInventoryPreflight`**.

## Primeiro comando (padrão)

Na **raiz do repo** no Windows:

```text
.\scripts\lab-completao-orchestrate.ps1 -Privileged
```

Depois **leia** **`docs/private/homelab/reports/`** (`completao_*_allhosts.log`, `*_completao_host_smoke.log` por host).

## Fatias sequenciais (não saltar sem motivo)

**Siga** **`LAB_COMPLETAO_RUNBOOK.md`** — **Ordem de fatias recomendada**, **Cobertura de capacidades**, **Reutilização de automação e registro de aprendizados**. Camadas extra (dados sintéticos, BDs, scans, API key, JWT, WebAuthn, POC de maturidade, checagens “secure by design”) usam os **smokes** e **docs** indicados nesse runbook (ex.: **`SMOKE_WEBAUTHN_JSON.pt_BR.md`**, **`SMOKE_MATURITY_ASSESSMENT_POC.pt_BR.md`**, **`SECURE_DASHBOARD_AUTH_AND_HTTPS_HOWTO.pt_BR.md`**, **`TECH_GUIDE.pt_BR.md`**). **Docs em inglês + código** são a fonte de verdade do comportamento.

## Não fazer

- Dizer que o assistente **não** chega ao lab por **SSH a partir deste PC** quando o **`ssh`** funciona para o operador — ver **`homelab-ssh-via-terminal.mdc`**.
- Pedir **de novo** “posso usar SSH / **`-Privileged`**?” se o operador já pediu **completão** — ver **`operator-direct-execution.mdc`**.
- Executar operações **destrutivas** no repo no **PC Windows principal de desenvolvimento** (papel **L-series**) — **`PRIMARY_WINDOWS_WORKSTATION_PROTECTION.pt_BR.md`**.
- Meter **segredos**, **tokens** ou **identificadores LAN** no **GitHub público**; notas só em **`docs/private/homelab/`**.

## Bloco copy-paste (operador → chat novo)

```text
completao

You are in the data-boar repo on my Windows dev PC. Read AGENTS.md (Quick index: Lab completão), then docs/ops/LAB_COMPLETAO_RUNBOOK.md, and follow .cursor/rules/lab-completao-workflow.mdc. Use the integrated terminal — same SSH reachability as my shell.

1) From repo root run: .\scripts\lab-completao-orchestrate.ps1 -Privileged
2) Summarize docs/private/homelab/reports/ logs (no secrets in chat if sensitive).
3) Continue the runbook slice order: repo alignment if needed, per-host FS smoke, CLI/API/web, then POC smokes (WebAuthn, maturity assessment, secure dashboard) per docs/ops/SMOKE_*.md and TECH_GUIDE as applicable.

Do not ask redundant permission for SSH or -Privileged. Do not claim the lab is unreachable from this workspace. Protect my primary Windows dev workstation per docs/ops/PRIMARY_WINDOWS_WORKSTATION_PROTECTION.md. Document material findings (timeouts, latency, FP/FN vs synthetic, confidence on real paths) under docs/private/homelab/.

If something fails, print the actual error and what I must fix (e.g. sudoers, manifest, **uv** em falta em hosts **nativos**), then stop — I will fix and ask you to retry. **Não** exigir **`uv`** no metal em hosts **só contêiner** no manifest (**`completaoEngineMode`:** **`container`**).
```

## Um agente novo consegue?

**Em grande parte sim**, desde que o **workspace** seja este repo (para carregar **`.cursor/rules/`**), **você use** **`completao`** ou o bloco acima, e as **pré-condições** estejam ok. **Nenhum** agente **inventa** chaves SSH, acesso **UDM** ou **sudoers** nos hosts — isso continua **do lado do operador**. As regras **reduzem** respostas medíocres do tipo “LAN impossível”; **não** substituem **setup** ou **segredos**.

## O que ainda pode melhorar

- Manter **`manifest.json`** e YAML **privados** **atualizados** à medida que o lab cresce.
- Depois de cada completão, **uma linha** em **`PLANS_TODO.md`** ou uma **issue** quando houver **lacuna de produto** confirmada — fecha o ciclo entre **notas de sessão** e **roadmap**.
