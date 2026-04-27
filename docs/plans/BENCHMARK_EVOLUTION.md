# Benchmark evolution — completão A/B (legacy tag vs current)

**Status:** living note — fill **Performance** numbers from `benchmark_runs/times.txt` after each `scripts/benchmark-ab.ps1` run. Replace **Business value** bullets with phrases copied from your generated Markdown under `benchmark_runs/<current>/` (no raw PII).

**Last refreshed:** 2026-04-27 (Slice 4 of [`PLAN_ENGINEERING_DOCTRINE_CONSOLIDATION.md`](PLAN_ENGINEERING_DOCTRINE_CONSOLIDATION.md)). The **v1.7.3 → HEAD** narrative below names the resilience and coverage gains by manifesto and links the **200k A/B 0.574x** evidence pinned in [`tests/test_official_benchmark_200k_evidence.py`](../../tests/test_official_benchmark_200k_evidence.py).

**Scope:** Lab orchestration (`lab-completao-orchestrate.ps1`) plus optional **`data-boar-report`** (`python -m cli.reporter`, see [USAGE.md](../USAGE.md) section 5) when the benchmark script is invoked with `-ReportConfigYaml` / `-ReportSessionId`.

---

## 1. Executive Markdown (`data-boar-report`) — required sections (code contract)

The stakeholder Markdown produced by `report.executive_report.generate_executive_report` always includes:

| Stakeholder ask | Markdown heading / block | Role |
| --- | --- | --- |
| **Action Plan (APG)** | `## 4. Plano de ação (APG)` | `### 4.1 Prioridades imediatas (Top 3)` — ranked recommendations; `### 4.2 Inventário por tipo de dado (achado → risco → recomendação técnica)` — full per-pattern inventory. |
| **Audit / methodology evidence** | `## 3. Metodologia e segurança` | Sampling caps, timeout hints, dialect posture (e.g. SQL Server `WITH (NOLOCK)` when applicable), leading SQL comment traceability. |
| **Manifest pointer (audit artefact)** | Footer line | `**Evidência técnica:** \`scan_manifest_<prefix>.yaml\`` — companion YAML emitted with the scan/evidence pipeline (`scan_manifest_*.yaml`). |

So: **APG** = section **4**; **audit evidence** = section **3** (narrative + manifest bullets) **plus** the explicit **`scan_manifest_*.yaml`** reference (and the YAML file itself when the full pipeline runs).

**Note:** In this workspace there was **no** `benchmark_runs/v1.7.4-beta/` tree to open; verification above is from **`report/executive_report.py`** (same output `data-boar-report` drives). After you run the benchmark locally, confirm the file under `benchmark_runs/v1.7.4-beta/` (e.g. `executive_report_benchmark.md`) contains those headings.

---

## 2. Delivery gain — what the client receives today that v1.7.3 did not ship

| Before (e.g. **v1.7.3** tag on clone) | After (current product + benchmark round B) |
| --- | --- |
| **No** `data-boar-report` entrypoint to regenerate **desk-ready executive Markdown** from **SQLite alone** (no new live connector reads). | **`data-boar-report`** (see USAGE): reproducible **executive Markdown** from a fixed `session_id` + config — useful for committees, DPO/CISO packs, and audit **preparation**. |
| Stakeholder narrative tied only to **Excel/heatmap** generation path when reports run. | **APG-aligned** Top 3 + **full per-pattern remediation inventory** in Markdown (patterns and counts — **not** raw table/column/cell samples). |
| Limited **machine-readable** “how we read” evidence alongside the desk doc. | **`scan_manifest_*.yaml`**: sampling/timeouts, `safety_tags`, `audit_trail` / DBA-facing bullets — **governance-adjacent** evidence aligned with [REPORTS_AND_COMPLIANCE_OUTPUTS.md](../REPORTS_AND_COMPLIANCE_OUTPUTS.md). |

