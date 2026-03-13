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

    def test_lyrics_with_date_like_content_downgraded(self):
        """Dates/numbers in song lyrics should not be classified as HIGH (false positive)."""
        scanner = DataScanner()
        lyrics = """Verse 1
        We met on 01/01/2020 and the sun was high
        Chorus
        La la la la la
        Bridge
        Oh oh oh"""
        result = scanner.scan_column("lyrics", lyrics)
        # Should be MEDIUM or LOW due to lyrics context (DATE_DMY is weak in entertainment)
        self.assertIn(result["sensitivity_level"], ("LOW", "MEDIUM"))
        if result["sensitivity_level"] == "MEDIUM":
            self.assertIn("lyrics", result.get("pattern_detected", "").lower() or "lyrics" in result.get("pattern_detected", ""))

    def test_music_tab_with_digits_downgraded(self):
        """Digit sequences in guitar tabs should not be classified as HIGH (false positive)."""
        scanner = DataScanner()
        tab = """e|--0--2--0----
        B|--1--3--1----
        G|--0--0--0----
        D|--2--0--2----
        A|--3-------3--
        E|------------"""
        result = scanner.scan_column("guitar_tab", tab)
        self.assertIn(result["sensitivity_level"], ("LOW", "MEDIUM"))

    def test_real_cpf_in_lyrics_still_high(self):
        """Strong PII (CPF) in content that looks like lyrics should still be HIGH."""
        scanner = DataScanner()
        lyrics_with_cpf = """Verse 1
        Chorus
        The CPF is 123.456.789-00 for the form
        La la la"""
        result = scanner.scan_column("form_data", lyrics_with_cpf)
        self.assertEqual(result["sensitivity_level"], "HIGH")
        self.assertIn("CPF", result.get("pattern_detected", ""))

    def test_ml_only_in_lyrics_capped_at_medium(self):
        """ML-only confidence in lyrics context should not be HIGH to reduce false positives."""
        ml_terms = [
            {"text": "super_sensitive_keyword", "label": "sensitive"},
            {"text": "lyrics", "label": "non_sensitive"},
        ]
        scanner = DataScanner(ml_terms_inline=ml_terms)
        lyrics = """Verse 1
        This is my super_sensitive_keyword
        Chorus
        La la la la la"""
        result = scanner.scan_column("lyrics", lyrics)
        self.assertIn(result["sensitivity_level"], ("LOW", "MEDIUM"))
        self.assertNotEqual(result["sensitivity_level"], "HIGH")


if __name__ == "__main__":
    unittest.main()
