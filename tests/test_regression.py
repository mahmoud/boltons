"""Regression test: an unparsable URL must not abort ``find_all_links``.

Fails on the affected release (boltons 26.2.0), passes with the proposed patch.

The assertions are the *documented* behaviour, not the observed one:

* ``find_all_links`` is documented as returning a list of ``URL`` objects it found in plain
  text -- so a text containing one unparsable URL must still return a list.
* With ``with_text=True`` it documents returning the text interleaved with the URLs, so the
  original text must be reconstructable.  That is the strongest available statement of "the
  scan kept going", and it is why the test does not merely assert "did not raise".
"""

import pytest

from boltons.urlutils import URL, find_all_links, parse_host

NUL = "\x00"

#: A host carrying an embedded NUL.  It is not a valid host in any form, which is why the
#: library's own design is to treat an unparsable host as a non-IP hostname and continue.
NUL_HOST_DOCUMENT = f"see http://a{NUL}b/ for details"


def test_find_all_links_returns_a_list_when_one_url_is_unparsable():
    found = find_all_links(NUL_HOST_DOCUMENT)
    assert isinstance(found, list)


def test_find_all_links_with_text_preserves_the_original_text():
    found = find_all_links(NUL_HOST_DOCUMENT, with_text=True)
    assert "".join(str(item) for item in found) == NUL_HOST_DOCUMENT


def test_find_all_links_does_not_raise_before_reaching_a_later_url():
    # the defect aborts the whole scan, so a good URL after the bad one is lost with it
    found = find_all_links(f"http://a{NUL}b/ then http://good.example/")
    assert any(isinstance(item, URL) and "good.example" in str(item) for item in found)


def test_parse_host_treats_a_nul_carrying_host_as_a_non_ip_hostname():
    # the library's existing precedent is `UnicodeEncodeError: pass` in the IPv6 branch and
    # `family = None` in the IPv4 branch: a host that is not an IP literal is a hostname
    family, host = parse_host(f"a{NUL}b")
    assert family is None
    assert host == f"a{NUL}b"


def test_broken_port_still_degrades_as_before():
    # the documented path the handler was written for must keep working
    assert find_all_links("see http://a:b/ for details") == []


def test_invalid_ipv6_literal_still_raises_url_parse_error():
    # the patch must not swallow the error the library *does* mean to raise
    from boltons.urlutils import URLParseError

    with pytest.raises(URLParseError):
        parse_host("[::zz]")
