"""Digit level utilities for arbitrary precision integers.

Python integers are already unbounded, so this module does not reimplement
arithmetic. It provides the digit and base conversions that the number
theory and combinatorics packages need, together with a transparent
Karatsuba multiplication that exists so that a reader can study the
divide and conquer recurrence it realizes.
"""

from __future__ import annotations

from typing import List, Sequence

from ..exceptions import DomainError
from ..validation import require_integer, require_non_negative
from .numeric import sign

__all__ = [
    "DIGITS",
    "digits",
    "from_digits",
    "to_base",
    "from_base",
    "digit_sum",
    "digital_root",
    "digit_count",
    "reverse_digits",
    "is_palindrome",
    "karatsuba_multiply",
]

#: Digit alphabet used by :func:`to_base` for bases up to thirty six.
DIGITS = "0123456789abcdefghijklmnopqrstuvwxyz"


def digits(value: int, base: int = 10) -> List[int]:
    """Return the digits of the absolute value, most significant first.

    Args:
        value: Any integer. The sign is ignored.
        base: A base of at least two.

    Raises:
        DomainError: When the base is smaller than two.

    Example:
        >>> digits(1234)
        [1, 2, 3, 4]
        >>> digits(13, base=2)
        [1, 1, 0, 1]
        >>> digits(0)
        [0]
    """
    require_integer(value, "value")
    if base < 2:
        raise DomainError(f"base must be at least 2, got {base}")
    magnitude = abs(value)
    if magnitude == 0:
        return [0]
    collected: List[int] = []
    while magnitude:
        magnitude, remainder = divmod(magnitude, base)
        collected.append(remainder)
    collected.reverse()
    return collected


def from_digits(sequence: Sequence[int], base: int = 10) -> int:
    """Return the integer with the given digits, most significant first.

    Raises:
        DomainError: When the base is too small or a digit is out of range.

    Example:
        >>> from_digits([1, 2, 3])
        123
        >>> from_digits([1, 0, 1], base=2)
        5
    """
    if base < 2:
        raise DomainError(f"base must be at least 2, got {base}")
    value = 0
    for digit in sequence:
        if not 0 <= digit < base:
            raise DomainError(f"digit {digit} is out of range for base {base}")
        value = value * base + digit
    return value


def to_base(value: int, base: int) -> str:
    """Return a positional representation using the digit alphabet.

    Args:
        value: Any integer. A negative value is prefixed with a minus sign.
        base: A base between two and thirty six.

    Raises:
        DomainError: When the base is outside the supported range.

    Example:
        >>> to_base(255, 16), to_base(255, 2), to_base(-10, 3)
        ('ff', '11111111', '-101')
    """
    if not 2 <= base <= len(DIGITS):
        raise DomainError(f"base must lie in [2, {len(DIGITS)}], got {base}")
    prefix = "-" if value < 0 else ""
    return prefix + "".join(DIGITS[digit] for digit in digits(value, base))


def from_base(text: str, base: int) -> int:
    """Return the integer denoted by a positional representation.

    Args:
        text: The representation, optionally signed, case insensitive.
        base: A base between two and thirty six.

    Raises:
        DomainError: When the base or a character is invalid.

    Example:
        >>> from_base("ff", 16), from_base("-101", 3)
        (255, -10)
    """
    if not 2 <= base <= len(DIGITS):
        raise DomainError(f"base must lie in [2, {len(DIGITS)}], got {base}")
    cleaned = text.strip().lower()
    negative = cleaned.startswith("-")
    if cleaned and cleaned[0] in "+-":
        cleaned = cleaned[1:]
    if not cleaned:
        raise DomainError("no digits to read")
    total = 0
    for character in cleaned:
        position = DIGITS.find(character)
        if position < 0 or position >= base:
            raise DomainError(f"character {character!r} is invalid in base {base}")
        total = total * base + position
    return -total if negative else total


def digit_sum(value: int, base: int = 10) -> int:
    """Return the sum of the digits of the absolute value.

    Example:
        >>> digit_sum(1234), digit_sum(255, base=16)
        (10, 30)
    """
    return sum(digits(value, base))


def digital_root(value: int, base: int = 10) -> int:
    """Return the repeated digit sum, reduced to a single digit.

    For base ten and a positive value the result equals the value modulo
    nine, except that multiples of nine give nine.

    Example:
        >>> digital_root(1234), digital_root(99), digital_root(0)
        (1, 9, 0)
    """
    current = abs(require_integer(value, "value"))
    while current >= base:
        current = digit_sum(current, base)
    return current


def digit_count(value: int, base: int = 10) -> int:
    """Return the number of digits of the absolute value.

    Example:
        >>> digit_count(0), digit_count(999), digit_count(1024, base=2)
        (1, 3, 11)
    """
    return len(digits(value, base))


def reverse_digits(value: int, base: int = 10) -> int:
    """Return the integer obtained by reversing the digits.

    The sign is preserved.

    Example:
        >>> reverse_digits(1230), reverse_digits(-12)
        (321, -21)
    """
    reversed_value = from_digits(list(reversed(digits(value, base))), base)
    return sign(value) * reversed_value if value else 0


def is_palindrome(value: int, base: int = 10) -> bool:
    """Return whether the digits of the absolute value read the same both ways.

    Example:
        >>> is_palindrome(12321), is_palindrome(123), is_palindrome(9, base=2)
        (True, False, True)
    """
    sequence = digits(value, base)
    return sequence == sequence[::-1]


def karatsuba_multiply(left: int, right: int, threshold: int = 32) -> int:
    """Multiply two non negative integers by the Karatsuba method.

    The routine is a transparent reference implementation of the divide and
    conquer recurrence ``T(n) = 3 T(n / 2) + O(n)``, whose solution is
    ``O(n ** log2(3))``, that is about ``O(n ** 1.585)``. For production use
    prefer the built-in multiplication, which this function falls back to
    below the threshold.

    Args:
        left: A non negative integer.
        right: A non negative integer.
        threshold: Bit length at which the recursion stops.

    Returns:
        The product of the two arguments.

    Raises:
        DomainError: When an argument is negative.

    Complexity:
        O(n ** 1.585) bit operations for n bit inputs.

    Example:
        >>> karatsuba_multiply(123456789, 987654321)
        121932631112635269
        >>> karatsuba_multiply(0, 5)
        0
    """
    require_non_negative(left, "left")
    require_non_negative(right, "right")
    if left.bit_length() <= threshold or right.bit_length() <= threshold:
        return left * right
    half = max(left.bit_length(), right.bit_length()) // 2
    mask = (1 << half) - 1
    left_low, left_high = left & mask, left >> half
    right_low, right_high = right & mask, right >> half
    low = karatsuba_multiply(left_low, right_low, threshold)
    high = karatsuba_multiply(left_high, right_high, threshold)
    middle = (
        karatsuba_multiply(left_low + left_high, right_low + right_high, threshold)
        - low
        - high
    )
    return (high << (2 * half)) + (middle << half) + low
