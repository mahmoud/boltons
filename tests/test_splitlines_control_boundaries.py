import pytest

from boltons.strutils import indent, iter_splitlines


@pytest.mark.parametrize("separator", ["\x1c", "\x1d", "\x1e"])
@pytest.mark.parametrize("trailing", [False, True])
def test_control_boundaries_match_string_splitlines(separator, trailing):
    text = separator + "first" + separator + "second" + (separator if trailing else "")
    expected = text.splitlines()
    if trailing:
        expected.append(
            ""
        )  # iter_splitlines retains its documented terminal empty line
    assert list(iter_splitlines(text)) == expected


@pytest.mark.parametrize("separator", ["\x1c", "\x1d", "\x1e"])
def test_indent_control_separated_lines(separator):
    assert indent("first" + separator + "second", "> ") == "> first\n> second"


def test_existing_boundaries_and_empty_input():
    text = "\r\nfirst\nsecond\vthird\ffourth\rfifth\x85sixth\u2028seventh\u2029"
    assert list(iter_splitlines(text)) == text.splitlines() + [""]
    assert list(iter_splitlines("")) == []
