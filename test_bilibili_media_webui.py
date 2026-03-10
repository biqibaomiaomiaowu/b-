import unittest
from bilibili_media_webui import extract_bilibili_identifier

class TestExtractBilibiliIdentifier(unittest.TestCase):
    def test_bv_id(self):
        # Valid BV ID
        self.assertEqual(extract_bilibili_identifier("BV1xx411c7mD"), ("bv", "BV1xx411c7mD"))
        # Case insensitivity (matches pattern but returns standardized BV)
        self.assertEqual(extract_bilibili_identifier("bv1xx411c7md"), ("bv", "BV1xx411c7md"))
        self.assertEqual(extract_bilibili_identifier("Bv1xx411c7md"), ("bv", "BV1xx411c7md"))
        self.assertEqual(extract_bilibili_identifier("bV1xx411c7md"), ("bv", "BV1xx411c7md"))

    def test_av_id(self):
        # Valid av ID
        self.assertEqual(extract_bilibili_identifier("av12345678"), ("av", "12345678"))
        # Case insensitivity
        self.assertEqual(extract_bilibili_identifier("AV12345678"), ("av", "12345678"))
        self.assertEqual(extract_bilibili_identifier("aV12345678"), ("av", "12345678"))

    def test_ep_id(self):
        # Valid ep ID
        self.assertEqual(extract_bilibili_identifier("ep12345"), ("ep", "12345"))
        # Case insensitivity
        self.assertEqual(extract_bilibili_identifier("EP12345"), ("ep", "12345"))

    def test_id_in_url(self):
        # Extracted from URL
        self.assertEqual(extract_bilibili_identifier("https://www.bilibili.com/video/BV1xx411c7mD/"), ("bv", "BV1xx411c7mD"))
        self.assertEqual(extract_bilibili_identifier("https://www.bilibili.com/video/av12345678"), ("av", "12345678"))
        self.assertEqual(extract_bilibili_identifier("https://www.bilibili.com/bangumi/play/ep12345"), ("ep", "12345"))

    def test_id_with_surrounding_text(self):
        self.assertEqual(extract_bilibili_identifier("Check out this video: BV1xx411c7mD!"), ("bv", "BV1xx411c7mD"))
        self.assertEqual(extract_bilibili_identifier("My favorite is av12345678"), ("av", "12345678"))
        self.assertEqual(extract_bilibili_identifier("Watching ep12345 now"), ("ep", "12345"))

    def test_invalid_target(self):
        self.assertEqual(extract_bilibili_identifier("just some text"), ("", ""))
        self.assertEqual(extract_bilibili_identifier(""), ("", ""))
        self.assertEqual(extract_bilibili_identifier("https://www.bilibili.com/"), ("", ""))
        # Too short for BV
        self.assertEqual(extract_bilibili_identifier("BV123"), ("", ""))
        # Missing numbers
        self.assertEqual(extract_bilibili_identifier("av"), ("", ""))

if __name__ == '__main__':
    unittest.main()
