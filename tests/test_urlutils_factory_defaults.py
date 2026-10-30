import pytest

from boltons.urlutils import URL


@pytest.mark.parametrize(
    "kwargs,text",
    [
        ({}, ""),
        ({"path_parts": ("a", "b")}, "a/b"),
        ({"host": "example.com", "port": 8080}, "//example.com:8080"),
        (
            {"scheme": "https", "host": "example.com", "password": "secret"},
            "https://:secret@example.com",
        ),
    ],
)
def test_from_parts_uses_empty_text_defaults(kwargs, text):
    result = URL.from_parts(**kwargs)
    result.normalize()
    assert result.to_text() == text
    for name in ("scheme", "host", "username", "password"):
        assert isinstance(getattr(result, name), str)


def test_explicit_parts_and_query_values_are_retained():
    result = URL.from_parts(
        scheme="https",
        host="example.com",
        path_parts=("", "a"),
        username="user",
        password="secret",
        port=8443,
        query_params=[("q", "one"), ("q", "two")],
        fragment="end",
    )
    assert result.to_text() == "https://user:secret@example.com:8443/a?q=one&q=two#end"
    assert result.query_params.getlist("q") == ["one", "two"]
