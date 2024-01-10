from array import array
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Iterable

from locutions import  LocutionsCold, LocutionsHot




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
        assert 2 == hot.ord("des")
        assert 1 == hot["des"]
        hot.add(["et", "des", "petits", "pois"])
        assert 2 == hot["des"]
        assert ["je", "mange", "des", "carottes", "et", "petits", "pois"] == list(hot)
        assert 1 == hot.values[2]
        hot.write()
        assert 2 == hot.cold.values[2]
        assert 0 == hot.values[2]
        values = array("I")
        values.fromfile((Path(data.temp.name) / "values.bin").open("rb"), 7)
        assert 2 == values[2]
        assert (
            "pois"
            == (Path(data.temp.name) / "keys.txt").open("r").readlines()[-1].strip()
        )


if __name__ == "__main__":
    test_hot()
