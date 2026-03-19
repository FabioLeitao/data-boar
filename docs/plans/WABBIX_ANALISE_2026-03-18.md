# Wabbix evolution review — 2026-03-18 (tracking in-repo)

**Source (local / operator):** PDF `docs/feedbacks, reviews, comments and criticism/analise_evolucao_data_boar_2026-03-18.pdf` (folder may be gitignored; keep the PDF in your workspace for audit trail).

**Verdict (Wabbix):** **9.1 / 10** — strong, consistent evolution (detection, connectors, tests, compliance docs; releases 1.6.0 / 1.6.1 cadence in the report snapshot).

---

## Already aligned in-repo (before this follow-up)

| Wabbix theme | Repo status |
|--------------|-------------|
| Content-type / magic-byte detection | Done (report: “Resolvido”). |
| Compliance documentation (e.g. ISO/IEC 27701) | Done. |
| Release governance + versioning | Done (`docs/VERSIONING.md`, `docs/releases/`, tags). |
| API host default loopback (Wabix P0/P1) | Done — see PLANS_TODO “Secure default host binding”. |
| Security triage **routine** (Dependabot / Scout) | **Tracked:** Priority band A, `scripts/maintenance-check.ps1`, `SECURITY.md`, `docs/ops/BRANCH_AND_DOCKER_CLEANUP.md` — formalize cadence in ops calendar (still human). |
| Doc snapshot per version | **Partial:** each release has `docs/releases/X.Y.Z.md`; optional future “frozen doc bundle” remains backlog (W-DOC below). |

---

## Executive recommendations → mapped work (token-aware order)

| ID | Wabbix recommendation | Mapping | Priority vs token-aware rule |
|----|------------------------|---------|------------------------------|
| **W-KPI** | Painel de KPIs de release e segurança operacional | **Done (baseline):** 2 manual KPIs in `PLAN_READINESS_AND_OPERATIONS.md` §4.7 + lightweight exporter `scripts/kpi-export.py`. **Next optional:** DORA-lite / Actions insights (lead time, CI fail rate). | Low AI / manual-friendly; after critical security band. |
| **W-CONTRACT** | Bateria de testes de contrato (relatórios + APIs críticas) | **Done (baseline):** report/heatmap artifact regressions in `tests/test_report_trends.py` + OpenAPI contract response documentation in `tests/test_routes_responses.py`. | Low/moderate slice; already covered by existing tests. |
| **W-DECOUPLE** | Desacoplar regras centrais (detector / gerador) | **Ongoing:** SonarQube cognitive-complexity gates; incremental extraction (e.g. `core/fuzzy_column_match.py` pattern). No big-bang refactor. | High effort; small extractions when touching files. |
| **W-DOC** | Disciplina de release + snapshot de documentação | **Done (baseline):** release notes per version; **optional:** export doc set per tag — backlog under W-KPI ops. | Doc-only follow-up. |

---

## Implemented from FN / aggregated plan in this cycle

- **Plan § aggregated wording (incomplete sample):** Excel **Cross-ref data – ident. risk** now starts with a **sample/coverage note** row; **Recommendations** row `AGGREGATED_IDENTIFICATION` mentions sampling and manual confirmation (`report/generator.py`).
- **Plan table:** [PLAN_ADDITIONAL_DETECTION_TECHNIQUES_AND_FN_REDUCTION.md](PLAN_ADDITIONAL_DETECTION_TECHNIQUES_AND_FN_REDUCTION.md) item **8** marked done; item **9** (MEDIUM / `PII_AMBIGUOUS` in aggregation) **verified** — `DEFAULT_PATTERN_CATEGORY_MAP` includes `PII_AMBIGUOUS` → `other` in `core/aggregated_identification.py`.

- **Plan §4 (format / length hints from connectors) initial slice:** `sensitivity_detection.connector_format_id_hint` + detector `FORMAT_LENGTH_HINT_ID`, wired through `DataScanner.scan_column(..., connector_data_type=...)` for SQL/Snowflake/Dataverse/Power BI and the SQLite/filesystem typed path; verified via `tests/test_format_length_hint.py`.

---

## Staging: fuzzy column match

Use **`deploy/config.staging.example.yaml`** as a merge overlay:

- `sensitivity_detection.fuzzy_column_match: true` (requires **`rapidfuzz`** via `uv sync --group dev` or `pip install ".[detection-fuzzy]"`; tune `fuzzy_column_match_min_ratio` if noise is high).
- `sensitivity_detection.connector_format_id_hint: true` (Plan §4: uses declared `CHAR`/`VARCHAR(N)` + conservative ID-like name heuristics; if it gets noisy on generic `*_id`, set it back to `false`).

---

## Next suggested (token-aware)

1. **W-KPI (optional next slice)** — extend from baseline to DORA-lite/Actions insights (lead time, CI fail rate, rollback frequency) when maintenance is green.
2. **W-DECOUPLE** — small extractions to reduce core detector/report coupling when touching high-complexity modules.
3. **–1 / –1b** — maintenance when critical (Dependabot / Docker Scout).

**Synced with:** [PLANS_TODO.md](PLANS_TODO.md) (Wabbix subsection + FN reduction rows 8–9).
