# Copyright (c) 2013, Mahmoud Hashemi
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are
# met:
#
#    * Redistributions of source code must retain the above copyright
#      notice, this list of conditions and the following disclaimer.
#
#    * Redistributions in binary form must reproduce the above
#      copyright notice, this list of conditions and the following
#      disclaimer in the documentation and/or other materials provided
#      with the distribution.
#
#    * The names of the contributors may not be used to endorse or
#      promote products derived from this software without specific
#      prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
# A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
# OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
# LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
# DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
# THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

"""``jsonutils`` aims to provide various helpers for working with
JSON. Currently it focuses on providing a reliable and intuitive means
of working with `JSON Lines`_-formatted files.

.. _JSON Lines: http://jsonlines.org/

"""


import io
import os
import json
import codecs
import re


DEFAULT_BLOCKSIZE = 4096


__all__ = ['JSONLIterator', 'reverse_iter_lines']


def reverse_iter_lines(file_obj, blocksize=DEFAULT_BLOCKSIZE, preseek=True, encoding=None):
    """Returns an iterator over the lines from a file object, in
    reverse order, i.e., last line first, first line last. Uses the
    :meth:`file.seek` method of file objects, and is tested compatible with
    :class:`file` objects, as well as :class:`StringIO.StringIO`.

    Args:
        file_obj (file): An open file object. Note that
            ``reverse_iter_lines`` mutably reads from the file and
            other functions should not mutably interact with the file
            object during iteration. Files can be opened in bytes or
            text mode. Seek before reusing a text stream after iteration.
        blocksize (int): The block size to pass to
          :meth:`file.read()`. Warning: keep this a fairly large
          multiple of 2, defaults to 4096.
        preseek (bool): Tells the function whether or not to automatically
            seek to the end of the file. Defaults to ``True``.
            ``preseek=False`` is useful in cases when the
            file cursor is already in position, either at the end of
            the file or in the middle for relative reverse line
            generation.
        encoding (str): Text encoding used to decode lines. Defaults to the
            file's encoding, or returns bytes when neither is specified.
            UTF-16/32 blocks are aligned to complete code points before
            decoding. Generic UTF-16/32 consume a leading byte-order mark,
            or use native byte order when no mark is present.

    """
    # This function is a bit of a pain because it attempts to be byte/text agnostic
    encoding = encoding or getattr(file_obj, 'encoding', None)

    # need orig_obj to keep alive otherwise __del__ on the TextWrapper will close the file
    orig_obj = file_obj
    try:
        file_obj = orig_obj.buffer
    except (AttributeError, io.UnsupportedOperation):
        pass

    # read(0) reveals whether the stream yields text (e.g., io.StringIO,
    # which has no .buffer to unwrap) or bytes
    empty = file_obj.read(0)
    is_text = isinstance(empty, str)
    newline = '\n' if is_text else b'\n'
    decode = bool(encoding) and not is_text
    empty_line = '' if (decode or is_text) else b''

    if preseek:
        file_obj.seek(0, os.SEEK_END)
    cur_pos = file_obj.tell()
    content_start = unit_size = 0
    if decode and cur_pos:
        codec = codecs.lookup(encoding).name
        if codec in ('utf-16', 'utf-16-le', 'utf-16-be',
                     'utf-32', 'utf-32-le', 'utf-32-be'):
            unit_size = 2 if codec.startswith('utf-16') else 4
            if codec in ('utf-16', 'utf-32') and cur_pos:
                file_obj.seek(0)
                mark = file_obj.read(unit_size)
                file_obj.seek(cur_pos)
                little = codecs.BOM_UTF16_LE if unit_size == 2 else codecs.BOM_UTF32_LE
                big = codecs.BOM_UTF16_BE if unit_size == 2 else codecs.BOM_UTF32_BE
                if mark in (little, big):
                    content_start = unit_size if cur_pos >= unit_size else 0
                    codec += '-le' if mark == little else '-be'
                else:
                    codec += '-le' if codecs.BOM_UTF16 == codecs.BOM_UTF16_LE else '-be'
            encoding = codec
            empty, newline, decode = '', '\n', False
    buff = empty
    while content_start < cur_pos:
        read_size = blocksize
        if unit_size:
            read_size = (read_size + unit_size - 1) // unit_size * unit_size
        read_size = min(read_size, cur_pos - content_start)
        cur_pos -= read_size
        file_obj.seek(cur_pos, os.SEEK_SET)
        cur = file_obj.read(read_size)
        if unit_size:
            # A UTF-16 block beginning with a low surrogate needs the preceding
            # high surrogate, which belongs to this same Unicode code point.
            byteorder = 'little' if encoding.endswith('-le') else 'big'
            if (unit_size == 2 and cur_pos > content_start
                    and 0xdc00 <= int.from_bytes(cur[:2], byteorder) <= 0xdfff):
                cur_pos -= 2
                file_obj.seek(cur_pos, os.SEEK_SET)
                cur = file_obj.read(2) + cur
            cur = cur.decode(encoding)
        buff = cur + buff
        if unit_size:
            # Preserve bytes.splitlines' CR/LF delimiters, rather than adding
            # the extra Unicode separators recognized by str.splitlines.
            lines = re.split(r'\r\n|\r|\n', buff)
            if not lines[-1]:
                lines.pop()
        else:
            lines = buff.splitlines()

        # until the start of the file, the first line may be partial
        if cur_pos > content_start and (len(lines) < 2 or lines[0] == empty):
            continue
        if buff[-1:] == newline:
            yield empty_line
        for line in reversed(lines[1:] if cur_pos > content_start else lines):
            yield line.decode(encoding) if decode else line
        buff = lines[0] if cur_pos > content_start else empty
    if buff:
        yield buff.decode(encoding) if decode else buff



