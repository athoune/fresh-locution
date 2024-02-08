from pathlib import Path

from db import Db
from nlp import locutions

if __name__ == "__main__":
    import sys

    sentence = " ".join(sys.argv[1:])
    target = Path("./fresh.loc")
    loc = Db(target)
    for ngrams in locutions(sentence, 2):
        ll = " ".join(ngrams)
        print(loc.tf_idf(ll), ll)
