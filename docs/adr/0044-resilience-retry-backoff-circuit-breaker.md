# ADR 0044: Resilience — exponential backoff with jitter and per-target circuit breaker

## Context

Data Boar connects to many target systems on the customer side: SQL engines (PostgreSQL, MySQL, Oracle, SQL Server), Snowflake, MongoDB, REST endpoints, and file shares. Customer infrastructure regularly exhibits **transient** failure modes — TCP resets, connection pool saturation, replica failovers, brief network partitions, statement timeouts under load.

The previous behavior had two gaps for these cases:

1. **Tight retry loops or no retries at all.** Connectors raised on the first transient error and the engine recorded a single `save_failure(reason="unreachable")`. A flaky target was either silently unscanned or hammered with whatever retry semantics the underlying driver happened to apply.
2. **No protection against zombie targets.** A single unresponsive Snowflake warehouse or Oracle service could re-attempt every row sample in a long-running scan, eating threads and burning customer DB time. There was no concept of "this target is misbehaving — leave it alone for a while and continue with the others."

The defensive scanning manifesto (`docs/ops/inspirations/DEFENSIVE_SCANNING_MANIFESTO.md`) and the fallback doctrine (`docs/ops/inspirations/THE_ART_OF_THE_FALLBACK.md`) require:

- **Bounded** I/O on every customer DB call.
- **No silent failure** — every demotion (retry, trip, skip) leaves an audit row.
- **Blast radius** containment — one misbehaving target must not kill the rest of the scan.

## Decision

Introduce a small, dependency-free resilience module in `core/resilience.py`:

1. **Exponential backoff with full jitter.** `compute_backoff_delay(attempt)` returns the sleep duration before the next retry. The default ladder is the agreed **1 s → 4 s → 10 s** (deterministic targets); with `jitter=True` (default) we apply `random.uniform(0, target)` to spread thundering-herd retries across many parallel workers. Past the ladder, classic exponential growth `base * 2^(attempt-1)` is clamped to `retry_max_seconds`.

2. **Per-target circuit breaker.** `CircuitBreaker` implements the canonical CLOSED → OPEN → HALF_OPEN lifecycle:
   - `CLOSED`: traffic flows; transient failures are counted.
   - After `failure_threshold=3` consecutive transient failures the breaker **trips** (`OPEN`).
   - While `OPEN`, calls short-circuit immediately with `CircuitOpenError` for `cooldown_seconds=900` (**15 minutes**) — no I/O, no retry.
   - When the cooldown elapses, the next call enters `HALF_OPEN`: one probe is allowed through. Success → `CLOSED`. Failure → `OPEN` again, fresh cooldown.

3. **Transient classification.** `is_transient_error(exc)` matches by class name to avoid importing every optional driver: `TimeoutError`, `ConnectionError`, `OperationalError`, `InterfaceError`, `ServerSelectionTimeoutError`, `AutoReconnect`, `OSError`-family, etc. Programmer errors (`ValueError`, `TypeError`, `KeyError`, `AttributeError`) are **never** retried and **never** trip the breaker.

4. **Engine integration (`core/engine.py`).** `_run_target` consults the breaker registry **before** invoking the connector. If the breaker for `target:<name>` is `OPEN`, the engine writes a structured `save_failure(reason="circuit_open")` row including blast-radius metadata (consecutive failures, retry-after seconds, cooldown, last error class and reason) and continues with the remaining targets.

5. **Connector integration.** `connect()` in `SQLConnector`, `SnowflakeConnector`, and `MongoDBConnector` now wraps the I/O call in `breaker.call(...)`. Driver-level retries collapse into the resilience ladder rather than each driver inventing its own.

6. **Telemetry.** Every breaker emits structured log lines (`[resilience] retry`, `circuit_tripped`, `short_circuit`, `circuit_half_open`, `circuit_closed`) and exposes a JSON-serializable snapshot via `all_circuit_telemetry()`. The engine exposes that snapshot through `AuditEngine.get_scan_audit_log()` under the `circuit_breakers` key — making it visible to the dashboard and the audit log API.

7. **Configuration.** Per-target YAML block (optional):

   ```yaml
   targets:
     - name: warehouse_lgpd
       type: database
       driver: snowflake
       circuit_breaker:
         failure_threshold: 3
         cooldown_seconds: 900
         retry_attempts: 3
         retry_max_seconds: 10
         jitter: true
   ```

   Environment overrides (process-wide, useful for `completão` smoke runs):
   `DATA_BOAR_CIRCUIT_FAILURE_THRESHOLD`, `DATA_BOAR_CIRCUIT_COOLDOWN_SECONDS`, `DATA_BOAR_RETRY_ATTEMPTS`, `DATA_BOAR_RETRY_MAX_SECONDS`.

## Consequences

- **Positive — guest contract.** A flaky customer DB receives at most **3** attempts with bounded backoff, then is left alone for 15 minutes. We never tight-loop on a host that is on fire.
- **Positive — blast radius.** One zombie target no longer aborts the scan: the engine writes a `circuit_open` failure row and processes the remaining targets normally. Operators see the breaker state in `audit_log.circuit_breakers`.
- **Positive — observability.** Every demotion is logged with the underlying exception class and short reason (PII-safe, redacted via `sanitize_log_text` when persisted to SQLite). This satisfies the Mark Russinovich / Cloudflare-style "why did it fail?" requirement from the engineering mission.
- **Trade-off — coverage.** A target that flaps right at the 3-strike threshold may be skipped on a particular run. That is the **correct** trade-off: skipping a sick target and reporting it as such beats pretending the scan was complete. Operators can override per-target with a higher `failure_threshold` if their environment legitimately needs it.
- **Trade-off — cooldown idleness.** A target that recovers quickly waits the full cooldown before the HALF_OPEN probe. That is the documented behavior; operators can shorten `cooldown_seconds` for noisy lab environments.

## Non-goals

- This ADR does **not** introduce per-statement retry inside the sampling loop. Sampling already has its own bounded timeout (`DATA_BOAR_SAMPLE_STATEMENT_TIMEOUT_MS`) and cannot retry against a customer DB without inflating I/O.
- It does **not** change the sampling SQL contract (`-- Data Boar Compliance Scan` leading comment, `WITH (NOLOCK)`, no `ORDER BY`, etc.) — see ADR 0043 and the defensive scanning manifesto.

## References

- [`core/resilience.py`](../../core/resilience.py)
- [`core/engine.py`](../../core/engine.py) — `_run_target`, `get_scan_audit_log`
- [`connectors/sql_connector.py`](../../connectors/sql_connector.py), [`connectors/snowflake_connector.py`](../../connectors/snowflake_connector.py), [`connectors/mongodb_connector.py`](../../connectors/mongodb_connector.py)
- [`tests/test_resilience.py`](../../tests/test_resilience.py), [`tests/test_engine_circuit_breaker.py`](../../tests/test_engine_circuit_breaker.py)
- [`docs/ops/inspirations/DEFENSIVE_SCANNING_MANIFESTO.md`](../ops/inspirations/DEFENSIVE_SCANNING_MANIFESTO.md)
- [`docs/ops/inspirations/THE_ART_OF_THE_FALLBACK.md`](../ops/inspirations/THE_ART_OF_THE_FALLBACK.md)
- AWS Architecture Blog — *Exponential Backoff and Jitter* (Marc Brooker, 2015)
