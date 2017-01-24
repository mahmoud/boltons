# -*- coding: utf-8 -*-
import re
import socket
import string

try:
    unicode, str, bytes, basestring = unicode, str, str, basestring
except NameError:  # basestring not defined in Python 3
    unicode, str, bytes, basestring = str, bytes, bytes, (str, bytes)


"""TODO:

- url.path_params (semicolon separated) http://www.w3.org/TR/REC-html40/appendix/notes.html#h-B.2.2
- support python compiled without IPv6
- support empty port (e.g., http://gweb.com:/)

The URL class isn't really for validation at the moment, though it
aims to be standards-compliant and will only emit valid URLs.
"""

DEFAULT_ENCODING = 'utf8'

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

_ABS_PATH_RE = (r'(?P<path>[' + _PATH_CHARS + ']*)'
                r'(\?(?P<query>[' + _QUERY_CHARS + ']*))?'
                r'(#(?P<fragment>[' + _FRAG_CHARS + '])*)?')

_URL_RE_STRICT = re.compile(r'^(?:(?P<scheme>[' + _SCHEME_CHARS + ']+):)?'
                            r'(//(?P<authority>[' + _AUTH_CHARS + ']*))?'
                            + _ABS_PATH_RE)


_HEX_CHAR_MAP = dict([(a + b, chr(int(a + b, 16)))
                      for a in string.hexdigits for b in string.hexdigits])
_ASCII_RE = re.compile('([\x00-\x7f]+)')


def _make_quote_map(allowed_chars):
    ret = {}
    for i, c in zip(range(256), str(bytearray(range(256)))):
        ret[c] = c if c in allowed_chars else '%{0:02X}'.format(i)
    return ret


_PATH_QUOTE_MAP = _make_quote_map(_ALLOWED_CHARS - set('?#'))
_QUERY_ELEMENT_QUOTE_MAP = _make_quote_map(_ALLOWED_CHARS - set('#&='))


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
        self.func = func

    def __get__(self, obj, objtype=None):
        if obj is None:
            return self
        value = self.func(obj)
        setattr(obj, self.func.__name__, value)
        return value

    def __repr__(self):
        cn = self.__class__.__name__
        return '<%s func=%s>' % (cn, self.func)


def escape_path(text):
    try:
        bytestr = text.encode(DEFAULT_ENCODING)
    except UnicodeDecodeError:
        # DecodeError from an encode means we already had bytes
        bytestr = text
    except:
        raise ValueError('expected text, not %r' % text)
    return u''.join([_PATH_QUOTE_MAP[b] for b in bytestr])


def escape_query_element(text):
    try:
        bytestr = text.encode(DEFAULT_ENCODING)
    except UnicodeDecodeError:
        # DecodeError from an encode means we already had bytes
        bytestr = text
    except:
        raise ValueError('expected text, not %r' % text)
    return u''.join([_QUERY_ELEMENT_QUOTE_MAP[b] for b in bytestr])


def parse_authority(au_str):  # TODO: namedtuple?
    user, pw, hostinfo = parse_userinfo(au_str)
    family, host, port = parse_hostinfo(hostinfo)
    return user, pw, family, host, port


def parse_hostinfo(au_str):
    """\
    returns:
      family (socket constant or None), host (string), port (int or None)

    >>> parse_hostinfo('googlewebsite.com:443')
    (None, 'googlewebsite.com', 443)
    >>> parse_hostinfo('[::1]:22')
    (10, '::1', 22)
    >>> parse_hostinfo('192.168.1.1:5000')
    (2, '192.168.1.1', 5000)

    TODO: check validity of non-IP host before returning?
    TODO: exception types for parse exceptions
    """
    family, host, port = None, '', None
    if not au_str:
        return family, host, port
    if ':' in au_str:  # for port-explicit and IPv6 authorities
        host, _, port_str = au_str.rpartition(':')
        if port_str and ']' not in port_str:
            try:
                port = int(port_str)
            except ValueError:
                raise ValueError('invalid authority in URL %r expected int'
                                 ' for port, not %r)' % (au_str, port_str))
        else:
            host, port = au_str, None
        if host and '[' == host[0] and ']' == host[-1]:
            host = host[1:-1]
            try:
                socket.inet_pton(socket.AF_INET6, host)
            except socket.error:
                raise ValueError('invalid IPv6 host: %r' % host)
            else:
                family = socket.AF_INET6
                return family, host, port
    try:
        socket.inet_pton(socket.AF_INET, host)
    except socket.error:
        host = host if (host or port) else au_str
    else:
        family = socket.AF_INET
    return family, host, port


def parse_userinfo(au_str):
    userinfo, _, hostinfo = au_str.partition('@')
    if hostinfo:
        username, _, password = userinfo.partition(':')
    else:
        username, password, hostinfo = None, None, au_str
    return username, password, hostinfo


def parse_url(url_str, encoding=DEFAULT_ENCODING, strict=False):
    if isinstance(url_str, str):
        url_str = url_str.decode(encoding)
    else:
        url_str = unicode(url_str)
    #raise TypeError('parse_url expected unicode or bytes, not %r' % url_str)
    um = (_URL_RE_STRICT if strict else _URL_RE).match(url_str)
    try:
        gs = um.groupdict()
    except AttributeError:
        raise ValueError('could not parse url: %r' % url_str)
    if gs['authority']:
        try:
            gs['authority'] = gs['authority'].decode('idna')
        except:
            pass
    else:
        gs['authority'] = ''
    user, pw, family, host, port = parse_authority(gs['authority'])
    gs['username'] = user
    gs['password'] = pw
    gs['family'] = family
    gs['host'] = host
    gs['port'] = port
    return gs


