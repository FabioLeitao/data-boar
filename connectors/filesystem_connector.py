"""
Filesystem connector: recursive walk, permission check before read, extensions filter,
extract text (pypdf, docx, openpyxl, etc.), run detector, save filesystem_findings only.
On permission error: save_failure with reason permission_denied.
"""
import os
from pathlib import Path
from typing import Any

from core.connector_registry import register

# Supported extensions for content extraction
SUPPORTED_EXTENSIONS = {".txt", ".csv", ".pdf", ".doc", ".docx", ".odt", ".xls", ".xlsx", ".sqlite", ".json"}


def _read_text_sample(path: Path, ext: str, max_chars: int = 10000) -> str:
    """Extract text from file for sensitivity scan; return empty on error. No content stored after return."""
    try:
        if ext in (".txt", ".csv", ".json"):
            with open(path, "r", encoding="utf-8", errors="replace") as f:
                return f.read(max_chars)
        if ext == ".pdf":
            from pypdf import PdfReader
            reader = PdfReader(path)
            return " ".join(p.extract_text() or "" for p in reader.pages[:5])[:max_chars]
        if ext == ".docx":
            from docx import Document
            doc = Document(path)
            return " ".join(p.text for p in doc.paragraphs[:50])[:max_chars]
        if ext == ".doc":
            # Legacy .doc: optional; fallback to binary skip or use antiword/optional lib
            return ""
        if ext == ".odt":
            try:
                from odf.opendocument import load
                from odf import text as odf_text, teletype
                doc = load(path)
                parts = [teletype.extractText(el) for el in doc.getElementsByType(odf_text.P)]
                return " ".join(parts)[:max_chars]
            except Exception:
                return ""
        if ext in (".xlsx", ".xls"):
            import pandas as pd
            df = pd.read_excel(path, nrows=20, header=None)
            return " ".join(df.astype(str).values.flatten().tolist())[:max_chars]
        return ""
    except Exception:
        return ""


class FilesystemConnector:
    """
    Scan a directory recursively (or not), filter by extensions, check os.access(R_OK) before read,
    run sensitivity detection, save filesystem findings. Implements run() for engine.
    """

    def __init__(
        self,
        target_config: dict[str, Any],
        scanner: Any,
        db_manager: Any,
        extensions: set[str] | list[str] | None = None,
    ):
        self.config = target_config
        self.scanner = scanner
        self.db_manager = db_manager
        self.extensions = set(extensions or SUPPORTED_EXTENSIONS)
        # Normalize to lowercase with dot
        self.extensions = {e if e.startswith(".") else f".{e}" for e in self.extensions}

    def run(self) -> None:
        """Walk target path, check permission, read sample, detect, save_finding or save_failure."""
        target_name = self.config.get("name", "filesystem")
        root = self.config.get("path", "")
        recursive = self.config.get("recursive", True)
        path = Path(root)
        if not path.exists():
            self.db_manager.save_failure(target_name, "unreachable", f"Path does not exist: {root}")
            return
        if not path.is_dir():
            self.db_manager.save_failure(target_name, "error", "Path is not a directory")
            return
        try:
            from utils.logger import log_connection
            log_connection(target_name, "filesystem", str(path))
        except Exception:
            pass
        pattern = "**/*" if recursive else "*"
        for file_path in path.glob(pattern):
            if not file_path.is_file():
                continue
            if file_path.suffix.lower() not in self.extensions:
                continue
            if not os.access(file_path, os.R_OK):
                self.db_manager.save_failure(target_name, "permission_denied", str(file_path))
                continue
            content = _read_text_sample(file_path, file_path.suffix.lower())
            res = self.scanner.scan_file_content(content, file_path)
            if res is None:
                continue
            self.db_manager.save_finding(
                source_type="filesystem",
                target_name=target_name,
                path=str(file_path.parent),
                file_name=file_path.name,
                data_type=file_path.suffix.replace(".", "").upper(),
                sensitivity_level=res["sensitivity_level"],
                pattern_detected=res["pattern_detected"],
                norm_tag=res.get("norm_tag", ""),
                ml_confidence=res.get("ml_confidence", 0),
            )
            try:
                from utils.logger import log_finding
                log_finding("filesystem", target_name, str(file_path), res["sensitivity_level"], res["pattern_detected"])
            except Exception:
                pass


register("filesystem", FilesystemConnector, ["name", "type", "path"])
