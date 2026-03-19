"""Plan §4: optional connector CHAR/VARCHAR length hint → MEDIUM FORMAT_LENGTH_HINT_ID."""

import unittest

from core.detector import (
    SensitivityDetector,
    _format_length_suggests_id_column,
    _parse_declared_char_length,
)


class TestParseDeclaredCharLength(unittest.TestCase):
    def test_variants(self):
        self.assertEqual(_parse_declared_char_length("VARCHAR(11)"), 11)
        self.assertEqual(_parse_declared_char_length("character varying(14)"), 14)
        self.assertEqual(_parse_declared_char_length("CHAR(9)"), 9)
        self.assertIsNone(_parse_declared_char_length("INT"))
        self.assertIsNone(_parse_declared_char_length(None))
        self.assertIsNone(_parse_declared_char_length(""))


class TestFormatLengthSuggestsId(unittest.TestCase):
    def test_cpf_and_id_suffix(self):
        self.assertTrue(
            _format_length_suggests_id_column("user_cpf", 11)
        )
        self.assertTrue(
            _format_length_suggests_id_column("external_id", 11)
        )
        self.assertFalse(
            _format_length_suggests_id_column("description", 11)
        )

    def test_cnpj(self):
        self.assertTrue(
            _format_length_suggests_id_column("company_cnpj", 14)
        )
        self.assertTrue(
            _format_length_suggests_id_column("tax_registration_id", 14)
        )

    def test_ssn(self):
        self.assertTrue(_format_length_suggests_id_column("employee_ssn", 9))
        self.assertFalse(_format_length_suggests_id_column("status_code", 9))


def _neutral_sample_text() -> str:
    """Push ML/DL confidence down so ID-like column names do not alone trigger HIGH."""
    return " ".join(["item_count"] * 20)


class TestDetectorFormatHintIntegration(unittest.TestCase):
    def test_disabled_no_effect(self):
        d = SensitivityDetector(detection_config={})
        level, pat, _, _ = d.analyze(
            "external_id",
            _neutral_sample_text(),
            connector_data_type="VARCHAR(11)",
        )
        self.assertEqual(level, "LOW")
        self.assertEqual(pat, "GENERAL")

    def test_enabled_low_to_medium(self):
        d = SensitivityDetector(
            detection_config={"connector_format_id_hint": True}
        )
        level, pat, norm, conf = d.analyze(
            "external_id",
            _neutral_sample_text(),
            connector_data_type="VARCHAR(11)",
        )
        self.assertEqual(level, "MEDIUM")
        self.assertEqual(pat, "FORMAT_LENGTH_HINT_ID")
        self.assertIn("Schema", norm)
        self.assertGreaterEqual(conf, 40)


if __name__ == "__main__":
    unittest.main()
