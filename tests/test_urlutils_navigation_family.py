import socket

import pytest

from boltons.urlutils import URL


@pytest.mark.parametrize('as_url', [False, True])
@pytest.mark.parametrize(('base', 'dest', 'expected', 'family'), [
    ('https://[2001:db8::1]:8443/a/b', 'child',
     'https://[2001:db8::1]:8443/a/child', socket.AF_INET6),
    ('https://[::1]/a/b', '/root', 'https://[::1]/root', socket.AF_INET6),
    ('https://[::1]/a/b?old=1', '?new=1',
     'https://[::1]/a/b?new=1', socket.AF_INET6),
    ('https://[::1]/a/b?old=1', '#new',
     'https://[::1]/a/b?old=1#new', socket.AF_INET6),
    ('https://[::1]/a/b?old=1#old', '',
     'https://[::1]/a/b?old=1', socket.AF_INET6),
    ('https://example.org/a/b', '//[2001:db8::2]/x',
     'https://[2001:db8::2]/x', socket.AF_INET6),
    ('https://[::1]/a/b', '//example.org/x',
     'https://example.org/x', None),
    ('https://[::1]/a/b', '//127.0.0.2/x',
     'https://127.0.0.2/x', socket.AF_INET),
    ('https://127.0.0.1/a/b', 'child',
     'https://127.0.0.1/a/child', socket.AF_INET),
    ('https://example.org/a/b', 'child',
     'https://example.org/a/child', None),
    ('https://example.org/a/b', 'https://[::1]/x',
     'https://[::1]/x', socket.AF_INET6),
])
def test_navigate_preserves_address_family(
    base, dest, expected, family, as_url
):
    original = URL(base)
    destination = URL(dest) if as_url else dest
    result = original.navigate(destination)

    assert result.to_text() == expected
    assert result.family == family
    assert URL(result.to_text()) == result
    assert original.to_text() == base
    if as_url:
        assert destination.to_text() == dest
        assert result is not destination
