"""Combinators for building predicates.

Predicates appear throughout the library: a partial order is defined by a
two argument predicate, a set can be described by a membership predicate,
and a relation can be filtered by a property. The combinators let those
predicates be composed in the same way the corresponding logical
connectives compose.
"""

from __future__ import annotations

from typing import Any, Callable, Iterable

from ..typing import Predicate

__all__ = [
    "always",
    "never",
    "negate",
    "conjoin",
    "disjoin",
    "implies",
    "equivalent",
    "exclusive",
    "for_all",
    "exists",
    "exactly_one",
    "count_satisfying",
    "restrict",
]


def always(*_: Any, **__: Any) -> bool:
    """Return ``True`` for any arguments.

    Example:
        >>> always(1, 2)
        True
    """
    return True


def never(*_: Any, **__: Any) -> bool:
    """Return ``False`` for any arguments.

    Example:
        >>> never(1, 2)
        False
    """
    return False


def negate(predicate: Predicate) -> Predicate:
    """Return the logical negation of a predicate.

    Example:
        >>> is_even = lambda n: n % 2 == 0
        >>> negate(is_even)(3)
        True
    """

    def wrapper(*args: Any, **kwargs: Any) -> bool:
        return not predicate(*args, **kwargs)

    return wrapper


def conjoin(*predicates: Predicate) -> Predicate:
    """Return the conjunction of the predicates, evaluated left to right.

    The empty conjunction is true, which matches the mathematical
    convention.

    Example:
        >>> positive = lambda n: n > 0
        >>> even = lambda n: n % 2 == 0
        >>> conjoin(positive, even)(4), conjoin(positive, even)(3)
        (True, False)
        >>> conjoin()(0)
        True
    """

    def wrapper(*args: Any, **kwargs: Any) -> bool:
        return all(predicate(*args, **kwargs) for predicate in predicates)

    return wrapper


def disjoin(*predicates: Predicate) -> Predicate:
    """Return the disjunction of the predicates, evaluated left to right.

    The empty disjunction is false.

    Example:
        >>> disjoin(lambda n: n < 0, lambda n: n > 10)(11)
        True
        >>> disjoin()(0)
        False
    """

    def wrapper(*args: Any, **kwargs: Any) -> bool:
        return any(predicate(*args, **kwargs) for predicate in predicates)

    return wrapper


def implies(antecedent: Predicate, consequent: Predicate) -> Predicate:
    """Return the material implication of two predicates.

    Example:
        >>> rule = implies(lambda n: n % 4 == 0, lambda n: n % 2 == 0)
        >>> rule(8), rule(3)
        (True, True)
    """

    def wrapper(*args: Any, **kwargs: Any) -> bool:
        return (not antecedent(*args, **kwargs)) or bool(consequent(*args, **kwargs))

    return wrapper


def equivalent(left: Predicate, right: Predicate) -> Predicate:
    """Return the biconditional of two predicates.

    Example:
        >>> same = equivalent(lambda n: n > 0, lambda n: n >= 1)
        >>> same(5), same(0)
        (True, True)
    """

    def wrapper(*args: Any, **kwargs: Any) -> bool:
        return bool(left(*args, **kwargs)) == bool(right(*args, **kwargs))

    return wrapper


def exclusive(left: Predicate, right: Predicate) -> Predicate:
    """Return the exclusive disjunction of two predicates.

    Example:
        >>> odd_or_negative = exclusive(lambda n: n % 2 == 1, lambda n: n < 0)
        >>> odd_or_negative(3), odd_or_negative(-3)
        (True, False)
    """

    def wrapper(*args: Any, **kwargs: Any) -> bool:
        return bool(left(*args, **kwargs)) != bool(right(*args, **kwargs))

    return wrapper


def for_all(values: Iterable[Any], predicate: Callable[[Any], bool]) -> bool:
    """Return whether the predicate holds for every value.

    This is the finite universal quantifier. It is true for the empty
    collection.

    Example:
        >>> for_all([2, 4], lambda n: n % 2 == 0)
        True
        >>> for_all([], lambda n: False)
        True
    """
    return all(predicate(value) for value in values)


def exists(values: Iterable[Any], predicate: Callable[[Any], bool]) -> bool:
    """Return whether the predicate holds for at least one value.

    This is the finite existential quantifier. It is false for the empty
    collection.

    Example:
        >>> exists([1, 2], lambda n: n % 2 == 0)
        True
        >>> exists([], lambda n: True)
        False
    """
    return any(predicate(value) for value in values)


def exactly_one(values: Iterable[Any], predicate: Callable[[Any], bool]) -> bool:
    """Return whether the predicate holds for exactly one value.

    Example:
        >>> exactly_one([1, 2, 3], lambda n: n == 2)
        True
        >>> exactly_one([2, 4], lambda n: n % 2 == 0)
        False
    """
    seen = False
    for value in values:
        if predicate(value):
            if seen:
                return False
            seen = True
    return seen


def count_satisfying(values: Iterable[Any], predicate: Callable[[Any], bool]) -> int:
    """Return how many values satisfy the predicate.

    Example:
        >>> count_satisfying(range(10), lambda n: n % 3 == 0)
        4
    """
    return sum(1 for value in values if predicate(value))


def restrict(
    predicate: Callable[[Any], bool],
    domain: Iterable[Any],
) -> Callable[[Any], bool]:
    """Return a predicate that is false outside a given domain.

    Example:
        >>> inside = restrict(lambda n: n % 2 == 0, [1, 2, 3])
        >>> inside(2), inside(4)
        (True, False)
    """
    members = set(domain)

    def wrapper(value: Any) -> bool:
        return value in members and bool(predicate(value))

    return wrapper
