# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

"""Exact rational helpers.

Closed forms in this library keep their coefficients as fractions rather
than floating point numbers, so that a reported solution of a recurrence or
an interpolated polynomial is exact. The helpers here convert into and out
of that representation and render it.
"""

from __future__ import annotations

from fractions import Fraction
from typing import Any, Iterable, List, Sequence, Tuple

from ..exceptions import DomainError, ValidationError
from ..validation import require_non_negative, require_positive

__all__ = [
    "as_fraction",
    "as_fractions",
    "common_denominator",
    "clear_denominators",
    "mediant",
    "harmonic_number",
    "fraction_to_latex",
    "fraction_to_text",
    "continued_fraction_of",
    "from_continued_fraction",
    "best_approximation",
]


def as_fraction(value: Any) -> Fraction:
    """Return the value as an exact fraction.

    Integers, fractions, decimal strings, and ``"a/b"`` strings convert
    exactly. A float converts through its exact binary value, which is what
    :class:`fractions.Fraction` does, so ``0.1`` becomes a fraction very
    close to but not equal to one tenth.

    Raises:
        ValidationError: When the value cannot be read as a number.

    Example:
        >>> as_fraction(3), as_fraction("2/4"), as_fraction("0.25")
        (Fraction(3, 1), Fraction(1, 2), Fraction(1, 4))
    """
    if isinstance(value, Fraction):
        return value
    if isinstance(value, bool):
        raise ValidationError("a boolean is not a number here")
    try:
        return Fraction(value)
    except (TypeError, ValueError, ZeroDivisionError) as exc:
        raise ValidationError(f"cannot read {value!r} as a rational number") from exc


def as_fractions(values: Iterable[Any]) -> List[Fraction]:
    """Return every value as an exact fraction.

    Example:
        >>> as_fractions([1, "1/2"])
        [Fraction(1, 1), Fraction(1, 2)]
    """
    return [as_fraction(value) for value in values]


def common_denominator(values: Iterable[Any]) -> int:
    """Return the least common denominator of a collection of rationals.

    Example:
        >>> common_denominator(["1/2", "1/3", 2])
        6
    """
    from math import gcd

    denominator = 1
    for value in values:
        other = as_fraction(value).denominator
        denominator = denominator * other // gcd(denominator, other)
    return denominator


def clear_denominators(values: Sequence[Any]) -> Tuple[List[int], int]:
    """Return integer numerators and the shared denominator.

    The identity ``value[i] == numerators[i] / denominator`` holds exactly
    for every index.

    Example:
        >>> clear_denominators(["1/2", "1/3"])
        ([3, 2], 6)
    """
    denominator = common_denominator(values)
    numerators = [
        int(as_fraction(value) * denominator) for value in values
    ]
    return numerators, denominator


def mediant(left: Any, right: Any) -> Fraction:
    """Return the mediant of two fractions.

    The mediant of ``a / b`` and ``c / d`` is ``(a + c) / (b + d)``, and it
    lies strictly between the two when they are distinct. It is the
    operation that generates the Stern Brocot tree and the Farey sequences.

    Example:
        >>> mediant("1/2", "2/3")
        Fraction(3, 5)
    """
    first, second = as_fraction(left), as_fraction(right)
    return Fraction(
        first.numerator + second.numerator,
        first.denominator + second.denominator,
    )


def harmonic_number(index: int) -> Fraction:
    """Return the exact harmonic number of the given index.

    The harmonic number is the sum of the reciprocals of the first ``index``
    positive integers, and it is zero for index zero.

    Complexity:
        O(index) exact rational additions.

    Example:
        >>> harmonic_number(4)
        Fraction(25, 12)
        >>> harmonic_number(0)
        Fraction(0, 1)
    """
    require_non_negative(index, "index")
    total = Fraction(0)
    for term in range(1, index + 1):
        total += Fraction(1, term)
    return total


def fraction_to_latex(value: Any, inline: bool = False) -> str:
    """Render a fraction as LaTeX.

    Args:
        value: Any value accepted by :func:`as_fraction`.
        inline: When true, use the slash form instead of a fraction box.

    Example:
        >>> fraction_to_latex("3/4")
        '\\\\frac{3}{4}'
        >>> fraction_to_latex("3/4", inline=True)
        '3/4'
        >>> fraction_to_latex(5)
        '5'
    """
    fraction = as_fraction(value)
    if fraction.denominator == 1:
        return str(fraction.numerator)
    if inline:
        return f"{fraction.numerator}/{fraction.denominator}"
    sign_prefix = "-" if fraction.numerator < 0 else ""
    return (
        sign_prefix
        + r"\frac{"
        + str(abs(fraction.numerator))
        + "}{"
        + str(fraction.denominator)
        + "}"
    )


def fraction_to_text(value: Any) -> str:
    """Render a fraction in plain text, omitting a unit denominator.

    Example:
        >>> fraction_to_text("4/2"), fraction_to_text("1/3")
        ('2', '1/3')
    """
    fraction = as_fraction(value)
    if fraction.denominator == 1:
        return str(fraction.numerator)
    return f"{fraction.numerator}/{fraction.denominator}"


def continued_fraction_of(value: Any, limit: int = 64) -> List[int]:
    """Return the continued fraction expansion of a rational number.

    The expansion of a rational number is finite, so ``limit`` only guards
    against a pathological input.

    Example:
        >>> continued_fraction_of("415/93")
        [4, 2, 6, 7]
        >>> continued_fraction_of(5)
        [5]
    """
    require_positive(limit, "limit")
    fraction = as_fraction(value)
    numerator, denominator = fraction.numerator, fraction.denominator
    terms: List[int] = []
    while denominator and len(terms) < limit:
        quotient, remainder = divmod(numerator, denominator)
        terms.append(quotient)
        numerator, denominator = denominator, remainder
    return terms


def from_continued_fraction(terms: Sequence[int]) -> Fraction:
    """Return the rational number denoted by a continued fraction.

    Raises:
        DomainError: When the expansion is empty.

    Example:
        >>> from_continued_fraction([4, 2, 6, 7])
        Fraction(415, 93)
    """
    if not terms:
        raise DomainError("a continued fraction needs at least one term")
    result = Fraction(terms[-1])
    for term in reversed(terms[:-1]):
        result = term + Fraction(1, 1) / result
    return result


def best_approximation(value: Any, max_denominator: int) -> Fraction:
    """Return the closest fraction with a bounded denominator.

    The routine is the standard best rational approximation, which the
    continued fraction expansion makes optimal in the sense that no fraction
    with a denominator at most ``max_denominator`` is closer.

    Example:
        >>> best_approximation(3.14159265358979, 100)
        Fraction(311, 99)
        >>> best_approximation("22/7", 10)
        Fraction(22, 7)
    """
    require_positive(max_denominator, "max_denominator")
    return as_fraction(value).limit_denominator(max_denominator)
