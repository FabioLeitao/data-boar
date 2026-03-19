from core.engine import _compute_config_scope_hash


def test_compute_config_scope_hash_is_stable_for_same_scope():
    config_a = {
        "targets": [
            {"name": "hr-db", "type": "postgresql"},
            {"name": "files", "type": "filesystem"},
        ],
        "file_scan": {"extensions": [".csv", ".xlsx"]},
    }
    config_b = {
        "targets": [
            {"name": "files", "type": "filesystem"},
            {"name": "hr-db", "type": "postgresql"},
        ],
        "file_scan": {"extensions": [".xlsx", ".csv"]},
    }

    assert _compute_config_scope_hash(config_a) == _compute_config_scope_hash(config_b)


def test_compute_config_scope_hash_changes_when_scope_changes():
    baseline = {
        "targets": [{"name": "hr-db", "type": "postgresql"}],
        "file_scan": {"extensions": [".csv"]},
    }
    changed = {
        "targets": [{"name": "hr-db", "type": "postgresql"}],
        "file_scan": {"extensions": [".csv", ".xlsx"]},
    }

    assert _compute_config_scope_hash(baseline) != _compute_config_scope_hash(changed)
