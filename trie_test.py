
from array import array

from trie import reverse, OrderedTrie


def test_reverse():
    src = array("I", [3, 2, 0, 1])
    assert array("I", [2, 3, 1, 0]) == reverse(src)

def test_orderedTrie():
    t = OrderedTrie(["je", "mange", "des", "carottes"])
    assert t["mange"] == 1
    assert "carottes" in t
    assert ["je", "mange", "des", "carottes"] == list(t)
