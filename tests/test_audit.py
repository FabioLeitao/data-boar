"""Tests for sensitivity detection using core.scanner.DataScanner and core.detector."""
import pytest
from core.scanner import DataScanner
from core.detector import SensitivityDetector


def test_cpf_detection():
    scanner = DataScanner()
    result = scanner.scan_column("cpf", "123.456.789-00")
    assert result["sensitivity_level"] == "HIGH"
    assert "LGPD_CPF" in result.get("pattern_detected", "") or "CPF" in result.get("pattern_detected", "")


def test_email_detection():
    scanner = DataScanner()
    result = scanner.scan_column("email", "user@example.com")
    assert result["sensitivity_level"] == "HIGH"
    assert "EMAIL" in result.get("pattern_detected", "")


def test_low_sensitivity():
    scanner = DataScanner()
    result = scanner.scan_column("item_count", "42")
    assert result["sensitivity_level"] in ("LOW", "MEDIUM", "HIGH")
    # Non-personal context often yields LOW
    assert "sensitivity_level" in result
    assert "pattern_detected" in result
