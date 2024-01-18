from array import array
from collections import Counter
from itertools import chain
from pathlib import Path
import struct
from typing import Generator, Iterable, Self

from trie import OrderedTrie


class LocutionsCold:
    "Read only locutions store"
    tf: array("I")
    df: array("I")
    _total: int
    _keys: OrderedTrie

    def __init__(self, folder: str | Path, create: bool = False):
        if isinstance(folder, str):
            folder = Path(folder)
        if not folder.exists():
            if not create:
                raise FileNotFoundError(f"Folder not found {folder}")
            folder.mkdir()
        self.f_keys = folder / "keys.txt"
        self.f_tf = folder / "tf.bin"
        self.f_df = folder / "df.bin"
        self.f_total = folder / "total.bin"
        if not (
            self.f_keys.exists()
            == self.f_tf.exists()
            == self.f_df.exists()
            == self.f_total.exists()
        ):
            raise FileNotFoundError("We need both keys.txt, tf.bin, df.bin & total.bin")
        self.tf = array("I")
        self.df = array("I")
        if self.f_tf.exists():
            size = self.f_tf.lstat().st_size
            self.tf.fromfile(self.f_tf.open("rb"), int(size / 4))  # It's int32
        if self.f_df.exists():
            size = self.f_df.lstat().st_size
            self.df.fromfile(self.f_df.open("rb"), int(size / 4))  # It's int32
        if not self.f_keys.exists():
            self.f_keys.open("wb")
        self._keys = OrderedTrie.fromfile(self.f_keys)
        if self.f_total.exists():
            self._total = struct.unpack("I", self.f_total.read_bytes())[0]
        else:
            self._total = 0

    def __len__(self) -> int:
        return len(self.tf)

    def __contains__(self, key) -> bool:
        return key in self._keys

    def __getitem__(self, key) -> tuple[int, int]:
        if key not in self._keys:
            raise KeyError(key)
        idx = self._keys[key]
        return self.tf[idx], self.df[idx]

    def ord(self, key) -> int:
        "position of the key, can raise a KeyError"
        return self._keys[key]

    def get(self, key, default: tuple[int, int]) -> tuple[int, int]:
        try:
            idx = self._keys[key]
        except KeyError:
            return default
        else:
            return self.tf[idx], self.df[idx]

    def __iter__(self) -> Generator[str, None, None]:
        for k in self._keys:
            yield k


class LocutionsHot:
    "Append only locutions store"
    cold: LocutionsCold
    new_words: dict
    tf: array("I")
    df: array("I")
    _total: int

    def __init__(self, cold: LocutionsCold):
        self.new_words = dict()
        self.tf = array("I", (0 for i in range(len(cold))))
        self.df = array("I", (0 for i in range(len(cold))))
        self.cold = cold
        self._total = 0

    def add_document(self, words: Iterable[str]):
        "Add a document for word counting."
        df = set()
        for word in words:
            self._add(word, 1)
            df.add(word)
        for word in df:
            i = self.ord(word)
            self.df[i] += 1
        self._total += 1

    def add_counter(self, words: Counter):
        "Add a Counter of words"
        for word, n in words.items():
            i = self._add(word, n)
            self.df[i] += 1
        self._total += 1

    def _add(self, key: str, value: int) -> int:
        try:
            i = self.ord(key)
            self.tf[i] = self.tf[i] + value
            return i
        except KeyError:  # The key doesn't exist yet
            idx = len(self.tf)
            self.tf.append(value)
            self.df.append(0)  # lets prepare the df array
            self.new_words[key] = idx
            return idx

    def __contains__(self, word) -> bool:
        return word in self.cold or word in self.new_words

    def __len__(self) -> int:
        return len(self.tf)

    def ord(self, key) -> int:
        "position of the key, can raise a KeyError"
        if key in self.new_words:
            return self.new_words[key]
        return self.cold.ord(key)

    def __getitem__(self, word) -> tuple[int, int]:
        tf, df = self.cold.get(word, (0, 0))
        idx = self.ord(word)
        return (tf + self.tf[idx], df + self.df[idx])

    def __iter__(self) -> Generator[str, None, None]:
        return chain(self.cold, self.new_words)

    def items(self) -> Generator[tuple[str, tuple[int, int]], None, None]:
        for k in self:
            yield k, self[k]

    def total(self) -> int:
        return self.cold._total + self._total

    def write(self):
        with self.cold.f_keys.open("a") as f:
            for token in self.new_words:
                f.write(token)
                f.write("\n")
        with self.cold.f_tf.open("wb") as f:
            fresh_tf = array("I", self.cold.tf)
            for i, v in enumerate(self.tf[: len(self.cold.tf)]):
                if v == 0:
                    continue
                fresh_tf[i] += v
            fresh_tf.extend(self.tf[len(self.cold.tf) :])
            fresh_tf.tofile(self.cold.f_tf.open("wb"))
        with self.cold.f_df.open("wb") as f:
            fresh_df = array("I", self.cold.df)
            for i, v in enumerate(self.df[: len(self.cold.df)]):
                if v == 0:
                    continue
                fresh_df[i] += v
            fresh_df.extend(self.df[len(self.cold.df) :])
            fresh_df.tofile(self.cold.f_df.open("wb"))
        new_keys = OrderedTrie(self)
        self.new_words = dict()
        self.tf = array("I", (0 for i in range(len(self.tf))))
        self.cold.tf = fresh_tf
        self.df = array("I", (0 for i in range(len(self.df))))
        self.cold.df = fresh_df
        self.cold._keys = new_keys
        self.cold.f_total.write_bytes(struct.pack("I", self.total()))
        self._total = 0

    def merge(self, other: Self):
        for k, v in other.items():
            tf, df = v
            self._add(k, tf)
            self.df[self.ord(k)] += df


def Locutions(folder: str | Path, create: bool = False) -> LocutionsHot:
    "Locutions store"
    cold = LocutionsCold(folder, create)
    return LocutionsHot(cold)
