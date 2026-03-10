import pytest
from pathlib import Path
import sys

# Add the root directory to sys.path so we can import bilibili_cache_to_mp4
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from bilibili_cache_to_mp4 import ensure_unique_path

def test_ensure_unique_path_empty_set():
    """Test when the path is not in used_paths."""
    used_paths = set()
    path = Path("test.mp4")
    result = ensure_unique_path(path, used_paths)
    assert result == Path("test.mp4")
    assert used_paths == {"test.mp4"}

def test_ensure_unique_path_already_used():
    """Test when the path is already in used_paths."""
    used_paths = {"test.mp4"}
    path = Path("test.mp4")
    result = ensure_unique_path(path, used_paths)
    assert result == Path("test_1.mp4")
    assert used_paths == {"test.mp4", "test_1.mp4"}

def test_ensure_unique_path_multiple_used():
    """Test when the path and its _1 variant are already in used_paths."""
    used_paths = {"test.mp4", "test_1.mp4"}
    path = Path("test.mp4")
    result = ensure_unique_path(path, used_paths)
    assert result == Path("test_2.mp4")
    assert used_paths == {"test.mp4", "test_1.mp4", "test_2.mp4"}

def test_ensure_unique_path_case_insensitive():
    """Test that the checking is case-insensitive."""
    used_paths = {"test.mp4"}
    path = Path("TEST.mp4")
    result = ensure_unique_path(path, used_paths)
    # The output path shouldn't be lowercased, just the check is insensitive
    assert result == Path("TEST_1.mp4")
    assert used_paths == {"test.mp4", "test_1.mp4"}

def test_ensure_unique_path_case_insensitive_multiple():
    """Test case-insensitivity with multiple pre-existing cases."""
    used_paths = {"test.mp4", "test_1.mp4"}
    path = Path("TeSt.mp4")
    result = ensure_unique_path(path, used_paths)
    assert result == Path("TeSt_2.mp4")
    assert used_paths == {"test.mp4", "test_1.mp4", "test_2.mp4"}

def test_ensure_unique_path_different_suffix():
    """Test with a different extension."""
    used_paths = {"video.mkv"}
    path = Path("video.mkv")
    result = ensure_unique_path(path, used_paths)
    assert result == Path("video_1.mkv")
    assert used_paths == {"video.mkv", "video_1.mkv"}

def test_ensure_unique_path_complex_name():
    """Test with a complex file name containing dots."""
    used_paths = {"my.video.v1.mp4", "my.video.v1_1.mp4"}
    path = Path("my.video.v1.mp4")
    result = ensure_unique_path(path, used_paths)
    assert result == Path("my.video.v1_2.mp4")
    assert used_paths == {"my.video.v1.mp4", "my.video.v1_1.mp4", "my.video.v1_2.mp4"}

def test_ensure_unique_path_absolute_path():
    """Test with an absolute path."""
    if os.name == 'nt':
        base = "C:\\videos"
    else:
        base = "/videos"

    p1 = str(Path(base) / "test.mp4").lower()
    used_paths = {p1}
    path = Path(base) / "test.mp4"
    result = ensure_unique_path(path, used_paths)
    assert result == Path(base) / "test_1.mp4"
    assert used_paths == {p1, str(Path(base) / "test_1.mp4").lower()}
