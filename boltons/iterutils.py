# -*- coding: utf-8 -*-
""":mod:`itertools` is full of great examples of Python generator
usage. However, there are still some critical gaps. ``iterutils``
fills many of those gaps with featureful, tested, and Pythonic
solutions.

Many of the functions below have two versions, one which
returns an iterator (denoted by the ``*_iter`` naming pattern), and a
shorter-named convenience form that returns a list. Some of the
following are based on examples in itertools docs.
"""

__all__ = ['is_iterable', 'is_scalar', 'split', 'split_iter', 'chunked',
           'chunked_iter', 'windowed', 'windowed_iter', 'bucketize', 'partition',
           'unique', 'unique_iter', 'one']


import itertools

try:
    from itertools import izip
except ImportError:
    # Python 3 compat
    basestring = (str, bytes)
    izip, xrange = zip, range


def is_iterable(obj):
    """Similar in nature to :func:`callable`, ``is_iterable`` returns
    ``True`` if an object is `iterable`_, ``False`` if not.

    >>> is_iterable([])
    True
    >>> is_iterable(object())
    False

    .. _iterable: https://docs.python.org/2/glossary.html#term-iterable
    """
    try:
        iter(obj)
    except TypeError:
        return False
    return True


def is_scalar(obj):
    """A near-mirror of :func:`is_iterable`. Returns ``False`` if an
    object is an iterable container type. Strings are considered
    scalar as well, because strings are more often treated as whole
    values as opposed to iterables of 1-character substrings.

    >>> is_scalar(object())
    True
    >>> is_scalar(range(10))
    False
    >>> is_scalar('hello')
    True
    """
    return not is_iterable(obj) or isinstance(obj, basestring)


def split(src, sep=None, maxsplit=None):
    """Splits an iterable based on a separator. Like :meth:`str.split`,
    but for all iterables. Returns a list of lists.

    >>> split(['hi', 'hello', None, None, 'sup', None, 'soap', None])
    [['hi', 'hello'], ['sup'], ['soap']]

    See :func:`split_iter` docs for more info.
    """
    return list(split_iter(src, sep, maxsplit))


def split_iter(src, sep=None, maxsplit=None):
    """Splits an iterable based on a separator, *sep*, a max of
    *maxsplit* times (no max by default). *sep* can be:

      * a single value
      * an iterable of separators
      * a single-argument callable that returns True when a separator is
        encountered

    ``split_iter()`` yields lists of non-separator values. A separator will
    never appear in the output.

    >>> list(split_iter(['hi', 'hello', None, None, 'sup', None, 'soap', None]))
    [['hi', 'hello'], ['sup'], ['soap']]

    Note that ``split_iter`` is based on :func:`str.split`, so if
    *sep* is ``None``, ``split()`` **groups** separators. If empty lists
    are desired between two contiguous ``None`` values, simply use
    ``sep=[None]``:

    >>> list(split_iter(['hi', 'hello', None, None, 'sup', None]))
    [['hi', 'hello'], ['sup']]
    >>> list(split_iter(['hi', 'hello', None, None, 'sup', None], sep=[None]))
    [['hi', 'hello'], [], ['sup'], []]

    Using a callable separator:

    >>> falsy_sep = lambda x: not x
    >>> list(split_iter(['hi', 'hello', None, '', 'sup', False], falsy_sep))
    [['hi', 'hello'], [], ['sup'], []]

    See :func:`split` for a list-returning version.

    """
    if not is_iterable(src):
        raise TypeError('expected an iterable')

    if maxsplit is not None:
        maxsplit = int(maxsplit)
        if maxsplit == 0:
            yield [src]
            return

    if callable(sep):
        sep_func = sep
    elif not is_scalar(sep):
        sep = frozenset(sep)
        sep_func = lambda x: x in sep
    else:
        sep_func = lambda x: x == sep

    cur_group = []
    split_count = 0
    for s in src:
        if maxsplit is not None and split_count >= maxsplit:
            sep_func = lambda x: False
        if sep_func(s):
            if sep is None and not cur_group:
                # If sep is none, str.split() "groups" separators
                # check the str.split() docs for more info
                continue
            split_count += 1
            yield cur_group
            cur_group = []
        else:
            cur_group.append(s)

    if cur_group or sep is not None:
        yield cur_group
    return


