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

    Slice 2 perf note: the previous implementation chained an extra
    ``deep_ml_analysis`` no-op that materialised a second list per chunk and
    paid an extra dispatch on the hottest path of the 200k benchmark. The
    placeholder is now a passthrough handled inline; a real ML/DL stage will
    arrive behind a feature flag (and an ADR) instead of as a phantom hop.
    """
    global _worker_filter_instance

    if _worker_filter_instance is None and RUST_AVAILABLE and FastFilter is not None:
        _worker_filter_instance = FastFilter()

    # Fast path: avoid the extra ``str(item)`` materialisation when the chunk
    # already contains strings (the common case from ``ProOrchestrator``).
    data_batch: list[str] = (
        list(chunk)
        if all(isinstance(item, str) for item in chunk)
        else [str(item) for item in chunk]
    )

    if _worker_filter_instance is not None:
        suspect_indices = _worker_filter_instance.filter_batch(data_batch)
        return [
            data_batch[i]
            for i in suspect_indices
            if isinstance(i, int) and 0 <= i < len(data_batch)
        ]

    return basic_python_scan(data_batch)


def deep_ml_analysis(suspects: list[str]) -> list[str]:
    """
    Placeholder for heavier ML/DL stage in Pro+.

    Kept for backward compatibility with callers that imported the symbol;
    ``process_chunk_worker`` no longer routes through this function on the hot
    path. Returning the suspects unchanged preserves the historical contract.
    """
    return suspects
