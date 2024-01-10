#! /usr/bin/env python3 -u

import pickle
import os
from collections import Counter

from joblib import Parallel, delayed

from wiki_abstract import wiki, Doc

n_cores: int
try:
    n_cores = len(os.sched_getaffinity(0))
except AttributeError:
    n_cores = os.cpu_count()



def doc2locutions(doc: Doc) -> list[str]:
    "Get locutions from a document."
    r = []
    for sentence in tokenize(doc.abstract):
        for n in ngram(sentence, 3):
            r.append(" ".join(n))
    return r


if __name__ == "__main__":
    import sys
    from tqdm import tqdm

    parallel = Parallel(n_jobs=n_cores - 1, return_as="generator")

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
    with open("locutions.pickle", "wb") as f:
        pickle.dump(tf, f)
    print(tf.most_common(10))