def chunked(src, size, count=None, **kw):
    """Returns a list of *count* chunks, each with *size* elements,
    generated from iterable *src*. If *src* is not evenly divisible by
    *size*, the final chunk will have fewer than *size* elements.
    Provide the *fill* keyword argument to provide a pad value and
    enable padding, otherwise no padding will take place.

    >>> chunked(range(10), 3)
    [[0, 1, 2], [3, 4, 5], [6, 7, 8], [9]]
    >>> chunked(range(10), 3, fill=None)
    [[0, 1, 2], [3, 4, 5], [6, 7, 8], [9, None, None]]
    >>> chunked(range(10), 3, count=2)
    [[0, 1, 2], [3, 4, 5]]

    See :func:`chunked_iter` for more info.
    """
    chunk_iter = chunked_iter(src, size, **kw)
    if count is None:
        return list(chunk_iter)
    else:
        return list(itertools.islice(chunk_iter, count))


def chunked_iter(src, size, **kw):
    """Generates *size*-sized chunks from *src* iterable. Unless the
    optional *fill* keyword argument is provided, iterables not even
    divisible by *size* will have a final chunk that is smaller than
    *size*.

    >>> list(chunked_iter(range(10), 3))
    [[0, 1, 2], [3, 4, 5], [6, 7, 8], [9]]
    >>> list(chunked_iter(range(10), 3, fill=None))
    [[0, 1, 2], [3, 4, 5], [6, 7, 8], [9, None, None]]

    Note that ``fill=None`` in fact uses ``None`` as the fill value.
    """
    # TODO: add count kwarg?
    if not is_iterable(src):
        raise TypeError('expected an iterable')
    size = int(size)
    if size <= 0:
        raise ValueError('expected a positive integer chunk size')
    do_fill = True
    try:
        fill_val = kw.pop('fill')
    except KeyError:
        do_fill = False
        fill_val = None
    if kw:
        raise ValueError('got unexpected keyword arguments: %r' % kw.keys())
    if not src:
        return
    postprocess = lambda chk: chk
    if isinstance(src, basestring):
        postprocess = lambda chk, _sep=type(src)(): _sep.join(chk)
    cur_chunk = []
    i = 0
    for item in src:
        cur_chunk.append(item)
        i += 1
        if i % size == 0:
            yield postprocess(cur_chunk)
            cur_chunk = []
    if cur_chunk:
        if do_fill:
            lc = len(cur_chunk)
            cur_chunk[lc:] = [fill_val] * (size - lc)
        yield postprocess(cur_chunk)
    return


def windowed(src, size):
    """Returns tuples with exactly length *size*. If the iterable is
    too short to make a window of length *size*, no tuples are
    returned. See :func:`windowed_iter` for more.
    """
    return list(windowed_iter(src, size))


def windowed_iter(src, size):
    """Returns tuples with length *size* which represent a sliding
    window over iterable *src*.

    >>> list(windowed_iter(range(7), 3))
    [(0, 1, 2), (1, 2, 3), (2, 3, 4), (3, 4, 5), (4, 5, 6)]

    If the iterable is too short to make a window of length *size*,
    then no window tuples are returned.

    >>> list(windowed_iter(range(3), 5))
    []
    """
    # TODO: lists? (for consistency)
    tees = itertools.tee(src, size)
    try:
        for i, t in enumerate(tees):
            for _ in xrange(i):
                next(t)
    except StopIteration:
        return izip([])
    return izip(*tees)


