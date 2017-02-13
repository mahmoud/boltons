# -*- coding: utf-8 -*-

import pytest

from boltons.urlutils import URL, _URL_RE


# fully quoted urls that should round trip
TEST_URLS = [
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
     'tr=udp://tracker.ccc.de:80&tr=udp://open.demonii.com:1337'),
    # from twisted:
    "http://localhost",
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
    "http://(%C3%A9)/(%C3%A9)?(%C3%A9)&(%C3%A9)=(%C3%A9)#(%C3%A9)"
    ]


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


@pytest.fixture(scope='module', params=TEST_URLS)
def test_roundtrip(test_url):
    result = URL(test_url).to_text(full_quote=True)
    assert test_url == result


def test_basic():
    u1 = URL('http://googlewebsite.com/e-shops.aspx')
    assert isinstance(u1.to_text(), unicode)
    assert u1.host == 'googlewebsite.com'


def test_utf8_url():
    url = URL('http://\xd9\x85\xd8\xab\xd8\xa7\xd9\x84'
              '.\xd8\xa2\xd8\xb2\xd9\x85\xd8\xa7'
              '\xdb\x8c\xd8\xb4\xdb\x8c')
    assert url.scheme == 'http'
    assert url.host == u'مثال.آزمایشی'


def test_idna():
    u1 = URL(u'http://bücher.ch')
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
    if not url_obj.query_params or url_obj.fragment:
        return True
    qp_text = url_obj.query_params.to_text(full_quote=True)
    assert test_url.endswith(qp_text)


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


def test_parse_equals_in_qp_value():
    u = URL('http://localhost/?=x=x=x')
    assert u.q[''] == 'x=x=x'
    assert u.to_text() == 'http://localhost/?=x%3Dx%3Dx'

    u = URL('http://localhost/?foo=x=x=x&bar=y')
    assert u.q['foo'] == 'x=x=x'
    assert u.q['bar'] == 'y'


def test_identical_equal():
    u = URL('http://example.com/path?query=param#frag')
    assert u == u


def test_equal():
    u = URL('http://example.com/path?query=param#frag')
    bono = URL('http://example.com/path?query=param#frag')
    assert bono == u


def test_not_equal():
    u = URL('http://example.com/path?query=param1#frag')
    bono = URL('http://example.com/path?query=param2#frag')
    assert bono != u


def _test_bad_utf8():  # not part of the API
    bad_bin_url = 'http://xn--9ca.com/%00%FF/%C3%A9'
    url = URL(bad_bin_url)

    expected = ('http://\N{LATIN SMALL LETTER E WITH ACUTE}.com/'
                '%00%FF/'
                '\N{LATIN SMALL LETTER E WITH ACUTE}')

    actual = url.to_text()

    assert expected == actual


def test_userinfo():
    url = URL('http://someuser:somepassword@example.com/some-segment@ignore')
    assert url.username == 'someuser'
    assert url.password == 'somepassword'
    assert url.to_text() == 'http://someuser:somepassword@example.com/some-segment@ignore'


def test_quoted_userinfo():
    url = URL('http://wikipedia.org')
    url.username = u'user'
    url.password = u'p@ss'
    assert url.to_text(full_quote=True) == 'http://user:p%40ss@wikipedia.org'


def test_mailto():
    mt = 'mailto:mahmoud@hatnote.com'
    assert URL(mt).to_text() == mt


# Examples from RFC 3986 section 5.4, Reference Resolution Examples
# painstakingly copied from the lovingly transcribed version in
# twisted's test_url, with inapplicable cases removed
REL_URL_BASE = 'http://a/b/c/d;p?q'
REL_URL_TEST_CASES = [
    # "Normal"
    #('g:h', 'g:h'),     # Not supported:  scheme with relative path
    ('g', 'http://a/b/c/g'),
    ('./g', 'http://a/b/c/g'),
    ('g/', 'http://a/b/c/g/'),
    ('/g', 'http://a/g'),
    (';x', 'http://a/b/c/;x'),
    ('g;x', 'http://a/b/c/g;x'),
    ('', 'http://a/b/c/d;p?q'),
    ('.', 'http://a/b/c/'),
    ('./', 'http://a/b/c/'),
    ('..', 'http://a/b/'),
    ('../', 'http://a/b/'),
    ('../g', 'http://a/b/g'),
    ('../..', 'http://a/'),
    ('../../', 'http://a/'),
    ('../../g', 'http://a/g'),

    # Abnormal examples
    # ".." cannot be used to change the authority component of a URI.
    ('../../../g', 'http://a/g'),  # TODO (rooted?)
    ('../../../../g', 'http://a/g'),  # TODO (rooted)?

    # Only include "." and ".." when they are only part of a larger segment,
    # not by themselves.
    ('/./g', 'http://a/g'),
    ('/../g', 'http://a/g'),
    ('g.', 'http://a/b/c/g.'),
    ('.g', 'http://a/b/c/.g'),
    ('g..', 'http://a/b/c/g..'),
    ('..g', 'http://a/b/c/..g'),

    # Unnecessary or nonsensical forms of "." and "..".
    ('./../g', 'http://a/b/g'),
    ('./g/.', 'http://a/b/c/g/'),
    ('g/./h', 'http://a/b/c/g/h'),
    ('g/../h', 'http://a/b/c/h'),
    ('g;x=1/./y', 'http://a/b/c/g;x=1/y'),
    ('g;x=1/../y', 'http://a/b/c/y'),
]


def test_suffix_normalize():
    for suffix, expected in REL_URL_TEST_CASES:
        url = URL(REL_URL_BASE)
        url.normalize(suffix)
        assert url.path == URL(expected).path

    return


def test_self_normalize():
    url = URL('http://hatnote.com/a/../../b?k=v#hashtags')
    url.normalize()
    assert url.to_text() == 'http://hatnote.com/b?k=v#hashtags'


def test_netloc_slashes():
    # basic sanity checks
    url = URL('mailto:mahmoud@hatnote.com')
    assert url.scheme == 'mailto'
    assert url.to_text() == 'mailto:mahmoud@hatnote.com'

    url = URL('http://hatnote.com')
    assert url.scheme == 'http'
    assert url.to_text() == 'http://hatnote.com'

    # test that unrecognized schemes stay consistent with '//'
    url = URL('newscheme:a:b:c')
    assert url.scheme == 'newscheme'
    assert url.to_text() == 'newscheme:a:b:c'

    url = URL('newerscheme://a/b/c')
    assert url.scheme == 'newerscheme'
    assert url.to_text() == 'newerscheme://a/b/c'

    # test that reasonable guesses are made
    url = URL('git+ftp://gitstub.biz/glyph/lefkowitz')
    assert url.scheme == 'git+ftp'
    assert url.to_text() == 'git+ftp://gitstub.biz/glyph/lefkowitz'

    url = URL('what+mailto:freerealestate@enotuniq.org')
    assert url.scheme == 'what+mailto'
    assert url.to_text() == 'what+mailto:freerealestate@enotuniq.org'

    return
