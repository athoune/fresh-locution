from array import array
from itertools import chain
from pathlib import Path
from tempfile import TemporaryDirectory

from trie import OrderedTrie, reverse


def test_reverse():
    src = array("I", [3, 2, 0, 1])
    assert array("I", [2, 3, 1, 0]) == reverse(src)


def test_orderedTrie():
    t = OrderedTrie(["je", "mange", "des", "carottes"])
    assert t["mange"] == 1
    assert "carottes" in t
    assert ["je", "mange", "des", "carottes"] == list(t)


def test_trie_on_trie():
    a = OrderedTrie(["je", "mange", "des", "carottes"])
    b = OrderedTrie(a)
    assert b["mange"] == 1


def test_file():
    with TemporaryDirectory() as temp:
        p = Path(temp) / "trie.txt"
        p.open("w").write(
            """pim
pam
poum
"""
        )
        t = OrderedTrie.fromfile(p)
        print(t.trie.keys())
        assert 1 == t["pam"]


def test_append():
    t = OrderedTrie(["pim", "pam", "poum"])
    assert 0 == t["pim"]
    assert 1 == t["pam"]
    assert 3 == len(t)
    print(list(chain.from_iterable((t, ["Bob"]))))
    t2 = t.append(["the captain"])
    assert 4 == len(t2)
    assert 0 == t2["pim"]
    assert 1 == t2["pam"]
    assert 3 == t2["the captain"]
