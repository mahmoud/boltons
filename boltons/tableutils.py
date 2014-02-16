# -*- coding: utf-8 -*-


from itertools import islice


_MISSING = object()

"""
class Backend(object):
    row_type = list

    def _guess_headers(self):
        pass


def _guess_headers(data):
    if not data:
        return [], data
    try:
        headers = data[0].keys()
        # assuming all dicts have the same keys would enable a faster version
        data = ([ci.get(ch, None) for ch in headers] for ci in data)
    except:
        try:
            headers = data[0][0]
            data = islice(data, 1, None)
        except:
            raise TypeError('could not infer headers from data')
    return headers, data
"""


class Table(object):
    # list-backed style
    def __init__(self, data=None, headers=_MISSING):
        if headers is _MISSING and data:
            headers, data = list(data[0]), islice(data, 1, None)
        self.headers = headers or []
        self._data = []
        self._width = 0
        self.extend(data)

    def _fill(self):
        width, filler = self._width, [None]
        if not width:
            return
        for d in self._data:
            rem = width - len(d)
            if rem > 0:
                d.extend(filler * rem)
        return

    def _set_width(self, reset=False):
        if reset:
            self._width = 0
        if self._width:
            return
        if self.headers:
            self._width = len(self.headers)
            return
        self._width = max([len(d) for d in self.data])

    def extend(self, data):
        if not data:
            return
        self._data.extend(data)
        self._set_width()
        self._fill()

    @classmethod
    def from_dict(cls, data, headers=_MISSING):
        if headers is _MISSING:
            try:
                headers, data = data.keys(), [data.values()]
            except (TypeError, AttributeError):
                raise TypeError('expected dict or Mapping, not %r'
                                % type(data))
        elif headers:
            data = [data.get(h, None) for h in headers]
        return cls(data=data, headers=headers)

    @classmethod
    def from_dicts(cls, data, headers=_MISSING):
        if headers is _MISSING:
            try:
                headers = data[0].keys()
            # TODO: support iterators?
            except IndexError:
                return cls()
            except (AttributeError, TypeError):
                raise TypeError('expected iterable of dicts')
        data = ([ci.get(h, None) for h in headers] for ci in data)
        return cls(data=data, headers=headers)

    def __len__(self):
        return len(self._data)

    def __getitem__(self, idx):
        return self._data[idx]

    def __repr__(self):
        cn = self.__class__.__name__
        if self.headers:
            return '%s(headers=%r, data=%r)' % (cn, self.headers, self._data)
        else:
            return '%s(%r)' % (cn, self._data)

    def to_html(self, orientation=None, wrapped=True,
                with_headers=True, with_newlines=True):
        lines = []
        if wrapped:
            lines.append('<table>')
        orientation = orientation or 'auto'
        ol = orientation[0].lower()
        if ol == 'a':
            ol = 'h' if len(self) > 1 else 'v'
        if ol == 'h':
            self._add_horizontal_html_lines(lines, with_headers=with_headers)
        elif ol == 'v':
            self._add_vertical_html_lines(lines, with_headers=with_headers)
        else:
            raise ValueError("expected one of 'auto', 'vertical', or"
                             " 'horizontal', not %r" % orientation)
        if wrapped:
            lines.append('</table>')
        sep = '\n' if with_newlines else ''
        return sep.join(lines)

    def _add_horizontal_html_lines(self, lines, with_headers):
        if with_headers:
            lines.append('<tr><th>' +
                         '</th><th>'.join([unicode(h) for h in self.headers]) +
                         '</th></tr>')
        for row in self._data:
            line = ''.join(['<tr><td>',
                            '</td><td>'.join([unicode(c) for c in row]),
                            '</td></tr>'])
            lines.append(line)

    def _add_vertical_html_lines(self, lines, with_headers):
        for i in range(self._width):
            line_parts = ['<tr>']
            if with_headers:
                line_parts.extend(['<th>', self.headers[i], '</th>'])
            _fill = '</td><td>'.join([unicode(row[i]) for row in self._data])
            line_parts.extend(['<td>', _fill, '</td>', '</tr>'])
            lines.append(''.join(line_parts))

    def to_text(self, with_headers=True):
        lines = []
        widths = []
        for idx in range(self._width):
            cur_widths = [len(unicode(cur[idx])) for cur in self._data]
            if with_headers:
                cur_widths.append(len(self.headers[idx]))
            widths.append(max(cur_widths))
        header_line = ' | '.join([h.center(widths[i]) for i, h in enumerate(self.headers)])
        lines.append(header_line)
        sep_line = '-+-'.join(['-' * w for w in widths])
        lines.append(sep_line)
        for row in self._data:
            lines.append(' | '.join([unicode(col).center(widths[j])
                                     for j, col in enumerate(row)]))
        return '\n'.join(lines)


def main():
    data_dicts = [{'id': 1, 'name': 'John Doe'},
                  {'id': 2, 'name': 'Dale Simmons'}]
    data_lists = [['id', 'name'],
                  [1, 'John Doe'],
                  [2, 'Dale Simmons']]
    t1 = Table(data_lists)
    t2 = Table.from_dict(data_dicts[0])
    t3 = Table.from_dicts(data_dicts)
    t3.extend([[3, 'Kurt Rose'], [4]])
    print t1
    print t2
    print t2.to_html()
    print t3
    print t3.to_html()
    print t3.to_text()
    import pdb;pdb.set_trace()


if __name__ == '__main__':
    main()
