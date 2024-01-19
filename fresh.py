#! /usr/bin/env python3 -u

import os
from collections import Counter
from pathlib import Path
from typing import Generator

from joblib import Parallel, delayed

from locutions import Locutions
from nlp import locutions
from wiki_abstract import Doc, wiki

n_cores: int
try:
    n_cores = len(os.sched_getaffinity(0))
except AttributeError:
    n_cores = os.cpu_count()


def doc2locutions(doc: Doc) -> Generator[str, None, None]:
    "Get locutions from a document."
    for ngrams in locutions(doc.abstract, 3):
        yield " ".join(ngrams)


def count_doc(doc: Doc, ngram_size: int = 3) -> Counter:
    "Count all ngrams in a doc"
    # locutions return a list of ngrams, list[str], lets rebuild a short sentences for counting purpose
    return Counter(" ".join(l) for l in locutions(doc.abstract, ngram_size))


def count_wiki_abstract(
    path: Path, ngram_size: int = 3, n_jobs: int = 0
) -> Generator[Counter, None, None]:
    if n_jobs == 0:  # 0 means max
        n_jobs = n_cores - 1
    parallel = Parallel(n_jobs=n_jobs, return_as="generator")
    output_generator = parallel(
        delayed(count_doc)(doc, ngram_size) for doc in wiki(path)
    )
    for c in output_generator:
        yield c


if __name__ == "__main__":
    import sys

    from tqdm import tqdm

    target = Path("./fresh.loc")
    if target.exists():
        target.rmdir()

    loc = Locutions(target, create=True)

    for count in tqdm(count_wiki_abstract(sys.argv[1]), unit=" docs"):
        loc.add_counter(count)
    loc.write()
