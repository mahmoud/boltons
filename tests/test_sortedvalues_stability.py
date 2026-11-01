import pytest

from boltons.dictutils import FastIterOrderedMultiDict, OrderedMultiDict
from boltons.urlutils import QueryParamDict, URL


@pytest.mark.parametrize(
    "mapping_type", [OrderedMultiDict, FastIterOrderedMultiDict, QueryParamDict]
)
@pytest.mark.parametrize("reverse", [False, True])
def test_sortedvalues_preserves_ties_and_key_positions(mapping_type, reverse):
    first = {"rank": 1, "name": "first"}
    second = {"rank": 1, "name": "second"}
    high = {"rank": 2, "name": "high"}
    other_first = {"rank": 0, "name": "other first"}
    other_second = {"rank": 0, "name": "other second"}
    pairs = [
        ("a", first),
        ("b", other_first),
        ("a", high),
        ("b", other_second),
        ("a", second),
    ]
    original = mapping_type(pairs)
    calls = []

    def rank(value):
        calls.append(value)
        return value["rank"]

    result = original.sortedvalues(key=rank, reverse=reverse)
    expected_a = [high, first, second] if reverse else [first, second, high]

    assert type(result) is mapping_type
    assert result is not original
    assert result.keys(multi=True) == [key for key, _ in pairs]
    assert result.getlist("a") == expected_a
    assert result.getlist("b") == [other_first, other_second]
    assert original.items(multi=True) == pairs
    assert sorted(map(id, calls)) == sorted(id(value) for _, value in pairs)
    for actual, expected in zip(result.getlist("a"), expected_a):
        assert actual is expected


@pytest.mark.parametrize("reverse", [False, True])
def test_sortedvalues_preserves_query_parameter_ties(reverse):
    url = URL("https://example.com/?a=beta&b=keep&a=Beta&a=alpha")
    original = url.query_params.items(multi=True)
    result = url.query_params.sortedvalues(key=str.casefold, reverse=reverse)

    expected = ["beta", "Beta", "alpha"] if reverse else ["alpha", "beta", "Beta"]
    assert result.getlist("a") == expected
    assert result.keys(multi=True) == ["a", "b", "a", "a"]
    assert url.query_params.items(multi=True) == original
