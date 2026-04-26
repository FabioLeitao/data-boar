"""Tests for CPF checksum validation (algorithmic false-positive reduction)."""

from __future__ import annotations

import unittest

from core.brazilian_cpf import PIIValidator, cpf_checksum_valid, normalize_cpf_digits


class TestNormalizeCpfDigits(unittest.TestCase):
    def test_strips_punctuation(self) -> None:
        self.assertEqual(normalize_cpf_digits("390.533.447-05"), "39053344705")

    def test_rejects_wrong_length(self) -> None:
        self.assertIsNone(normalize_cpf_digits("3905334470"))
        self.assertIsNone(normalize_cpf_digits(""))


class TestCpfChecksumValid(unittest.TestCase):
    def test_public_fixture_passes(self) -> None:
        # Widely used documentation-style number (passes DV only; not a real identity claim).
        self.assertTrue(cpf_checksum_valid("39053344705"))

    def test_rejects_all_same_digit(self) -> None:
        self.assertFalse(cpf_checksum_valid("11111111111"))

    def test_rejects_wrong_check_digit(self) -> None:
        self.assertFalse(cpf_checksum_valid("39053344704"))


class TestPIIValidator(unittest.TestCase):
    def test_validate_cpf_accepts_formatted(self) -> None:
        self.assertTrue(PIIValidator.validate_cpf("390.533.447-05"))

    def test_scan_content_skips_shape_without_valid_checksum(self) -> None:
        v = PIIValidator()
        # CPF-shaped 11 digits with invalid check digits (not a valid CPF).
        text = "id=12345678901 end"
        out = v.scan_content(text)
        self.assertEqual(out["risk_score"], 0)
        self.assertEqual(len(out["found"]), 0)

    def test_scan_content_keeps_valid_hits_masked(self) -> None:
        v = PIIValidator()
        text = "cpf 390.533.447-05 ok"
        out = v.scan_content(text)
        self.assertEqual(out["risk_score"], 10)
        self.assertEqual(len(out["found"]), 1)
        self.assertEqual(out["found"][0]["type"], "BRAZIL_CPF")
        self.assertEqual(out["found"][0]["masked_tail"], "05")
        self.assertEqual(out["found"][0]["confidence"], "HIGH")
