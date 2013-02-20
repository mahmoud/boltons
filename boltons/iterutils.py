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


def main():
    vals = ['hi', 'hello', None, None, 'sup', None, 'soap', None]
    falsy_sep = lambda x: not x
    print list(split(vals, falsy_sep))
    print list(split(vals, [None]))


if __name__ == '__main__':
    main()
