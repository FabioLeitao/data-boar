"""
Optional commercial licensing (open by default).

See docs/LICENSING_SPEC.md and docs/LICENSING_OPEN_CORE_AND_COMMERCIAL.md.
"""

from core.licensing.errors import LicenseBlockedError
from core.licensing.feature_gate import (
    FeatureGateDecision,
    FeatureNotAvailableError,
    evaluate_feature,
    is_feature_enabled,
    require_feature,
    snapshot_gate_state,
)
from core.licensing.guard import (
    LicenseContext,
    LicenseGuard,
    get_license_guard,
    reset_license_guard_for_tests,
)

__all__ = [
    "FeatureGateDecision",
    "FeatureNotAvailableError",
    "LicenseBlockedError",
    "LicenseContext",
    "LicenseGuard",
    "evaluate_feature",
    "get_license_guard",
    "is_feature_enabled",
    "require_feature",
    "reset_license_guard_for_tests",
    "snapshot_gate_state",
]
