"""Smoke tests for the bounded SRE prefilter exposed by ``boar_fast_filter``.

These exercise the doctrine surface added in
``rust/boar_fast_filter/src/bounded_filter.rs``:

* The legacy ``FastFilter`` is unbounded by design — fast path for clean
  inputs.
* ``BoundedFilter`` is the **doctrine-aware** path: per-row size cap and
  wall-clock budget that clamp to documented hard ceilings, plus a
  ``BudgetReport`` dict that carries the demotion reason for the audit log
  (THE_ART_OF_THE_FALLBACK §3).

If the Rust extension is not installed (no ``maturin develop`` on the runner),
the tests are skipped — same posture as ``tests/test_rust_bridge.py``.
"""

from __future__ import annotations

import pytest


@pytest.fixture(scope="module")
def bounded_filter():
    """Skip cleanly when the Rust extension has not been built locally."""
    mod = pytest.importorskip(
        "boar_fast_filter",
        reason="Rust extension not installed. Run maturin develop first.",
    )
    cls = getattr(mod, "BoundedFilter", None)
    if cls is None:
        pytest.skip("boar_fast_filter built without BoundedFilter (older artifact)")
    return cls()


def test_hard_ceilings_match_doctrine_constants(bounded_filter) -> None:
    """The Python-visible ceilings must match DEFENSIVE_SCANNING_MANIFESTO §2."""
    cls = type(bounded_filter)
    # 4 MiB / 60 s — matches `bounded_filter::HARD_MAX_*` in the Rust crate.
    assert cls.hard_max_row_bytes() == 4 * 1024 * 1024
    assert cls.hard_max_wall_clock_ms() == 60_000


def test_clean_batch_returns_no_demotion(bounded_filter) -> None:
    indices, report = bounded_filter.filter_batch_bounded(
        ["hello world", "no pii here"],
        0,  # use hard ceiling for row size
        0,  # use hard ceiling for wall clock
    )
    assert indices == []
    assert report["rows_scanned"] == 2
    assert report["rows_skipped_oversize"] == 0
    assert report["rows_skipped_budget"] == 0
    assert report["wall_clock_exceeded"] is False
    assert report["demotion_reason"] is None


def test_pii_batch_flags_expected_indices(bounded_filter) -> None:
    indices, report = bounded_filter.filter_batch_bounded(
        [
            "123.456.789-00",  # 0: CPF-shaped
            "no pii here",  # 1: clean
            "fulano@example.test",  # 2: email
            "pan 4111 1111 1111 1111",  # 3: valid Luhn (Visa test PAN)
            "pan 4111 1111 1111 1112",  # 4: invalid Luhn
        ],
        0,
        0,
    )
    assert indices == [0, 2, 3]
    assert report["rows_scanned"] == 5
    assert report["demotion_reason"] is None


def test_oversize_row_demotes_with_audit_reason(bounded_filter) -> None:
    """Per-row size cap kicks in *before* regex evaluation."""
    huge = "X" * 4096 + " 4111 1111 1111 1111"  # would match if read
    indices, report = bounded_filter.filter_batch_bounded(
        ["fulano@example.test", huge, "no pii here"],
        1024,  # 1 KiB cap forces the middle row to be skipped
        0,
    )
    assert indices == [0]  # only the small email matched
    assert report["rows_scanned"] == 2
    assert report["rows_skipped_oversize"] == 1
    assert report["demotion_reason"] == "row_size_cap_exceeded"
    # 1 KiB request is below the hard ceiling — must be honored, not clamped up.
    assert report["effective_max_row_bytes"] == 1024


def test_zero_arguments_clamp_to_hard_ceiling(bounded_filter) -> None:
    _, report = bounded_filter.filter_batch_bounded([], 0, 0)
    assert report["effective_max_row_bytes"] == 4 * 1024 * 1024
    assert report["effective_wall_clock_ms"] == 60_000


def test_over_ceiling_arguments_are_clamped(bounded_filter) -> None:
    """Doctrine: requests above the hard ceiling are silently clamped down."""
    _, report = bounded_filter.filter_batch_bounded(
        [],
        4 * 1024 * 1024 * 1024,  # 4 GiB requested
        60 * 60 * 1000,  # 1 h requested
    )
    assert report["effective_max_row_bytes"] == 4 * 1024 * 1024
    assert report["effective_wall_clock_ms"] == 60_000


def test_audit_row_arithmetic_invariant(bounded_filter) -> None:
    """rows_scanned + skipped_oversize + skipped_budget == len(batch).

    THE_ART_OF_THE_FALLBACK §4 — "reduce coverage, never truthfulness".
    The audit math has to balance whether the loop completed normally or
    broke on a relief valve.
    """
    batch = ["a@b.cd", "x" * 100_000, "no pii"]
    _, report = bounded_filter.filter_batch_bounded(batch, 1024, 0)
    total = (
        report["rows_scanned"]
        + report["rows_skipped_oversize"]
        + report["rows_skipped_budget"]
    )
    assert total == len(batch)
