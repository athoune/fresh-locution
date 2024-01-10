from io import BytesIO
from wiki_abstract import docs


def test_doc():
    txt = b"""
<feed>
<doc>
<title>Wikipedia: Anarchism</title>
<url>https://en.wikipedia.org/wiki/Anarchism</url>
<abstract>Anarchism is a political philosophy and movement that is skeptical of all justifications for authority and seeks to abolish the institutions it claims maintain unnecessary coercion and hierarchy, typically including nation-states, and capitalism. Anarchism advocates for the replacement of the state with stateless societies and voluntary free associations.</abstract>
<links>
<sublink linktype="nav"><anchor>Etymology, terminology, and definition</anchor><link>https://en.wikipedia.org/wiki/Anarchism#Etymology,_terminology,_and_definition</link></sublink>
</links>
</doc>
</feed>
    """
    d = list(docs(BytesIO(txt)))
    assert 1 == len(d)
    assert "Anarchism" == d[0].title
