# -*- coding: UTF-8 -*-

# Coding decl above needed for rendering the emdash properly in the
# documentation.

"""
Module ``ioutils`` implements a number of helper classes and functions which
are useful when dealing with input, output, and bytestreams in a variety of
ways.
"""
import os
import sys
from abc import (
    ABCMeta,
    abstractmethod,
    abstractproperty,
)
from errno import EINVAL
from io import BytesIO
from codecs import EncodedFile
from tempfile import TemporaryFile

# Python2/3 compat
if sys.version_info[0] == 3:
    text_type = str
    binary_type = bytes
else:
    text_type = unicode
    binary_type = str

READ_CHUNK_SIZE = 21333
"""
Number of bytes to read at a time. The value is ~ 1/3rd of 64k which means that
the value will easily fit in the L2 cache of most processors even if every
codepoint in a string is three bytes long which makes it a nice fast default
value.
"""


class SpooledIOBase(object):
    """
    The SpooledTempoaryFile class doesn't support a number of attributes and
    methods that a StringIO instance does. This brings the api as close to
    compatible as possible with StringIO so that it may be used as a near
    drop-in replacement to save memory.

    Another issue with SpooledTemporaryFile is that the spooled file is always
    a cStringIO rather than a StringIO which causes issues with some of our
    tools.
    """
    __metaclass__ = ABCMeta

    def __init__(self, max_size=5000000):
        self._max_size = max_size

    @abstractmethod
    def read(self, n=-1):
        """Read n characters from the buffer"""

    @abstractmethod
    def write(self, s):
        """Write into the buffer"""

    @abstractmethod
    def seek(self, pos, mode=0):
        """Seek to a specific point in a file"""

    @abstractmethod
    def readline(self, length=None):
        """Returns the next available line"""

    @abstractmethod
    def readlines(self, sizehint=0):
        """Returns a list of all lines from the current position forward"""

    @abstractmethod
    def rollover(self):
        """Roll file-like-object over into a real temporary file"""

    @abstractmethod
    def tell(self):
        """Return the current position"""

    @abstractproperty
    def buffer(self):
        """Should return a flo instance"""

    @abstractproperty
    def _rolled(self):
        """Returns whether the file has been rolled to a real file or not"""

    @abstractproperty
    def len(self):
        """Returns the length of the data"""

    def _get_softspace(self):
        return self.buffer.softspace

    def _set_softspace(self, val):
        self.buffer.softspace = val

    softspace = property(_get_softspace, _set_softspace)

    @property
    def _file(self):
        return self.buffer

    def close(self):
        return self.buffer.close()

    def flush(self):
        return self.buffer.flush()

    def isatty(self):
        return self.buffer.isatty()

    def next(self):
        return self.readline()

    @property
    def closed(self):
        return self.buffer.closed

    @property
    def pos(self):
        return self.tell()

    @property
    def buf(self):
        return self.getvalue()

    def fileno(self):
        self.rollover()
        return self.buffer.fileno()

    def truncate(self, size=None):
        """
        Custom version of truncate that takes either no arguments (like the
        real SpooledTemporaryFile) or a single argument that truncates the
        value to a certain index location.
        """
        if size is None:
            return self.buffer.truncate()

        if size < 0:
            raise IOError(EINVAL, "Negative size not allowed")

        # Emulate truncation to a particular location
        pos = self.tell()
        self.seek(size)
        self.buffer.truncate()
        if pos < size:
            self.seek(pos)

    def getvalue(self):
        """Return the entire files contents"""
        pos = self.tell()
        self.seek(0)
        val = self.read()
        self.seek(pos)
        return val

    def __len__(self):
        return self.len

    def __iter__(self):
        yield self.readline()

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self._file.close()

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.getvalue() == other.getvalue()
        return False

    def __ne__(self, other):
        return not self.__eq__(other)

    def __bool__(self):
        return True

    __nonzero__=__bool__


class SpooledBytesIO(SpooledIOBase):
    """
    SpooledBytesIO is a spooled file-like-object that only accepts bytes. On
    Python 2.x this means the 'str' type; on Python 3.x this means the 'bytes'
    type. Bytes are written in and retrieved exactly as given, but it will
    raise TypeErrors if something other than bytes are written.

    Example::

        >>> from boltons import ioutils
        >>> with ioutils.SpooledBytesIO() as f:
        ...     f.write(b"Happy IO")
        ...     _ = f.seek(0)
        ...     isinstance(f.getvalue(), ioutils.binary_type)
        True
    """

    def read(self, n=-1):
        return self.buffer.read(n)

    def write(self, s):
        if not isinstance(s, binary_type):
            raise TypeError("{0} expected, got {1}".format(
                binary_type.__name__,
                type(s).__name__
            ))

        if self.tell() + len(s) >= self._max_size:
            self.rollover()
        self.buffer.write(s)

    def seek(self, pos, mode=0):
        return self.buffer.seek(pos, mode)

    def readline(self, length=None):
        return self.buffer.readline(length)

    def readlines(self, sizehint=0):
        return self.buffer.readlines(sizehint)

    def rollover(self):
        """Roll the StringIO over to a TempFile"""
        if not self._rolled:
            tmp = TemporaryFile()
            pos = self.buffer.tell()
            tmp.write(self.buffer.getvalue())
            tmp.seek(pos)
            self.buffer.close()
            self._buffer = tmp

    @property
    def _rolled(self):
        return not isinstance(self.buffer, BytesIO)

    @property
    def buffer(self):
        try:
            return self._buffer
        except AttributeError:
            self._buffer = BytesIO()
        return self._buffer

    @property
    def len(self):
        """Determine the length of the file"""
        pos = self.tell()
        if self._rolled:
            self.seek(0)
            val = os.fstat(self.fileno()).st_size
        else:
            self.seek(0, os.SEEK_END)
            val = self.tell()
        self.seek(pos)
        return val

    def tell(self):
        return self.buffer.tell()