class URLError(ValueError):
    pass


class URL(object):
    # TODO: removed bytestring helper, so may need to figure something
    # else out for __bytes__/__str__

    # XXX encoded query strings and paths have an encoding behind the
    # percent-escaping, and we assume that it is utf8 here. how bad is
    # that really? should urls keep track of input encoding and be
    # able to reserialize back out to latin-1 percent encoded urls?

    _attrs = ('scheme', 'username', 'password', 'family',
              'host', 'port', 'path', 'query', 'fragment')
    _quotable_attrs = ('username', 'password', 'path', 'query')  # fragment?

    def __init__(self, url_str=None, strict=False):
        url_dict = {}
        if url_str:
            if isinstance(url_str, URL):
                url_str = url_str.to_text()  # better way to copy URLs?
            elif isinstance(url_str, bytes):
                try:
                    url_str = url_str.decode(DEFAULT_ENCODING)
                except UnicodeDecodeError as ude:
                    raise URLError('expected text or %s-encoded bytes.'
                                   ' try decoding the url bytes and passing in'
                                   ' the result. (got: %s)'
                                   % (DEFAULT_ENCODING, ude))
            url_dict = parse_url(url_str, strict=strict)

        _d = unicode()
        self.path_params = _d  # TODO: support parsing path params?
        for attr in self._attrs:
            val = url_dict.get(attr, _d) or _d
            if attr in self._quotable_attrs and '%' in val:
                val = unquote(val)
            setattr(self, attr, val)

    @cachedproperty
    def query_params(self):
        return QueryParamDict.from_string(self.query)

    q = query_params  # handy alias?

    @property
    def is_absolute(self):
        return bool(self.scheme)  # RFC2396 3.1

    @property
    def http_request_url(self):  # TODO: name
        parts = [escape_path(self.path)]
        query_string = self.get_query_string()
        if query_string:
            parts.append(query_string)
        return '?'.join(parts)

    @property
    def http_request_host(self):  # TODO: name
        ret = []
        host = self.host.encode('idna')
        if self.family == socket.AF_INET6:
            ret.extend(['[', host, ']'])
        else:
            ret.append(host)
        if self.port:
            ret.extend([':', unicode(self.port)])
        return ''.join(ret)

    def __iter__(self):
        s = self
        return iter((s.scheme, s.get_authority(idna=True), s.path,
                     s.path_params, s.get_query_string(),
                     s.fragment))

    # TODO: normalize?

    def get_query_string(self):
        return self.query_params.to_text()

    def get_authority(self, idna=True):
        parts = []
        _add = parts.append
        if self.username:
            _add(self.username)
            if self.password:
                _add(':')
                _add(self.password)
            _add('@')
        if self.host:
            if self.family == socket.AF_INET6:
                _add('[')
                _add(self.host)
                _add(']')
            elif idna:
                _add(self.host.encode('idna'))
            else:
                _add(self.host)
            if self.port:
                _add(':')
                _add(unicode(self.port))
        return u''.join(parts)

    def to_text(self, display=False):
        """\
        This method takes the place of urlparse.urlunparse/urlunsplit.
        It's a tricky business.
        """
        full_encode = (not display)
        scheme, path, params = self.scheme, self.path, self.path_params
        authority = self.get_authority(idna=full_encode)
        query_string = self.get_query_string()
        fragment = self.fragment

        parts = []
        _add = parts.append
        if scheme:
            _add(scheme)
            _add(':')
        if authority:
            _add('//')
            _add(authority)
        elif (scheme and path[:2] != '//'):
            _add('//')
        if path:
            if parts and path[:1] != '/':
                _add('/')
            _add(escape_path(path))
        if params:
            _add(';')
            _add(params)
        if query_string:
            _add('?')
            _add(query_string)
        if fragment:
            _add('#')
            _add(fragment)
        return u''.join(parts)

    def __repr__(self):
        return '%s(%r)' % (self.__class__.__name__, self.to_text())

    def __eq__(self, other):
        for attr in self._attrs:
            if not getattr(self, attr) == getattr(other, attr, None):
                return False
        return True

    def __ne__(self, other):
        return not self == other


def unquote(s, encoding=DEFAULT_ENCODING):
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


def parse_qsl(qs, keep_blank_values=True, encoding=DEFAULT_ENCODING):
    pairs = [s2 for s1 in qs.split('&') for s2 in s1.split(';')]
    ret = []
    for pair in pairs:
        if not pair:
            continue
        key, _, value = pair.partition('=')
        if not value:
            if keep_blank_values:
                value = ''
            else:
                continue
        if value or keep_blank_values:
            # TODO: really always convert plus signs to spaces?
            key = unquote(key.replace('+', ' '))
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


__all__ = ['MultiDict', 'OMD', 'OrderedMultiDict']


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
    # TODO: self.update_extend_from_string()?

    @classmethod
    def from_string(cls, query_string):
        pairs = parse_qsl(query_string, keep_blank_values=True)
        return cls(pairs)

    def to_text(self):
        ret_list = []
        for k, v in self.iteritems(multi=True):
            key = escape_query_element(to_unicode(k))
            val = escape_query_element(to_unicode(v))
            ret_list.append(u'='.join((key, val)))
        return u'&'.join(ret_list)


def to_unicode(obj):
    try:
        return unicode(obj)
    except UnicodeDecodeError:
        return unicode(obj, encoding=DEFAULT_ENCODING)


# end urlutils.py
