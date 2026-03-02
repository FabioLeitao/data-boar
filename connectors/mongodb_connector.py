"""
Optional MongoDB connector: connect, list collections, sample documents, run detector, save_finding.
Register as type 'mongodb'. Install: pip install pymongo
Config target: type: database, driver: mongodb, host, port, database (and optional user/pass).
"""
from typing import Any

try:
    from pymongo import MongoClient
    _MONGO_AVAILABLE = True
except ImportError:
    _MONGO_AVAILABLE = False
    MongoClient = None

from core.connector_registry import register


class MongoDBConnector:
    """Scan MongoDB: list collections, sample docs, detect sensitive field names and sample values."""

    def __init__(self, target_config: dict[str, Any], scanner: Any, db_manager: Any, sample_limit: int = 5):
        self.config = target_config
        self.scanner = scanner
        self.db_manager = db_manager
        self.sample_limit = sample_limit
        self._client = None

    def connect(self) -> None:
        if not _MONGO_AVAILABLE:
            raise RuntimeError("pymongo is not installed. Install with: pip install pymongo")
        host = self.config.get("host", "localhost")
        port = int(self.config.get("port", 27017))
        user = self.config.get("user") or self.config.get("username")
        password = self.config.get("pass") or self.config.get("password")
        database = self.config.get("database", "test")
        if user and password:
            uri = f"mongodb://{user}:{password}@{host}:{port}/{database}"
        else:
            uri = f"mongodb://{host}:{port}"
        self._client = MongoClient(uri)
        self._db = self._client[database]

    def close(self) -> None:
        if self._client:
            try:
                self._client.close()
            except Exception:
                pass
            self._client = None

    def run(self) -> None:
        target_name = self.config.get("name", "mongodb")
        try:
            self.connect()
        except Exception as e:
            self.db_manager.save_failure(target_name, "unreachable", str(e))
            return
        try:
            from utils.logger import log_connection
            log_connection(target_name, "mongodb", self.config.get("host", "localhost"))
            for coll_name in self._db.list_collection_names():
                coll = self._db[coll_name]
                sample_docs = list(coll.find().limit(self.sample_limit))
                if not sample_docs:
                    continue
                # Flatten keys from sample docs
                all_keys = set()
                sample_texts = []
                for doc in sample_docs:
                    for k, v in doc.items():
                        if k.startswith("_"):
                            continue
                        all_keys.add(k)
                        if v is not None:
                            sample_texts.append(f"{k} {str(v)[:100]}")
                combined = " ".join(sample_texts)
                for key in all_keys:
                    res = self.scanner.scan_column(key, combined)
                    if res["sensitivity_level"] == "LOW":
                        continue
                    self.db_manager.save_finding(
                        source_type="database",
                        target_name=target_name,
                        server_ip=self.config.get("host", "localhost"),
                        engine_details="mongodb",
                        schema_name="",
                        table_name=coll_name,
                        column_name=key,
                        data_type="document",
                        sensitivity_level=res["sensitivity_level"],
                        pattern_detected=res["pattern_detected"],
                        norm_tag=res.get("norm_tag", ""),
                        ml_confidence=res.get("ml_confidence", 0),
                    )
                    try:
                        from utils.logger import log_finding
                        log_finding("database", target_name, f"{coll_name}.{key}", res["sensitivity_level"], res["pattern_detected"])
                    except Exception:
                        pass
        except Exception as e:
            self.db_manager.save_failure(target_name, "error", str(e))
        finally:
            self.close()


if _MONGO_AVAILABLE:
    register("mongodb", MongoDBConnector, ["name", "type"])
