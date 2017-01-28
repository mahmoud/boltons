
import re
import socket
import string

unicode = type(u'')

# The unreserved URI characters (per RFC 3986)
_UNRESERVED_CHARS = (frozenset(string.uppercase)
                     | frozenset(string.lowercase)
                     | frozenset(string.digits)
                     | frozenset('-._~'))
_RESERVED_CHARS = frozenset(":/?#[]@!$&'()*+,;=")
_PCT_ENCODING = (frozenset('%')
                 | frozenset(string.digits)
                 | frozenset(string.uppercase[:6])
                 | frozenset(string.lowercase[:6]))
_ALLOWED_CHARS = _UNRESERVED_CHARS | _RESERVED_CHARS | _PCT_ENCODING

# URL parsing regex (per RFC 3986)
_URL_RE = re.compile(r'^((?P<scheme>[^:/?#]+):)?'
                     r'(//(?P<authority>[^/?#]*))?'
                     r'(?P<path>[^?#]*)'
                     r'(\?(?P<query>[^#]*))?'
                     r'(#(?P<fragment>.*))?')

_SCHEME_CHARS = re.escape(''.join(_ALLOWED_CHARS - set(':/?#')))
_AUTH_CHARS = re.escape(''.join(_ALLOWED_CHARS - set(':/?#')))
_PATH_CHARS = re.escape(''.join(_ALLOWED_CHARS - set('?#')))
_QUERY_CHARS = re.escape(''.join(_ALLOWED_CHARS - set('#')))
_FRAG_CHARS = re.escape(''.join(_ALLOWED_CHARS))


_HEX_CHAR_MAP = dict([(a + b, chr(int(a + b, 16)))
                      for a in string.hexdigits for b in string.hexdigits])
_ASCII_RE = re.compile('([\x00-\x7f]+)')


def minimal_percent_encode(text, safe):
    pass


def maximal_percent_decode(text, safe):
    pass


def unquote(s, encoding='utf8'):
    "unquote('abc%20def') -> 'abc def'. aka percent decoding."
    if isinstance(s, unicode):
        if '%' not in s:
            return s
        bits = _ASCII_RE.split(s)
        res = [bits[0]]
        append = res.append
        for i in range(1, len(bits), 2):
            if '%' in bits[i]:
                append(unquote(str(bits[i])).decode(encoding))
            else:
                append(bits[i])
            append(bits[i + 1])
        return u''.join(res)

    bits = s.split('%')
    if len(bits) == 1:
        return s
    res = [bits[0]]
    append = res.append
    for item in bits[1:]:
        try:
            append(_HEX_CHAR_MAP[item[:2]])
            append(item[2:])
        except KeyError:
            append('%')
            append(item)
    return ''.join(res)


class URLError(ValueError):
    pass


DEFAULT_ENCODING = 'utf8'


class URL(object):

    def __init__(self, url):
        # TODO: encoding param. The encoding that underlies the
        # percent-encoding is always utf8 for IRIs, but can be Latin-1
        # for other usage schemes.
        url_dict = {}
        if url:
            if isinstance(url, URL):
                url = url.to_text()  # better way to copy URLs?
            elif isinstance(url, bytes):
                try:
                    url = url.decode(DEFAULT_ENCODING)
                except UnicodeDecodeError as ude:
                    raise URLError('expected text or %s-encoded bytes.'
                                   ' try decoding the url bytes and passing in'
                                   ' the result. (got: %s)'
                                   % (DEFAULT_ENCODING, ude))
            url_dict = parse_url(url)

        _d = unicode()
        for attr in self._attrs:
            val = url_dict.get(attr, _d) or _d
            if attr in self._quotable_attrs and '%' in val:
                val = unquote(val)
            setattr(self, attr, val)
        return

    @classmethod
    def from_parts(cls, scheme=None, host=None, path=u'', query=u'',
                   fragment=u'', port=None, username=None, password=None):
        ret = cls()

        ret.scheme = scheme
        ret.host = host
        ret.path = path
        ret.query = query
        ret.fragment = fragment
        ret.port = port
        ret.username = username
        ret.password = password

        return ret

    @property
    def path_parts(self):
        return tuple(self.path.split(u'/'))

    @path_parts.setter
    def path_parts(self, part_iterable):
        """
        url.path_parts += ('c', 'd',)
        """
        self.path = u'/'.join(part_iterable)


def parse_host(host):
    """\
    returns:
      family (socket constant or None), host (string)

    >>> parse_host('googlewebsite.com')
    (None, 'googlewebsite.com')
    >>> parse_host('[::1])
    (10, '::1', 22)
    >>> parse_host('192.168.1.1')
    (2, '192.168.1.1')
    """
    if not host:
        return None, u''
    if u':' in host and u'[' == host[0] and u']' == host[-1]:
        host = host[1:-1]
        try:
            socket.inet_pton(socket.AF_INET6, host)
        except socket.error:
            raise URLError('invalid IPv6 host: %r' % host)
        else:
            family = socket.AF_INET6
            return family, host
    try:
        socket.inet_pton(socket.AF_INET, host)
    except socket.error:
        family = None  # not an IP
    else:
        family = socket.AF_INET
    return family, host


def parse_url(url_text):
    """
    >>> urlutils2.parse_url('http://127.0.0.1:3000/?a=1')
    {'username': None, 'password': None, 'family': 2, 'fragment': None,
    'authority': u'127.0.0.1:3000', 'host': u'127.0.0.1', 'query': u'a=1',
    'path': u'/', 'scheme': u'http', 'port': 3000}
    """
    url_text = unicode(url_text)
    # raise TypeError('parse_url expected text, not %r' % url_str)
    um = _URL_RE.match(url_text)
    try:
        gs = um.groupdict()
    except AttributeError:
        raise ValueError('could not parse url: %r' % url_text)

    au_text = gs['authority']

    userinfo, sep, hostinfo = au_text.partition('@')
    if sep:
         # TODO: empty userinfo?
        user, _, pw = userinfo.partition(':')
    else:
        user, pw, hostinfo = None, None, au_text

    host, sep, port_str = au_text.rpartition(u':')
    if sep:
        if u']' in port_str:
            host = hostinfo  # wrong split, was an ipv6
        try:
            port = int(port_str)
        except ValueError:
            if not port_str:
                raise URLError('port must not be empty')  # TODO: excessive?
            raise URLError('expected integer for port, not %r)' % port_str)
    else:
        port = None

    family, host = parse_host(host)

    gs['username'] = user
    gs['password'] = pw
    gs['family'] = family
    gs['host'] = host
    gs['port'] = port
    return gs
