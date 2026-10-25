import gc
import sys
import time


if '__pypy__' not in sys.builtin_module_names:
    # pypy's gc really is different

    from boltons.gcutils import (get_all, toggle_gc, toggle_gc_postcollect,
                                 GCToggler)

    def test_get_all():
        class TestType:
            pass

        tt = TestType()

        assert len(get_all(TestType)) == 1
        assert len(get_all(bool)) == 0
        return

    def test_get_all_subtypes():
        class Base:
            pass

        class Sub(Base):
            pass

        sub = Sub()

        assert get_all(Base) == [sub]
        assert get_all(Base, include_subtypes=False) == []

    def test_toggle_gc_restores_state():
        was_enabled = gc.isenabled()
        try:
            gc.disable()
            with toggle_gc:
                pass
            assert not gc.isenabled()

            gc.enable()
            toggler = GCToggler()
            with toggler:
                with toggler:
                    pass
                assert not gc.isenabled()
            assert gc.isenabled()
        finally:
            if was_enabled:
                gc.enable()
            else:
                gc.disable()

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
