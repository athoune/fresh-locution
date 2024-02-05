import struct
from array import array
from collections import Counter
from pathlib import Path

import plyvel


class Db:
    keys: plyvel.DB
    tf: array("I")
    df: array("I")
    size: int

    def __init__(self, path: str | Path) -> None:
        if isinstance(path, str):
            path = Path(path)
        exist = (path / "db").exists()
        self.f_tf = path / "tf"
        self.f_df = path / "df"
        self.keys = plyvel.DB(str(path / "db"), create_if_missing=True)
        self.tf = array("I")
        self.df = array("I")
        self.size = 0
        if exist:
            self.size = self.f_df.lstat().st_size / 4
            self.tf.fromfile(self.f_tf.open("rb"), self.size)
            self.df.fromfile(self.f_df.open("rb"), self.size)

    def add_doc(self, document: Counter) -> int:
        wb = self.keys.write_batch()
        fresh = 0
        for k, v in document.items():
            k = k.encode('utf8')
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
        return fresh

    def write(self) -> None:
        self.df.tofile(self.f_df.open('wb'))
        self.tf.tofile(self.f_tf.open('wb'))
