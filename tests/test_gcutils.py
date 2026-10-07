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


if '__pypy__' not in sys.builtin_module_names:
    def test_get_all_includes_subtype_instances():
        class Base:
            pass

        class Child(Base):
            pass

        class Grandchild(Child):
            pass

        base, child, grandchild = Base(), Child(), Grandchild()
        assert set(get_all(Base)) == {base, child, grandchild}
        assert set(get_all(Child)) == {child, grandchild}
        assert get_all(Base, include_subtypes=False) == [base]
        assert get_all(Child, include_subtypes=False) == [child]
