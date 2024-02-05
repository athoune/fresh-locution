from collections import Counter
from tempfile import TemporaryDirectory

from db import Db


def test_db():
    with TemporaryDirectory() as temp:
        d = Db(temp)
        c = Counter("je mange des carottes et des petits pois".split(" "))
        d.add_doc(c)
        d.add_doc(Counter("je mange des croissants".split(" ")))
        d.write()
        assert 0.7 == round(d.tf_idf("croissants"), 1)
        assert 0 == d.tf_idf("mange")
        d.close()

        d2 = Db(temp)
        assert 2 == d2.n_docs
        assert (2, 2) == d2["mange"]
