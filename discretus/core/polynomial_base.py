"""Dense polynomials with exact coefficients.

Coefficients are stored from the constant term upward, which makes indexing
match the exponent. The representation is normalized so that the leading
coefficient is nonzero, and the zero polynomial has an empty coefficient
tuple and degree minus one by convention.
"""

from __future__ import annotations

from fractions import Fraction
from typing import Any, Iterable, List, Sequence, Tuple

from ..exceptions import DomainError, ValidationError
from .rationals import as_fraction, fraction_to_latex, fraction_to_text

__all__ = ["PolynomialBase"]


class PolynomialBase:
    """An immutable univariate polynomial with exact rational coefficients.

    Args:
        coefficients: Coefficients from the constant term upward.
        variable: Name used when the polynomial is printed.

    Example:
        >>> p = PolynomialBase([1, 2, 3])
        >>> p
        PolynomialBase(3*x^2 + 2*x + 1)
        >>> p.degree()
        2
        >>> p.evaluate(2)
        Fraction(17, 1)
        >>> p * p
        PolynomialBase(9*x^4 + 12*x^3 + 10*x^2 + 4*x + 1)
    """

    __slots__ = ("_coefficients", "_variable")

    def __init__(
        self,
        coefficients: Iterable[Any],
        variable: str = "x",
    ) -> None:
        exact = [as_fraction(value) for value in coefficients]
        while exact and exact[-1] == 0:
            exact.pop()
        self._coefficients: Tuple[Fraction, ...] = tuple(exact)
        self._variable = variable

    # Construction.

    @classmethod
    def zero(cls, variable: str = "x") -> "PolynomialBase":
        """Return the zero polynomial.

        Example:
            >>> PolynomialBase.zero().is_zero()
            True
        """
        return cls([], variable)

    @classmethod
    def one(cls, variable: str = "x") -> "PolynomialBase":
        """Return the constant polynomial one."""
        return cls([1], variable)

    @classmethod
    def monomial(
        cls,
        degree: int,
        coefficient: Any = 1,
        variable: str = "x",
    ) -> "PolynomialBase":
        """Return a single term polynomial.

        Example:
            >>> PolynomialBase.monomial(3, 2)
            PolynomialBase(2*x^3)
        """
        if degree < 0:
            raise DomainError(f"degree must be non negative, got {degree}")
        return cls([0] * degree + [coefficient], variable)

    @classmethod
    def from_roots(cls, roots: Sequence[Any], variable: str = "x") -> "PolynomialBase":
        """Return the monic polynomial with the given roots.

        Example:
            >>> PolynomialBase.from_roots([1, 2])
            PolynomialBase(x^2 - 3*x + 2)
        """
        result = cls.one(variable)
        for root in roots:
            result = result.multiply(cls([-as_fraction(root), 1], variable))
        return result

    # Access.

    @property
    def coefficients(self) -> List[Fraction]:
        """Return the coefficients from the constant term upward."""
        return list(self._coefficients)

    @property
    def variable(self) -> str:
        """Return the name used when printing."""
        return self._variable

    def degree(self) -> int:
        """Return the degree, using minus one for the zero polynomial."""
        return len(self._coefficients) - 1

    def coefficient(self, exponent: int) -> Fraction:
        """Return the coefficient of a given power, or zero when absent.

        Example:
            >>> PolynomialBase([1, 2]).coefficient(5)
            Fraction(0, 1)
        """
        if exponent < 0:
            raise DomainError(f"exponent must be non negative, got {exponent}")
        if exponent >= len(self._coefficients):
            return Fraction(0)
        return self._coefficients[exponent]

    def leading_coefficient(self) -> Fraction:
        """Return the coefficient of the highest power, or zero.

        Example:
            >>> PolynomialBase([1, 0, 4]).leading_coefficient()
            Fraction(4, 1)
        """
        if not self._coefficients:
            return Fraction(0)
        return self._coefficients[-1]

    def is_zero(self) -> bool:
        """Return whether this is the zero polynomial."""
        return not self._coefficients

    def is_constant(self) -> bool:
        """Return whether the degree is at most zero."""
        return self.degree() <= 0

    def is_monic(self) -> bool:
        """Return whether the leading coefficient is one."""
        return self.leading_coefficient() == 1

    # Arithmetic.

    def add(self, other: "PolynomialBase") -> "PolynomialBase":
        """Return the sum of two polynomials."""
        size = max(len(self._coefficients), len(other._coefficients))
        return PolynomialBase(
            [
                self.coefficient(index) + other.coefficient(index)
                for index in range(size)
            ],
            self._variable,
        )

    def subtract(self, other: "PolynomialBase") -> "PolynomialBase":
        """Return the difference of two polynomials."""
        return self.add(other.scale(-1))

    def scale(self, factor: Any) -> "PolynomialBase":
        """Return the polynomial with every coefficient multiplied."""
        multiplier = as_fraction(factor)
        return PolynomialBase(
            [coefficient * multiplier for coefficient in self._coefficients],
            self._variable,
        )

    def multiply(self, other: "PolynomialBase") -> "PolynomialBase":
        """Return the product of two polynomials.

        Complexity:
            O(n m) exact multiplications for degrees n and m.
        """
        if self.is_zero() or other.is_zero():
            return PolynomialBase.zero(self._variable)
        result = [Fraction(0)] * (self.degree() + other.degree() + 1)
        for i, left in enumerate(self._coefficients):
            if left == 0:
                continue
            for j, right in enumerate(other._coefficients):
                result[i + j] += left * right
        return PolynomialBase(result, self._variable)

    def power(self, exponent: int) -> "PolynomialBase":
        """Return an integer power by repeated squaring.

        Example:
            >>> PolynomialBase([1, 1]).power(3)
            PolynomialBase(x^3 + 3*x^2 + 3*x + 1)
        """
        if exponent < 0:
            raise DomainError(f"exponent must be non negative, got {exponent}")
        result = PolynomialBase.one(self._variable)
        base = self
        remaining = exponent
        while remaining:
            if remaining & 1:
                result = result.multiply(base)
            remaining >>= 1
            if remaining:
                base = base.multiply(base)
        return result

    def divmod(self, divisor: "PolynomialBase") -> Tuple["PolynomialBase", "PolynomialBase"]:
        """Return the quotient and remainder of polynomial long division.

        The identity ``self == quotient * divisor + remainder`` holds
        exactly, and the remainder has smaller degree than the divisor.

        Raises:
            ValidationError: When the divisor is the zero polynomial.

        Complexity:
            O((n - m + 1) m) exact operations for degrees n and m.

        Example:
            >>> q, r = PolynomialBase([-1, 0, 0, 1]).divmod(PolynomialBase([-1, 1]))
            >>> q, r
            (PolynomialBase(x^2 + x + 1), PolynomialBase(0))
        """
        if divisor.is_zero():
            raise ValidationError("cannot divide by the zero polynomial")
        remainder = list(self._coefficients)
        divisor_degree = divisor.degree()
        divisor_lead = divisor.leading_coefficient()
        quotient = [Fraction(0)] * max(0, len(remainder) - divisor_degree)
        for index in range(len(remainder) - 1, divisor_degree - 1, -1):
            if remainder[index] == 0:
                continue
            factor = remainder[index] / divisor_lead
            position = index - divisor_degree
            quotient[position] = factor
            for offset, coefficient in enumerate(divisor._coefficients):
                remainder[position + offset] -= factor * coefficient
        return (
            PolynomialBase(quotient, self._variable),
            PolynomialBase(remainder, self._variable),
        )

    def evaluate(self, value: Any) -> Fraction:
        """Return the value of the polynomial by Horner evaluation.

        Complexity:
            O(n) exact multiplications and additions.
        """
        point = as_fraction(value)
        total = Fraction(0)
        for coefficient in reversed(self._coefficients):
            total = total * point + coefficient
        return total

    def compose(self, other: "PolynomialBase") -> "PolynomialBase":
        """Return the composition of this polynomial with another.

        Example:
            >>> PolynomialBase([0, 0, 1]).compose(PolynomialBase([1, 1]))
            PolynomialBase(x^2 + 2*x + 1)
        """
        result = PolynomialBase.zero(self._variable)
        for coefficient in reversed(self._coefficients):
            result = result.multiply(other).add(
                PolynomialBase([coefficient], self._variable)
            )
        return result

    def derivative(self) -> "PolynomialBase":
        """Return the formal derivative.

        Example:
            >>> PolynomialBase([5, 3, 2]).derivative()
            PolynomialBase(4*x + 3)
        """
        return PolynomialBase(
            [
                coefficient * exponent
                for exponent, coefficient in enumerate(self._coefficients)
                if exponent > 0
            ],
            self._variable,
        )

    def monic(self) -> "PolynomialBase":
        """Return the polynomial scaled to have leading coefficient one.

        Raises:
            ValidationError: When the polynomial is zero.
        """
        if self.is_zero():
            raise ValidationError("the zero polynomial cannot be made monic")
        return self.scale(Fraction(1, 1) / self.leading_coefficient())

    # Operators and rendering.

    def __add__(self, other: "PolynomialBase") -> "PolynomialBase":
        return self.add(other)

    def __sub__(self, other: "PolynomialBase") -> "PolynomialBase":
        return self.subtract(other)

    def __neg__(self) -> "PolynomialBase":
        return self.scale(-1)

    def __mul__(self, other: Any) -> "PolynomialBase":
        if isinstance(other, PolynomialBase):
            return self.multiply(other)
        return self.scale(other)

    def __rmul__(self, other: Any) -> "PolynomialBase":
        return self.scale(other)

    def __pow__(self, exponent: int) -> "PolynomialBase":
        return self.power(exponent)

    def __divmod__(
        self, other: "PolynomialBase"
    ) -> Tuple["PolynomialBase", "PolynomialBase"]:
        return self.divmod(other)

    def __call__(self, value: Any) -> Fraction:
        return self.evaluate(value)

    def __eq__(self, other: object) -> bool:
        if isinstance(other, PolynomialBase):
            return self._coefficients == other._coefficients
        return NotImplemented

    def __hash__(self) -> int:
        return hash(self._coefficients)

    def _terms(self, latex: bool) -> List[str]:
        """Return the rendered terms from the highest power downward."""
        pieces: List[str] = []
        variable = self._variable
        for exponent in range(self.degree(), -1, -1):
            coefficient = self.coefficient(exponent)
            if coefficient == 0:
                continue
            magnitude = abs(coefficient)
            rendered = (
                fraction_to_latex(magnitude) if latex else fraction_to_text(magnitude)
            )
            if exponent == 0:
                term = rendered
            else:
                power = variable if exponent == 1 else (
                    f"{variable}^{{{exponent}}}" if latex else f"{variable}^{exponent}"
                )
                if magnitude == 1:
                    term = power
                else:
                    term = f"{rendered}{power}" if latex else f"{rendered}*{power}"
            sign = "-" if coefficient < 0 else "+"
            pieces.append(f"{sign} {term}" if pieces else (f"-{term}" if sign == "-" else term))
        return pieces

    def to_text(self) -> str:
        """Return the polynomial in plain text notation.

        Example:
            >>> PolynomialBase([0, -1, 1]).to_text()
            'x^2 - x'
        """
        pieces = self._terms(latex=False)
        return " ".join(pieces) if pieces else "0"

    def to_latex(self) -> str:
        """Return the polynomial in LaTeX notation.

        Example:
            >>> PolynomialBase([1, 2]).to_latex()
            '2x + 1'
        """
        pieces = self._terms(latex=True)
        return " ".join(pieces) if pieces else "0"

    def __str__(self) -> str:
        return self.to_text()

    def __repr__(self) -> str:
        return f"PolynomialBase({self.to_text()})"
