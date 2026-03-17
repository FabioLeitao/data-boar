from core.scanner import DataScanner


def test_legacy_numeric_cnpj_matches_lgpd_cnpj():
    scanner = DataScanner(detection_config={"cnpj_alphanumeric": True})
    content = "Empresa ABC com CNPJ 12.345.678/0001-90 em operação."
    result = scanner.scan_column("cnpj_legacy", content)
    assert result is not None
    assert "LGPD_CNPJ" in result.get("pattern_detected", "")


def test_alphanumeric_cnpj_matches_lgpd_cnpj_alnum():
    scanner = DataScanner(detection_config={"cnpj_alphanumeric": True})
    # First 12 positions alphanumeric, last two digits remain numeric check digits.
    content = "Empresa XYZ com CNPJ AB.CDE.FGH/1234-56 registrado."
    result = scanner.scan_column("cnpj_alnum", content)
    assert result is not None
    assert "LGPD_CNPJ_ALNUM" in result.get("pattern_detected", "")


def test_mixed_cnpj_formats_can_surface_both_patterns():
    scanner = DataScanner(detection_config={"cnpj_alphanumeric": True})
    legacy = "CNPJ 12.345.678/0001-90"
    alnum = "CNPJ AB.CDE.FGH/1234-56"

    res_legacy = scanner.scan_column("cnpj_mixed_legacy", legacy)
    res_alnum = scanner.scan_column("cnpj_mixed_alnum", alnum)

    patterns = {
        res_legacy.get("pattern_detected", ""),
        res_alnum.get("pattern_detected", ""),
    }
    assert any("LGPD_CNPJ" in p for p in patterns)
    assert any("LGPD_CNPJ_ALNUM" in p for p in patterns)

