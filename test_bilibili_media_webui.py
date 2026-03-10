import unittest
from bilibili_media_webui import strip_trailing_url_punctuation, TRAILING_URL_PUNCTUATION

class TestStripTrailingUrlPunctuation(unittest.TestCase):
    def test_no_trailing_punctuation(self):
        self.assertEqual(
            strip_trailing_url_punctuation("https://bilibili.com/video/BV12345678"),
            "https://bilibili.com/video/BV12345678"
        )

    def test_single_trailing_punctuation(self):
        self.assertEqual(
            strip_trailing_url_punctuation("https://bilibili.com/video/BV12345678)"),
            "https://bilibili.com/video/BV12345678"
        )
        self.assertEqual(
            strip_trailing_url_punctuation("https://bilibili.com/video/BV12345678】"),
            "https://bilibili.com/video/BV12345678"
        )
        self.assertEqual(
            strip_trailing_url_punctuation("https://bilibili.com/video/BV12345678?"),
            "https://bilibili.com/video/BV12345678"
        )

    def test_multiple_trailing_punctuations(self):
        self.assertEqual(
            strip_trailing_url_punctuation("https://bilibili.com/video/BV12345678)！?"),
            "https://bilibili.com/video/BV12345678"
        )
        self.assertEqual(
            strip_trailing_url_punctuation("https://bilibili.com/video/BV12345678】。；"),
            "https://bilibili.com/video/BV12345678"
        )

    def test_punctuation_in_middle(self):
        self.assertEqual(
            strip_trailing_url_punctuation("https://bilibili.com/video/BV12345678?p=1"),
            "https://bilibili.com/video/BV12345678?p=1"
        )
        self.assertEqual(
            strip_trailing_url_punctuation("https://bilibili.com/video/BV12345678?p=1)"),
            "https://bilibili.com/video/BV12345678?p=1"
        )

    def test_empty_string(self):
        self.assertEqual(strip_trailing_url_punctuation(""), "")

    def test_only_punctuation(self):
        self.assertEqual(strip_trailing_url_punctuation(")]}>"), "")
        self.assertEqual(strip_trailing_url_punctuation("?！，。"), "")

    def test_all_defined_punctuation(self):
        for char in TRAILING_URL_PUNCTUATION:
            self.assertEqual(
                strip_trailing_url_punctuation(f"https://example.com{char}"),
                "https://example.com"
            )

if __name__ == '__main__':
    unittest.main()
