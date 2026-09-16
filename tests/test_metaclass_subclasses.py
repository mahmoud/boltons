from boltons.typeutils import get_all_subclasses


def test_subclass_traversal_supports_metaclasses():
    class Meta(type):
        pass
    class ChildMeta(Meta):
        pass
    descendants = get_all_subclasses(type)
    assert Meta in descendants
    assert ChildMeta in descendants
    assert descendants.count(ChildMeta) == 1


def test_subclass_traversal_supports_object_root():
    class Sample:
        pass
    descendants = get_all_subclasses(object)
    assert type in descendants
    assert Sample in descendants
