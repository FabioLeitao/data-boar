"""Structural regression guard for ``docs/ops/AUDIT_PROTOCOL.md``.

The audit protocol registry encodes three contracts (Adam Savage Bench /
Registry / Integrity Warning) demanded by the operator on 2026-04-28
(see Slack trigger ``1777382881.844609``).

This test does **not** police the *content* of changelog rows — that is the
human reviewer's job. It only ensures the file (and its pt-BR mirror)
remain present and well-formed so that future PRs cannot silently delete
the registry. Anti-pattern protection is the explicit purpose of the
manifesto in ``docs/ops/inspirations/THE_ART_OF_THE_FALLBACK.md`` §3
("Diagnostic on fall — never fall through silently").
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest


def _project_root() -> Path:
    return Path(__file__).resolve().parent.parent


_REQUIRED_SECTIONS_EN = (
    "## 1. The three contracts",
    "### Contract 1 — Bench discipline",
    "### Contract 2 — Ritual / contract changes are registered here",
    "### Contract 3 — Integrity Warning",
    "## 3. Changelog",
)

_REQUIRED_SECTIONS_PT = (
    "## 1. Os três contratos",
    "### Contrato 1 — Disciplina de bancada",
    "### Contrato 2 — Mudanças de ritual",
    "### Contrato 3 — Warning de Integridade",
    "## 3. Changelog",
)


def _audit_doc_en() -> Path:
    return _project_root() / "docs" / "ops" / "AUDIT_PROTOCOL.md"


def _audit_doc_pt() -> Path:
    return _project_root() / "docs" / "ops" / "AUDIT_PROTOCOL.pt_BR.md"


def test_audit_protocol_en_exists():
    """Canonical EN registry MUST exist."""
    assert _audit_doc_en().is_file(), (
        "docs/ops/AUDIT_PROTOCOL.md is missing — operator directive 2026-04-28 requires it."
    )


def test_audit_protocol_pt_br_exists():
    """pt-BR mirror MUST exist (docs-policy: EN + pt-BR pair for ops)."""
    assert _audit_doc_pt().is_file(), (
        "docs/ops/AUDIT_PROTOCOL.pt_BR.md missing — pair the EN canonical mirror."
    )


@pytest.mark.parametrize("required", _REQUIRED_SECTIONS_EN)
def test_audit_protocol_en_has_required_sections(required: str):
    """Each canonical section heading MUST appear verbatim."""
    text = _audit_doc_en().read_text(encoding="utf-8")
    assert required in text, (
        f"Missing required heading prefix in AUDIT_PROTOCOL.md: {required!r}"
    )


@pytest.mark.parametrize("required", _REQUIRED_SECTIONS_PT)
def test_audit_protocol_pt_br_has_required_sections(required: str):
    """Each canonical pt-BR section heading MUST appear verbatim."""
    text = _audit_doc_pt().read_text(encoding="utf-8")
    assert required in text, (
        f"Missing required heading prefix in AUDIT_PROTOCOL.pt_BR.md: {required!r}"
    )


def test_audit_protocol_changelog_table_has_at_least_one_row():
    """Changelog table MUST contain the seed row (2026-04-28-01)."""
    text = _audit_doc_en().read_text(encoding="utf-8")
    assert "2026-04-28-01" in text, (
        "Seed changelog row 2026-04-28-01 is required — see operator directive 2026-04-28."
    )


def test_audit_protocol_changelog_row_id_format():
    """Every changelog ID MUST follow YYYY-MM-DD-NN to keep the registry sortable."""
    text = _audit_doc_en().read_text(encoding="utf-8")
    pattern = re.compile(r"\b(\d{4}-\d{2}-\d{2}-\d{2})\b")
    ids = pattern.findall(text)
    assert ids, (
        "AUDIT_PROTOCOL.md must contain at least one well-formed YYYY-MM-DD-NN row id."
    )
    for row_id in ids:
        assert re.fullmatch(r"\d{4}-\d{2}-\d{2}-\d{2}", row_id), (
            f"Malformed changelog row id: {row_id!r} (expected YYYY-MM-DD-NN)"
        )


def test_audit_protocol_pair_locale_link():
    """Each side MUST link to its sibling so navigation never dead-ends."""
    en = _audit_doc_en().read_text(encoding="utf-8")
    pt = _audit_doc_pt().read_text(encoding="utf-8")
    assert "AUDIT_PROTOCOL.pt_BR.md" in en, (
        "EN doc must link to pt-BR sibling (docs-policy navigation rule)."
    )
    assert "AUDIT_PROTOCOL.md" in pt, (
        "pt-BR doc must link to EN canonical sibling (docs-policy navigation rule)."
    )
