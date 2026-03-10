import pytest
from unittest.mock import patch, MagicMock
from pathlib import Path
from backend.bilibili import get_request_cookie_text
from backend.constants import DEFAULT_BBDOWN

def test_explicit_cookie_present():
    payload = {"cookie": "SESSDATA=1234; bili_jct=5678;"}
    result = get_request_cookie_text(payload)
    assert result == "SESSDATA=1234; bili_jct=5678;"

def test_explicit_cookie_empty_string():
    payload = {"cookie": "  "}
    # Should fall through to checking files
    with patch("backend.bilibili.get_bbdown_data_candidates") as mock_candidates:
        mock_candidates.return_value = []
        result = get_request_cookie_text(payload)
        assert result == ""
        mock_candidates.assert_called_once_with(DEFAULT_BBDOWN)

def test_explicit_cookie_none():
    payload = {}
    with patch("backend.bilibili.get_bbdown_data_candidates") as mock_candidates:
        mock_candidates.return_value = []
        result = get_request_cookie_text(payload)
        assert result == ""
        mock_candidates.assert_called_once_with(DEFAULT_BBDOWN)

def test_custom_bbdown_path():
    payload = {"bbdown_path": "/custom/path/BBDown"}
    with patch("backend.bilibili.get_bbdown_data_candidates") as mock_candidates:
        mock_candidates.return_value = []
        result = get_request_cookie_text(payload)
        assert result == ""
        mock_candidates.assert_called_once_with("/custom/path/BBDown")

@patch("backend.bilibili.get_bbdown_data_candidates")
@patch("backend.bilibili.read_cookie_data_file")
def test_valid_cookie_file_found(mock_read_cookie, mock_candidates):
    payload = {}

    mock_path1 = MagicMock(spec=Path)
    mock_path1.exists.return_value = False

    mock_path2 = MagicMock(spec=Path)
    mock_path2.exists.return_value = True

    mock_candidates.return_value = [mock_path1, mock_path2]

    # Return valid cookie text and dict
    mock_read_cookie.return_value = ("SESSDATA=file_cookie;", {"SESSDATA": "file_cookie"})

    result = get_request_cookie_text(payload)

    assert result == "SESSDATA=file_cookie;"
    mock_read_cookie.assert_called_once_with(mock_path2)

@patch("backend.bilibili.get_bbdown_data_candidates")
@patch("backend.bilibili.read_cookie_data_file")
def test_file_exists_but_invalid_cookie(mock_read_cookie, mock_candidates):
    payload = {}

    mock_path1 = MagicMock(spec=Path)
    mock_path1.exists.return_value = True

    mock_path2 = MagicMock(spec=Path)
    mock_path2.exists.return_value = True

    mock_candidates.return_value = [mock_path1, mock_path2]

    # First file has empty dict
    # Second file has valid dict
    mock_read_cookie.side_effect = [
        ("invalid_format", {}),
        ("SESSDATA=valid_cookie;", {"SESSDATA": "valid_cookie"})
    ]

    result = get_request_cookie_text(payload)

    assert result == "SESSDATA=valid_cookie;"
    assert mock_read_cookie.call_count == 2
    mock_read_cookie.assert_any_call(mock_path1)
    mock_read_cookie.assert_any_call(mock_path2)

@patch("backend.bilibili.get_bbdown_data_candidates")
@patch("backend.bilibili.read_cookie_data_file")
def test_no_valid_files_found(mock_read_cookie, mock_candidates):
    payload = {}

    mock_path1 = MagicMock(spec=Path)
    mock_path1.exists.return_value = True

    mock_candidates.return_value = [mock_path1]

    # File exists but contains no valid cookies
    mock_read_cookie.return_value = ("", {})

    result = get_request_cookie_text(payload)

    assert result == ""
    mock_read_cookie.assert_called_once_with(mock_path1)
