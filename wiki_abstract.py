#! /usr/bin/env python

from dataclasses import dataclass
from pathlib import Path

from typing import Generator
import zstandard
from lxml import etree as ET


@dataclass(init=False)
class Doc:
    title: str
    url: str
    abstract: str


def wiki(p: [Path,str]) -> Generator[Doc, None, None]:
    dctx = zstandard.ZstdDecompressor()
    with open(p, "rb") as fh:
        for doc in dctx.stream_reader(fh):
            yield doc


def docs(reader) -> Generator[Doc, None, None]:
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
    import sys
    from tqdm import tqdm

    reader = wiki(sys.argv[1])
    for doc in tqdm(reader, unit=" docs", delay=30):
        pass
