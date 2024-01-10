from array import array
from collections import defaultdict
from pathlib import Path
from struct import pack
from typing import Generator, Iterable

from trie import OrderedTrie


class LocutionsCold:
    values: array
    _keys: OrderedTrie

    def __init__(self, folder: str | Path, create: bool = False):
        if isinstance(folder, str):
            folder = Path(folder)
        if not folder.exists():
            if not create:
                raise FileNotFoundError(f"Folder not found {folder}")
            folder.mkdir()
        self.f_keys = folder / "keys.txt"
        self.f_values = folder / "values.bin"
        if self.f_keys.exists() != self.f_values.exists():
            raise FileNotFoundError("We need both keys.txt and values.bien")
        self.values = array("I")
        if self.f_values.exists():
            size = self.f_values.lstat().st_size
            self.values.fromfile(self.f_values.open("rb"), int(size / 4))  # It's int32
        self.dirty_keys = defaultdict(int)
        if not self.f_keys.exists():
            self.f_keys.open("wb")
        self._keys = OrderedTrie.fromfile(self.f_keys)
        self.dirty_keys: int = len(self.values)
        self.dirty_values: array("b") = array("b", [0] * len(self.values))

    def __len__(self) -> int:
        return len(self.values)

    def __contains__(self, key) -> bool:
        return key in self._keys

    def __getitem__(self, key) -> int:
        if key not in self._keys:
            raise KeyError(key)
        return self.values[self._keys[key]]

    def ord(self, key) -> int:
        "position of the key, can raise a KeyError"
        return self._keys[key]

    def get(self, key) -> int:
        try:
            idx = self._keys[key]
        except KeyError:
            return 0
        else:
            return self.values[idx]

    def __iter__(self) -> Generator[str, None, None]:
        for k in self._keys:
            yield k


class LocutionsHot:
    cold: LocutionsCold
    dirty_keys: dict
    values: array("I")

    def __init__(self, cold: LocutionsCold):
        self.dirty_keys = dict()
        self.values = array("I", (0 for i in range(len(cold))))
        self.cold = cold

    def add(self, keys: Iterable[str]):
        "Add some keys to count."
        for key in keys:
            try:
                self.values[self.ord(key)] += 1
            except KeyError:  # The key doesn't exist yet
                idx = len(self.values)
                self.values.append(1)
                self.dirty_keys[key] = idx

    def __contains__(self, key) -> bool:
        return key in self.cold or key in self.dirty_keys

    def __len__(self) -> int:
        return len(self.values)

    def ord(self, key) -> int:
        "position of the key, can raise a KeyError"
        if key in self.dirty_keys:
            return self.dirty_keys[key]
        return self.cold.ord(key)

    def __getitem__(self, key) -> int:
        return self.cold.get(key) + self.values[self.ord(key)]

    def __iter__(self) -> Generator[str, None, None]:
        for k in self.cold:
            yield k
        for k in self.dirty_keys:
            yield k

    def write(self):
        with self.cold.f_keys.open("a") as f:
            for token in self.dirty_keys:
                f.write(token)
                f.write("\n")
        with self.cold.f_values.open("wb") as f:
            fresh = array("I", self.cold.values)
            fresh.extend(self.values)
            for i, value in enumerate(self.values):
                if value == 0:
                    continue
                f.seek(i * 4)
                if i < len(self.cold.values):
                    fresh[i] += value
                    value += self.cold.values[i]
                f.write(pack("I", value))

        self.dirty_keys = dict()
        self.values = array("I", (0 for i in range(len(self.values))))
        freshKeys = OrderedTrie(self)
        self.cold.values = fresh
        self.cold._keys = freshKeys
