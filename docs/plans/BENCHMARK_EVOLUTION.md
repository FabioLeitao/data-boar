# Benchmark evolution — completão A/B (legacy tag vs current)

**Status:** living note — fill **Performance** numbers from `benchmark_runs/times.txt` after each `scripts/benchmark-ab.ps1` run. Replace **Business value** bullets with phrases copied from your generated Markdown under `benchmark_runs/<current>/` (no raw PII).

**Doctrine cycle status (Slices 1–4):** Slice 1 (manifestos) and Slice 4 (this file) are doc-only. Slice 2 added a Sysinternals-style RCA block to `python -m cli.reporter` so a failed regen names the failed step (`load_config`, `open_sqlite`, `fetch_findings`, `build_manifest`, `render_markdown`, `write_output`) plus a narrowed hypothesis and the smallest deterministic command an operator can paste — **stdout** stays clean for piped Markdown, **stderr** carries the RCA. Slice 3 fused the Pro Python fallback into a single pass (`pro/worker_logic.py::basic_python_scan`) and skipped the redundant per-chunk string-coercion copy in `pro/engine.py::process_chunk_worker`; precision contract (CPF regex, email regex, Luhn validator, hard sample caps, statement timeouts) is unchanged. Pinned by `tests/test_cli_reporter_rca.py` and `tests/test_basic_python_scan_single_pass_parity.py`.

**Scope:** Lab orchestration (`lab-completao-orchestrate.ps1`) plus optional **`data-boar-report`** (`python -m cli.reporter`, see [USAGE.md](../USAGE.md) section 5) when the benchmark script is invoked with `-ReportConfigYaml` / `-ReportSessionId`.

**Nomenclature (avoid `paths:` / pathspec mistakes):**

- **`data-boar-report`** is the **console script name** for the **Python** executive-report CLI (`cli/reporter.py`, entry `cli.reporter:main` in `pyproject.toml`). It reads **local SQLite** and writes stakeholder Markdown — it is **not** a Rust crate and **not** a directory under the repo root.
- The **Rust** optional pre-filter is the **`boar_fast_filter`** package in **`rust/boar_fast_filter/`** (Cargo `name = "boar_fast_filter"`). GitHub Actions **`Rust CI`** (`.github/workflows/rust-ci.yml`) must list **`rust/**`** (and the workflow file) under `on.push.paths` / `on.pull_request.paths`. Using an unrelated label (for example the **Python** CLI name above) in those filters causes **wrong or empty pathspec matches** and skips CI when only the Rust tree changes.

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

## 8. 0.574x Pro path — current technical debt baseline (operator-pinned)

`tests/benchmarks/official_benchmark_200k.json` records a Pro-path **`speedup_vs_opencore = 0.574`** at 200k rows / 8 workers (`opencore_seconds = 0.252242`, `pro_seconds = 0.439419`). In plain English: in this profile the Pro path takes roughly `1 / 0.574 ≈ 1.74x` more time than the OpenCore baseline. **The direction is correct — Pro is slower in this profile** — and `tests/test_official_benchmark_200k_evidence.py` enforces it so a future commit cannot silently flip the sign without also updating the JSON artifact.

**Why we are not chasing a "Pro faster" number in this PR cycle:**

- The recorded Pro path runs without the Rust `boar_fast_filter` extension on the lab host (the Python fallback `pro.worker_logic.basic_python_scan` is the hot path). Until the Rust extension is universally available across the lab matrix, the operator-pinned benchmark is the **honest** A/B; inverting it would violate `docs/ops/inspirations/INTERNAL_DIAGNOSTIC_AESTHETICS.md` §4 ("no invented numbers").
- Slice 3 addressed the **algorithmic** side of the bottleneck only: one fused predicate pass instead of two, and zero per-chunk string-coercion copy on the documented hot path. Sample caps, statement timeouts, isolation level, dialect posture, and precision logic were **not** modified — that is the safety rail the operator named in the Slack mission brief.
- The next benchmark run on the lab will measure the algorithmic delta against the recorded baseline. The JSON artifact will be regenerated **on the lab host**, in the same `scripts/benchmark-ab.ps1` cycle — not on the agent VM, where wall-time is not comparable.

**Reading the 0.574x figure (Julia Evans-style note):**

```text
opencore_seconds  = 0.252242  (Open Core regex prefilter)
pro_seconds       = 0.439419  (Pro Python fallback after Slice 3 baseline)
speedup_vs_open   = 0.574     (= opencore_seconds / pro_seconds, rounded)
direction         = Pro slower in this profile (no Rust extension)
fallback path     = pro.worker_logic.basic_python_scan
                    (single-pass after Slice 3; was two-pass before)
```

The recorded `pro_hits == opencore_hits` (both 100_000) is the precision invariant: any commit that drops `pro_hits` below `opencore_hits` is a **scanner regression**, not a "performance optimization". `tests/test_official_benchmark_200k_evidence.py::test_benchmark_findings_parity` fails first if that ever happens.

---

## 9. Rust CI, local Rust guard, and Python 3.14+ (ABI3)

### Rust CI Infrastructure

- [x] **Rust CI Infrastructure** — **`.github/workflows/rust-ci.yml`** runs `cargo fmt`, `cargo check`, `cargo test`, and `cargo clippy` with `defaults.run.working-directory: rust/boar_fast_filter`, and `on.<event>.paths` includes **`rust/**`** plus the workflow file so edits to the **real** crate path always trigger the job (see § *Nomenclature* above).

### Local build / gate (ABI3 forward compatibility)

- The **`boar_fast_filter`** crate enables PyO3 **`abi3-py37`** (`rust/boar_fast_filter/Cargo.toml`). For **CPython 3.14+** on the operator workstation, the full local gate (**`scripts/check-all.ps1`** / **`scripts/check-all.sh`**) sets **`PYO3_USE_ABI3_FORWARD_COMPATIBILITY=1`** for the nested **`cargo fmt` / `cargo check` / `cargo test`** step in **`rust/boar_fast_filter/`**, so the Rust guard stays green while upstream PyO3 finalizes support for newer ABIs.

---

## Revision log

| Date | Author | Change |
| --- | --- | --- |
| 2026-04-27 | doctrine-cycle | Closed Slices 1–3 of [PLAN_ENGINEERING_DOCTRINE_CONSOLIDATION.md](PLAN_ENGINEERING_DOCTRINE_CONSOLIDATION.md): manifestos shipped (Slice 1), RCA block in `cli/reporter.py` (Slice 2), single-pass Pro fallback + chunk-copy skip in `pro/worker_logic.py` / `pro/engine.py` (Slice 3). 0.574x recorded as the **technical debt baseline** (§8 above). |
| 2026-04-27 | maintainer | §9 + preamble **nomenclature**: distinguish **`data-boar-report`** (Python CLI, `cli/reporter.py`) from **`boar_fast_filter`** (`rust/boar_fast_filter/`); document correct **`paths:`** filters vs pathspec confusion; mark **Rust CI Infrastructure** complete; note **`PYO3_USE_ABI3_FORWARD_COMPATIBILITY`** for local **check-all** Rust guard on Python **3.14+**. |
| (fill) | maintainer | Initial consolidation; performance TBD until local `times.txt` exists. |
