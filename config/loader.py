"""
Unified configuration loader for the LGPD/GDPR/CCPA audit application.
Loads YAML or JSON config; validates required keys; returns normalized dict.
Used by both CLI (main.py) and API.
"""
from pathlib import Path
from typing import Any

import yaml

# Optional JSON support without requiring top-level json for YAML-first flow
try:
    import json
except ImportError:
    json = None


def load_config(path: str | Path) -> dict[str, Any]:
    """
    Load configuration from a YAML or JSON file.
    Supports unified schema: targets[], file_scan, report, api, ml_patterns_file, regex_overrides_file.
    """
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"Config file not found: {path}")

    raw = path.read_text(encoding="utf-8")
    suffix = path.suffix.lower()

    if suffix in (".yaml", ".yml"):
        data = yaml.safe_load(raw)
    elif suffix == ".json":
        if json is None:
            raise RuntimeError("JSON config requires stdlib json")
        data = json.loads(raw)
    else:
        raise ValueError(f"Unsupported config format: {suffix}. Use .yaml or .json")

    if not isinstance(data, dict):
        raise ValueError("Config root must be a dict")

    return normalize_config(data)


def normalize_config(data: dict[str, Any]) -> dict[str, Any]:
    """
    Normalize config to unified schema. Accepts legacy shapes (e.g. databases[] from config.json).
    """
    out: dict[str, Any] = {}

    # Targets: prefer 'targets'; fallback: build from 'databases' + file_scan
    if "targets" in data:
        out["targets"] = list(data["targets"])
    else:
        out["targets"] = []
        for db in data.get("databases", []):
            out["targets"].append({
                "name": db.get("name", "unknown"),
                "type": "database",
                "driver": db.get("driver", "postgresql+psycopg2"),
                "host": db.get("host", "localhost"),
                "port": int(db.get("port", 5432)),
                "user": db.get("user", ""),
                "pass": db.get("password", db.get("pass", "")),
                "database": db.get("database", ""),
            })
        fs = data.get("file_scan", {})
        for directory in fs.get("directories", []):
            out["targets"].append({
                "name": Path(directory).name or "filesystem",
                "type": "filesystem",
                "path": directory,
                "recursive": fs.get("recursive", True),
            })

    # File scan defaults (for filesystem targets that don't override)
    out["file_scan"] = {
        "extensions": data.get("file_scan", {}).get("extensions", [
            ".txt", ".csv", ".pdf", ".doc", ".docx", ".odt", ".xls", ".xlsx", ".sqlite", ".json"
        ]),
        "recursive": data.get("file_scan", {}).get("recursive", True),
    }
    # Normalize extensions to list of suffixes (e.g. "*.pdf" -> ".pdf")
    exts = out["file_scan"]["extensions"]
    out["file_scan"]["extensions"] = [
        e if e.startswith(".") else f".{e.lstrip('*')}" for e in exts
    ]

    # Report
    out["report"] = data.get("report", {})
    if "output_dir" not in out["report"]:
        out["report"]["output_dir"] = "."

    # API
    out["api"] = data.get("api", {})
    if "port" not in out["api"]:
        out["api"]["port"] = 8088

    # Optional external pattern files
    out["ml_patterns_file"] = data.get("ml_patterns_file") or ""
    out["regex_overrides_file"] = data.get("regex_overrides_file") or ""

    # Parallel/sequential
    out["scan"] = data.get("scan", {})
    if "max_workers" not in out["scan"]:
        out["scan"]["max_workers"] = 1  # 1 = sequential; >1 = parallel

    # SQLite path for audit results
    out["sqlite_path"] = data.get("sqlite_path", "audit_results.db")

    return out
