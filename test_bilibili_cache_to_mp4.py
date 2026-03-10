import pytest
from unittest.mock import patch
from pathlib import Path

from bilibili_cache_to_mp4 import guess_ffprobe

def test_guess_ffprobe_with_explicit_calls_resolve_executable():
    with patch("bilibili_cache_to_mp4.resolve_executable") as mock_resolve:
        mock_resolve.return_value = "/path/to/explicit/ffprobe"
        result = guess_ffprobe("/path/to/ffmpeg", "explicit_ffprobe")
        assert result == "/path/to/explicit/ffprobe"
        mock_resolve.assert_called_once_with("explicit_ffprobe", "ffprobe")

def test_guess_ffprobe_with_sibling_exists(tmp_path):
    # Setup tmp_path with a fake ffmpeg and a fake ffprobe
    ffmpeg_file = tmp_path / "ffmpeg.exe"
    ffmpeg_file.touch()

    ffprobe_file = tmp_path / "ffprobe.exe"
    ffprobe_file.touch()

    result = guess_ffprobe(str(ffmpeg_file), None)
    assert result == str(ffprobe_file)

def test_guess_ffprobe_sibling_not_exists_fallback_to_which(tmp_path):
    # Setup tmp_path with a fake ffmpeg but no ffprobe
    ffmpeg_file = tmp_path / "ffmpeg.exe"
    ffmpeg_file.touch()

    with patch("bilibili_cache_to_mp4.shutil.which") as mock_which:
        mock_which.return_value = "/system/path/ffprobe"
        result = guess_ffprobe(str(ffmpeg_file), None)
        assert result == "/system/path/ffprobe"
        mock_which.assert_called_once_with("ffprobe")

def test_guess_ffprobe_ffmpeg_not_exists_fallback_to_which():
    with patch("bilibili_cache_to_mp4.shutil.which") as mock_which:
        mock_which.return_value = "/system/path/ffprobe"
        result = guess_ffprobe("/non_existent/ffmpeg", None)
        assert result == "/system/path/ffprobe"
        mock_which.assert_called_once_with("ffprobe")

def test_guess_ffprobe_which_fails_returns_empty_string():
    with patch("bilibili_cache_to_mp4.shutil.which") as mock_which:
        mock_which.return_value = None
        result = guess_ffprobe("/non_existent/ffmpeg", None)
        assert result == ""
        mock_which.assert_called_once_with("ffprobe")
