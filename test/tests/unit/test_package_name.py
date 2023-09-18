from unittest import TestCase

# Test class
from src.keyword_extractor import KeywordExtractor


class TestKeywordExtractor(TestCase):
    def test_init_returns_correct_instance(self):
        # Setup
        kwe = KeywordExtractor()

        # Asserts
        self.assertEqual(kwe.foo, "bar")
