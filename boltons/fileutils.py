# -*- coding: utf-8 -*-

import os
import stat
import errno
import tempfile

VALID_PERM_CHARS = 'rwx'


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
                invalid_chars = str(value).translate(None, VALID_PERM_CHARS)
            except (TypeError, UnicodeEncodeError):
                raise TypeError('expected string, not %r' % value)
            if invalid_chars:
                raise ValueError('got invalid chars %r in permission'
                                 ' specification %r, expected empty string'
                                 ' or one or more of %r'
                                 % (invalid_chars, value, VALID_PERM_CHARS))
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


def atomic_save(dest_path, **kwargs):
    return AtomicSaver(dest_path, **kwargs)


def _atomic_rename(path, new_path, overwrite=False):
    if overwrite:
        os.rename(path, new_path)
    else:
        os.link(path, new_path)
        os.unlink(path)


class AtomicSaver(object):
    def __init__(self, dest_path, **kwargs):
        self.dest_path = dest_path
        self.overwrite = kwargs.pop('overwrite', True)
        self.overwrite_part = kwargs.pop('overwrite_partfile', True)
        self.part_filename = kwargs.pop('part_file', None)
        self.text_mode = kwargs.pop('text_mode', False)  # for windows
        self.rm_part_on_exc = kwargs.pop('rm_part_on_exc', True)
        self._open = kwargs.pop('open_func', open)
        self._open_kwargs = kwargs.pop('open_kwargs', {})
        if kwargs:
            raise TypeError('unexpected kwargs: %r' % kwargs.keys)

        self.dest_path = os.path.abspath(self.dest_path)
        self.dest_dir = os.path.dirname(self.dest_path)
        if not self.part_filename:
            self.part_path = dest_path + '.part'
        else:
            self.part_path = os.path.join(self.dest_dir, self.part_path)
        self.mode = 'w+' if self.text_mode else 'w+b'

        self.part_file = None

    def setup(self):
        if os.path.lexists(self.dest_path):
            if not self.overwrite:
                raise OSError(errno.EEXIST,
                              'Overwrite disabled and file already exists',
                              self.dest_path)
        # this tests for a writable directory with rename permissions
        # early, as we may be writing to the part file for a while (not
        # using os.access because of the potential issues of effective vs
        # real privileges)
        _, tmp_part_path = tempfile.mkstemp(dir=self.dest_dir,
                                            text=self.text_mode)
        try:
            _atomic_rename(tmp_part_path, self.part_path,
                           overwrite=self.overwrite_part)
        except OSError:
            os.unlink(tmp_part_path)
            raise

        self.part_file = self._open(self.part_path, self.mode,
                                    **self._open_kwargs)

    def __enter__(self):
        self.setup()
        return self.part_file

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type:
            if self.rm_part_on_exc:
                try:
                    os.unlink(self.part_path)
                except:
                    pass
            return
        try:
            _atomic_rename(self.part_path, self.dest_path,
                           overwrite=self.overwrite)
        except OSError:
            if self.rm_part_on_exc:
                os.unlink(self.part_path)
        return


#with atomic_save('/home/mahmoud/tmp/final.txt') as f:
#    f.write('rofl')
#    raise ValueError('nope')
#    f.write('\n')


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
