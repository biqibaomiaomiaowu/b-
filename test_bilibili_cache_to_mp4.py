import pytest
from pathlib import Path
from bilibili_cache_to_mp4 import find_cache_dirs

def test_find_cache_dirs_path_not_exists(tmp_path):
    non_existent_path = tmp_path / "does_not_exist"
    with pytest.raises(FileNotFoundError, match="路径不存在"):
        find_cache_dirs(non_existent_path)

def test_find_cache_dirs_not_a_directory(tmp_path):
    file_path = tmp_path / "test.txt"
    file_path.touch()
    with pytest.raises(NotADirectoryError, match="请输入目录路径"):
        find_cache_dirs(file_path)

def test_find_cache_dirs_direct_m4s(tmp_path):
    # Setup directory with .m4s directly inside
    m4s_file = tmp_path / "video.m4s"
    m4s_file.touch()

    result = find_cache_dirs(tmp_path)
    assert result == [tmp_path]

def test_find_cache_dirs_nested_m4s(tmp_path):
    # Setup directory with nested subdirectories containing .m4s
    subdir1 = tmp_path / "b_subdir"
    subdir1.mkdir()
    (subdir1 / "audio.m4s").touch()

    subdir2 = tmp_path / "a_subdir"
    subdir2.mkdir()
    (subdir2 / "video.m4s").touch()

    subdir3 = tmp_path / "c_subdir_no_m4s"
    subdir3.mkdir()
    (subdir3 / "test.txt").touch()

    result = find_cache_dirs(tmp_path)
    # The result should be sorted by Path
    assert result == [subdir2, subdir1]

def test_find_cache_dirs_no_m4s(tmp_path):
    # Setup directory with no .m4s files
    (tmp_path / "test.txt").touch()
    subdir1 = tmp_path / "subdir"
    subdir1.mkdir()
    (subdir1 / "image.jpg").touch()

    result = find_cache_dirs(tmp_path)
    assert result == []
