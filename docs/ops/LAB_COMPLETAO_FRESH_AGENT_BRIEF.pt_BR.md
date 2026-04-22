# Completão no lab — brief para agente Cursor novo (copy-paste)

**English:** [LAB_COMPLETAO_FRESH_AGENT_BRIEF.md](LAB_COMPLETAO_FRESH_AGENT_BRIEF.md)

**Quando usar:** Quando você abre um **chat novo** **sem contexto** e **quer** que o assistente **execute** o **completão** como nos **contratos** do repo (`lab-completao-workflow.mdc`, `LAB_COMPLETAO_RUNBOOK.md`).

## Pré-condições (estação do operador)

- **Mesmo** PC Windows de desenvolvimento, **mesmo** clone, **terminal integrado do Cursor** (não um “datacenter de IA” à parte).
- **`docs/private/homelab/lab-op-hosts.manifest.json`** presente (cópia a partir de **`docs/private.example/homelab/lab-op-hosts.manifest.example.json`** quando preciso). Em hosts em que o Data Boar **roda** **só** via **Docker Swarm / Podman** (sem **`uv`** no metal), defina **`completaoEngineMode`:** **`container`** (ou **`completaoSkipEngineImport`:** **`true`**) para o smoke **não** tratar **`uv`** ausente como falha — ver **`LAB_COMPLETAO_RUNBOOK.md`** (*Hosts só com contêiner*).
- **`ssh`** para os hosts do manifesto funciona nesse terminal (chaves / `~/.ssh/config`).
- Opcional: **sudoers estreito** para **`sudo -n`** nos Linux — ver **`LAB_OP_PRIVILEGED_COLLECTION.pt_BR.md`** e **`LABOP_COMPLETÃO_SUDOERS*.md`** (gitignored).

## Ler primeiro (ordem)

1. **[`AGENTS.md`](../../AGENTS.md)** — linha do Quick index **Completão no lab** e token **`completao`**.
2. **[`LAB_COMPLETAO_RUNBOOK.md`](LAB_COMPLETAO_RUNBOOK.md)** — contratos, scripts, **ordem de fatias**, cobertura de capacidades, automação + aprendizados.
3. **`.cursor/rules/lab-completao-workflow.mdc`** — política sempre ativa (SSH, **`-Privileged`**, sem perguntas ociosas sobre SSH, proteção **L-series**, matriz doc+código, timeouts/FP-FN).

## Token de sessão (inglês)

**Escreva** **`completao`** no chat para alinhar o âmbito a **`session-mode-keywords.mdc`**.

## Modos de sessão (escolha um)

| Modo | Objetivo | O que os **scripts do repo** executam de uma vez | O que ainda depende **de você** (config / serviços / segredos) |
| ---- | -------- | ---------------------------------------------- | -------------------------------------------------------------- |
| **Só smoke** | LAN + clone + probes de runtime + logs | **`lab-completao-orchestrate.ps1 -Privileged`** (inclui preflight → pode executar **`lab-op-sync-and-collect.ps1`**) | Manifesto, SSH, opcional **`completaoHealthUrl`**, opcional sudoers para **`sudo -n`** |
| **Estendido** | Igual ao smoke + validação mais funda (CLI, BDs, API, fatias pytest POC) | **Não há** um único script que cubra tudo — seguir **ordem de fatias** em **`LAB_COMPLETAO_RUNBOOK.md`** em passos ou chats | YAML privado (ex. padrão **`config.complete-eval.yaml`**), **`lab-smoke-stack`** levantado onde precisar, env para API key / JWT / WebAuthn, browser para UX FIDO2 manual |

**Âmbito honesto:** A fatia 1 (orchestrator) **por si** **não** faz deploy completo de sintéticos em BDs, scans comparativos nem prova ponta a ponta JWT/WebAuthn/browser. Isso está **documentado** em **`SMOKE_*.md`**, **`LAB_EXTERNAL_CONNECTIVITY_EVAL.md`**, **`TECH_GUIDE.md`**, **`SECURITY.md`** — passos **orientados pelo assistente**, não um comando mágico.

## Checklists opcionais

### Só smoke (primeira fatia útil mínima)

