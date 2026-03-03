"""
Tests for possible minor data detection (DOB/age heuristic).
Covers EN and PT-BR column names, acronyms (DOB, DDN, NASC, idade), date formats (DMY, YMD),
and numeric age; ensures DOB_POSSIBLE_MINOR and LGPD Art. 14 / GDPR Art. 8 appear when appropriate
and are not set for adults or non-DOB/age columns.
"""
import unittest

from core.detector import SensitivityDetector, _detect_possible_minor
from core.scanner import DataScanner


class TestMinorDetectionHeuristic(unittest.TestCase):
    """Unit tests for _detect_possible_minor (column name + sample → possible minor)."""

    def test_age_like_column_with_minor_age_returns_true(self):
        self.assertTrue(_detect_possible_minor("idade", "17", 18))
        self.assertTrue(_detect_possible_minor("age", "0", 18))
        self.assertTrue(_detect_possible_minor("idade_atual", "15", 18))

    def test_age_like_column_with_adult_age_returns_false(self):
        self.assertFalse(_detect_possible_minor("idade", "25", 18))
        self.assertFalse(_detect_possible_minor("age", "18", 18))
        self.assertFalse(_detect_possible_minor("idade", "30", 18))

    def test_dob_like_column_with_minor_birth_date_returns_true(self):
        # Use a recent birth date so age is always < 18 regardless of test run year
        self.assertTrue(_detect_possible_minor("data de nascimento", "01/01/2022", 18))
        self.assertTrue(_detect_possible_minor("dob", "2015-06-15", 18))
        self.assertTrue(_detect_possible_minor("ddn", "15/03/2012", 18))
        self.assertTrue(_detect_possible_minor("nascimento", "01/01/2020", 18))

    def test_dob_like_column_with_adult_birth_date_returns_false(self):
        self.assertFalse(_detect_possible_minor("data de nascimento", "01/01/1990", 18))
        self.assertFalse(_detect_possible_minor("dob", "1985-01-01", 18))
        self.assertFalse(_detect_possible_minor("birth date", "15/03/1995", 18))

    def test_non_dob_age_column_ignores_minor_value(self):
        # "17" in sample but column name does not suggest age/DOB → not minor
        self.assertFalse(_detect_possible_minor("item_count", "17", 18))
        self.assertFalse(_detect_possible_minor("quantity", "5", 18))
        self.assertFalse(_detect_possible_minor("other_column", "01/01/2022", 18))

    def test_custom_threshold(self):
        self.assertTrue(_detect_possible_minor("idade", "20", 21))
        self.assertFalse(_detect_possible_minor("idade", "20", 18))


class TestMinorDetectionViaScanner(unittest.TestCase):
    """Integration tests: DataScanner returns HIGH + DOB_POSSIBLE_MINOR and LGPD Art. 14 when appropriate."""

    def test_idade_with_17_returns_high_and_possible_minor_marker(self):
        scanner = DataScanner()
        result = scanner.scan_column("idade", "17")
        self.assertEqual(result["sensitivity_level"], "HIGH")
        self.assertIn("DOB_POSSIBLE_MINOR", result["pattern_detected"])
        self.assertIn("LGPD Art. 14", result["norm_tag"])
        self.assertIn("GDPR Art. 8", result["norm_tag"])

    def test_data_de_nascimento_with_minor_date_returns_high_and_possible_minor(self):
        scanner = DataScanner()
        # Birth date that yields age < 18 regardless of current year
        result = scanner.scan_column("data de nascimento", "01/01/2022")
        self.assertEqual(result["sensitivity_level"], "HIGH")
        self.assertIn("DOB_POSSIBLE_MINOR", result["pattern_detected"])
        self.assertIn("LGPD Art. 14", result["norm_tag"])

    def test_dob_acronym_with_minor_date_returns_possible_minor(self):
        scanner = DataScanner()
        result = scanner.scan_column("dob", "2015-01-01")
        self.assertEqual(result["sensitivity_level"], "HIGH")
        self.assertIn("DOB_POSSIBLE_MINOR", result["pattern_detected"])

    def test_age_with_adult_value_no_possible_minor_marker(self):
        scanner = DataScanner()
        result = scanner.scan_column("age", "25")
        # Should not be tagged as possible minor (adult age)
        self.assertNotIn("DOB_POSSIBLE_MINOR", result.get("pattern_detected", ""))

    def test_dob_with_adult_birth_date_no_possible_minor_marker(self):
        scanner = DataScanner()
        result = scanner.scan_column("dob", "01/01/1990")
        self.assertNotIn("DOB_POSSIBLE_MINOR", result.get("pattern_detected", ""))

    def test_unrelated_column_with_number_no_minor_marker(self):
        scanner = DataScanner()
        result = scanner.scan_column("quantity", "17")
        self.assertNotIn("DOB_POSSIBLE_MINOR", result.get("pattern_detected", ""))


class TestMinorDetectionDoesNotBreakExisting(unittest.TestCase):
    """Ensure minor detection is additive: existing behaviour for non-minor data unchanged."""

    def test_cpf_still_high(self):
        scanner = DataScanner()
        result = scanner.scan_column("documento", "123.456.789-00")
        self.assertEqual(result["sensitivity_level"], "HIGH")
        self.assertIn("CPF", result.get("pattern_detected", ""))

    def test_low_sensitivity_unchanged(self):
        scanner = DataScanner()
        result = scanner.scan_column("item_count", "42")
        self.assertEqual(result["sensitivity_level"], "LOW")

    def test_scan_column_shape_unchanged(self):
        scanner = DataScanner()
        result = scanner.scan_column("idade", "17")
        self.assertIn("sensitivity_level", result)
        self.assertIn("pattern_detected", result)
        self.assertIn("norm_tag", result)
        self.assertIn("ml_confidence", result)


if __name__ == "__main__":
    unittest.main()
