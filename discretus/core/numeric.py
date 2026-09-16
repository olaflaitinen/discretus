# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

"""Exact integer helpers.

The library computes over arbitrary precision integers wherever it can, so
that results are exact regardless of size. The helpers here are the integer
primitives the domain packages share, each avoiding floating point entirely
so that no result depends on the width of a machine word.
"""

from __future__ import annotations

import math
from typing import Iterable, List, Optional, Tuple

from ..exceptions import DomainError, ValidationError
from ..validation import require_integer, require_non_negative, require_positive

__all__ = [
    "sign",
    "product",
    "ceil_div",
    "floor_div",
    "integer_sqrt",
    "is_perfect_square",
    "integer_nth_root",
    "is_perfect_power",
    "integer_log",
    "exact_divide",
    "clamp",
    "next_power_of_two",
    "is_power_of_two",
    "bit_count",
    "triangular",
    "divisor_pairs",
]


def sign(value: int) -> int:
    """Return ``-1``, ``0``, or ``1`` according to the sign of the value.

    Example:
        >>> sign(-7), sign(0), sign(7)
        (-1, 0, 1)
    """
    if value < 0:
        return -1
    return 1 if value > 0 else 0


def product(values: Iterable[int], start: int = 1) -> int:
    """Return the product of the values, exactly.

    The empty product is ``start``, which defaults to one.

    Example:
        >>> product([2, 3, 7])
        42
        >>> product([])
        1
    """
    result = start
    for value in values:
        result *= value
    return result


