import re
import nltk
from nltk.stem import WordNetLemmatizer
from nltk.corpus import stopwords
from typing import Union, Dict, List, Any


def flatten_nested_lists(collection: Union[List[str], List[List[str]]]) -> List[Any]:
    flatted_list = []  # Set empty flatted list

    for value in collection:
        if isinstance(value, List) and not isinstance(value, str):  # `value` is a list and not a string
            for x in flatten_nested_lists(value):
                flatted_list.append(x)
        else:  # Otherwise `value` must be a string
            flatted_list.append(value)

    # Return the flatted list
    return flatted_list


def remove_duplicates(collection: List[str]) -> List[str]:
    duplicate_free_result = []

    for word in collection:
        if word not in duplicate_free_result:
            duplicate_free_result.append(word)

    return duplicate_free_result


def remove_stop_words(collection: List[List[str]], lang: str = "english"):
    stop_words: set = set(stopwords.words(lang))
    filtered_words_per_sentence = []

    for sentence in collection:
        filtered_words = []

        for word in sentence:
            if word.lower() not in stop_words:  # and word.lower() not in self.signs_to_remove:
                filtered_words.append(word)
        filtered_words_per_sentence.append(filtered_words)

    return filtered_words_per_sentence


class Tokenizer:
    def __init__(self) -> None:
        pass

    @staticmethod
    def text_to_paragraphs(txt: Union[str, None]) -> List[str]:
        # Return a list without empty strings and without leading or trailing spaces
        # Step 1: txt.split('\n')
        # Step 2: [x.strip() for x in Step 1 if x]
        # Step 3: [y for y in Step 2 if y]
        if txt:
            return [y for y in [x.strip() for x in txt.split("\n") if x] if y]
        else:
            raise ValueError("Text is not set, please first add a text!")

    @staticmethod
    def paragraphs_to_sentences_per_paragraph(paragraphs: List[str]) -> List[List[str]]:
        sentences_per_paragraph: List = []  # Set empty result list

        for paragraph in paragraphs:  # Iterate through all paragraphs
            sentences = [
                x.strip() for x in paragraph.split(".") if x
            ]  # Split by regular sentence seperator '.'

            for index, value in enumerate(sentences):  # Iterate through all sentence inside a paragraph
                if "?" in value:  # Split by '?'
                    sentences[index] = value.split("?")
                if "!" in value:  # Split by '!'
                    sentences[index] = value.split("!")
            _sentences = flatten_nested_lists(collection=sentences)  # Remove nested lists
            sentences_per_paragraph.append(
                [x.strip() for x in _sentences if x]
            )  # Remove leading or trailing spaces

        return sentences_per_paragraph

    @staticmethod
    def sentences_per_paragraph_to_sentences(sentences_per_paragraph: List[List[str]]) -> List[str]:
        return flatten_nested_lists(collection=sentences_per_paragraph)

    @staticmethod
    def sentences_to_words_per_sentence(sentences: List[str]) -> List[List[str]]:
        pattern = r"\b\w+\b"
        words_in_sentence = []

        for sentence in sentences:
            matches = re.findall(pattern, sentence)
            words_in_sentence.append(matches)

        return words_in_sentence

    @staticmethod
    def words_per_sentence_to_words(words_per_sentence: List[List[str]]) -> List[str]:
        return flatten_nested_lists(collection=words_per_sentence)


class POSTagger:
    def __init__(self) -> None:
        pass

    @staticmethod
    def generate_tags(collection: List[List[str]]) -> List[List[tuple[str, str]]]:
        result = []
        for value in collection:
            pos_tokens_per_sentence = nltk.pos_tag(value)
            sub_result = []

            for token in pos_tokens_per_sentence:
                if token[1] in ["N", "NN", "NNS", "NNP", "NNPS"]:  # Nouns
                    sub_result.append((token[0], "n"))
                elif token[1] in ["JJ", "JJR", "JJS"]:  # Adjectives
                    sub_result.append((token[0], "a"))
                elif token[1] in ["RB", "RBR", "RBS"]:  # Adverbs
                    sub_result.append((token[0], "r"))
                elif token[1] in ["VB", "VBD", "VBG", "VBN", "VBP", "VBZ"]:  # Verbs
                    sub_result.append((token[0], "v"))
                else:
                    sub_result.append((token[0], token[1]))
            result.append(sub_result)
        return result


class Lemmatizer:
    def __init__(self) -> None:
        self._lemmatizer: WordNetLemmatizer = WordNetLemmatizer()

    def lemmatize(self, collection: List[List[str]]):
        result = []
        for value in collection:
            sub_result = []

            for token in value:
                if token[1] in ["n", "a", "r", "v"]:
                    sub_result.append(self._lemmatizer.lemmatize(token[0], token[1]))
                else:
                    sub_result.append(self._lemmatizer.lemmatize(token[0]))

            result.append(sub_result)
        return result


class File:
    def __init__(self) -> None:
        self.text: Union[str, None] = None
        self.tokens: Union[Dict, None] = None
        self.pos: Union[Dict, None] = None
        self.lemma: Union[Dict, None] = None
        self.stop_word_free: Union[Dict, None] = None
        self.word_frequency: Union[Dict, None] = None
        self.tf_idf: Union[Dict, None] = None
        self.stemmed: Union[Dict, None] = None
        self.page_rank: Union[Dict, None] = None

    def add_text(self, txt: str) -> None:
        self.text = txt

    def get_text(self) -> Union[str, None]:
        return self.text

    def add_metric(self, metric_type: str, key: str, value: Any) -> None:
        if not isinstance(getattr(self, metric_type), Dict):
            setattr(self, metric_type, {})

        getattr(self, metric_type)[key] = value

    def get_metric(self, metric_type: str, key: Union[str, None] = None) -> Any:
        if not key:
            return getattr(self, metric_type, None)
        return getattr(self, metric_type, {}).get(key, None)

    def as_dict(self) -> Dict:
        return self.__dict__
