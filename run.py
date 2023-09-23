########################
# Author: Patrick Maul #
########################

import argparse
import json
from os import path
from typing import Union, Optional
from src.keyword_extractor import KeywordExtractor, KeywordExtractorDirectory

# import json

# Init ArgumentParser
parser = argparse.ArgumentParser(
    prog="Keyword extractor", description="Extracts keywords from a text or directory with texts."
)

# Add arguments
parser.add_argument("-t", "--text", type=str, dest="text", help="Text for extraction")
parser.add_argument("-f", "--file-path", type=str, dest="file_path", help="Path to text for extraction")
parser.add_argument("-d", "--dir-path", type=str, dest="dir_path", help="Path to directory for extraction")
parser.add_argument(
    "-m",
    "--extraction-method",
    type=str,
    dest="extraction_method",
    default="wf",
    help="Extraction method (wf => Word Frequency, tfidf => Term Frequency Inverse Document "
    "Frequency, pr => Page Rank",
)
parser.add_argument("-o", "--output", type=str, dest="output", help="Destination for output. (keywords.json)")
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
    with open(path.join(args.output, "keywords.json"), "w") as file:
        file.write(json.dumps(result))
if args.print and result:
    if args.dir_path:
        for key, value in result.items():
            print(f"Keywords for '{key}': {', '.join(value.get('keywords'))}")
    else:
        print(result.get("keywords"))

# kw_e_wf = KeywordExtractor(txt=TEXT, method="wf")
# kw_e_tfidf = KeywordExtractor(txt=TEXT, method="tfidf")
# kw_e_pr = KeywordExtractor(txt=TEXT, method="pr")

# result = kw_e_wf._extract()
# print(f'word frequency result => {result.get("keywords")}')
# with open("./word_frequency.json", "w") as file:
#     file.write(json.dumps(result))

# result = kw_e_tfidf._extract()
# print(f'tf-idf result => {result.get("keywords")}')
# with open("./tf_idf.json", "w") as file:
#     file.write(json.dumps(result))

# result = kw_e_pr._extract()
# print(f'page-rank result => {result.get("keywords")}')
# with open("./page_rank.json", "w") as file:
#     file.write(json.dumps(result))

# kw_e_d_wf = KeywordExtractorDirectory(directory='../../assets', method="wf")
# kw_e_d_tfidf = KeywordExtractorDirectory(directory='../../assets', method="tfidf")
# kw_e_d_pr = KeywordExtractorDirectory(directory='../../assets', method="pr")

# r_1 = kw_e_d_wf.extract()
# r_2 = kw_e_d_tfidf.extract()
# r_3 = kw_e_d_pr.extract()


# for key in r_1.keys():
# print(r_1[key].get('keywords'))
# print(r_2[key].get('keywords'))
# print(r_3[key].get('keywords'))
