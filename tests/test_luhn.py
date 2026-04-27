"""Tests for the shared Luhn helper (``core.luhn``)."""

from __future__ import annotations

import unittest

from core.luhn import (
    luhn_check,
    luhn_check_digits,
    string_contains_luhn_valid_card,
)


class TestLuhnCheckDigits(unittest.TestCase):
    def test_known_valid_visa_test_number(self) -> None:
        # Public test card number (4111 1111 1111 1111).
        self.assertTrue(luhn_check_digits("4111111111111111"))

    def test_known_valid_mastercard_test_number(self) -> None:
        self.assertTrue(luhn_check_digits("5555555555554444"))

    def test_invalid_single_digit_typo(self) -> None:
        # Flip the final digit so the checksum no longer holds.
        self.assertFalse(luhn_check_digits("4111111111111112"))

    def test_rejects_too_short(self) -> None:
        self.assertFalse(luhn_check_digits("411111"))

    def test_rejects_too_long(self) -> None:
        # 20 digits is outside ISO/IEC 7812 PAN range, even if Luhn were valid.
        self.assertFalse(luhn_check_digits("0" * 20))

    def test_rejects_non_digit_input(self) -> None:
        self.assertFalse(luhn_check_digits("4111-1111-1111-1111"))

    def test_rejects_empty(self) -> None:
        self.assertFalse(luhn_check_digits(""))


class TestLuhnCheck(unittest.TestCase):
    def test_strips_spaces_and_dashes(self) -> None:
        self.assertTrue(luhn_check("4111 1111 1111 1111"))
        self.assertTrue(luhn_check("4111-1111-1111-1111"))

    def test_rejects_typo_after_strip(self) -> None:
        self.assertFalse(luhn_check("4111 1111 1111 1112"))


class TestStringContainsLuhnValidCard(unittest.TestCase):
    def test_finds_card_inside_text(self) -> None:
        text = "payment ref=4111 1111 1111 1111 ok"
        self.assertTrue(string_contains_luhn_valid_card(text))

    def test_ignores_random_16_digit_run(self) -> None:
        # 16 digits, deliberately not Luhn-valid (would fail real card auth).
        text = "barcode 1234567890123456 product"
        self.assertFalse(string_contains_luhn_valid_card(text))

    def test_empty_text(self) -> None:
        self.assertFalse(string_contains_luhn_valid_card(""))


if __name__ == "__main__":
    unittest.main()
