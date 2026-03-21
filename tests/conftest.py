"""
Pytest configuration: shared fixtures and CLI flags.

**Optional private lint:** Pass ``--include-private`` or set environment variable
``INCLUDE_PRIVATE_LINT=1`` (or ``true`` / ``yes``) to include **gitignored**
``docs/private/`` in markdown lint and optional PowerShell/bash syntax checks under
that tree. Default remains **exclude** so CI and ``check-all`` never depend on local
private notes.
"""

from __future__ import annotations

import os

import pytest


def pytest_addoption(parser: pytest.Parser) -> None:
    parser.addoption(
        "--include-private",
        action="store_true",
        default=False,
        help=(
            "Include docs/private/ in markdown lint and optional script syntax checks "
            "(gitignored; default: skip)."
        ),
    )


@pytest.fixture(scope="session")
def include_private_lint(request: pytest.FixtureRequest) -> bool:
    """True if private trees should be linted (CLI flag or INCLUDE_PRIVATE_LINT env)."""
    env = os.environ.get("INCLUDE_PRIVATE_LINT", "").strip().lower()
    if env in ("1", "true", "yes"):
        return True
    return bool(request.config.getoption("--include-private"))
