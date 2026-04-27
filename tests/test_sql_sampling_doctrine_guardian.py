"""
Stress & coverage guardian for ``connectors/sql_sampling.py``.

These tests encode the **Defensive Scanning Manifesto** invariants
(``docs/ops/inspirations/DEFENSIVE_SCANNING_MANIFESTO.md``) as
regression-proof negative tests across every supported dialect:

1. The leading ``-- Data Boar Compliance Scan`` line MUST appear on every
   emitted statement (DBA grep contract, §4 of the manifesto).
2. Auto-sampling SQL MUST never inject ``ORDER BY`` (§5).
3. SQL Server sampling MUST always carry ``WITH (NOLOCK)`` (§3 / §6).
4. The hard sample cap (``_HARD_MAX_SAMPLE = 10_000``) MUST clamp even
   when an attacker / misconfigured caller asks for a buffer-overflow
   sized read (the "Data Soup" §6.Don't list).
5. Env knobs (``DATA_BOAR_PG_TABLESAMPLE_SYSTEM_PERCENT``,
   ``DATA_BOAR_MSSQL_TABLESAMPLE_SYSTEM_PERCENT``,
   ``DATA_BOAR_SAMPLE_STATEMENT_TIMEOUT_MS``) MUST stay clamped to
   documented ranges; invalid input MUST fall back to defaults, never
   to "unbounded".
6. MySQL identifier escaping MUST double an embedded backtick
   (defensive identifier handling — connectors guarantee ``safe_col`` is
   pre-escaped, but the composer must not re-introduce a hole).

Tests are deterministic (no ``sleep``, no real DB).
"""

from __future__ import annotations

import pytest

from connectors.sql_sampling import (
    SamplingManager,
    SqlColumnSampleQueryBuilder,
    TableSamplingMetadata,
    _HARD_MAX_SAMPLE,
    column_sample_sql_for_cursor,
    resolve_sql_sample_limit,
    resolve_statement_timeout_ms_for_sampling,
)

_LEADING = "-- Data Boar Compliance Scan\n"

_DIALECTS_WITH_SCHEMA = (
    "sqlite",
    "mysql",
    "mariadb",
    "postgresql",
    "postgres",
    "mssql",
    "microsoft sql server",
    "oracle",
    "snowflake",
    "duckdb",
    "cockroachdb",
    "tibero",
)


def _build(dialect: str, *, limit: int = 5, large: bool = False) -> str:
    meta = TableSamplingMetadata(estimated_row_count=2_000_000) if large else None
    plan = SamplingManager.build_column_sample(
        dialect,
        safe_col="c",
        safe_table="t",
        safe_schema="pub",
        schema="pub",
        limit=limit,
        table_metadata=meta,
        statement_timeout_ms=None,
    )
    return str(plan.query)


@pytest.mark.parametrize("dialect", _DIALECTS_WITH_SCHEMA)
def test_every_dialect_carries_compliance_scan_leading_comment(dialect: str) -> None:
    """Manifesto §4: DBA-grep contract — never lose the leading tag."""
    sql = _build(dialect)
    assert sql.startswith(_LEADING), (
        f"dialect={dialect!r} dropped the '-- Data Boar Compliance Scan' tag; "
        "this breaks pg_stat_activity / DMV grep for DBAs."
    )


@pytest.mark.parametrize("dialect", _DIALECTS_WITH_SCHEMA)
@pytest.mark.parametrize("large", [False, True])
def test_no_order_by_on_auto_sampling(dialect: str, large: bool) -> None:
    """Manifesto §5: auto-sampling SQL must not introduce ORDER BY."""
    sql = _build(dialect, large=large).upper()
    assert " ORDER BY " not in sql, (
        f"dialect={dialect!r} large={large}: ORDER BY leaked into auto-sampling; "
        "this would force a full-table sort on customer DBs."
    )


@pytest.mark.parametrize("dialect", ("mssql", "microsoft sql server"))
@pytest.mark.parametrize("large", [False, True])
def test_mssql_paths_always_keep_nolock(dialect: str, large: bool) -> None:
    """Manifesto §3: SQL Server sampling reads never block a writer."""
    sql = _build(dialect, large=large)
    assert "WITH (NOLOCK)" in sql, (
        f"dialect={dialect!r} large={large}: NOLOCK lost; "
        "compliance read could now contend with long writers."
    )


def test_hard_cap_clamps_buffer_overflow_request() -> None:
    """Manifesto §2: hard ceiling applies even to a hostile-large request.

    A misconfigured ETL or hostile YAML must never coerce the sampler into
    asking for ``2**31`` rows. The cap is enforced **in code**, not asked
    nicely in the docs.
    """
    huge = 2**31  # ~2.1 billion: classic 32-bit overflow scenario.
    plan = SamplingManager.build_column_sample(
        "postgresql",
        safe_col="c",
        safe_table="t",
        safe_schema="pub",
        schema="pub",
        limit=huge,
        table_metadata=None,
        statement_timeout_ms=None,
    )
    sql = str(plan.query)
    assert f"LIMIT {_HARD_MAX_SAMPLE}" in sql, (
        f"hard cap {_HARD_MAX_SAMPLE} did not clamp request={huge}; SQL was: {sql!r}"
    )
    assert str(huge) not in sql


