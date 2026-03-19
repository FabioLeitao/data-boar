"""
Stable machine fingerprint for optional license binding.

Uses hostname + optional DATA_BOAR_MACHINE_SEED (recommended in Docker/VM pools).
"""

from __future__ import annotations

import hashlib
import os
import socket


def compute_machine_fingerprint() -> str:
    """
    Return SHA-256 hex digest identifying this runtime environment.

    Set DATA_BOAR_MACHINE_SEED in production (especially containers) to a stable
    per-deployment secret so licenses can bind to a deployment, not a random hostname.
    """
    seed = (os.environ.get("DATA_BOAR_MACHINE_SEED") or "").strip()
    host = socket.gethostname().lower()
    blob = f"v1|host={host}|seed={seed}".encode("utf-8")
    return hashlib.sha256(blob).hexdigest()
