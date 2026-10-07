import sys
import time


if '__pypy__' not in sys.builtin_module_names:
    # pypy's gc really is different

    from boltons.gcutils import get_all, toggle_gc_postcollect

    def test_get_all():
        class TestType:
            pass

        tt = TestType()

        assert len(get_all(TestType)) == 1
        assert len(get_all(bool)) == 0
        return

    def test_toggle_gc_postcollect():
        COUNT = int(1e6)

        start = time.time()
        with toggle_gc_postcollect:
            x = [{} for x in range(COUNT)]
        no_gc_time = time.time() - start

        start = time.time()
        x = [{} for x in range(COUNT)]
        with_gc_time = time.time() - start

        time_diff = no_gc_time < with_gc_time


def test_gc_context_restores_state_and_supports_nesting():
    import gc
    from boltons.gcutils import GCToggler

    was_enabled = gc.isenabled()
    try:
        for initial_state in (True, False):
            (gc.enable if initial_state else gc.disable)()
            toggler = GCToggler()
            with toggler:
                assert not gc.isenabled()
                with toggler:
                    assert not gc.isenabled()
                assert not gc.isenabled()
            assert gc.isenabled() == initial_state
    finally:
        (gc.enable if was_enabled else gc.disable)()


def test_gc_context_restores_state_after_exception():
    import gc
    import pytest
    from boltons.gcutils import GCToggler

    was_enabled = gc.isenabled()
    try:
        gc.disable()
        with pytest.raises(ValueError):
            with GCToggler():
                raise ValueError('test')
        assert not gc.isenabled()
    finally:
        (gc.enable if was_enabled else gc.disable)()
