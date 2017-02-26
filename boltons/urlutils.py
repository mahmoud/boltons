# -*- coding: utf-8 -*-
"""
TODO: docs
"""

import re
import socket
import string
from unicodedata import normalize

unicode = type(u'')
try:
    unichr
except NameError:
    unichr = chr

# The unreserved URI characters (per RFC 3986)
_UNRESERVED_CHARS = frozenset('~-._0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ'
                              'abcdefghijklmnopqrstuvwxyz')

# URL parsing regex (per RFC 3986)
_URL_RE = re.compile(r'^((?P<scheme>[^:/?#]+):)?'
                     r'((?P<_uses_netloc>//)(?P<authority>[^/?#]*))?'
                     r'(?P<path_parts>[^?#]*)'
                     r'(\?(?P<_query>[^#]*))?'
                     r'(#(?P<fragment>.*))?')


_HEX_CHAR_MAP = dict([((a + b).encode('ascii'),
                       unichr(int(a + b, 16)).encode('charmap'))
                      for a in string.hexdigits for b in string.hexdigits])
_ASCII_RE = re.compile('([\x00-\x7f]+)')


# RFC 3986 section 2.2, Reserved Characters
_GEN_DELIMS = frozenset(u':/?#[]@')
_SUB_DELIMS = frozenset(u"!$&'()*+,;=")
_ALL_DELIMS = _GEN_DELIMS | _SUB_DELIMS

_USERINFO_SAFE = _UNRESERVED_CHARS | _SUB_DELIMS
_PATH_SAFE = _UNRESERVED_CHARS | _SUB_DELIMS | set(u':@')
_FRAGMENT_SAFE = _UNRESERVED_CHARS | _PATH_SAFE | set(u'/?')
_QUERY_SAFE = _UNRESERVED_CHARS | _FRAGMENT_SAFE - set(u'&=+')

NETLOC_SCHEMES = ['ftp', 'http', 'gopher', 'nntp', 'telnet',
                  'imap', 'wais', 'file', 'mms', 'https', 'shttp',
                  'snews', 'prospero', 'rtsp', 'rtspu', 'rsync', '',
                  'svn', 'svn+ssh', 'sftp', 'nfs', 'git', 'git+ssh']
NO_NETLOC_SCHEMES = ['urn', 'tel', 'news', 'mailto', 'magnet']  # TODO: others?

DEFAULT_PORT_MAP = {'http': 80, 'https': 443}

DEFAULT_ENCODING = 'utf8'


def to_unicode(obj):
    try:
        return unicode(obj)
    except UnicodeDecodeError:
        return unicode(obj, encoding=DEFAULT_ENCODING)


class URLParseError(ValueError):
    pass


# regex from gruber via tornado
# doesn't support ipv6 or mailto (netloc-less schemes)
_FIND_ALL_URL_RE = re.compile(to_unicode(r"""\b((?:([\w-]+):(/{1,3})|www[.])(?:(?:(?:[^\s&()<>]|&amp;|&quot;)*(?:[^!"#$%'()*+,.:;<=>?@\[\]^`{|}~\s]))|(?:\((?:[^\s&()]|&amp;|&quot;)*\)))+)"""))


def find_all_links(text, with_text=False,
                   require_scheme=False, default_scheme='http', schemes=()):
    """
    Heuristic-based link finder.
    """
    text = to_unicode(text)
    prev_end, start, end = 0, None, None
    ret = []
    _add = ret.append

    def _add_text(t):
        if ret and isinstance(ret[-1], unicode):
            ret[-1] += t
        else:
            _add(t)

    for match in _FIND_ALL_URL_RE.finditer(text):
        start, end = match.start(1), match.end(1)
        if prev_end < start and with_text:
            _add(text[prev_end:start])
        prev_end = end
        try:
            cur_url_text = match.group(0)
            cur_url = URL(cur_url_text)
            if not cur_url.scheme:
                if require_scheme:
                    _add_text(text[start:end])
                else:
                    cur_url = URL(default_scheme + '://' + cur_url_text)
            if schemes and cur_url.scheme not in schemes:
                _add_text(text[start:end])
            else:
                _add(cur_url)
        except URLParseError:
            # currently this should only be hit with broken port
            # strings. the regex above doesn't support ipv6 addresses
            if with_text:
                _add_text(text[start:end])

    if with_text:
        tail = text[prev_end:]
        if tail:
            _add_text(tail)

    return ret


def _make_quote_map(safe_chars):
    ret = {}
    # v is included in the dict for py3 mostly, because bytestrings
    # are iterables of ints, of course!
    for i, v in zip(range(256), range(256)):
        c = chr(v)
        if c in safe_chars:
            ret[c] = ret[v] = c
        else:
            ret[c] = ret[v] = '%{0:02X}'.format(i)
    return ret


