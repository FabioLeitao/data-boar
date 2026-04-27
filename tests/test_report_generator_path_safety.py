"""
Path-traversal / jail-containment tests for ``report.generator``.

Targets the CodeQL ``py/path-injection`` finding on the *write* sinks that build
the heatmap PNG and Excel report path from an attacker-controllable
``session_id`` (lines 176 and 1284 of the legacy ``report/generator.py`` before
the hardening). The doctrinal contract is documented in
``docs/ops/inspirations/DEFENSIVE_SCANNING_MANIFESTO.md`` (§1.3 — *no surprise
side effects*) and ``THE_ART_OF_THE_FALLBACK.md`` §3 (*diagnostic on fall, never
silent*).

Note: ``test_report_trends.test_heatmap_embed_only_accepts_path_under_output_dir``
already covers the *embed* sink (read path); these tests cover the *write*
sinks and additional adversarial inputs that the previous shape would have
mishandled.
"""

from pathlib import Path

import pytest

from core.database import LocalDBManager
from report.generator import (
    _heatmap_path_under_output_dir,
    _resolve_under_output_dir,
    generate_report,
)


# ---------- _resolve_under_output_dir (write-time barrier) ------------------


def test_resolve_under_output_dir_accepts_clean_basename(tmp_path):
    """Happy path: a clean basename under an existing output_dir resolves OK."""
    out = tmp_path / "reports"
    out.mkdir()
    candidate = _resolve_under_output_dir(str(out), "Relatorio_Auditoria_abc123.xlsx")
    assert candidate is not None
    assert candidate.parent.resolve() == out.resolve()
    assert candidate.name == "Relatorio_Auditoria_abc123.xlsx"


def test_resolve_under_output_dir_creates_missing_directory(tmp_path):
    """Legacy callers pass output_dir='.' or a not-yet-created subdir; we must mkdir."""
    out = tmp_path / "fresh_dir_to_be_made"
    candidate = _resolve_under_output_dir(str(out), "heatmap_xxx.png")
    assert candidate is not None
    assert out.exists() and out.is_dir()


@pytest.mark.parametrize(
    "evil_filename",
    [
        "../../etc/passwd",
        "..\\..\\Windows\\System32",
        "../escape.xlsx",
        "..",
        ".",
        "",
        "/etc/passwd",
        "C:\\Windows\\evil.xlsx",
        "subdir/inner.xlsx",
        "....//....//etc/passwd",  # naive ".."-strip filter bypass; we collapse to basename.
        "report\x00.xlsx",  # null byte in filename
    ],
)
def test_resolve_under_output_dir_rejects_traversal(tmp_path, evil_filename):
    """Adversarial inputs must not escape output_dir; helper returns None."""
    out = tmp_path / "out"
    out.mkdir()
    candidate = _resolve_under_output_dir(str(out), evil_filename)
    if candidate is not None:
        # If something resolves at all, it MUST sit inside the resolved out dir.
        # (e.g. "....//etc/passwd" -> "etc/passwd" basename is allowed only as a
        # plain basename inside out/; we confirm the containment property.)
        resolved_base = out.resolve()
        assert candidate.resolve() == resolved_base or str(
            candidate.resolve()
        ).startswith(str(resolved_base) + "/")


def test_resolve_under_output_dir_rejects_non_string_inputs(tmp_path):
    """Type confusion guard."""
    out = tmp_path / "out"
    out.mkdir()
    assert _resolve_under_output_dir(str(out), None) is None  # type: ignore[arg-type]
    assert _resolve_under_output_dir(None, "x.xlsx") is None  # type: ignore[arg-type]


# ---------- _heatmap_path_under_output_dir (read/embed barrier) ------------


def test_heatmap_path_helper_accepts_real_file_under_dir(tmp_path):
    out = tmp_path / "out"
    out.mkdir()
    f = out / "heatmap_abc123.png"
    f.write_bytes(b"\x89PNG\r\n\x1a\n")
    got = _heatmap_path_under_output_dir(str(f), str(out))
    assert got is not None
    assert got.resolve() == f.resolve()


def test_heatmap_path_helper_rejects_outside_path(tmp_path):
    out = tmp_path / "out"
    out.mkdir()
    bad = tmp_path / "outside.png"
    bad.write_bytes(b"x")
    assert _heatmap_path_under_output_dir(str(bad), str(out)) is None


def test_heatmap_path_helper_rejects_nonexistent_basename(tmp_path):
    out = tmp_path / "out"
    out.mkdir()
    # Even if the basename looks safe, the file must exist for read/embed.
    assert _heatmap_path_under_output_dir("missing.png", str(out)) is None


# ---------- end-to-end: generate_report with adversarial session_id --------


def _seed_session(mgr: LocalDBManager, sid: str) -> None:
    mgr.set_current_session_id(sid)
    mgr.create_session_record(sid)
    mgr.save_finding(
        "database",
        target_name="T1",
        column_name="cpf",
        sensitivity_level="HIGH",
        pattern_detected="CPF",
        norm_tag="LGPD",
        ml_confidence=90,
    )
    mgr.finish_session(sid)


def test_generate_report_with_traversal_session_id_stays_inside_output_dir(
    tmp_path,
):
    """
    A malicious ``session_id`` like ``../../etc/passwd`` MUST NOT cause writes
    outside the configured ``output_dir``. The session_id is laundered through
    :func:`safe_session_prefix` before joining the output directory, and the
    final path is validated by :func:`_resolve_under_output_dir`.
    """
    db_path = str(tmp_path / "audit.db")
    out_dir = tmp_path / "out"
    out_dir.mkdir()

    evil_sid = "../../escape_attempt_xyz"
    mgr = LocalDBManager(db_path)
    try:
        _seed_session(mgr, evil_sid)
        report_path = generate_report(mgr, evil_sid, output_dir=str(out_dir))
        assert report_path is not None
        report = Path(report_path).resolve()
        # Must sit strictly under the resolved output directory.
        assert str(report).startswith(str(out_dir.resolve()) + "/")
        # Must not contain literal traversal segments.
        assert ".." not in report.parts
        # Outside the jail, nothing must have been created.
        outside = (tmp_path / "etc").exists() or (
            tmp_path / "escape_attempt_xyz"
        ).exists()
        assert not outside
    finally:
        mgr.dispose()


def test_generate_report_with_clean_uuid_session_id_keeps_legacy_filename(
    tmp_path,
):
    """
    No regression on the legitimate happy path: a UUID-style session_id keeps
    the documented ``Relatorio_Auditoria_<first16>.xlsx`` shape.
    """
    db_path = str(tmp_path / "audit.db")
    out_dir = tmp_path / "out"
    out_dir.mkdir()
    sid = "a1b2c3d4-e5f6-7890-abcd-ef1234567890"
    mgr = LocalDBManager(db_path)
    try:
        _seed_session(mgr, sid)
        report_path = generate_report(mgr, sid, output_dir=str(out_dir))
        assert report_path is not None
        name = Path(report_path).name
        assert name.startswith("Relatorio_Auditoria_")
        assert name.endswith(".xlsx")
        # Resolve and confirm containment.
        assert str(Path(report_path).resolve()).startswith(str(out_dir.resolve()) + "/")
    finally:
        mgr.dispose()
