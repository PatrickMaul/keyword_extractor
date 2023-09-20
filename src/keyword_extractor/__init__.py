import math
from nltk.stem import PorterStemmer
import networkx as nx
from src.utils import Tokenizer, POSTagger, Lemmatizer, File, flatten_nested_lists, remove_duplicates, remove_stop_words


class KeywordExtractor:
    def __init__(self, txt: str, method: str = 'wf') -> None:
        self.txt: str = txt
        self.method: str = method
        self._tokenizer: Tokenizer = Tokenizer()
        self._pos_tagger: POSTagger = POSTagger()
        self._lemmatizer: Lemmatizer = Lemmatizer()
        self._stemmer: PorterStemmer = PorterStemmer()

    def update_txt(self, new_txt: str) -> None:
        self.txt = new_txt

    def _extract(self) -> dict:
        result: dict = {"text": self.txt, "extraction_method": self.method, "keywords": None}

        if self.method == "wf":
            extract = self._extract_with_word_frequency()
            result["keywords"] = extract.get('keywords')
            result["file"] = extract.get('file').as_dict()
        elif self.method == "tfidf":
            extract = self._extract_with_tf_idf(doc_counter=1)
            result["keywords"] = extract.get('keywords')
            result["file"] = extract.get('file').as_dict()
        elif self.method == "pr":
            extract = self._extract_with_page_rank()
            result["keywords"] = extract.get('keywords')
            result["file"] = extract.get('file').as_dict()
        elif self.method == "full":
            # ToDo: Define full extraction with all methods
            pass
        else:
            # ToDo: Exception handling
            pass

        return result

    def _extract_with_word_frequency(self, max_keywords: int = 10) -> dict:
        file: File = self._base_extraction()

        clean_words = file.get_metric(metric_type='stop_word_free', key='words')

        word_counts = {}
        for word in clean_words:
            if word not in word_counts.keys():
                word_counts[word] = 1
            else:
                word_counts[word] += 1

        raw_file_length = len(file.get_metric(metric_type='tokens', key='words'))

        term_frequencies = {}
        for word, count in word_counts.items():
            term_frequencies[word] = count / raw_file_length

        file.add_metric(metric_type='word_frequency', key='word_counts', value=word_counts)
        file.add_metric(metric_type='word_frequency', key='raw_file_length', value=raw_file_length)
        file.add_metric(metric_type='word_frequency', key='term_frequencies', value=term_frequencies)

        return {
            'keywords': self._get_keywords(
                data=file.get_metric(metric_type='word_frequency', key='term_frequencies'),
                max_length=max_keywords
            ),
            'file': file
        }

    def _extract_with_tf_idf(self, doc_counter: int = 1, max_keywords: int = 10) -> dict:
        file: File = self._extract_with_word_frequency().get('file')
        tokens = file.get_metric(metric_type='word_frequency', key='word_counts').keys()
        document_frequencies = {}
        inverse_document_frequencies = {}
        term_frequency_inverse_document_frequencies = {}

        for token in tokens:
            if token in file.get_metric(metric_type='stop_word_free', key='words'):
                if token not in document_frequencies:
                    document_frequencies[token] = 0
                document_frequencies[token] += 1

        for key, value in document_frequencies.items():
            inverse_document_frequencies[key] = 1 + math.log(doc_counter / value)

        for key, value in inverse_document_frequencies.items():
            term_frequency_inverse_document_frequencies[key] = len(file.get_metric(
                metric_type='word_frequency',
                key='term_frequencies'
            ).keys()) * value

        file.add_metric(metric_type='tf_idf', key='document_frequencies', value=document_frequencies)
        file.add_metric(metric_type='tf_idf', key='inverse_document_frequencies', value=inverse_document_frequencies)
        file.add_metric(
            metric_type='tf_idf',
            key='term_frequency_inverse_document_frequencies',
            value=term_frequency_inverse_document_frequencies
        )

        return {
            'keywords': self._get_keywords(
                data=file.get_metric(metric_type='tf_idf', key='term_frequency_inverse_document_frequencies'),
                max_length=max_keywords
            ),
            'file': file
        }

    def _extract_with_page_rank(self, doc_counter: int = 1, max_keywords: int = 10) -> dict:
        file: File = self._extract_with_tf_idf(doc_counter=doc_counter).get('file')

        stemmed_words = []
        for sentence in file.get_metric(metric_type='stop_word_free', key='words_per_sentence'):
            stemmed_words.append([self._stemmer.stem(word) for word in sentence])

        file.add_metric(
            metric_type='stemmed',
            key='words_per_sentence',
            value=stemmed_words
        )
        file.add_metric(
            metric_type='stemmed',
            key='words',
            value=flatten_nested_lists(collection=file.get_metric(metric_type='stemmed', key='words_per_sentence'))
        )
        file.add_metric(
            metric_type='stemmed',
            key='duplicate_free_words',
            value=remove_duplicates(collection=file.get_metric(metric_type='stemmed', key='words'))
        )

        graph = nx.Graph()
        for sentence in file.get_metric(metric_type='stemmed', key='words_per_sentence'):
            graph.add_nodes_from(sentence)
            for word1 in sentence:
                for word2 in sentence:
                    if word1 != word2:
                        graph.add_edge(word1, word2)

        scores = nx.pagerank(graph)
        file.add_metric(
            metric_type='page_rank',
            key='scores',
            value=scores
        )
        top_keywords = self._get_keywords(
            data=file.get_metric(metric_type='page_rank', key='scores'),
            max_length=max_keywords
        )

        mapped_top_keywords = []
        for keyword in top_keywords:
            if keyword in file.get_metric(metric_type='stop_word_free', key='duplicate_free_words'):
                mapped_top_keywords.append(keyword)
            else:
                for c_word in file.get_metric(metric_type='stop_word_free', key='duplicate_free_words'):
                    if c_word.startswith(keyword):
                        mapped_top_keywords.append(c_word)
                        break

        return {
            'keywords': mapped_top_keywords,
            'file': file
        }

    def _base_extraction(self) -> File:
        file: File = File()

        # Add original text
        file.add_text(txt=self.txt.lower())

        # Add tokens
        file.add_metric(
            metric_type='tokens',
            key='paragraphs',
            value=self._tokenizer.text_to_paragraphs(txt=file.get_text())
        )
        file.add_metric(
            metric_type='tokens',
            key='sentences_per_paragraph',
            value=self._tokenizer.paragraphs_to_sentences_per_paragraph(
                paragraphs=file.get_metric(metric_type='tokens', key='paragraphs')
            )
        )
        file.add_metric(
            metric_type='tokens',
            key='sentences',
            value=self._tokenizer.sentences_per_paragraph_to_sentences(
                sentences_per_paragraph=file.get_metric(metric_type='tokens', key='sentences_per_paragraph')
            )
        )
        file.add_metric(
            metric_type='tokens',
            key='words_per_sentence',
            value=self._tokenizer.sentences_to_words_per_sentence(
                sentences=file.get_metric(metric_type='tokens', key='sentences')
            )
        )
        file.add_metric(
            metric_type='tokens',
            key='words',
            value=self._tokenizer.words_per_sentence_to_words(
                words_per_sentence=file.get_metric(metric_type='tokens', key='words_per_sentence')
            )
        )
        file.add_metric(
            metric_type='tokens',
            key='duplicate_free_words',
            value=remove_duplicates(collection=file.get_metric(metric_type='tokens', key='words'))
        )

        # Add point of speech
        file.add_metric(
            metric_type='pos',
            key='words_per_sentence',
            value=self._pos_tagger.generate_tags(
                collection=file.get_metric(metric_type='tokens', key='words_per_sentence')
            )
        )
        file.add_metric(
            metric_type='pos',
            key='words',
            value=flatten_nested_lists(collection=file.get_metric(metric_type='pos', key='words_per_sentence'))
        )
        file.add_metric(
            metric_type='pos',
            key='duplicate_free_words',
            value=remove_duplicates(collection=file.get_metric(metric_type='pos', key='words'))
        )

        # Add lemma
        file.add_metric(
            metric_type='lemma',
            key='words_per_sentence',
            value=self._lemmatizer.lemmatize(
                collection=file.get_metric(metric_type='pos', key='words_per_sentence')
            )
        )
        file.add_metric(
            metric_type='lemma',
            key='words',
            value=flatten_nested_lists(collection=file.get_metric(metric_type='lemma', key='words_per_sentence'))
        )
        file.add_metric(
            metric_type='lemma',
            key='duplicate_free_words',
            value=remove_duplicates(collection=file.get_metric(metric_type='lemma', key='words'))
        )

        # Remove stop words
        file.add_metric(
            metric_type='stop_word_free',
            key='words_per_sentence',
            value=remove_stop_words(collection=file.get_metric(metric_type='lemma', key='words_per_sentence'))
        )
        file.add_metric(
            metric_type='stop_word_free',
            key='words',
            value=flatten_nested_lists(collection=file.get_metric(metric_type='stop_word_free', key='words_per_sentence'))
        )
        file.add_metric(
            metric_type='stop_word_free',
            key='duplicate_free_words',
            value=remove_duplicates(collection=file.get_metric(metric_type='stop_word_free', key='words'))
        )

        return file

    @staticmethod
    def _get_keywords(data: dict, max_length: int = 10):
        mapped_list = []
        for key, value in data.items():
            mapped_list.append({'word': key, 'value': value})

        keywords_sorted = sorted(mapped_list, key=lambda d: d['value'], reverse=True)

        top_keywords = []
        for index in range(0, max_length, 1):
            top_keywords.append(keywords_sorted[index].get('word'))

        return top_keywords
