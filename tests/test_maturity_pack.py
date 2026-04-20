"""Maturity assessment YAML pack loader (architecture A)."""

from __future__ import annotations

from pathlib import Path

import pytest

from core.maturity_assessment.pack import load_maturity_pack


def test_load_sample_pack():
    p = (
        Path(__file__).resolve().parent
        / "fixtures"
        / "maturity_assessment"
        / "sample_pack.yaml"
    )
    pack = load_maturity_pack(p)
    assert pack.version == 1
    assert len(pack.sections) == 1
    assert pack.sections[0].id == "governance"
    assert len(pack.sections[0].questions) == 2


def test_load_pack_rejects_empty_sections(tmp_path):
    bad = tmp_path / "bad.yaml"
    bad.write_text("version: 1\nsections: []\n", encoding="utf-8")
    with pytest.raises(ValueError, match="no valid sections"):
        load_maturity_pack(bad)
