class KeywordExtractor:
    def __init__(self, text: str, method: str = 'wf') -> None:
        self.text: str = text
        self.method: str = method

    def update_text(self, new_text: str) -> None:
        self.text = new_text

    def _extract(self) -> dict:
        result: dict = {"text": self.text, "extraction_method": self.method, "keywords": None}

        if self.method == "wf":
            result["keywords"] = self._extract_with_word_frequency()
        elif self.method == "tfidf":
            result["keywords"] = self._extract_with_tf_idf()
        elif self.method == "pr":
            result["keywords"] = self._extract_with_page_rank()
        elif self.method == "full":
            # ToDo: Define full extraction with all methods
            pass
        else:
            # ToDo: Exception handling
            pass

        return result

    def _extract_with_word_frequency(self) -> list:
        keywords: list = []
        return keywords

    def _extract_with_tf_idf(self) -> list:
        keywords: list = []
        return keywords

    def _extract_with_page_rank(self) -> list:
        keywords: list = []
        return keywords


if __name__ == '__main__':
    kwe = KeywordExtractor(text='foo bla', method='wf')
    print(kwe._extract())