- [ ] Manifesto existe e **`sshHost`** / **`repoPaths`** estão corretos.
- [ ] Hosts só contêiner têm **`completaoEngineMode`:** **`container`** (ou **`completaoSkipEngineImport`**) onde aplicável.
- [ ] (Opcional) **`completaoHealthUrl`** por host se **`main.py --web`** estiver no ar e acessível a partir do PC dev.
- [ ] **Execute** **`.\scripts\lab-completao-orchestrate.ps1 -Privileged`** na raiz do repo; leia os logs em **`docs/private/homelab/reports/`**.
- [ ] Anexar achados materiais em **`docs/private/homelab/`** (ex.: **`COMPLETAO_SESSION_YYYY-MM-DD.md`** ou modelo **`COMPLETAO_SESSION_TEMPLATE.pt_BR.md`**).

### Estendido (vários passos; mesmo chat ou chats seguintes)

- [ ] Checklist **só smoke** feito (ou saltado com motivo nas notas privadas).
- [ ] **`lab-op-repo-status.ps1`** se os clones puderem estar atrás / apareceu **`MISSING_SCRIPT`** antes.
- [ ] Fundir **telemetria recente** em **`LAB_SOFTWARE_INVENTORY.md`** / **`OPERATOR_SYSTEM_MAP.md`** e atualizar **`Lab inventory as-of`** / **`<!-- lab-op-inventory-as-of: ... -->`** (ver **`docs/private.example/homelab/README.md`**).
- [ ] Scans de FS no Linux: cópias **`config.lab-fs-*.example.yaml`** + **`main.py`** **no host** segundo o runbook — não a partir do Windows salvo mounts.
- [ ] Avaliação CLI a partir do PC dev: **`LAB_EXTERNAL_CONNECTIVITY_EVAL.md`** + YAML **privado** (caminhos do operador).
- [ ] API/web: processo **`main.py --web`**, **`curl`** / **`completaoHealthUrl`**, browser conforme preciso; **`SECURE_DASHBOARD_AUTH_AND_HTTPS_HOWTO.pt_BR.md`** para TLS/API key.
- [ ] No **PC dev**: **`.\scripts\smoke-maturity-assessment-poc.ps1`**, **`.\scripts\smoke-webauthn-json.ps1`** — subconjuntos **pytest**; **não** substituem **`check-all.ps1`** nem prova FIDO2 completa no browser.
- [ ] **Registre** **evidência** (timeouts, FP/FN vs sintéticos, confiança em caminhos reais) em **`docs/private/homelab/`**; ligue lacunas de produto a **`PLANS_TODO.md`** / issues quando fizer sentido.

## Antes do orchestrator (automático)

O **`lab-completao-orchestrate.ps1`** executa primeiro o **`lab-completao-inventory-preflight.ps1`** (frescura **15 dias** por padrão nos privados **`LAB_SOFTWARE_INVENTORY.md`** + **`OPERATOR_SYSTEM_MAP.md`**; dispara **`lab-op-sync-and-collect.ps1`** se estiver velho). **Leia** esses inventários quando existirem — **`LAB_COMPLETAO_RUNBOOK.md`** (*Frescura do inventário*). Desligar: **`-SkipInventoryPreflight`**.

## Primeiro comando (padrão)

Na **raiz do repo** no Windows:

```text
.\scripts\lab-completao-orchestrate.ps1 -Privileged
```

Depois **leia** **`docs/private/homelab/reports/`** (`completao_*_allhosts.log`, `*_completao_host_smoke.log` por host).

## Fatias sequenciais (não saltar sem motivo)

**Siga** **`LAB_COMPLETAO_RUNBOOK.md`** — **Ordem de fatias recomendada**, **Cobertura de capacidades**, **Reutilização de automação e registro de aprendizados**. Camadas extra usam os **smokes** e **docs** indicados nesse runbook. **Docs em inglês + código** são a fonte de verdade do comportamento.

## Não fazer

- Dizer que o assistente **não** chega ao lab por **SSH a partir deste PC** quando o **`ssh`** funciona — ver **`homelab-ssh-via-terminal.mdc`**.
- Pedir **de novo** permissão SSH / **`-Privileged`** se o operador já pediu **completao** — ver **`operator-direct-execution.mdc`**.
- Operações **destrutivas** no **PC Windows principal** — **`PRIMARY_WINDOWS_WORKSTATION_PROTECTION.pt_BR.md`**.
- **Segredos** ou identificadores LAN no **GitHub público**; notas só em **`docs/private/homelab/`**.
- Prometer **FIDO2 no browser**, **JWT de licenciamento completo** ou prova **“secure by design”** só com scripts — documentar **o que foi executado** vs **`SMOKE_*.md`** / **`SECURITY.md`**.

