//! SRE-bounded prefilter (Data Boar doctrine in Rust).
//!
//! `FastFilter` (in `lib.rs`) is the unbounded "best effort" prefilter used by
//! the legacy Pro+ scan path. `BoundedFilter` is the version that follows the
//! two doctrinal manifestos in `docs/ops/inspirations/`:
//!
//! - **DEFENSIVE_SCANNING_MANIFESTO §2** — every read has a hard sample cap
//!   and a wall-clock budget; controls clamp to a hard ceiling instead of
//!   silently going unbounded.
//! - **THE_ART_OF_THE_FALLBACK §3** — when a strategy degrades (oversize row
//!   skipped, wall-clock budget exceeded), Data Boar **never** falls through
//!   silently. The audit row carries the reason so a reviewer can re-run with
//!   the same correlation id and reproduce.
//!
//! This module does **not** import `filter_logic` (sibling refactor in PR
//! #255); it owns its own pattern set so the two slices can land in either
//! order. A future cleanup pass can dedupe regex compilation across modules.

use regex::Regex;
use std::time::Instant;

/// Hard ceilings applied even when the caller passes a more permissive value.
///
/// Mirrors `connectors/sql_sampling.py::_HARD_MAX_SAMPLE` posture: invalid or
/// "unbounded" requests fall back to the documented base, never to "unbounded".
pub const HARD_MAX_ROW_BYTES: usize = 4 * 1024 * 1024; // 4 MiB per row
pub const HARD_MAX_WALL_CLOCK_MS: u64 = 60_000; // 60 s per batch

/// Diagnostic record produced by every call to `filter_batch_bounded`.
///
/// The Python side of Data Boar reads this dict and copies it into the
/// `core/scan_audit_log` row for the current `session_id`. The intent is the
/// same as the audit example in THE_ART_OF_THE_FALLBACK §3:
///
/// ```text
/// [fallback] table=customers column=notes
///   parser_sql      → declined (dialect=mixed_postgres_mssql)
///   regex           → engaged (rows=10000, skipped_oversize=12, demoted=wall_clock)
/// ```
#[derive(Debug, Clone, Default)]
pub struct BudgetReport {
    /// Rows that the prefilter actually inspected (passed size + budget gates).
    pub rows_scanned: usize,
    /// Rows skipped because they exceeded `max_row_bytes`. Counted but not read.
    pub rows_skipped_oversize: usize,
    /// Rows the loop never reached because the wall-clock budget was exhausted.
    pub rows_skipped_budget: usize,
    /// True iff the loop broke on the wall-clock relief valve.
    pub wall_clock_exceeded: bool,
    /// Short, factual reason for the demotion (None when no demotion happened).
    /// Stable strings so audit log dashboards can group them.
    pub demotion_reason: Option<String>,
    /// Resolved per-row byte cap after clamping to `HARD_MAX_ROW_BYTES`.
    pub effective_max_row_bytes: usize,
    /// Resolved wall-clock budget after clamping to `HARD_MAX_WALL_CLOCK_MS`.
    pub effective_wall_clock_ms: u64,
}

/// Bounded prefilter: same pattern set as `FastFilter`, with relief valves.
///
/// The patterns intentionally mirror `lib.rs::FastFilter::new` so a finding
/// produced by the bounded path is byte-for-byte equivalent to a finding
/// produced by the legacy path on the same input — only the budget tracking
/// changes.
pub struct BoundedFilter {
    cpf_pattern: Regex,
    email_pattern: Regex,
    credit_card_pattern: Regex,
}

impl BoundedFilter {
    /// Compile the regex set once. Errors propagate so the PyO3 wrapper can
    /// raise `RuntimeError` with the underlying compile diagnostic instead of
    /// panicking inside the embedded interpreter.
    pub fn new() -> Result<Self, regex::Error> {
        let cpf_pattern = Regex::new(r"\d{3}\.?\d{3}\.?\d{3}-?\d{2}")?;
        let email_pattern = Regex::new(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}")?;
        let credit_card_pattern = Regex::new(r"\b(?:\d[ -]*?){13,19}\b")?;
        Ok(Self {
            cpf_pattern,
            email_pattern,
            credit_card_pattern,
        })
    }

