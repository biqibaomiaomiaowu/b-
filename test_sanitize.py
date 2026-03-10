import pytest
from bilibili_cache_to_mp4 import sanitize_filename

def test_sanitize_filename():
    assert sanitize_filename("normal_name", "fallback") == "normal_name"
    assert sanitize_filename("invalid<name>", "fallback") == "invalid_name_"
    assert sanitize_filename("   invalid<name>  ", "fallback") == "invalid_name_"
    assert sanitize_filename("a\\b/c:d*e?f\"g<h>i|j", "fallback") == "a_b_c_d_e_f_g_h_i_j"
    assert sanitize_filename("CON", "fallback") == "_CON"
    assert sanitize_filename("PRN. ", "fallback") == "_PRN"
    assert sanitize_filename("", "fallback") == "fallback"
    assert sanitize_filename(None, "fallback") == "fallback"
    assert sanitize_filename("  ", "fallback") == "fallback"
