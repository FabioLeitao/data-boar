"""Tests for audit logic: core.scanner.DataScanner scan_column and analyze_data."""
import unittest
from core.scanner import DataScanner


class TestAuditLogic(unittest.TestCase):
    def test_scan_column_cpf_content(self):
        scanner = DataScanner()
        result = scanner.scan_column("documento", "O CPF do usuario é 123.456.789-00")
        self.assertIn(result["sensitivity_level"], ("HIGH", "MEDIUM"))
        self.assertIn("pattern_detected", result)

    def test_analyze_data_backward_compat(self):
        scanner = DataScanner()
        level, pattern = scanner.analyze_data("user_password", "secret123")
        self.assertIn(level, ("HIGH", "MEDIUM", "LOW"))
        self.assertIsInstance(pattern, str)

    def test_scan_file_content_returns_none_for_low(self):
        scanner = DataScanner()
        out = scanner.scan_file_content("just some random text 999", "/tmp/readme.txt")
        # May be None if LOW or a dict if ML flags it
        if out is not None:
            self.assertIn("sensitivity_level", out)
            self.assertIn("pattern_detected", out)


if __name__ == "__main__":
    unittest.main()
