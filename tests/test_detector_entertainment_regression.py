"""
Regression guards: entertainment / low-PII context vs ML-only HIGH.

**Why this module exists:** Clone-tree and music-folder scans used to yield many rows with
``HIGH`` + ``ML_DETECTED`` and ~99% ``ml_confidence`` on README/lyrics/cifra-like content.
The detector caps ML-only highs in that context to ``MEDIUM`` + ``ML_POTENTIAL_ENTERTAINMENT``
with reported confidence ≤ 55 (or ``MEDIUM`` + ``ML_POTENTIAL`` when post-penalty score
stays below 70). **Never** ``HIGH`` + ``ML_DETECTED`` for those paths.

**Determinism:** Two tests patch ``RandomForestClassifier.predict_proba`` to simulate ~100%
sensitive probability so we always exercise the ``>= 70`` branch after the entertainment
``-25`` penalty, without depending on TF-IDF + RF noise from tiny training sets.

**Gate:** Full pytest is run by ``scripts/check-all.ps1`` (``pre-commit-and-tests.ps1``); CI
runs the same suite. No separate registration needed.
"""

from __future__ import annotations

import unittest
from unittest.mock import patch

import numpy as np

from core.scanner import DataScanner

# Minimal terms so a real vectorizer + RF exist; ML score comes from the patch below.
_MIN_ML_TERMS: list[dict[str, str]] = [
    {"text": "sensitive_token_xyz", "label": "sensitive"},
    {"text": "neutral_plain", "label": "non_sensitive"},
]


def _almost_certain_sensitive_proba(_X) -> np.ndarray:
    """Binary classifier: class index 1 = sensitive (~100%)."""
    return np.array([[0.001, 0.999]], dtype=float)


class TestDetectorEntertainmentRegression(unittest.TestCase):
    """Contract: ML-only highs in entertainment/OSS-doc context must not be HIGH + ML_DETECTED."""

    def setUp(self) -> None:
        self.scanner = DataScanner(ml_terms_inline=_MIN_ML_TERMS)
        if not getattr(self.scanner.detector, "_model", None):
            self.skipTest("sklearn ML stack not available")

    def test_patched_high_ml_in_lyrics_is_medium_ml_potential_entertainment(self) -> None:
        lyrics = """Verse 1
This line has sensitive_token_xyz in it
Chorus
La la la la la"""
        with patch.object(
            self.scanner.detector._model,
            "predict_proba",
            side_effect=_almost_certain_sensitive_proba,
        ):
            result = self.scanner.scan_column("song_lyrics", lyrics)
        self.assertEqual(result["sensitivity_level"], "MEDIUM")
        self.assertEqual(result["pattern_detected"], "ML_POTENTIAL_ENTERTAINMENT")
        self.assertLessEqual(result["ml_confidence"], 55)
        self.assertNotIn("ML_DETECTED", result["pattern_detected"])

    def test_patched_high_ml_readme_short_sample_one_heading_entertainment(self) -> None:
        """Filesystem-sized chunks: one # line + short body must still trigger OSS Markdown context."""
        body = (
            "# Data Boar\n\n"
            "Short readme sample for scan; fewer than two headings in this chunk only.\n"
        )
        assert len(body.strip()) >= 60
        with patch.object(
            self.scanner.detector._model,
            "predict_proba",
            side_effect=_almost_certain_sensitive_proba,
        ):
            result = self.scanner.scan_file_content(body, "README.md")
        self.assertIsNotNone(result)
        assert result is not None
        self.assertEqual(result["sensitivity_level"], "MEDIUM")
        self.assertEqual(result["pattern_detected"], "ML_POTENTIAL_ENTERTAINMENT")
        self.assertLessEqual(result["ml_confidence"], 55)

    def test_patched_high_ml_subtitle_srt_path_entertainment(self) -> None:
        """Sidecar .srt path + dialogue text → ML-only HIGH capped (patched proba)."""
        body = "\n".join(f"Cue line {i} with sensitive_token_xyz mention" for i in range(10))
        with patch.object(
            self.scanner.detector._model,
            "predict_proba",
            side_effect=_almost_certain_sensitive_proba,
        ):
            result = self.scanner.scan_file_content(body, "movie.pt_BR.srt")
        self.assertIsNotNone(result)
        assert result is not None
        self.assertEqual(result["sensitivity_level"], "MEDIUM")
        self.assertEqual(result["pattern_detected"], "ML_POTENTIAL_ENTERTAINMENT")
        self.assertLessEqual(result["ml_confidence"], 55)

    def test_patched_high_ml_interleaved_cifra_mixed_case_chords_entertainment(self) -> None:
        """Alternating chord rows (C, D2sus9, EM7, Am, …) and lyric lines → entertainment context."""
        body = (
            "C    D2sus9    EM7    Am\n"
            "Maria called on Tuesday saying she would wait at the station downtown\n"
            "G    C    F    dm7\n"
            "Walking down the long avenue in the summer rain again tonight\n"
            "F    G    C\n"
            "The doctor said tomorrow never knows what sensitive_token_xyz meant anyway\n"
        )
        with patch.object(
            self.scanner.detector._model,
            "predict_proba",
            side_effect=_almost_certain_sensitive_proba,
        ):
            result = self.scanner.scan_file_content(body, "Song idea.txt")
        self.assertIsNotNone(result)
        assert result is not None
        self.assertEqual(result["sensitivity_level"], "MEDIUM")
        self.assertEqual(result["pattern_detected"], "ML_POTENTIAL_ENTERTAINMENT")
        self.assertLessEqual(result["ml_confidence"], 55)

    def test_patched_high_ml_in_contributing_md_is_medium_ml_potential_entertainment(self) -> None:
        body = """# Contributing

## How to report
Use the issue tracker. sensitive_token_xyz is internal jargon.

## Code style
Run tests before PR.
"""
        with patch.object(
            self.scanner.detector._model,
            "predict_proba",
            side_effect=_almost_certain_sensitive_proba,
        ):
            result = self.scanner.scan_file_content(body, "CONTRIBUTING.md")
        self.assertIsNotNone(result)
        assert result is not None
        self.assertEqual(result["sensitivity_level"], "MEDIUM")
        self.assertEqual(result["pattern_detected"], "ML_POTENTIAL_ENTERTAINMENT")
        self.assertLessEqual(result["ml_confidence"], 55)
        self.assertNotEqual(result["pattern_detected"], "ML_DETECTED")

    def test_never_high_ml_detected_for_chord_grid_cifra_pattern(self) -> None:
        """Chord-only lines (cifra) must stay out of HIGH + ML_DETECTED when ML fires alone."""
        scanner = DataScanner()
        cifra = """intro
C    G    Am   F
C    G    Am   F
Dm7  G7   C
"""
        result = scanner.scan_column("partitura", cifra)
        if result["sensitivity_level"] == "HIGH" and "ML_DETECTED" in result.get(
            "pattern_detected", ""
        ):
            self.fail(
                "Regression: cifra-like grid must not yield HIGH + ML_DETECTED "
                "(entertainment heuristics should cap ML-only path)"
            )
        self.assertIn(result["sensitivity_level"], ("LOW", "MEDIUM"))


if __name__ == "__main__":
    unittest.main()
