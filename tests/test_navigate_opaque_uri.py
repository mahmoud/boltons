import pytest

from boltons.urlutils import URL


@pytest.mark.parametrize('destination', [
    'mailto:me@example.com', 'urn:isbn:9780000000001',
    'data:text/plain,hello', 'g:h',
])
@pytest.mark.parametrize('as_url', [False, True])
def test_navigate_opaque_uri_replaces_base(destination, as_url):
    base = URL('https://user:secret@example.com:8443/a/b?q=1#old')
    target = URL(destination) if as_url else destination
    result = base.navigate(target)
    assert result.to_text() == destination
    assert result is not target
    assert base.to_text() == 'https://user:secret@example.com:8443/a/b?q=1#old'
