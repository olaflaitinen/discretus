# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

"""Modular arithmetic primitives.

The number theory package exposes the documented public interface for
modular arithmetic. The primitives live here because the algebra package
needs them too, for modular integer rings, prime fields, and modular
matrices, and duplicating them would risk the two copies drifting apart.
"""

from __future__ import annotations

from typing import Any, List, Optional, Sequence, Tuple

from ..exceptions import DomainError, InfeasibleError
from ..validation import require_integer, require_modulus
from .repr_utils import class_repr

__all__ = [
    "normalize",
    "mod_add",
    "mod_subtract",
    "mod_multiply",
    "mod_power",
    "extended_euclidean",
    "mod_inverse",
    "mod_divide",
    "solve_congruence",
    "ModularInteger",
    "residues",
    "units",
    "crt_pair",
    "crt",
]


def normalize(value: int, modulus: int) -> int:
    """Return the representative of a residue class in ``[0, modulus)``.

    Example:
        >>> normalize(-1, 7), normalize(15, 7)
        (6, 1)
    """
    require_integer(value, "value")
    require_modulus(modulus)
    return value % modulus


def mod_add(left: int, right: int, modulus: int) -> int:
    """Return the sum of two residues.

    Example:
        >>> mod_add(5, 4, 7)
        2
    """
    return (normalize(left, modulus) + normalize(right, modulus)) % modulus


def mod_subtract(left: int, right: int, modulus: int) -> int:
    """Return the difference of two residues.

    Example:
        >>> mod_subtract(2, 5, 7)
        4
    """
    return (normalize(left, modulus) - normalize(right, modulus)) % modulus


def mod_multiply(left: int, right: int, modulus: int) -> int:
    """Return the product of two residues.

    Example:
        >>> mod_multiply(3, 5, 7)
        1
    """
    return (normalize(left, modulus) * normalize(right, modulus)) % modulus


def mod_power(base: int, exponent: int, modulus: int) -> int:
    """Return a modular power by square and multiply.

    A negative exponent is handled by inverting the base first, which
    requires the base to be invertible.

    Args:
        base: Any integer.
        exponent: Any integer.
        modulus: A modulus of at least one.

    Raises:
        InfeasibleError: When a negative exponent meets a base that is not
            invertible modulo the modulus.

    Complexity:
        O(log exponent) modular multiplications.

    Example:
        >>> mod_power(7, 128, 13)
        3
        >>> mod_power(3, -1, 7)
        5
    """
    require_modulus(modulus)
    if exponent < 0:
        return pow(mod_inverse(base, modulus), -exponent, modulus)
    return pow(normalize(base, modulus), exponent, modulus)


def extended_euclidean(left: int, right: int) -> Tuple[int, int, int]:
    """Return the greatest common divisor together with Bezout coefficients.

    The returned triple ``(g, x, y)`` satisfies ``left * x + right * y == g``
    with ``g`` non negative.

    Complexity:
        O(log min(left, right)) division steps.

    Example:
        >>> extended_euclidean(462, 1071)
        (21, 7, -3)
        >>> g, x, y = extended_euclidean(240, 46)
        >>> g, 240 * x + 46 * y
        (2, 2)
    """
    require_integer(left, "left")
    require_integer(right, "right")
    old_r, r = left, right
    old_s, s = 1, 0
    old_t, t = 0, 1
    while r:
        quotient = old_r // r
        old_r, r = r, old_r - quotient * r
        old_s, s = s, old_s - quotient * s
        old_t, t = t, old_t - quotient * t
    if old_r < 0:
        return (-old_r, -old_s, -old_t)
    return (old_r, old_s, old_t)


def mod_inverse(value: int, modulus: int) -> int:
    """Return the multiplicative inverse of a residue.

    Args:
        value: Any integer.
        modulus: A modulus of at least one.

    Raises:
        InfeasibleError: When the value and the modulus are not coprime, in
            which case no inverse exists.

    Complexity:
        O(log modulus) division steps.

    Example:
        >>> mod_inverse(3, 11)
        4
    """
    require_modulus(modulus)
    if modulus == 1:
        return 0
    divisor, coefficient, _ = extended_euclidean(normalize(value, modulus), modulus)
    if divisor != 1:
        raise InfeasibleError(
            f"{value} is not invertible modulo {modulus} because their "
            f"greatest common divisor is {divisor}"
        )
    return coefficient % modulus