def bucketize(src, key=None):
    """Group values in the *src* iterable by the value returned by *key*,
    which defaults to :class:`bool`, grouping values by
    truthiness.

    >>> bucketize(range(5))
    {False: [0], True: [1, 2, 3, 4]}
    >>> is_odd = lambda x: x % 2 == 1
    >>> bucketize(range(5), is_odd)
    {False: [0, 2, 4], True: [1, 3]}

    Value lists are not deduplicated:

    >>> bucketize([None, None, None, 'hello'])
    {False: [None, None, None], True: ['hello']}

    Note in these examples there were at most two keys, ``True`` and
    ``False``, and each key present has a list with at least one
    item. See :func:`partition` for a version specialized for binary
    use cases.
    """
    if not is_iterable(src):
        raise TypeError('expected an iterable')
    if key is None:
        key = bool
    if not callable(key):
        raise TypeError('expected callable key function')

    ret = {}
    for val in src:
        keyval = key(val)
        ret.setdefault(keyval, []).append(val)
    return ret


def partition(src, key=None):
    """No relation to :meth:`str.partition`, ``partition`` is like
    :func:`bucketize`, but for added convenience returns a tuple of
    ``(truthy_values, falsy_values)``.

    >>> nonempty, empty = partition(['', '', 'hi', '', 'bye'])
    >>> nonempty
    ['hi', 'bye']

    *key* defaults to :class:`bool`, but can be carefully overridden to
    use any function that returns either ``True`` or ``False``.

    >>> import string
    >>> is_digit = lambda x: x in string.digits
    >>> decimal_digits, hexletters = partition(string.hexdigits, is_digit)
    >>> ''.join(decimal_digits), ''.join(hexletters)
    ('0123456789', 'abcdefABCDEF')
    """
    bucketized = bucketize(src, key)
    return bucketized.get(True, []), bucketized.get(False, [])


def unique(src, key=None):
    """``unique()`` returns a list of unique values, as determined by
    *key*, in the order they first appeared in the input iterable,
    *src*.

    >>> ones_n_zeros = '11010110001010010101010'
    >>> ''.join(unique(ones_n_zeros))
    '10'

    See :func:`unique_iter` docs for more details.
    """
    return list(unique_iter(src, key))


def unique_iter(src, key=None):
    """Yield unique elements from the iterable, *src*, based on *key*,
    in the order in which they first appeared in *src*.

    >>> repetitious = [1, 2, 3] * 10
    >>> list(unique_iter(repetitious))
    [1, 2, 3]

    By default, *key* is the object itself, but *key* can either be a
    callable or, for convenience, a string name of the attribute on
    which to uniqueify objects, falling back on identity when the
    attribute is not present.

    >>> pleasantries = ['hi', 'hello', 'ok', 'bye', 'yes']
    >>> list(unique_iter(pleasantries, key=lambda x: len(x)))
    ['hi', 'hello', 'bye']
    """
    if not is_iterable(src):
        raise TypeError('expected an iterable, not %r' % type(src))
    if key is None:
        key_func = lambda x: x
    elif callable(key):
        key_func = key
    elif isinstance(key, basestring):
        key_func = lambda x: getattr(x, key, x)
    else:
        raise TypeError('"key" expected a string or callable, not %r' % key)
    seen = set()
    for i in src:
        k = key_func(i)
        if k not in seen:
            seen.add(k)
            yield i
    return


def one(src, cmp=None):
    """Along the same lines as builtins, :func:`all` and :func:`any`,
    ``one()`` returns the single object in the given iterable *src*
    that evaluates to ``True``, as determined by callable *cmp*. If
    unset, *cmp* defaults to :class:`bool`.

    If *src* has more than one object that evaluates to ``True``, or
    if there is no object that fulfills such condition, return
    ``False``. It's like an `XOR`_ over an iterable.

    >>> one((True, False, False))
    True
    >>> one((True, False, True))
    False
    >>> one((0, 0, 'a'))
    'a'
    >>> one((0, False, None))
    False
    >>> one((True, True))
    False
    >>> bool(one(('', 1)))
    True
    >>> one((10, 20, 30, 42), lambda i: i > 40)
    42

    See `Martín Gaitán's original repo`_ for further use cases.

    .. Martín Gaitán's original repo: https://github.com/mgaitan/one
    .. XOR: https://en.wikipedia.org/wiki/Exclusive_or
    """
    the_one = False
    for i in src:
        if cmp(i) if cmp else i:
            if the_one:
                return False
            the_one = i
    return the_one
