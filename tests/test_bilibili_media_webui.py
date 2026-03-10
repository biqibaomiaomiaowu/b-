import pytest
import re
from unittest.mock import patch

from backend.bilibili import extract_qualities

def test_extract_qualities_empty():
    """Test extracting from empty string or string without matches."""
    assert extract_qualities("") == []
    assert extract_qualities("no quality here") == []

def test_extract_qualities_single():
    """Test extracting a single quality."""
    assert extract_qualities("这是一些文本 1080P 高清 更多文本") == ["1080P 高清"]

def test_extract_qualities_multiple():
    """Test extracting multiple qualities."""
    assert extract_qualities("视频有 1080P 高码率 和 720P 高清 选项") == ["1080P 高码率", "720P 高清"]

def test_extract_qualities_duplicates():
    """Test that duplicates are removed."""
    assert extract_qualities("1080P 高清, 1080P 高清") == ["1080P 高清"]
    assert extract_qualities("1080P 高清 和 720P 高清, 以及 1080P 高清") == ["1080P 高清", "720P 高清"]

def test_extract_qualities_order():
    """
    Test that qualities are ordered according to VALID_QUALITIES order.
    If 1080P appears before 720P in the string but 1080P is first in VALID_QUALITIES,
    it should follow VALID_QUALITIES order.
    """
    # 720P is first in text, 1080P is second
    assert extract_qualities("720P 高清 和 1080P 高清") == ["1080P 高清", "720P 高清"]

@patch('backend.bilibili.VALID_QUALITIES', ["Quality A", "Quality B", "Quality C"])
def test_extract_qualities_mocked():
    """Test with a mocked list of valid qualities to ensure the underlying logic works."""
    # Test deduplication and order
    text = "Here is Quality C, Quality B, and Quality A and Quality B again."
    # Patterns order is A, B, C. So it should find A, then B, then C.
    assert extract_qualities(text) == ["Quality A", "Quality B", "Quality C"]
