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
        self._width = len(headers)
        self._data = []
        self.extend(data)

    def _fill(self, data):
        width, filler = self._width, [None]
        for d in data:
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

    @classmethod
    def from_dict(cls, data, headers=_MISSING):
        if headers is _MISSING:
            try:
                headers, data = data.keys(), data.values()
            except AttributeError:
                raise TypeError('expected Mapping, not %r' % type(obj))
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

    def __repr__(self):
        cn = self.__class__.__name__
        if self.headers:
            return '%s(headers=%r, data=%r)' % (cn, self.headers, self._data)
        else:
            return '%s(%r)' % (cn, self._data)



def main():
    data_dicts = [{'id': 1, 'name': 'John Doe'},
                  {'id': 2, 'name': 'Dale Simmons'}]
    data_lists = [['id', 'name'],
                  [1, 'John Doe'],
                  [2, 'Dale Simmons']]
    t1 = Table(data_lists)
    t2 = Table.from_dict(data_dicts[0])
    t3 = Table.from_dicts(data_dicts)
    print t1
    print t2
    print t3
    import pdb;pdb.set_trace()


if __name__ == '__main__':
    main()
