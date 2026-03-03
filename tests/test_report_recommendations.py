"""Tests for report Recommendations sheet, recommendation_overrides, and Executive summary."""
import pytest
from pathlib import Path

from core.database import LocalDBManager
from report.generator import generate_report


def test_recommendations_without_overrides_uses_builtin_logic(tmp_path):
    """Without config/recommendation_overrides, Recommendations sheet uses built-in CPF/EMAIL/etc. logic."""
    db_path = str(tmp_path / "audit.db")
    out_dir = str(tmp_path / "out")
    Path(out_dir).mkdir(parents=True, exist_ok=True)
    mgr = LocalDBManager(db_path)
    try:
        mgr.set_current_session_id("s1")
        mgr.create_session_record("s1")
        mgr.save_finding(
            "database",
            target_name="T1",
            column_name="cpf",
            sensitivity_level="HIGH",
            pattern_detected="CPF",
            norm_tag="LGPD Art. 5",
            ml_confidence=90,
        )
        mgr.finish_session("s1")
        path = generate_report(mgr, "s1", output_dir=out_dir, config=None)
        assert path is not None
        import pandas as pd
        with pd.ExcelFile(path) as xl:
            assert "Recommendations" in xl.sheet_names
            df = pd.read_excel(xl, sheet_name="Recommendations")
        assert "Data / Pattern" in df.columns and "Base legal" in df.columns
        cpf_row = df[df["Data / Pattern"] == "CPF"].iloc[0]
        assert "CRÍTICA" in str(cpf_row["Prioridade"])
        assert "LGPD" in str(cpf_row["Base legal"]) or "identificação" in str(cpf_row["Base legal"]).lower()
    finally:
        mgr.dispose()


def test_recommendations_with_overrides_uses_override_for_matching_norm_tag(tmp_path):
    """With report.recommendation_overrides, a matching norm_tag gets the override row in Recommendations."""
    db_path = str(tmp_path / "audit2.db")
    out_dir = str(tmp_path / "out2")
    Path(out_dir).mkdir(parents=True, exist_ok=True)
    mgr = LocalDBManager(db_path)
    try:
        mgr.set_current_session_id("s2")
        mgr.create_session_record("s2")
        mgr.save_finding(
            "database",
            target_name="T1",
            column_name="national_id",
            sensitivity_level="HIGH",
            pattern_detected="UK_SSN",
            norm_tag="UK GDPR",
            ml_confidence=85,
        )
        mgr.finish_session("s2")
        config = {
            "report": {
                "output_dir": out_dir,
                "recommendation_overrides": [
                    {
                        "norm_tag_pattern": "UK GDPR",
                        "base_legal": "UK GDPR Art. 4(1)",
                        "risk": "Identification of data subject.",
                        "recommendation": "Apply UK GDPR safeguards and DPA registration if required.",
                        "priority": "ALTA",
                        "relevant_for": "DPO, UK Representative",
                    },
                ],
            },
        }
        path = generate_report(mgr, "s2", output_dir=out_dir, config=config)
        assert path is not None
        import pandas as pd
        with pd.ExcelFile(path) as xl:
            df = pd.read_excel(xl, sheet_name="Recommendations")
        uk_row = df[df["Data / Pattern"] == "UK_SSN"].iloc[0]
        assert "UK GDPR Art. 4(1)" in str(uk_row["Base legal"])
        assert "UK GDPR safeguards" in str(uk_row["Recomendação"]) or "DPA" in str(uk_row["Recomendação"])
        assert str(uk_row["Prioridade"]) == "ALTA"
    finally:
        mgr.dispose()


