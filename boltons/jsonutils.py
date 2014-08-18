# -*- coding: utf-8 -*-

import os
import json


DEFAULT_BLOCKSIZE = 4096

"""
reverse iter lines algorithm:

- if it ends in a newline, add an empty string to the line list
- if there's one item, then prepend it to the buffer, continue
- if there's more than one item, pop the last item and prepend it to the buffer, yielding it
- yield all remaining items in reverse, except for the first
- first item becomes the new buffer

- when the outer loop completes, yield the buffer
"""


def reverse_iter_lines(file_obj, blocksize=DEFAULT_BLOCKSIZE, preseek=True):
    """\
    Iteratively generates a list of lines from a file object, in
    reverse order, i.e., Last line first, first line last. Uses the
    `.seek()` method of file objects, and is tested compatible with
    `file` objects, as well as StringIO/cStringIO.

    :param file_obj: The file object. Note that this
    generator mutably reads from the file and other functions should
    not mutably interact with the file object.
    :param blocksize: The block size to pass to `file.read()`
    :param preseek: tells the function whether or not to
    automatically seek to the end of the file. Defaults to
    True. `preseek=False` is useful in cases when the file cursor is
    already in position, either at the end of the file or in the
    middle for relative reverse line generation.
    """
    if preseek:
        file_obj.seek(0, os.SEEK_END)
    cur_pos = file_obj.tell()
    buff = ''
    while 0 < cur_pos:
        read_size = min(blocksize, cur_pos)
        cur_pos -= read_size
        file_obj.seek(cur_pos, os.SEEK_SET)
        cur = file_obj.read(read_size)
        lines = cur.splitlines()
        if cur[-1] == '\n':
            lines.append('')
        if len(lines) == 1:
            buff = lines[0] + buff
            continue
        last = lines.pop()
        yield last + buff
        for line in lines[:0:-1]:
            yield line
        buff = lines[0]
    if buff:
        # TODO: test this, does an empty buffer always mean don't yield?
        yield buff


"""
TODO: allow passthroughs for:

json.load(fp[, encoding[, cls[, object_hook[, parse_float[, parse_int[, parse_constant[, object_pairs_hook[, **kw]]]]]]]])
"""


class JSONLIterator(object):
    def __init__(self, file_obj, ignore_errors=False, reverse=False, rel_seek=None):
        self._reverse = bool(reverse)
        self._file_obj = file_obj
        self.ignore_errors = ignore_errors

        if rel_seek is None:
            if reverse:
                rel_seek = 1.0
        elif not -1.0 < rel_seek < 1.0:
            raise ValueError()
        elif rel_seek < 0:
            rel_seek = 1.0 - rel_seek
        self._rel_seek = rel_seek
        self._blocksize = 4096
        if rel_seek is not None:
            self._init_rel_seek()
        if self._reverse:
            self._line_iter = reverse_iter_lines(self._file_obj,
                                                 blocksize=self._blocksize,
                                                 preseek=False)
        else:
            self._line_iter = iter(self._file_obj)

    def _align_to_newline(self):
        fo, bsize = self._file_obj, self._blocksize
        cur, total_read = '', 0
        cur_pos = fo.tell()
        while '\n' not in cur:
            cur = fo.read(bsize)
            total_read += bsize
        try:
            newline_offset = cur.index('\n') + total_read - bsize
        except ValueError:
            raise  # TODO: seek to end?
        fo.seek(cur_pos + newline_offset)

    def _init_rel_seek(self):
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
        while 1:
            line = next(self._line_iter)
            if not line:
                continue
            try:
                obj = json.loads(line)
            except:
                if not self.ignore_errors:
                    raise
                continue
            return obj


def _test_reverse_iter_lines(filename, blocksize=DEFAULT_BLOCKSIZE):
    #from cStringIO import StringIO
    fo = open('_tmp_nl.txt')
    reference = fo.read()
    #fo = StringIO(reference)
    fo.seek(0, os.SEEK_END)
    rev_lines = list(reverse_iter_lines(fo, blocksize))
    assert '\n'.join(rev_lines[::-1]) == reference


if __name__ == '__main__':
    for blocksize in (1, 4, 11, 4096):
        _test_reverse_iter_lines('_tmp_nl.txt', blocksize)

    print list(JSONLIterator(open('_tmp_jsonl.jsonl'), reverse=True))
