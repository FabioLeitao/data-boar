"""FinOps + Defensive Scanning guardrail.

Why this test exists
--------------------
``utils/report_gen.py`` historically issued an unbounded
``SELECT * FROM audit_findings`` against the operator database to build the
"comprehensive report". That single line breaks three doctrines at once:

1. **Defensive Scanning Manifesto §2** — *no unbounded scans*. No ``LIMIT``,
   no projection, no statement timeout. On a busy customer instance this
   pulled every row over the wire (cloud egress + worker RAM bloat).
2. **Defensive Scanning Manifesto §4** — *DBA-grep contract*. The query
   was missing the ``-- Data Boar Compliance Scan`` leading comment, so a
   DBA could not identify or kill it cleanly.
3. **The Art of the Fallback §3** — *diagnostic on fall*. The referenced
   table (``audit_findings``) does not exist in the current schema; the
   call would have raised ``OperationalError`` from a worker with no audit
   row and no demoted strategy. Silent failure is a worse outcome than
   degraded coverage.

This test enforces, on every run, that **no production tracked Python
file** passes an unbounded ``SELECT * FROM <table>`` literal as the SQL
argument of ``pd.read_sql``, ``connection.execute``, ``cursor.execute``,
``sqlalchemy.text``, or any other SQL execution wrapper. Dialect-aware
sampling helpers in ``connectors/sql_sampling.py`` are intentionally
allow-listed because they wrap the inner ``SELECT *`` in a bounded
``WHERE ... IS NOT NULL`` plus dialect cap (``ROWNUM``, ``SAMPLE``, etc.)
and tag the statement with the compliance comment (manifesto §3).
"""

from __future__ import annotations

import ast
import re
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]

# Files that legitimately compose ``SELECT * FROM (... bounded inner ...)``
# under the dialect-aware sampling envelope. Composed and audited in
# connectors/sql_sampling.py and exercised by tests/test_sql_sampling.py.
_ALLOWED_FILES = {
    "connectors/sql_sampling.py",
}

_PROD_DIRS = (
    "core",
    "connectors",
    "report",
    "api",
    "utils",
    "cli",
    "scanners",
    "db",
    "database",
    "pro",
    "app",
    "analysis",
    "ops",
    "tools",
    "schemas",
    "config",
    "logging_custom",
    "file_scan",
    "audit_pipeline",
)

# Function names (callable side) that take a SQL string as their first arg.
_SQL_SINK_NAMES = {
    "read_sql",
    "read_sql_query",
    "read_sql_table",
    "execute",
    "executemany",
    "executescript",
    "exec_driver_sql",
    "text",
    "raw",
}

_UNBOUNDED_SELECT_STAR = re.compile(
    r"""\bSELECT\s+\*\s+FROM\s+[A-Za-z_][\w\.\"\`\[\]]*""",
    re.IGNORECASE,
)

_BOUND_TOKEN = re.compile(
    r"\b(LIMIT|TOP|ROWNUM|FETCH\s+FIRST|SAMPLE|WHERE|OFFSET)\b",
    re.IGNORECASE,
)


def _iter_prod_python_files() -> list[Path]:
    files: list[Path] = []
    for top in _PROD_DIRS:
        root = REPO_ROOT / top
        if not root.is_dir():
            continue
        files.extend(p for p in root.rglob("*.py") if p.is_file())
    return files


def _string_literal(node: ast.AST) -> str | None:
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        return node.value
    return None


def _call_target_name(call: ast.Call) -> str | None:
    func = call.func
    if isinstance(func, ast.Attribute):
        return func.attr
    if isinstance(func, ast.Name):
        return func.id
    return None


def _scan_file_for_unbounded_sql(path: Path) -> list[tuple[int, str]]:
    try:
        source = path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return []
    try:
        tree = ast.parse(source, filename=str(path))
    except SyntaxError:
        return []

    offenders: list[tuple[int, str]] = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        target = _call_target_name(node)
        if target not in _SQL_SINK_NAMES:
            continue
        if not node.args:
            continue
        sql = _string_literal(node.args[0])
        if not sql:
            continue
        if not _UNBOUNDED_SELECT_STAR.search(sql):
            continue
        if _BOUND_TOKEN.search(sql):
            continue
        offenders.append((node.lineno, sql.strip()))
    return offenders


def test_no_unbounded_select_star_in_production_python() -> None:
    """Forbid unbounded ``SELECT * FROM <table>`` SQL passed to DB sinks.

    Mirrors ``DEFENSIVE_SCANNING_MANIFESTO.md`` §2 (no unbounded scans).
    """

    offenders: list[tuple[str, int, str]] = []
    for path in _iter_prod_python_files():
        rel = path.relative_to(REPO_ROOT).as_posix()
        if rel in _ALLOWED_FILES:
            continue
        for lineno, sql in _scan_file_for_unbounded_sql(path):
            offenders.append((rel, lineno, sql))

    assert not offenders, (
        "Unbounded SELECT * detected in production tracked code. "
        "See docs/ops/inspirations/DEFENSIVE_SCANNING_MANIFESTO.md §2.\n"
        + "\n".join(f"  {rel}:{lineno}: {sql}" for rel, lineno, sql in offenders)
    )


def test_legacy_report_gen_is_safe_stub() -> None:
    """``utils.report_gen`` must be import-safe and DB-free.

    The retired ``ReportGenerator.generate_comprehensive_report`` and
    ``create_risk_heatmap`` paths must raise ``NotImplementedError`` so we
    never silently fall back into a costly, schema-mismatched read.
    """

    pd = pytest.importorskip("pandas")
    from utils import report_gen  # type: ignore[import-not-found]

    assert set(report_gen.__all__) >= {
        "ReportGenerator",
        "create_risk_heatmap",
        "get_mitigation_plan",
    }

    with pytest.warns(DeprecationWarning):
        rg = report_gen.ReportGenerator(db_manager=object())
    with pytest.raises(NotImplementedError):
        rg.generate_comprehensive_report()

    with pytest.warns(DeprecationWarning):
        with pytest.raises(NotImplementedError):
            report_gen.create_risk_heatmap(pd.DataFrame())

    # Pure helper still works on caller-owned DataFrames (no DB call).
    with pytest.warns(DeprecationWarning):
        out = report_gen.get_mitigation_plan(
            pd.DataFrame({"pattern_detected": ["CPF", "EMAIL", "ML_DETECTED", "OTHER"]})
        )
    assert {"Violação", "Risco", "Ação Recomendada", "Prioridade"} <= set(out.columns)
    assert len(out) == 3

    with pytest.warns(DeprecationWarning):
        empty = report_gen.get_mitigation_plan(pd.DataFrame())
    assert empty.empty

    with pytest.warns(DeprecationWarning):
        no_col = report_gen.get_mitigation_plan(pd.DataFrame({"foo": [1, 2]}))
    assert no_col.empty
