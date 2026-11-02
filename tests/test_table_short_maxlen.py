import pytest

from boltons.tableutils import Table


@pytest.mark.parametrize(
    "text, maxlen, expected",
    [
        ("abcdefgh", 1, "."),
        ("abcdefgh", 2, ".."),
        ("abcdefgh", 3, "..."),
        ("abcdefgh", 5, "ab..."),
        ("\u03b1\u03b2\u03b3\u03b4\u03b5\u03b6\u03b7\u03b8", 1, "."),
        ("\u03b1\u03b2\u03b3\u03b4\u03b5\u03b6\u03b7\u03b8", 2, ".."),
        ("\u03b1\u03b2\u03b3\u03b4\u03b5\u03b6\u03b7\u03b8", 3, "..."),
        ("\u03b1\u03b2\u03b3\u03b4\u03b5\u03b6\u03b7\u03b8", 5, "\u03b1\u03b2..."),
    ],
)
def test_table_cell_respects_positive_maxlen(text, maxlen, expected):
    table = Table([[text]], headers=["column"])

    assert table.to_text(with_headers=False, maxlen=maxlen) == expected
    assert len(expected) <= maxlen
    assert table[0] == [text]


@pytest.mark.parametrize("maxlen, marker", [(1, "."), (2, "..")])
def test_table_headers_respect_short_maxlen(maxlen, marker):
    table = Table([["abcdefgh"]], headers=["heading"])

    assert table.to_text(maxlen=maxlen) == "\n".join([marker, "-" * maxlen, marker])
    assert table.headers == ["heading"]


@pytest.mark.parametrize("text, maxlen", [("a", 1), ("ab", 2)])
def test_table_short_values_that_fit_remain_unchanged(text, maxlen):
    table = Table([[text]], headers=["column"])
    assert table.to_text(with_headers=False, maxlen=maxlen) == text


@pytest.mark.parametrize("maxlen", [None, 0])
def test_table_unlimited_maxlen_is_unchanged(maxlen):
    table = Table([["abcdefgh"]], headers=["column"])
    assert table.to_text(with_headers=False, maxlen=maxlen) == "abcdefgh"
