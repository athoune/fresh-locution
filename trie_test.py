from array import array
from tempfile import TemporaryDirectory
from pathlib import Path

from trie import reverse, OrderedTrie


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
