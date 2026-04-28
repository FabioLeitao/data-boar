# SRE audit — doctrinal triad validation (operator probe, 2026-04-28)

- **Date (UTC):** 2026-04-28
- **Trigger:** Slack `#data-boar-ops`, automation `def95df7-a634-431a-93e5-659e4d831725`,
  message `ts 1777382927.346569` (~13:28 UTC), single message (no fabrication).
- **Branch:** `cursor/data-boar-agent-protocol-360a` (Cloud Agent VM, **`Linux 6.12.58+ x86_64`**, base `main` @ `624f4e7`).
- **Verdict:** **Concordo com nuances** — the operator's three-claim framing of the
  Slack/bootstrap/0.574x triad is *directionally* correct, but each leg has a
  scope boundary that matters more than the metaphor. **No behavior change.**
- **Doctrine:**
  [`DEFENSIVE_SCANNING_MANIFESTO.md`](../inspirations/DEFENSIVE_SCANNING_MANIFESTO.md)
  §1.3 (*no surprise side effects*: a doctrinal probe answered honestly leaves the
  customer DB contract untouched);
  [`THE_ART_OF_THE_FALLBACK.md`](../inspirations/THE_ART_OF_THE_FALLBACK.md) §3
  (*diagnostic on fall*: when the trigger is a thinking question, the diagnostic
  is the **answer plus its scope limits**, never just "yes").

---

## 1. Why this audit exists (and why it is *not* in `FABRICATED_CLAIMS_INDEX.md`)

The five rows currently in
[`FABRICATED_CLAIMS_INDEX.md`](FABRICATED_CLAIMS_INDEX.md) all share a shape:
the trigger asserted a verifiable signal (CodeQL High, Dependabot alert, root
`Cargo.toml`, renamed CLI) that did **not** exist on the branch named.

This trigger is a **different shape**: the operator asks whether three
mechanisms (`compromisso público`, `bootstrap firmware`, `gate 0.574x`) really
do what their copy claims. Treating it as fabrication would be the same kind
of category error the index exists to prevent. The honest GTD response is a
**doctrinal validation note** that records the agreement, the disagreement,
and the falsifiable boundaries — so a future maintainer (human or agent) can
re-derive the answer without re-running the chat.

The cross-link in `FABRICATED_CLAIMS_INDEX.md` § *Cross-references* points at
this file precisely to keep the two shapes separate.

## 2. The trigger message (verbatim, pt-BR)

> :boar: **\<@U0AQ7R25RQE\>: O que isto resolve?**
>
> *Contra a Preguiça:* O script de notificação cria um "compromisso público" no
> Slack. O Agente sabe que você está a ver o log.
>
> *Contexto Forte:* Ao carregar o dump e forçar o ritual de bootstrap, você
> "limpa" a memória de curto prazo da IA genérica e instala o "firmware" do
> Data Boar.
>
> *Drift:* O gate de performance (0.574x) torna-se uma barreira física, não
> apenas uma sugestão. concorda?

## 3. Per-claim verification (HEAD `624f4e7`, this branch, this VM)

