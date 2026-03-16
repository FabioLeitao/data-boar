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
            self.assertIn(
                "lyrics",
                result.get("pattern_detected", "").lower()
                or "lyrics" in result.get("pattern_detected", ""),
            )

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

    def test_phone_column_names_flagged_sensitive(self):
        """Phone-related column names (home phone, mobile, celular, téléphone, etc.) are recognised and flagged."""
        scanner = DataScanner()
        phone_columns = [
            "celular",
            "home_phone",
            "mobile",
            "telefone",
            "téléphone",
            "work phone",
            "handynummer",
        ]
        for col in phone_columns:
            with self.subTest(column=col):
                result = scanner.scan_column(col, "sample value")
                self.assertIn(
                    result["sensitivity_level"],
                    ("HIGH", "MEDIUM"),
                    f"Column '{col}' should be flagged as sensitive (phone)",
                )

    def test_name_column_names_flagged_sensitive(self):
        """Name-related column names (first name, surname, apellido, nachname, etc.) are recognised and flagged."""
        scanner = DataScanner()
        name_columns = [
            "first_name",
            "last_name",
            "surname",
            "full_name",
            "birth name",
            "nickname",
            "sobrenome",
            "apellido",
            "prénom",
            "nom de famille",
            "vorname",
            "nachname",
        ]
        for col in name_columns:
            with self.subTest(column=col):
                result = scanner.scan_column(col, "sample value")
                self.assertIn(
                    result["sensitivity_level"],
                    ("HIGH", "MEDIUM"),
                    f"Column '{col}' should be flagged as sensitive (name/identifier)",
                )

    def test_id_document_column_names_flagged_sensitive(self):
        """ID/document column names (passport, ctps, documento oficial, green card, etc.) are recognised and flagged."""
        scanner = DataScanner()
        id_columns = [
            "passaporte",
            "passport",
            "ctps",
            "documento oficial",
            "green card",
            "cnh",
            "driver license",
            "identity document",
            "id card",
            "national id",
            "document number",
            "certidao",
            "cartao cidadao",
        ]
        for col in id_columns:
            with self.subTest(column=col):
                result = scanner.scan_column(col, "sample value")
                self.assertIn(
                    result["sensitivity_level"],
                    ("HIGH", "MEDIUM"),
                    f"Column '{col}' should be flagged as sensitive (ID/document)",
                )

    def test_ambiguous_column_doc_id_returns_medium_and_pii_ambiguous(self):
        """Generic column names (doc_id, document_id, etc.) return MEDIUM and PII_AMBIGUOUS for manual confirmation."""
        scanner = DataScanner()
        for col in ("doc_id", "document_id", "id_number"):
            with self.subTest(column=col):
                result = scanner.scan_column(col, "sample value")
                self.assertEqual(
                    result["sensitivity_level"],
                    "MEDIUM",
                    f"Column '{col}' should be MEDIUM (ambiguous)",
                )
                self.assertIn(
                    "PII_AMBIGUOUS",
                    result.get("pattern_detected", ""),
                    f"Column '{col}' should have PII_AMBIGUOUS",
                )


if __name__ == "__main__":
    unittest.main()
