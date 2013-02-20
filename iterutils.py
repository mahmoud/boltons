# -*- coding: utf-8 -*-


def is_scalar(obj):
    return not hasattr(obj, '__iter__') or isinstance(obj, basestring)


def split(src, key=None, maxsplit=None):
    """
    Splits an iterable based on a separator, iterable of separators, or
    function that evaluates to True when a separator is encountered.

    Frankly, this feature should be part of the list builtin.

    TODO: This works with iterators but could itself be an generator.
    """
    if maxsplit is not None:
        maxsplit = int(maxsplit)
        if maxsplit == 0:
            return [src]

    if callable(key):
        key_func = key
    elif not is_scalar(key):
        key = set(key)
        key_func = lambda x: x in key
    else:
        key_func = lambda x: x == key

    ret = []
    cur_list = []
    for s in src:
        if key_func(s):
            ret.append(cur_list)
            cur_list = []
            if maxsplit is not None and len(ret) >= maxsplit:
                key_func = lambda x: False
        else:
            cur_list.append(s)
    ret.append(cur_list)

    if key is None:
        # If sep is none, str.split() "groups" separators
        # check the str.split() docs for more info
        return [x for x in ret if x]
    else:
        return ret
