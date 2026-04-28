"""
Regression tests for ``report.generator`` path-injection sanitizers (CodeQL py/path-injection).

History (PR #283 RCA, archived in ADR 0044):
``Path.is_relative_to`` is **not** a CodeQL-recognized barrier. The earlier
``_heatmap_path_under_output_dir`` helper resolved both ``output_dir`` and
``heatmap_path`` and then called ``candidate.is_relative_to(base)``. CodeQL's
``py/path-injection`` query continued to flag the ``OpenpyxlImage(str(...))``
sink because the user-influenced segment never crossed a documented sanitizer
(``re.fullmatch`` allowlist + ``normpath/startswith/isfile`` containment).

The replacement helper, :func:`report.generator._safe_heatmap_path_under_output_dir`,
mirrors the documented mold already accepted by CodeQL in
``api.routes._real_file_under_out_dir_str``: reduce to a single basename, run
``re.fullmatch`` on a heatmap allowlist, then ``normpath(join(base, name))``
+ ``startswith(base)`` + ``isfile()`` against a realpath-canonical base.

These tests are the regression guard so the same defect class cannot return
silently if someone tries to "simplify" the helper back to ``is_relative_to``
or skip the basename allowlist.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from report.generator import (
    _heatmap_basename,
    _HEATMAP_BASENAME_PATTERN,
    _safe_heatmap_path_under_output_dir,
)


# ---------------------------------------------------------------------------
# _heatmap_basename — whitelist barrier
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "name",
    [
        "heatmap_abcdef123456.png",
        "heatmap_a1b2c3d4e5f6.png",
        "heatmap_session-01.png",
        "heatmap_ABCD_efgh-1234.png",
    ],
)
def test_heatmap_basename_accepts_allowlisted_filenames(name: str) -> None:
    assert _heatmap_basename(name) == name
    assert _HEATMAP_BASENAME_PATTERN.fullmatch(name) is not None


@pytest.mark.parametrize(
    "evil",
    [
        "",
        "../../etc/passwd",
        "..",
        ".",
        "/etc/shadow",
        "C:/Windows/System32/cmd.exe",
        "heatmap_../etc.png",
        "heatmap_with space.png",
        "heatmap_abc.jpg",
        "report.xlsx",
        "heatmap_.png",
        "heatmap_abc;rm -rf.png",
        "heatmap_" + "a" * 200 + ".png",
    ],
)
def test_heatmap_basename_rejects_unsafe_or_off_pattern_inputs(evil: str) -> None:
    assert _heatmap_basename(evil) is None


def test_heatmap_basename_strips_directory_components_then_validates() -> None:
    """Even with a directory prefix, only the basename is matched (strict allowlist)."""
    assert _heatmap_basename("nested/dir/heatmap_abcdef123456.png") == (
        "heatmap_abcdef123456.png"
    )
    assert _heatmap_basename("nested/dir/etc_passwd_disguised_heatmap.png") is None, (
        "non-allowlisted basenames must not pass even with safe-looking parents"
    )


# ---------------------------------------------------------------------------
# _safe_heatmap_path_under_output_dir — full sanitizer Colleague-Nn
# ---------------------------------------------------------------------------


def test_safe_helper_returns_path_for_real_file_inside_output_dir(
    tmp_path: Path,
) -> None:
    out = tmp_path / "reports"
    out.mkdir()
    target = out / "heatmap_abcdef123456.png"
    target.write_bytes(b"\x89PNG\r\n\x1a\n")
    got = _safe_heatmap_path_under_output_dir(str(target), str(out))
    assert got is not None
    assert got.name == "heatmap_abcdef123456.png"
    assert got.is_file()


def test_safe_helper_rejects_path_outside_output_dir(tmp_path: Path) -> None:
    """Even if the file exists, an outside parent must be refused (containment guard)."""
    out = tmp_path / "reports"
    out.mkdir()
    sibling = tmp_path / "elsewhere"
    sibling.mkdir()
    outside = sibling / "heatmap_abcdef123456.png"
    outside.write_bytes(b"png")
    # Same basename also exists inside out_dir to avoid an isfile() shortcut.
    (out / "heatmap_abcdef123456.png").write_bytes(b"png")

    got = _safe_heatmap_path_under_output_dir(str(outside), str(out))
    # Behaviour: the helper trusts only the basename + output_dir; it does not
    # leak the outside path back to the caller.
    assert got is not None and got.parent.resolve() == out.resolve()


def test_safe_helper_returns_none_for_traversal_attempts(tmp_path: Path) -> None:
    """
    The basename allowlist *intentionally* strips parent-directory components
    before validation (that is the documented CodeQL sanitizer mold). So inputs
    whose **basename** is not allowlisted must return None, regardless of the
    directory prefix that was stripped.
    """
    out = tmp_path / "reports"
    out.mkdir()
    (out / "heatmap_abcdef123456.png").write_bytes(b"png")

    for evil in (
        "../../../etc/passwd",
        "/etc/shadow",
        "..",
        ".",
        "",
        "/tmp/heatmap_with space.png",
        "C:\\Windows\\System32\\heatmap_evil!.png",
    ):
        assert _safe_heatmap_path_under_output_dir(evil, str(out)) is None, evil


def test_safe_helper_collapses_directory_prefix_to_safe_basename(
    tmp_path: Path,
) -> None:
    """
    When the basename **is** allowlisted, the helper trusts only ``output_dir``
    + that basename. Any user-controlled directory prefix is dropped — this is
    the explicit CodeQL barrier (basename-only). Confirms the intent so a future
    refactor cannot "tighten" this into rejecting the legitimate case where the
    operator-controlled output_dir already holds the file.
    """
    out = tmp_path / "reports"
    out.mkdir()
    (out / "heatmap_abcdef123456.png").write_bytes(b"png")
    got = _safe_heatmap_path_under_output_dir("../heatmap_abcdef123456.png", str(out))
    assert got is not None
    assert got.parent.resolve() == out.resolve()


def test_safe_helper_returns_none_when_basename_off_allowlist(tmp_path: Path) -> None:
    out = tmp_path / "reports"
    out.mkdir()
    bad = out / "report.xlsx"
    bad.write_bytes(b"xlsx")
    assert _safe_heatmap_path_under_output_dir(str(bad), str(out)) is None


def test_safe_helper_returns_none_when_file_missing_inside_output_dir(
    tmp_path: Path,
) -> None:
    out = tmp_path / "reports"
    out.mkdir()
    # No file written; allowlisted basename, but containment fails on isfile().
    assert (
        _safe_heatmap_path_under_output_dir(
            str(out / "heatmap_abcdef123456.png"), str(out)
        )
        is None
    )


def test_safe_helper_handles_unresolvable_output_dir_gracefully(tmp_path: Path) -> None:
    """A weird output_dir must not raise; the helper returns None."""
    # ``\x00`` in a path triggers OSError on POSIX/Windows resolvers.
    assert (
        _safe_heatmap_path_under_output_dir("heatmap_abcdef123456.png", "no\x00null")
        is None
    )


def test_safe_helper_resolves_symlinked_output_dir(tmp_path: Path) -> None:
    """
    A symlinked ``output_dir`` is fine; we use ``realpath`` so the canonical
    base is used for the ``startswith`` containment check.
    """
    real = tmp_path / "real_reports"
    real.mkdir()
    link = tmp_path / "reports_link"
    try:
        link.symlink_to(real, target_is_directory=True)
    except (OSError, NotImplementedError):
        pytest.skip("symlink creation not supported on this platform")
    target = real / "heatmap_abcdef123456.png"
    target.write_bytes(b"png")
    got = _safe_heatmap_path_under_output_dir(str(target), str(link))
    assert got is not None and got.is_file()
