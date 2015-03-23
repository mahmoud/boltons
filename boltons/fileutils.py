# -*- coding: utf-8 -*-
"""\

Given how often Python is used for wrangling disk contents, one
would expect more of these to be provided.

"""

import os
import re
import stat
import errno
import fnmatch
import tempfile
from shutil import copy2, copystat, Error


VALID_PERM_CHARS = 'rwx'


def mkdir_p(path):
    """\
    Creates a directory and any parent directories that may need to
    be created along the way, without raising errors for any existing
    directories. This function mimics the behavior of ``mkdir -p`` of
    Linux/BSD environments, but also works on Windows.
    """
    try:
        os.makedirs(path)
    except OSError as exc:
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            return
        raise
    return


class FilePerms(object):
    """\
    The ``FilePerms`` type is used to represent standard POSIX filesystem permissions:

    * Read
    * Write
    * Execute

    Across three classes of user:

    * Owning (u)ser
    * Owner's (g)roup
    * Any (o)ther user

    This class assists with computing new permissions, as well as
    working with numeric octal ``777``-style and ``rwx``-style
    permissions. Currently it only considers the bottom 9 permission
    bits; it does not support sticky bits or more advanced permission
    systems.
    """
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
    """\
    A convenient interface to the ``AtomicSaver`` type. See the
    ``AtomicSaver`` documentation for more info.
    """
    return AtomicSaver(dest_path, **kwargs)


def _atomic_rename(path, new_path, overwrite=False):
    if overwrite:
        os.rename(path, new_path)
    else:
        os.link(path, new_path)
        os.unlink(path)


class AtomicSaver(object):
    """\

    Use this to get a writable file which will be moved into place as
    long as no exceptions are raised before its close. It returns a
    standard Python ``file`` which can still be closed explicitly and
    is also usable as a context manager (i.e., via the ``with``
    statement).
    """
    def __init__(self, dest_path, **kwargs):
        """
            Args:
                dest_path (str): The path where the completed file will be written
                overwrite (bool, optional): Whether to overwrite the destination file if it exists at completion time. Defaults to True.
                part_file (str, optional): Name of the temporary ``part_file``. Defaults to ``dest_path`` + ".part"
                rm_part_on_exc (bool, optional): Remove ``part_file`` on exception. Defaults to True.
                overwrite_partfile (bool, optional): Whether to overwrite the ``part_file`` should it exist at setup time. Defaults to True.
                open_func (callable, optional): Function used to open the file. Override this if you want to use ``codecs.open`` or some other alternative. Defaults to ``open()``.
                open_kwargs (dict, optional): Additional keyword arguments to pass to ``open_func``. Defaults to ``{}``.
        """
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
        """\
        Called on context manager entry (the ``with`` statement), the
        ``setup()`` function creates the temporary file in the same
        directory as the destination file. It tests for a writable
        directory with rename permissions early, as we may be writing
        to the part file for a while (not using os.access because of
        the potential issues of effective vs real privileges).
        """
        if os.path.lexists(self.dest_path):
            if not self.overwrite:
                raise OSError(errno.EEXIST,
                              'Overwrite disabled and file already exists',
                              self.dest_path)
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


_CUR_DIR = os.path.dirname(os.path.abspath(__file__))


def iter_find_files(directory, patterns, ignored=None):
    """\
    Finds files under a `directory`, matching `patterns` using "glob"
    syntax (e.g., "*.txt"). It's also possible to ignore patterns with
    the `ignored` argument, which uses the same format as `patterns.

    >>> filenames = sorted(iter_find_files(_CUR_DIR, '*.py'))
    >>> filenames[-1].split('/')[-1]
    'tzutils.py'
    >>> filenames = iter_find_files(_CUR_DIR, '*.py', ignored='.#*')

    That last example ignores emacs lockfiles.
    """
    if isinstance(patterns, basestring):
        patterns = [patterns]
    pats_re = re.compile('|'.join([fnmatch.translate(p) for p in patterns]))

    if not ignored:
        ignored = []
    elif isinstance(ignored, basestring):
        ignored = [ignored]
    ign_re = re.compile('|'.join([fnmatch.translate(p) for p in ignored]))
    for root, dirs, files in os.walk(directory):
        for basename in files:
            if pats_re.match(basename):
                if ignored and ign_re.match(basename):
                    continue
                filename = os.path.join(root, basename)
                yield filename
    return


def copytree(src, dst, symlinks=False, ignore=None):
    """Recursively copy a directory tree using copy2().

    The destination directory is allowed to already exist.
    If exception(s) occur, an Error is raised with a list of reasons.

    If the optional symlinks flag is true, symbolic links in the
    source tree result in symbolic links in the destination tree; if
    it is false, the contents of the files pointed to by symbolic
    links are copied.

    The optional ignore argument is a callable. If given, it
    is called with the `src` parameter, which is the directory
    being visited by copytree(), and `names` which is the list of
    `src` contents, as returned by os.listdir():

        callable(src, names) -> ignored_names

    Since copytree() is called recursively, the callable will be
    called once for each directory that is copied. It returns a
    list of names relative to the `src` directory that should
    not be copied.

    XXX Consider this example code rather than the ultimate tool.

    """
    names = os.listdir(src)
    if ignore is not None:
        ignored_names = ignore(src, names)
    else:
        ignored_names = set()

    mkdir_p(dst)
    errors = []
    for name in names:
        if name in ignored_names:
            continue
        srcname = os.path.join(src, name)
        dstname = os.path.join(dst, name)
        try:
            if symlinks and os.path.islink(srcname):
                linkto = os.readlink(srcname)
                os.symlink(linkto, dstname)
            elif os.path.isdir(srcname):
                copytree(srcname, dstname, symlinks, ignore)
            else:
                # Will raise a SpecialFileError for unsupported file types
                copy2(srcname, dstname)
        # catch the Error from the recursive copytree so that we can
        # continue with other files
        except Error as e:
            errors.extend(e.args[0])
        except EnvironmentError, why:
            errors.append((srcname, dstname, str(why)))
    try:
        copystat(src, dst)
    except OSError, why:
        if WindowsError is not None and isinstance(why, WindowsError):
            # Copying file access times may fail on Windows
            pass
        else:
            errors.append((src, dst, str(why)))
    if errors:
        raise Error(errors)


if __name__ == '__main__':
    #with atomic_save('/tmp/final.txt') as f:
    #    f.write('rofl')
    #    raise ValueError('nope')
    #    f.write('\n')

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
