"""
Tests for docs/compliance-samples/compliance-sample-*.yaml files.

Validates that each compliance sample YAML has the structure expected by the
detector (regex, terms) and report generator (recommendation_overrides), and
that the detector can load each sample without error.
"""
from pathlib import Path

import pytest
import yaml

# Repo root: tests/ -> parent -> parent
REPO_ROOT = Path(__file__).resolve().parent.parent
COMPLIANCE_SAMPLES_DIR = REPO_ROOT / "docs" / "compliance-samples"


def _compliance_sample_yaml_files():
    """All compliance-sample-*.yaml files in docs/compliance-samples/."""
    if not COMPLIANCE_SAMPLES_DIR.is_dir():
        return []
    return sorted(COMPLIANCE_SAMPLES_DIR.glob("compliance-sample-*.yaml"))


@pytest.fixture
def sample_files():
    """List of paths to compliance-sample-*.yaml files."""
    return _compliance_sample_yaml_files()


def test_compliance_sample_yaml_files_exist():
    """At least one compliance sample YAML exists (UK GDPR or more)."""
    files = _compliance_sample_yaml_files()
    assert len(files) >= 1, "Expected at least one docs/compliance-samples/compliance-sample-*.yaml"


def _validate_regex_section(data: dict, sample_name: str) -> None:
    """Assert regex/patterns list has items with name, pattern, norm_tag."""
    regex_items = data.get("regex") or data.get("patterns")
    if regex_items is None:
        return
    assert isinstance(regex_items, list), f"{sample_name}: regex/patterns must be a list"
    for i, item in enumerate(regex_items):
        assert isinstance(item, dict), f"{sample_name}: regex item {i} must be a dict"
        assert "name" in item and item.get("name"), f"{sample_name}: regex item {i} must have non-empty name"
        assert "pattern" in item and item.get("pattern"), f"{sample_name}: regex item {i} must have non-empty pattern"
        assert "norm_tag" in item, f"{sample_name}: regex item {i} must have norm_tag"


def _validate_terms_section(data: dict, sample_name: str) -> None:
    """Assert terms list has items with text and label."""
    terms_items = data.get("terms") or (data.get("patterns") if "regex" in data else None)
    if terms_items is None:
        return
    assert isinstance(terms_items, list), f"{sample_name}: terms must be a list"
    for i, item in enumerate(terms_items):
        assert isinstance(item, dict), f"{sample_name}: terms item {i} must be a dict"
        assert "text" in item and (item.get("text") or "").strip(), f"{sample_name}: terms item {i} must have non-empty text"
        assert "label" in item, f"{sample_name}: terms item {i} must have label"


def _validate_recommendation_overrides_section(data: dict, sample_name: str) -> None:
    """Assert recommendation_overrides list has items with required keys."""
    overrides = data.get("recommendation_overrides")
    if overrides is None:
        return
    assert isinstance(overrides, list), f"{sample_name}: recommendation_overrides must be a list"
    required_keys = ("norm_tag_pattern", "base_legal", "risk", "recommendation", "priority", "relevant_for")
    for i, item in enumerate(overrides):
        assert isinstance(item, dict), f"{sample_name}: recommendation_overrides item {i} must be a dict"
        for key in required_keys:
            assert key in item, f"{sample_name}: recommendation_overrides item {i} must have {key}"


@pytest.mark.parametrize("sample_path", _compliance_sample_yaml_files(), ids=lambda p: p.name)
def test_compliance_sample_yaml_structure(sample_path):
    """
    Each compliance-sample-*.yaml has valid structure:
    - regex (or patterns): list of { name, pattern, norm_tag }
    - terms (or patterns for ML): list of { text, label }
    - recommendation_overrides: list of { norm_tag_pattern, base_legal, risk, recommendation, priority, relevant_for }
    """
    raw = sample_path.read_text(encoding="utf-8")
    data = yaml.safe_load(raw)
    assert isinstance(data, dict), f"{sample_path.name}: root must be a YAML mapping"

    _validate_regex_section(data, sample_path.name)
    _validate_terms_section(data, sample_path.name)
    _validate_recommendation_overrides_section(data, sample_path.name)

    has_regex = (data.get("regex") or data.get("patterns")) is not None
    has_terms = data.get("terms") is not None
    has_overrides = data.get("recommendation_overrides") is not None
    assert has_regex or has_terms or has_overrides, (
        f"{sample_path.name}: must contain at least one of regex, terms, or recommendation_overrides"
    )


@pytest.mark.parametrize("sample_path", _compliance_sample_yaml_files(), ids=lambda p: p.name)
def test_compliance_sample_loadable_by_detector(sample_path):
    """Detector can load each sample as regex_overrides_file and ml_patterns_file without error."""
    from core.scanner import DataScanner

    path_str = str(sample_path.resolve())
    scanner = DataScanner(
        regex_overrides_path=path_str,
        ml_patterns_path=path_str,
    )
    # Trigger a minimal analysis to ensure loader ran (no exception)
    result = scanner.scan_column("test_column", "some sample text")
    assert "sensitivity_level" in result
    assert "norm_tag" in result
