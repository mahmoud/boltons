import pytest

from boltons.urlutils import URL


@pytest.mark.parametrize('text', [
    'http://[::1]:8080/path',
    'http://[::1]/path',
    'https://[2001:db8::1]:443/path',
    'http://[::1]:0/path',
    'https://user:p%40ss@[::ffff:192.0.2.1]:8443/a?x=1&x=2#fragment',
    'http://[2001:DB8:0:0:0:0:0:1]/path',
])
def test_from_parts_preserves_ipv6_authority(text):
    original = URL(text)
    rebuilt = URL.from_parts(
        scheme=original.scheme,
        host=original.host,
        port=original.port,
        path_parts=original.path_parts,
        query_params=original.query_params,
        fragment=original.fragment,
        username=original.username,
        password=original.password,
    )

    for full_quote in (False, True):
        assert rebuilt.to_text(full_quote=full_quote) == original.to_text(
            full_quote=full_quote)
        assert rebuilt.get_authority(full_quote=full_quote, with_userinfo=True) == (
            original.get_authority(full_quote=full_quote, with_userinfo=True))
    assert rebuilt.host == original.host
    assert rebuilt.family == original.family
