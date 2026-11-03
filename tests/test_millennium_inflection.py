import pytest

from boltons.strutils import pluralize, singularize


@pytest.mark.parametrize(
    "singular, plural",
    [
        ("millennium", "millennia"),
        ("Millennium", "Millennia"),
        ("MILLENNIUM", "MILLENNIA"),
    ],
)
def test_pluralize_millennium(singular, plural):
    assert pluralize(singular) == plural
    assert pluralize(plural) == plural


@pytest.mark.parametrize(
    "singular, plural",
    [
        ("millennium", "millennia"),
        ("Millennium", "Millennia"),
        ("MILLENNIUM", "MILLENNIA"),
    ],
)
def test_singularize_millennia(singular, plural):
    assert singularize(plural) == singular
    assert singularize(pluralize(singular)) == singular


@pytest.mark.parametrize(
    "singular, plural", [("criterion", "criteria"), ("goose", "geese")]
)
def test_other_irregular_inflections_are_unchanged(singular, plural):
    assert pluralize(singular) == plural
    assert singularize(plural) == singular
