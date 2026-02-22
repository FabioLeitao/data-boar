import unittest
from core.scanner import DataScanner

class TestAuditLogic(unittest.TestCase):
    def test_regex_cpf(self):
        sample = "O CPF do usuario é 123.456.789-00"
        result = DataScanner.scan_text(sample)
        self.assertIn("LGPD_CPF", result)

    def test_sensitivity_check(self):
        self.assertEqual(DataScanner.identify_sensitivity("user_password"), "HIGH")

if __name__ == '__main__':
    unittest.main()
