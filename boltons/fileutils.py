# -*- coding: utf-8 -*-

import re


class FilePerms(object):
    VALID = re.compile('^[rwx]*$')

    class _fp_field(object):

        def __init__(self, attribute):
            self.attribute = attribute

        def __get__(self, fp_obj, type_=None):
            return getattr(fp_obj, self.attribute)

        def __set__(self, fp_obj, value):
            curr = getattr(fp_obj, self.attribute)
            if curr != value:
                if not FilePerms.VALID.match(value):
                    raise ValueError('unknown specification: '
                                     '{0}'.format(value))
                setattr(fp_obj, self.attribute, value)
                fp_obj._update_integer()

    def __init__(self, user='', group='', other=''):
        self._user, self._group, self._other = '', '', ''
        self._integer = 0
        self.user = user
        self.group = group
        self.other = other

    @classmethod
    def fromint(cls, i):
        # TODO: consider more than the lower 9 bits
        i &= 0777
        key = ('', 'x', 'w', 'xw', 'r', 'rx', 'rw', 'rwx')
        parts = []
        while i:
            parts.append(key[i & 07])
            i >>= 3
        parts.reverse()
        return cls(*parts)

    def _update_integer(self):
        specs = self._other, self._group, self._user
        mode = 0
        key = 'xwr'

        for field, spec in enumerate(specs):
            for symbol in spec:
                bit = key.index(symbol) * 2 or 1
                mode |= (bit << (field * len(specs)))

        self._integer = mode

    def __int__(self):
        return self._integer

    user = _fp_field('_user')
    group = _fp_field('_group')
    other = _fp_field('_other')

    def __repr__(self):
        cls = self.__class__.__name__
        return '{0!r}(user={1!r}, group={2!r}, other={3!r})'.format(cls,
                                                                    self.user,
                                                                    self.group,
                                                                    self.other)
