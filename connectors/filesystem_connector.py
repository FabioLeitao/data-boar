"""
Filesystem connector: recursive walk, permission check before read, extensions filter,
extract text (pypdf, docx, openpyxl, etc.), run detector, save filesystem_findings only.
On permission error: save_failure with reason permission_denied.
Scans all compatible/supported file types by extension; unknown types get path/name-only analysis.
"""
import os
import zipfile
from pathlib import Path
from typing import Any

from core.connector_registry import register

# Plain text and markup (read as text with errors=replace)
_TEXT_EXTENSIONS = {
    ".txt", ".csv", ".tsv", ".tab", ".json", ".jsonl", ".ndjson", ".xml", ".html", ".htm", ".xhtml",
    ".md", ".markdown", ".rst", ".log", ".ini", ".cfg", ".conf", ".config",
    ".yml", ".yaml", ".toml", ".env", ".properties", ".sql", ".sh", ".bat", ".ps1",
    ".py", ".js", ".ts", ".mjs", ".cjs", ".vue", ".rb", ".php", ".pl", ".pm",
    ".java", ".kt", ".kts", ".scala", ".go", ".rs", ".c", ".h", ".cpp", ".hpp",
    ".cs", ".vb", ".r", ".R", ".graphql", ".gql", ".tex", ".bib",
    ".rtf", ".rtfd", ".rdf", ".owl", ".ttl", ".n3", ".svg", ".svgz", ".diff", ".patch",
}

# Binary/document formats with dedicated extractors
_DOCUMENT_EXTENSIONS = {
    ".pdf", ".doc", ".docx", ".odt", ".ods", ".odp", ".odm", ".odg", ".odf", ".odb",
    ".xls", ".xlsx", ".xlsm", ".xlsb", ".ppt", ".pptx", ".pps", ".ppsx",
    ".msg", ".eml", ".mht", ".mhtml",
}

# Database / structured (sample or path-only)
_DATA_EXTENSIONS = {".sqlite", ".sqlite3", ".db", ".accdb", ".mdb"}

# Supported extensions = all of the above (recursive scan uses this when config does not override)
SUPPORTED_EXTENSIONS = _TEXT_EXTENSIONS | _DOCUMENT_EXTENSIONS | _DATA_EXTENSIONS

# Optional: extension -> MIME (for reference; scanning is extension-based)
EXTENSION_MIME = {
    ".txt": "text/plain", ".csv": "text/csv", ".json": "application/json",
    ".pdf": "application/pdf", ".doc": "application/msword", ".docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    ".xls": "application/vnd.ms-excel", ".xlsx": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    ".odt": "application/vnd.oasis.opendocument.text", ".ods": "application/vnd.oasis.opendocument.spreadsheet", ".odp": "application/vnd.oasis.opendocument.presentation",
    ".xml": "application/xml", ".html": "text/html", ".htm": "text/html",
    ".eml": "message/rfc822", ".msg": "application/vnd.ms-outlook",
    ".pptx": "application/vnd.openxmlformats-officedocument.presentationml.presentation",
    ".rtf": "application/rtf", ".sqlite": "application/vnd.sqlite3", ".yml": "text/yaml", ".yaml": "text/yaml",
}


def _read_text_sample(path: Path, ext: str, max_chars: int = 10000) -> str:
    """Extract text from file for sensitivity scan; return empty on error. No content stored after return."""
    try:
        # Plain text and markup: read as text
        if ext in _TEXT_EXTENSIONS:
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
            # Legacy .doc: binary format; path/name still analyzed
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
        if ext == ".ods":
            try:
                from odf.opendocument import load
                from odf import text as odf_text, teletype
                doc = load(path)
                parts = [teletype.extractText(el) for el in doc.getElementsByType(odf_text.P)]
                return " ".join(parts)[:max_chars]
            except Exception:
                return ""
        if ext == ".odp":
            try:
                from odf.opendocument import load
                from odf import text as odf_text, teletype
                doc = load(path)
                parts = [teletype.extractText(el) for el in doc.getElementsByType(odf_text.P)]
                return " ".join(parts)[:max_chars]
            except Exception:
                return ""
        if ext in (".xlsx", ".xls", ".xlsm"):
            import pandas as pd
            df = pd.read_excel(path, nrows=20, header=None)
            return " ".join(df.astype(str).stack().tolist())[:max_chars]
        if ext == ".xlsb":
            try:
                import pandas as pd
                df = pd.read_excel(path, engine="pyxlsb", nrows=20, header=None)
                return " ".join(df.astype(str).stack().tolist())[:max_chars]
            except Exception:
                return ""
        if ext == ".pptx":
            try:
                with zipfile.ZipFile(path, "r") as z:
                    parts = []
                    for name in z.namelist():
                        if name.startswith("ppt/slides/slide") and name.endswith(".xml"):
                            data = z.read(name).decode("utf-8", errors="replace")
                            import re
                            parts.append(re.sub(r"<[^>]+>", " ", data))
                    return " ".join(parts)[:max_chars]
            except Exception:
                return ""
        if ext == ".msg":
            try:
                import extract_msg
                msg = extract_msg.Message(path)
                body = (msg.body or "") + " " + (msg.subject or "")
                for att in (msg.attachments or [])[:3]:
                    body += " " + (getattr(att, "longFilename", "") or "")
                msg.close()
                return body[:max_chars]
            except Exception:
                return ""
        if ext in (".eml", ".mht", ".mhtml"):
            with open(path, "r", encoding="utf-8", errors="replace") as f:
                return f.read(max_chars)
        # .sqlite, .db, .accdb, .mdb: path/name only for text; SQLite files scanned as DB in run() when scan_sqlite_as_db
        return ""
    except Exception:
        return ""