---

## Bloco copy-paste A — primeira fatia (smoke + logs)

Chat **novo** sem contexto (após pré-condições). O texto do bloco está em **inglês** para alinhar ao assistente; o cabeçalho **`Session mode: smoke-only`** referencia este arquivo.

```text
completao

You are in the data-boar repo on my Windows dev PC. Read AGENTS.md (Quick index: Lab completão), then docs/ops/LAB_COMPLETAO_RUNBOOK.md, and follow .cursor/rules/lab-completao-workflow.mdc. Use the integrated terminal — same SSH reachability as my shell.

Session mode: smoke-only (see docs/ops/LAB_COMPLETAO_FRESH_AGENT_BRIEF.md).

1) From repo root run: .\scripts\lab-completao-orchestrate.ps1 -Privileged
2) Summarize docs/private/homelab/reports/ logs (no secrets in chat if sensitive).
3) Read docs/private/homelab/OPERATOR_SYSTEM_MAP.md and LAB_SOFTWARE_INVENTORY.md when present; reconcile host-smoke with documented roles (container-only manifest hosts are not "missing uv" defects).
4) Document material findings under docs/private/homelab/ (timeouts, latency, FP/FN vs synthetic, confidence on real paths). Do not expand to full CLI/DB/browser/API proof unless I ask in a follow-up.

Do not ask redundant permission for SSH or -Privileged. Do not claim the lab is unreachable from this workspace. Protect my primary Windows dev workstation per docs/ops/PRIMARY_WINDOWS_WORKSTATION_PROTECTION.md.

If something fails, print the actual error and what I must fix (e.g. sudoers, manifest, missing uv on native hosts), then stop — I will fix and ask you to retry. Do not demand bare-metal uv on container-only manifest hosts (completaoEngineMode: container).
```

---

## Bloco copy-paste B — após fatia A (alinhamento de repo, só leitura)

```text
completao follow-up — repo alignment

Same repo and terminal as before. Run .\scripts\lab-op-repo-status.ps1 from repo root. Summarize per-host git state vs origin/main. If MISSING_SCRIPT appeared in past completão logs, point to LAB_COMPLETAO_RUNBOOK.md (align clones). Do not run lab-op-git-align-main.ps1 unless I explicitly ask (destructive on lab clones). Document under docs/private/homelab/.
```

---

## Bloco copy-paste C — estendido: smokes POC pytest no PC dev (sem segredos LAN)

```text
completao follow-up — Windows POC pytest smokes

From repo root run: .\scripts\smoke-maturity-assessment-poc.ps1 then .\scripts\smoke-webauthn-json.ps1
Summarize pass/fail. These are pytest subsets per docs/ops/SMOKE_MATURITY_ASSESSMENT_POC.md and SMOKE_WEBAUTHN_JSON.md — not a full browser FIDO2 demo and not a substitute for .\scripts\check-all.ps1.
```

---

## Bloco copy-paste D — estendido: padrão CLI eval (precisa config privada)

```text
completao follow-up — CLI eval

Read docs/ops/LAB_EXTERNAL_CONNECTIVITY_EVAL.md. If I have a private config path under docs/private/homelab/, run uv run python main.py --config <path> only after read_file confirms the YAML exists; redact secrets in chat. If no config exists, stop and list what I must provide. Document findings under docs/private/homelab/.
```

---

## Bloco copy-paste E — pacote de evidência (documentação / próxima sessão)

```text
completao follow-up — evidence pack

Consolidate what we proved this session: commands run, log paths under docs/private/homelab/reports/, inventory as-of dates, pass/fail matrix, gaps vs LAB_COMPLETAO_RUNBOOK.md slice order. Suggest one PLANS_TODO.md row or issue title only if a product gap is confirmed — no public PII.
```

## Um agente novo consegue?

**Em grande parte sim** no modo **só smoke**, com workspace deste repo e bloco **A**. O **estendido** é **vários passos** de propósito — use **B–E** ou chats novos para não misturar âmbito. **Nenhum** assistente **inventa** chaves SSH, **LAB-ROUTER-01** ou **sudoers** — continua **do lado do operador**.

## O que melhorar fora deste arquivo

- Manter **manifesto** e YAML **privados** atualizados.
- Depois de cada completão, **uma linha** em **`PLANS_TODO.md`** ou **issue** quando houver lacuna de produto confirmada.
