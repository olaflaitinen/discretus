# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

"""Lazy evaluation helpers.

Several structures in the library are conceptually infinite, for example the
sequence of prime numbers or the sequence of Catalan numbers. The wrappers
here expose such a sequence as an indexable object that computes and caches
only the terms that are actually requested.
"""

from __future__ import annotations

import contextlib
from typing import Any, Callable, Dict, Generic, Iterator, List, Optional, TypeVar

from ..exceptions import DomainError

__all__ = ["cached_property", "LazySequence", "LazyMapping", "memoized_recursion"]

T = TypeVar("T")
K = TypeVar("K")
V = TypeVar("V")


class cached_property(Generic[T]):  # noqa: N801
    """A read only property computed once per instance.

    The value is stored in the instance dictionary under the property name,
    so later reads cost a dictionary lookup. Instances without a dictionary,
    such as classes using ``__slots__``, recompute on every access.

    Example:
        >>> class Counter:
        ...     calls = 0
        ...     @cached_property
        ...     def value(self) -> int:
        ...         Counter.calls += 1
        ...         return 42
        >>> counter = Counter()
        >>> counter.value, counter.value, Counter.calls
        (42, 42, 1)
    """

    def __init__(self, function: Callable[[Any], T]) -> None:
        self.function = function
        self.__doc__ = function.__doc__
        self.name = function.__name__

    def __set_name__(self, owner: type, name: str) -> None:
        self.name = name

    def __get__(self, instance: Any, owner: Optional[type] = None) -> Any:
        if instance is None:
            return self
        value = self.function(instance)
        # An instance without a mutable attribute dictionary, one using
        # slots for example, cannot cache the value. That is not an error:
        # the property still works, it is simply recomputed each time.
        with contextlib.suppress(AttributeError):
            instance.__dict__[self.name] = value
        return value


class LazySequence(Generic[T]):
    """An indexable sequence whose terms are produced on demand.

    Args:
        generator: A function from a zero based index to the term.
        length: Number of terms, or ``None`` for a conceptually infinite
            sequence.

    Example:
        >>> squares = LazySequence(lambda n: n * n)
        >>> squares[4]
        16
        >>> list(squares.prefix(5))
        [0, 1, 4, 9, 16]
        >>> len(LazySequence(lambda n: n, length=3))
        3
    """

    def __init__(
        self,
        generator: Callable[[int], T],
        length: Optional[int] = None,
    ) -> None:
        if length is not None and length < 0:
            raise DomainError(f"length must be non negative, got {length}")
        self._generator = generator
        self._length = length
        self._cache: Dict[int, T] = {}

    @property
    def length(self) -> Optional[int]:
        """Return the number of terms, or ``None`` when unbounded."""
        return self._length

    def __getitem__(self, index: int) -> T:
        if index < 0:
            if self._length is None:
                raise DomainError("negative indices need a finite length")
            index += self._length
        if index < 0 or (self._length is not None and index >= self._length):
            raise IndexError(f"index {index} is out of range")
        if index not in self._cache:
            self._cache[index] = self._generator(index)
        return self._cache[index]

    def prefix(self, count: int) -> List[T]:
        """Return the first ``count`` terms."""
        if count < 0:
            raise DomainError(f"count must be non negative, got {count}")
        return [self[index] for index in range(count)]

    def __iter__(self) -> Iterator[T]:
        index = 0
        while self._length is None or index < self._length:
            yield self[index]
            index += 1

    def __len__(self) -> int:
        if self._length is None:
            raise DomainError("an unbounded lazy sequence has no length")
        return self._length

    def cached(self) -> Dict[int, T]:
        """Return a copy of the terms computed so far."""
        return dict(self._cache)

    def __repr__(self) -> str:
        shown = ", ".join(
            repr(self[index]) for index in range(min(5, self._length or 5))
        )
        tail = "..." if self._length is None or self._length > 5 else ""
        return f"LazySequence([{shown}{', ' + tail if tail else ''}])"


class LazyMapping(Generic[K, V]):
    """A read only mapping whose values are computed on first access.

    Example:
        >>> doubles = LazyMapping(lambda key: key * 2)
        >>> doubles[21]
        42
        >>> 21 in doubles.cached()
        True
    """

    def __init__(self, function: Callable[[K], V]) -> None:
        self._function = function
        self._cache: Dict[K, V] = {}

    def __getitem__(self, key: K) -> V:
        if key not in self._cache:
            self._cache[key] = self._function(key)
        return self._cache[key]

    def get(self, key: K) -> V:
        """Return the value for a key, computing it when needed."""
        return self[key]

    def cached(self) -> Dict[K, V]:
        """Return a copy of the values computed so far."""
        return dict(self._cache)

    def clear(self) -> None:
        """Discard every cached value."""
        self._cache.clear()

    def __repr__(self) -> str:
        return f"LazyMapping(cached={len(self._cache)})"


def memoized_recursion(function: Callable[..., T]) -> Callable[..., T]:
    """Memoize a recursive function on its positional arguments.

    Unlike :func:`functools.lru_cache` the cache is unbounded, which suits
    the recurrences in this library where the argument space is small and
    every value is reused.

    Example:
        >>> @memoized_recursion
        ... def fib(n: int) -> int:
        ...     return n if n < 2 else fib(n - 1) + fib(n - 2)
        >>> fib(60)
        1548008755920
    """
    cache: Dict[Any, T] = {}

    def wrapper(*args: Any) -> T:
        if args not in cache:
            cache[args] = function(*args)
        return cache[args]

    wrapper.__name__ = function.__name__
    wrapper.__doc__ = function.__doc__
    wrapper.cache = cache  # type: ignore[attr-defined]
    return wrapper
