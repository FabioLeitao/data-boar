"""
Process worker helpers for Pro+ discovery orchestration.

This module is intentionally top-level and stateless-friendly so functions are
picklable by ``ProcessPoolExecutor``.
"""

from __future__ import annotations

from collections.abc import Sequence
from typing import Any

from core.luhn import string_contains_luhn_valid_card
from core.prefilter import OpenCorePreFilter

try:
    from boar_fast_filter import FastFilter

    HAS_RUST = True
except Exception:
    FastFilter = None  # type: ignore[assignment]
    HAS_RUST = False

_open_core = OpenCorePreFilter()
_filter_instance: Any = None


def process_chunk_pro(chunk: Sequence[Any]) -> list[str]:
    """
    Process one chunk in a worker process.

    - Pro path: Rust pre-filter (CPF/email/card+Luhn).
    - Open Core path: Python fallback candidate scan.
    """
    global _filter_instance
    data_strings = [str(row) for row in chunk]

    if HAS_RUST and _filter_instance is None and FastFilter is not None:
        _filter_instance = FastFilter()

    if HAS_RUST and _filter_instance is not None:
        suspect_indices = _filter_instance.filter_batch(data_strings)
        return [
            data_strings[i]
            for i in suspect_indices
            if isinstance(i, int) and 0 <= i < len(data_strings)
        ]

    return basic_python_scan(data_strings)


def basic_python_scan(payloads: list[str]) -> list[str]:
    """
    Open Core fallback that keeps CPF/email candidates plus Luhn-valid cards.

    The Luhn step is delegated to ``core.luhn.string_contains_luhn_valid_card``
    so the Open Core fallback, the Pro Rust filter, and the high-confidence
    detector path agree on what "valid card shape + check digit" means.
    """
    candidates = _open_core.filter_candidates(payloads)
    out = list(candidates)
    known = set(candidates)
    for value in payloads:
        if value in known:
            continue
        if string_contains_luhn_valid_card(value):
            out.append(value)
    return out
