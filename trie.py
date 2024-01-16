from array import array
from collections.abc import Iterator
from itertools import chain
from pathlib import Path
from typing import Generator

from marisa_trie import Trie


class KeysReader:
    "Read a file with \\n terminated file"

    path: Path

    def __init__(self, path: Path | str):
        if isinstance(path, str):
            self.path = Path(path)
        else:
            self.path = path

    def __iter__(self) -> Generator[str, None, None]:
        with self.path.open("r", encoding="utf8") as f:
            for line in f:
                yield line[:-1]


class Loop:
    def __init__(self, *gens):
        self.gens = gens

    def __iter__(self):
        return chain(*self.gens)


class OrderedTrie:
    """
    A Trie, built from a list of uniques lines.
    Order is not shuffled, you can store values in an array, and use words as keys.
    """

    file: Path
    trie: Trie
    ids: array("I")

    @classmethod
    def fromfile(cls, path: Path | str):
        o = cls(KeysReader(path))
        return o

    def __init__(self, gen: Iterator[str]):
        self.trie = Trie(gen)
        self.ids = array("I", [0] * len(self.trie))
        for i, line in enumerate(gen):
            self.ids[self.trie[line]] = i

    def __getitem__(self, key: str) -> int:
        id_ = self.trie[key]
        return self.ids[id_]

    def __contains__(self, key: str) -> bool:
        return key in self.trie

    def __len__(self) -> int:
        assert len(self.trie) == len(self.ids), "OrderedTrie storage out of sync"
        return len(self.trie)

    def __iter__(self):
        return (self.trie.restore_key(id_) for id_ in reverse(self.ids))

    def append(self, gen: Iterator[str]):
        "Return a new OrderedTrie with appended values"
        return OrderedTrie(Loop(self, gen))


def reverse(src: array) -> array:
    """
    from an array of n unique positions, with n < len(src)

    [3, 2, 0, 1] => [2, 3, 1,0]
    """
    res = array("I", [0] * len(src))
    for i, value in enumerate(src):
        res[value] = i
    return res
