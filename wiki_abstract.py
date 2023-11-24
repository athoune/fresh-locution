#! /usr/bin/env python

import io
from dataclasses import dataclass

from typing import Generator
import zstandard
import xml.etree.ElementTree as ET


@dataclass(init=False)
class Doc:
    title: str
    url: str
    abstract: str


def wiki(p) -> Generator[Doc, None, None]:
    dctx = zstandard.ZstdDecompressor()
    parser = ET.XMLPullParser(["start", "end"])
    # help(dctx.read_to_iter)
    with open(p, "rb") as fh:
        stream_reader = dctx.stream_reader(fh)
        text_stream = io.TextIOWrapper(stream_reader, encoding="utf-8")
        bread_crumbs = []
        doc = Doc()
        for line in text_stream:
            parser.feed(line)
            for event, elem in parser.read_events():
                if event == "start":
                    bread_crumbs.append(elem.tag)
                elif event == "end":
                    bread_crumbs.pop()
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

    for doc in wiki(sys.argv[1]):
        print(doc)
