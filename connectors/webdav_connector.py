"""
WebDAV connector: connect to WebDAV server by URL (FQDN or IP), list files, download to temp,
run same text extraction and sensitivity detection as filesystem.
Requires optional dependency: pip install webdavclient3 (or uv pip install -e ".[shares]").
"""

import os
import tempfile
from pathlib import Path
from typing import Any

from core.connector_registry import register
from core.archives import (
    default_compressed_extensions,
    is_supported_archive,
    normalize_compressed_extensions,
)

from connectors.filesystem_connector import (
    SUPPORTED_EXTENSIONS,
    _read_text_sample,
    _scan_sqlite_file_as_db,
    scan_archive_at_path,
)

try:
    from webdav3.client import Client as WebDAVClient

    _WEBDAV_AVAILABLE = True
except ImportError:
    _WEBDAV_AVAILABLE = False
    WebDAVClient = None

SQLITE_EXTENSIONS = {".sqlite", ".sqlite3", ".db"}


def _normalize_extensions(extensions: Any) -> set[str]:
    if not extensions:
        return set(SUPPORTED_EXTENSIONS)
    exts = list(extensions) if isinstance(extensions, (list, set)) else [extensions]
    use_all = any(str(x).strip().lower() in ("*", "all", ".*") for x in exts)
    if use_all:
        return set(SUPPORTED_EXTENSIONS)
    return {e if e.startswith(".") else f".{e.lstrip('*')}" for e in exts}


def _list_webdav_recursive(client: Any, path: str) -> list[str]:
    """Return list of remote file paths (relative)."""
    out = []
    try:
        items = client.list(path, get_info=True)
    except Exception:
        return out
    if not items:
        return out
    for item in items:
        if isinstance(item, dict):
            name = (item.get("name") or item.get("href", "")).strip("/")
            if not name:
                continue
            rel = (path + "/" + name).strip("/") if path else name
            content_length = item.get("content_length")
            is_file = content_length is not None and str(content_length).isdigit()
            if is_file:
                out.append(rel)
            else:
                out.extend(_list_webdav_recursive(client, rel))
        else:
            name = str(item).strip("/")
            if not name:
                continue
            rel = (path + "/" + name).strip("/") if path else name
            if rel.endswith("/"):
                rel = rel.rstrip("/")
                out.extend(_list_webdav_recursive(client, rel))
            else:
                out.append(rel)
    return out


class WebDAVConnector:
    """
    Connect to WebDAV server (base_url = FQDN or IP with optional path). Credentials: user, password.
    List files recursively, download to temp, run filesystem-style text extraction and scanner, save findings.
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
        fs_opts = target_config.get("file_scan") or {}
        self.scan_compressed = bool(fs_opts.get("scan_compressed"))
        self.max_inner_size = fs_opts.get("max_inner_size")
        self.compressed_extensions = normalize_compressed_extensions(
            fs_opts.get("compressed_extensions") or default_compressed_extensions()
        )

    def run(self) -> None:
        if not _WEBDAV_AVAILABLE:
            self.db_manager.save_failure(
                self.config.get("name", "WebDAV"),
                "error",
                'webdavclient3 not installed. Install with: pip install webdavclient3 or uv pip install -e ".[shares]"',
            )
            return
        target_name = self.config.get("name", "WebDAV")
        base_url = (
            self.config.get("base_url")
            or self.config.get("url")
            or self.config.get("host", "")
        ).rstrip("/")
        if not base_url:
            self.db_manager.save_failure(
                target_name, "error", "Missing base_url or url (e.g. https://host/path)"
            )
            return
        user = self.config.get("user", self.config.get("username", ""))
        password = self.config.get("pass", self.config.get("password", ""))
        path_in_share = (self.config.get("path", "") or "").strip("/")
        recursive = self.config.get("recursive", True)
        options = {
            "webdav_hostname": base_url,
            "webdav_login": user,
            "webdav_password": password,
        }
        if self.config.get("verify_ssl") is False:
            options["webdav_verify"] = False
        try:
            client = WebDAVClient(options)
        except Exception as e:
            self.db_manager.save_failure(target_name, "error", str(e))
            return
        if path_in_share:
            list_path = path_in_share
        else:
            list_path = ""
        try:
            if recursive:
                files = _list_webdav_recursive(client, list_path)
            else:
                items = client.list(list_path, get_info=True)
                files = []
                for item in items:
                    if isinstance(item, dict):
                        cl = item.get("content_length")
                        if cl is not None and str(cl).isdigit():
                            name = (item.get("name") or item.get("href", "")).strip("/")
                            if name:
                                files.append(name)
                    elif isinstance(item, str) and item.strip("/"):
                        files.append(item.strip("/"))
        except Exception as e:
            self.db_manager.save_failure(target_name, "unreachable", str(e))
            return
        for rel_path in files:
            name = rel_path.split("/")[-1] if "/" in rel_path else rel_path
            ext = Path(name).suffix.lower()
            if ext not in self.extensions and not (
                self.scan_compressed and ext in self.compressed_extensions
            ):
                continue
            remote = rel_path if not list_path else f"{list_path}/{rel_path}"
            with tempfile.NamedTemporaryFile(suffix=ext, delete=False) as tmp:
                temp_path = tmp.name
            try:
                client.download(remote, temp_path)
            except Exception as e:
                self.db_manager.save_failure(
                    target_name, "permission_denied", f"{remote}: {e}"
                )
                try:
                    os.unlink(temp_path)
                except Exception:
                    pass
                continue
            try:
                if (
                    self.scan_compressed
                    and ext in self.compressed_extensions
                    and is_supported_archive(
                        Path(temp_path), exts=self.compressed_extensions
                    )
                ):
                    scan_archive_at_path(
                        archive_path=Path(temp_path),
                        archive_display_name=name,
                        target_name=target_name,
                        path_display=remote,
                        scanner=self.scanner,
                        db_manager=self.db_manager,
                        extensions=self.extensions,
                        max_inner_size=self.max_inner_size,
                        file_passwords=self.file_passwords,
                        sample_limit=self.sample_limit,
                    )
                elif self.scan_sqlite_as_db and ext in SQLITE_EXTENSIONS:
                    for finding in _scan_sqlite_file_as_db(
                        Path(temp_path), self.scanner, self.sample_limit
                    ):
                        self.db_manager.save_finding(
                            "filesystem",
                            target_name=target_name,
                            path=remote,
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
                    res = self.scanner.scan_file_content(text, Path(remote))
                    if res is not None:
                        self.db_manager.save_finding(
                            "filesystem",
                            target_name=target_name,
                            path=remote,
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


if _WEBDAV_AVAILABLE:
    register("webdav", WebDAVConnector, ["name", "base_url"])
