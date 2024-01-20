from array import array
from collections import Counter
from pathlib import Path
import struct
from tempfile import TemporaryDirectory
from typing import Iterable

from locutions import Locutions, LocutionsCold


class tempData:
    def __init__(self, values: Iterable[str], name: str = "keys.txt"):
        self.temp = TemporaryDirectory()
        self.path = Path(self.temp.name) / name
        with open(self.path, "w") as f:
            f.write("\n".join(values))
            f.write("\n")

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.temp.cleanup()


class tempDataLocutions(tempData):
    def __init__(self, values: list[str]):
        super().__init__(values, "keys.txt")
        v = array("I", (1 for i in values))
        v.tofile((Path(self.temp.name) / "tf.bin").open("wb"))
        v.tofile((Path(self.temp.name) / "df.bin").open("wb"))
        (Path(self.temp.name) / "total.bin").write_bytes(struct.pack("I", 1))


def test_cold():
    with tempDataLocutions(["je", "mange", "des", "carottes"]) as data:
        l = LocutionsCold(data.temp.name)
        assert "mange" in l
        assert 4 == len(l)
        assert (1, 1) == l["mange"]


def test_hot():
    with tempDataLocutions(["je", "mange", "des", "carottes"]) as data:
        hot = Locutions(data.temp.name)
        assert 2 == hot.ord("des")
        assert (1, 1) == hot["des"]
        hot.add_document(["des", "patates", "et", "des", "petits", "pois"])
        assert (3, 2) == hot["des"]
        assert [
            "je",
            "mange",
            "des",
            "carottes",
            "patates",
            "et",
            "petits",
            "pois",
        ] == list(hot)
        assert 1 == hot.tf[2]
        assert 2 == hot.new_tf[2]
        assert 2 == hot.total()
        hot.write()
        assert 3 == hot.tf[2]
        assert 0 == hot.new_tf[2]
        values = array("I")
        values.fromfile((Path(data.temp.name) / "tf.bin").open("rb"), 7)
        print(values)
        assert 3 == values[2]
        assert (
            "pois"
            == (Path(data.temp.name) / "keys.txt").open("r").readlines()[-1].strip()
        )


def test_write():
    with TemporaryDirectory() as temp:
        loc = Locutions(Path(temp) / "test", create=True)
        loc.add_document(["je", "mange", "des", "carottes"])
        assert "des" in loc
        print(list(loc))
        loc.write()
        keys = (Path(temp) / "test/keys.txt").read_text().split("\n")[:-1]
        assert 4 == len(keys), "keys are written"
        assert (
            4 * 4 == (Path(temp) / "test/tf.bin").stat().st_size
        ), "values are written"
        assert 4 == len(loc.tf)
        assert 4 == len(loc._keys)
        assert "des" in loc
        assert (1, 1) == loc["des"]


def test_counter():
    with TemporaryDirectory() as temp:
        loc = Locutions(Path(temp) / "test", create=True)
        loc.add_counter(Counter(["je", "mange", "des", "carottes"]))
        assert 1 == loc.ord("mange")
        assert 4 == len(loc)


def test_merge():
    with TemporaryDirectory() as temp:
        a = Locutions(Path(temp) / "a", create=True)
        b = Locutions(Path(temp) / "b", create=True)
        a.add_document(["je", "mange", "des", "carottes"])
        assert "des" in a
        b.add_document(["et", "des", "petits", "pois"])
        assert "des" in b
        a.write()
        b.write()
        a.merge(b)
        a.write()
        assert (2, 2) == a["des"]


if __name__ == "__main__":
    test_write()
