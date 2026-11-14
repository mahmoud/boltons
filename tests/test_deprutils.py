import sys
from types import ModuleType

import pytest

from boltons.deprutils import deprecate_module_member


def test_deprecating_a_member_preserves_module_globals(monkeypatch):
    module = ModuleType('legacy_counter')
    monkeypatch.setitem(sys.modules, module.__name__, module)
    exec(
        'count = 0\n'
        'def increment():\n'
        '    global count\n'
        '    count += 1\n'
        '    return count\n',
        vars(module),
    )
    module.old_name = 42

    deprecate_module_member(module.__name__, 'old_name', 'use new_name')
    imported_module = sys.modules[module.__name__]

    assert imported_module.increment() == 1
    assert imported_module.count == 1
    imported_module.count = 10
    assert imported_module.increment() == 11
    assert imported_module is module

    with pytest.warns(DeprecationWarning, match='use new_name'):
        assert imported_module.old_name == 42


def test_deprecating_members_on_a_module_subclass(monkeypatch):
    class CustomModule(ModuleType):
        __slots__ = ('marker',)

    module = CustomModule('custom_module')
    module.marker = 'preserved'
    module.old_name = 42
    module.second_old_name = 43
    monkeypatch.setitem(sys.modules, module.__name__, module)

    deprecate_module_member(module.__name__, 'old_name', 'first warning')
    deprecate_module_member(module.__name__, 'second_old_name', 'second warning')

    assert sys.modules[module.__name__] is module
    assert isinstance(module, CustomModule)
    assert module.marker == 'preserved'
    with pytest.warns(DeprecationWarning, match='first warning'):
        assert module.old_name == 42
    with pytest.warns(DeprecationWarning, match='second warning'):
        assert module.second_old_name == 43
