"""
Process worker helpers for Pro+ discovery orchestration.

This module is intentionally top-level and stateless-friendly so functions are
picklable by ``ProcessPoolExecutor``.
"""

from __future__ import annotations

import re
from collections.abc import Sequence
from typing import Any

from core.prefilter import OpenCorePreFilter

try:
    from boar_fast_filter import FastFilter

    HAS_RUST = True
except Exception:
    FastFilter = None  # type: ignore[assignment]
    HAS_RUST = False

_CARD_PATTERN = re.compile(r"\b(?:\d[ -]?){13,19}\b")
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
    """
    candidates = _open_core.filter_candidates(payloads)
    out = list(candidates)
    known = set(candidates)
    for value in payloads:
        if value in known:
            continue
        if _contains_luhn_valid_card(value):
            out.append(value)
    return out


def _contains_luhn_valid_card(value: str) -> bool:
    return any(_check_luhn(m.group(0)) for m in _CARD_PATTERN.finditer(value))


def _check_luhn(card_number: str) -> bool:
    digits = [int(ch) for ch in card_number if ch.isdigit()]
    if len(digits) < 13 or len(digits) > 19:
        return False
    total = 0
    for idx, digit in enumerate(reversed(digits)):
        if idx % 2 == 1:
            doubled = digit * 2
            total += doubled - 9 if doubled > 9 else doubled
        else:
            total += digit
    return total % 10 == 0
