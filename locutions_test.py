from array import array
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Iterable

from locutions import Locutions, LocutionsCold, LocutionsHot


class tempData:
    def __init__(self, values: Iterable[str], name: str = "data.txt"):
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
        v.tofile((Path(self.temp.name) / "values.bin").open("wb"))




def test_cold():
    with tempDataLocutions(["je", "mange", "des", "carottes"]) as data:
        l = LocutionsCold(data.temp.name)
        assert "mange" in l
        assert 4 == len(l)


def test_hot():
    with tempDataLocutions(["je", "mange", "des", "carottes"]) as data:
        cold = LocutionsCold(data.temp.name)
        hot = LocutionsHot(cold)
        print(list(hot))
        assert 2 == hot.ord("des")
        assert 1 == hot["des"]
        hot.batch_add(["et", "des", "petits", "pois"])
        assert 2 == hot["des"]
        assert ["je", "mange", "des", "carottes", "et", "petits", "pois"] == list(hot)
        assert 1 == hot.values[2]
        hot.write()
        assert 2 == hot.cold.values[2]
        assert 0 == hot.values[2]
        values = array("I")
        values.fromfile((Path(data.temp.name) / "values.bin").open("rb"), 7)
        print(values)
        assert 2 == values[2]
        assert (
            "pois"
            == (Path(data.temp.name) / "keys.txt").open("r").readlines()[-1].strip()
        )


def test_write():
    with TemporaryDirectory() as temp:
        loc = Locutions(Path(temp) / "test", create=True)
        loc.batch_add(["je", "mange", "des", "carottes"])
        assert "des" in loc
        print(list(loc))
        loc.write()
        keys = (Path(temp) / "test/keys.txt").read_text().split("\n")[:-1]
        assert 4 == len(keys), "keys are written"
        assert 4*4 == (Path(temp) / "test/values.bin").stat().st_size, "values are written"
        assert 4 == len(loc.cold.values)
        assert 4 == len(loc.cold._keys)
        assert "des" in loc
        assert 1 == loc["des"]


def test_merge():
    with TemporaryDirectory() as temp:
        a = Locutions(Path(temp) / "a", create=True)
        b = Locutions(Path(temp) / "b", create=True)
        a.batch_add(["je", "mange", "des", "carottes"])
        assert "des" in a
        b.batch_add(["et", "des", "petits", "pois"])
        assert "des" in b
        a.write()
        b.write()
        a.merge(b)
        a.write()
        assert 2 == a["des"]


if __name__ == "__main__":
    test_write()
