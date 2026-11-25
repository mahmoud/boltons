from boltons.tableutils import Table


def test_mapping_with_mixed_key_types():
    table = Table.from_dict({'name': 'Ada', 1: 'first'})
    assert table.headers == ['name', 1]
    assert table[0] == ['Ada', 'first']
    assert 'Ada' in table.to_text()


def test_mixed_key_order_is_shared_by_rows():
    table = Table.from_data([{'name': 'Ada', 1: 'first'}, {1: 'second', 'name': 'Grace'}])
    assert table.headers == ['name', 1]
    assert table[0] == ['Ada', 'first']
    assert table[1] == ['Grace', 'second']


def test_comparable_mapping_keys_remain_sorted():
    table = Table.from_dict({'z': 1, 'a': 2})
    assert table.headers == ['a', 'z']
    assert table[0] == [2, 1]
