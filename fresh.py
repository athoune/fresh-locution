#! /usr/bin/env python -u
import re
from collections import Counter
from typing import Generator

from joblib import Parallel, delayed

import pysbd

seg = pysbd.Segmenter(language="en", clean=False)
SPACE = re.compile(r"\s+")


def ngram(txt: list[str], size: int) -> Generator[list[str], None, None]:
    for i in range(len(txt) - size):
        yield txt[i : i + size]


def tokenize(txt: str) -> Generator[list[str], None, None]:
    if not isinstance(txt, str):
        return None
    for sentence in seg.segment(txt):
        yield SPACE.split(sentence.lower())


if __name__ == "__main__":
    from wiki_abstract import wiki, Doc
    import sys
    from tqdm import tqdm

    def doc2locutions(doc: Doc) -> list[str]:
        r = []
        for sentence in tokenize(doc.abstract):
            for n in ngram(sentence, 3):
                r.append(" ".join(n))
        return r

    tf = Counter()
    parallel = Parallel(n_jobs=6, return_as="generator")

    output_generator = parallel(
        delayed(doc2locutions)(doc) for doc in wiki(sys.argv[1])
    )

    for locution in tqdm(output_generator, unit=" locs"):
        tf.update(locution)

    print(tf)
