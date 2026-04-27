# Benchmark evolution — completão A/B (legacy tag vs current)

**Status:** living note — fill **Performance** numbers from `benchmark_runs/times.txt` after each `scripts/benchmark-ab.ps1` run. Replace **Business value** bullets with phrases copied from your generated Markdown under `benchmark_runs/<current>/` (no raw PII).

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

## Revision log

| Date | Author | Change |
| --- | --- | --- |
| (fill) | maintainer | Initial consolidation; performance TBD until local `times.txt` exists. |
