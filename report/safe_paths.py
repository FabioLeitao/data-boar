"""
Safe filesystem path construction for report artifacts (heatmap PNG, Excel, manifests).

CodeQL flags ``Path(output_dir) / f"...{user_supplied}.png"`` as *Uncontrolled data
used in path expression* even when ``session_id`` was previously normalized via
:mod:`report.safe_prefix`, because the dataflow analyzer cannot prove that the
sanitizer eliminates traversal/absolute-path inputs *and* that the join stays
under ``output_dir``.

This module collapses both concerns into a single funnel:

* ``output_dir`` is resolved to an absolute :class:`~pathlib.Path` (the *base*).
* The leaf filename is matched against a strict ``[A-Za-z0-9_.-]`` allowlist
  (no path separators, no ``..``, no NUL).
* The joined target is resolved and re-checked with :meth:`Path.is_relative_to`.

Anything that fails returns ``None`` so callers can fall back to a no-op
(skip embed, skip write) instead of touching disk with attacker-influenced data.
"""

from __future__ import annotations

import re
from pathlib import Path

_SAFE_FILENAME_RE = re.compile(r"^[A-Za-z0-9_.-]+$")


def _resolve_base(output_dir: str | Path) -> Path | None:
    try:
        base = Path(output_dir).expanduser().resolve()
    except (OSError, RuntimeError):
        return None
    if not base.is_dir():
        return None
    return base


def _is_safe_leaf(filename: str) -> bool:
    """Return True only for plain basenames (no separators, no traversal)."""
    if not filename or filename in (".", ".."):
        return False
    if "/" in filename or "\\" in filename or "\x00" in filename:
        return False
    if not _SAFE_FILENAME_RE.fullmatch(filename):
        return False
    return True


def get_safe_report_path(output_dir: str | Path, filename: str) -> Path | None:
    """
    Build an absolute :class:`~pathlib.Path` under ``output_dir`` for ``filename``.

    Both arguments are validated:

    * ``output_dir`` must resolve to an existing directory.
    * ``filename`` must match the strict basename allowlist
      (``^[A-Za-z0-9_.-]+$``); this rejects path separators, ``..`` segments,
      NUL bytes, and absolute paths regardless of platform.

    The joined path is resolved and re-checked with :meth:`Path.is_relative_to`
    before being returned, so symlink chicanery inside ``output_dir`` cannot
    escape the base. Returns ``None`` when any check fails — callers MUST treat
    ``None`` as "do not write / do not embed".
    """
    base = _resolve_base(output_dir)
    if base is None:
        return None
    if not _is_safe_leaf(filename):
        return None
    try:
        candidate = (base / filename).resolve()
    except (OSError, RuntimeError):
        return None
    if not candidate.is_relative_to(base):
        return None
    return candidate


def existing_safe_report_path(
    output_dir: str | Path, candidate_path: str | Path
) -> Path | None:
    """
    Validate that an existing file path lies under ``output_dir`` and is a file.

    Used for *read-back* after a writer produced a path: confirms containment
    before openpyxl embeds the PNG inside the spreadsheet (defense-in-depth
    against a downstream caller that might forge ``heatmap_path``).
    """
    base = _resolve_base(output_dir)
    if base is None:
        return None
    try:
        candidate = Path(candidate_path).resolve()
    except (OSError, RuntimeError):
        return None
    if not candidate.is_relative_to(base) or not candidate.is_file():
        return None
    return candidate


__all__ = ["existing_safe_report_path", "get_safe_report_path"]
