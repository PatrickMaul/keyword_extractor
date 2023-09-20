from unittest import TestCase
# Test class
from src.keyword_extractor import KeywordExtractor
from src.utils import Tokenizer, POSTagger, Lemmatizer
from nltk.stem import PorterStemmer


TEST_TEXT: str = '''JavaScript: Empowering Modern Web Development
JavaScript, often abbreviated as JS, stands as a cornerstone of modern web development. This versatile and essential programming language empowers developers to craft websites that transcend static content, ushering in interactivity, enhanced functionality, and dynamic features. Whether the aim is to create a responsive user interface, validate user input, or seamlessly fetch and display real-time data from a server, JavaScript is the formidable force behind these feats.
At the heart of JavaScript's appeal lies its capacity to execute directly within web browsers, earning its classification as a client-side scripting language. This crucial distinction ensures that users can interact with websites in ways that were once deemed impossible without constant server-side requests. JavaScript's capability to manipulate the Document Object Model (DOM) of a web page facilitates the magic of on-the-fly updates and responsive user interactions, revolutionizing the web experience.
But JavaScript's influence extends far beyond its role as a dynamic front-end tool. Its vast ecosystem of libraries and frameworks, exemplified by the likes of React, Angular, and Vue.js, elevates the development process to new heights. These resources furnish developers with pre-built components and well-defined structures, significantly reducing development time while upholding best practices in web development. 
JavaScript's dominance isn't confined to the browser; it has also found a prominent place on the server-side, largely thanks to the advent of Node.js. This innovation empowers developers to utilize the same language for both client and server-side development, fostering consistency and efficiency across web applications.
In summary, JavaScript reigns supreme as the foundation of contemporary web development. Its adaptability, user-friendliness, and robust community support have made it an indispensable tool for crafting web experiences that are both dynamic and interactive. 
Whether you're a novice embarking on your coding journey or a seasoned developer seeking to broaden your horizons, JavaScript stands as the gateway to a realm of endless possibilities in the dynamic world of web development. Its influence is undeniable, and its future, as the bedrock of the web, is bright.
'''


class TestKeywordExtractor(TestCase):
    def set_up_word_frequency_keyword_extractor(self) -> None:
        self.KWE: KeywordExtractor = KeywordExtractor(txt=TEST_TEXT, method='wf')

    def test_init_returns_correct_word_frequency_keyword_extractor_instance(self):
        # Setup
        self.set_up_word_frequency_keyword_extractor()

        # Asserts
        self.assertEqual(TEST_TEXT, self.KWE.txt)
        self.assertEqual('wf', self.KWE.method)
        self.assertIsNotNone(self.KWE._tokenizer)
        self.assertIsInstance(self.KWE._tokenizer, Tokenizer)
        self.assertIsNotNone(self.KWE._pos_tagger)
        self.assertIsInstance(self.KWE._pos_tagger, POSTagger)
        self.assertIsNotNone(self.KWE._lemmatizer)
        self.assertIsInstance(self.KWE._lemmatizer, Lemmatizer)
        self.assertIsNotNone(self.KWE._stemmer)
        self.assertIsInstance(self.KWE._stemmer, PorterStemmer)
