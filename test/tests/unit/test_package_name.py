from unittest import TestCase

# Test class
from keyword_extractor import KeywordExtractor
from utils import Tokenizer, POSTagger, Lemmatizer
from nltk.stem import PorterStemmer

with open("./assets/dummy-text.txt", "r") as file:
    TEST_TEXT: str = file.read()


class TestKeywordExtractor(TestCase):
    def set_up_word_frequency_keyword_extractor(self) -> None:
        self.KWE: KeywordExtractor = KeywordExtractor(txt=TEST_TEXT, method="wf")

    def test_init_returns_correct_word_frequency_keyword_extractor_instance(self):
        # Setup
        self.set_up_word_frequency_keyword_extractor()

        # Asserts
        self.assertEqual(TEST_TEXT, self.KWE.txt)
        self.assertEqual("wf", self.KWE.method)
        self.assertIsNotNone(self.KWE._tokenizer)
        self.assertIsInstance(self.KWE._tokenizer, Tokenizer)
        self.assertIsNotNone(self.KWE._pos_tagger)
        self.assertIsInstance(self.KWE._pos_tagger, POSTagger)
        self.assertIsNotNone(self.KWE._lemmatizer)
        self.assertIsInstance(self.KWE._lemmatizer, Lemmatizer)
        self.assertIsNotNone(self.KWE._stemmer)
        self.assertIsInstance(self.KWE._stemmer, PorterStemmer)
