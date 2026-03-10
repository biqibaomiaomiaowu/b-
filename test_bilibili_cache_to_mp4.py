import pytest
from unittest.mock import patch, MagicMock
from bilibili_cache_to_mp4 import resolve_executable

def test_resolve_executable_found_by_which():
    with patch('bilibili_cache_to_mp4.shutil.which') as mock_which:
        mock_which.return_value = '/usr/bin/ffmpeg'
        result = resolve_executable('ffmpeg', 'FFmpeg')
        assert result == '/usr/bin/ffmpeg'
        mock_which.assert_called_once_with('ffmpeg')

def test_resolve_executable_found_by_path():
    with patch('bilibili_cache_to_mp4.shutil.which') as mock_which, \
         patch('bilibili_cache_to_mp4.Path') as mock_path_cls:

        mock_which.return_value = None

        mock_candidate = MagicMock()
        mock_candidate.exists.return_value = True
        mock_candidate.__str__.return_value = '/home/user/bin/ffmpeg'

        mock_path_instance = MagicMock()
        mock_path_instance.expanduser.return_value = mock_candidate
        mock_path_cls.return_value = mock_path_instance

        result = resolve_executable('~/bin/ffmpeg', 'FFmpeg')

        assert result == '/home/user/bin/ffmpeg'
        mock_which.assert_called_once_with('~/bin/ffmpeg')
        mock_path_cls.assert_called_once_with('~/bin/ffmpeg')

def test_resolve_executable_not_found():
    with patch('bilibili_cache_to_mp4.shutil.which') as mock_which, \
         patch('bilibili_cache_to_mp4.Path') as mock_path_cls:

        mock_which.return_value = None

        mock_candidate = MagicMock()
        mock_candidate.exists.return_value = False

        mock_path_instance = MagicMock()
        mock_path_instance.expanduser.return_value = mock_candidate
        mock_path_cls.return_value = mock_path_instance

        with pytest.raises(FileNotFoundError) as exc_info:
            resolve_executable('not_exist', 'Not Exist')

        assert '未找到 Not Exist: not_exist' in str(exc_info.value)
