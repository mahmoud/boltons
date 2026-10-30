import pytest

from boltons.funcutils import CachedInstancePartial, InstancePartial


@pytest.mark.parametrize("partial_type", [InstancePartial, CachedInstancePartial])
def test_partial_can_be_accessed_through_class(partial_type):
    class Greeter:
        def greet(self, greeting, punctuation="!"):
            return greeting + self.name + punctuation

        hello = partial_type(greet, punctuation=".")

        def __init__(self, name):
            self.name = name

    descriptor = vars(Greeter)["hello"]
    instance = Greeter("Ada")
    assert Greeter.hello is descriptor
    assert Greeter.hello(instance, "Hello ") == "Hello Ada."
    assert instance.hello("Hi ") == "Hi Ada."
    if partial_type is CachedInstancePartial:
        assert instance.hello is instance.hello
    assert Greeter.hello is descriptor


@pytest.mark.parametrize("partial_type", [InstancePartial, CachedInstancePartial])
def test_partial_class_access_through_subclass(partial_type):
    class Parent:
        def greet(self, punctuation="!"):
            return self.name + punctuation

        hello = partial_type(greet, punctuation=".")

    class Child(Parent):
        name = "child"

    child = Child()
    assert Child.hello is vars(Parent)["hello"]
    assert Child.hello(child) == "child."
    assert child.hello() == "child."