"""
TODO: allow passthroughs for:

json.load(fp[, encoding[, cls[, object_hook[, parse_float[, parse_int[, parse_constant[, object_pairs_hook[, **kw]]]]]]]])
"""


class JSONLIterator:
    """The ``JSONLIterator`` is used to iterate over JSON-encoded objects
    stored in the `JSON Lines format`_ (one object per line).

    Most notably it has the ability to efficiently read from the
    bottom of files, making it very effective for reading in simple
    append-only JSONL use cases. It also has the ability to start from
    anywhere in the file and ignore corrupted lines.

    Args:
        file_obj (file): An open file object.
        ignore_errors (bool): Whether to skip over lines that raise an error on
            deserialization (:func:`json.loads`).
        reverse (bool): Controls the direction of the iteration.
            Defaults to ``False``. If set to ``True`` and *rel_seek*
            is unset, seeks to the end of the file before iteration
            begins.
        rel_seek (float): Used to preseek the start position of
            iteration. Set to 0.0 for the start of the file, 1.0 for the
            end, and anything in between.

    .. _JSON Lines format: http://jsonlines.org/
    """
    def __init__(self, file_obj,
                 ignore_errors=False, reverse=False, rel_seek=None):
        self._reverse = bool(reverse)
        self._file_obj = file_obj
        self.ignore_errors = ignore_errors

        if rel_seek is None:
            if reverse:
                rel_seek = 1.0
        elif not -1.0 < rel_seek <= 1.0:
            raise ValueError("'rel_seek' expected a float between"
                             " -1.0 and 1.0, not %r" % rel_seek)
        elif rel_seek < 0:
            rel_seek = 1.0 + rel_seek
        self._rel_seek = rel_seek
        self._blocksize = 4096
        if rel_seek is not None:
            self._init_rel_seek()
        if self._reverse:
            self._line_iter = reverse_iter_lines(self._file_obj,
                                                 blocksize=self._blocksize,
                                                 preseek=False)
        else:
            # readline() (unlike next()) keeps tell() usable on text files
            self._line_iter = iter(self._file_obj.readline,
                                   self._file_obj.read(0))

    @property
    def cur_byte_pos(self):
        "A property representing where in the file the iterator is reading."
        return self._file_obj.tell()

    def _align_to_newline(self):
        "Aligns the file object's position to the next newline."
        fo, bsize = self._file_obj, self._blocksize
        newline = b'\n' if isinstance(fo.read(0), bytes) else '\n'
        cur, total_read = newline[:0], 0
        cur_pos = fo.tell()
        while newline not in cur:
            cur = fo.read(bsize)
            if not cur:
                # no newline until EOF; a partial trailing line was
                # never yieldable from a mid-line seek anyway
                fo.seek(0, os.SEEK_END)
                return
            total_read += bsize
        newline_offset = cur.index(newline) + total_read - bsize
        fo.seek(cur_pos + newline_offset)

    def _init_rel_seek(self):
        "Sets the file object's position to the relative location set above."
        rs, fo = self._rel_seek, self._file_obj
        if rs == 0.0:
            fo.seek(0, os.SEEK_SET)
        else:
            fo.seek(0, os.SEEK_END)
            size = fo.tell()
            if rs == 1.0:
                self._cur_pos = size
            else:
                target = int(size * rs)
                fo.seek(target, os.SEEK_SET)
                self._align_to_newline()
                self._cur_pos = fo.tell()

    def __iter__(self):
        return self

    def next(self):
        """Yields one :class:`dict` loaded with :func:`json.loads`, advancing
        the file object by one line. Raises :exc:`StopIteration` upon reaching
        the end of the file (or beginning, if ``reverse`` was set to ``True``.
        """
        while 1:
            line = next(self._line_iter).lstrip()
            if not line:
                continue
            try:
                obj = json.loads(line)
            except Exception:
                if not self.ignore_errors:
                    raise
                continue
            return obj

    __next__ = next


if __name__ == '__main__':
    def _main():
        import sys
        if '-h' in sys.argv or '--help' in sys.argv:
            print('loads one or more JSON Line files for basic validation.')
            return
        verbose = False
        if '-v' in sys.argv or '--verbose' in sys.argv:
            verbose = True
        file_count, obj_count = 0, 0
        filenames = sys.argv[1:]
        for filename in filenames:
            if filename in ('-h', '--help', '-v', '--verbose'):
                continue
            file_count += 1
            with open(filename, 'rb') as file_obj:
                iterator = JSONLIterator(file_obj)
                cur_obj_count = 0
                while 1:
                    try:
                        next(iterator)
                    except ValueError:
                        print('error reading object #%s around byte %s in %s'
                              % (cur_obj_count + 1, iterator.cur_byte_pos, filename))
                        return
                    except StopIteration:
                        break
                    obj_count += 1
                    cur_obj_count += 1
                    if verbose and obj_count and obj_count % 100 == 0:
                        sys.stdout.write('.')
                        if obj_count % 10000:
                            sys.stdout.write('%s\n' % obj_count)
        if verbose:
            print('files checked: %s' % file_count)
            print('objects loaded: %s' % obj_count)
        return

    _main()
