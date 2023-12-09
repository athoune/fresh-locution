from pathlib import Path
from typing import Iterable
from sortedcontainers import SortedList
from array import array
import io


class Locutions:
    values: array
    keys: SortedList

    def __init__(self, folder: str | Path, create: bool = False):
        if isinstance(folder, str):
            folder = Path(folder)
        if not folder.exists():
            if not create:
                raise FileNotFoundError(f"Folder not found {folder}")
            folder.mkdir()
        self.f_keys = folder / "keys.txt"
        self.f_values = folder / "values.bin"
        self.values = array("I")
        if self.f_values.exists():
            size = self.f_values.lstat().st_size
            self.values.fromfile(self.f_values.open("rb"), int(size / 4))  # It's int32
        if self.f_keys.exists():
            self.keys = SortedList()
            with self.f_keys.open("r") as f:
                for _ in range(len(self.values)):
                    self.keys.add(f.readline()[:-1])
        else:
            self.keys = SortedList()
        self.dirty_keys: int = len(self.values)
        self.dirty_values: array("b") = array("b", [0] * len(self.values))

    def add(self, keys: Iterable[str]):
        for key in keys:
            try:
                idx = self.keys.index(key)
            except ValueError:
                self.keys.add(key)
                self.values.append(1)
                self.dirty_values.append(1)
            else:
                self.values[idx] += 1
                self.dirty_values[idx] = 1

    def get(self, key) -> int:
        try:
            idx = self.keys.index(key)
        except ValueError:
            return 0
        else:
            return self.values[idx]

    def dump(self):
        self.values.tofile(self.f_values.open("wb"))  # FIXME: use the dirty map
        with self.f_keys.open("w") as f:  # FIXME: use the dirt
            for token in self.keys:
                f.write(token)
                f.write("\n")
