mod bounded_filter;

use bounded_filter::{BoundedFilter, BudgetReport};
use pyo3::exceptions::PyRuntimeError;
use pyo3::prelude::*;
use pyo3::types::{PyDict, PyList, PyTuple};
use regex::Regex;

/// PyO3 wrapper around `bounded_filter::BoundedFilter`.
///
/// Exposes one method, `filter_batch_bounded`, that returns a tuple of
/// `(suspect_indices: list[int], report: dict[str, Any])`. The `report` dict
/// keys are stable strings consumed by `core/scan_audit_log.py`; do not
/// rename them without updating both ends and the manifesto cross-link in
/// `docs/ops/inspirations/THE_ART_OF_THE_FALLBACK.md` §5.
#[pyclass(name = "BoundedFilter")]
pub struct PyBoundedFilter {
    inner: BoundedFilter,
}

#[pymethods]
impl PyBoundedFilter {
    #[new]
    fn new() -> PyResult<Self> {
        let inner = BoundedFilter::new().map_err(|e| {
            PyRuntimeError::new_err(format!("BoundedFilter regex compile error: {e}"))
        })?;
        Ok(Self { inner })
    }

    /// Filter a batch under a per-row size cap (bytes) and wall-clock budget (ms).
    ///
    /// Pass `0` for either argument to use the documented hard ceiling
    /// (4 MiB / 60 s). Values above the ceiling are clamped, never honored.
    #[pyo3(signature = (batch, max_row_bytes=0, wall_clock_ms=0))]
    fn filter_batch_bounded<'py>(
        &self,
        py: Python<'py>,
        batch: Vec<String>,
        max_row_bytes: usize,
        wall_clock_ms: u64,
    ) -> PyResult<Bound<'py, PyTuple>> {
        let (indices, report) =
            self.inner
                .filter_batch_bounded(&batch, max_row_bytes, wall_clock_ms);
        let py_indices = PyList::new(py, indices)?;
        let py_report = budget_report_to_pydict(py, &report)?;
        PyTuple::new(py, &[py_indices.into_any(), py_report.into_any()])
    }

    /// Read-only access to the doctrine ceilings (so Python tests can
    /// assert on the exact values without re-declaring them).
    #[staticmethod]
    fn hard_max_row_bytes() -> usize {
        bounded_filter::HARD_MAX_ROW_BYTES
    }

    #[staticmethod]
    fn hard_max_wall_clock_ms() -> u64 {
        bounded_filter::HARD_MAX_WALL_CLOCK_MS
    }
}

fn budget_report_to_pydict<'py>(
    py: Python<'py>,
    report: &BudgetReport,
) -> PyResult<Bound<'py, PyDict>> {
    let dict = PyDict::new(py);
    dict.set_item("rows_scanned", report.rows_scanned)?;
    dict.set_item("rows_skipped_oversize", report.rows_skipped_oversize)?;
    dict.set_item("rows_skipped_budget", report.rows_skipped_budget)?;
    dict.set_item("wall_clock_exceeded", report.wall_clock_exceeded)?;
    dict.set_item("effective_max_row_bytes", report.effective_max_row_bytes)?;
    dict.set_item("effective_wall_clock_ms", report.effective_wall_clock_ms)?;
    match &report.demotion_reason {
        Some(reason) => dict.set_item("demotion_reason", reason)?,
        None => dict.set_item("demotion_reason", py.None())?,
    }
    Ok(dict)
}

#[pyclass]
pub struct FastFilter {
    // Compiled once; reused for all batches.
    cpf_pattern: Regex,
    email_pattern: Regex,
    credit_card_pattern: Regex,
}

#[pymethods]
impl FastFilter {
    #[new]
    fn new() -> PyResult<Self> {
        let cpf_pattern = Regex::new(r"\d{3}\.?\d{3}\.?\d{3}-?\d{2}")
            .map_err(|e| PyRuntimeError::new_err(format!("cpf regex compile error: {e}")))?;
        let email_pattern = Regex::new(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}")
            .map_err(|e| PyRuntimeError::new_err(format!("email regex compile error: {e}")))?;
        let credit_card_pattern = Regex::new(r"\b(?:\d[ -]*?){13,19}\b").map_err(|e| {
            PyRuntimeError::new_err(format!("credit card regex compile error: {e}"))
        })?;
        Ok(FastFilter {
            cpf_pattern,
            email_pattern,
            credit_card_pattern,
        })
    }

    /// Return only suspect indexes from the input batch.
    /// Panic-free by design: regex matching does not unwrap dynamic state.
    fn filter_batch(&self, batch: Vec<String>) -> PyResult<Vec<usize>> {
        let mut suspects = Vec::new();
        for (idx, content) in batch.iter().enumerate() {
            if self.cpf_pattern.is_match(content) || self.email_pattern.is_match(content) {
                suspects.push(idx);
                continue;
            }
            if self.has_valid_luhn_card(content) {
                suspects.push(idx);
            }
        }
        Ok(suspects)
    }
}

impl FastFilter {
    fn has_valid_luhn_card(&self, content: &str) -> bool {
        self.credit_card_pattern
            .find_iter(content)
            .any(|m| Self::check_luhn(m.as_str()))
    }

    fn check_luhn(card_number: &str) -> bool {
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
                    if d > 9 { d - 9 } else { d }
                } else {
                    digit
                }
            })
            .sum();

        sum % 10 == 0
    }
}

#[pymodule]
fn boar_fast_filter(_py: Python<'_>, m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_class::<FastFilter>()?;
    m.add_class::<PyBoundedFilter>()?;
    Ok(())
}
