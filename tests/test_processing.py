import unittest

from asi_core.processing import process_reflection


class TestProcessReflection(unittest.TestCase):
    def test_process_reflection_structure(self):
        raw_text = "Dies ist ein Test-Reflexionstext."
        result = process_reflection(raw_text)
        self.assertIsInstance(result, dict)
        self.assertIn("type", result)
        self.assertIn("timestamp", result)
        self.assertIn("text_content_anonymized", result)
        self.assertIn("tags", result)
        self.assertIn("context", result)
        self.assertEqual(result["type"], "reflection")
        self.assertEqual(result["text_content_anonymized"], raw_text)
        self.assertIsInstance(result["tags"], list)
        self.assertIsInstance(result["context"], dict)


if __name__ == "__main__":
    unittest.main()
