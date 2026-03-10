import unittest
from bilibili_media_webui import normalize_page_spec

class TestNormalizePageSpec(unittest.TestCase):
    def test_empty_or_whitespace(self):
        self.assertEqual(normalize_page_spec(""), "")
        self.assertEqual(normalize_page_spec("   "), "")
        self.assertEqual(normalize_page_spec("\t\n"), "")

    def test_special_keywords(self):
        # ALL keyword
        self.assertEqual(normalize_page_spec("ALL"), "ALL")
        self.assertEqual(normalize_page_spec("all"), "ALL")
        self.assertEqual(normalize_page_spec(" All "), "ALL")
        self.assertEqual(normalize_page_spec("\tAlL\n"), "ALL")

        # LAST keyword
        self.assertEqual(normalize_page_spec("LAST"), "LAST")
        self.assertEqual(normalize_page_spec("last"), "LAST")
        self.assertEqual(normalize_page_spec("  Last  "), "LAST")
        self.assertEqual(normalize_page_spec("lASt"), "LAST")

    def test_page_ranges_and_lists(self):
        self.assertEqual(normalize_page_spec("1"), "1")
        self.assertEqual(normalize_page_spec("1,2,3"), "1,2,3")
        self.assertEqual(normalize_page_spec("1, 2, 3"), "1,2,3")
        self.assertEqual(normalize_page_spec("1 - 5"), "1-5")
        self.assertEqual(normalize_page_spec("  1 - 5, 8, 10 - 12  "), "1-5,8,10-12")
        self.assertEqual(normalize_page_spec("1\t-\n5"), "1-5")

if __name__ == '__main__':
    unittest.main()
