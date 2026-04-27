"""Regression guard for the 200k A/B benchmark evidence (OpenCore vs Pro).

Pin the published numbers in ``tests/benchmarks/official_benchmark_200k.json``
so executive material cannot accidentally claim a Pro+ "speedup" that
contradicts the recorded artifact — and, after Slice 2 (PR #233-class), so
the **direction** stays the doctrinal one: Pro must be at least as fast as
OpenCore on the seeded synthetic workload.

Why this lives in the test suite (Julia Evans-style note):

- Slice 1 pinned a recorded ``speedup_vs_opencore = 0.574`` (Pro **slower**
  than OpenCore by ~1.74x wall-clock). That number was a real measurement and
  a real regression — the Pro Python fallback was running the OpenCore regex
  twice and the worker pipeline added a no-op pass through ``deep_ml_analysis``.
- Slice 2 fuses the candidate regex into a single alternation and does a
  single-pass scan inside the worker (CPF / e-mail short-circuit; Luhn only
  fires on card-shape matches). The new artifact records the corrected
  measurement, and this test asserts the **fixed direction** plus the still
  non-negotiable findings parity.

Defensive posture (``DEFENSIVE_SCANNING_MANIFESTO.md``):

- The check is a **read-only** JSON parse. No database connection, no SQLite
  write, no file lock acquisition; safe to run alongside scans.

Fallback posture (``THE_ART_OF_THE_FALLBACK.md``):

- If the artifact is ever regenerated with a different profile (larger chunks,
  heavier downstream stage, Rust path enabled), the assertions surface the
  change immediately so the operator updates marketing prose **and** the JSON
  together, instead of one drifting from the other.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

ARTIFACT = (
    Path(__file__).resolve().parents[1]
    / "tests"
    / "benchmarks"
    / "official_benchmark_200k.json"
)


@pytest.fixture(scope="module")
def benchmark_payload() -> dict:
    assert ARTIFACT.exists(), (
        f"Missing benchmark artifact: {ARTIFACT}. "
        "Re-run tests/benchmarks/run_official_bench.py and commit the JSON."
    )
    return json.loads(ARTIFACT.read_text(encoding="utf-8"))


def test_benchmark_shape_is_official_pro_v1(benchmark_payload: dict) -> None:
    """The pinned artifact must declare its provenance fields."""
    assert benchmark_payload.get("benchmark") == "official_pro_v1"
    assert benchmark_payload.get("rows") == 200_000
    assert benchmark_payload.get("workers") == 8


def test_benchmark_pro_path_is_at_least_as_fast(
    benchmark_payload: dict,
) -> None:
    """Direction of the recorded A/B: Pro path must be at least as fast as OpenCore.

    Slice 2 closed the regression captured in Slice 1 (``0.574x`` ratio). The
    guard now refuses any artifact that records Pro slower than OpenCore by
    more than a small noise band (5 percent), forcing whoever regresses
    performance to either fix the code or write up a post-mortem and adjust
    the slack consciously.
    """
    opencore_seconds = float(benchmark_payload["opencore_seconds"])
    pro_seconds = float(benchmark_payload["pro_seconds"])
    speedup = float(benchmark_payload["speedup_vs_opencore"])

    assert opencore_seconds > 0
    assert pro_seconds > 0

    # Tolerate a 5 percent noise band on slow CI runners; anything beyond that
    # is a real regression and should fail loud.
    noise_band_ratio = 0.95
    assert speedup >= noise_band_ratio, (
        f"speedup_vs_opencore={speedup} fell below the {noise_band_ratio} "
        "noise band: Pro path regressed against OpenCore. Investigate "
        "core/prefilter.py and pro/worker_logic.py before refreshing the "
        "artifact."
    )


def test_benchmark_speedup_matches_recorded_ratio(
    benchmark_payload: dict,
) -> None:
    """Recorded speedup field must match opencore/pro arithmetic (rounded).

    We use a generous tolerance because the JSON stores ``round(speedup, 4)``.
    """
    opencore_seconds = float(benchmark_payload["opencore_seconds"])
    pro_seconds = float(benchmark_payload["pro_seconds"])
    recorded = float(benchmark_payload["speedup_vs_opencore"])
    expected = opencore_seconds / pro_seconds
    assert abs(recorded - expected) < 1e-3, (
        f"speedup_vs_opencore={recorded} drifted from "
        f"opencore_seconds/pro_seconds={expected}; regenerate or fix by hand."
    )


def test_benchmark_findings_parity(benchmark_payload: dict) -> None:
    """Both paths must report the same finding count for the seeded corpus.

    A divergence here would mean the Pro path silently dropped detections,
    which is more important than performance for a defensive scanner.
    """
    opencore_hits = int(benchmark_payload["opencore_hits"])
    pro_hits = int(benchmark_payload["pro_hits"])
    assert opencore_hits == pro_hits, (
        "Pro and OpenCore disagree on hit counts at 200k. "
        "Investigate prefilter/worker logic before any performance tuning."
    )
