import pytest

from boltons.urlutils import URL, URLParseError, find_all_links, parse_host

NUL_HOST_DOCUMENT = "see http://a\x00b/ for details"


def test_find_all_links_returns_a_list_when_one_url_is_unparsable():
    assert isinstance(find_all_links(NUL_HOST_DOCUMENT), list)


def test_find_all_links_with_text_preserves_the_original_text():
    found = find_all_links(NUL_HOST_DOCUMENT, with_text=True)
    assert "".join(str(item) for item in found) == NUL_HOST_DOCUMENT


def test_broken_port_still_degrades_as_before():
    assert find_all_links("see http://a:b/ for details") == []


def test_invalid_ipv6_literal_still_raises_url_parse_error():
    with pytest.raises(URLParseError):
        parse_host("[::zz]")


def test_parse_host_and_url_with_nul_host_do_not_leak_bare_valueerror():
    for inp in ("a\x00b", "[\x00]"):
        try:
            parse_host(inp)
        except URLParseError:
            pass
    url = URL("http://a\x00b/")
    assert isinstance(url, URL)
