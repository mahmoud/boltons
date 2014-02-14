# -*- coding: utf-8 -*-


from itertools import islice


_MISSING = object()


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


class Table(object):
    def __init__(self, data, headers=_MISSING):
        if headers is _MISSING:
            headers, data = _guess_headers(data)
        self.headers = headers
        self._data = []
        self.extend(data)

    def list_append(self, item_list):
        self._data.append(item)

    def list_extend(self, item_lists):
        self._data.extend(list(items))

    def dict_append(self, item_dict):
        if self.headers is None:
            self._data.append([ci.get(ch, None) for ch in self.headers])


def main():
    data = [{'id': 1, 'name': 'John Doe'},
            {'id': 2, 'name': 'Dale Simmons'}]
    data_lists = [['id', 'name'],
                  [1, 'John Doe'],
                  [2, 'Dale Simmons']]
    t1 = Table(data)
    t2 = Table(data_lists)
    print t1._data == t2._data


if __name__ == '__main__':
    main()
