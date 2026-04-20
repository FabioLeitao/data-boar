"""Regression: runtime version string matches pyproject.toml (single source of truth)."""

from __future__ import annotations

import re
import tomllib
from pathlib import Path

import pytest


def _project_version_from_pyproject() -> str:
    root = Path(__file__).resolve().parent.parent
    with (root / "pyproject.toml").open("rb") as f:
        data = tomllib.load(f)
    return str(data["project"]["version"])


def _fallback_version_in_about_source() -> str:
    """String used when importlib.metadata has no distribution (see docs/VERSIONING.md)."""
    root = Path(__file__).resolve().parent.parent
    text = (root / "core" / "about.py").read_text(encoding="utf-8")
    m = re.search(r"except Exception:\s*\n\s*ver = \"([^\"]+)\"", text)
    assert m is not None, (
        'expected fallback `ver = "..."` after `except Exception:` in core/about.py'
    )
    return m.group(1)


def test_about_version_matches_pyproject() -> None:
    """Installed/metadata path must agree with repo `version =` (see docs/VERSIONING.md)."""
    from core.about import get_about_info

    expected = _project_version_from_pyproject()
    assert get_about_info()["version"] == expected


def test_about_fallback_string_matches_pyproject() -> None:
    """Bump checklist: `core/about.py` except-branch must track `pyproject.toml`."""
    assert _fallback_version_in_about_source() == _project_version_from_pyproject()


@pytest.mark.parametrize(
    "path,label",
    [
        ("docs/data_boar.1", "man section 1"),
        ("docs/data_boar.5", "man section 5"),
    ],
)
def test_man_th_line_contains_project_version(path: str, label: str) -> None:
    """`.TH` fourth argument includes the marketing version (e.g. Data Boar 1.7.1)."""
    root = Path(__file__).resolve().parent.parent
    ver = _project_version_from_pyproject()
    text = (root / path).read_text(encoding="utf-8")
    first = next((ln for ln in text.splitlines() if ln.startswith(".TH")), "")
    assert ver in first, f"{label}: expected {ver!r} in {first!r}"
