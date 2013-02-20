# -*- coding: utf-8 -*-


def is_iterable(obj):
    return callable(getattr(obj, '__iter__', None))


def is_scalar(obj):
    return not is_iterable(obj) or isinstance(obj, basestring)


def split(src, sep=None, maxsplit=None):
    """
    Splits an iterable based on a separator, see split_iter
    docs below for more info.
    """
    return list(split_iter(src, sep, maxsplit))


def split_iter(src, sep=None, maxsplit=None):
    """
    Splits an iterable based on a separator, 'sep'. 'sep' can be a
    single value, an iterable of separators, or a single-argument
    callable that returns True when a separator is encountered.

    split_iter yields lists of non-separator values. A separator will
    never appear in the output.

    Note that split_iter is based on str.split(), so if sep is None,
    str.split() "groups" separators check the str.split() docs
    for more info.

    >>> list(split_iter(['hi', 'hello', None, None, 'sup', None, 'soap', None])
    [['hi', 'hello'], ['sup'], ['soap']]

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

    Note that fill=None will in fact use None as a fill value.
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
    cur_chunk = []
    i = 0
    for item in src:
        cur_chunk.append(item)
        i += 1
        if i % size == 0:
            yield cur_chunk
            cur_chunk = []
    if cur_chunk:
        if do_fill:
            lc = len(cur_chunk)
            cur_chunk[lc:] = [fill_val] * (size - lc)
        yield cur_chunk
    return


def main():
    vals = ['hi', 'hello', None, None, 'sup', None, 'soap', None]
    falsy_sep = lambda x: not x
    print list(split(vals, falsy_sep))
    print list(split(vals, [None]))
    print chunked(vals, 3)
    print chunked(vals, 3, fill=None)


if __name__ == '__main__':
    main()
