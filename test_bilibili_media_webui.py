import unittest
from bilibili_media_webui import format_duration_text

class TestFormatDurationText(unittest.TestCase):
    def test_format_duration_text(self):
        # None/Empty cases
        self.assertEqual(format_duration_text(None), "")
        self.assertEqual(format_duration_text(0), "")
        self.assertEqual(format_duration_text(-1), "")

        # Small seconds
        self.assertEqual(format_duration_text(5), "0:05")
        self.assertEqual(format_duration_text(59), "0:59")

        # Minutes
        self.assertEqual(format_duration_text(60), "1:00")
        self.assertEqual(format_duration_text(61), "1:01")
        self.assertEqual(format_duration_text(3599), "59:59")

        # Hours
        self.assertEqual(format_duration_text(3600), "1:00:00")
        self.assertEqual(format_duration_text(3661), "1:01:01")
        self.assertEqual(format_duration_text(7200), "2:00:00")
        self.assertEqual(format_duration_text(360000), "100:00:00")

        # Types
        self.assertEqual(format_duration_text("120"), "2:00")
        self.assertEqual(format_duration_text(120.5), "2:00")

        # Invalid
        self.assertEqual(format_duration_text("abc"), "")

if __name__ == "__main__":
    unittest.main()
