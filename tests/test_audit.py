import pytest
from main import HybridScanner

def test_sensitive_detection():
    scanner = HybridScanner()
    
    # Teste de Regex
    sens, pat, conf = scanner.scan("user_id", "Meu CPF é 123.456.789-00")
    assert sens == "HIGH"
    assert "LGPD_CPF" in pat
    
    # Teste de ML (Contexto)
    sens_ml, pat_ml, conf_ml = scanner.scan("salary_amount", "5000.00")
    assert sens_ml in ["MEDIUM", "HIGH"]
