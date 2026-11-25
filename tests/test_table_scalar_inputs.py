import pytest

from boltons.tableutils import Table


@pytest.mark.parametrize('value', [42, 3.5, False, None, 'hello', '', b'hello'])
def test_scalar_factory_preserves_a_data_cell(value):
    table = Table.from_data(value)
    assert table.headers == []
    assert len(table) == 1
    assert table[0] == [value]
    assert table.to_text() == str(value)


def test_scalar_factory_keeps_explicit_header():
    table = Table.from_data(42, headers=['answer'])
    assert table.headers == ['answer']
    assert table[0] == [42]


def test_scalar_sequence_remains_a_single_row():
    table = Table.from_data([1, 2])
    assert table.headers == []
    assert table[0] == [1, 2]
