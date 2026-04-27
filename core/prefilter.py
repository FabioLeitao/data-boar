"""
Pre-filter contract and Open Core implementation.

Goal: reduce candidate payloads before expensive validation/ML without changing
the downstream raw findings contract.

Performance posture (Slice 2 doctrine, see ``THE_ART_OF_THE_FALLBACK.md`` and
``DEFENSIVE_SCANNING_MANIFESTO.md``): the regex-shape candidate gate is a hot
path on every batch in both OpenCore and Pro. We fuse CPF and e-mail into one
compiled alternation so each row pays a single ``re.search`` call instead of
two — same finding contract, half the bytecode dispatch.
"""

from __future__ import annotations

import re
from typing import Protocol, runtime_checkable

# Kept exported for backward-compat (other modules and tests may import these
# names; the fused pattern below is what the hot path uses).
_CPF_CANDIDATE_RX = re.compile(r"\d{3}\D?\d{3}\D?\d{3}\D?\d{2}")
_EMAIL_CANDIDATE_RX = re.compile(r"[^\s@]+@[^\s@]+\.[^\s@]+")

# Fused candidate alternation: ONE compiled regex, ONE search per row.
# The order is "cheaper anchor first" (CPF is purely numeric; e-mail needs the
# @ scan). Behavior is identical to the OR of the two individual patterns.
_OPENCORE_CANDIDATE_RX = re.compile(
    r"\d{3}\D?\d{3}\D?\d{3}\D?\d{2}|[^\s@]+@[^\s@]+\.[^\s@]+"
)


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

    # Bind the compiled regex's ``search`` to a local attribute so the hot loop
    # avoids attribute lookups per row (small but free win on 100k+ batches).
    _search = staticmethod(_OPENCORE_CANDIDATE_RX.search)

    def filter_candidates(self, payloads: list[str]) -> list[str]:
        # List comprehension + bound local search is measurably faster than the
        # explicit ``for ... if ... append`` loop on CPython for hot paths.
        search = self._search
        return [item for item in payloads if item and search(item)]

    @staticmethod
    def _looks_sensitive(value: str) -> bool:
        if not value:
            return False
        return bool(_OPENCORE_CANDIDATE_RX.search(value))
