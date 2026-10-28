from collections import namedtuple

from pytest import raises

from boltons.debugutils import wrap_trace


def test_trace_dict():
    target = {}
    wrapped = wrap_trace(target)

    assert target is not wrapped
    assert isinstance(wrapped, dict)

    wrapped['a'] = 'A'
    assert target['a'] == 'A'
    assert len(wrapped) == len(target)

    wrapped.pop('a')
    assert 'a' not in target

    with raises(AttributeError):
        wrapped.nonexistent_attr = 'nope'

    return


def test_trace_bytes():
    target = b'Hello'

    wrapped = wrap_trace(target)

    assert target is not wrapped
    assert isinstance(wrapped, bytes)

    assert len(wrapped) == len(target)
    assert wrapped.decode('utf-8') == 'Hello'
    assert wrapped.lower() == target.lower()


def test_trace_exc():
    class TestException(Exception):
        pass

    target = TestException('exceptions can be a good thing')
    wrapped = wrap_trace(target)

    try:
        raise wrapped
    except TestException as te:
        assert te.args == target.args


def test_trace_raise_suppressed():
    class Target:
        def boom(self):
            raise ValueError('boom')

    wrapped = wrap_trace(Target(), hook=lambda **kw: True, events='raise')
    assert wrapped.boom() is None


def test_trace_which():
    class Config:
        def __init__(self, value):
            self.value = value

    config = Config('first')
    wrapped = wrap_trace(config, which='__setattr__')

    wrapped.value = 'second'
    assert config.value == 'second'


def test_trace_falsey_callable_which():
    class Target:
        def selected(self):
            pass

        def skipped(self):
            pass

    class FalseySelector:
        def __bool__(self):
            return False

        def __call__(self, name, value):
            return name == 'selected'

    calls = []

    def hook(**event):
        calls.append(event['attr_name'])

    wrapped = wrap_trace(Target(), hook=hook, which=FalseySelector(),
                         events='call')
    wrapped.selected()
    wrapped.skipped()
    assert calls == ['selected']


def test_trace_namedtuple():
    TargetType = namedtuple('TargetType', 'x y z')
    target = TargetType(1, 2, 3)

    wrapped = wrap_trace(target)

    assert wrapped == (1, 2, 3)


def test_trace_oldstyle():
    class Oldie:
        test = object()

        def get_test(self):
            return self.test

    oldie = Oldie()

    wrapped = wrap_trace(oldie)
    assert wrapped.get_test() is oldie.test

    return