def test_executive_summary_sheet_when_enabled(tmp_path):
    """With report.include_executive_summary true, report contains 'Executive summary' sheet with Metric, Category, Count."""
    db_path = str(tmp_path / "audit_exec.db")
    out_dir = str(tmp_path / "out_exec")
    Path(out_dir).mkdir(parents=True, exist_ok=True)
    mgr = LocalDBManager(db_path)
    try:
        mgr.set_current_session_id("s-exec")
        mgr.create_session_record("s-exec")
        mgr.save_finding(
            "database",
            target_name="DB1",
            column_name="email",
            sensitivity_level="HIGH",
            pattern_detected="EMAIL",
            norm_tag="GDPR Art. 4(1)",
            ml_confidence=90,
        )
        mgr.save_finding(
            "filesystem",
            target_name="FS1",
            file_name="data.csv",
            sensitivity_level="MEDIUM",
            pattern_detected="DATE",
            norm_tag="",
            ml_confidence=70,
        )
        mgr.finish_session("s-exec")
        config = {"report": {"output_dir": out_dir, "include_executive_summary": True}}
        path = generate_report(mgr, "s-exec", output_dir=out_dir, config=config)
        assert path is not None
        import pandas as pd
        with pd.ExcelFile(path) as xl:
            assert "Executive summary" in xl.sheet_names
            df = pd.read_excel(xl, sheet_name="Executive summary")
        assert "Metric" in df.columns and "Category" in df.columns and "Count" in df.columns
        by_sens = df[df["Metric"] == "Findings by sensitivity"]
        assert len(by_sens) >= 3  # HIGH, MEDIUM, LOW
        high_row = by_sens[by_sens["Category"] == "HIGH"].iloc[0]
        assert high_row["Count"] == 1
        by_norm = df[df["Metric"] == "Findings by Framework / Norm"]
        assert len(by_norm) >= 1
        top_targets = df[df["Metric"] == "Top targets by finding count"]
        assert len(top_targets) >= 1
    finally:
        mgr.dispose()


def test_min_sensitivity_filters_low_from_findings_sheets(tmp_path):
    """With report.min_sensitivity HIGH, LOW findings do not appear in Database/Filesystem findings sheets."""
    db_path = str(tmp_path / "audit_min.db")
    out_dir = str(tmp_path / "out_min")
    Path(out_dir).mkdir(parents=True, exist_ok=True)
    mgr = LocalDBManager(db_path)
    try:
        mgr.set_current_session_id("s-min")
        mgr.create_session_record("s-min")
        mgr.save_finding(
            "database",
            target_name="T1",
            column_name="cpf",
            sensitivity_level="HIGH",
            pattern_detected="CPF",
            norm_tag="LGPD",
            ml_confidence=90,
        )
        mgr.save_finding(
            "database",
            target_name="T1",
            column_name="note",
            sensitivity_level="LOW",
            pattern_detected="GENERIC",
            norm_tag="",
            ml_confidence=30,
        )
        mgr.finish_session("s-min")
        config = {"report": {"output_dir": out_dir, "min_sensitivity": "HIGH"}}
        path = generate_report(mgr, "s-min", output_dir=out_dir, config=config)
        assert path is not None
        import pandas as pd
        with pd.ExcelFile(path) as xl:
            assert "Database findings" in xl.sheet_names
            df = pd.read_excel(xl, sheet_name="Database findings")
        # Only HIGH (CPF) should appear; LOW (note/GENERIC) excluded
        assert len(df) == 1
        assert df.iloc[0]["sensitivity_level"] == "HIGH"
        assert "CPF" in str(df.iloc[0]["pattern_detected"])
    finally:
        mgr.dispose()


def test_config_scope_hash_stored_and_in_report_info(tmp_path):
    """Session can store config_scope_hash; report Report info sheet includes it when present."""
    db_path = str(tmp_path / "audit_hash.db")
    out_dir = str(tmp_path / "out_hash")
    Path(out_dir).mkdir(parents=True, exist_ok=True)
    mgr = LocalDBManager(db_path)
    try:
        mgr.set_current_session_id("s-hash")
        mgr.create_session_record(
            "s-hash",
            config_scope_hash="a1b2c3d4e5f6",
        )
        mgr.save_finding(
            "database",
            target_name="T1",
            column_name="email",
            sensitivity_level="HIGH",
            pattern_detected="EMAIL",
            norm_tag="GDPR",
            ml_confidence=85,
        )
        mgr.finish_session("s-hash")
        sessions = mgr.list_sessions()
        assert len(sessions) == 1
        assert sessions[0].get("config_scope_hash") == "a1b2c3d4e5f6"
        path = generate_report(mgr, "s-hash", output_dir=out_dir, config={})
        assert path is not None
        import pandas as pd
        with pd.ExcelFile(path) as xl:
            df = pd.read_excel(xl, sheet_name="Report info")
        scope_row = df[df["Field"] == "Config scope hash"]
        assert len(scope_row) == 1
        assert scope_row.iloc[0]["Value"] == "a1b2c3d4e5f6"
    finally:
        mgr.dispose()
