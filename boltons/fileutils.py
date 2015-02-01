# -*- coding: utf-8 -*-

import os
import stat

VALID_CHARS = 'rwx'

class FilePerms(object):
    # TODO: consider more than the lower 9 bits
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

    @classmethod
    def from_path(cls, path):
        stat_res = os.stat(path)
        return cls.from_int(stat.S_IMODE(stat_res.st_mode))

    def __int__(self):
        return self._integer

    user = _FilePermProperty('_user', 2)
    group = _FilePermProperty('_group', 1)
    other = _FilePermProperty('_other', 0)

    def __repr__(self):
        cn = self.__class__.__name__
        return ('%s(user=%r, group=%r, other=%r)'
                % (cn, self.user, self.group, self.other))


"""
def validate(file_path):
    pass

with success_swap(file_to_write, validate=validate) as f:
    f.write(urllib.get(url))

"""

import errno
import tempfile


def success_swap(dest_path, validate=None, **kwargs):
    overwrite = kwargs.pop('overwrite', True)
    part_file = kwargs.pop('part_file', None)
    text_mode = kwargs.pop('text_mode', False)
    if kwargs:
        raise TypeError('unexpected kwargs: %r' % kwargs.keys)
    dest_path = os.path.abspath(dest_path)
    if os.path.isfile(dest_path):
        if not overwrite:
            raise OSError(errno.EEXIST,
                          'Overwrite disabled and file already exists',
                          dest_path)
    dest_dir = os.path.dirname(dest_path)
    if not part_file:
        part_path = dest_path + '.part'
    else:
        part_path = os.path.join(dest_dir, part_path)

    # this tests for a writable directory with rename permissions
    # early, as we may be writing to the part file for a while (not
    # using os.access because of the potential issues of effective vs
    # real privileges)
    part_fd, tmp_part_path = tempfile.mkstemp(dir=dest_dir, text=text_mode)
    os.rename(tmp_part_path, part_path)
    mode = 'w+' if text_mode else 'w+b'
    part_file = open(part_path, mode)  # os.fdopen(part_fd, mode)
    #part_file.name = part_path
    ss = SuccessSwapper(part_file, dest_path, validate, overwrite)
    # import pdb;pdb.set_trace()
    return ss


class SuccessSwapper(object):
    def __init__(self, part_file, dest_path, validate, overwrite):
        self.part_file = part_file
        self.part_path = part_file.name
        self.dest_path = dest_path
        self.validate = validate
        self.overwrite = overwrite
        self.rm_part_on_exc = True

    def __enter__(self):
        return self.part_file

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type:
            if self.rm_part_on_exc:
                os.unlink(self.part_path)
            return
        if self.validate:
            if not self.validate(self.part_path):
                # TODO raise exception or just return?
                return
        if not self.overwrite and os.path.isfile(self.dest_path):
            # TODO: again, raise or just return
            return

        os.rename(self.part_path, self.dest_path)

    def __getattr__(self, attr):
        return getattr(self.part_file, attr)


#with success_swap('/home/mahmoud/tmp/final.txt') as f:
#    f.write('lol')


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
        print 'user:', up.user
        print oct(int(up))
        print oct(int(FilePerms()))
    _main()
