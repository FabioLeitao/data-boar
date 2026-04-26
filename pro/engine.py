"""
Pro+ scanner wrapper with optional Rust pre-filter.

When Rust extension is unavailable, behavior falls back to Open Core pre-filter.
"""

from __future__ import annotations

from collections.abc import Callable, Sequence
from typing import Any

from core.prefilter import OpenCorePreFilter
from pro.worker_logic import basic_python_scan

try:
    from boar_fast_filter import FastFilter

    RUST_AVAILABLE = True
except Exception:
    FastFilter = None  # type: ignore[assignment]
    RUST_AVAILABLE = False

_worker_filter_instance: Any = None


class ProScanner:
    """
    Pro scanner facade that narrows candidate rows before deep scan.

    ``deep_scan_fn`` and ``legacy_scan_fn`` are injected so this wrapper remains
    framework-agnostic and testable.
    """

    def __init__(
        self,
        *,
        deep_scan_fn: Callable[[list[str]], Any] | None = None,
        legacy_scan_fn: Callable[[list[str]], Any] | None = None,
    ) -> None:
        self._fallback = OpenCorePreFilter()
        self._deep_scan_fn = deep_scan_fn
        self._legacy_scan_fn = legacy_scan_fn
        self.fast_filter = FastFilter() if RUST_AVAILABLE and FastFilter else None

    def scan(self, data_batch: list[str]) -> Any:
        if self.fast_filter is not None:
            suspect_indices = self.fast_filter.filter_batch(data_batch)
            filtered_data = [
                data_batch[i]
                for i in suspect_indices
                if isinstance(i, int) and 0 <= i < len(data_batch)
            ]
            if self._deep_scan_fn is None:
                return filtered_data
            return self._deep_scan_fn(filtered_data)

        filtered_data = self._fallback.filter_candidates(data_batch)
        if self._legacy_scan_fn is None:
            return filtered_data
        return self._legacy_scan_fn(filtered_data)


def process_chunk_worker(chunk: Sequence[str]) -> list[str]:
    """
    Process worker entrypoint for ``ProcessPoolExecutor``.

    The Rust filter is lazily initialized inside each child process.
    """
    global _worker_filter_instance

    data_batch = [str(item) for item in chunk]
    if _worker_filter_instance is None and RUST_AVAILABLE and FastFilter is not None:
        _worker_filter_instance = FastFilter()

    if _worker_filter_instance is not None:
        suspect_indices = _worker_filter_instance.filter_batch(data_batch)
        suspects = [
            data_batch[i]
            for i in suspect_indices
            if isinstance(i, int) and 0 <= i < len(data_batch)
        ]
        return deep_ml_analysis(suspects)

    return deep_ml_analysis(basic_python_scan(data_batch))


def deep_ml_analysis(suspects: list[str]) -> list[str]:
    """
    Placeholder for heavier ML/DL stage in Pro+.

    Current implementation keeps candidates unchanged to preserve compatibility.
    """
    return suspects
