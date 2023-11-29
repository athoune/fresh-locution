#! /usr/bin/env python3 -u

import pickle
import re
import os
from collections import Counter
from typing import Generator

from joblib import Parallel, delayed

import pysbd
from wiki_abstract import wiki, Doc

seg = pysbd.Segmenter(language="en", clean=False)
SPACE = re.compile(r"\s+")
n_cores: int
try:
    n_cores = len(os.sched_getaffinity(0))
except AttributeError:
    n_cores = os.cpu_count()


def ngram(txt: list[str], size: int) -> Generator[list[str], None, None]:
    for i in range(len(txt) - size):
        yield txt[i : i + size]


def tokenize(txt: str) -> Generator[list[str], None, None]:
    if not isinstance(txt, str):
        return None
    for sentence in seg.segment(txt):
        yield SPACE.split(sentence.lower())


def doc2locutions(doc: Doc) -> list[str]:
    r = []
    for sentence in tokenize(doc.abstract):
        for n in ngram(sentence, 3):
            r.append(" ".join(n))
    return r


if __name__ == "__main__":
    import sys
    from tqdm import tqdm

    parallel = Parallel(n_jobs=n_cores -1, return_as="generator")

    output_generator = parallel(
        delayed(doc2locutions)(doc) for doc in wiki(sys.argv[1])
    )

    tf = Counter()
    buffer: list[str] = []
    for locution in tqdm(output_generator, unit=" locs"):
        buffer += locution
        if len(buffer) == 1000:
            tf.update(tuple(buffer))
            buffer = []

    tf.update(buffer)
    with open('locutions.pickle', 'wb') as f:
        pickle.dump(tf, f)
    print(tf.most_common(10))
