"""RBAC feature gate (GitHub #86 Phase 2): config + Pro tier per ``tier_features.dashboard_rbac``."""

from __future__ import annotations

from typing import Any

from core.licensing.runtime_feature_tier import get_runtime_tier_for_features
from core.licensing.tier_features import is_feature_available


def rbac_enforcement_active(config: dict[str, Any]) -> bool:
    """
    True when ``api.rbac.enabled`` is set and the deployment tier allows ``dashboard_rbac``.

    Community tier cannot enable in-product RBAC; OPEN/dev mode keeps all features available.
    """
    api = config.get("api") if isinstance(config.get("api"), dict) else {}
    raw = api.get("rbac")
    if not isinstance(raw, dict) or not raw.get("enabled"):
        return False
    return is_feature_available(
        "dashboard_rbac",
        get_runtime_tier_for_features(config),
    )
