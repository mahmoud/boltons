
import sys
import types
import warnings

import pytest

from boltons.deprutils import DeprecatableModule, deprecate_module_member


@pytest.fixture
def fake_module():
    name = "_boltons_fake_dep_module"
    mod = types.ModuleType(name)
    mod.old = 1
    mod.new = 2
    sys.modules[name] = mod
    try:
        yield name
    finally:
        sys.modules.pop(name, None)


def test_deprecate_wraps_the_module_in_place(fake_module):
    deprecate_module_member(fake_module, "old", "old is gone")
    assert isinstance(sys.modules[fake_module], DeprecatableModule)


def test_accessing_deprecated_member_warns(fake_module):
    deprecate_module_member(fake_module, "old", "old is gone, use new")
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        value = sys.modules[fake_module].old
    assert value == 1
    assert len(caught) == 1
    assert issubclass(caught[0].category, DeprecationWarning)
    assert "old is gone, use new" in str(caught[0].message)


def test_accessing_a_live_member_does_not_warn(fake_module):
    deprecate_module_member(fake_module, "old", "old is gone")
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        value = sys.modules[fake_module].new
    assert value == 2
    assert caught == []


def test_second_deprecation_reuses_the_same_wrapper(fake_module):
    deprecate_module_member(fake_module, "old", "old is gone")
    wrapper = sys.modules[fake_module]
    # A subsequent call must not re-wrap an already-wrapped module.
    deprecate_module_member(fake_module, "new", "new is gone too")
    assert sys.modules[fake_module] is wrapper
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        _ = sys.modules[fake_module].new
    assert len(caught) == 1


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, "-v"]))
