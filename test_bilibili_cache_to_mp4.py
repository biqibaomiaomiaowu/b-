import unittest
from pathlib import Path
from bilibili_cache_to_mp4 import ensure_unique_path

class TestEnsureUniquePath(unittest.TestCase):
    def test_empty_set(self):
        used_paths = set()
        path = Path("video.mp4")
        result = ensure_unique_path(path, used_paths)
        self.assertEqual(result, Path("video.mp4"))
        self.assertIn(str(result).lower(), used_paths)

    def test_already_exists(self):
        path = Path("video.mp4")
        used_paths = {str(path).lower()}
        result = ensure_unique_path(path, used_paths)
        self.assertEqual(result, Path("video_1.mp4"))
        self.assertIn(str(result).lower(), used_paths)
        self.assertEqual(len(used_paths), 2)

    def test_multiple_exist(self):
        used_paths = {
            str(Path("video.mp4")).lower(),
            str(Path("video_1.mp4")).lower(),
            str(Path("video_2.mp4")).lower()
        }
        path = Path("video.mp4")
        result = ensure_unique_path(path, used_paths)
        self.assertEqual(result, Path("video_3.mp4"))
        self.assertIn(str(result).lower(), used_paths)
        self.assertEqual(len(used_paths), 4)

    def test_case_insensitive(self):
        used_paths = {str(Path("ViDeO.Mp4")).lower()}
        path = Path("video.mp4")
        result = ensure_unique_path(path, used_paths)
        self.assertEqual(result, Path("video_1.mp4"))
        self.assertIn(str(result).lower(), used_paths)

    def test_with_directory(self):
        base_dir = Path("/some/dir")
        path = base_dir / "video.mp4"
        used_paths = {str(path).lower()}
        result = ensure_unique_path(path, used_paths)
        self.assertEqual(result, base_dir / "video_1.mp4")
        self.assertIn(str(result).lower(), used_paths)

    def test_different_extensions(self):
        used_paths = {str(Path("video.mp4")).lower()}
        path = Path("video.mkv")
        result = ensure_unique_path(path, used_paths)
        self.assertEqual(result, Path("video.mkv"))
        self.assertIn(str(result).lower(), used_paths)
        self.assertEqual(len(used_paths), 2)

    def test_no_extension(self):
        used_paths = {str(Path("video")).lower()}
        path = Path("video")
        result = ensure_unique_path(path, used_paths)
        self.assertEqual(result, Path("video_1"))
        self.assertIn(str(result).lower(), used_paths)

    def test_multiple_suffixes(self):
        used_paths = {str(Path("archive.tar.gz")).lower()}
        path = Path("archive.tar.gz")
        result = ensure_unique_path(path, used_paths)
        # Pathlib's stem for "archive.tar.gz" is "archive.tar" and suffix is ".gz"
        self.assertEqual(result, Path("archive.tar_1.gz"))
        self.assertIn(str(result).lower(), used_paths)

if __name__ == '__main__':
    unittest.main()
