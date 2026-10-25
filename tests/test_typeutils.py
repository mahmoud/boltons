import copy
import pickle

from boltons.typeutils import make_sentinel, get_all_subclasses

NOT_SET = make_sentinel('not_set', var_name='NOT_SET')

def test_sentinel_falsiness():
    assert not NOT_SET


def test_sentinel_pickle():
    assert pickle.dumps(NOT_SET)

def test_sentinel_copy():
    test = make_sentinel('test')
    assert test is copy.copy(test)
    assert test is copy.deepcopy(test)


def test_get_all_subclasses_metaclass():
    class Meta(type):
        pass

    class SubMeta(Meta):
        pass

    assert get_all_subclasses(Meta) == [SubMeta]
    assert get_all_subclasses(SubMeta) == []