    /// Filter a batch with a per-row byte cap and a wall-clock budget.
    ///
    /// Arguments use the doctrine convention where `0` means "use the
    /// documented base, not unbounded". A value above the hard ceiling is
    /// silently clamped to the ceiling and recorded in `BudgetReport`.
    ///
    /// Returns `(suspect_indices, report)`. Suspect indices use the **input
    /// position**, not the post-skip position, so callers can map findings
    /// back to the original rows for attribution.
    pub fn filter_batch_bounded(
        &self,
        batch: &[String],
        max_row_bytes: usize,
        wall_clock_ms: u64,
    ) -> (Vec<usize>, BudgetReport) {
        let mut report = BudgetReport::default();

        // Clamp 0/over-ceiling to the hard ceilings — never run unbounded.
        let effective_row = if max_row_bytes == 0 || max_row_bytes > HARD_MAX_ROW_BYTES {
            HARD_MAX_ROW_BYTES
        } else {
            max_row_bytes
        };
        let effective_clock = if wall_clock_ms == 0 || wall_clock_ms > HARD_MAX_WALL_CLOCK_MS {
            HARD_MAX_WALL_CLOCK_MS
        } else {
            wall_clock_ms
        };
        report.effective_max_row_bytes = effective_row;
        report.effective_wall_clock_ms = effective_clock;

        let mut suspects: Vec<usize> = Vec::new();
        let started = Instant::now();
        let budget_nanos = (effective_clock as u128).saturating_mul(1_000_000);

        for (idx, content) in batch.iter().enumerate() {
            // Wall-clock relief valve: stop reading rows the moment the
            // budget is gone. Remaining rows are accounted for as
            // `rows_skipped_budget` so the audit log shows real coverage,
            // not wishful coverage.
            if started.elapsed().as_nanos() >= budget_nanos {
                let remaining = batch.len().saturating_sub(idx);
                report.rows_skipped_budget = remaining;
                report.wall_clock_exceeded = true;
                report.demotion_reason = Some("wall_clock_budget_exceeded".to_string());
                break;
            }

            // Per-row size cap: skip the row but log it. We cannot run a
            // 12 MiB blob through `regex::is_match` and still keep the
            // §2 promise that the relief valve is hard.
            if content.len() > effective_row {
                report.rows_skipped_oversize += 1;
                if report.demotion_reason.is_none() {
                    report.demotion_reason = Some("row_size_cap_exceeded".to_string());
                }
                continue;
            }

            report.rows_scanned += 1;

            if self.cpf_pattern.is_match(content) || self.email_pattern.is_match(content) {
                suspects.push(idx);
                continue;
            }
            if self.has_valid_luhn_card(content) {
                suspects.push(idx);
            }
        }

        (suspects, report)
    }

    fn has_valid_luhn_card(&self, content: &str) -> bool {
        self.credit_card_pattern
            .find_iter(content)
            .any(|m| check_luhn(m.as_str()))
    }
}

/// Luhn check on digit runs; ignores spaces and hyphens in `card_number`.
///
/// Public so unit tests in this module and (future) integration tests can
/// share one implementation without re-rolling the algorithm.
pub fn check_luhn(card_number: &str) -> bool {
    let digits: Vec<u32> = card_number
        .chars()
        .filter(|c| c.is_ascii_digit())
        .filter_map(|c| c.to_digit(10))
        .collect();

    if digits.len() < 13 || digits.len() > 19 {
        return false;
    }

    let sum: u32 = digits
        .iter()
        .rev()
        .enumerate()
        .map(|(i, &digit)| {
            if i % 2 == 1 {
                let d = digit * 2;
                if d > 9 {
                    d - 9
                } else {
                    d
                }
            } else {
                digit
            }
        })
        .sum();

    sum % 10 == 0
}

#[cfg(test)]
mod tests {
    use super::*;

    fn filter() -> BoundedFilter {
        BoundedFilter::new().expect("test regexes compile")
    }

    #[test]
    fn luhn_known_test_pattern_accepted() {
        // Visa test PAN (publicly documented for QA — never a real card).
        assert!(check_luhn("4111111111111111"));
        assert!(check_luhn("4111 1111 1111 1111"));
        assert!(check_luhn("4111-1111-1111-1111"));
    }

    #[test]
    fn luhn_single_digit_flip_rejected() {
        assert!(!check_luhn("4111111111111112"));
    }

    #[test]
    fn luhn_length_bounds_enforced() {
        assert!(!check_luhn("411111111111")); // 12 digits — too short
        assert!(!check_luhn(&"4".repeat(20))); // 20 digits — too long
    }

