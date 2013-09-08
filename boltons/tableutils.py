# -*- coding: utf-8 -*-

from __future__ import unicode_literals


class SimpleTable(object):
    delimeter = ' | '

    def __init__(self, headers, data=()):
        self.widths = []
        self._headers = None
        self.headers = headers
        self.rows = []
        self.extend(data)
        self.row_labels = {}
        self._max_label = 0

    @property
    def headers(self):
        return self._headers

    @headers.setter
    def headers(self, headers):
        self._headers = headers
        self.widths = [len(h) for h in headers]

    def extend(self, rows):
        for row in rows:
            self.append(row)

    def append(self, row, label=None):
        header_len = len(self.headers)
        if len(row) != header_len:
            raise ValueError('row length {} disagrees '
                             'with header length '
                             '{}'.format(len(row), header_len))

        prepped = []
        for i, col in enumerate(row):
            col = unicode(col)
            self.widths[i] = max(self.widths[i], len(col))
            prepped.append(col)

        self.rows.append(prepped)
        if label is not None:
            self._max_label = max(len(label), self._max_label)
            self.row_labels[len(self.rows) - 1] = label

    def column_for_key(self, key):
        try:
            idx = self.headers.index(key)
        except ValueError:
            raise ValueError('unknown key {}'.format(key))

        return [row[idx] for row in self.rows]

    def row_for_key(self, key):
        for idx, k in self.row_labels.iteritems():
            if k == key:
                return self.rows[idx]
        else:
            raise ValueError('unknown key {}'.format(key))

    def __getitem__(self, idx):
        return self.rows[idx]

    def __repr__(self):
        cls = self.__class__.__name__
        return '{}({}, data={})'.format(cls, repr(self.headers),
                                        repr(self.rows))

    def _with_label(self, s, label=None, delimeter=None):
        if self._max_label:
            return '{}{}{}'.format(label or ' ' * self._max_label,
                                   delimeter or self.delimeter,
                                   s)
        return s

    def __unicode__(self):
        l = self._with_label
        formatted = []

        headers = ' | '.join(h.center(self.widths[i])
                           for i, h in enumerate(self.headers))

        formatted.append(l(headers, delimeter=' ' * len(self.delimeter)))
        formatted.append(l('-+-'.join('-' * w for w in self.widths)))

        for i, row in enumerate(self.rows):
            formatted.append(l(' | '.join(col.center(self.widths[j])
                                          for j, col in enumerate(row)),
                               label=self.row_labels.get(i)))


        return '\n'.join(formatted)


def test():
    table = [['1', '100000'],
             ['55', '5555555555']]

    st = SimpleTable(('a', 'b'), table)

    print unicode(st)
    print
    st.append([u'thing', u'5'], label='a test')
    print unicode(st)
    print
    print st.column_for_key('a')
    print st.row_for_key('a test')


if __name__ == '__main__':
    test()