def ceil_div(numerator: int, denominator: int) -> int:
    """Return the ceiling of an integer division, without floating point.

    Raises:
        DomainError: When the denominator is zero.

    Example:
        >>> ceil_div(7, 2), ceil_div(-7, 2), ceil_div(6, 3)
        (4, -3, 2)
    """
    if denominator == 0:
        raise DomainError("division by zero")
    return -((-numerator) // denominator)


def floor_div(numerator: int, denominator: int) -> int:
    """Return the floor of an integer division.

    Raises:
        DomainError: When the denominator is zero.

    Example:
        >>> floor_div(7, 2), floor_div(-7, 2)
        (3, -4)
    """
    if denominator == 0:
        raise DomainError("division by zero")
    return numerator // denominator


def integer_sqrt(value: int) -> int:
    """Return the floor of the square root of a non negative integer.

    Complexity:
        O(log value) arithmetic operations through Newton iteration.

    Example:
        >>> integer_sqrt(0), integer_sqrt(15), integer_sqrt(16)
        (0, 3, 4)
    """
    require_non_negative(value, "value")
    return math.isqrt(value)


def is_perfect_square(value: int) -> bool:
    """Return whether the value is the square of an integer.

    Example:
        >>> is_perfect_square(49), is_perfect_square(50), is_perfect_square(-1)
        (True, False, False)
    """
    if value < 0:
        return False
    root = math.isqrt(value)
    return root * root == value


def integer_nth_root(value: int, degree: int) -> int:
    """Return the floor of the ``degree`` th root of a non negative integer.

    The routine uses integer Newton iteration, so the result is exact for
    inputs of any size.

    Args:
        value: A non negative integer.
        degree: A positive integer.

    Raises:
        DomainError: When the value is negative or the degree is not
            positive.

    Example:
        >>> integer_nth_root(1000, 3), integer_nth_root(999, 3)
        (10, 9)
        >>> integer_nth_root(0, 5)
        0
    """
    require_non_negative(value, "value")
    require_positive(degree, "degree")
    if value in (0, 1) or degree == 1:
        return value
    guess = 1 << (value.bit_length() // degree + 1)
    while True:
        candidate = ((degree - 1) * guess + value // guess ** (degree - 1)) // degree
        if candidate >= guess:
            break
        guess = candidate
    while guess**degree > value:
        guess -= 1
    while (guess + 1) ** degree <= value:
        guess += 1
    return guess


def is_perfect_power(value: int) -> Optional[Tuple[int, int]]:
    """Return a base and exponent with ``base ** exponent == value``.

    The exponent returned is the largest one available, and the function
    returns ``None`` when the value is not a perfect power.

    Args:
        value: An integer greater than one.

    Returns:
        A pair ``(base, exponent)`` with ``exponent >= 2``, or ``None``.

    Example:
        >>> is_perfect_power(64)
        (2, 6)
        >>> is_perfect_power(72) is None
        True
    """
    require_integer(value, "value")
    if value < 2:
        return None
    best: Optional[Tuple[int, int]] = None
    for exponent in range(2, value.bit_length() + 1):
        base = integer_nth_root(value, exponent)
        if base >= 2 and base**exponent == value:
            best = (base, exponent)
    return best


def integer_log(value: int, base: int) -> int:
    """Return the floor of the logarithm of ``value`` in the given base.

    Args:
        value: A positive integer.
        base: An integer base of at least two.

    Raises:
        DomainError: When the value is not positive or the base is too small.

    Example:
        >>> integer_log(1000, 10), integer_log(1023, 2), integer_log(1, 5)
        (3, 9, 0)
    """
    require_positive(value, "value")
    if base < 2:
        raise DomainError(f"base must be at least 2, got {base}")
    exponent = 0
    power = 1
    while power * base <= value:
        power *= base
        exponent += 1
    return exponent


def exact_divide(numerator: int, denominator: int) -> int:
    """Return the quotient when the division is exact.

    Raises:
        DomainError: When the denominator is zero.
        ValidationError: When the division leaves a remainder.

    Example:
        >>> exact_divide(12, 4)
        3
    """
    if denominator == 0:
        raise DomainError("division by zero")
    quotient, remainder = divmod(numerator, denominator)
    if remainder:
        raise ValidationError(f"{denominator} does not divide {numerator}")
    return quotient


def clamp(value: int, low: int, high: int) -> int:
    """Return the value moved into the inclusive range ``[low, high]``.

    Raises:
        DomainError: When the range is empty.

    Example:
        >>> clamp(5, 0, 3), clamp(-1, 0, 3), clamp(2, 0, 3)
        (3, 0, 2)
    """
    if low > high:
        raise DomainError(f"empty range [{low}, {high}]")
    return max(low, min(value, high))


def next_power_of_two(value: int) -> int:
    """Return the least power of two that is at least the value.

    Example:
        >>> next_power_of_two(0), next_power_of_two(1), next_power_of_two(17)
        (1, 1, 32)
    """
    require_non_negative(value, "value")
    if value <= 1:
        return 1
    return 1 << (value - 1).bit_length()


def is_power_of_two(value: int) -> bool:
    """Return whether the value is a positive power of two.

    Example:
        >>> is_power_of_two(64), is_power_of_two(48), is_power_of_two(0)
        (True, False, False)
    """
    return value > 0 and value & (value - 1) == 0


def bit_count(value: int) -> int:
    """Return the number of one bits in the binary expansion.

    Example:
        >>> bit_count(0), bit_count(7), bit_count(1024)
        (0, 3, 1)
    """
    require_non_negative(value, "value")
    return bin(value).count("1")


def triangular(index: int) -> int:
    """Return the triangular number of the given index.

    The triangular numbers count the edges of a complete graph, so the
    index is the number of vertices minus one.

    Example:
        >>> [triangular(n) for n in range(5)]
        [0, 1, 3, 6, 10]
    """
    require_non_negative(index, "index")
    return index * (index + 1) // 2


def divisor_pairs(value: int) -> List[Tuple[int, int]]:
    """Return the factor pairs of a positive integer in increasing order.

    Example:
        >>> divisor_pairs(12)
        [(1, 12), (2, 6), (3, 4)]
    """
    require_positive(value, "value")
    pairs = []
    for candidate in range(1, math.isqrt(value) + 1):
        if value % candidate == 0:
            pairs.append((candidate, value // candidate))
    return pairs
