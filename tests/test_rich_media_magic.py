"""Unit tests for magic-byte inference of image/audio/video containers (cloaking)."""

import tempfile
from pathlib import Path

import pytest

from core.content_type import choose_effective_rich_media_extension
from core.rich_media_magic import infer_rich_media_suffix, infer_rich_media_suffix_from_source


@pytest.mark.parametrize(
    "prefix,expected",
    [
        (b"\xff\xd8\xff\xe0", ".jpg"),
        (b"\x89PNG\r\n\x1a\n\x00\x00\x00", ".png"),
        (b"GIF89a" + b"\x00" * 20, ".gif"),
        (b"BM" + b"\x00" * 30, ".bmp"),
        (b"II*\x00" + b"\x00" * 20, ".tif"),
        (b"MM\x00*" + b"\x00" * 20, ".tif"),
        (b"RIFF" + b"\x00\x00\x00\x00" + b"WEBP", ".webp"),
        (b"ID3\x04\x00\x00" + b"\x00" * 20, ".mp3"),
        (b"fLaC" + b"\x00" * 20, ".flac"),
        (b"OggS" + b"\x00" * 20, ".ogg"),
        (b"\x00\x00\x00\x18ftypmp42" + b"\x00" * 10, ".mp4"),
    ],
)
def test_infer_rich_media_suffix(prefix: bytes, expected: str) -> None:
    assert infer_rich_media_suffix(prefix + b"\x00" * 64) == expected


def test_infer_rich_media_suffix_too_short() -> None:
    assert infer_rich_media_suffix(b"\xff\xd8") is None


def test_infer_rich_media_suffix_from_path_writes_file() -> None:
    data = b"\xff\xd8\xff\xe0" + b"\x00" * 100
    with tempfile.NamedTemporaryFile(suffix=".txt", delete=False) as f:
        f.write(data)
        p = Path(f.name)
    try:
        assert infer_rich_media_suffix_from_source(p) == ".jpg"
    finally:
        p.unlink(missing_ok=True)


def test_choose_effective_rich_media_extension_remaps_txt() -> None:
    data = b"\xff\xd8\xff\xe0" + b"\x00" * 100
    with tempfile.NamedTemporaryFile(suffix=".txt", delete=False) as f:
        f.write(data)
        p = Path(f.name)
    try:
        assert choose_effective_rich_media_extension(".txt", False, p) == ".txt"
        assert choose_effective_rich_media_extension(".txt", True, p) == ".jpg"
        assert choose_effective_rich_media_extension(".jpg", True, p) == ".jpg"
    finally:
        p.unlink(missing_ok=True)