Net: the **client** gains a **repeatable, session-scoped governance narrative** (methodology + APG + manifest pointer) **without** re-running scans — that path did not exist as a first-class CLI deliverable on the legacy tag side of the A/B.

---

## 3. Performance (wall time — completão orchestrator)

**Source of truth:** `benchmark_runs/times.txt` (written by `scripts/benchmark-ab.ps1`).

| Round | Git ref (typical) | `Measure-Command` field in `times.txt` | Value (fill after run) |
| --- | --- | --- | --- |
| **A — Legacy** | `v1.7.3` | `legacy_total_seconds` / `legacy_total_milliseconds` | **TBD** |
| **B — Current** | e.g. `origin/main` or feature branch via `-CurrentLabGitRef` | `current_total_seconds` / `current_total_milliseconds` | **TBD** |

**Interpretation:** difference is **orchestrator wall time** (SSH, lab git ensure, inventory, smoke, optional GRC hooks) — not a micro-benchmark of Python hot paths. Call a swing **significant** only if repeats cluster (same manifest, same lab day) and network/sudo/Docker noise is ruled out.

### 3.1 Pinned 200k A/B (OpenCore vs Pro path) — direction-only evidence

**Artifact:** [`tests/benchmarks/official_benchmark_200k.json`](../../tests/benchmarks/official_benchmark_200k.json) (frozen 2026-04-25 lab session, untouched in this Slice).

| Field | Value |
| --- | --- |
| `opencore_seconds` | `0.252242` |
| `pro_seconds` | `0.439419` |
| `speedup_vs_opencore` (`= t_open / t_pro`) | `0.574` |
| `opencore_hits` / `pro_hits` | `100000` / `100000` (parity) |

**Reading guide (Julia Evans-style — do not double-invert):**

- `speedup_vs_opencore = 0.574` means **Pro is 0.574x as fast as** OpenCore.
- The operator-chat phrasing **"0.574x mais lento"** points at the same direction (Pro slower) using the same numeric anchor.
- Pro wall-clock ≈ `1 / 0.574 ≈ 1.74x` the OpenCore wall-clock in this profile.

**Regression guard:** [`tests/test_official_benchmark_200k_evidence.py`](../../tests/test_official_benchmark_200k_evidence.py) pins direction (`pro_seconds > opencore_seconds`, `speedup < 1.0`), arithmetic (`recorded ≈ opencore_seconds / pro_seconds`), and findings parity (`opencore_hits == pro_hits`). Future executive copy or manifests that flip the sign without regenerating the JSON will fail CI loudly.

**Doctrinal reading of the result** (see manifestos at [`docs/ops/inspirations/`](../ops/inspirations/)):

- *DEFENSIVE_SCANNING_MANIFESTO* — sample caps and statement timeouts that protect the customer DB are not free; the Pro path's extra wall-clock in this profile is the cost of stricter sampling discipline (no `ORDER BY`, leading SQL comment, dialect-specific clamps). The recorded JSON is the *evidence* that those guarantees do not silently regress.
- *THE_ART_OF_THE_FALLBACK* — findings parity (`100000 == 100000`) is asserted **before** any speed comparison: a defensive scanner protects detection coverage even when the Pro path is slower.
- *ACTIONABLE_GOVERNANCE_AND_TRUST* — the 200k JSON sits next to the executive Markdown produced by `data-boar-report` and the manifest YAML; together they form the customer trust triangle. Removing any leg degrades the deliverable to a slide deck.

---

## 4. Security — “protocols” and scan posture (evidence model)

**Clarification:** `safety_protocol` / `sampling_method` are **not** columns on `scan_sessions` in the canonical SQLite schema (`core/database.py`). Posture lives in:

- **`scan_manifest_*.yaml`**: `safety_tags`, `audit_trail`, scope snapshot, engine signature.
- **Executive Markdown §3**: human-readable condensation of that posture.

