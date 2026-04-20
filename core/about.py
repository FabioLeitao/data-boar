"""
Application about information (name, version, author, license) for reports, API and UI.
Single source of truth aligned with LICENSE and README in the repository.
"""


def get_about_info() -> dict:
    """
    Return application name, version, author and license (same as LICENSE and README).
    Used by the API /about page, Excel report "Report info" sheet, heatmap image footer,
    and dashboard/reports web pages.
    """
    try:
        from importlib.metadata import version

        ver = version("data-boar")
    except Exception:
        ver = "1.7.1"
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
