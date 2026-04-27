"""
Tests for the opt-in algorithmic checksum gate in ``SensitivityDetector``.

The gate post-filters regex shape matches (CPF, CREDIT_CARD) with the
existing modulo-11 (``core.brazilian_cpf``) and Luhn (``core.luhn``) helpers
so a random 11-digit ID or 16-digit barcode that *looks* like PII is no
longer reported as HIGH on shape alone.
"""

from __future__ import annotations

import unittest

from core.detector import SensitivityDetector


# Public/documentation-style fixtures (do not represent real people / cards).
VALID_CPF_FORMATTED = "390.533.447-05"
# Formatted CPF whose check digits ``-01`` are wrong (the real DV for
# 123456789 is ``-09``). Formatted shape avoids overlap with PHONE_BR
# so the test isolates the CPF checksum gate.
INVALID_CPF_FORMATTED = "123.456.789-01"
VALID_VISA_TEST_CARD = "4111 1111 1111 1111"
INVALID_16_DIGIT_RUN = "1234 5678 9012 3456"


class TestChecksumGateDefaultOff(unittest.TestCase):
    """When the flag is off the detector behaves as before (FN-first)."""

    def test_invalid_cpf_still_high_when_disabled(self) -> None:
        detector = SensitivityDetector()
        level, pattern, _, _ = detector.analyze(
            "external_ref", f"value: {INVALID_CPF_FORMATTED}"
        )
        self.assertEqual(level, "HIGH")
        self.assertIn("LGPD_CPF", pattern)

    def test_invalid_card_run_still_high_when_disabled(self) -> None:
        detector = SensitivityDetector()
        level, pattern, _, _ = detector.analyze("ref", INVALID_16_DIGIT_RUN)
        self.assertEqual(level, "HIGH")
        self.assertIn("CREDIT_CARD", pattern)


class TestChecksumGateEnabled(unittest.TestCase):
    """With the flag enabled, shape-only hits are demoted to MEDIUM."""

    def setUp(self) -> None:
        self.detector = SensitivityDetector(
            detection_config={"checksum_validation": True}
        )

    def test_valid_cpf_still_high(self) -> None:
        level, pattern, _, _ = self.detector.analyze("cpf", VALID_CPF_FORMATTED)
        self.assertEqual(level, "HIGH")
        self.assertIn("LGPD_CPF", pattern)

    def test_valid_card_still_high(self) -> None:
        level, pattern, _, _ = self.detector.analyze(
            "payment_ref", VALID_VISA_TEST_CARD
        )
        self.assertEqual(level, "HIGH")
        self.assertIn("CREDIT_CARD", pattern)

    def test_invalid_cpf_demoted_with_diagnostic(self) -> None:
        level, pattern, norm, _ = self.detector.analyze(
            "external_ref", f"value: {INVALID_CPF_FORMATTED}"
        )
        # Random 11-digit IDs should no longer be HIGH on shape alone.
        self.assertEqual(level, "MEDIUM")
        self.assertTrue(
            pattern.startswith("CHECKSUM_REJECTED"),
            f"pattern={pattern!r} should start with CHECKSUM_REJECTED",
        )
        self.assertIn("LGPD_CPF", pattern)
        self.assertIn("Shape match without valid check digit", norm)

    def test_invalid_card_run_demoted_with_diagnostic(self) -> None:
        level, pattern, _, _ = self.detector.analyze("ref", INVALID_16_DIGIT_RUN)
        self.assertEqual(level, "MEDIUM")
        self.assertTrue(pattern.startswith("CHECKSUM_REJECTED"))
        self.assertIn("CREDIT_CARD", pattern)

    def test_email_unaffected_by_checksum_gate(self) -> None:
        # The gate must not touch patterns that have no algorithmic check.
        level, pattern, _, _ = self.detector.analyze("contact", "alice@example.com")
        self.assertEqual(level, "HIGH")
        self.assertIn("EMAIL", pattern)


if __name__ == "__main__":
    unittest.main()
