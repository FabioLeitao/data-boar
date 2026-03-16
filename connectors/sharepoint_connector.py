"""
SharePoint connector: connect to SharePoint (on-prem or URL) by site_url (FQDN), list files in a folder,
download to temp, run same text extraction and sensitivity detection as filesystem.
Uses REST API with NTLM or basic auth. Requires optional: requests_ntlm (or uv pip install -e ".[shares]").
"""

import os
import tempfile
from pathlib import Path
from typing import Any

from core.connector_registry import register

from connectors.filesystem_connector import (
    SUPPORTED_EXTENSIONS,
    _read_text_sample,
    _scan_sqlite_file_as_db,
)

try:
    import requests
    from requests_ntlm import HttpNtlmAuth

    _REQUESTS_NTLM_AVAILABLE = True
except ImportError:
    _REQUESTS_NTLM_AVAILABLE = False
    requests = None
    HttpNtlmAuth = None

SQLITE_EXTENSIONS = {".sqlite", ".sqlite3", ".db"}


def _normalize_extensions(extensions: Any) -> set[str]:
    if not extensions:
        return set(SUPPORTED_EXTENSIONS)
    exts = list(extensions) if isinstance(extensions, (list, set)) else [extensions]
    use_all = any(str(x).strip().lower() in ("*", "all", ".*") for x in exts)
    if use_all:
        return set(SUPPORTED_EXTENSIONS)
    return {e if e.startswith(".") else f".{e.lstrip('*')}" for e in exts}


class SharePointConnector:
    """
    Connect to SharePoint site (site_url = FQDN or host with path). Credentials: user, password; auth NTLM or basic.
    List files in folder (path_in_site), download via REST GetFileByServerRelativeUrl/.../$value, scan, save findings.
    """

    def __init__(
        self,
        target_config: dict[str, Any],
        scanner: Any,
        db_manager: Any,
        extensions: set[str] | list[str] | None = None,
        scan_sqlite_as_db: bool = True,
        sample_limit: int = 5,
        file_passwords: dict[str, str] | None = None,
    ):
        self.config = target_config
        self.scanner = scanner
        self.db_manager = db_manager
        self.scan_sqlite_as_db = scan_sqlite_as_db
        self.sample_limit = sample_limit
        self.extensions = _normalize_extensions(extensions)
        self.file_passwords = file_passwords or {}

    def run(self) -> None:
        if not _REQUESTS_NTLM_AVAILABLE:
            self.db_manager.save_failure(
                self.config.get("name", "SharePoint"),
                "error",
                'requests and requests_ntlm required. Install with: pip install requests requests_ntlm or uv pip install -e ".[shares]"',
            )
            return
        target_name = self.config.get("name", "SharePoint")
        site_url = (
            self.config.get("site_url")
            or self.config.get("base_url")
            or self.config.get("url", "")
        ).rstrip("/")
        if not site_url:
            self.db_manager.save_failure(
                target_name,
                "error",
                "Missing site_url (e.g. https://host/sites/sitename)",
            )
            return
        user = self.config.get("user", self.config.get("username", ""))
        password = self.config.get("pass", self.config.get("password", ""))
        path_in_site = (
            self.config.get("path", "")
            or self.config.get("path_in_site", "Shared Documents")
        ).strip("/")
        use_ntlm = self.config.get("auth", {}).get("type", "ntlm").lower() in (
            "ntlm",
            "",
        )
        verify_ssl = self.config.get("verify_ssl", True)
        session = requests.Session()
        session.verify = verify_ssl
        if use_ntlm and user and password:
            session.auth = HttpNtlmAuth(user, password)
        elif user and password:
            session.auth = (user, password)
        session.headers["Accept"] = "application/json;odata=verbose"
        list_files_url = (
            f"{site_url}/_api/web/GetFolderByServerRelativeUrl('{path_in_site}')/Files"
        )
        try:
            r = session.get(list_files_url)
            r.raise_for_status()
            data = r.json()
        except Exception as e:
            self.db_manager.save_failure(target_name, "unreachable", str(e))
            return
        results = data.get("d", {}).get("results", data.get("results", []))
        if not results:
            return
        for item in results:
            name = item.get("Name", item.get("name", ""))
            if not name:
                continue
            ext = Path(name).suffix.lower()
            if ext not in self.extensions:
                continue
            server_relative_url = item.get(
                "ServerRelativeUrl", item.get("serverRelativeUrl", "")
            )
            if not server_relative_url:
                server_relative_url = f"/{path_in_site}/{name}".replace("//", "/")
            file_value_url = f"{site_url}/_api/web/GetFileByServerRelativeUrl('{server_relative_url}')/$value"
            try:
                r2 = session.get(file_value_url)
                r2.raise_for_status()
                content = r2.content
            except Exception as e:
                self.db_manager.save_failure(
                    target_name, "permission_denied", f"{name}: {e}"
                )
                continue
            with tempfile.NamedTemporaryFile(suffix=ext, delete=False) as tmp:
                tmp.write(content)
                temp_path = tmp.name
            try:
                if self.scan_sqlite_as_db and ext in SQLITE_EXTENSIONS:
                    for finding in _scan_sqlite_file_as_db(
                        Path(temp_path), self.scanner, self.sample_limit
                    ):
                        self.db_manager.save_finding(
                            "filesystem",
                            target_name=target_name,
                            path=server_relative_url,
                            file_name=finding["file_name"],
                            data_type=finding["data_type"],
                            sensitivity_level=finding["sensitivity_level"],
                            pattern_detected=finding["pattern_detected"],
                            norm_tag=finding["norm_tag"],
                            ml_confidence=finding["ml_confidence"],
                        )
                else:
                    text = _read_text_sample(
                        Path(temp_path), ext, self.sample_limit, self.file_passwords
                    )
                    res = self.scanner.scan_file_content(text, Path(name))
                    if res is not None:
                        self.db_manager.save_finding(
                            "filesystem",
                            target_name=target_name,
                            path=server_relative_url,
                            file_name=name,
                            data_type=ext.replace(".", "").upper(),
                            sensitivity_level=res["sensitivity_level"],
                            pattern_detected=res["pattern_detected"],
                            norm_tag=res.get("norm_tag", ""),
                            ml_confidence=res.get("ml_confidence", 0),
                        )
            finally:
                try:
                    os.unlink(temp_path)
                except Exception:
                    pass


if _REQUESTS_NTLM_AVAILABLE:
    register("sharepoint", SharePointConnector, ["name", "site_url"])
