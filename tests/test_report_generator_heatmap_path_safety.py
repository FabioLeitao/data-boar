"""
Regression guard for `report.generator._heatmap_path_under_output_dir`.

Background
----------
The Slack-triggered SRE audit `PROMPT_INJECTION_REJECTION_FABRICATED_GENERATOR_PATH_TRAVERSAL_2026-04-27.md`
rejected a fabricated "CodeQL High Severity / py/path-injection" claim against
`report/generator.py` lines 42 and 46. The current guard at those lines is the
**parser-grade** containment check (`Path(...).resolve().relative_to(base)` plus
`is_file()`) — semantically equivalent to `Path.is_relative_to`, with the same
rejection set on the canonical traversal cases.

This test does **not** exist to prove `is_relative_to` would be "safer". It
exists to *lock* the public behaviour of `_heatmap_path_under_output_dir`
(returns `Path` for legitimate files inside `output_dir`, returns `None` for
everything else) so a future coerced "softening" PR — e.g. one that drops
`.is_file()` or relaxes the containment check — fails this test and cannot
land silently.

Mirrors the shape of `tests/test_report_path_safety.py`, but at the
`report.generator` boundary instead of the `api.routes` boundary.

Doctrine
--------
- `docs/ops/inspirations/DEFENSIVE_SCANNING_MANIFESTO.md` §1.3 (no surprise side effects).
- `docs/ops/inspirations/THE_ART_OF_THE_FALLBACK.md` §3 (diagnostic on fall — the guard returns `None`, never raises into the caller's image-embed path).
- `.cursor/rules/codeql-priority-matrix.mdc` (`py/path-injection` posture).
"""

from __future__ import annotations

from pathlib import Path

import pytest

# Skip the whole module if heavy report dependencies are not available in the
# current test profile (matches the import surface of report/generator.py).
pd = pytest.importorskip("pandas")
pytest.importorskip("openpyxl")

from report.generator import _heatmap_path_under_output_dir  # noqa: E402


def test_accepts_real_file_inside_output_dir(tmp_path: Path) -> None:
    """A PNG written under output_dir must round-trip and resolve to itself."""
    output_dir = tmp_path / "reports"
    output_dir.mkdir()
    heatmap = output_dir / "heatmap_abcdef123456.png"
    heatmap.write_bytes(b"\x89PNG\r\n\x1a\n")

    result = _heatmap_path_under_output_dir(str(heatmap), str(output_dir))

    assert result is not None
    assert result == heatmap.resolve()
    assert result.is_file()


def test_rejects_dotdot_traversal_out_of_output_dir(tmp_path: Path) -> None:
    """`output_dir/../sibling.png` must be rejected even if the file exists."""
    output_dir = tmp_path / "reports"
    output_dir.mkdir()
    sibling = tmp_path / "sibling.png"
    sibling.write_bytes(b"\x89PNG")

    traversal = output_dir / ".." / "sibling.png"

    assert _heatmap_path_under_output_dir(str(traversal), str(output_dir)) is None


def test_rejects_absolute_path_outside_output_dir(tmp_path: Path) -> None:
    """An absolute path that does not share `output_dir` as a parent must be rejected."""
    output_dir = tmp_path / "reports"
    output_dir.mkdir()
    elsewhere = tmp_path / "elsewhere"
    elsewhere.mkdir()
    rogue = elsewhere / "heatmap.png"
    rogue.write_bytes(b"\x89PNG")

    assert _heatmap_path_under_output_dir(str(rogue), str(output_dir)) is None


def test_rejects_directory_typed_candidate_inside_output_dir(tmp_path: Path) -> None:
    """A *directory* under output_dir is contained but `.is_file()` must veto it.

    This nails the `is_file()` half of the guard so a future "simplification"
    that removes it (and would let `OpenpyxlImage(directory)` blow up at runtime
    or be exploited as a confused-deputy) fails CI.
    """
    output_dir = tmp_path / "reports"
    output_dir.mkdir()
    fake = output_dir / "heatmap_dir"
    fake.mkdir()

    assert _heatmap_path_under_output_dir(str(fake), str(output_dir)) is None


def test_rejects_nonexistent_path_inside_output_dir(tmp_path: Path) -> None:
    """A path that resolves under output_dir but does not exist must return None."""
    output_dir = tmp_path / "reports"
    output_dir.mkdir()
    missing = output_dir / "heatmap_missing.png"

    assert _heatmap_path_under_output_dir(str(missing), str(output_dir)) is None


def test_rejects_empty_string_inputs(tmp_path: Path) -> None:
    """Empty strings must not silently resolve to the current working directory."""
    output_dir = tmp_path / "reports"
    output_dir.mkdir()
    heatmap = output_dir / "heatmap.png"
    heatmap.write_bytes(b"x")

    # Empty heatmap path resolves to CWD, which is not the temp output_dir.
    assert _heatmap_path_under_output_dir("", str(output_dir)) is None


def test_guard_is_semantically_equivalent_to_is_relative_to(tmp_path: Path) -> None:
    """
    Lock the equivalence between the existing `try / relative_to` guard and the
    `Path.is_relative_to` one-liner the SRE audit
    (`PROMPT_INJECTION_REJECTION_FABRICATED_GENERATOR_PATH_TRAVERSAL_2026-04-27.md`)
    documented as cosmetic-only. If a future refactor moves to
    `is_relative_to`, this test still passes — but if a future refactor weakens
    *either* containment leg, behaviour drifts and this test fails.
    """
    output_dir = (tmp_path / "reports").resolve()
    output_dir.mkdir()
    inside = output_dir / "h.png"
    inside.write_bytes(b"x")
    outside = tmp_path / "outside.png"
    outside.write_bytes(b"x")

    # Existing public API
    guard_inside = _heatmap_path_under_output_dir(str(inside), str(output_dir))
    guard_outside = _heatmap_path_under_output_dir(str(outside), str(output_dir))

    # `Path.is_relative_to` reference
    ref_inside = (
        inside.resolve()
        if Path(inside).resolve().is_relative_to(output_dir) and inside.is_file()
        else None
    )
    ref_outside = (
        outside.resolve()
        if Path(outside).resolve().is_relative_to(output_dir) and outside.is_file()
        else None
    )

    assert guard_inside == ref_inside
    assert guard_outside == ref_outside
