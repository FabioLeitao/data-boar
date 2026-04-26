"""
Pre-filter contract and Open Core implementation.

Goal: reduce candidate payloads before expensive validation/ML without changing
the downstream raw findings contract.
"""

from __future__ import annotations

import re
from typing import Protocol, runtime_checkable

_CPF_CANDIDATE_RX = re.compile(r"\d{3}\D?\d{3}\D?\d{3}\D?\d{2}")
_EMAIL_CANDIDATE_RX = re.compile(r"[^\s@]+@[^\s@]+\.[^\s@]+")


@runtime_checkable
class PreFilter(Protocol):
    """Contract used by discovery/scanner layers (Open Core and Pro+)."""

    name: str

    def filter_candidates(self, payloads: list[str]) -> list[str]:
        """Return only strings likely to contain sensitive candidates."""


class OpenCorePreFilter:
    """
    Basic regex-based candidate filter (Open Core baseline).

    Keeps rows that look like CPF-shape or e-mail; all others are dropped before
    deeper validation.
    """

    name = "open_core_regex_prefilter_v1"

    def filter_candidates(self, payloads: list[str]) -> list[str]:
        out: list[str] = []
        for item in payloads:
            if self._looks_sensitive(item):
                out.append(item)
        return out

    @staticmethod
    def _looks_sensitive(value: str) -> bool:
        if not value:
            return False
        return bool(
            _CPF_CANDIDATE_RX.search(value) or _EMAIL_CANDIDATE_RX.search(value)
        )
