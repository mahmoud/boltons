# -*- coding: utf-8 -*-

import itertools

from compat import basestring


__all__ = ['is_iterable', 'is_scalar', 'split', 'split_iter',
           'chunked', 'chunked_iter', 'bucketize', 'partition',
           'unique_iter', 'unique']


def is_iterable(obj):
    try:
        iter(obj)
    except TypeError:
        return False
    return True


def is_scalar(obj):
    return not is_iterable(obj) or isinstance(obj, basestring)


def split(src, sep=None, maxsplit=None):
    """
    Splits an iterable based on a separator. Returns a list of lists.

    >>> split(['hi', 'hello', None, None, 'sup', None, 'soap', None])
    [['hi', 'hello'], ['sup'], ['soap']]

    See split_iter docs below for more info.
    """
    return list(split_iter(src, sep, maxsplit))


def split_iter(src, sep=None, maxsplit=None):
    """
    Splits an iterable based on a separator, 'sep'. 'sep' can be a
    single value, an iterable of separators, or a single-argument
    callable that returns True when a separator is encountered.

    split_iter yields lists of non-separator values. A separator will
    never appear in the output.

    >>> list(split_iter(['hi', 'hello', None, None, 'sup', None, 'soap', None]))
    [['hi', 'hello'], ['sup'], ['soap']]

    Note that split_iter is based on str.split(), so if 'sep' is None,
    split() "groups" separators. If empty lists are desired between two
    contiguous None values, simply use sep=[None].

    >>> list(split_iter(['hi', 'hello', None, None, 'sup', None], sep=[None]))
    [['hi', 'hello'], [], ['sup'], []]

    Using a callable separator:

    >>> falsy_sep = lambda x: not x
    >>> list(split_iter(['hi', 'hello', None, '', 'sup', False], falsy_sep))
    [['hi', 'hello'], [], ['sup'], []]
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
    """
    Returns a list of 'count' chunks, each with 'size' elements,
    generated from iterable 'src'. If 'src' is not even divisible by
    'size', the final chunk will have fewer than 'size' elements.
    Use the 'fill' keyword argument to pad the final chunk.

    >>> chunked(range(10), 3)
    [[0, 1, 2], [3, 4, 5], [6, 7, 8], [9]]
    >>> chunked(range(10), 3, fill=None)
    [[0, 1, 2], [3, 4, 5], [6, 7, 8], [9, None, None]]
    >>> chunked(range(10), 3, count=2)
    [[0, 1, 2], [3, 4, 5]]
    """
    chunk_iter = chunked_iter(src, size, **kw)
    if count is None:
        return list(chunk_iter)
    ret = []
    for chunk in chunk_iter:
        if len(ret) >= count:
            return ret
        ret.append(chunk)
    return ret


def chunked_iter(src, size, **kw):
    """
    Generates 'size'-sized chunks from 'src' iterable. Unless
    the optional 'fill' keyword argument is provided, iterables
    not even divisible by 'size' will have a final chunk that is
    smaller than 'size'.

    Note that fill=None will in fact use None as the fill value.

    >>> list(chunked_iter(range(10), 3))
    [[0, 1, 2], [3, 4, 5], [6, 7, 8], [9]]
    >>> list(chunked_iter(range(10), 3, fill=None))
    [[0, 1, 2], [3, 4, 5], [6, 7, 8], [9, None, None]]
    """
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


def windowed_iter(src, size):
    """\
    Returns tuples with length `size` which represent a sliding
    window over iterable `src`.

    >>> list(windowed_iter(range(7), 3))
    [(0, 1, 2), (1, 2, 3), (2, 3, 4), (3, 4, 5), (4, 5, 6)]

    If the iterable is too short to make a window of length `size`,
    then no window tuples are returned.

    >>> list(windowed_iter(range(3), 5))
    []
    """
    tees = itertools.tee(src, size)
    try:
        for i, t in enumerate(tees):
            for _ in xrange(i):
                next(t)
    except StopIteration:
        return itertools.izip([])
    return itertools.izip(*tees)


def bucketize(src, keyfunc=None):
    """
    Group values in 'src' iterable by value returned by 'keyfunc'.
    keyfunc defaults to bool, which will group the values by
    truthiness; at most there will be two keys, True and False, and
    each key will have a list with at least one item.

    >>> bucketize(range(5))
    {False: [0], True: [1, 2, 3, 4]}
    >>> is_odd = lambda x: x % 2 == 1
    >>> bucketize(range(5), is_odd)
    {False: [0, 2, 4], True: [1, 3]}

    Value lists are not deduplicated:

    >>> bucketize([None, None, None, 'hello'])
    {False: [None, None, None], True: ['hello']}
    """
    if not is_iterable(src):
        raise TypeError('expected an iterable')
    if keyfunc is None:
        keyfunc = bool
    if not callable(keyfunc):
        raise TypeError('expected callable key function')

    ret = {}
    for val in src:
        key = keyfunc(val)
        ret.setdefault(key, []).append(val)
    return ret


def partition(src, keyfunc=None):
    """
    Like bucketize, but for added convenience returns a tuple of
    (truthy_values, falsy_values).

    >>> nonempty, empty = partition(['', '', 'hi', '', 'bye'])
    >>> nonempty
    ['hi', 'bye']

    keyfunc defaults to bool, but can be carefully overridden to
    use any function that returns either True or False.

    >>> import string
    >>> is_digit = lambda x: x in string.digits
    >>> decimal_digits, hexletters = partition(string.hexdigits, is_digit)
    >>> ''.join(decimal_digits), ''.join(hexletters)
    ('0123456789', 'abcdefABCDEF')
    """
    bucketized = bucketize(src, keyfunc)
    return bucketized.get(True, []), bucketized.get(False, [])


def unique_iter(iterable, key=None):
    """
    Yield unique elements from `iterable`, based on `key`, in the
    order in which they first appeared in `iterable`.

    By default, `key` is the identity operator, but `key` can either
    be a callable or, for convenience, a string name of the attribute
    on which to uniqueify objects, falling back on identity when the
    attribute is not present.

    >>> repetitious = [1, 2, 3] * 10
    >>> list(unique_iter(repetitious))
    [1, 2, 3]

    >>> pleasantries = ['hi', 'hello', 'ok', 'bye', 'yes']
    >>> list(unique_iter(pleasantries, key=lambda x: len(x)))
    ['hi', 'hello', 'bye']
    """
    if not is_iterable(iterable):
        raise TypeError('expected an iterable')
    if key is None:
        key_func = lambda x: x
    elif callable(key):
        key_func = key
    elif isinstance(key, basestring):
        key_func = lambda x: getattr(x, key, x)
    else:
        raise TypeError('"key" expected a string or callable')
    seen = set()
    for i in iterable:
        k = key_func(i)
        if k not in seen:
            seen.add(k)
            yield i
    return


def unique(iterable, key=None):
    """
    In keeping with the emergent convention of this module, unique()
    works exactly the same as unique_iter() (above), except that it
    returns a list instead of a generator.

    >>> ones_n_zeros = '11010110001010010101010'
    >>> ''.join(unique(ones_n_zeros))
    '10'
    """
    return list(unique_iter(iterable, key))
