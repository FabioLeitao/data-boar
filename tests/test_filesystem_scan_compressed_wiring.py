import zipfile
from pathlib import Path

import pytest

from connectors.filesystem_connector import FilesystemConnector
from core.scanner import DataScanner

try:
    import py7zr  # noqa: F401

    HAS_PY7ZR = True
except ImportError:
    HAS_PY7ZR = False


class _DummyDB:
    def __init__(self) -> None:
        self.failures: list[tuple[str, str, str]] = []
        self.findings: list[dict] = []

    def save_failure(self, target_name: str, reason: str, details: str) -> None:
        self.failures.append((target_name, reason, details))

    def save_finding(self, *args, **kwargs) -> None:
        self.findings.append(kwargs)


def test_scan_compressed_off_does_not_scan_inside_archives(tmp_path):
    root = tmp_path / "root"
    root.mkdir()
    zip_path = root / "data.zip"
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("inner.txt", "CPF 123.456.789-00")

    db = _DummyDB()
    scanner = DataScanner()

    target = {"name": "FS", "type": "filesystem", "path": str(root), "recursive": True}
    connector = FilesystemConnector(
        target,
        scanner,
        db,
        extensions=[".zip"],
        scan_sqlite_as_db=False,
        sample_limit=5000,
        file_passwords={},
    )
    connector.run()

    # With scan_compressed False, we do not open the zip; no inner findings.
    inner_findings = [f for f in db.findings if "|" in f.get("file_name", "")]
    assert len(inner_findings) == 0


def test_scan_compressed_on_scans_inside_zip_and_reports_findings(tmp_path):
    root = tmp_path / "root"
    root.mkdir()
    zip_path = root / "data.zip"
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("inner.txt", "Contact: CPF 123.456.789-00 and email a@b.com")

    db = _DummyDB()
    scanner = DataScanner()

    target = {
        "name": "FS",
        "type": "filesystem",
        "path": str(root),
        "recursive": True,
        "file_scan": {
            "scan_compressed": True,
            "compressed_extensions": [".zip"],
        },
    }
    connector = FilesystemConnector(
        target,
        scanner,
        db,
        extensions=[".zip", ".txt"],
        scan_sqlite_as_db=False,
        sample_limit=5000,
        file_passwords={},
    )
    connector.run()

    inner_findings = [f for f in db.findings if "|" in f.get("file_name", "")]
    assert len(inner_findings) >= 1
    assert any("data.zip|" in f.get("file_name", "") for f in inner_findings)


def test_scan_compressed_sample_zip_in_data_dir():
    """Use the real sample under tests/data/compressed to validate Phase 4."""
    sample_dir = Path(__file__).resolve().parent / "data" / "compressed"
    sample_zip = sample_dir / "sample1.zip"
    if not sample_zip.exists():
        return  # skip if samples not present

    db = _DummyDB()
    scanner = DataScanner()

    target = {
        "name": "FS",
        "type": "filesystem",
        "path": str(sample_dir),
        "recursive": False,
        "file_scan": {
            "scan_compressed": True,
            "compressed_extensions": [".zip"],
        },
    }
    connector = FilesystemConnector(
        target,
        scanner,
        db,
        extensions=[".zip", ".txt", ".yaml", ".pdf"],
        scan_sqlite_as_db=False,
        sample_limit=10000,
        file_passwords={},
    )
    connector.run()

    inner_findings = [f for f in db.findings if "|" in f.get("file_name", "")]
    assert len(inner_findings) >= 1, (
        "expected at least one finding from inside sample1.zip"
    )


def test_7z_archive_handling_with_or_without_compressed_extra():
    """With [compressed] extra (py7zr) we scan .7z; without it we record archive_unsupported."""
    sample_dir = Path(__file__).resolve().parent / "data" / "compressed"
    sample_7z = sample_dir / "sample2.7z"
    if not sample_7z.exists():
        pytest.skip("tests/data/compressed/sample2.7z not present")

    db = _DummyDB()
    scanner = DataScanner()
    target = {
        "name": "FS",
        "type": "filesystem",
        "path": str(sample_dir),
        "recursive": False,
        "file_scan": {
            "scan_compressed": True,
            "compressed_extensions": [".7z", ".zip"],
        },
    }
    connector = FilesystemConnector(
        target,
        scanner,
        db,
        extensions=[".7z", ".txt", ".yaml"],
        scan_sqlite_as_db=False,
        sample_limit=10000,
        file_passwords={},
    )
    connector.run()

    unsupported_7z = [
        d
        for _, reason, d in db.failures
        if reason == "archive_unsupported" and d and "sample2.7z" in d
    ]
    if HAS_PY7ZR:
        assert len(unsupported_7z) == 0, "with py7zr installed, .7z should be opened"
    else:
        assert len(unsupported_7z) >= 1, (
            "without py7zr, .7z should yield archive_unsupported"
        )
