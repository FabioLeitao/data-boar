"""
Unified scanner that uses core.detector only. No duplicate regex/ML.
Interface: scan_column(label, sample) and scan_file_content(content, path) returning
structured result for LocalDBManager.save_finding.
"""
from pathlib import Path
from typing import Any

from core.detector import SensitivityDetector


class DataScanner:
    """Uses SensitivityDetector for DB columns and file content; returns dicts for save_finding."""

    def __init__(
        self,
        regex_overrides_path: str | None = None,
        ml_patterns_path: str | None = None,
    ):
        self.detector = SensitivityDetector(
            regex_overrides_path=regex_overrides_path,
            ml_patterns_path=ml_patterns_path,
        )

    def scan_column(self, column_name: str, sample_content: str) -> dict[str, Any]:
        """
        Analyze a DB column (name + sample). Returns dict with sensitivity_level, pattern_detected, norm_tag, ml_confidence.
        Sample content is not stored.
        """
        level, pattern, norm, conf = self.detector.analyze(column_name, sample_content or "")
        return {
            "sensitivity_level": level,
            "pattern_detected": pattern,
            "norm_tag": norm,
            "ml_confidence": conf,
        }

    def scan_file_content(self, content: str, file_path: str | Path) -> dict[str, Any] | None:
        """
        Analyze file content (and path for context). Returns same shape as scan_column if sensitivity != LOW; else None.
        """
        path_str = str(file_path)
        name = Path(file_path).name if isinstance(file_path, (str, Path)) else path_str
        level, pattern, norm, conf = self.detector.analyze(name, content or "")
        if level == "LOW":
            return None
        return {
            "sensitivity_level": level,
            "pattern_detected": pattern,
            "norm_tag": norm,
            "ml_confidence": conf,
        }

    # Backward compatibility: analyze_data used by old code
    def analyze_data(self, column_name: str, sample_content: str) -> tuple[str, str]:
        """Returns (sensitivity_level, pattern_detected) for callers that expect a tuple."""
        d = self.scan_column(column_name, sample_content)
        return d["sensitivity_level"], d["pattern_detected"]