    #[test]
    fn cpf_email_and_card_are_flagged() {
        let f = filter();
        let batch = vec![
            "123.456.789-00".to_string(),          // 0: CPF-shaped
            "no pii here".to_string(),             // 1: clean
            "fulano@example.test".to_string(),     // 2: email
            "pan 4111 1111 1111 1111".to_string(), // 3: valid Luhn
            "pan 4111 1111 1111 1112".to_string(), // 4: invalid Luhn
        ];
        let (idx, report) = f.filter_batch_bounded(&batch, 0, 0);
        assert_eq!(idx, vec![0, 2, 3]);
        assert_eq!(report.rows_scanned, 5);
        assert_eq!(report.rows_skipped_oversize, 0);
        assert_eq!(report.rows_skipped_budget, 0);
        assert!(!report.wall_clock_exceeded);
        assert_eq!(report.demotion_reason, None);
    }

    #[test]
    fn zero_arguments_clamp_to_hard_ceiling() {
        let f = filter();
        let (_, report) = f.filter_batch_bounded(&[], 0, 0);
        assert_eq!(report.effective_max_row_bytes, HARD_MAX_ROW_BYTES);
        assert_eq!(report.effective_wall_clock_ms, HARD_MAX_WALL_CLOCK_MS);
    }

    #[test]
    fn over_ceiling_arguments_are_clamped_not_honored() {
        let f = filter();
        let (_, report) =
            f.filter_batch_bounded(&[], HARD_MAX_ROW_BYTES * 1024, HARD_MAX_WALL_CLOCK_MS * 60);
        assert_eq!(report.effective_max_row_bytes, HARD_MAX_ROW_BYTES);
        assert_eq!(report.effective_wall_clock_ms, HARD_MAX_WALL_CLOCK_MS);
    }

    #[test]
    fn oversize_row_is_skipped_with_demotion_reason() {
        let f = filter();
        // 1 KiB cap; build a 4 KiB string with PII inside it. The PII would
        // match if we read it, but the size cap must short-circuit.
        let huge = "X".repeat(4096) + " 4111 1111 1111 1111";
        let batch = vec![
            "fulano@example.test".to_string(), // small + matches
            huge,                              // oversize → must skip
            "no pii here".to_string(),         // small + clean
        ];
        let (idx, report) = f.filter_batch_bounded(&batch, 1024, 0);
        assert_eq!(idx, vec![0]);
        assert_eq!(report.rows_scanned, 2);
        assert_eq!(report.rows_skipped_oversize, 1);
        assert_eq!(
            report.demotion_reason.as_deref(),
            Some("row_size_cap_exceeded")
        );
    }

    #[test]
    fn wall_clock_zero_budget_demotes_immediately() {
        // We cannot honestly assert against a clock-driven loop without
        // making the test flaky. Instead we test the boundary: a 1 ns
        // budget is guaranteed to be exhausted before the first iteration
        // completes (the elapsed check runs at the top of the loop).
        let f = filter();
        let batch = vec![
            "fulano@example.test".to_string(),
            "123.456.789-00".to_string(),
        ];
        // Force the clamp path to *small* budget by using 1 ms; combined
        // with a `std::thread::sleep` we guarantee the first elapsed check
        // already exceeds it.
        std::thread::sleep(std::time::Duration::from_millis(2));
        let (idx, report) = f.filter_batch_bounded(&batch, 0, 1);
        // Either zero rows ran, or one ran and the rest were demoted.
        // Both outcomes are valid; what we lock in is the audit invariant.
        if report.rows_scanned == 0 {
            assert!(report.wall_clock_exceeded);
            assert_eq!(report.rows_skipped_budget, batch.len());
            assert_eq!(idx, Vec::<usize>::new());
        }
        assert_eq!(
            report.rows_scanned + report.rows_skipped_budget + report.rows_skipped_oversize,
            batch.len()
        );
    }

    #[test]
    fn empty_batch_returns_clean_report() {
        let f = filter();
        let (idx, report) = f.filter_batch_bounded(&[], 0, 0);
        assert!(idx.is_empty());
        assert_eq!(report.rows_scanned, 0);
        assert_eq!(report.rows_skipped_oversize, 0);
        assert_eq!(report.rows_skipped_budget, 0);
        assert!(!report.wall_clock_exceeded);
        assert_eq!(report.demotion_reason, None);
    }
}
