import math
import struct
from array import array
from collections import Counter
from pathlib import Path

import plyvel


class Db:
    """
    A Db for counting tokens
    leveldb (a key/value store) is used for storing tokens, a get them an Id.
    Counting term frequency and document frequency are done with vectors, using token id as its position.
    """
    keys: plyvel.DB
    tf: array("I")
    df: array("I")
    n_docs: int
    size: int

    def __init__(self, path: str | Path) -> None:
        if isinstance(path, str):
            path = Path(path)
        path.mkdir(exist_ok=True)
        exist = (path / "db").exists()
        self.f_tf = path / "tf"
        self.f_df = path / "df"
        self.f_n_docs = path / "docs"
        if not exist:
            (path / "db").mkdir()
        self.keys = plyvel.DB(str(path / "db"), create_if_missing=True)
        self.tf = array("I")
        self.df = array("I")
        self.size = 0
        self.n_docs = 0
        if exist:
            self.size = int(self.f_df.lstat().st_size / 4)
            self.tf.fromfile(self.f_tf.open("rb"), self.size)
            self.df.fromfile(self.f_df.open("rb"), self.size)
            self.n_docs = struct.unpack("I", self.f_n_docs.read_bytes())[0]

    def close(self):
        self.keys.close()

    def __len__(self) -> int:
        return self.size

    def __contains__(self, key) -> bool:
        return self.keys.get(key.encode("utf8")) is not None

    def __getitem__(self, key) -> tuple[int, int]:
        if isinstance(key, str):
            key = key.encode("utf8")
        v = self.keys.get(key)
        if v is None:
            raise KeyError(key)
        pos = struct.unpack("I", v)[0]
        return (self.tf[pos], self.df[pos])

    def add_doc(self, document: Counter) -> int:
        wb = self.keys.write_batch()
        fresh = 0
        for k, v in document.items():
            k = k.encode("utf8")
            pos = self.keys.get(k)
            if pos is None:
                wb.put(k, struct.pack("I", self.size))
                self.size += 1
                self.tf.append(v)
                self.df.append(1)
                fresh += 1
            else:
                n = struct.unpack("I", pos)[0]
                self.tf[n] += v
                self.df[n] += 1
        wb.write()
        self.n_docs += 1
        return fresh

    def write(self) -> None:
        self.df.tofile(self.f_df.open("wb"))
        self.tf.tofile(self.f_tf.open("wb"))
        self.f_n_docs.open("wb").write(struct.pack("I", self.n_docs))

    def tf_idf(self, key: str) -> float:
        pos = self.keys.get(key.encode("utf8"))
        if pos is None:
            return 0
        pos = struct.unpack("I", pos)[0]
        tf = self.tf[pos]
        df = self.df[pos]
        return tf * math.log(float(self.n_docs) / df)