def test_resolve_sql_sample_limit_negative_input_clamps_to_one() -> None:
    """Negative request must collapse to the documented baseline of 1."""
    assert resolve_sql_sample_limit(-1) == 1
    assert resolve_sql_sample_limit(-(2**30)) == 1


def test_resolve_sql_sample_limit_env_negative_clamps_to_one(monkeypatch) -> None:
    monkeypatch.setenv("DATA_BOAR_SQL_SAMPLE_LIMIT", "-9999")
    assert resolve_sql_sample_limit(50) == 1


def test_resolve_statement_timeout_explicit_clamped_to_60s() -> None:
    """Manifesto §2: 60_000 ms is the documented hard ceiling."""
    assert resolve_statement_timeout_ms_for_sampling(10**9) == 60_000


def test_resolve_statement_timeout_explicit_minimum_floor() -> None:
    """A positive but too-small budget must be raised to the documented floor."""
    assert resolve_statement_timeout_ms_for_sampling(1) == 250


def test_resolve_statement_timeout_explicit_zero_or_negative_returns_none() -> None:
    """``<= 0`` disables the SQL hint (connector may still SET LOCAL)."""
    assert resolve_statement_timeout_ms_for_sampling(0) is None
    assert resolve_statement_timeout_ms_for_sampling(-5) is None


@pytest.mark.parametrize("bad_value", ["abc", "", "  ", "1.5e3junk"])
def test_resolve_statement_timeout_env_invalid_returns_none(monkeypatch, bad_value):
    """Invalid env values must NOT silently coerce into a partial timeout."""
    monkeypatch.setenv("DATA_BOAR_SAMPLE_STATEMENT_TIMEOUT_MS", bad_value)
    assert resolve_statement_timeout_ms_for_sampling(None) is None


def test_pg_tablesample_percent_env_invalid_falls_back_to_default(monkeypatch) -> None:
    """``DATA_BOAR_PG_TABLESAMPLE_SYSTEM_PERCENT=garbage`` must use the documented 1.0%."""
    monkeypatch.setenv("DATA_BOAR_PG_TABLESAMPLE_SYSTEM_PERCENT", "garbage")
    meta = TableSamplingMetadata(estimated_row_count=2_000_000)
    sql = str(
        SamplingManager.build_column_sample(
            "postgresql",
            safe_col="c",
            safe_table="t",
            safe_schema="pub",
            schema="pub",
            limit=10,
            table_metadata=meta,
        ).query
    )
    assert "TABLESAMPLE SYSTEM (1)" in sql


def test_mssql_tablesample_percent_env_clamped_high(monkeypatch) -> None:
    """Out-of-range percent must clamp to 100, never pass through unbounded."""
    monkeypatch.setenv("DATA_BOAR_MSSQL_TABLESAMPLE_SYSTEM_PERCENT", "99999")
    meta = TableSamplingMetadata(estimated_row_count=2_000_000)
    sql = str(
        SamplingManager.build_column_sample(
            "mssql",
            safe_col="c",
            safe_table="t",
            safe_schema="dbo",
            schema="dbo",
            limit=10,
            table_metadata=meta,
        ).query
    )
    assert "TABLESAMPLE SYSTEM (100 PERCENT)" in sql
    assert "WITH (NOLOCK)" in sql


def test_mssql_tablesample_percent_env_clamped_low(monkeypatch) -> None:
    monkeypatch.setenv("DATA_BOAR_MSSQL_TABLESAMPLE_SYSTEM_PERCENT", "-5")
    meta = TableSamplingMetadata(estimated_row_count=2_000_000)
    sql = str(
        SamplingManager.build_column_sample(
            "mssql",
            safe_col="c",
            safe_table="t",
            safe_schema="dbo",
            schema="dbo",
            limit=10,
            table_metadata=meta,
        ).query
    )
    assert "TABLESAMPLE SYSTEM (0.01 PERCENT)" in sql


def test_mysql_backtick_in_identifier_is_doubled() -> None:
    """Defensive identifier handling: an embedded backtick must not break out."""
    q = SqlColumnSampleQueryBuilder.build(
        "mysql",
        safe_col="ev`il",
        safe_table="users",
        safe_schema="app",
        schema="app",
        limit=2,
    )
    s = str(q)
    assert "`ev``il`" in s, (
        "MySQL composer must double an embedded backtick to keep the identifier "
        f"quoted; got: {s!r}"
    )
    assert "ev`il`" not in s.replace("ev``il", "")


def test_oracle_cursor_path_uses_literal_lim_no_binds() -> None:
    """DB-API drivers without SQLAlchemy must not see ``:lim`` placeholders."""
    sql, binds, label, _notes, human = column_sample_sql_for_cursor(
        "oracle",
        safe_col="C",
        safe_table="T",
        safe_schema="S",
        schema="S",
        limit=3,
        table_metadata=None,
    )
    assert binds == {}
    assert ":lim" not in sql
    assert "<= 3" in sql
    assert label == "non_null_rownum_oracle"
    assert human == "ROWNUM inner filter (Oracle)"


def test_unknown_dialect_falls_back_with_tag_and_limit() -> None:
    """Manifesto: unknown dialect is a *fallback*, never an unbounded scan."""
    sql = _build("teradata-future", limit=4)
    assert sql.startswith(_LEADING)
    assert "LIMIT 4" in sql
    assert "ORDER BY" not in sql.upper()
