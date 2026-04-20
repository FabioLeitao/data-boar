"""
Application about information (name, version, author, license) for reports, API and UI.
Single source of truth aligned with LICENSE and README in the repository.
"""

from pathlib import Path


def _version_string() -> str:
    """
    Prefer the literal `version` in `pyproject.toml` when the repo layout is present so
    pre-release suffixes (e.g. `-beta`) match docs/README; `importlib.metadata` normalizes
    PEP 440 (e.g. to `1.7.1b0`), which is correct for packaging but confusing in About/UX.
    """
    root = Path(__file__).resolve().parents[1]
    pyproject = root / "pyproject.toml"
    if pyproject.is_file():
        try:
            import tomllib

            with pyproject.open("rb") as f:
                data = tomllib.load(f)
            return str(data["project"]["version"])
        except Exception:
            pass
    try:
        from importlib.metadata import version

        return version("data-boar")
    except Exception:
        return "1.7.1-beta"


def get_about_info() -> dict:
    """
    Return application name, version, author and license (same as LICENSE and README).
    Used by the API /about page, Excel report "Report info" sheet, heatmap image footer,
    and dashboard/reports web pages.
    """
    ver = _version_string()
    return {
        "name": "Data Boar",
        "version": ver,
        # Note: the template already prints `about.name` before `about.description`,
        # so `description` must not repeat the product name.
        "description": "Audits personal and sensitive data across databases and filesystems, aligned with LGPD, GDPR, CCPA, HIPAA, and GLBA.",
        "author": "Fabio Leitao",
        "license": "BSD 3-Clause License",
        "license_url": "https://opensource.org/licenses/BSD-3-Clause",
        "copyright": "Copyright (c) 2025, Fabio Leitao",
    }
