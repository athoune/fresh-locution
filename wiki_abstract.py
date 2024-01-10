#! /usr/bin/env python

from dataclasses import dataclass
from pathlib import Path
import gzip
import sys

from typing import BinaryIO, Generator
import zstandard
from lxml import etree as ET

dctx = zstandard.ZstdDecompressor()


@dataclass(init=False)
class Doc:
    """
    Wikipedia abstract document

    * Go to https://dumps.wikimedia.org/enwiki/
    * Pick a date
    * Search "Recombine extracted page abstracts for Yahoo"
    * Download the xml.gz file
    * Decompress it, recompress with more agressive zstd
    """

    title: str
    url: str
    abstract: str


def wiki(path: Path | str) -> Generator[Doc, None, None]:
    """
    Read a archive and yield Doc.
    If path is "-", source is STDIN.
    File can be compressed with zstd or gzip.
    """
    if isinstance(path, str):
        if path == "-":
            for d in docs(sys.stdin.buffer):
                yield d
            return
        path = Path(path)
    if path.suffix == ".zst":
        with open(path, "rb") as fh:
            for d in docs(dctx.stream_reader(fh)):
                yield d
    elif path.suffix == ".gz":
        for d in docs(gzip.open(path, mode="rb")):
            yield d
    else:
        for d in docs(path.open(encoding="utf8")):
            yield d


def docs(reader: BinaryIO) -> Generator[Doc, None, None]:
    "Parse Wikipedia abstract's XML format"
    doc = Doc()
    for event, elem in ET.iterparse(reader):
        if event == "end":
            if elem.tag == "doc":
                yield doc
                doc = Doc()
            elif elem.tag == "title":
                if elem.text.startswith("Wikipedia: "):
                    doc.title = elem.text[11:]
                else:
                    doc.title = elem.text
            elif elem.tag == "url":
                doc.url = elem.text
            elif elem.tag == "abstract":
                doc.abstract = elem.text


if __name__ == "__main__":
    from tqdm import tqdm

    reader = wiki(sys.argv[1])
    for doc in tqdm(reader, unit=" docs", delay=30):
        pass
