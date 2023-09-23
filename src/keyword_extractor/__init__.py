import argparse
import json
import math
import networkx
import os
from nltk.stem import PorterStemmer
from utils import (
    Tokenizer,
    POSTagger,
    Lemmatizer,
    File,
    flatten_nested_lists,
    remove_duplicates,
    remove_stop_words,
)
from typing import Union, Optional


def run() -> None:
    # Init ArgumentParser
    parser = argparse.ArgumentParser(
        prog="Keyword extractor", description="Extracts keywords from a text or directory with texts."
    )

    # Add arguments
    parser.add_argument("-t", "--text", type=str, dest="text", help="Text for extraction")
    parser.add_argument("-f", "--file-path", type=str, dest="file_path", help="Path to text for extraction")
    parser.add_argument(
        "-d", "--dir-path", type=str, dest="dir_path", help="Path to directory for extraction"
    )
    parser.add_argument(
        "-m",
        "--extraction-method",
        type=str,
        dest="extraction_method",
        default="wf",
        help="Extraction method (wf => Word Frequency, tfidf => Term Frequency Inverse Document "
        "Frequency, pr => Page Rank",
    )
    parser.add_argument(
        "-o", "--output", type=str, dest="output", help="Destination for output. (keywords.json)"
    )
    parser.add_argument("-p", "--print", action="store_true", dest="print", help="Print result in console")

    # Get arguments & load config
    args = parser.parse_args()
    result: Optional[dict] = None
    keyword_extractor: Union[KeywordExtractor, KeywordExtractorDirectory]

    if args.text and args.extraction_method:
        keyword_extractor = KeywordExtractor(txt=args.text, method=args.extraction_method)
        result = keyword_extractor.extract()
    elif args.file_path and args.extraction_method:
        with open(args.file_path, "r") as file:
            text: str = file.read()

        keyword_extractor = KeywordExtractor(txt=text, method=args.extraction_method)
        result = keyword_extractor.extract()
    elif args.dir_path and args.extraction_method:
        keyword_extractor = KeywordExtractorDirectory(directory=args.dir_path, method=args.extraction_method)
        result = keyword_extractor.extract()
    else:
        print("Somthing went wrong")

    if args.output and result:
        with open(os.path.join(args.output, "keywords.json"), "w") as file:
            file.write(json.dumps(result))
    if args.print and result:
        if args.dir_path:
            for key, value in result.items():
                print(f"Keywords for '{key}': {', '.join(value.get('keywords'))}")
        else:
            print(result.get("keywords"))