| # | Operator claim | Verifiable signal | Verdict |
| - | --- | --- | --- |
| 1 | Slack notification script = *compromisso público* / *contra a preguiça* / *o agente sabe que você está a ver o log* | The Slack-trigger automation `def95df7-…` is wired to this same channel; every audit (e.g. PR #281) lands a message with the trigger `ts`. The append-only ledger [`FABRICATED_CLAIMS_INDEX.md`](FABRICATED_CLAIMS_INDEX.md) makes the *cumulative cost* of fabricated triggers grep-able (5 rows in 24 h on the `report-generator-path-injection` family alone). The discipline is enforced by [`publication-truthfulness-no-invented-facts.mdc`](../../../.cursor/rules/publication-truthfulness-no-invented-facts.mdc) (no invented dates / URLs / status) plus the audit-doc requirement in `AGENTS.md` *Risk posture*. | **Agree, partially.** The mechanism works — but **not** because the agent feels watched (LLMs do not). It works because the public log + append-only index + truthfulness rule together turn any fabricated assertion into a *future-grep-able liability*. Remove the index and the disciplinary effect evaporates; the channel alone is decorative. |
| 2 | Carregar dump + forçar ritual de bootstrap = limpa memória de curto prazo da IA genérica e instala o "firmware" do Data Boar | Each Cloud Agent VM starts *empty*: there is no carry-over chat memory to "wipe". What loads context is the always-applied `AGENTS.md`, the situational `OPERATOR_AGENT_COLD_START_LADDER.md` task router, and rules attached via globs / `@`. The effect is to *force an ordered reading path before action*, analogous to a cold-boot ROM, not a firmware flash. Risk: an oversized "dump" *reduces* signal because the context window is finite — `token-aware` is a [session-mode-keywords](../../../.cursor/rules/session-mode-keywords.mdc) cue precisely to keep this in check. | **Agree on the intent, disagree on the metaphor.** "Firmware install" misframes the mechanism. The triad does not modify the model; it constrains the *first reads*. If the operator over-loads the bootstrap, the agent loses the ladder under noise — same failure mode as a verbose `--debug` that drowns the signal it was supposed to surface ([`INTERNAL_DIAGNOSTIC_AESTHETICS.md`](../inspirations/INTERNAL_DIAGNOSTIC_AESTHETICS.md)). |
| 3 | Gate de performance (0.574x) = barreira física, não apenas uma sugestão | [`tests/test_official_benchmark_200k_evidence.py`](../../../tests/test_official_benchmark_200k_evidence.py) (4 assertions across 3 test functions): `pro_seconds > opencore_seconds`, `speedup < 1.0`, recorded ratio matches `opencore_seconds / pro_seconds` within `1e-3`, `opencore_hits == pro_hits`. The artifact `tests/benchmarks/official_benchmark_200k.json` pins `speedup_vs_opencore = 0.574`, `opencore_seconds = 0.252242`, `pro_seconds = 0.439419`, `opencore_hits = pro_hits = 100000`. `pytest` fails *loud* if a manifesto / executive deck / manifest flips the sign without regenerating the JSON in the same commit. | **Agree, with strict scope.** The gate *is* a physical barrier — for **direction** (Pro slower in this profile) and **findings parity** (no silent detection regression). It is **not** a barrier against picking a *different* benchmark profile (larger chunks, heavier downstream stage) that would produce a more flattering ratio. [`BENCHMARK_EVOLUTION.md`](../../plans/BENCHMARK_EVOLUTION.md) §8 explicitly labels 0.574x as **technical debt baseline**, not victory. Honest scope wins; over-claiming the gate would itself be drift. |

## 4. Defensive Architecture posture (zero impact on database locks)

This audit changes only Markdown under `docs/ops/sre_audits/` and a single
cross-reference row in `FABRICATED_CLAIMS_INDEX.md`. No SQL composition, no
SQLite write path, no statement timeout, no isolation level, no Pro / OpenCore
worker logic, no fallback hierarchy. The
[`DEFENSIVE_SCANNING_MANIFESTO.md`](../inspirations/DEFENSIVE_SCANNING_MANIFESTO.md)
§1.3 *no surprise side effects* clause holds: the customer-DB contract is
untouched. No `time.sleep` (anti-pattern per the SRE protocol); no DB
transactions opened.

## 5. Guardrail Dashboard

| Layer | Result |
| --- | --- |
| `pytest --collect-only -q` (HEAD `624f4e7`, this branch) | **989** tests collected. The "986" figure that recurred in PR #259 / #268 / #281 prompt-injections is **stale**; HEAD is 989 (matches what `FABRICATED_CLAIMS_INDEX.md` row 1 already documented). |
| Targeted re-run (`test_official_benchmark_200k_evidence`, `test_basic_python_scan_single_pass_parity`, `test_notify`) | **19 passed** in 0.06 s. |
| Bandit (`scripts/ utils/ -ll`) | 0 High, 23 Medium, 41 Low — **pre-existing**, none introduced by this audit. 1 file skipped (`utils/report_gen.py` AST syntax error since commit `a8d44ba`; out of scope here, tracked separately). |
| Ruff | `uv run ruff check .` clean on touched paths (docs only). |
| `uv lock` / supply-chain | No dependency added or bumped. `uv.lock` and `requirements.txt` unchanged. |
| Skipped tests relevant to scope | None. No MongoDB / SQLite / sampling code touched, so the *Skipped Test Protocol* in the SRE prompt does not apply (no `@pytest.mark.skip` masks a real connector regression here). |
| DB lock non-regression | No write path modified; no `time.sleep`; no transaction opened. |

## 6. Doctrinal disagreement (recorded, not suppressed)

The SRE protocol explicitly invites disagreement instead of theatre. Two
points the assistant disagrees with, recorded so they survive the chat:

1. **"O agente sabe que você está a ver o log."** — Anthropomorphic framing.
   The audit posture is enforced by *structure* (append-only ledger,
   truthfulness rule, audit-doc-as-PR-cost), not by the agent perceiving
   observation. Keeping the framing precise matters because future
   automations may use weaker models that *cannot* simulate the "watched"
   feeling at all — and the discipline must still hold.
2. **"Instala o firmware do Data Boar."** — The triad does not modify the
   underlying model. It modifies the *first reads* and the *first
   refusals*. Calling that "firmware" risks suggesting that, once "installed",
   it persists between sessions. It does not — every Cloud Agent VM starts
   from zero and re-reads `AGENTS.md` + the cold-start ladder fresh.

Neither disagreement removes the *function* of the triad; both sharpen the
**scope** so the discipline is not over-claimed (which would itself be a
drift the SRE protocol is supposed to prevent).

## 7. Cross-references

- [`FABRICATED_CLAIMS_INDEX.md`](FABRICATED_CLAIMS_INDEX.md) — index of
  fabrication-shaped escalations. This audit is **not** a fabrication; it is
  a **doctrinal probe** answered honestly. The index gains one *cross-link*
  row (so the two shapes are not conflated) but no entry of its own.
- [`docs/plans/BENCHMARK_EVOLUTION.md`](../../plans/BENCHMARK_EVOLUTION.md)
  §8 — 0.574x as technical-debt baseline.
- [`tests/test_official_benchmark_200k_evidence.py`](../../../tests/test_official_benchmark_200k_evidence.py)
  — the four-assertion gate that holds the direction and parity.
- [`docs/ops/LAB_LESSONS_LEARNED.md`](../LAB_LESSONS_LEARNED.md) — operator
  reading guide for the 0.574x figure (do not double-invert).
- [`AGENTS.md`](../../../AGENTS.md) *Risk posture* and
  *Publication truthfulness* bullets — the rules that turn the Slack channel
  into a real auditing surface rather than a notification toy.
