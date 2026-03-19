"""
Unified configuration loader for the LGPD/GDPR/CCPA audit application.
Loads YAML or JSON config; validates required keys; returns normalized dict.
Used by both CLI (main.py) and API.

Encoding: config file is read with auto-detection (UTF-8, UTF-8-sig, cp1252, latin_1)
so it works in multilingual and legacy Windows environments. Pattern files
(regex_overrides_file, ml_patterns_file, dl_patterns_file) use the optional
pattern_files_encoding key (default utf-8) with errors=replace to avoid crashes.
"""

from pathlib import Path
from typing import Any

import yaml

from utils.file_encoding import read_text_auto_encoding

# Optional JSON support without requiring top-level json for YAML-first flow
try:
    import json
except ImportError:
    json = None

import os


def load_config(path: str | Path) -> dict[str, Any]:
    """
    Load configuration from a YAML or JSON file.
    Supports unified schema: targets[], file_scan, report, api, sqlite_path, scan, ml_patterns_file, dl_patterns_file, regex_overrides_file, sensitivity_detection, learned_patterns.
    """
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"Config file not found: {path}")

    raw = read_text_auto_encoding(path)
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
            out["targets"].append(
                {
                    "name": db.get("name", "unknown"),
                    "type": "database",
                    "driver": db.get("driver", "postgresql+psycopg2"),
                    "host": db.get("host", "localhost"),
                    "port": int(db.get("port", 5432)),
                    "user": db.get("user", ""),
                    "pass": db.get("password", db.get("pass", "")),
                    "database": db.get("database", ""),
                }
            )
        fs = data.get("file_scan", {})
        for directory in fs.get("directories", []):
            out["targets"].append(
                {
                    "name": Path(directory).name or "filesystem",
                    "type": "filesystem",
                    "path": directory,
                    "recursive": fs.get("recursive", True),
                }
            )

    # File scan defaults: all compatible extensions when not specified (see connectors.filesystem_connector.SUPPORTED_EXTENSIONS)
    def _normalize_file_passwords(pw: Any) -> dict[str, str]:
        """Normalize file_passwords to dict mapping extension or 'default' to password string. Used for password-protected PDF/ZIP/PPTX."""
        if not pw or not isinstance(pw, dict):
            return {}
        out: dict[str, str] = {}
        for k, v in pw.items():
            if v is None or not isinstance(v, str):
                continue
            key = (k or "").strip().lower()
            if key == "default":
                out["default"] = v
            elif key.startswith("."):
                out[key] = v
            else:
                out[f".{key}"] = v
        return out

    # Per-archive inner size cap: valid range 1 MB–500 MB; invalid/missing -> None.
    _MIN_MAX_INNER = 1_000_000
    _MAX_MAX_INNER = 500_000_000

    def _normalize_max_inner_size(val: Any) -> int | None:
        if val is None:
            return None
        try:
            n = int(val)
        except (TypeError, ValueError):
            return None
        if n < _MIN_MAX_INNER:
            return _MIN_MAX_INNER
        if n > _MAX_MAX_INNER:
            return _MAX_MAX_INNER
        return n

    _default_extensions = [
        ".txt",
        ".csv",
        ".pdf",
        ".doc",
        ".docx",
        ".odt",
        ".ods",
        ".odp",
        ".xls",
        ".xlsx",
        ".xlsm",
        ".ppt",
        ".pptx",
        ".sqlite",
        ".sqlite3",
        ".db",
        ".json",
        ".jsonl",
        ".xml",
        ".html",
        ".htm",
        ".md",
        ".yml",
        ".yaml",
        ".log",
        ".ini",
        ".cfg",
        ".conf",
        ".env",
        ".sql",
        ".rtf",
        ".eml",
        ".msg",
        ".tex",
        ".bib",
    ]
    fs_cfg = data.get("file_scan", {}) or {}
    out["file_scan"] = {
        "extensions": fs_cfg.get("extensions", _default_extensions),
        "recursive": fs_cfg.get("recursive", True),
        "scan_sqlite_as_db": fs_cfg.get("scan_sqlite_as_db", True),
        "sample_limit": fs_cfg.get("sample_limit", 5),
        # Optional: scan inside compressed files (zip, tar, gz, bz2, xz, 7z, …)
        # This flag is deliberately conservative: default False so existing configs
        # keep current behaviour until explicitly opted-in.
        "scan_compressed": bool(fs_cfg.get("scan_compressed", False)),
        # Optional: per-archive inner-bytes safety cap (bytes). Valid range 1 MB–500 MB;
        # invalid or missing -> None (connector uses default).
        "max_inner_size": _normalize_max_inner_size(
            fs_cfg.get("max_inner_size") or fs_cfg.get("scan_compressed_max_inner_size")
        ),
        # Optional: restrict which archive types to open; if omitted, engine/connector
        # will use a sensible default Tier 1 + Tier 2 list (see PLAN_COMPRESSED_FILES.md).
        "compressed_extensions": fs_cfg.get("compressed_extensions"),
        "file_passwords": _normalize_file_passwords(fs_cfg.get("file_passwords")),
        # Planned: optional content-based type detection helper (magic bytes) to
        # help with renamed/cloaked files. Currently an inert toggle; future
        # phases will wire this into filesystem/share connectors behind an opt-in flag.
        "use_content_type": bool(fs_cfg.get("use_content_type", False)),
    }
    # Normalize extensions to list of suffixes (e.g. "*.pdf" -> ".pdf")
    exts = out["file_scan"]["extensions"]
    out["file_scan"]["extensions"] = [
        e if e.startswith(".") else f".{e.lstrip('*')}" for e in exts
    ]

    # Resolve credential-from-env for targets (Phase A: secrets in env, not in config)
    for t in out.get("targets") or []:
        if not isinstance(t, dict):
            continue
        env_pass_key = (
            t.get("pass_from_env") or t.get("password_from_env") or ""
        ).strip()
        if env_pass_key:
            t["pass"] = (
                (os.environ.get(env_pass_key) or "").strip()
                or t.get("pass")
                or t.get("password")
                or ""
            )
        env_user_key = (t.get("user_from_env") or "").strip()
        if env_user_key:
            t["user"] = (
                (os.environ.get(env_user_key) or "").strip()
                or t.get("user")
                or t.get("username")
                or ""
            )
        auth = t.get("auth")
        if isinstance(auth, dict):
            token_env = (auth.get("token_from_env") or "").strip()
            if token_env:
                auth["token"] = (
                    (os.environ.get(token_env) or "").strip() or auth.get("token") or ""
                )
            cs_env = (auth.get("client_secret_from_env") or "").strip()
            if cs_env:
                auth["client_secret"] = (
                    (os.environ.get(cs_env) or "").strip()
                    or auth.get("client_secret")
                    or ""
                )
        env_cs_key = (t.get("client_secret_from_env") or "").strip()
        if env_cs_key:
            t["client_secret"] = (
                (os.environ.get(env_cs_key) or "").strip()
                or t.get("client_secret")
                or ""
            )

    # Detection: configuration toggles for detector behaviour (regex/ML/DL options)
    det_cfg = data.get("detection", {}) or {}
    # CNPJ alphanumeric: when true, the detector keeps LGPD_CNPJ_ALNUM active as a built-in pattern.
    # When false or omitted, only the legacy numeric LGPD_CNPJ pattern is used unless re-enabled via
    # regex_overrides_file. This avoids surprising behaviour changes when operators have not yet
    # reviewed or agreed with the newer format.
    out["detection"] = {
        **det_cfg,
        "cnpj_alphanumeric": bool(det_cfg.get("cnpj_alphanumeric", False)),
    }

    # Report
    out["report"] = data.get("report", {})
    if "output_dir" not in out["report"]:
        out["report"]["output_dir"] = "."
    # Optional: list of { norm_tag_pattern, base_legal, risk, recommendation, priority, relevant_for } for recommendations
    overrides = out["report"].get("recommendation_overrides")
    out["report"]["recommendation_overrides"] = (
        list(overrides) if isinstance(overrides, list) else []
    )
    if "include_executive_summary" not in out["report"]:
        out["report"]["include_executive_summary"] = False
    else:
        out["report"]["include_executive_summary"] = bool(
            out["report"]["include_executive_summary"]
        )
    if "min_sensitivity" not in out["report"]:
        out["report"]["min_sensitivity"] = "LOW"
    else:
        v = (out["report"].get("min_sensitivity") or "LOW").upper()
        out["report"]["min_sensitivity"] = (
            v if v in ("HIGH", "MEDIUM", "LOW") else "LOW"
        )

    # API
    out["api"] = data.get("api", {})
    if "port" not in out["api"]:
        out["api"]["port"] = 8088
    if "workers" not in out["api"]:
        out["api"]["workers"] = (
            1  # 1 = minimal footprint; 2+ for concurrent API traffic
        )
    # Optional API key (enterprise): when require_api_key is true, API checks X-API-Key or Authorization: Bearer
    out["api"]["require_api_key"] = bool(out["api"].get("require_api_key", False))
    out["api"]["api_key"] = (out["api"].get("api_key") or "").strip() or None
    api_key_env = (out["api"].get("api_key_from_env") or "").strip()
    if api_key_env and not out["api"]["api_key"]:
        out["api"]["api_key"] = (os.environ.get(api_key_env) or "").strip() or None
    out["api"]["api_key_from_env"] = api_key_env or None

    # Optional external pattern files (ML/DL training terms: list of { text, label } with label "sensitive"|1 or "non_sensitive"|0)
    out["ml_patterns_file"] = data.get("ml_patterns_file") or ""
    out["regex_overrides_file"] = data.get("regex_overrides_file") or ""
    out["dl_patterns_file"] = data.get("dl_patterns_file") or ""

    # Encoding for pattern files (regex_overrides_file, ml_patterns_file, dl_patterns_file). Default utf-8.
    # Use utf-8, utf-8-sig, cp1252, latin_1, or iso-8859-1 for legacy/multilingual environments.
    _enc = (
        (data.get("pattern_files_encoding") or data.get("file_encoding") or "utf-8")
        .strip()
        .lower()
    )
    out["pattern_files_encoding"] = _enc if _enc else "utf-8"

    # Inline sensitivity-detection terms (override or supplement file-based terms when provided)
    sens = data.get("sensitivity_detection") or {}
    out["sensitivity_detection"] = {
        "ml_terms": sens.get("ml_terms") or [],
        "dl_terms": sens.get("dl_terms") or [],
    }

    # Detection options (e.g. possible minor data)
    detection_cfg = data.get("detection") or {}
    minor_age = detection_cfg.get("minor_age_threshold", 18)
    try:
        minor_age_int = int(minor_age)
    except (TypeError, ValueError):
        minor_age_int = 18
    minor_full_scan_limit = detection_cfg.get("minor_full_scan_limit", 100)
    try:
        minor_full_scan_limit = max(1, int(minor_full_scan_limit))
    except (TypeError, ValueError):
        minor_full_scan_limit = 100
    agg_min = detection_cfg.get("aggregated_min_categories", 2)
    try:
        agg_min = max(1, int(agg_min))
    except (TypeError, ValueError):
        agg_min = 2
    quasi = detection_cfg.get("quasi_identifier_mapping")
    out["detection"] = {
        "minor_age_threshold": minor_age_int,
        "minor_full_scan": bool(detection_cfg.get("minor_full_scan", False)),
        "minor_full_scan_limit": minor_full_scan_limit,
        "minor_cross_reference": bool(detection_cfg.get("minor_cross_reference", True)),
        "aggregated_identification_enabled": bool(
            detection_cfg.get("aggregated_identification_enabled", True)
        ),
        "aggregated_min_categories": agg_min,
        "quasi_identifier_mapping": list(quasi) if isinstance(quasi, list) else [],
    }

    # Rate limiting / safety
    rate_cfg = data.get("rate_limit") or {}
    # Enabled default: True, but with conservative defaults so existing behaviour is effectively unchanged
    enabled_default = True
    enabled = rate_cfg.get("enabled", enabled_default)
    env_enabled = os.environ.get("RATE_LIMIT_ENABLED")
    if env_enabled is not None:
        enabled = env_enabled.strip().lower() in ("1", "true", "yes", "on")

    max_concurrent = rate_cfg.get("max_concurrent_scans", 1)
    env_max = os.environ.get("RATE_LIMIT_MAX_CONCURRENT_SCANS")
    if env_max is not None:
        try:
            max_concurrent = int(env_max)
        except ValueError:
            pass
    try:
        max_concurrent = max(1, int(max_concurrent))
    except (TypeError, ValueError):
        max_concurrent = 1

    min_interval = rate_cfg.get("min_interval_seconds", 0)
    env_min = os.environ.get("RATE_LIMIT_MIN_INTERVAL_SECONDS")
    if env_min is not None:
        try:
            min_interval = int(env_min)
        except ValueError:
            pass
    try:
        min_interval = max(0, int(min_interval))
    except (TypeError, ValueError):
        min_interval = 0

    grace = rate_cfg.get("grace_for_running_status", 0)
    env_grace = os.environ.get("RATE_LIMIT_GRACE_FOR_RUNNING_STATUS")
    if env_grace is not None:
        try:
            grace = int(env_grace)
        except ValueError:
            pass
    try:
        grace = max(0, int(grace))
    except (TypeError, ValueError):
        grace = 0

    out["rate_limit"] = {
        "enabled": bool(enabled),
        "max_concurrent_scans": max_concurrent,
        "min_interval_seconds": min_interval,
        "grace_for_running_status": grace,
    }

    # Timeouts for data source connections (global defaults; per-target overrides applied below)
    timeout_cfg = data.get("timeouts") or {}
    _connect = timeout_cfg.get("connect_seconds", 25)
    _read = timeout_cfg.get("read_seconds", 90)
    try:
        _connect = max(1, int(_connect))
    except (TypeError, ValueError):
        _connect = 25
    try:
        _read = max(1, int(_read))
    except (TypeError, ValueError):
        _read = 90
    out["timeouts"] = {"connect_seconds": _connect, "read_seconds": _read}

    # Per-target timeout overrides: merge global timeouts with optional target.connect_timeout,
    # target.read_timeout, or target.timeout (single value for both). Target overrides global when set.
    global_connect = out["timeouts"]["connect_seconds"]
    global_read = out["timeouts"]["read_seconds"]
    for t in out.get("targets") or []:
        if not isinstance(t, dict):
            continue
        target_connect = t.get("connect_timeout_seconds") or t.get("connect_timeout")
        target_read = t.get("read_timeout_seconds") or t.get("read_timeout")
        single = t.get("timeout")
        if single is not None:
            try:
                single = max(1, int(single))
            except (TypeError, ValueError):
                single = None
        if single is not None:
            if target_connect is None:
                target_connect = single
            if target_read is None:
                target_read = single
        for _name, _val in (
            ("connect_timeout_seconds", target_connect),
            ("read_timeout_seconds", target_read),
        ):
            if _val is not None:
                try:
                    _val = max(1, int(_val))
                except (TypeError, ValueError):
                    _val = (
                        global_connect
                        if _name == "connect_timeout_seconds"
                        else global_read
                    )
            else:
                _val = (
                    global_connect
                    if _name == "connect_timeout_seconds"
                    else global_read
                )
            t[_name] = _val

    # Parallel/sequential
    out["scan"] = data.get("scan", {})
    if "max_workers" not in out["scan"]:
        out["scan"]["max_workers"] = 1  # 1 = sequential; >1 = parallel
    # Clamp max_workers to a safe range to avoid accidental huge parallelism
    raw_max_workers = out["scan"].get("max_workers", 1)
    try:
        mw = int(raw_max_workers)
    except (TypeError, ValueError):
        mw = 1
    if mw < 1:
        mw = 1
    # Hard upper cap to avoid runaway parallelism from misconfiguration
    if mw > 32:
        mw = 32
    out["scan"]["max_workers"] = mw

    # SQLite path for audit results
    out["sqlite_path"] = data.get("sqlite_path", "audit_results.db")

    # Learned patterns (optional): write terms classified sensitive to a file for merging into ml_patterns_file
    out["learned_patterns"] = data.get("learned_patterns") or {}
    lp = out["learned_patterns"]
    if "enabled" not in lp:
        lp["enabled"] = False
    if "output_file" not in lp:
        lp["output_file"] = "learned_patterns.yaml"
    if "min_sensitivity" not in lp:
        lp["min_sensitivity"] = "HIGH"
    if "min_confidence" not in lp:
        lp["min_confidence"] = 70
    if "min_term_length" not in lp:
        lp["min_term_length"] = 3
    if "require_pattern" not in lp:
        lp["require_pattern"] = True
    if "append" not in lp:
        lp["append"] = True
    if "exclude_if_in_ml_patterns" not in lp:
        lp["exclude_if_in_ml_patterns"] = True

    # Optional commercial licensing (default: open — no enforcement). See docs/LICENSING_SPEC.md.
    lic = data.get("licensing") or {}
    if not isinstance(lic, dict):
        lic = {}
    mode = str(lic.get("mode", "open")).strip().lower()
    if mode not in ("open", "enforced"):
        mode = "open"
    out["licensing"] = {
        "mode": mode,
        "public_key_path": str(lic.get("public_key_path") or "").strip(),
        "license_path": str(lic.get("license_path") or "").strip(),
        "revocation_list_path": str(lic.get("revocation_list_path") or "").strip(),
        "manifest_path": str(lic.get("manifest_path") or "").strip(),
        "machine_bind_strict": bool(lic.get("machine_bind_strict", False)),
    }

    return out