| Signal | Where it appears | Legacy vs current (conceptual) |
| --- | --- | --- |
| Sampling row caps / strategy | `safety_tags` / audit narrative | Current stack documents **resolved caps** and **timeout hints** for DB sampling (see `report/scan_evidence.py`, `core/scan_audit_log.py`). |
| Dialect / isolation bullets (e.g. `NOLOCK`, `statement_timeout`) | `audit_trail.dba_facing_summary_pt` + §3 text | **Newer** manifests/tests expect these bullets when SQL Server (or other configured engines) participate — compare YAML side-by-side for the two benchmark folders. |
| Traceability comment on sample SQL | `leading_sql_comment` / §3 | Confirms **attributed** workload in engine telemetry. |

**Fill after run:** paste one-line deltas (e.g. “baseline manifest lacked X; head includes Y”) from diffing the two `scan_manifest_*.yaml` files captured under `benchmark_runs/v1.7.3/` vs `benchmark_runs/v1.7.4-beta/` (or your `-CurrentCaptureDir` name).

---

## 5. Business value — examples of APG-style recommendations (replace with your session text)

The **RecommendationEngine** maps patterns to **Phase A** actions (`core.recommendations` / `report/recommendation_engine.py`). The executive report surfaces them in **§4.1** (Top 3) and **§4.2** (inventory). Until you paste real bullets from **`executive_report_benchmark.md`**, these are **illustrative** patterns validated in tests (not claims about your lab SQLite):

| Pattern (example) | Risk band (example) | Type of recommendation |
| --- | --- | --- |
| `CREDIT_CARD` | PCI / Bloqueante | Tokenization / PAN handling; PCI-DSS alignment language. |
| `LGPD_CPF` / `CPF` | Alta | Dynamic masking / titular-data handling. |
| `EMAIL` | Médio | Masking / homologation in non-prod flows. |

**Action:** open `benchmark_runs/v1.7.4-beta/*.md`, copy the **Top 3** lines and 1–2 inventory blocks **redacted** (no tenant-specific prose), and replace this table.

---

## 6. SQLite file size (sampling vs density)

**Not asserted here:** file byte size depends on **row counts** in findings tables, optional inventory/aggregates, and whether the same session(s) are in both DBs. After each benchmark:

```text
(Get-Item benchmark_runs/v1.7.3/*.db).Length
(Get-Item benchmark_runs/v1.7.4-beta/*.db).Length
```

Compare **and** `SELECT COUNT(*) FROM database_findings` / `filesystem_findings` per session. Sampling reduces **read** pressure; DB size follows **persisted** rows + schema, not “lighter” by definition.

---

## 7. Related automation

| Script | Purpose |
| --- | --- |
| `scripts/benchmark-ab.ps1` | Git checkout A/B, `Measure-Command`, `benchmark_runs/times.txt`, copy logs / optional SQLite / optional `data-boar-report` output. |
| `scripts/benchmark_sqlite_diff.py` | Table/column diff between two SQLite files (optional `scan_metadata` checklist if you maintain that table in lab DBs). |

---

## 8. v1.7.3 → HEAD narrative (Slice 4 of `PLAN_ENGINEERING_DOCTRINE_CONSOLIDATION`)

This section closes the loop on `PLAN_ENGINEERING_DOCTRINE_CONSOLIDATION.md` Slice 4: it names where v1.7.3 → HEAD gained **resilience** (Art of the Fallback) and **coverage** (Defensive Scanning) without collapsing the production-like profile back into marketing speedups.

### 8.1 Resilience gains (Art of the Fallback)

