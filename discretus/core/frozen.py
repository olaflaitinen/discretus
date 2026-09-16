"""Immutability helpers.

Value types in the library do not mutate after construction. The mixin and
the mapping in this module make that guarantee enforceable instead of merely
documented.
"""

from __future__ import annotations

from typing import Any, Dict, Hashable, Iterator, Mapping, Optional, Tuple, TypeVar

from ..exceptions import StructureError

__all__ = ["FrozenMixin", "FrozenDict", "freeze"]

K = TypeVar("K", bound=Hashable)
V = TypeVar("V")


class FrozenMixin:
    """Reject attribute assignment after construction.

    A subclass sets its attributes through :meth:`_initialize` inside its
    own ``__init__`` and is immutable from then on.

    Example:
        >>> class Point(FrozenMixin):
        ...     def __init__(self, x: int, y: int) -> None:
        ...         self._initialize(x=x, y=y)
        >>> p = Point(1, 2)
        >>> p.x
        1
        >>> p.x = 5
        Traceback (most recent call last):
        ...
        discretus.exceptions.StructureError: Point is immutable; attribute 'x' cannot be reassigned
    """

    __frozen__ = False

    def _initialize(self, **attributes: Any) -> None:
        """Set the attributes once and freeze the instance."""
        for name, value in attributes.items():
            object.__setattr__(self, name, value)
        object.__setattr__(self, "__frozen__", True)

    def __setattr__(self, name: str, value: Any) -> None:
        if getattr(self, "__frozen__", False):
            raise StructureError(
                f"{type(self).__name__} is immutable; "
                f"attribute {name!r} cannot be reassigned"
            )
        object.__setattr__(self, name, value)

    def __delattr__(self, name: str) -> None:
        raise StructureError(
            f"{type(self).__name__} is immutable; attribute {name!r} cannot be deleted"
        )


class FrozenDict(Mapping[K, V]):
    """A hashable, read only mapping with deterministic iteration order.

    Keys are visited in insertion order, and the hash depends only on the
    key and value pairs, so two mappings built in different orders are equal
    and hash alike.

    Example:
        >>> table = FrozenDict({"a": 1, "b": 2})
        >>> table["a"], len(table)
        (1, 2)
        >>> table == FrozenDict({"b": 2, "a": 1})
        True
    """

    __slots__ = ("_data", "_hash")

    def __init__(self, data: Optional[Mapping[K, V]] = None, **extra: Any) -> None:
        merged: Dict[K, V] = dict(data or {})
        merged.update(extra)  # type: ignore[arg-type]
        self._data: Dict[K, V] = merged
        self._hash: Optional[int] = None

    def __getitem__(self, key: K) -> V:
        return self._data[key]

    def __iter__(self) -> Iterator[K]:
        return iter(self._data)

    def __len__(self) -> int:
        return len(self._data)

    def __eq__(self, other: object) -> bool:
        if isinstance(other, FrozenDict):
            return self._data == other._data
        if isinstance(other, Mapping):
            return self._data == dict(other)
        return NotImplemented

    def __hash__(self) -> int:
        if self._hash is None:
            self._hash = hash(frozenset(self._data.items()))
        return self._hash

    def with_entry(self, key: K, value: V) -> "FrozenDict[K, V]":
        """Return a copy with one entry added or replaced."""
        updated = dict(self._data)
        updated[key] = value
        return FrozenDict(updated)

    def without(self, key: K) -> "FrozenDict[K, V]":
        """Return a copy with one key removed, if it is present."""
        updated = dict(self._data)
        updated.pop(key, None)
        return FrozenDict(updated)

    def to_dict(self) -> Dict[K, V]:
        """Return a mutable copy of the mapping."""
        return dict(self._data)

    def __repr__(self) -> str:
        inner = ", ".join(f"{key!r}: {value!r}" for key, value in self._data.items())
        return "FrozenDict({" + inner + "})"


def freeze(value: Any) -> Any:
    """Return an immutable, hashable counterpart of a container.

    Example:
        >>> freeze([1, [2, 3]])
        (1, (2, 3))
        >>> freeze({"a": [1]})
        FrozenDict({'a': (1,)})
    """
    if isinstance(value, (list, tuple)):
        return tuple(freeze(item) for item in value)
    if isinstance(value, (set, frozenset)):
        return frozenset(freeze(item) for item in value)
    if isinstance(value, Mapping):
        return FrozenDict({key: freeze(item) for key, item in value.items()})
    return value
