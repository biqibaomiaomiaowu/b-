import pytest
from unittest.mock import mock_open, patch
from pathlib import Path

from bilibili_cache_to_mp4 import (
    has_bilibili_cache_prefix,
    BILIBILI_CACHE_PREFIX,
    BILIBILI_CACHE_PREFIX_LEN,
)


def test_has_bilibili_cache_prefix_with_prefix():
    """Test when the file starts with the bilibili cache prefix."""
    mock_file = mock_open(read_data=BILIBILI_CACHE_PREFIX + b"some_video_data")
    with patch("pathlib.Path.open", mock_file):
        path = Path("dummy.m4s")
        result = has_bilibili_cache_prefix(path)

    assert result is True
    # mock_open was called with the path and mode
    mock_file.assert_called_once_with("rb")
    mock_file.return_value.read.assert_called_once_with(BILIBILI_CACHE_PREFIX_LEN)


def test_has_bilibili_cache_prefix_without_prefix():
    """Test when the file does not start with the prefix."""
    mock_file = mock_open(read_data=b"some_other_data")
    with patch("pathlib.Path.open", mock_file):
        result = has_bilibili_cache_prefix(Path("dummy.m4s"))

    assert result is False


def test_has_bilibili_cache_prefix_short_file():
    """Test when the file is shorter than the prefix length."""
    mock_file = mock_open(read_data=b"short")
    with patch("pathlib.Path.open", mock_file):
        result = has_bilibili_cache_prefix(Path("dummy.m4s"))

    assert result is False


def test_has_bilibili_cache_prefix_empty_file():
    """Test when the file is empty."""
    mock_file = mock_open(read_data=b"")
    with patch("pathlib.Path.open", mock_file):
        result = has_bilibili_cache_prefix(Path("dummy.m4s"))

    assert result is False
