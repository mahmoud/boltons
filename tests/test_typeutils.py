
from boltons.typeutils import make_sentinel


def test_sentinel_falsiness():
    not_set = make_sentinel('not_set')
    assert not not_set
