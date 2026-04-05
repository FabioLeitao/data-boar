import json
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent
SCHEMA_PATH = (
    REPO_ROOT
    / "docs"
    / "ops"
    / "schemas"
    / "quasi-identification-risk-record.schema.json"
)
EXAMPLE_PATH = (
    REPO_ROOT
    / "docs"
    / "ops"
    / "schemas"
    / "quasi-identification-risk-record.example.json"
)


def _load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def test_quasi_identification_contract_files_exist() -> None:
    assert SCHEMA_PATH.exists(), f"Missing schema file: {SCHEMA_PATH}"
    assert EXAMPLE_PATH.exists(), f"Missing example file: {EXAMPLE_PATH}"


def test_quasi_identification_example_matches_required_fields() -> None:
    schema = _load_json(SCHEMA_PATH)
    example = _load_json(EXAMPLE_PATH)

    required = set(schema.get("required", []))
    assert required, "Schema must define required fields"
    assert required.issubset(set(example.keys())), (
        "Example JSON must include all schema required fields"
    )


def test_quasi_identification_labels_and_scores_are_coherent() -> None:
    example = _load_json(EXAMPLE_PATH)

    risk_score = example["risk_score"]
    confidence_score = example["confidence_score"]
    risk_label = example["risk_label"]
    confidence_label = example["confidence_label"]

    assert 0 <= risk_score <= 100
    assert 0 <= confidence_score <= 100

    expected_risk = (
        "LOW" if risk_score < 35 else "MEDIUM" if risk_score < 65 else "HIGH"
    )
    expected_confidence = (
        "LOW"
        if confidence_score < 40
        else "MEDIUM"
        if confidence_score < 70
        else "HIGH"
    )

    assert risk_label == expected_risk
    assert confidence_label == expected_confidence
