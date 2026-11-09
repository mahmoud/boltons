from collections import namedtuple
from types import SimpleNamespace

import pytest

from boltons.tableutils import DictInputType, InputType, Table


def test_table_lists():
    data_lists = [['id', 'name'],
                  [1, 'John Doe'],
                  [2, 'Dale Simmons']]
    t1 = Table(data_lists)
    assert set(t1.headers) == {'id', 'name'}
    assert len(t1) == 2
    assert 'John Doe' in repr(t1)

T2_REF_HTML = """<table>
<tr><th>id</th><td>1</td></tr>
<tr><th>name</th><td>John Doe</td></tr>
</table>"""

T3_REF_HTML = """<table>
<thead>
<tr><th>id</th><th>name</th></tr>
</thead>
<tbody>
<tr><td>1</td><td>John Doe</td></tr>
<tr><td>2</td><td>Dale Simmons</td></tr>
<tr><td>3</td><td>Kurt Rose</td></tr>
<tr><td>4</td><td>None</td></tr>
</tbody>
</table>"""


def test_table_dicts():
    data_dicts = [{'id': 1, 'name': 'John Doe'},
                  {'id': 2, 'name': 'Dale Simmons'}]
    t2 = Table.from_dict(data_dicts[0])
    t3 = Table.from_dict(data_dicts)
    t3.extend([[3, 'Kurt Rose'], [4]])

    assert set(t2.headers) == {'id', 'name'}
    assert len(t2) == 1
    # the sorted() stuff handles ordering differences between versions
    # TODO: should maybe change Table to sort the headers of dicts and such?
    assert sorted(t2.to_html()) == sorted(T2_REF_HTML)
    assert sorted(t3.to_html()) == sorted(T3_REF_HTML)
    assert t3.to_text()


def test_table_obj():
    class TestType:
        def __init__(self):
            self.greeting = 'hi'

    t4 = Table.from_object(TestType())
    assert len(t4) == 1
    assert 'greeting' in t4.headers



def test_to_text_empty_table():
    # used to raise ValueError from max() over an empty sequence
    assert Table([[]]).to_text() == ''


def test_to_text_none_headers():
    # used to raise AttributeError calling .center() on a None header
    t = Table([[None, 'b'], [1, 2]])
    lines = t.to_text().splitlines()
    header_cells = [c.strip() for c in lines[0].split(' | ')]
    # None headers render the same as None data cells
    assert header_cells[0] == 'None'


def test_to_text_no_headers():
    # used to raise IndexError; empty headers mean no header row or
    # separator rule, same as to_html
    t = Table([[], [1]])
    assert t.headers == []
    assert t.to_text() == '1'


def test_to_text_short_headers_padded():
    # used to raise IndexError; non-empty headers shorter than the
    # table width get padded with None cells, same as to_html
    t = Table([[1, 2]], headers=[])
    t.headers = ['a']
    lines = t.to_text().splitlines()
    header_cells = [c.strip() for c in lines[0].split(' | ')]
    assert header_cells == ['a', 'None']


@pytest.mark.parametrize('factory, data, rows', [
    (Table.from_dict, {'b': 2, 'a': 1}, [[1, 2]]),
    (Table.from_dict, [{'b': 2, 'a': 1}, {'b': 4}], [[1, 2], [None, 4]]),
    (Table.from_data, namedtuple('Row', ['b', 'a'])(2, 1), [[2, 1]]),
    (Table.from_list, [[1, 2]], [[1, 2]]),
])
def test_headerless_factory_keeps_fields(factory, data, rows):
    table = factory(data, headers=None)

    assert table.headers == []
    assert list(table) == rows
    assert '<th>' not in table.to_html()
    assert len(table.to_text().splitlines()) == len(rows)


def test_headerless_factory_keeps_object_fields():
    data = SimpleNamespace(b=2, a=1)
    inferred = Table.from_object(data)
    table = Table.from_object(data, headers=None)

    assert table.headers == []
    assert list(table) == list(inferred)
    assert '<th>' not in table.to_html()


def test_headerless_factory_preserves_custom_adapter():
    class CustomInput(InputType):
        def get_entry(self, obj, headers):
            assert headers is None
            return [obj.value]

    data = SimpleNamespace(value=42)
    table = Table.from_data(data, headers=None, _data_type=CustomInput())
    assert table.headers == []
    assert list(table) == [[42]]


def test_headerless_factory_preserves_custom_dict_adapter_order():
    class ValuesInOrder(DictInputType):
        def get_entry(self, obj, headers):
            if headers is None:
                return list(obj.values())
            return super().get_entry(obj, headers)

    table = Table.from_data({'b': 2, 'a': 1}, headers=None, _data_type=ValuesInOrder())
    assert table.headers == []
    assert list(table) == [[2, 1]]


def test_factory_preserves_explicit_field_selection():
    table = Table.from_dict({'a': 1, 'b': 2}, headers=['b'])
    assert table.headers == ['b']
    assert list(table) == [[2]]


def test_iterator_headers():
    # see #561
    t = Table([[1, 2]], headers=iter(['a', 'b']))
    assert t.headers == ['a', 'b']
    assert t.to_text().splitlines()[0] == 'a | b'

    t = Table.from_data([[1, 2]], headers=iter(['a', 'b']))
    assert t.headers == ['a', 'b']
    assert t.to_text().splitlines()[-1] == '1 | 2'


def test_headerless_extend_wider_row():
    # see #497
    t = Table([[1]], headers=[])
    t.extend([[2, 3]])
    assert t.to_text().splitlines() == ['1 | None', '2 |  3  ']


def test_to_html_bottom_metadata_after_table():
    # see #558
    t = Table([[1, 2]], headers=['a', 'b'], metadata={'k': 'v'})
    html = t.to_html(with_metadata='bottom')
    main_close = html.index('</table>')
    assert main_close < html.index('<br />') < html.index('<th>k</th>')
    assert html.endswith('</table>')
    assert html.count('<table>') == html.count('</table>') == 2