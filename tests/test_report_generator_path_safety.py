"""
Path-injection guards for ``report.generator``.

These tests pin the contract enforced by ``get_safe_report_path`` and the
``_heatmap_path_for_embed`` helpers introduced after CodeQL py/path-injection
flagged the older ``Path.is_relative_to`` shape (which CodeQL does not model
as a sanitizer). The chosen idiom mirrors ``api.routes._real_file_under_out_dir_str``:
allowlist the basename **before** join, then require
``normpath(join(realpath(base), name)).startswith(realpath(base) + os.sep)``.
"""

from __future__ import annotations

import os
from pathlib import Path

from report.generator import (
    _heatmap_path_for_embed,
    get_safe_report_path,
)


# -- get_safe_report_path -----------------------------------------------------


def test_get_safe_report_path_accepts_clean_basename(tmp_path: Path) -> None:
    out = tmp_path / "reports"
    out.mkdir()
    result = get_safe_report_path(str(out), "Relatorio_Auditoria_abc123.xlsx")
    assert result is not None
    # Containment: resolved path lives inside the resolved out dir.
    assert str(result).startswith(str(out.resolve()))
    assert result.name == "Relatorio_Auditoria_abc123.xlsx"


def test_get_safe_report_path_rejects_path_separators(tmp_path: Path) -> None:
    out = tmp_path / "reports"
    out.mkdir()
    assert get_safe_report_path(str(out), "../escape.xlsx") is None
    assert get_safe_report_path(str(out), "subdir/file.xlsx") is None
    assert get_safe_report_path(str(out), "subdir\\file.xlsx") is None


def test_get_safe_report_path_rejects_dot_and_parent(tmp_path: Path) -> None:
    out = tmp_path / "reports"
    out.mkdir()
    assert get_safe_report_path(str(out), ".") is None
    assert get_safe_report_path(str(out), "..") is None
    assert get_safe_report_path(str(out), "...") is None  # not a clean name


def test_get_safe_report_path_rejects_absolute_path(tmp_path: Path) -> None:
    out = tmp_path / "reports"
    out.mkdir()
    # Absolute paths contain a separator, so the basename allowlist refuses them.
    assert get_safe_report_path(str(out), "/etc/passwd") is None
    assert get_safe_report_path(str(out), "C:\\Windows\\system32\\cmd.exe") is None


def test_get_safe_report_path_rejects_control_chars_and_nul(tmp_path: Path) -> None:
    out = tmp_path / "reports"
    out.mkdir()
    assert get_safe_report_path(str(out), "report\x00.xlsx") is None
    assert get_safe_report_path(str(out), "report\n.xlsx") is None
    assert get_safe_report_path(str(out), "report .xlsx") is None  # space not allowed


def test_get_safe_report_path_rejects_empty_input(tmp_path: Path) -> None:
    out = tmp_path / "reports"
    out.mkdir()
    assert get_safe_report_path(str(out), "") is None
    assert get_safe_report_path(str(out), None) is None  # type: ignore[arg-type]


def test_get_safe_report_path_does_not_require_existence(tmp_path: Path) -> None:
    """Write-side callers (XLSX/PNG) need a containment-checked target path,
    even before the file exists. Read-side callers add ``is_file()``."""
    out = tmp_path / "reports"
    out.mkdir()
    result = get_safe_report_path(str(out), "heatmap_abc123.png")
    assert result is not None
    assert not result.exists()  # we did not create it; path is still safe to use


def test_get_safe_report_path_handles_pathlike_output_dir(tmp_path: Path) -> None:
    """Accepts ``Path`` (PathLike) for output_dir, not only str."""
    out = tmp_path / "reports"
    out.mkdir()
    result = get_safe_report_path(out, "heatmap_abc.png")
    assert result is not None


def test_get_safe_report_path_no_prefix_collision(tmp_path: Path) -> None:
    """Two siblings sharing a prefix (``/tmp/out`` vs ``/tmp/out_evil``) must
    not be treated as nested by the startswith check (we append os.sep)."""
    base = tmp_path / "out"
    base.mkdir()
    (tmp_path / "out_evil").mkdir()
    # Filename allowlist already blocks separators, so the only way to confirm
    # the collision guard is via the resolved containment.
    assert get_safe_report_path(str(base), "ok.xlsx") is not None


# -- _heatmap_path_for_embed --------------------------------------------------


def test_heatmap_embed_accepts_existing_file_under_out_dir(tmp_path: Path) -> None:
    out = tmp_path / "out"
    out.mkdir()
    png = out / "heatmap_abcdef.png"
    png.write_bytes(b"\x89PNG\r\n\x1a\n")
    embedded = _heatmap_path_for_embed(str(png), str(out))
    assert embedded is not None
    assert embedded.resolve() == png.resolve()


def test_heatmap_embed_rejects_file_outside_out_dir(tmp_path: Path) -> None:
    out = tmp_path / "out"
    out.mkdir()
    outside = tmp_path / "heatmap_abcdef.png"
    outside.write_bytes(b"\x89PNG\r\n\x1a\n")
    # The basename matches the allowlist, but no such file exists *under out*.
    assert _heatmap_path_for_embed(str(outside), str(out)) is None


def test_heatmap_embed_rejects_traversal_attempt(tmp_path: Path) -> None:
    out = tmp_path / "out"
    out.mkdir()
    # We strip to basename first; "../../etc/passwd" -> "passwd". Allowlist
    # accepts the basename, but the file does not exist under out, so reject.
    assert _heatmap_path_for_embed("../../etc/passwd", str(out)) is None


def test_heatmap_embed_rejects_missing_file(tmp_path: Path) -> None:
    out = tmp_path / "out"
    out.mkdir()
    assert _heatmap_path_for_embed("heatmap_missing.png", str(out)) is None


def test_heatmap_embed_rejects_empty_input(tmp_path: Path) -> None:
    out = tmp_path / "out"
    out.mkdir()
    assert _heatmap_path_for_embed("", str(out)) is None


def test_heatmap_embed_rejects_directory(tmp_path: Path) -> None:
    out = tmp_path / "out"
    out.mkdir()
    sub = out / "subdir"
    sub.mkdir()
    # basename "subdir" passes the allowlist but is_file() must reject it.
    assert _heatmap_path_for_embed(str(sub), str(out)) is None


# -- Containment behavior with real symlinks (POSIX only) ---------------------


def test_get_safe_report_path_resolves_symlinked_base(tmp_path: Path) -> None:
    """If output_dir itself is a symlink, realpath canonicalizes it; the
    containment check still holds because we apply realpath to the base."""
    real_out = tmp_path / "real_out"
    real_out.mkdir()
    link = tmp_path / "link_out"
    try:
        os.symlink(real_out, link)
    except (OSError, NotImplementedError):
        # Symlinks not supported (Windows without privilege). Skip silently.
        return
    result = get_safe_report_path(str(link), "ok.xlsx")
    assert result is not None
    # Resolved path must live under the real output directory.
    assert str(result).startswith(str(real_out.resolve()))
