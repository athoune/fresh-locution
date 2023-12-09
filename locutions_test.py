from tempfile import TemporaryDirectory
from locutions import Locutions


def test_locutions():
    with TemporaryDirectory() as tempdir:
        l = Locutions(tempdir)
        l.add("je mange des carottes".split(" "))
        l.add("j'aime les carottes".split(" "))
        assert 2 == l.get("carottes")
        assert 1 == l.get("mange")
        assert 0 == l.get("navet")
        l.dump()
        l2 = Locutions(tempdir)
        assert 2 == l2.get("carottes")