class KeywordExtractor:
    def __init__(self, txt: str, method: str = "wf") -> None:
        self.txt: str = txt
        self.method: str = method
        self._tokenizer: Tokenizer = Tokenizer()
        self._pos_tagger: POSTagger = POSTagger()
        self._lemmatizer: Lemmatizer = Lemmatizer()
        self._stemmer: PorterStemmer = PorterStemmer()

    def update_txt(self, new_txt: str) -> None:
        self.txt = new_txt

    def extract(self) -> dict:
        result: dict = {"text": self.txt, "extraction_method": self.method, "keywords": [], "file": File()}

        if self.method == "wf":
            keywords, file = self._extract_with_word_frequency()
            result["keywords"] = keywords
            result["file"] = file.as_dict()
        elif self.method == "tfidf":
            keywords, file = self._extract_with_tf_idf(doc_counter=1)
            result["keywords"] = keywords
            result["file"] = file.as_dict()
        elif self.method == "pr":
            keywords, file = self._extract_with_page_rank()
            result["keywords"] = keywords
            result["file"] = file.as_dict()
        elif self.method == "full":
            # ToDo: Define full extraction with all methods
            pass
        else:
            # ToDo: Exception handling
            pass

        return result

    def _extract_with_word_frequency(self, max_keywords: int = 10) -> list:
        file: File = self._base_extraction()

        clean_words: list = file.get_metric(metric_type="stop_word_free", key="words")

        word_counts: dict = {}
        for word in clean_words:
            if word not in word_counts.keys():
                word_counts[word] = 1
            else:
                word_counts[word] += 1

        raw_file_length: int = len(file.get_metric(metric_type="tokens", key="words"))

        term_frequencies: dict = {}
        for word, count in word_counts.items():
            term_frequencies[word] = count / raw_file_length

        file.add_metric(metric_type="word_frequency", key="word_counts", value=word_counts)
        file.add_metric(metric_type="word_frequency", key="raw_file_length", value=raw_file_length)
        file.add_metric(metric_type="word_frequency", key="term_frequencies", value=term_frequencies)

        return [
            self._get_keywords(
                data=file.get_metric(metric_type="word_frequency", key="term_frequencies"),
                max_length=max_keywords,
            ),
            file,
        ]

    def _extract_with_tf_idf(self, doc_counter: int = 1, max_keywords: int = 10) -> list:
        file: File = self._extract_with_word_frequency()[1]
        tokens = file.get_metric(metric_type="word_frequency", key="word_counts").keys()
        document_frequencies = {}
        inverse_document_frequencies = {}
        term_frequency_inverse_document_frequencies = {}

        for token in tokens:
            if token in file.get_metric(metric_type="stop_word_free", key="words"):
                if token not in document_frequencies:
                    document_frequencies[token] = 0
                document_frequencies[token] += 1

        for key, value in document_frequencies.items():
            inverse_document_frequencies[key] = 1 + math.log(doc_counter / value)

        keys: list[str] = list(inverse_document_frequencies.keys())
        for index, key in enumerate(keys):
            tf_idf: float = list(inverse_document_frequencies.values())[index]
            term_frequency_inverse_document_frequencies[key] = (
                len(file.get_metric(metric_type="word_frequency", key="term_frequencies").keys()) * tf_idf
            )

        file.add_metric(metric_type="tf_idf", key="document_frequencies", value=document_frequencies)
        file.add_metric(
            metric_type="tf_idf", key="inverse_document_frequencies", value=inverse_document_frequencies
        )
        file.add_metric(
            metric_type="tf_idf",
            key="term_frequency_inverse_document_frequencies",
            value=term_frequency_inverse_document_frequencies,
        )

        return [
            self._get_keywords(
                data=file.get_metric(metric_type="tf_idf", key="term_frequency_inverse_document_frequencies"),
                max_length=max_keywords,
            ),
            file,
        ]

    def _extract_with_page_rank(self, doc_counter: int = 1, max_keywords: int = 10) -> list:
        file: File = self._extract_with_tf_idf(doc_counter=doc_counter)[1]

        stemmed_words = []
        for sentence in file.get_metric(metric_type="stop_word_free", key="words_per_sentence"):
            stemmed_words.append([self._stemmer.stem(word) for word in sentence])

        file.add_metric(metric_type="stemmed", key="words_per_sentence", value=stemmed_words)
        file.add_metric(
            metric_type="stemmed",
            key="words",
            value=flatten_nested_lists(
                collection=file.get_metric(metric_type="stemmed", key="words_per_sentence")
            ),
        )
        file.add_metric(
            metric_type="stemmed",
            key="duplicate_free_words",
            value=remove_duplicates(collection=file.get_metric(metric_type="stemmed", key="words")),
        )

        graph = networkx.Graph()
        for sentence in file.get_metric(metric_type="stemmed", key="words_per_sentence"):
            graph.add_nodes_from(sentence)
            for word1 in sentence:
                for word2 in sentence:
                    if word1 != word2:
                        graph.add_edge(word1, word2)

        scores = networkx.pagerank(graph)
        file.add_metric(metric_type="page_rank", key="scores", value=scores)
        top_keywords = self._get_keywords(
            data=file.get_metric(metric_type="page_rank", key="scores"), max_length=max_keywords
        )

        mapped_top_keywords = []
        for keyword in top_keywords:
            if keyword in file.get_metric(metric_type="stop_word_free", key="duplicate_free_words"):
                mapped_top_keywords.append(keyword)
            else:
                for c_word in file.get_metric(metric_type="stop_word_free", key="duplicate_free_words"):
                    if c_word.startswith(keyword):
                        mapped_top_keywords.append(c_word)
                        break

        return [mapped_top_keywords, file]

    def _base_extraction(self) -> File:
        file: File = File()

        # Add original text
        file.add_text(txt=self.txt.lower())

        # Add tokens
        file.add_metric(
            metric_type="tokens",
            key="paragraphs",
            value=self._tokenizer.text_to_paragraphs(txt=file.get_text()),
        )
        file.add_metric(
            metric_type="tokens",
            key="sentences_per_paragraph",
            value=self._tokenizer.paragraphs_to_sentences_per_paragraph(
                paragraphs=file.get_metric(metric_type="tokens", key="paragraphs")
            ),
        )
        file.add_metric(
            metric_type="tokens",
            key="sentences",
            value=self._tokenizer.sentences_per_paragraph_to_sentences(
                sentences_per_paragraph=file.get_metric(metric_type="tokens", key="sentences_per_paragraph")
            ),
        )
        file.add_metric(
            metric_type="tokens",
            key="words_per_sentence",
            value=self._tokenizer.sentences_to_words_per_sentence(
                sentences=file.get_metric(metric_type="tokens", key="sentences")
            ),
        )
        file.add_metric(
            metric_type="tokens",
            key="words",
            value=self._tokenizer.words_per_sentence_to_words(
                words_per_sentence=file.get_metric(metric_type="tokens", key="words_per_sentence")
            ),
        )
        file.add_metric(
            metric_type="tokens",
            key="duplicate_free_words",
            value=remove_duplicates(collection=file.get_metric(metric_type="tokens", key="words")),
        )

        # Add point of speech
        file.add_metric(
            metric_type="pos",
            key="words_per_sentence",
            value=self._pos_tagger.generate_tags(
                collection=file.get_metric(metric_type="tokens", key="words_per_sentence")
            ),
        )
        file.add_metric(
            metric_type="pos",
            key="words",
            value=flatten_nested_lists(
                collection=file.get_metric(metric_type="pos", key="words_per_sentence")
            ),
        )
        file.add_metric(
            metric_type="pos",
            key="duplicate_free_words",
            value=remove_duplicates(collection=file.get_metric(metric_type="pos", key="words")),
        )

        # Add lemma
        file.add_metric(
            metric_type="lemma",
            key="words_per_sentence",
            value=self._lemmatizer.lemmatize(
                collection=file.get_metric(metric_type="pos", key="words_per_sentence")
            ),
        )
        file.add_metric(
            metric_type="lemma",
            key="words",
            value=flatten_nested_lists(
                collection=file.get_metric(metric_type="lemma", key="words_per_sentence")
            ),
        )
        file.add_metric(
            metric_type="lemma",
            key="duplicate_free_words",
            value=remove_duplicates(collection=file.get_metric(metric_type="lemma", key="words")),
        )

        # Remove stop words
        file.add_metric(
            metric_type="stop_word_free",
            key="words_per_sentence",
            value=remove_stop_words(
                collection=file.get_metric(metric_type="lemma", key="words_per_sentence")
            ),
        )
        file.add_metric(
            metric_type="stop_word_free",
            key="words",
            value=flatten_nested_lists(
                collection=file.get_metric(metric_type="stop_word_free", key="words_per_sentence")
            ),
        )
        file.add_metric(
            metric_type="stop_word_free",
            key="duplicate_free_words",
            value=remove_duplicates(collection=file.get_metric(metric_type="stop_word_free", key="words")),
        )

        return file

    @staticmethod
    def _get_keywords(data: dict, max_length: int = 10):
        mapped_list = []
        for key, value in data.items():
            mapped_list.append({"word": key, "value": value})

        keywords_sorted = sorted(mapped_list, key=lambda d: d["value"], reverse=True)

        top_keywords = []
        for index in range(0, max_length, 1):
            top_keywords.append(keywords_sorted[index].get("word"))

        return top_keywords


class KeywordExtractorDirectory:
    def __init__(self, directory: str, method: str) -> None:
        self.directory: str = directory
        self.method: str = method
        self._paths: list[str] = self._scan_directory()

    def _scan_directory(self, directory: Optional[str] = None) -> list[str]:
        directory = directory or self.directory

        paths: list[str] = [os.path.join(directory, path) for path in os.listdir(directory)]
        result_paths: list[str] = []

        for path in paths:
            if os.path.isfile(path):
                result_paths.append(path)
            elif os.path.isdir(path):
                for item in self._scan_directory(path):
                    result_paths.append(item)

        return result_paths

    def extract(self):
        result: dict[str, dict] = {}
        for path in self._paths:
            with open(path, "r") as file:
                text: str = file.read()
                result[path] = KeywordExtractor(txt=text, method=self.method).extract()

        return result