- **Completão failure-path RCA blocks** (`scripts/lab-completao-orchestrate.ps1`, Slice 2): the orchestrator no longer writes a one-line `failed` message and exits. Each phase failure (`inventory_preflight`, `lab_git_ensure_ref`, `data_contract_preflight`, `image_preflight`, `host_smoke`, `grc_executive_report`, `grc_export_artifacts`) writes a Sysinternals-style block with phase name, narrowed hypotheses, next concrete step, and a structured `rca_<phase>` JSONL event under `docs/private/homelab/reports/completao_*_orchestrate_events.jsonl`. Future tooling can grep that file to triage completão runs without reading PowerShell line-by-line.
- **`data-boar-report` failure-path RCA block** (`cli/reporter.py`, Slice 2): the executive Markdown CLI emits a structured RCA block on empty `--session-id`, on output-path-escapes-cfg-dir guard hits, and on any exception during manifest + report generation, then re-raises so existing test behaviour is preserved.
- **Methodology-of-Safety proof block** in the executive Markdown (`report/executive_report.py`, Slice 2): under section 3 the report now narrates **why** the existing sample caps and timeouts protect the customer DB. This is read-only narration around values already in `manifest['safety_tags']`; the clamps remain enforced in `connectors/sql_sampling.py` (`_HARD_MAX_SAMPLE = 10_000`, statement timeout clamp `250..60_000` ms).
- **Doctrinal docstrings** in `connectors/sql_sampling.py`, `core/scan_audit_log.py`, and `report/executive_report.py` (Slice 3): each module now cross-references the relevant manifesto so a future refactor PR cannot silently strip the leading `-- Data Boar Compliance Scan` comment, the cap clamp, or the disclaimer field without updating the doctrine first.

### 8.2 Coverage gains (Defensive Scanning posture)

- **200k A/B regression guard** (Slice 1 / 2026-04-25 + 2026-04-27 erratum): the recorded JSON is now machine-readable evidence that the Pro path keeps `100000 == 100000` finding parity with OpenCore even when slower (`speedup_vs_opencore = 0.574`). Coverage cannot silently drop in exchange for performance.
- **Audit log echoes the relief valves** (`core/scan_audit_log.py`): `nolock`, `statement_timeout_ms`, `leading_sql_comment`, and `connector_default_statement_timeout_ms_when_unset` mirror the values clamped in `connectors/sql_sampling.py` so `GET /status` and the executive report quote the same numbers.
- **Strategy labels never silently fall through** (`THE_ART_OF_THE_FALLBACK.md`): sampling plans carry `strategy_label` / `audit_notes` and the executive report's section 3 quotes the **last** demotion reason — a reviewer can re-run with the same `session_id` and reproduce the path the scanner actually took.

### 8.3 Pinned constraints (non-negotiable through this slice)

| Constraint | Where it lives | Why it matters |
| ---------- | -------------- | -------------- |
| `_HARD_MAX_SAMPLE = 10_000` | `connectors/sql_sampling.py::_HARD_MAX_SAMPLE` | Cap is enforced in code; YAML / env values clamp to it. |
| Statement timeout `250..60_000` ms | `resolve_statement_timeout_ms_for_sampling` | Prevents indefinite session pinning on the customer DB. |
| Leading `-- Data Boar Compliance Scan` | `_COMPLIANCE_SCAN_LEADING` | DBA-grep contract from `DEFENSIVE_SCANNING_MANIFESTO.md` §4. |
| No `ORDER BY` in auto-sampling | `connectors/sql_sampling.py` composition layer | Avoids forced full-table sorts; ordering requires an ADR + explicit flag. |
| Findings parity asserted before performance | `tests/test_official_benchmark_200k_evidence.py::test_benchmark_findings_parity` | Defensive scanner protects coverage even if Pro is slower. |

These are exactly the constraints the Slack handoff named as "non-negociáveis"; this slice integrates the 0.574x evidence into the v1.7.3 → HEAD narrative without re-running the harness or weakening any of them.

---

## Revision log

| Date | Author | Change |
| --- | --- | --- |
| 2026-04-27 | data-boar-sre-agent | Slice 4: refreshed for v1.7.3 → HEAD narrative; added §3.1 (200k A/B reading guide) and §8 (resilience + coverage gains, pinned constraints) integrating the 0.574x figure. Performance §3 numbers still TBD until a fresh `times.txt` exists. |
| (fill) | maintainer | Initial consolidation; performance TBD until local `times.txt` exists. |
