use pyo3::exceptions::PyRuntimeError;
use pyo3::prelude::*;
use regex::Regex;

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
    Ok(())
}
