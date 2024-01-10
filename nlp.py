import re
from typing import Generator

import pysbd

seg = pysbd.Segmenter(language="en", clean=False)
SPACE = re.compile(r"\s+")


def ngram(txt: list[str], size: int) -> Generator[list[str], None, None]:
    "Group tokens as ngrams"
    for i in range(len(txt) - size):
        yield txt[i : i + size]


def tokenize(txt: str) -> Generator[list[str], None, None]:
    "Read a text, cut it by sentences"
    if not isinstance(txt, str):
        return None
    for sentence in seg.segment(txt):
        yield SPACE.split(sentence.lower())


def locutions(txt: str, size: int) -> Generator[list[str], None, None]:
    "Yield all ngrams of all sentences of a text."
    for sentence in tokenize(txt):
        for n in ngram(sentence, size):
            yield n
