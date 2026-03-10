import unittest
from bilibili_media_webui import normalize_video_target

class TestNormalizeVideoTarget(unittest.TestCase):
    def test_empty_string(self):
        self.assertEqual(normalize_video_target(""), "")
        self.assertEqual(normalize_video_target("   "), "")

    def test_url_match(self):
        self.assertEqual(
            normalize_video_target("https://www.bilibili.com/video/BV1xx411c7mD"),
            "https://www.bilibili.com/video/BV1xx411c7mD"
        )
        self.assertEqual(
            normalize_video_target("http://b23.tv/xxx"),
            "http://b23.tv/xxx"
        )

    def test_url_with_trailing_punctuation(self):
        self.assertEqual(
            normalize_video_target("https://www.bilibili.com/video/BV1xx411c7mD)"),
            "https://www.bilibili.com/video/BV1xx411c7mD"
        )
        self.assertEqual(
            normalize_video_target("https://b23.tv/xxx】"),
            "https://b23.tv/xxx"
        )
        self.assertEqual(
            normalize_video_target("https://b23.tv/xxx?p=1;"),
            "https://b23.tv/xxx?p=1"
        )
        self.assertEqual(
            normalize_video_target("https://b23.tv/xxx?p=1?"),
            "https://b23.tv/xxx?p=1"
        )

    def test_bilibili_id_bv(self):
        self.assertEqual(normalize_video_target("BV1xx411c7mD"), "BV1xx411c7mD")
        self.assertEqual(normalize_video_target("bv1xx411c7md"), "BV1xx411c7md")

    def test_bilibili_id_av(self):
        self.assertEqual(normalize_video_target("av123456"), "av123456")
        self.assertEqual(normalize_video_target("AV123456"), "av123456")

    def test_bilibili_id_ep_ss(self):
        self.assertEqual(normalize_video_target("ep12345"), "ep12345")
        self.assertEqual(normalize_video_target("EP12345"), "ep12345")
        self.assertEqual(normalize_video_target("ss12345"), "ss12345")
        self.assertEqual(normalize_video_target("SS12345"), "ss12345")

    def test_embedded_bilibili_id(self):
        self.assertEqual(normalize_video_target("look at this video BV1xx411c7mD!"), "BV1xx411c7mD")
        self.assertEqual(normalize_video_target("video ID: av123456"), "av123456")

    def test_embedded_url(self):
        self.assertEqual(normalize_video_target("look at this url https://b23.tv/xxx"), "https://b23.tv/xxx")

    def test_plain_text(self):
        self.assertEqual(normalize_video_target("hello world"), "hello world")
        self.assertEqual(normalize_video_target("just some random text"), "just some random text")

if __name__ == '__main__':
    unittest.main()
