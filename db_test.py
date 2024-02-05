
from tempfile import TemporaryDirectory

from db import Db
from collections import Counter


def test_db():
    with TemporaryDirectory() as temp:
        d = Db(temp)
        c = Counter("je mange des carottes et des petits pois".split(" "))
        d.add_doc(c)
        d.write()
