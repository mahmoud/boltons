# -*- coding: utf-8 -*-

import pytest

from boltons.urlutils2 import URL, _URL_RE


TEST_URLS = [
    '*',  # e.g., OPTIONS *
    'http://googlewebsite.com/e-shops.aspx',
    'http://example.com:8080/search?q=123&business=Nothing%20Special',
    'http://hatnote.com:9000?arg=1&arg=2&arg=3',
    'https://xn--bcher-kva.ch',
    'http://xn--ggbla1c4e.xn--ngbc5azd/',
    'http://tools.ietf.org/html/rfc3986#section-3.4',
    'http://wiki:pedia@hatnote.com',
    'ftp://ftp.rfc-editor.org/in-notes/tar/RFCs0001-0500.tar.gz',
    'http://[1080:0:0:0:8:800:200C:417A]/index.html',
    'ssh://192.0.2.16:22/',
    'https://[::101.45.75.219]:80/?hi=bye',
    'ldap://[::192.9.5.5]/dc=example,dc=com??sub?(sn=Jensen)',
    'mailto:me@example.com?to=me@example.com&body=hi%20http://wikipedia.org',
    'news:alt.rec.motorcycle',
    'tel:+1-800-867-5309',
    'urn:oasis:member:A00024:x',
    ('magnet:?xt=urn:btih:1a42b9e04e122b97a5254e3df77ab3c4b7da725f&dn=Puppy%'
     '20Linux%20precise-5.7.1.iso&tr=udp://tracker.openbittorrent.com:80&'
     'tr=udp://tracker.publicbt.com:80&tr=udp://tracker.istole.it:6969&'
     'tr=udp://tracker.ccc.de:80&tr=udp://open.demonii.com:1337')]


UNICODE_URLS = [
    # 'http://مثال.آزمایشی'
    ('\xd9\x85\xd8\xab\xd8\xa7\xd9\x84'
     '.\xd8\xa2\xd8\xb2\xd9\x85\xd8\xa7'
     '\xdb\x8c\xd8\xb4\xdb\x8c')]


@pytest.fixture(scope="module", params=TEST_URLS)
def test_url(request):
    param = request.param
    return param


@pytest.fixture(scope="module", params=TEST_URLS)
def test_authority(request):
    match = _URL_RE.match(request.param)
    return match.groupdict()['authority']


def test_regex(test_url):
    match = _URL_RE.match(test_url)
    assert match.groupdict()


def test_basic():
    u1 = URL('http://googlewebsite.com/e-shops.aspx')
    assert isinstance(u1.to_text(), unicode)
    assert u1.host == 'googlewebsite.com'


def test_idna():
    u1 = URL('http://bücher.ch')
    assert u1.host == u'bücher.ch'
    assert u1.to_text(full_quote=True) == 'http://xn--bcher-kva.ch'
    assert u1.to_text(full_quote=False) == u'http://bücher.ch'

    u2 = URL('https://xn--bcher-kva.ch')
    assert u2.host == u'bücher.ch'
    assert u2.to_text(full_quote=True) == 'https://xn--bcher-kva.ch'
    assert u2.to_text(full_quote=False) == u'https://bücher.ch'


#def test_urlparse_equiv(test_url):
#    from urlparse import urlparse, urlunparse
#    url_obj = URL(test_url)
#    assert urlunparse(urlparse(test_url)) == urlunparse(url_obj)


def test_query_params(test_url):
    url_obj = URL(test_url)
    if not url_obj.query_params:
        return True
    assert test_url.endswith(url_obj.query_params.to_text())


def test_iri_query():
    url = URL(u'http://minerals.rocks.ore/?mountain=\N{MOUNTAIN}')
    assert url.query_params['mountain'] == u'\N{MOUNTAIN}'
    assert url.query_params.to_text().endswith(u'%E2%9B%B0')  # \N{MOUNTAIN}')

    # fails because urlparse assumes query strings are encoded with latin1
    # url2 = URL(url.to_bytes())
    # assert url2.query_params['mountain'] == u'\N{MOUNTAIN}'


def test_iri_path():
    url = URL(u'http://minerals.rocks.ore/mountain/\N{MOUNTAIN}/')
    assert url.path == u'/mountain/\N{MOUNTAIN}/'
    # assert url.to_bytes().endswith('%E2%9B%B0/')


#def test_urlparse_obj_input():  # TODO
#    with pytest.raises(TypeError):
#        URL(object())


def test_url_copy():
    url = URL('http://example.com/foo?bar=baz')
    url_copy = URL(url)
    assert url == url_copy


def test_invalid_port():
    with pytest.raises(ValueError):
        URL('http://reader.googlewebsite.com:neverforget')


def test_invalid_ipv6():
    invalid_ipv6_ips = ['2001::0234:C1ab::A0:aabc:003F',
                        '2001::1::3F']
    for ip in invalid_ipv6_ips:
        with pytest.raises(ValueError):
            URL('http://[' + ip + ']')


def test_roundtrip():
    # fully quoted urls that should round trip
    tests = ("http://localhost",
             "http://localhost/",
             "http://localhost/foo",
             "http://localhost/foo/",
             "http://localhost/foo!!bar/",
             "http://localhost/foo%20bar/",
             "http://localhost/foo%2Fbar/",
             "http://localhost/foo?n",
             "http://localhost/foo?n=v",
             "http://localhost/foo?n=/a/b",
             "http://example.com/foo!@$bar?b!@z=123",
             "http://localhost/asd?a=asd%20sdf/345",
             "http://(%2525)/(%2525)?(%2525)&(%2525)=(%2525)#(%2525)",
             "http://(%C3%A9)/(%C3%A9)?(%C3%A9)&(%C3%A9)=(%C3%A9)#(%C3%A9)")

    for test in tests:
        result = URL(test).to_text(full_quote=True)
        assert test == result


def test_parse_equals_in_qp_value():
    u = URL('http://localhost/?=x=x=x')
    assert u.q[''] == 'x=x=x'
    assert u.to_text() == 'http://localhost/?=x%3Dx%3Dx'

    u = URL('http://localhost/?foo=x=x=x&bar=y')
    assert u.q['foo'] == 'x=x=x'
    assert u.q['bar'] == 'y'
