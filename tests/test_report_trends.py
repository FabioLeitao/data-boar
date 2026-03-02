"""Tests for report trends / session comparison sheet."""
import pytest
from pathlib import Path

from core.database import LocalDBManager
from report.generator import generate_report


def test_report_includes_trends_sheet(tmp_path):
    db_path = str(tmp_path / "audit.db")
    out_dir = str(tmp_path / "out")
    Path(out_dir).mkdir(parents=True, exist_ok=True)
    mgr = LocalDBManager(db_path)
    # First session: 2 DB findings
    mgr.set_current_session_id("s1")
    mgr.create_session_record("s1")
    mgr.save_finding("database", target_name="T1", column_name="cpf", sensitivity_level="HIGH", pattern_detected="CPF", norm_tag="LGPD", ml_confidence=90)
    mgr.save_finding("database", target_name="T1", column_name="email", sensitivity_level="HIGH", pattern_detected="EMAIL", norm_tag="GDPR", ml_confidence=88)
    mgr.finish_session("s1")
    # Second session: 1 DB finding (improvement)
    mgr.set_current_session_id("s2")
    mgr.create_session_record("s2")
    mgr.save_finding("database", target_name="T1", column_name="cpf", sensitivity_level="HIGH", pattern_detected="CPF", norm_tag="LGPD", ml_confidence=90)
    mgr.finish_session("s2")
    path = generate_report(mgr, "s2", output_dir=out_dir)
    assert path is not None
    import pandas as pd
    xl = pd.ExcelFile(path)
    assert "Trends - Session comparison" in xl.sheet_names
    df = pd.read_excel(path, sheet_name="Trends - Session comparison")
    assert len(df) == 4
    assert "Metric" in df.columns and "Note" in df.columns and "Change" in df.columns
    # Total findings: 1 this run vs 2 previous -> improvement
    total_row = df[df["Metric"] == "Total findings (DB + filesystem)"].iloc[0]
    assert "Improvement" in str(total_row["Note"]) or "reduced" in str(total_row["Note"]).lower()
