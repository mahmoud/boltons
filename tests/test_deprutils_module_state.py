import importlib
import sys

import pytest

from boltons.deprutils import deprecate_module_member


def test_deprecated_member_preserves_module_globals(tmp_path, monkeypatch):
    name = 'boltons_test_legacy_counter'
    monkeypatch.delitem(sys.modules, name, raising=False)
    monkeypatch.syspath_prepend(str(tmp_path))
    (tmp_path / (name + '.py')).write_text(
        "from boltons.deprutils import deprecate_module_member\n"
        "count = 0\n"
        "old_name = 42\n"
        "def increment():\n"
        "    global count\n"
        "    count += 1\n"
        "    return count\n"
        "deprecate_module_member(__name__, 'old_name', 'use new_name')\n"
        "new_name = 42\n",
        encoding='utf-8',
    )
    try:
        module = importlib.import_module(name)
        assert module.increment() == module.count == 1
        module.count = 10
        assert module.increment() == module.count == 11
        assert module.new_name == 42
        with pytest.warns(DeprecationWarning, match='use new_name'):
            assert module.old_name == 42
        deprecate_module_member(name, 'new_name', 'use replacement')
        assert sys.modules[name] is module
        with pytest.warns(DeprecationWarning, match='use replacement'):
            assert module.new_name == 42
    finally:
        sys.modules.pop(name, None)
