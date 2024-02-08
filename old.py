#! /usr/bin/env python3 -u
"""
Build the db of old locutions.
"""

import os
from collections import Counter
from pathlib import Path
from typing import Generator

from datasets import load_dataset
from joblib import Parallel, delayed

from db import Db
from nlp import locutions

n_cores: int
try:
    n_cores = len(os.sched_getaffinity(0))
except AttributeError:
    n_cores = os.cpu_count()


def doc2locutions(txt: str) -> Generator[str, None, None]:
    "Get locutions from a document."
    for ngrams in locutions(txt, 3):
        yield " ".join(ngrams)


def count_doc(txt: str, ngram_size: int = 3) -> Counter:
    "Count all ngrams in a doc"
    # locutions return a list of ngrams, list[str], lets rebuild a short sentences for counting purpose
    return Counter(" ".join(l) for l in locutions(txt, ngram_size))


def fresh(loc: Db, sentence: str):
    for l in locutions(sentence, 2):
        ll = " ".join(l)
        if ll not in loc:
            print("! ", ll)
            continue
        score = loc.tf_idf(ll)
        print(score, ll)


def count_wiki_datasets(
    ngram_size: int = 3, n_jobs: int = 0
) -> Generator[Counter, None, None]:
    datas = load_dataset("wikipedia", "20220301.en", trust_remote_code=True)["train"]
    if n_jobs == 0:  # 0 means max
        n_jobs = n_cores - 1
    parallel = Parallel(n_jobs=n_jobs, return_as="generator")
    output_generator = parallel(
        delayed(count_doc)(doc["text"], ngram_size) for doc in datas
    )
    for c in output_generator:
        yield c


if __name__ == "__main__":
    from tqdm import tqdm
    import shutil

    target = Path("./fresh.loc")
    if target.exists():
        shutil.rmtree(target)

    loc = Db(target)

    for count in tqdm(count_wiki_datasets(ngram_size=2), unit=" docs"):
        loc.add_doc(count)
    loc.write()
