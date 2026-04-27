mod filter_logic;

use filter_logic::CompiledPatterns;
use pyo3::exceptions::PyRuntimeError;
use pyo3::prelude::*;

#[pyclass]
pub struct FastFilter {
    patterns: CompiledPatterns,
}

#[pymethods]
impl FastFilter {
    #[new]
    fn new() -> PyResult<Self> {
        let patterns = CompiledPatterns::new().map_err(|e| {
            PyRuntimeError::new_err(format!("fast filter regex compile error: {e}"))
        })?;
        Ok(FastFilter { patterns })
    }

    /// Return only suspect indexes from the input batch.
    /// Panic-free by design: regex matching does not unwrap dynamic state.
    fn filter_batch(&self, batch: Vec<String>) -> PyResult<Vec<usize>> {
        Ok(self.patterns.suspect_indices(&batch))
    }
}

#[pymodule]
fn boar_fast_filter(_py: Python<'_>, m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_class::<FastFilter>()?;
    Ok(())
}
