"""Unit tests for :mod:`report.safe_paths` (helper used by report writers / embed)."""

from __future__ import annotations

from pathlib import Path

import pytest

from report.safe_paths import existing_safe_report_path, get_safe_report_path


@pytest.fixture
def base_dir(tmp_path: Path) -> Path:
    out = tmp_path / "out"
    out.mkdir()
    return out


# ---------------------------------------------------------------------------
# get_safe_report_path
# ---------------------------------------------------------------------------


def test_get_safe_report_path_accepts_simple_basename(base_dir: Path) -> None:
    target = get_safe_report_path(base_dir, "heatmap_abc.png")
    assert target is not None
    assert target == (base_dir / "heatmap_abc.png").resolve()
    assert target.is_relative_to(base_dir.resolve())


def test_get_safe_report_path_accepts_xlsx(base_dir: Path) -> None:
    target = get_safe_report_path(base_dir, "Relatorio_Auditoria_abc123.xlsx")
    assert target is not None
    assert target.parent == base_dir.resolve()


@pytest.mark.parametrize(
    "bad",
    [
        "../escape.png",
        "..",
        ".",
        "sub/heatmap.png",
        "sub\\heatmap.png",
        "/abs/heatmap.png",
        "C:/abs/heatmap.png",
        "heat\x00map.png",
        "heat map.png",  # space not in allowlist
        "heat$map.png",  # symbol not in allowlist
        "",
    ],
)
def test_get_safe_report_path_rejects_unsafe_filenames(
    base_dir: Path, bad: str
) -> None:
    assert get_safe_report_path(base_dir, bad) is None


def test_get_safe_report_path_rejects_missing_output_dir(tmp_path: Path) -> None:
    missing = tmp_path / "does_not_exist"
    assert get_safe_report_path(missing, "heatmap.png") is None


def test_get_safe_report_path_rejects_file_as_base(tmp_path: Path) -> None:
    f = tmp_path / "regular.txt"
    f.write_text("x", encoding="utf-8")
    assert get_safe_report_path(f, "heatmap.png") is None


def test_get_safe_report_path_join_stays_under_base(base_dir: Path) -> None:
    """Even a 'safe' leaf must resolve back inside base_dir (defense in depth)."""
    target = get_safe_report_path(base_dir, "heatmap.png")
    assert target is not None
    base_resolved = base_dir.resolve()
    assert str(target).startswith(str(base_resolved))


# ---------------------------------------------------------------------------
# existing_safe_report_path
# ---------------------------------------------------------------------------


def test_existing_safe_report_path_accepts_file_inside_base(base_dir: Path) -> None:
    f = base_dir / "heatmap.png"
    f.write_bytes(b"png")
    assert existing_safe_report_path(base_dir, f) == f.resolve()


def test_existing_safe_report_path_rejects_file_outside_base(
    tmp_path: Path, base_dir: Path
) -> None:
    outside = tmp_path / "outside.png"
    outside.write_bytes(b"png")
    assert existing_safe_report_path(base_dir, outside) is None


def test_existing_safe_report_path_rejects_directory(base_dir: Path) -> None:
    sub = base_dir / "sub"
    sub.mkdir()
    assert existing_safe_report_path(base_dir, sub) is None


def test_existing_safe_report_path_rejects_traversal_string(base_dir: Path) -> None:
    bogus = str(base_dir / ".." / "etc" / "passwd")
    assert existing_safe_report_path(base_dir, bogus) is None


def test_existing_safe_report_path_rejects_missing_file(base_dir: Path) -> None:
    assert existing_safe_report_path(base_dir, base_dir / "nope.png") is None
