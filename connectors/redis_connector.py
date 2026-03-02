"""
Optional Redis connector: connect, scan keys (or sample), run detector on key names and types.
Register as type 'redis'. Install: pip install redis
Config target: type: database, driver: redis, host, port, (optional password).
"""
from typing import Any

try:
    import redis
    _REDIS_AVAILABLE = True
except ImportError:
    _REDIS_AVAILABLE = False
    redis = None

from core.connector_registry import register


class RedisConnector:
    """Scan Redis: sample keys (e.g. SCAN), detect sensitive key names; no value storage."""

    def __init__(self, target_config: dict[str, Any], scanner: Any, db_manager: Any, sample_limit: int = 100):
        self.config = target_config
        self.scanner = scanner
        self.db_manager = db_manager
        self.sample_limit = sample_limit
        self._client = None

    def connect(self) -> None:
        if not _REDIS_AVAILABLE:
            raise RuntimeError("redis is not installed. Install with: pip install redis")
        host = self.config.get("host", "localhost")
        port = int(self.config.get("port", 6379))
        password = self.config.get("pass") or self.config.get("password")
        self._client = redis.Redis(host=host, port=port, password=password or None, decode_responses=True)

    def close(self) -> None:
        if self._client:
            try:
                self._client.close()
            except Exception:
                pass
            self._client = None

    def run(self) -> None:
        target_name = self.config.get("name", "redis")
        try:
            self.connect()
        except Exception as e:
            self.db_manager.save_failure(target_name, "unreachable", str(e))
            return
        try:
            from utils.logger import log_connection
            log_connection(target_name, "redis", self.config.get("host", "localhost"))
            keys = []
            for k in self._client.scan_iter(count=self.sample_limit):
                keys.append(k)
                if len(keys) >= self.sample_limit:
                    break
            combined = " ".join(keys)
            for key in keys[:50]:  # per-key classification
                res = self.scanner.scan_column(key, combined)
                if res["sensitivity_level"] == "LOW":
                    continue
                self.db_manager.save_finding(
                    source_type="database",
                    target_name=target_name,
                    server_ip=self.config.get("host", "localhost"),
                    engine_details="redis",
                    schema_name="",
                    table_name="keys",
                    column_name=key,
                    data_type="key",
                    sensitivity_level=res["sensitivity_level"],
                    pattern_detected=res["pattern_detected"],
                    norm_tag=res.get("norm_tag", ""),
                    ml_confidence=res.get("ml_confidence", 0),
                )
                try:
                    from utils.logger import log_finding
                    log_finding("database", target_name, f"keys.{key}", res["sensitivity_level"], res["pattern_detected"])
                except Exception:
                    pass
        except Exception as e:
            self.db_manager.save_failure(target_name, "error", str(e))
        finally:
            self.close()


if _REDIS_AVAILABLE:
    register("redis", RedisConnector, ["name", "type"])