_USERINFO_PART_QUOTE_MAP = _make_quote_map(_USERINFO_SAFE)
_PATH_PART_QUOTE_MAP = _make_quote_map(_PATH_SAFE)
_QUERY_PART_QUOTE_MAP = _make_quote_map(_QUERY_SAFE)
_FRAGMENT_QUOTE_MAP = _make_quote_map(_FRAGMENT_SAFE)


def quote_path_part(text, full_quote=True):
    # TODO: why does one route allow percents through and not the
    # other?
    if not full_quote:
        return u''.join([_PATH_PART_QUOTE_MAP.get(t, t) for t in text])

    bytestr = normalize('NFC', to_unicode(text)).encode('utf8')
    return u''.join([_PATH_PART_QUOTE_MAP[b] for b in bytestr])


def quote_query_part(text, full_quote=True):
    if not full_quote:
        return u''.join([_QUERY_PART_QUOTE_MAP.get(t, t) for t in text])

    bytestr = normalize('NFC', to_unicode(text)).encode('utf8')
    return u''.join([_QUERY_PART_QUOTE_MAP[b] for b in bytestr])


# fragments don't really have parts, there are no official
# subdelimiters within fragments, I believe
def quote_fragment_part(text, full_quote=True):
    if not full_quote:
        return u''.join([_FRAGMENT_QUOTE_MAP.get(t, t) for t in text])

    bytestr = normalize('NFC', to_unicode(text)).encode('utf8')
    return u''.join([_FRAGMENT_QUOTE_MAP[b] for b in bytestr])


def quote_userinfo_part(text, full_quote=True):
    if not full_quote:
        return u''.join([_USERINFO_PART_QUOTE_MAP.get(t, t) for t in text])

    bytestr = normalize('NFC', to_unicode(text)).encode('utf8')
    return u''.join([_USERINFO_PART_QUOTE_MAP[b] for b in bytestr])


def unquote(string, encoding='utf-8', errors='replace'):
    """Replace %xx escapes by their single-character equivalent. The optional
    encoding and errors parameters specify how to decode percent-encoded
    sequences into Unicode characters, as accepted by the bytes.decode()
    method.
    By default, percent-encoded sequences are decoded with UTF-8, and invalid
    sequences are replaced by a placeholder character.

    unquote('abc%20def') -> 'abc def'.
    """
    if '%' not in string:
        string.split
        return string
    if encoding is None:
        encoding = 'utf-8'
    if errors is None:
        errors = 'replace'
    bits = _ASCII_RE.split(string)
    res = [bits[0]]
    append = res.append
    for i in range(1, len(bits), 2):
        append(unquote_to_bytes(bits[i]).decode(encoding, errors))
        append(bits[i + 1])
    return ''.join(res)


def unquote_to_bytes(string):
    """unquote_to_bytes('abc%20def') -> b'abc def'."""
    # Note: strings are encoded as UTF-8. This is only an issue if it contains
    # unescaped non-ASCII characters, which URIs should not.
    if not string:
        # Is it a string-like object?
        string.split
        return b''
    if isinstance(string, unicode):
        string = string.encode('utf-8')
    bits = string.split(b'%')
    if len(bits) == 1:
        return string
    # import pdb;pdb.set_trace()
    res = [bits[0]]
    append = res.append

    for item in bits[1:]:
        try:
            append(_HEX_CHAR_MAP[item[:2]])
            append(item[2:])
        except KeyError:
            append(b'%')
            append(item)
    return b''.join(res)


def register_scheme(text, uses_netloc=None, default_port=None):
    """Registers new scheme information, resulting in correct port and
    slash behavior from the URL object.
    """
    text = text.lower()
    if default_port is not None:
        try:
            default_port = int(default_port)
        except ValueError:
            raise ValueError('default_port expected integer or None, not %r'
                             % (default_port,))

    if uses_netloc is True:
        if text not in NETLOC_SCHEMES:
            NETLOC_SCHEMES.append(text)
    elif uses_netloc is False:
        if text not in NO_NETLOC_SCHEMES:
            NO_NETLOC_SCHEMES.append(text)
    elif uses_netloc is not None:
        raise ValueError('uses_netloc expected True, False, or None')

    DEFAULT_PORT_MAP[text] = default_port

    return


def resolve_path_parts(path_parts):
    """
    Normalize the URL path by resolving segments of '.' and '..'.
    See RFC 3986 section 5.2.4, Remove Dot Segments.
    """
    # TODO: what to do with multiple slashes
    ret = []

    for part in path_parts:
        if part == u'.':
            pass
        elif part == u'..':
            if ret and (len(ret) > 1 or ret[0]):  # prevent unrooting
                ret.pop()
        else:
            ret.append(part)

    if list(path_parts[-1:]) in ([u'.'], [u'..']):
        ret.append(u'')

    return ret


