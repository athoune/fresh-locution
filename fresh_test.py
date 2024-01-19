from io import BytesIO

from fresh import count_doc
from nlp import locutions
from wiki_abstract import docs

txt = """
        ... there is an upstart Crow, beautified with our feathers, that with his Tiger's heart wrapped in a Player's hide, supposes he is as well able to bombast out a blank verse as the best of you: and being an absolute Johannes factotum, is in his own conceit the only Shake-scene in a country.
        Hell yeah!
             """


doc_raw = b"""
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


def test_count_doc():
    d = next(docs(BytesIO(doc_raw)))
    c = count_doc(d)
    print(c.most_common())
