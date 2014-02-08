# -*- coding: utf-8 -*-

# TODO: consider more than the lower 9 bits

VALID_CHARS = 'rwx'


class UnixPerms(object):
    class _UnixPermProperty(object):
        def __init__(self, attribute):
            self.attribute = attribute

        def __get__(self, fp_obj, type_=None):
            return getattr(fp_obj, self.attribute)

        def __set__(self, fp_obj, value):
            try:
                cur = getattr(fp_obj, self.attribute)
            except AttributeError:
                cur = ''
                setattr(fp_obj, self.attribute, cur)  # not actually necessary
            if cur == value:
                return
            try:
                invalid_chars = str(value).translate(None, VALID_CHARS)
            except (TypeError, UnicodeEncodeError):
                raise TypeError('expected string, not %r' % value)
            if invalid_chars:
                raise ValueError('got invalid chars %r in permission'
                                 ' specification %r, expected empty string'
                                 ' or one or more of %r'
                                 % (invalid_chars, value, VALID_CHARS))
            setattr(fp_obj, self.attribute, ''.join(set(value)))
            fp_obj._update_integer()

    def __init__(self, user='', group='', other=''):
        self._integer = 0
        self.user = user
        self.group = group
        self.other = other

    @classmethod
    def from_int(cls, i):
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

    user = _UnixPermProperty('_user')
    group = _UnixPermProperty('_group')
    other = _UnixPermProperty('_other')

    def __repr__(self):
        cn = self.__class__.__name__
        return ('%s(user=%r, group=%r, other=%r)'
                % (cn, self.user, self.group, self.other))


if __name__ == '__main__':

    def _main():
        up = UnixPerms()
        up.other = ''
        up.user = 'xrw'
        up.group = 'rrrwx'
        try:
            up.other = 'nope'
        except ValueError:
            pass
        print up
        print oct(int(up))
    _main()
