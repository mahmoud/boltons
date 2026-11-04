from boltons.typeutils import get_all_subclasses


def test_unhashable_classes_in_diamond_are_returned_once():
    class Meta(type):
        __hash__ = None

    class Root(metaclass=Meta):
        pass

    class Left(Root):
        pass

    class Right(Root):
        pass

    class Leaf(Left, Right):
        pass

    assert list(map(id, get_all_subclasses(Root))) == list(map(id, [Left, Right, Leaf]))


def test_distinct_equal_classes_are_returned():
    class Meta(type):
        def __eq__(self, other):
            return isinstance(other, Meta)

        def __hash__(self):
            return 0

    class Root(metaclass=Meta):
        pass

    class Left(Root):
        pass

    class Right(Root):
        pass

    assert Left == Right
    assert list(map(id, get_all_subclasses(Root))) == list(map(id, [Left, Right]))
