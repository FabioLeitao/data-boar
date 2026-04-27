"""
Luhn (modulo-10) checksum helper.

Why does this module exist? A 16-digit run of digits looks like a credit card
to a regex, but most random 16-digit runs are **not** valid card numbers.
The Luhn algorithm catches almost all single-digit typos and most
adjacent-digit transpositions, which means we can use it as a cheap, **algorithmic**
post-filter on top of the credit-card shape regex to reduce false positives
without paying for ML.

This is the same idea ``core.brazilian_cpf.cpf_checksum_valid`` applies to CPF
(modulo-11). Both helpers exist so the detector can confirm that "shape match"
becomes "shape match + check digit holds", i.e. high-confidence PII.

The contract is intentionally tiny and side-effect free so it stays
picklable and importable from the Pro+ worker pool
(``pro.worker_logic.basic_python_scan``) and the Open Core detector
(``core.detector.SensitivityDetector``).

References
----------
- Luhn, H. P. (1960). U.S. Patent 2,950,048 — *Computer for verifying numbers*.
- ISO/IEC 7812-1 (Identification cards — Identification of issuers).
- Defensive scanning manifesto: ``docs/ops/inspirations/DEFENSIVE_SCANNING_MANIFESTO.md``.
"""

from __future__ import annotations

import re

# Card-shape candidate. Aligned with the shape used by
# ``pro.worker_logic._CARD_PATTERN`` and ``rust/boar_fast_filter`` so all three
# scan paths agree on what "looks like a card number" means before checksum.
_CARD_CANDIDATE_RX = re.compile(r"\b(?:\d[ -]?){13,19}\b")


def luhn_check_digits(digits: str) -> bool:
    """
    Return ``True`` if ``digits`` (a string of decimal digits, 13..19 long)
    passes the Luhn (mod-10) checksum.

    Steps (the version every payments engineer can read):

    1. From the rightmost digit moving left, double **every second digit**.
    2. If a doubled value is greater than 9, subtract 9 (equivalent to summing
       its decimal digits — both definitions appear in references).
    3. Sum every digit and the (possibly reduced) doubled values.
    4. The number is valid iff the sum is divisible by 10.

    Returns ``False`` for empty strings, non-digit input, or out-of-range
    lengths. Out-of-range lengths matter: ISO/IEC 7812 cards are 13..19 digits;
    a 20-digit run that *happens* to be Luhn-valid is far more likely a
    serial / barcode than a card.
    """
    if not digits:
        return False
    if not digits.isdigit():
        return False
    n = len(digits)
    if n < 13 or n > 19:
        return False
    total = 0
    for idx, ch in enumerate(reversed(digits)):
        d = ord(ch) - 48  # '0' is 48
        if idx % 2 == 1:
            doubled = d * 2
            total += doubled - 9 if doubled > 9 else doubled
        else:
            total += d
    return total % 10 == 0


def luhn_check(value: str) -> bool:
    """
    Convenience: return ``True`` if ``value`` (which may contain spaces or
    dashes, e.g. ``"4111 1111 1111 1111"``) is a Luhn-valid card number once
    non-digit characters are stripped.

    Use ``luhn_check_digits`` directly when the input is already clean digits.
    """
    if not value:
        return False
    digits = "".join(ch for ch in value if ch.isdigit())
    return luhn_check_digits(digits)


def string_contains_luhn_valid_card(text: str) -> bool:
    """
    Return ``True`` if any 13..19-digit run in ``text`` (allowing single
    spaces or hyphens between digits) passes the Luhn check.

    This is the function ``pro.worker_logic`` uses to decide whether an
    Open Core payload survives the candidate filter. It is intentionally
    bounded by the regex ``\\b(?:\\d[ -]?){13,19}\\b`` so we do not spend
    Luhn cycles on arbitrary digit floods.
    """
    if not text:
        return False
    return any(luhn_check(m.group(0)) for m in _CARD_CANDIDATE_RX.finditer(text))


__all__ = [
    "luhn_check_digits",
    "luhn_check",
    "string_contains_luhn_valid_card",
]
