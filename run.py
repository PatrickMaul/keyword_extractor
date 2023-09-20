from src.keyword_extractor import KeywordExtractor
import json

with open("../../assets/dummy-text.txt", "r") as file:
    TEXT: str = file.read()

kw_e_wf = KeywordExtractor(txt=TEXT, method="wf")
kw_e_tfidf = KeywordExtractor(txt=TEXT, method="tfidf")
kw_e_pr = KeywordExtractor(txt=TEXT, method="pr")

result = kw_e_wf._extract()
print(f'word frequency result => {result.get("keywords")}')
with open("./word_frequency.json", "w") as file:
    file.write(json.dumps(result))

result = kw_e_tfidf._extract()
print(f'tf-idf result => {result.get("keywords")}')
with open("./tf_idf.json", "w") as file:
    file.write(json.dumps(result))

result = kw_e_pr._extract()
print(f'page-rank result => {result.get("keywords")}')
with open("./page_rank.json", "w") as file:
    file.write(json.dumps(result))
