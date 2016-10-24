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


def utf8_encode_if_unicode(string):
    """
    Given a string type, return it in bytes, encoding to UTF-8 if the string is
    unicode.
    """
    if isinstance(string, text_type):
        return string.encode('utf-8')
    elif isinstance(string, binary_type):
        return string
    else:
        raise TypeError("{} is not a unicode or str object".format(string))


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

    def seek(self, pos, mode=0):
        return self.buffer.seek(pos, mode)

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
        self.buffer.truncate(size)
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

        self.buffer.write(s)
        if self.tell() >= self._max_size:
            self.rollover()

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

    def read(self, n=-1):
        return self.buffer.read(n).decode('utf-8')

    def write(self, s):
        if not isinstance(s, text_type):
            raise TypeError("{0} expected, got {1}".format(
                text_type.__name__,
                type(s).__name__
            ))

        self.buffer.write(s.encode('utf-8'))
        if self.tell() >= self._max_size:
            self.rollover()

    def readline(self, length=None):
        return self.buffer.readline(length).decode('utf-8')

    def readlines(self, sizehint=0):
        return [x.decode('utf-8') for x in self.buffer.readlines(sizehint)]

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
        pos = self.buffer.tell()
        self.seek(0)
        enc_pos = 0
        while True:
            current_pos = self.buffer.tell()
            if current_pos == pos:
                break

            ret = self.read(21333)
            if self.buffer.tell() < pos:
                enc_pos += len(ret)
                continue

            # If the previous check fails, then we've seeked beyond the
            # intended position. Go back to our position at the start of the
            # loop and iterate one codepoint at a time until we reach the
            # buffers position.
            self.buffer.seek(current_pos)
            while True:
                if self.buffer.tell() == pos:
                    break
                self.read(1)
                enc_pos += 1
            break
        self.buffer.seek(pos)
        return enc_pos

    @property
    def len(self):
        """Determine the number of codepoints in the file"""
        pos = self.buffer.tell()
        self.seek(0)
        total = 0
        while True:
            ret = self.read(21333)
            if not ret:
                break
            total += len(ret)
        self.buffer.seek(pos)
        return total
