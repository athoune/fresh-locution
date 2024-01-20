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


class Locutions(LocutionsCold):
    "Append only locutions store"
    new_words: dict
    new_tf: array("I")
    new_df: array("I")
    _new_total: int

    def __init__(self, folder: str | Path, create: bool = False):
        super().__init__(folder, create)
        self.new_words = dict()
        self.new_tf = array("I", (0 for i in range(len(self.tf))))
        self.new_df = array("I", (0 for i in range(len(self.tf))))
        self._new_total = 0

    def add_document(self, words: Iterable[str]):
        "Add a document for word counting."
        df = set()
        for word in words:
            self._add(word, 1)
            df.add(word)
        for word in df:
            i = self.ord(word)
            self.new_df[i] += 1
        self._total += 1

    def add_counter(self, words: Counter):
        "Add a Counter of words"
        for word, n in words.items():
            i = self._add(word, n)
            self.new_df[i] += 1
        self._new_total += 1

    def _add(self, key: str, value: int) -> int:
        try:
            i = self.ord(key)
            self.new_tf[i] = self.new_tf[i] + value
            return i
        except KeyError:  # The key doesn't exist yet
            idx = len(self.new_tf)
            self.new_tf.append(value)
            self.new_df.append(0)  # lets prepare the df array
            self.new_words[key] = idx
            return idx

    def __contains__(self, word) -> bool:
        return word in self._keys or word in self.new_words

    def __len__(self) -> int:
        return len(self.new_tf)

    def ord(self, key) -> int:
        "position of the key, can raise a KeyError"
        if key in self.new_words:
            return self.new_words[key]
        return super().ord(key)

    def __getitem__(self, word) -> tuple[int, int]:
        tf, df = super().get(word, (0, 0))
        idx = self.ord(word)
        return (tf + self.new_tf[idx], df + self.new_df[idx])

    def __iter__(self) -> Generator[str, None, None]:
        return chain(self._keys, self.new_words)

    def items(self) -> Generator[tuple[str, tuple[int, int]], None, None]:
        for k in self:
            yield k, self[k]

    def total(self) -> int:
        return self._total + self._new_total

    def write(self):
        with self.f_keys.open("a") as f:
            for token in self.new_words:
                f.write(token)
                f.write("\n")
        with self.f_tf.open("wb") as f:
            fresh_tf = array("I", self.tf)
            for i, v in enumerate(self.new_tf[: len(self.tf)]):
                if v == 0:
                    continue
                fresh_tf[i] += v
            fresh_tf.extend(self.new_tf[len(self.tf) :])
            fresh_tf.tofile(self.f_tf.open("wb"))
        with self.f_df.open("wb") as f:
            fresh_df = array("I", self.df)
            for i, v in enumerate(self.new_df[: len(self.df)]):
                if v == 0:
                    continue
                fresh_df[i] += v
            fresh_df.extend(self.new_df[len(self.df) :])
            fresh_df.tofile(self.f_df.open("wb"))
        new_keys = OrderedTrie(self)
        self.new_words = dict()
        self.new_tf = array("I", (0 for i in range(len(self.new_tf))))
        self.tf = fresh_tf
        self.new_df = array("I", (0 for i in range(len(self.new_df))))
        self.df = fresh_df
        self._keys = new_keys
        total = self.total()
        self.f_total.write_bytes(struct.pack("I", total))
        self._new_total = 0
        self._total = total

    def merge(self, other: Self):
        for k, v in other.items():
            tf, df = v
            self._add(k, tf)
            self.new_df[self.ord(k)] += df
