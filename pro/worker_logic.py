"""
Process worker helpers for Pro+ discovery orchestration.

This module is intentionally top-level and stateless-friendly so functions are
picklable by ``ProcessPoolExecutor``.

Performance posture (Slice 2 — Savage / NASA / Gibson):

The original Python fallback ran the OpenCore CPF+email regex over every row,
**then** ran the card-shape regex over every row that did *not* match — i.e.
two full passes over the batch. On a 200k synthetic seed where 50 percent of
rows are misses, that doubled the regex work for the Pro path vs OpenCore and
showed up as the ``0.574x`` regression in the official 200k benchmark.

The new ``basic_python_scan`` does a **single fused pass** per row:

1. One ``re.search`` against the fused alternation (CPF | e-mail | card-shape).
2. Only rows whose match span looks like a card-shape pay the Luhn arithmetic.

Same finding contract (CPF / e-mail / Luhn-valid card), zero database locks
(this is in-memory pre-filter), and no change to the audit log shape.
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

# Card-shape pattern kept exported for tests / external callers.
_CARD_PATTERN = re.compile(r"\b(?:\d[ -]?){13,19}\b")

# Fused single-pass alternation used by the Python fallback worker.
# Group ``card`` is named so we can detect a card-shape hit without re-running
# the regex; CPF and e-mail short-circuit immediately as accepted candidates.
_FUSED_PRO_RX = re.compile(
    r"(?P<cpf>\d{3}\D?\d{3}\D?\d{3}\D?\d{2})"
    r"|(?P<email>[^\s@]+@[^\s@]+\.[^\s@]+)"
    r"|(?P<card>\b(?:\d[ -]?){13,19}\b)"
)

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

    Single fused pass: each payload is scanned **once** against
    ``_FUSED_PRO_RX``. CPF and e-mail matches are accepted immediately; card
    shapes only trigger the Luhn arithmetic (``_check_luhn``) when the regex
    actually finds a card-length digit run, which is the rare case in real
    customer data and in the seeded 200k benchmark.
    """
    out: list[str] = []
    out_append = out.append
    fused_search = _FUSED_PRO_RX.search
    fused_finditer = _FUSED_PRO_RX.finditer

    for value in payloads:
        if not value:
            continue
        match = fused_search(value)
        if match is None:
            continue
        last_group = match.lastgroup
        if last_group != "card":
            # CPF or e-mail short-circuit: cheapest accept path.
            out_append(value)
            continue
        # Card-shape first: pay Luhn only when needed. Defensive fallback —
        # a row may carry several card-shape spans plus a CPF/e-mail later;
        # walk the string once with ``finditer`` to handle that without
        # re-scanning from scratch.
        accepted = False
        for hit in fused_finditer(value):
            group = hit.lastgroup
            if group == "card":
                if _check_luhn(hit.group(0)):
                    accepted = True
                    break
                continue
            accepted = True
            break
        if accepted:
            out_append(value)
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
