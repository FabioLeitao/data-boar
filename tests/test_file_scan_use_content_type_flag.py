from __future__ import annotations

from connectors.filesystem_connector import FilesystemConnector


class DummyScanner:
    def scan_file_content(self, *_args, **_kwargs):
        return None


class DummyDB:
    def save_failure(self, *_args, **_kwargs):
        pass

    def save_finding(self, *_args, **_kwargs):
        pass


def test_filesystem_connector_reads_use_content_type_flag() -> None:
    target_config = {
        "name": "fs-test",
        "path": ".",
        "recursive": False,
        "file_scan": {
            "scan_compressed": False,
            "use_content_type": True,
        },
    }
    connector = FilesystemConnector(
        target_config=target_config,
        scanner=DummyScanner(),
        db_manager=DummyDB(),
        extensions=[".txt"],
        scan_sqlite_as_db=False,
        sample_limit=1,
    )
    assert connector.use_content_type is True