class cachedproperty(object):
    """The ``cachedproperty`` is used similar to :class:`property`, except
    that the wrapped method is only called once. This is commonly used
    to implement lazy attributes.

    After the property has been accessed, the value is stored on the
    instance itself, using the same name as the cachedproperty. This
    allows the cache to be cleared with :func:`delattr`, or through
    manipulating the object's ``__dict__``.
    """
    def __init__(self, func):
        self.__doc__ = getattr(func, '__doc__')
        self.func = func

    def __get__(self, obj, objtype=None):
        if obj is None:
            return self
        value = obj.__dict__[self.func.__name__] = self.func(obj)
        return value

    def __repr__(self):
        cn = self.__class__.__name__
        return '<%s func=%s>' % (cn, self.func)


class URL(object):

    _attrs = ('scheme', '_uses_netloc', 'username', 'password', 'family',
              'host', 'port', 'path_parts', '_query', 'fragment')

    def __init__(self, url=''):
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
                    raise URLParseError('expected text or %s-encoded bytes.'
                                        ' try decoding the url bytes and'
                                        ' passing the result. (got: %s)'
                                        % (DEFAULT_ENCODING, ude))
            url_dict = parse_url(url)

        _d = unicode()
        for attr in self._attrs:
            # TODO: possibly use None as marker for empty vs missing
            val = url_dict.get(attr, _d) or _d
            if attr == 'path_parts':
                val = tuple([unquote(p) if '%' in p else p
                             for p in val.split(u'/')])
            elif attr in ('username', 'password', 'fragment') and '%' in val:
                val = unquote(val)
            elif attr == 'host' and val:
                try:
                    val = val.encode("ascii")
                except UnicodeEncodeError:
                    pass  # already non-ascii text
                else:
                    val = val.decode("idna")
            setattr(self, attr, val)
        return

    @classmethod
    def from_parts(cls, scheme=None, host=None, path_parts=(), query_params=(),
                   fragment=u'', port=None, username=None, password=None):
        """
        Build a new URL from parts.
        """
        ret = cls()

        ret.scheme = scheme
        ret.host = host
        ret.path_parts = tuple(path_parts) or (u'',)
        ret.query_params.update(query_params)
        ret.fragment = fragment
        ret.port = port
        ret.username = username
        ret.password = password

        return ret

    @cachedproperty
    def query_params(self):
        return QueryParamDict.from_text(self._query)

    qp = query_params

    @property
    def path(self):
        return u'/'.join([quote_path_part(p, full_quote=False)
                          for p in self.path_parts])

    @path.setter
    def path(self, path_text):
        self.path_parts = tuple([unquote(p) if '%' in p else p
                                 for p in to_unicode(path_text).split(u'/')])
        return

    @property
    def uses_netloc(self):
        default = self._uses_netloc
        if self.scheme in NETLOC_SCHEMES:
            return True
        if self.scheme in NO_NETLOC_SCHEMES:
            return False
        if self.scheme.split('+')[-1] in NETLOC_SCHEMES:
            return True
        return default

    @property
    def default_port(self):
        try:
            return DEFAULT_PORT_MAP[self.scheme]
        except KeyError:
            return DEFAULT_PORT_MAP.get(self.scheme.split('+')[-1])

    def normalize(self, with_case=True):
        """Resolve any "." and ".." references in the path, as well as
        normalize scheme and host casing.

        More information can be found in Section 6.2.2 of RFC 3986.

        """
        self.path_parts = resolve_path_parts(self.path_parts)

        if with_case:
            self.scheme = self.scheme.lower()
            self.host = self.host.lower()
        return

    def navigate(self, dest):
        """Factory method that returns a _new_ URL based on a given
        destination, *dest*.
        """
        orig_dest = None
        if not isinstance(dest, URL):
            dest, orig_dest = URL(dest), dest
        if dest.scheme and dest.host:
            # absolute URLs replace everything, but don't make an
            # extra copy if we don't have to
            return URL(dest) if orig_dest is None else dest
        query_params = dest.query_params

        if dest.path:
            if dest.path.startswith(u'/'):   # absolute path
                new_path_parts = list(dest.path_parts)
            else:  # relative path
                new_path_parts = self.path_parts[:-1] + dest.path_parts
        else:
            new_path_parts = list(self.path_parts)
            if not query_params:
                query_params = self.query_params

        ret = self.from_parts(scheme=dest.scheme or self.scheme,
                              host=dest.host or self.host,
                              port=dest.port or self.port,
                              path_parts=new_path_parts,
                              query_params=query_params,
                              fragment=dest.fragment,
                              username=dest.username or self.username,
                              password=dest.password or self.password)
        ret.normalize()
        return ret

    def get_authority(self, full_quote=True, with_userinfo=True):
        parts = []
        _add = parts.append
        if self.username and with_userinfo:
            _add(quote_userinfo_part(self.username))
            _add(':')
            if self.password:
                _add(quote_userinfo_part(self.password))
            _add('@')
        if self.host:
            if self.family == socket.AF_INET6:
                _add('[')
                _add(self.host)
                _add(']')
            elif full_quote:
                _add(self.host.encode('idna').decode('ascii'))
            else:
                _add(self.host)
            # TODO: 0 port?
            if self.port and self.port != self.default_port:
                _add(':')
                _add(unicode(self.port))
        return u''.join(parts)

    def to_text(self, full_quote=False):
        scheme = self.scheme
        path = u'/'.join([quote_path_part(p, full_quote=full_quote)
                          for p in self.path_parts])
        authority = self.get_authority(full_quote=full_quote)
        query_string = self.query_params.to_text(full_quote=full_quote)
        fragment = quote_fragment_part(self.fragment, full_quote=full_quote)

        parts = []
        _add = parts.append
        if scheme:
            _add(scheme)
            _add(':')
        if authority:
            _add('//')
            _add(authority)
        elif (scheme and path[:2] != '//' and self.uses_netloc):
            _add('//')
        if path:
            if scheme and authority and path[:1] != '/':
                _add('/')
                # TODO: i think this is here because relative paths
                # with absolute authorities = undefined
            _add(path)
        if query_string:
            _add('?')
            _add(query_string)
        if fragment:
            _add('#')
            _add(fragment)
        return u''.join(parts)

    def __repr__(self):
        cn = self.__class__.__name__
        return u'%s(%r)' % (cn, self.to_text())

    def __eq__(self, other):
        for attr in self._attrs:
            if not getattr(self, attr) == getattr(other, attr, None):
                return False
        return True

    def __ne__(self, other):
        return not self == other


