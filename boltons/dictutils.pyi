try:
    from collections.abc import ItemsView, KeysView, ValuesView
except ImportError:
    from collections import ItemsView, KeysView, ValuesView

from collections.abc import Callable, Generator, Hashable, Iterable, Iterator
from typing import Any, Never

class OrderedMultiDict(dict):
    def __init__(self, *args, **kwargs) -> None: ...
    def add(self, k: Hashable, v: Any) -> None: ...
    def addlist(self, k: Hashable, v: Any) -> None: ...
    def get(self, k: Hashable, default: Any | None = ...) -> Any: ...
    def getlist(self, k: Hashable, default=...) -> list[Any]: ...
    def clear(self) -> None: ...
    def setdefault(self, k: Hashable, default: Any = ...) -> Any: ...
    def copy(self) -> OrderedMultiDict: ...
    @classmethod
    def fromkeys(
        cls, keys: list[Any], default: Any | None = ...
    ) -> OrderedMultiDict: ...
    def update(self, E: dict[Any, Any] | Iterable, **F: dict[str, Any]) -> None: ...
    def update_extend(
        self, E: dict[Any, Any] | Iterable, **F: dict[str, Any]
    ) -> None: ...
    def __setitem__(self, k: Hashable, v: Any) -> None: ...
    def __getitem__(self, k: Hashable) -> Any: ...
    def __delitem__(self, k: Hashable) -> None: ...
    def __eq__(self, other: OrderedMultiDict) -> bool: ...
    def __ne__(self, other: OrderedMultiDict) -> bool: ...
    def pop(self, k: Hashable, default: Any = ...) -> None: ...
    def popall(self, k: Hashable, default: Any = ...) -> None: ...
    def poplast(self, k: Hashable = ..., default: Any = ...) -> None: ...
    def iteritems(self, multi: bool = ...) -> Generator[Any, None, None]: ...
    def iterkeys(self, multi: bool = ...) -> Generator[Any, None, None]: ...
    def itervalues(self, multi: bool = ...) -> Generator[Any, None, None]: ...
    def todict(self, multi: bool = ...) -> dict[Hashable, Any]: ...
    def sorted(
        self, key: Any | None = ..., reverse: bool = ...
    ) -> OrderedMultiDict: ...
    def sortedvalues(
        self, key: Any | None = ..., reverse: bool = ...
    ) -> OrderedMultiDict: ...
    def inverted(self) -> OrderedMultiDict: ...
    def counts(self) -> OrderedMultiDict: ...
    def keys(self, multi: bool = ...) -> list[Hashable]: ...
    def values(self, multi: bool = ...) -> list[Any]: ...
    def items(self, multi: bool = ...) -> list[Generator[Any, None, None]]: ...
    def __iter__(self) -> Generator[Any, None, None]: ...
    def __reversed__(self) -> Generator[Any, None, None]: ...
    def viewkeys(self) -> KeysView: ...
    def viewvalues(self) -> ValuesView: ...
    def viewitems(self) -> ItemsView: ...

OMD = OrderedMultiDict
MultiDict = OrderedMultiDict

class FastIterOrderedMultiDict(OrderedMultiDict):
    def iteritems(self, multi: bool = ...) -> Generator[Any, None, None]: ...
    def iterkeys(self, multi: bool = ...) -> Generator[Any, None, None]: ...
    def __reversed__(self) -> Generator[Any, None, None]: ...

class OneToOne(dict):
    inv: OneToOne
    def __init__(self, *a, **kw) -> None: ...
    @classmethod
    def unique(cls, *a, **kw): ...
    def __setitem__(self, key: Hashable, val: Hashable) -> None: ...
    def __delitem__(self, key: Hashable) -> None: ...
    def clear(self) -> None: ...
    def copy(self) -> OneToOne: ...
    def pop(self, key: Hashable, default: Any = ...) -> Hashable: ...
    def popitem(self) -> tuple[Hashable, Hashable]: ...
    def setdefault(self, key, default: Any = ...) -> Hashable: ...
    def update(
        self, dict_or_iterable: dict | Iterable, **kw: dict[Hashable, Any]
    ) -> None: ...

class ManyToMany:
    data: dict[Hashable, Any]
    inv: ManyToMany
    def __init__(self, items: tuple[Hashable] | dict[Hashable, Any] = ...) -> None: ...
    def get(self, key: Hashable, default: Any = ...) -> Any: ...
    def __getitem__(self, key: Hashable) -> Any: ...
    def __setitem__(self, key: Hashable, vals: Iterable) -> None: ...
    def __delitem__(self, key: Hashable) -> None: ...
    def update(self, iterable: Iterable) -> None: ...
    def add(self, key: Hashable, val: Any) -> None: ...
    def remove(self, key: Hashable, val: Any) -> None: ...
    def replace(self, key: Hashable, newkey: Hashable) -> None: ...
    def iteritems(self) -> Generator[Hashable, Any]: ...
    def keys(self) -> Iterable[Hashable]: ...
    def __contains__(self, key: Hashable) -> bool: ...
    def __iter__(self) -> Iterator: ...
    def __len__(self) -> int: ...
    def __eq__(self, other) -> bool: ...

def subdict(
    d, keep: dict[Hashable, Any] | None = ..., drop: list[Hashable] | None = ...
): ...

class FrozenHashError(TypeError): ...

class FrozenDict(dict):
    def updated(self, *a, **kw): ...
    @classmethod
    def fromkeys(cls, keys: Iterable | None, value: Any | None = ...): ...
    def __reduce_ex__(self, protocol): ...
    def __hash__(self) -> int: ...
    def __copy__(self) -> FrozenDict: ...
    __ior__: Callable[[Any], Never]
    __setitem__: Callable[[Any], Never]
    __delitem__: Callable[[Any], Never]
    update: Callable[[Any], Never]
    setdefault: Callable[[Any], Never]
    pop: Callable[[Any], Never]
    popitem: Callable[[Any], Never]
    clear: Callable[[Any], Never]
