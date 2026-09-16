"""Iteration helpers used by the lazy generators across the library.

The helpers never materialize their input unless the documentation says so,
which is what lets the combinatorial generators iterate over spaces far too
large to hold in memory.
"""

from __future__ import annotations

from itertools import islice
from typing import (
    Any,
    Callable,
    Iterable,
    Iterator,
    List,
    Optional,
    Tuple,
    TypeVar,
)

from ..exceptions import DomainError
from .comparators import universal_key

__all__ = [
    "take",
    "drop",
    "first",
    "nth",
    "chunked",
    "windowed",
    "pairwise",
    "unique",
    "interleave",
    "count_items",
    "exhaust",
    "repeat_apply",
    "sorted_unique",
]

T = TypeVar("T")


def take(iterable: Iterable[T], count: int) -> List[T]:
    """Return the first ``count`` items as a list.

    Example:
        >>> take(range(10), 3)
        [0, 1, 2]
    """
    if count < 0:
        raise DomainError(f"count must be non negative, got {count}")
    return list(islice(iterable, count))


def drop(iterable: Iterable[T], count: int) -> Iterator[T]:
    """Return an iterator over the items after the first ``count``.

    Example:
        >>> list(drop(range(5), 3))
        [3, 4]
    """
    if count < 0:
        raise DomainError(f"count must be non negative, got {count}")
    return islice(iter(iterable), count, None)


def first(iterable: Iterable[T], default: Optional[T] = None) -> Optional[T]:
    """Return the first item, or ``default`` when the iterable is empty.

    Example:
        >>> first([7, 8]), first([], default=-1)
        (7, -1)
    """
    for item in iterable:
        return item
    return default


def nth(iterable: Iterable[T], index: int) -> T:
    """Return the item at a zero based index.

    Raises:
        DomainError: When the index is negative or beyond the end.

    Example:
        >>> nth("abc", 1)
        'b'
    """
    if index < 0:
        raise DomainError(f"index must be non negative, got {index}")
    for position, item in enumerate(iterable):
        if position == index:
            return item
    raise DomainError(f"index {index} is beyond the end of the iterable")


def chunked(iterable: Iterable[T], size: int) -> Iterator[Tuple[T, ...]]:
    """Yield consecutive tuples of at most ``size`` items.

    The final chunk is shorter when the length is not a multiple of the size.

    Example:
        >>> list(chunked(range(5), 2))
        [(0, 1), (2, 3), (4,)]
    """
    if size < 1:
        raise DomainError(f"size must be positive, got {size}")
    iterator = iter(iterable)
    while True:
        chunk = tuple(islice(iterator, size))
        if not chunk:
            return
        yield chunk


def windowed(iterable: Iterable[T], size: int) -> Iterator[Tuple[T, ...]]:
    """Yield overlapping windows of exactly ``size`` items.

    Example:
        >>> list(windowed(range(4), 2))
        [(0, 1), (1, 2), (2, 3)]
    """
    if size < 1:
        raise DomainError(f"size must be positive, got {size}")
    window: List[T] = []
    for item in iterable:
        window.append(item)
        if len(window) == size:
            yield tuple(window)
            window.pop(0)


def pairwise(iterable: Iterable[T]) -> Iterator[Tuple[T, T]]:
    """Yield consecutive overlapping pairs.

    Example:
        >>> list(pairwise([1, 2, 3]))
        [(1, 2), (2, 3)]
    """
    for window in windowed(iterable, 2):
        yield (window[0], window[1])


def unique(iterable: Iterable[T], key: Optional[Callable[[T], Any]] = None) -> Iterator[T]:
    """Yield the items in order, skipping later duplicates.

    Example:
        >>> list(unique([1, 2, 1, 3]))
        [1, 2, 3]
        >>> list(unique(["a", "A", "b"], key=str.lower))
        ['a', 'b']
    """
    seen = set()
    for item in iterable:
        marker = key(item) if key is not None else item
        if marker in seen:
            continue
        seen.add(marker)
        yield item


def interleave(*iterables: Iterable[T]) -> Iterator[T]:
    """Yield one item from each iterable in turn until all are exhausted.

    Example:
        >>> list(interleave([1, 3, 5], [2, 4]))
        [1, 2, 3, 4, 5]
    """
    iterators = [iter(iterable) for iterable in iterables]
    while iterators:
        remaining = []
        for iterator in iterators:
            try:
                yield next(iterator)
            except StopIteration:
                continue
            remaining.append(iterator)
        iterators = remaining


def count_items(iterable: Iterable[Any]) -> int:
    """Return the number of items, consuming the iterable.

    Example:
        >>> count_items(iter([1, 2, 3]))
        3
    """
    return sum(1 for _ in iterable)


def exhaust(iterator: Iterable[Any]) -> None:
    """Consume an iterable for its side effects and discard the items."""
    for _ in iterator:
        pass


def repeat_apply(function: Callable[[T], T], start: T, times: int) -> T:
    """Return the result of applying a function ``times`` times.

    Example:
        >>> repeat_apply(lambda n: n * 2, 1, 5)
        32
    """
    if times < 0:
        raise DomainError(f"times must be non negative, got {times}")
    value = start
    for _ in range(times):
        value = function(value)
    return value


def sorted_unique(iterable: Iterable[Any]) -> List[Any]:
    """Return the distinct items in the universal total order.

    Example:
        >>> sorted_unique([3, 1, 3, "a"])
        [1, 3, 'a']
    """
    return sorted(set(iterable), key=universal_key)