class SpooledStringIO(SpooledIOBase):
    """
    SpooledStringIO is a spooled file-like-object that only accepts unicode
    values. On Python 2.x this means the 'unicode' type and on Python 3.x this
    means the 'str' type. Values are accepted as unicode and then coerced into
    utf-8 encoded bytes for storage. On retrieval, the values are returned as
    unicode.

    Example::

        >>> from boltons import ioutils
        >>> with ioutils.SpooledStringIO() as f:
        ...     f.write(u"\u2014 Hey, an emdash!")
        ...     _ = f.seek(0)
        ...     isinstance(f.read(), ioutils.text_type)
        True

    """
    def __init__(self, *args, **kwargs):
        self._tell = 0
        super(SpooledStringIO, self).__init__(*args, **kwargs)

    def read(self, n=-1):
        ret = self.buffer.reader.read(n, n)
        self._tell = self.tell() + len(ret)
        return ret

    def write(self, s):
        if not isinstance(s, text_type):
            raise TypeError("{0} expected, got {1}".format(
                text_type.__name__,
                type(s).__name__
            ))
        current_pos = self.tell()
        if self.buffer.tell() + len(s.encode('utf-8')) >= self._max_size:
            self.rollover()
        self.buffer.write(s.encode('utf-8'))
        self._tell = current_pos + len(s)

    def _traverse_codepoints(self, current_position, n):
        """Traverse from current position to the right n codepoints"""
        dest = current_position + n
        while True:
            if current_position == dest:
                # By chance we've landed on the right position, break
                break

            # If the read would take us past the intended position then
            # seek only enough to cover the offset
            if current_position + READ_CHUNK_SIZE > dest:
                self.read(dest - current_position)
                break
            else:
                ret = self.read(READ_CHUNK_SIZE)

            # Increment our current position
            current_position += READ_CHUNK_SIZE

            # If we kept reading but there was nothing here, break
            # as we are at the end of the file
            if not ret:
                break

        return dest

    def seek(self, pos, mode=0):
        """Traverse from offset to the specified codepoint"""
        # Seek to position from the start of the file
        if mode == os.SEEK_SET:
            self.buffer.seek(0)
            self._traverse_codepoints(0, pos)
            self._tell = pos
        # Seek to new position relative to current position
        elif mode == os.SEEK_CUR:
            start_pos = self.tell()
            self._traverse_codepoints(self.tell(), pos)
            self._tell = start_pos + pos
        elif mode == os.SEEK_END:
            self.buffer.seek(0)
            dest_position = self.len - pos
            self._traverse_codepoints(0, dest_position)
            self._tell = dest_position
        else:
            raise ValueError(
                "Invalid whence ({0}, should be 0, 1, or 2)".format(mode)
            )
        return self.tell()

    def readline(self, length=None):
        ret = self.buffer.readline(length).decode('utf-8')
        self._tell = self.tell() + len(ret)
        return ret

    def readlines(self, sizehint=0):
        ret = [x.decode('utf-8') for x in self.buffer.readlines(sizehint)]
        self._tell = self.tell() + sum((len(x) for x in ret))
        return ret

    @property
    def buffer(self):
        try:
            return self._buffer
        except AttributeError:
            self._buffer = EncodedFile(BytesIO(), data_encoding='utf-8')
        return self._buffer

    @property
    def _rolled(self):
        return not isinstance(self.buffer.stream, BytesIO)

    def rollover(self):
        """Roll the StringIO over to a TempFile"""
        if not self._rolled:
            tmp = EncodedFile(TemporaryFile(), data_encoding='utf-8')
            pos = self.buffer.tell()
            tmp.write(self.buffer.getvalue())
            tmp.seek(pos)
            self.buffer.close()
            self._buffer = tmp

    def tell(self):
        """Return the codepoint position"""
        return self._tell

    @property
    def len(self):
        """Determine the number of codepoints in the file"""
        pos = self.buffer.tell()
        self.buffer.seek(0)
        total = 0
        while True:
            ret = self.read(READ_CHUNK_SIZE)
            if not ret:
                break
            total += len(ret)
        self.buffer.seek(pos)
        return total
