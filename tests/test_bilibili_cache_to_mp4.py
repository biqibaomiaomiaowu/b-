import pytest
from bilibili_cache_to_mp4 import sanitize_filename

def test_sanitize_filename_normal():
    # Normal valid filenames are returned unchanged
    assert sanitize_filename("valid_filename", "fallback") == "valid_filename"
    assert sanitize_filename("hello world", "fallback") == "hello world"
    assert sanitize_filename("12345", "fallback") == "12345"

def test_sanitize_filename_invalid_chars():
    # Invalid characters (<>:"/\|?*) are replaced with underscores (_)
    assert sanitize_filename('hello<world>', "fallback") == "hello_world_"
    assert sanitize_filename('a:b"c/d\\e|f?g*h', "fallback") == "a_b_c_d_e_f_g_h"
    assert sanitize_filename('file/name: test?', "fallback") == "file_name_ test_"

def test_sanitize_filename_whitespace():
    # Multiple consecutive spaces are reduced to a single space
    assert sanitize_filename("hello   world", "fallback") == "hello world"
    assert sanitize_filename("  leading  and  trailing  ", "fallback") == "leading and trailing"
    # Leading/trailing whitespace and trailing dots are removed
    assert sanitize_filename("file name . .", "fallback") == "file name"
    assert sanitize_filename("file name...", "fallback") == "file name"
    assert sanitize_filename("file name. . .", "fallback") == "file name"

def test_sanitize_filename_fallback():
    # Null (None), empty strings (""), or strings that become empty after cleaning return the fallback value
    assert sanitize_filename(None, "fallback") == "fallback" # type: ignore
    assert sanitize_filename("", "fallback") == "fallback"
    assert sanitize_filename("   ", "fallback") == "fallback"
    assert sanitize_filename(".", "fallback") == "fallback"
    assert sanitize_filename(" . . . ", "fallback") == "fallback"

def test_sanitize_filename_windows_reserved():
    # Exact Windows reserved names are prefixed with an underscore
    reserved_names = [
        "CON", "PRN", "AUX", "NUL",
        "COM1", "COM2", "COM3", "COM4", "COM5", "COM6", "COM7", "COM8", "COM9",
        "LPT1", "LPT2", "LPT3", "LPT4", "LPT5", "LPT6", "LPT7", "LPT8", "LPT9"
    ]
    for name in reserved_names:
        assert sanitize_filename(name, "fallback") == f"_{name}"
        assert sanitize_filename(name.lower(), "fallback") == f"_{name.lower()}"

    # Non-exact matches should not be prefixed
    assert sanitize_filename("CON.txt", "fallback") == "CON.txt"
    assert sanitize_filename("my_CON", "fallback") == "my_CON"
    assert sanitize_filename("CON10", "fallback") == "CON10"
