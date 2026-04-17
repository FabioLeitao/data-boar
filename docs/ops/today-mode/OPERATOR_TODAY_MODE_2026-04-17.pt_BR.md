# Modo hoje do operador — 2026-04-17 (beta estável, CI, testes sintéticos + lab-op)

**English:** [OPERATOR_TODAY_MODE_2026-04-17.md](OPERATOR_TODAY_MODE_2026-04-17.md)

**Tema:** Confirmar que **`main`** está **verde no GitHub Actions** após o ajuste do **`ci.yml`** (condição com `secrets` no nível do job removida). **Puxar** o remoto. **v1.7.0** + amostra **FCPA** + **dicas de jurisdição** como linha de base **beta estável** para **Talita** e **Felipe** iniciarem **testes sintéticos / estruturados**, e para **lab-op** quando quiseres. **Triage** do carryover do **2026-04-16** sem perder o ritmo **Wabbix / WRB**.

---

## Handoff da sessão (manhã 2026-04-17)

- **`origin/main`:** **v1.7.0** já publicado; commits do dia **2026-04-17** incluem amostra **FCPA**, **jurisdiction hints** e correção de **CI** — confirmar com `git log -3`.
- **Sincronizar:** `git fetch origin && git pull origin main`.
- **CI:** **Actions** → **CI** — jobs **test**, **lint**, **bandit**, **audit**; job **Sonar** **pula** passos sem `SONAR_TOKEN` ou **executa** scan se o segredo existir.
- **Compliance:** amostra **`compliance-sample-us_fcpa_internal_policy_pack.yaml`** — mesclar no config com **assessoria** para texto de política corporativa.
- **Testadores beta:** caminho de instalação (Docker **`1.7.0`** / `latest`), barra **`check-all`**, **USAGE** e dicas de jurisdição (opt-in).

---

## Bloco A — Verificar portões (15–20 min)

1. `git status -sb` · `gh run list -L 5 --workflow ci.yml` — último push **sucesso**.
2. Opcional: **`.\scripts\maintenance-check.ps1`**.
3. **`.\scripts\check-all.ps1`** após o pull.
4. Sonar em casa (opcional).

---

## Bloco B — Beta estável para testes sintéticos

- [ ] **Escopo** curto para o casal de testadores — o que exercitar (dashboard, config de exemplo, relatórios **metadata-only**).
- [ ] **Sem PII em issues** públicas — ver **AGENTS.md**.
- [ ] **Versão:** manter **1.7.0** salvo hotfix — **PUBLISHED_SYNC.md**.

---

## Bloco C — Lab-op (opcional)

- [ ] Manifest **`lab-op-hosts.manifest.json`** → **`lab-op-sync-and-collect.ps1`**.
- [ ] **`docker pull fabioleitao/data_boar:1.7.0`** no host alvo.

---

## Carryover

Ver **[CARRYOVER.md](CARRYOVER.md)**. Prioridade: **CI verde**, **onboarding de testadores**, **fila honesta**.

---

## Fim do dia

- **`eod-sync`** ou **`operator-day-ritual.ps1 -Mode Eod`**
- **`gh pr list --state open`**

---

## Referências rápidas

- **Publicação:** [PUBLISHED_SYNC.md](PUBLISHED_SYNC.md) · [releases/1.7.0.md](../../releases/1.7.0.md)
- **PLANS:** [PLANS_TODO.md](../../plans/PLANS_TODO.md) · [PLANS_HUB.md](../../plans/PLANS_HUB.md)
- **ADR 0026 / 0025** como acima (EN).
