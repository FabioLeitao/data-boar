"""Smoke test for optional Rust bridge module ``boar_fast_filter``."""

from __future__ import annotations

import time

import pytest


def test_rust_bridge_fast_filter_batch() -> None:
    mod = pytest.importorskip(
        "boar_fast_filter",
        reason="Rust extension not installed. Run maturin develop first.",
    )
    fast_filter_cls = getattr(mod, "FastFilter", None)
    assert fast_filter_cls is not None

    scanner = fast_filter_cls()
    data = [
        "123.456.789-00",
        "texto comum",
        "contato@empresa.com",
        "cartao valido 4111 1111 1111 1111",
        "cartao invalido 4111 1111 1111 1112",
    ] * 1000

    start = time.perf_counter()
    indices = scanner.filter_batch(data)
    elapsed = time.perf_counter() - start

    assert isinstance(indices, list)
    assert len(indices) == 3000
    # Keep as smoke threshold to avoid flaky CI on slower runners.
    assert elapsed < 2.0