try:
    from socket import inet_pton
except ImportError:
    # from https://gist.github.com/nnemkin/4966028
    import ctypes

    class _sockaddr(ctypes.Structure):
        _fields_ = [("sa_family", ctypes.c_short),
                    ("__pad1", ctypes.c_ushort),
                    ("ipv4_addr", ctypes.c_byte * 4),
                    ("ipv6_addr", ctypes.c_byte * 16),
                    ("__pad2", ctypes.c_ulong)]

    WSAStringToAddressA = ctypes.windll.ws2_32.WSAStringToAddressA
    WSAAddressToStringA = ctypes.windll.ws2_32.WSAAddressToStringA

    def inet_pton(address_family, ip_string):
        addr = _sockaddr()
        ip_string = ip_string.encode('ascii')  # TODO
        addr.sa_family = address_family
        addr_size = ctypes.c_int(ctypes.sizeof(addr))

        if WSAStringToAddressA(ip_string, address_family, None, ctypes.byref(addr), ctypes.byref(addr_size)) != 0:
            raise socket.error(ctypes.FormatError())

        if address_family == socket.AF_INET:
            return ctypes.string_at(addr.ipv4_addr, 4)
        if address_family == socket.AF_INET6:
            return ctypes.string_at(addr.ipv6_addr, 16)
        raise socket.error('unknown address family')


def parse_host(host):
    """\
    returns:
      family (socket constant or None), host (string)

    >>> parse_host('googlewebsite.com') == (None, 'googlewebsite.com')
    True
    >>> parse_host('[::1]') == (socket.AF_INET6, '::1')
    True
    >>> parse_host('192.168.1.1') == (socket.AF_INET, '192.168.1.1')
    True

    (odd doctest formatting above due to py3's switch from int to enums
    for socket constants)
    """
    if not host:
        return None, u''
    if u':' in host and u'[' == host[0] and u']' == host[-1]:
        host = host[1:-1]
        try:
            inet_pton(socket.AF_INET6, host)
        except socket.error as se:
            raise URLParseError('invalid IPv6 host: %r (%r)' % (host, se))
        except UnicodeEncodeError:
            pass  # TODO: this can't be a real host right?
        else:
            family = socket.AF_INET6
            return family, host
    try:
        inet_pton(socket.AF_INET, host)
    except (socket.error, UnicodeEncodeError):
        family = None  # not an IP
    else:
        family = socket.AF_INET
    return family, host


def parse_url(url_text):
    url_text = unicode(url_text)
    # raise TypeError('parse_url expected text, not %r' % url_str)
    um = _URL_RE.match(url_text)
    try:
        gs = um.groupdict()
    except AttributeError:
        raise URLParseError('could not parse url: %r' % url_text)

    au_text = gs['authority']
    user, pw, hostinfo = None, None, au_text

    if au_text:
        userinfo, sep, hostinfo = au_text.rpartition('@')
        if sep:
            # TODO: empty userinfo error?
            user, _, pw = userinfo.partition(':')

    host, port = None, None
    if hostinfo:
        host, sep, port_str = hostinfo.partition(u':')
        if sep:
            if u']' in port_str:
                host = hostinfo  # wrong split, was an ipv6
            else:
                try:
                    port = int(port_str)
                except ValueError:
                    if port_str:  # empty ports ok according to RFC 3986 6.2.3
                        raise URLParseError('expected integer for port, not %r'
                                            % port_str)
                    port = None

    family, host = parse_host(host)

    gs['username'] = user
    gs['password'] = pw
    gs['family'] = family
    gs['host'] = host
    gs['port'] = port
    return gs


