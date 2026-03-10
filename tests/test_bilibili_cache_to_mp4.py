import json
import pytest
from pathlib import Path
from bilibili_cache_to_mp4 import read_json_with_fallback

def test_read_json_with_fallback_utf8(tmp_path: Path):
    file_path = tmp_path / "test_utf8.json"
    data = {"key": "value", "chinese": "测试"}
    file_path.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
    assert read_json_with_fallback(file_path) == data

def test_read_json_with_fallback_utf8_sig(tmp_path: Path):
    file_path = tmp_path / "test_utf8_sig.json"
    data = {"key": "value", "chinese": "测试"}
    file_path.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8-sig")
    assert read_json_with_fallback(file_path) == data

def test_read_json_with_fallback_gb18030(tmp_path: Path):
    file_path = tmp_path / "test_gb18030.json"
    data = {"key": "value", "chinese": "测试"}
    file_path.write_text(json.dumps(data, ensure_ascii=False), encoding="gb18030")
    assert read_json_with_fallback(file_path) == data

def test_read_json_with_fallback_invalid_json(tmp_path: Path):
    file_path = tmp_path / "test_invalid.json"
    file_path.write_text("{invalid json", encoding="utf-8")
    assert read_json_with_fallback(file_path) == {}

def test_read_json_with_fallback_empty_file(tmp_path: Path):
    file_path = tmp_path / "test_empty.json"
    file_path.write_text("", encoding="utf-8")
    assert read_json_with_fallback(file_path) == {}

def test_read_json_with_fallback_unsupported_encoding(tmp_path: Path):
    file_path = tmp_path / "test_utf16.json"
    data = {"key": "value", "chinese": "测试"}
    file_path.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-16")
    assert read_json_with_fallback(file_path) == {}

def test_read_json_with_fallback_file_not_found(tmp_path: Path):
    file_path = tmp_path / "non_existent.json"
    with pytest.raises(FileNotFoundError):
        read_json_with_fallback(file_path)
