from nlp import ngram, tokenize


def test_ngram():
    txt = "Albedo is the fraction of sunlight that is diffusely reflected by a body"
    n = list(ngram(txt.split(" "), 3))
    assert ["Albedo", "is", "the"] == n[0]
    assert ["is", "the", "fraction"] == n[1]


def test_tokenize():
    txt = """
    An American in Paris is a jazz-influenced symphonic poem (or tone poem) for orchestra by American composer George Gershwin first performed in 1928.
    It was inspired by the time that Gershwin had spent in Paris and evokes the sights and energy of the French capital during the .
    """
    t = list(tokenize(txt))
    assert 2 == len(t)
    assert "american" == t[0][1]