def mod_divide(numerator: int, denominator: int, modulus: int) -> int:
    """Return the quotient of two residues.

    Example:
        >>> mod_divide(4, 3, 11)
        5
    """
    return mod_multiply(numerator, mod_inverse(denominator, modulus), modulus)


def solve_congruence(
    coefficient: int,
    value: int,
    modulus: int,
) -> Optional[Tuple[int, int]]:
    """Solve the linear congruence ``coefficient * x == value``.

    The congruence has a solution precisely when the greatest common
    divisor of the coefficient and the modulus divides the value. When it
    does, the solution set is an arithmetic progression, which the function
    reports as a base residue and a step.

    Returns:
        A pair ``(base, step)`` such that the solutions are exactly
        ``base + k * step`` modulo the modulus, or ``None`` when there is no
        solution.

    Example:
        >>> solve_congruence(3, 6, 9)
        (2, 3)
        >>> solve_congruence(2, 3, 4) is None
        True
    """
    require_modulus(modulus)
    divisor, inverse_part, _ = extended_euclidean(
        normalize(coefficient, modulus), modulus
    )
    if value % divisor != 0:
        return None
    step = modulus // divisor
    base = (inverse_part * (value // divisor)) % step
    return (base, step)


class ModularInteger:
    """A residue class modulo a fixed modulus, with arithmetic operators.

    The type makes modular computations read like ordinary arithmetic while
    keeping the modulus attached to the value, so that two residues with
    different moduli can never be combined by accident.

    Args:
        value: Any integer representative of the class.
        modulus: A modulus of at least one.

    Example:
        >>> a = ModularInteger(7, 5)
        >>> a
        ModularInteger(value=2, modulus=5)
        >>> a + 4, a * 3, a ** 3
        (ModularInteger(value=1, modulus=5), ModularInteger(value=1, modulus=5), ModularInteger(value=3, modulus=5))
        >>> a.inverse()
        ModularInteger(value=3, modulus=5)
        >>> int(a)
        2
    """

    __slots__ = ("_value", "_modulus")

    def __init__(self, value: int, modulus: int) -> None:
        self._modulus = require_modulus(modulus)
        self._value = normalize(value, modulus)

    @property
    def value(self) -> int:
        """Return the representative in ``[0, modulus)``."""
        return self._value

    @property
    def modulus(self) -> int:
        """Return the modulus."""
        return self._modulus

    def _coerce(self, other: Any) -> "ModularInteger":
        """Return the argument as a residue with the same modulus."""
        if isinstance(other, ModularInteger):
            if other.modulus != self._modulus:
                raise DomainError(
                    f"cannot combine residues with moduli {self._modulus} "
                    f"and {other.modulus}"
                )
            return other
        return ModularInteger(other, self._modulus)

    def add(self, other: Any) -> "ModularInteger":
        """Return the sum of two residues."""
        return ModularInteger(self._value + self._coerce(other).value, self._modulus)

    def subtract(self, other: Any) -> "ModularInteger":
        """Return the difference of two residues."""
        return ModularInteger(self._value - self._coerce(other).value, self._modulus)

    def multiply(self, other: Any) -> "ModularInteger":
        """Return the product of two residues."""
        return ModularInteger(self._value * self._coerce(other).value, self._modulus)

    def power(self, exponent: int) -> "ModularInteger":
        """Return an integer power of the residue."""
        return ModularInteger(mod_power(self._value, exponent, self._modulus), self._modulus)

    def inverse(self) -> "ModularInteger":
        """Return the multiplicative inverse.

        Raises:
            InfeasibleError: When the residue is not invertible.
        """
        return ModularInteger(mod_inverse(self._value, self._modulus), self._modulus)

    def divide(self, other: Any) -> "ModularInteger":
        """Return the quotient of two residues."""
        return self.multiply(self._coerce(other).inverse())

    def is_unit(self) -> bool:
        """Return whether the residue is invertible.

        Example:
            >>> ModularInteger(2, 4).is_unit(), ModularInteger(3, 4).is_unit()
            (False, True)
        """
        return extended_euclidean(self._value, self._modulus)[0] == 1

    def order(self) -> int:
        """Return the multiplicative order of the residue.

        Raises:
            InfeasibleError: When the residue is not invertible, in which
                case it generates no cyclic group.

        Example:
            >>> ModularInteger(2, 7).order()
            3
        """
        if not self.is_unit():
            raise InfeasibleError(
                f"{self._value} is not invertible modulo {self._modulus}"
            )
        current = self._value % self._modulus
        count = 1
        while current != 1 % self._modulus:
            current = (current * self._value) % self._modulus
            count += 1
        return count

    def __add__(self, other: Any) -> "ModularInteger":
        return self.add(other)

    __radd__ = __add__

    def __sub__(self, other: Any) -> "ModularInteger":
        return self.subtract(other)

    def __rsub__(self, other: Any) -> "ModularInteger":
        return self._coerce(other).subtract(self)

    def __mul__(self, other: Any) -> "ModularInteger":
        return self.multiply(other)

    __rmul__ = __mul__

    def __truediv__(self, other: Any) -> "ModularInteger":
        return self.divide(other)

    def __pow__(self, exponent: int) -> "ModularInteger":
        return self.power(exponent)

    def __neg__(self) -> "ModularInteger":
        return ModularInteger(-self._value, self._modulus)

    def __int__(self) -> int:
        return self._value

    def __eq__(self, other: object) -> bool:
        if isinstance(other, ModularInteger):
            return (self._value, self._modulus) == (other._value, other._modulus)
        if isinstance(other, int):
            return self._value == other % self._modulus
        return NotImplemented

    def __hash__(self) -> int:
        return hash((self._value, self._modulus))

    def __str__(self) -> str:
        return f"{self._value} (mod {self._modulus})"

    def __repr__(self) -> str:
        return class_repr(self, value=self._value, modulus=self._modulus)


def residues(modulus: int) -> List[ModularInteger]:
    """Return every residue class modulo the given modulus.

    Example:
        >>> [int(item) for item in residues(4)]
        [0, 1, 2, 3]
    """
    require_modulus(modulus)
    return [ModularInteger(value, modulus) for value in range(modulus)]


def units(modulus: int) -> List[int]:
    """Return the representatives that are invertible modulo the modulus.

    Example:
        >>> units(12)
        [1, 5, 7, 11]
    """
    require_modulus(modulus)
    return [
        value
        for value in range(modulus)
        if extended_euclidean(value, modulus)[0] == 1
    ]


def crt_pair(
    first_value: int,
    first_modulus: int,
    second_value: int,
    second_modulus: int,
) -> Tuple[int, int]:
    """Combine two congruences into one by the Chinese remainder theorem.

    The moduli need not be coprime. When they are not, the routine still
    succeeds if the two congruences agree on the shared part.

    Returns:
        A pair ``(value, modulus)`` describing the combined congruence.

    Raises:
        InfeasibleError: When the two congruences are incompatible.

    Example:
        >>> crt_pair(2, 3, 3, 5)
        (8, 15)
        >>> crt_pair(1, 4, 3, 6)
        (9, 12)
    """
    divisor, coefficient, _ = extended_euclidean(first_modulus, second_modulus)
    difference = second_value - first_value
    if difference % divisor != 0:
        raise InfeasibleError(
            f"the congruences {first_value} mod {first_modulus} and "
            f"{second_value} mod {second_modulus} are incompatible"
        )
    combined_modulus = first_modulus // divisor * second_modulus
    step = (difference // divisor * coefficient) % (second_modulus // divisor)
    return ((first_value + first_modulus * step) % combined_modulus, combined_modulus)


def crt(values: Sequence[int], moduli: Sequence[int]) -> Tuple[int, int]:
    """Combine any number of congruences by the Chinese remainder theorem.

    Args:
        values: The right hand sides of the congruences.
        moduli: The moduli, in the same order.

    Returns:
        A pair ``(value, modulus)`` describing the combined congruence.

    Raises:
        DomainError: When the two sequences have different lengths or are
            empty.
        InfeasibleError: When the system has no solution.

    Example:
        >>> crt([2, 3, 2], [3, 5, 7])
        (23, 105)
    """
    if len(values) != len(moduli):
        raise DomainError("values and moduli must have the same length")
    if not values:
        raise DomainError("at least one congruence is required")
    value, modulus = normalize(values[0], moduli[0]), require_modulus(moduli[0])
    for next_value, next_modulus in zip(values[1:], moduli[1:]):
        value, modulus = crt_pair(value, modulus, next_value, require_modulus(next_modulus))
    return (value, modulus)
