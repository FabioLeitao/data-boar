"""
Tests for Markdown documentation: structure, presence of key docs, and internal links.

Encodes good-doc practice so regressions are caught (e.g. broken links, missing README).
This project has no TypeScript/TSX files; quality coverage is Python + Markdown only.
"""

import re
from pathlib import Path


def _project_root() -> Path:
    return Path(__file__).resolve().parent.parent


def _read_md(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


# --- Key documentation files exist ---


def test_readme_exists():
    """README.md must exist at project root."""
    assert (_project_root() / "README.md").is_file()


def test_usage_doc_exists():
    """docs/USAGE.md must exist (canonical usage)."""
    assert (_project_root() / "docs" / "USAGE.md").is_file()


def test_security_doc_exists():
    """SECURITY.md must exist (security and API key)."""
    assert (_project_root() / "SECURITY.md").is_file()


def test_contributing_exists():
    """CONTRIBUTING.md must exist."""
    assert (_project_root() / "CONTRIBUTING.md").is_file()


def test_compliance_frameworks_doc_exists():
    """docs/COMPLIANCE_FRAMEWORKS.md must exist (compliance samples and frameworks)."""
    assert (_project_root() / "docs" / "COMPLIANCE_FRAMEWORKS.md").is_file()


def test_compliance_samples_folder_exists():
    """docs/compliance-samples/ must exist and contain README (compliance sample configs)."""
    root = _project_root()
    folder = root / "docs" / "compliance-samples"
    assert folder.is_dir(), "docs/compliance-samples/ should exist"
    assert (folder / "README.md").is_file(), "docs/compliance-samples/README.md should exist"


def test_compliance_and_legal_doc_exists():
    """docs/COMPLIANCE_AND_LEGAL.md must exist (summary for legal and compliance teams)."""
    assert (_project_root() / "docs" / "COMPLIANCE_AND_LEGAL.md").is_file()


# --- README structure (SonarQube-style doc quality) ---


def test_readme_has_title_heading():
    """README must start with a level-1 heading."""
    path = _project_root() / "README.md"
    text = _read_md(path)
    first_line = text.lstrip().split("\n")[0] if text.strip() else ""
    assert first_line.startswith("# "), "README.md should start with # Title"


def test_readme_mentions_config_and_lgpd():
    """README should mention configuration and LGPD/compliance (key product description)."""
    text = _read_md(_project_root() / "README.md")
    assert "config" in text.lower()
    assert "lgpd" in text.lower() or "compliance" in text.lower()


# --- docs/USAGE.md structure ---


def test_usage_has_heading_structure():
    """docs/USAGE.md should have at least one top-level heading."""
    text = _read_md(_project_root() / "docs" / "USAGE.md")
    assert "# " in text


def test_usage_mentions_cli_and_api():
    """docs/USAGE should mention CLI and API (main ways to use the app)."""
    text = _read_md(_project_root() / "docs" / "USAGE.md")
    assert "cli" in text.lower() or "command" in text.lower()
    assert "api" in text.lower() or "endpoint" in text.lower()


# --- Internal relative links: same-repo links should resolve ---


def _collect_relative_links_from_md(text: str) -> list[str]:
    """Extract relative links [text](path) where path does not start with http or #."""
    pattern = re.compile(r"\[([^\]]*)\]\(([^)#]+)\)")
    links = []
    for _label, path in pattern.findall(text):
        path = path.strip()
        if path.startswith("http") or path.startswith("mailto:") or path.startswith("#"):
            continue
        if "://" in path:
            continue
        links.append(path)
    return links


def test_readme_internal_links_resolve():
    """Relative links in README.md should point to existing files (no broken links)."""
    root = _project_root()
    path = root / "README.md"
    text = _read_md(path)
    links = _collect_relative_links_from_md(text)
    broken = []
    for link in links:
        # Normalize: remove anchor
        file_part = link.split("#")[0].strip()
        if not file_part:
            continue
        target = (root / file_part).resolve()
        try:
            if not target.is_file() and not target.is_dir():
                broken.append(link)
        except OSError:
            broken.append(link)
    assert not broken, f"README.md broken relative link(s): {broken}"


def test_usage_internal_links_resolve():
    """Relative links in docs/USAGE.md should point to existing files (base dir is docs/ or repo root)."""
    root = _project_root()
    path = root / "docs" / "USAGE.md"
    text = _read_md(path)
    links = _collect_relative_links_from_md(text)
    broken = []
    for link in links:
        file_part = link.split("#")[0].strip()
        if not file_part:
            continue
        # Resolve from docs/ (e.g. SENSITIVITY_DETECTION.md) or from repo root (e.g. ../SECURITY.md)
        found = False
        for base in (root / "docs", root):
            target = (base / file_part).resolve()
            try:
                if target.is_file() or target.is_dir():
                    found = True
                    break
            except OSError:
                pass
        if not found:
            broken.append(link)
    assert not broken, f"docs/USAGE.md broken relative link(s): {broken}"


# --- Optional: key doc files are non-empty and have minimal structure ---


def test_security_has_content():
    """SECURITY.md should not be empty and mention security."""
    text = _read_md(_project_root() / "SECURITY.md")
    assert len(text.strip()) > 100
    assert "security" in text.lower() or "http" in text.lower() or "header" in text.lower()