def _scan_sqlite_file_as_db(
    file_path: Path,
    scanner: Any,
    sample_limit: int = 5,
) -> list[dict[str, Any]]:
    """
    Open a .sqlite/.sqlite3/.db file with SQLAlchemy, discover tables/columns, sample and detect.
    Returns list of findings (dicts for save_finding source_type=filesystem); file_name encodes table.column.
    No raw content stored.
    """
    from sqlalchemy import create_engine, inspect, text
    findings = []
    try:
        engine = create_engine(f"sqlite:///{file_path.resolve()}", pool_pre_ping=True)
    except Exception:
        return []
    try:
        inspector = inspect(engine)
        with engine.connect() as conn:
            for table in inspector.get_table_names():
                try:
                    columns = inspector.get_columns(table)
                except Exception:
                    columns = []
                for col in columns:
                    cname = col["name"]
                    ctype = str(col["type"])
                    sample_parts = []
                    try:
                        safe_table = table.replace('"', '""')
                        safe_col = cname.replace('"', '""')
                        row = conn.execute(text(f'SELECT "{safe_col}" FROM "{safe_table}" LIMIT {sample_limit}'))
                        for r in row:
                            if r[0] is not None:
                                sample_parts.append(str(r[0])[:200])
                    except Exception:
                        pass
                    sample = " ".join(sample_parts)
                    res = scanner.scan_column(cname, sample)
                    if res["sensitivity_level"] == "LOW":
                        continue
                    findings.append({
                        "path": str(file_path.parent),
                        "file_name": f"{file_path.name} | {table}.{cname}",
                        "data_type": ctype,
                        "sensitivity_level": res["sensitivity_level"],
                        "pattern_detected": res["pattern_detected"],
                        "norm_tag": res.get("norm_tag", ""),
                        "ml_confidence": res.get("ml_confidence", 0),
                    })
    except Exception:
        pass
    finally:
        engine.dispose()
    return findings


class FilesystemConnector:
    """
    Scan a directory recursively (or not), filter by extensions, check os.access(R_OK) before read,
    run sensitivity detection, save filesystem findings. Implements run() for engine.
    """

    SQLITE_EXTENSIONS = {".sqlite", ".sqlite3", ".db"}

    def __init__(
        self,
        target_config: dict[str, Any],
        scanner: Any,
        db_manager: Any,
        extensions: set[str] | list[str] | None = None,
        scan_sqlite_as_db: bool = True,
        sample_limit: int = 5,
    ):
        self.config = target_config
        self.scanner = scanner
        self.db_manager = db_manager
        self.scan_sqlite_as_db = scan_sqlite_as_db
        self.sample_limit = sample_limit
        # "*" or "all" in list => use full SUPPORTED_EXTENSIONS; else use provided list or default
        use_all = False
        if extensions:
            exts = list(extensions) if isinstance(extensions, (list, set)) else [extensions]
            use_all = any(str(x).strip().lower() in ("*", "all", ".*") for x in exts)
        self.extensions = SUPPORTED_EXTENSIONS if use_all else set(extensions or SUPPORTED_EXTENSIONS)
        # Normalize to lowercase with dot
        self.extensions = {e if e.startswith(".") else f".{e.lstrip('*')}" for e in self.extensions}

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
            ext = file_path.suffix.lower()
            # 2.6: treat .sqlite/.sqlite3/.db as DBs when scan_sqlite_as_db is True
            if self.scan_sqlite_as_db and ext in self.SQLITE_EXTENSIONS:
                for finding in _scan_sqlite_file_as_db(file_path, self.scanner, self.sample_limit):
                    self.db_manager.save_finding(
                        source_type="filesystem",
                        target_name=target_name,
                        path=finding["path"],
                        file_name=finding["file_name"],
                        data_type=finding["data_type"],
                        sensitivity_level=finding["sensitivity_level"],
                        pattern_detected=finding["pattern_detected"],
                        norm_tag=finding["norm_tag"],
                        ml_confidence=finding["ml_confidence"],
                    )
                    try:
                        from utils.logger import log_finding
                        log_finding("filesystem", target_name, finding["file_name"], finding["sensitivity_level"], finding["pattern_detected"])
                    except Exception:
                        pass
                continue
            content = _read_text_sample(file_path, ext)
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
