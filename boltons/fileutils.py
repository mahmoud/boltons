# -*- coding: utf-8 -*-

# TODO: consider more than the lower 9 bits

VALID_CHARS = 'rwx'


class FilePerms(object):
    class _FilePermProperty(object):
        def __init__(self, attribute, offset):
            self.attribute = attribute
            self.offset = offset

        def __get__(self, fp_obj, type_=None):
            return getattr(fp_obj, self.attribute)

        def __set__(self, fp_obj, value):
            cur = getattr(fp_obj, self.attribute)
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
            unique_chars = ''.join(set(value))
            setattr(fp_obj, self.attribute, unique_chars)
            self._update_integer(fp_obj, unique_chars)

        def _update_integer(self, fp_obj, value):
            mode = 0
            key = 'xwr'
            for symbol in value:
                bit = 2 ** key.index(symbol)
                mode |= (bit << (self.offset * 3))
            fp_obj._integer |= mode

    def __init__(self, user='', group='', other=''):
        self._user, self._group, self._other = '', '', ''
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

    def __int__(self):
        return self._integer

    user = _FilePermProperty('_user', 2)
    group = _FilePermProperty('_group', 1)
    other = _FilePermProperty('_other', 0)

    def __repr__(self):
        cn = self.__class__.__name__
        return ('%s(user=%r, group=%r, other=%r)'
                % (cn, self.user, self.group, self.other))


if __name__ == '__main__':

    def _main():
        up = FilePerms()
        up.other = ''
        up.user = 'xrw'
        up.group = 'rrrwx'
        try:
            up.other = 'nope'
        except ValueError:
            pass
        print up
        print 'user:' , up.user
        print oct(int(up))
        print oct(int(FilePerms()))
    _main()
