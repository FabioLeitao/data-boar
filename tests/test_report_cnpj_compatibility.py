from report.generator import _build_report_info


def test_report_info_includes_cnpj_format_compatibility_note():
    """Report info includes a brief CNPJ format compatibility summary when CNPJ patterns are present."""
    session_id = "test-session-cnpj"
    meta = {
        "started_at": "2026-03-16T10:00:00Z",
        "tenant_name": "TestTenant",
        "technician_name": "Tester",
        "config_scope_hash": None,
    }
    about = {
        "name": "Data Boar",
        "version": "1.5.4",
        "author": "Tester",
        "license": "BSD",
        "copyright": "Copyright",
    }
    # One numeric-only column, one alphanumeric-only, one mixed
    db_rows = [
        {
            "target_name": "db1",
            "column_name": "cnpj_legacy",
            "pattern_detected": "LGPD_CNPJ",
        },
        {
            "target_name": "db1",
            "column_name": "cnpj_mixed",
            "pattern_detected": "LGPD_CNPJ",
        },
    ]
    fs_rows = [
        {
            "target_name": "fs1",
            "file_name": "doc_alnum.txt",
            "pattern_detected": "LGPD_CNPJ_ALNUM",
        },
        {
            "target_name": "db1",
            "column_name": "cnpj_mixed",
            "pattern_detected": "LGPD_CNPJ_ALNUM",
        },
    ]

    rows = _build_report_info(session_id, meta, about, db_rows, fs_rows)
    compat_rows = [r for r in rows if r.get("Field") == "CNPJ format compatibility"]
    assert len(compat_rows) == 1
    value = compat_rows[0]["Value"]
    # Legacy-only: db1/cnpj_legacy; Alphanumeric-only: fs1/doc_alnum.txt; Mixed: db1/cnpj_mixed
    assert "Legacy numeric: 1 columns" in value
    assert "Alphanumeric: 1 columns" in value
    assert "Mixed: 1 columns" in value
