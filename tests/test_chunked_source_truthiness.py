import pytest

from boltons.iterutils import chunked, chunked_filter, chunked_iter


class FalseyList(list):
    def __bool__(self):
        return False


class AmbiguousList(list):
    def __bool__(self):
        raise ValueError('truth value is ambiguous')


class OneShotIterable:
    def __init__(self, values):
        self.iterator = iter(values)

    def __iter__(self):
        return self

    def __next__(self):
        return next(self.iterator)

    def __bool__(self):
        raise AssertionError('iteration must not require a truth value')


@pytest.mark.parametrize('factory', [
    FalseyList, AmbiguousList, OneShotIterable,
])
@pytest.mark.parametrize('values', [[], [0], [0, 1, 2, 3, 4]])
@pytest.mark.parametrize('func', [chunked, chunked_iter])
@pytest.mark.parametrize('fill', [False, True])
def test_chunking_depends_on_iteration(factory, values, func, fill):
    kwargs = {'fill': None} if fill else {}
    expected = [values[i:i + 2] for i in range(0, len(values), 2)]
    if fill and expected and len(expected[-1]) == 1:
        expected[-1].append(None)
    assert list(func(factory(values), 2, **kwargs)) == expected


@pytest.mark.parametrize('factory', [
    FalseyList, AmbiguousList, OneShotIterable,
])
@pytest.mark.parametrize('values', [[], [0], [0, 1, 2, 3, 4]])
def test_batch_filter_uses_the_same_iterable_contract(factory, values):
    batches = []

    def keep(batch):
        batches.append(list(batch))
        return [True] * len(batch)

    assert list(chunked_filter(factory(values), 2, key=keep)) == values
    assert batches == [values[i:i + 2] for i in range(0, len(values), 2)]


@pytest.mark.parametrize('source', ['', b'', [], iter([])])
def test_empty_sources_remain_empty(source):
    assert list(chunked_iter(source, 2, fill=None)) == []


@pytest.mark.parametrize('source, expected', [
    ('abcde', ['ab', 'cd', 'e']),
    (b'abcde', [b'ab', b'cd', b'e']),
])
def test_string_and_byte_chunks_keep_their_type(source, expected):
    assert chunked(source, 2) == expected
