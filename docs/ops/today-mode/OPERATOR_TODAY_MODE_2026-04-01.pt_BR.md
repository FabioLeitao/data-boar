# “Today mode” do operador — 2026-04-01 (fatia release-ready, token-aware)

**English:** [OPERATOR_TODAY_MODE_2026-04-01.md](OPERATOR_TODAY_MODE_2026-04-01.md)

**Objetivo:** Fechar uma **fatia coesa e revisável** rumo a production readiness, sem criar backlog silencioso. Limites: **`carryover-sweep`** · **`eod-sync`** · **`scripts/operator-day-ritual.ps1`**.

---

## Bloco 0 — Verdade + carryover (≈ 15–25 min)

1) Percorre **[CARRYOVER.pt_BR.md](CARRYOVER.pt_BR.md)** — fecha, adia com data ou promove para PLANS/issue cada ⬜.
1) Confirma a verdade de versão:
   - **Publicado**: a última tag/release deve continuar `v1.6.7` a menos que você tenha publicado de novo.
   - **Trabalho**: o repo agora foi bumpado para **`1.6.8`** (rastreamento pré-publish).

---

## Bloco A — Fechar a fatia Cursor/MCP + tracking de versão (≈ 30–60 min)

- Abrir PR para o commit local que bumpou a versão de trabalho para **1.6.8** e documentou troubleshooting do `MCP_DOCKER`.
- Manter o PR **focado em workflow/docs**; não misturar feature/fix aqui.

**Gate token-aware:** `.\scripts\lint-only.ps1` é suficiente para esta fatia (já está verde localmente).

---

## Bloco B — WRB (Wabbix) e evidência mínima (≈ 20–40 min)

- Usar o bloco para colar: **`docs/ops/WRB_DELTA_SNAPSHOT_2026-03-31.pt_BR.md`**
- Atualizar os bullets de “verdade de versão” se você for referenciar **working 1.6.8** no `main` (e confirmar que o publicado ainda é `v1.6.7`).
- Enviar o e-mail (ou adiar explicitamente com data no **CARRYOVER**).

---

## Bloco C — Slack ping proof-of-life (≈ 10–15 min)

- Seguir **`docs/ops/OPERATOR_NOTIFICATION_CHANNELS.pt_BR.md`** e registrar uma nota **CHAN-OK** quando o alerta em telefone + PC estiver confirmado.

---

## Critério de paragem

Fatia do dia **fechada** quando:

- **CARRYOVER** atualizado (sem pendência silenciosa).
- PR da fatia `1.6.8` está **aberto** (ou mergeado).
- WRB foi **enviado** (ou adiado com data).
- Ping Slack foi **confirmado** (ou adiado com data).
