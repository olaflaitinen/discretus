# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

"""Ordering helpers for heterogeneous collections of elements.

Discrete structures are often built over mixed collections, for example a
graph whose vertices are both strings and integers. Sorting such a
collection with the built-in comparison raises, so the library sorts through
the key function defined here. The order is total, deterministic, and
independent of hash randomization.
"""

from __future__ import annotations

from fractions import Fraction
from typing import Any, Callable, Iterable, List, Tuple, TypeVar

from ..typing import Comparator

__all__ = [
    "universal_key",
    "sorted_elements",
    "compare",
    "lexicographic",
    "by_key",
    "reverse_comparator",
    "is_sorted",
]

T = TypeVar("T")

#: Ranks used to order values of different types relative to one another.
_TYPE_RANK = {
    "bool": 0,
    "int": 1,
    "Fraction": 1,
    "float": 1,
    "str": 2,
    "tuple": 3,
    "frozenset": 4,
}


def universal_key(value: Any) -> Tuple[Any, ...]:
    """Return a sort key that totally orders arbitrary elements.

    Numbers sort numerically before strings, strings sort lexicographically,
    tuples sort component by component, and sets sort by size and then by
    their sorted members. Anything else sorts by type name and
    representation.

    Example:
        >>> sorted([3, "a", 1], key=universal_key)
        [1, 3, 'a']
        >>> sorted([(2,), (1, 0)], key=universal_key)
        [(1, 0), (2,)]
    """
    name = type(value).__name__
    rank = _TYPE_RANK.get(name, 9)
    if isinstance(value, bool):
        return (rank, int(value))
    if isinstance(value, (int, float, Fraction)):
        return (rank, Fraction(value) if not isinstance(value, float) else value)
    if isinstance(value, str):
        return (rank, value)
    if isinstance(value, tuple):
        return (rank, tuple(universal_key(item) for item in value))
    if isinstance(value, (frozenset, set)):
        return (
            rank,
            len(value),
            tuple(sorted((universal_key(item) for item in value), key=repr)),
        )
    return (rank, name, repr(value))


def sorted_elements(values: Iterable[Any]) -> List[Any]:
    """Return the values in the universal total order.

    Example:
        >>> sorted_elements({"b", "a"})
        ['a', 'b']
    """
    return sorted(values, key=universal_key)


def compare(left: Any, right: Any) -> int:
    """Return ``-1``, ``0``, or ``1`` in the universal total order.

    Example:
        >>> compare(1, 2), compare(2, 2), compare("b", "a")
        (-1, 0, 1)
    """
    left_key, right_key = universal_key(left), universal_key(right)
    if left_key < right_key:
        return -1
    if left_key > right_key:
        return 1
    return 0


def lexicographic(left: Iterable[Any], right: Iterable[Any]) -> int:
    """Compare two sequences component by component.

    A proper prefix precedes the longer sequence.

    Example:
        >>> lexicographic([1, 2], [1, 3])
        -1
        >>> lexicographic([1], [1, 0])
        -1
        >>> lexicographic([1, 2], [1, 2])
        0
    """
    left_items, right_items = list(left), list(right)
    for first, second in zip(left_items, right_items):
        result = compare(first, second)
        if result != 0:
            return result
    return compare(len(left_items), len(right_items))


def by_key(key: Callable[[Any], Any]) -> Comparator:
    """Return a two argument predicate that compares by a key function.

    Example:
        >>> shorter = by_key(len)
        >>> shorter("ab", "abc")
        True
    """

    def predicate(left: Any, right: Any) -> bool:
        return bool(key(left) < key(right))

    return predicate


def reverse_comparator(comparator: Comparator) -> Comparator:
    """Return the comparator with its arguments swapped.

    Example:
        >>> less = lambda a, b: a < b
        >>> reverse_comparator(less)(1, 2)
        False
    """

    def predicate(left: Any, right: Any) -> bool:
        return bool(comparator(right, left))

    return predicate


def is_sorted(values: Iterable[Any], strict: bool = False) -> bool:
    """Return whether the values are in non decreasing universal order.

    Args:
        values: The sequence to inspect.
        strict: When true, equal neighbours make the result false.

    Example:
        >>> is_sorted([1, 2, 2])
        True
        >>> is_sorted([1, 2, 2], strict=True)
        False
    """
    items = list(values)
    for first, second in zip(items, items[1:]):
        result = compare(first, second)
        if result > 0 or (strict and result == 0):
            return False
    return True