def parse_qsl(qs, keep_blank_values=True, encoding=DEFAULT_ENCODING):
    pairs = [s2 for s1 in qs.split('&') for s2 in s1.split(';')]
    ret = []
    for pair in pairs:
        if not pair:
            continue
        key, _, value = pair.partition('=')
        if not value:
            if keep_blank_values:
                value = None
            else:
                continue
        key = unquote(key.replace('+', ' '))
        if value:
            value = unquote(value.replace('+', ' '))
        ret.append((key, value))
    return ret


"""
# What follows is the OrderedMultiDict from dictutils.py, circa
# 20161021, used for the QueryParamDict, toward the bottom.
"""

from collections import KeysView, ValuesView, ItemsView

try:
    from itertools import izip_longest
except ImportError:
    from itertools import zip_longest as izip_longest

try:
    from typeutils import make_sentinel
    _MISSING = make_sentinel(var_name='_MISSING')
except ImportError:
    _MISSING = object()


PREV, NEXT, KEY, VALUE, SPREV, SNEXT = range(6)


class OrderedMultiDict(dict):
    """A MultiDict is a dictionary that can have multiple values per key
    and the OrderedMultiDict (OMD) is a MultiDict that retains
    original insertion order. Common use cases include:

      * handling query strings parsed from URLs
      * inverting a dictionary to create a reverse index (values to keys)
      * stacking data from multiple dictionaries in a non-destructive way

    The OrderedMultiDict constructor is identical to the built-in
    :class:`dict`, and overall the API is constitutes an intuitive
    superset of the built-in type:

    >>> omd = OrderedMultiDict()
    >>> omd['a'] = 1
    >>> omd['b'] = 2
    >>> omd.add('a', 3)
    >>> omd.get('a')
    3
    >>> omd.getlist('a')
    [1, 3]

    Some non-:class:`dict`-like behaviors also make an appearance,
    such as support for :func:`reversed`:

    >>> list(reversed(omd))
    ['b', 'a']

    Note that unlike some other MultiDicts, this OMD gives precedence
    to the most recent value added. ``omd['a']`` refers to ``3``, not
    ``1``.

    >>> omd
    OrderedMultiDict([('a', 1), ('b', 2), ('a', 3)])
    >>> omd.poplast('a')
    3
    >>> omd
    OrderedMultiDict([('a', 1), ('b', 2)])
    >>> omd.pop('a')
    1
    >>> omd
    OrderedMultiDict([('b', 2)])

    Note that calling :func:`dict` on an OMD results in a dict of keys
    to *lists* of values:

    >>> from pprint import pprint as pp  # ensuring proper key ordering
    >>> omd = OrderedMultiDict([('a', 1), ('b', 2), ('a', 3)])
    >>> pp(dict(omd))
    {'a': [1, 3], 'b': [2]}

    Note that modifying those lists will modify the OMD. If you want a
    safe-to-modify or flat dictionary, use :meth:`OrderedMultiDict.todict()`.

    >>> pp(omd.todict())
    {'a': 3, 'b': 2}
    >>> pp(omd.todict(multi=True))
    {'a': [1, 3], 'b': [2]}

    With ``multi=False``, items appear with the keys in to original
    insertion order, alongside the most-recently inserted value for
    that key.

    >>> OrderedMultiDict([('a', 1), ('b', 2), ('a', 3)]).items(multi=False)
    [('a', 3), ('b', 2)]

    """
    def __init__(self, *args, **kwargs):
        if len(args) > 1:
            raise TypeError('%s expected at most 1 argument, got %s'
                            % (self.__class__.__name__, len(args)))
        super(OrderedMultiDict, self).__init__()

        self._clear_ll()
        if args:
            self.update_extend(args[0])
        if kwargs:
            self.update(kwargs)

    def _clear_ll(self):
        try:
            _map = self._map
        except AttributeError:
            _map = self._map = {}
            self.root = []
        _map.clear()
        self.root[:] = [self.root, self.root, None]

    def _insert(self, k, v):
        root = self.root
        cells = self._map.setdefault(k, [])
        last = root[PREV]
        cell = [last, root, k, v]
        last[NEXT] = root[PREV] = cell
        cells.append(cell)

    def add(self, k, v):
        """Add a single value *v* under a key *k*. Existing values under *k*
        are preserved.
        """
        values = super(OrderedMultiDict, self).setdefault(k, [])
        self._insert(k, v)
        values.append(v)

    def addlist(self, k, v):
        """Add an iterable of values underneath a specific key, preserving
        any values already under that key.

        >>> omd = OrderedMultiDict([('a', -1)])
        >>> omd.addlist('a', range(3))
        >>> omd
        OrderedMultiDict([('a', -1), ('a', 0), ('a', 1), ('a', 2)])

        Called ``addlist`` for consistency with :meth:`getlist`, but
        tuples and other sequences and iterables work.
        """
        self_insert = self._insert
        values = super(OrderedMultiDict, self).setdefault(k, [])
        for subv in v:
            self_insert(k, subv)
        values.extend(v)

    def get(self, k, default=None):
        """Return the value for key *k* if present in the dictionary, else
        *default*. If *default* is not given, ``None`` is returned.
        This method never raises a :exc:`KeyError`.

        To get all values under a key, use :meth:`OrderedMultiDict.getlist`.
        """
        return super(OrderedMultiDict, self).get(k, [default])[-1]

    def getlist(self, k, default=_MISSING):
        """Get all values for key *k* as a list, if *k* is in the
        dictionary, else *default*. The list returned is a copy and
        can be safely mutated. If *default* is not given, an empty
        :class:`list` is returned.
        """
        try:
            return super(OrderedMultiDict, self).__getitem__(k)[:]
        except KeyError:
            if default is _MISSING:
                return []
            return default

    def clear(self):
        "Empty the dictionary."
        super(OrderedMultiDict, self).clear()
        self._clear_ll()

    def setdefault(self, k, default=_MISSING):
        """If key *k* is in the dictionary, return its value. If not, insert
        *k* with a value of *default* and return *default*. *default*
        defaults to ``None``. See :meth:`dict.setdefault` for more
        information.
        """
        if not super(OrderedMultiDict, self).__contains__(k):
            self[k] = None if default is _MISSING else default
        return self[k]

    def copy(self):
        "Return a shallow copy of the dictionary."
        return self.__class__(self.iteritems(multi=True))

    @classmethod
    def fromkeys(cls, keys, default=None):
        """Create a dictionary from a list of keys, with all the values
        set to *default*, or ``None`` if *default* is not set.
        """
        return cls([(k, default) for k in keys])

    def update(self, E, **F):
        """Add items from a dictionary or iterable (and/or keyword arguments),
        overwriting values under an existing key. See
        :meth:`dict.update` for more details.
        """
        # E and F are throwback names to the dict() __doc__
        if E is self:
            return
        self_add = self.add
        if isinstance(E, OrderedMultiDict):
            for k in E:
                if k in self:
                    del self[k]
            for k, v in E.iteritems(multi=True):
                self_add(k, v)
        elif hasattr(E, 'keys'):
            for k in E.keys():
                self[k] = E[k]
        else:
            seen = set()
            seen_add = seen.add
            for k, v in E:
                if k not in seen and k in self:
                    del self[k]
                    seen_add(k)
                self_add(k, v)
        for k in F:
            self[k] = F[k]
        return

    def update_extend(self, E, **F):
        """Add items from a dictionary, iterable, and/or keyword
        arguments without overwriting existing items present in the
        dictionary. Like :meth:`update`, but adds to existing keys
        instead of overwriting them.
        """
        if E is self:
            iterator = iter(E.items())
        elif isinstance(E, OrderedMultiDict):
            iterator = E.iteritems(multi=True)
        elif hasattr(E, 'keys'):
            iterator = ((k, E[k]) for k in E.keys())
        else:
            iterator = E

        self_add = self.add
        for k, v in iterator:
            self_add(k, v)

    def __setitem__(self, k, v):
        if super(OrderedMultiDict, self).__contains__(k):
            self._remove_all(k)
        self._insert(k, v)
        super(OrderedMultiDict, self).__setitem__(k, [v])

    def __getitem__(self, k):
        return super(OrderedMultiDict, self).__getitem__(k)[-1]

    def __delitem__(self, k):
        super(OrderedMultiDict, self).__delitem__(k)
        self._remove_all(k)

    def __eq__(self, other):
        if self is other:
            return True
        try:
            if len(other) != len(self):
                return False
        except TypeError:
            return False
        if isinstance(other, OrderedMultiDict):
            selfi = self.iteritems(multi=True)
            otheri = other.iteritems(multi=True)
            zipped_items = izip_longest(selfi, otheri, fillvalue=(None, None))
            for (selfk, selfv), (otherk, otherv) in zipped_items:
                if selfk != otherk or selfv != otherv:
                    return False
            if not(next(selfi, _MISSING) is _MISSING
                   and next(otheri, _MISSING) is _MISSING):
                # leftovers  (TODO: watch for StopIteration?)
                return False
            return True
        elif hasattr(other, 'keys'):
            for selfk in self:
                try:
                    other[selfk] == self[selfk]
                except KeyError:
                    return False
            return True
        return False

    def __ne__(self, other):
        return not (self == other)

    def pop(self, k, default=_MISSING):
        """Remove all values under key *k*, returning the most-recently
        inserted value. Raises :exc:`KeyError` if the key is not
        present and no *default* is provided.
        """
        try:
            return self.popall(k)[-1]
        except KeyError:
            if default is _MISSING:
                raise KeyError(k)
        return default

    def popall(self, k, default=_MISSING):
        """Remove all values under key *k*, returning them in the form of
        a list. Raises :exc:`KeyError` if the key is not present and no
        *default* is provided.
        """
        super_self = super(OrderedMultiDict, self)
        if super_self.__contains__(k):
            self._remove_all(k)
        if default is _MISSING:
            return super_self.pop(k)
        return super_self.pop(k, default)

    def poplast(self, k=_MISSING, default=_MISSING):
        """Remove and return the most-recently inserted value under the key
        *k*, or the most-recently inserted key if *k* is not
        provided. If no values remain under *k*, it will be removed
        from the OMD.  Raises :exc:`KeyError` if *k* is not present in
        the dictionary, or the dictionary is empty.
        """
        if k is _MISSING:
            if self:
                k = self.root[PREV][KEY]
            else:
                raise KeyError('empty %r' % type(self))
        try:
            self._remove(k)
        except KeyError:
            if default is _MISSING:
                raise KeyError(k)
            return default
        values = super(OrderedMultiDict, self).__getitem__(k)
        v = values.pop()
        if not values:
            super(OrderedMultiDict, self).__delitem__(k)
        return v

    def _remove(self, k):
        values = self._map[k]
        cell = values.pop()
        cell[PREV][NEXT], cell[NEXT][PREV] = cell[NEXT], cell[PREV]
        if not values:
            del self._map[k]

    def _remove_all(self, k):
        values = self._map[k]
        while values:
            cell = values.pop()
            cell[PREV][NEXT], cell[NEXT][PREV] = cell[NEXT], cell[PREV]
        del self._map[k]

    def iteritems(self, multi=False):
        """Iterate over the OMD's items in insertion order. By default,
        yields only the most-recently inserted value for each key. Set
        *multi* to ``True`` to get all inserted items.
        """
        root = self.root
        curr = root[NEXT]
        if multi:
            while curr is not root:
                yield curr[KEY], curr[VALUE]
                curr = curr[NEXT]
        else:
            for key in self.iterkeys():
                yield key, self[key]

    def iterkeys(self, multi=False):
        """Iterate over the OMD's keys in insertion order. By default, yields
        each key once, according to the most recent insertion. Set
        *multi* to ``True`` to get all keys, including duplicates, in
        insertion order.
        """
        root = self.root
        curr = root[NEXT]
        if multi:
            while curr is not root:
                yield curr[KEY]
                curr = curr[NEXT]
        else:
            yielded = set()
            yielded_add = yielded.add
            while curr is not root:
                k = curr[KEY]
                if k not in yielded:
                    yielded_add(k)
                    yield k
                curr = curr[NEXT]

    def itervalues(self, multi=False):
        """Iterate over the OMD's values in insertion order. By default,
        yields the most-recently inserted value per unique key.  Set
        *multi* to ``True`` to get all values according to insertion
        order.
        """
        for k, v in self.iteritems(multi=multi):
            yield v

    def todict(self, multi=False):
        """Gets a basic :class:`dict` of the items in this dictionary. Keys
        are the same as the OMD, values are the most recently inserted
        values for each key.

        Setting the *multi* arg to ``True`` is yields the same
        result as calling :class:`dict` on the OMD, except that all the
        value lists are copies that can be safely mutated.
        """
        if multi:
            return dict([(k, self.getlist(k)) for k in self])
        return dict([(k, self[k]) for k in self])

    def sorted(self, key=None, reverse=False):
        """Similar to the built-in :func:`sorted`, except this method returns
        a new :class:`OrderedMultiDict` sorted by the provided key
        function, optionally reversed.

        Args:
            key (callable): A callable to determine the sort key of
              each element. The callable should expect an **item**
              (key-value pair tuple).
            reverse (bool): Set to ``True`` to reverse the ordering.

        >>> omd = OrderedMultiDict(zip(range(3), range(3)))
        >>> omd.sorted(reverse=True)
        OrderedMultiDict([(2, 2), (1, 1), (0, 0)])

        Note that the key function receives an **item** (key-value
        tuple), so the recommended signature looks like:

        >>> omd = OrderedMultiDict(zip('hello', 'world'))
        >>> omd.sorted(key=lambda i: i[1])  # i[0] is the key, i[1] is the val
        OrderedMultiDict([('o', 'd'), ('l', 'l'), ('e', 'o'), ('h', 'w')])
        """
        cls = self.__class__
        return cls(sorted(self.iteritems(), key=key, reverse=reverse))

    def sortedvalues(self, key=None, reverse=False):
        """Returns a copy of the :class:`OrderedMultiDict` with the same keys
        in the same order as the original OMD, but the values within
        each keyspace have been sorted according to *key* and
        *reverse*.

        Args:
            key (callable): A single-argument callable to determine
              the sort key of each element. The callable should expect
              an **item** (key-value pair tuple).
            reverse (bool): Set to ``True`` to reverse the ordering.

        >>> omd = OrderedMultiDict()
        >>> omd.addlist('even', [6, 2])
        >>> omd.addlist('odd', [1, 5])
        >>> omd.add('even', 4)
        >>> omd.add('odd', 3)
        >>> somd = omd.sortedvalues()
        >>> somd.getlist('even')
        [2, 4, 6]
        >>> somd.keys(multi=True) == omd.keys(multi=True)
        True
        >>> omd == somd
        False
        >>> somd
        OrderedMultiDict([('even', 2), ('even', 4), ('odd', 1), ('odd', 3), ('even', 6), ('odd', 5)])

        As demonstrated above, contents and key order are
        retained. Only value order changes.
        """
        try:
            superself_iteritems = super(OrderedMultiDict, self).iteritems()
        except AttributeError:
            superself_iteritems = super(OrderedMultiDict, self).items()
        # (not reverse) because they pop off in reverse order for reinsertion
        sorted_val_map = dict([(k, sorted(v, key=key, reverse=(not reverse)))
                               for k, v in superself_iteritems])
        ret = self.__class__()
        for k in self.iterkeys(multi=True):
            ret.add(k, sorted_val_map[k].pop())
        return ret

    def inverted(self):
        """Returns a new :class:`OrderedMultiDict` with values and keys
        swapped, like creating dictionary transposition or reverse
        index.  Insertion order is retained and all keys and values
        are represented in the output.

        >>> omd = OMD([(0, 2), (1, 2)])
        >>> omd.inverted().getlist(2)
        [0, 1]

        Inverting twice yields a copy of the original:

        >>> omd.inverted().inverted()
        OrderedMultiDict([(0, 2), (1, 2)])
        """
        return self.__class__((v, k) for k, v in self.iteritems(multi=True))

    def counts(self):
        """Returns a mapping from key to number of values inserted under that
        key. Like :py:class:`collections.Counter`, but returns a new
        :class:`OrderedMultiDict`.
        """
        # Returns an OMD because Counter/OrderedDict may not be
        # available, and neither Counter nor dict maintain order.
        super_getitem = super(OrderedMultiDict, self).__getitem__
        return self.__class__((k, len(super_getitem(k))) for k in self)

    def keys(self, multi=False):
        """Returns a list containing the output of :meth:`iterkeys`.  See
        that method's docs for more details.
        """
        return list(self.iterkeys(multi=multi))

    def values(self, multi=False):
        """Returns a list containing the output of :meth:`itervalues`.  See
        that method's docs for more details.
        """
        return list(self.itervalues(multi=multi))

    def items(self, multi=False):
        """Returns a list containing the output of :meth:`iteritems`.  See
        that method's docs for more details.
        """
        return list(self.iteritems(multi=multi))

    def __iter__(self):
        return self.iterkeys()

    def __reversed__(self):
        root = self.root
        curr = root[PREV]
        lengths = {}
        lengths_sd = lengths.setdefault
        get_values = super(OrderedMultiDict, self).__getitem__
        while curr is not root:
            k = curr[KEY]
            vals = get_values(k)
            if lengths_sd(k, 1) == len(vals):
                yield k
            lengths[k] += 1
            curr = curr[PREV]

    def __repr__(self):
        cn = self.__class__.__name__
        kvs = ', '.join([repr((k, v)) for k, v in self.iteritems(multi=True)])
        return '%s([%s])' % (cn, kvs)

    def viewkeys(self):
        "OMD.viewkeys() -> a set-like object providing a view on OMD's keys"
        return KeysView(self)

    def viewvalues(self):
        "OMD.viewvalues() -> an object providing a view on OMD's values"
        return ValuesView(self)

    def viewitems(self):
        "OMD.viewitems() -> a set-like object providing a view on OMD's items"
        return ItemsView(self)


try:
    # try to import the built-in one anyways
    from boltons.dictutils import OrderedMultiDict
except ImportError:
    pass

OMD = OrderedMultiDict


class QueryParamDict(OrderedMultiDict):
    # TODO: caching
    # TODO: self.update_extend_from_text()?

    @classmethod
    def from_text(cls, query_string):
        pairs = parse_qsl(query_string, keep_blank_values=True)
        return cls(pairs)

    def to_text(self, full_quote=False):
        ret_list = []
        for k, v in self.iteritems(multi=True):
            key = quote_query_part(to_unicode(k), full_quote=full_quote)
            if v is None:
                ret_list.append(key)
            else:
                val = quote_query_part(to_unicode(v), full_quote=full_quote)
                ret_list.append(u'='.join((key, val)))
        return u'&'.join(ret_list)


# end urlutils.py
