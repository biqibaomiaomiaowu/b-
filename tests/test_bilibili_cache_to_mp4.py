import os
from pathlib import Path

import pytest

from bilibili_cache_to_mp4 import (
    BILIBILI_CACHE_PREFIX,
    BILIBILI_CACHE_PREFIX_LEN,
    strip_bilibili_cache_prefix,
)


def test_strip_bilibili_cache_prefix_creates_target_dir(tmp_path: Path):
    """Test that the target directory is created if it does not exist."""
    source_path = tmp_path / "source.m4s"
    target_dir = tmp_path / "target_dir"
    target_path = target_dir / "target.m4s"

    # Create source file with valid prefix
    content = BILIBILI_CACHE_PREFIX + b"hello world"
    source_path.write_bytes(content)

    assert not target_dir.exists()

    result_path = strip_bilibili_cache_prefix(source_path, target_path)

    assert target_dir.exists()
    assert target_path.exists()
    assert result_path == target_path
    assert target_path.read_bytes() == b"hello world"


def test_strip_bilibili_cache_prefix_content(tmp_path: Path):
    """Test that the correct content is stripped."""
    source_path = tmp_path / "source.m4s"
    target_path = tmp_path / "target.m4s"

    # Prefix is exactly BILIBILI_CACHE_PREFIX_LEN bytes
    content = b"A" * BILIBILI_CACHE_PREFIX_LEN + b"actual media content"
    source_path.write_bytes(content)

    strip_bilibili_cache_prefix(source_path, target_path)

    assert target_path.read_bytes() == b"actual media content"


def test_strip_bilibili_cache_prefix_large_file(tmp_path: Path):
    """Test with a file larger than the copy buffer (1MB)."""
    source_path = tmp_path / "source.m4s"
    target_path = tmp_path / "target.m4s"

    # 2MB of data
    large_data = os.urandom(2 * 1024 * 1024)
    content = BILIBILI_CACHE_PREFIX + large_data
    source_path.write_bytes(content)

    strip_bilibili_cache_prefix(source_path, target_path)

    assert target_path.read_bytes() == large_data


def test_strip_bilibili_cache_prefix_empty_after_prefix(tmp_path: Path):
    """Test with a file that only contains the prefix."""
    source_path = tmp_path / "source.m4s"
    target_path = tmp_path / "target.m4s"

    source_path.write_bytes(BILIBILI_CACHE_PREFIX)

    strip_bilibili_cache_prefix(source_path, target_path)

    assert target_path.exists()
    assert target_path.read_bytes() == b""


def test_strip_bilibili_cache_prefix_file_smaller_than_prefix(tmp_path: Path):
    """Test with a file smaller than the prefix length. Should just copy empty."""
    source_path = tmp_path / "source.m4s"
    target_path = tmp_path / "target.m4s"

    # Write only a few bytes (less than prefix length)
    source_path.write_bytes(b"short")

    strip_bilibili_cache_prefix(source_path, target_path)

    assert target_path.exists()
    assert target_path.read_bytes() == b""
