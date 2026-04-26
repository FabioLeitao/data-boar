"""
Brazilian CPF checksum and optional text scan for context-aware PII hints.

``core.detector`` matches CPF *shape* with the built-in ``LGPD_CPF`` regex.
This module adds **Modulo-11** check-digit validation so 11-digit-like tokens
that are **not** valid CPF numbers can be down-ranked or filtered in
post-processing, lab contracts, or future detector phases.

**Sync:** keep ``CPF_SHAPE_PATTERN`` identical to the ``LGPD_CPF`` pattern string
in ``core.detector.DEFAULT_PATTERNS``.
"""

from __future__ import annotations

import re
from typing import Any

CPF_SHAPE_PATTERN = r"\b\d{3}\.?\d{3}\.?\d{3}-?\d{2}\b"
_CPF_RX = re.compile(CPF_SHAPE_PATTERN)


def normalize_cpf_digits(value: str) -> str | None:
    """Return 11 digits only, or None if the string cannot be a CPF payload."""
    if not value:
        return None
    digits = re.sub(r"\D", "", value)
    if len(digits) != 11 or not digits.isdigit():
        return None
    return digits


def cpf_checksum_valid(digits: str) -> bool:
    """
    True if ``digits`` (exactly 11 decimal digits) passes both CPF check digits.

    Rejects known-invalid sequences (all same digit). Does not prove the
    number is *issued* or belongs to a person—only that it satisfies the public
    checksum algorithm used by Receita Federal.
    """
    if len(digits) != 11 or not digits.isdigit():
        return False
    if digits == digits[0] * 11:
        return False

    def _digit(base: str, count: int) -> int:
        total = sum(int(base[i]) * (count + 1 - i) for i in range(count))
        remainder = total % 11
        return 0 if remainder < 2 else 11 - remainder

    if _digit(digits, 9) != int(digits[9]):
        return False
    if _digit(digits, 10) != int(digits[10]):
        return False
    return True


class PIIValidator:
    """Optional validator for CPF shape + checksum over free text or column samples."""

    @staticmethod
    def validate_cpf(cpf: str) -> bool:
        """Return True only when the value is 11 digits and passes both verifiers."""
        normalized = normalize_cpf_digits(cpf)
        if normalized is None:
            return False
        return cpf_checksum_valid(normalized)

    def scan_content(self, text: str) -> dict[str, Any]:
        """
        Find CPF-shaped substrings and keep those that pass ``validate_cpf``.

        Returns structured hits with a coarse ``risk_score`` for reporting demos.
        **Do not** persist raw matched values to public logs—``masked_tail`` exposes
        only the last two digits of the normalized form.
        """
        found: list[dict[str, Any]] = []
        risk_score = 0
        if not text:
            return {"found": found, "risk_score": risk_score}

        for match in _CPF_RX.finditer(text):
            raw = match.group()
            if not self.validate_cpf(raw):
                continue
            digits = normalize_cpf_digits(raw)
            if digits is None:
                continue
            masked_tail = digits[-2:]
            found.append(
                {
                    "type": "BRAZIL_CPF",
                    "masked_tail": masked_tail,
                    "confidence": "HIGH",
                }
            )
            risk_score += 10
        return {"found": found, "risk_score": risk_score}
