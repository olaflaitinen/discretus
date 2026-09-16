"""Exact vectors over the rationals.

The vector type is immutable and arithmetic is exact, which keeps the linear
algebra used by the graph spectral routines, the recurrence solvers, and the
finite field machinery free of rounding error.
"""

from __future__ import annotations

from fractions import Fraction
from typing import Any, Iterable, Iterator, List, Sequence

from ..exceptions import DimensionError, DomainError
from .rationals import as_fraction, fraction_to_text

__all__ = ["VectorBase"]


class VectorBase:
    """An immutable vector of exact rational entries.

    Args:
        entries: The components, each accepted by
            :func:`~discretus.core.rationals.as_fraction`.

    Example:
        >>> u = VectorBase([1, 2, 3])
        >>> v = VectorBase([0, 1, "1/2"])
        >>> u + v
        VectorBase([1, 3, 7/2])
        >>> u.dot(v)
        Fraction(7, 2)
        >>> 2 * u
        VectorBase([2, 4, 6])
    """

    __slots__ = ("_entries",)

    def __init__(self, entries: Iterable[Any]) -> None:
        self._entries = tuple(as_fraction(entry) for entry in entries)

    # Construction.

    @classmethod
    def zero(cls, size: int) -> "VectorBase":
        """Return the zero vector of the given size.

        Example:
            >>> VectorBase.zero(3)
            VectorBase([0, 0, 0])
        """
        if size < 0:
            raise DomainError(f"size must be non negative, got {size}")
        return cls([0] * size)

    @classmethod
    def unit(cls, size: int, index: int) -> "VectorBase":
        """Return the standard basis vector with a one at ``index``.

        Example:
            >>> VectorBase.unit(3, 1)
            VectorBase([0, 1, 0])
        """
        if not 0 <= index < size:
            raise DomainError(f"index {index} is out of range for size {size}")
        entries = [0] * size
        entries[index] = 1
        return cls(entries)

    # Access.

    @property
    def entries(self) -> List[Fraction]:
        """Return the components as a list."""
        return list(self._entries)

    @property
    def size(self) -> int:
        """Return the number of components."""
        return len(self._entries)

    def __len__(self) -> int:
        return len(self._entries)

    def __getitem__(self, index: int) -> Fraction:
        return self._entries[index]

    def __iter__(self) -> Iterator[Fraction]:
        return iter(self._entries)

    def _require_same_size(self, other: "VectorBase") -> None:
        if self.size != other.size:
            raise DimensionError(
                f"vectors have incompatible sizes {self.size} and {other.size}"
            )

    # Arithmetic.

    def add(self, other: "VectorBase") -> "VectorBase":
        """Return the componentwise sum."""
        self._require_same_size(other)
        return VectorBase(a + b for a, b in zip(self._entries, other._entries))

    def subtract(self, other: "VectorBase") -> "VectorBase":
        """Return the componentwise difference."""
        self._require_same_size(other)
        return VectorBase(a - b for a, b in zip(self._entries, other._entries))

    def scale(self, factor: Any) -> "VectorBase":
        """Return the vector multiplied by a scalar."""
        multiplier = as_fraction(factor)
        return VectorBase(entry * multiplier for entry in self._entries)

    def negate(self) -> "VectorBase":
        """Return the additive inverse."""
        return self.scale(-1)

    def dot(self, other: "VectorBase") -> Fraction:
        """Return the standard inner product.

        Complexity:
            O(n) exact multiplications.
        """
        self._require_same_size(other)
        return sum(
            (a * b for a, b in zip(self._entries, other._entries)),
            Fraction(0),
        )

    def norm_squared(self) -> Fraction:
        """Return the squared Euclidean norm, exactly.

        The square root is not taken, because it is irrational in general
        and the library avoids inexact values.

        Example:
            >>> VectorBase([3, 4]).norm_squared()
            Fraction(25, 1)
        """
        return self.dot(self)

    def is_zero(self) -> bool:
        """Return whether every component is zero."""
        return all(entry == 0 for entry in self._entries)

    def is_orthogonal_to(self, other: "VectorBase") -> bool:
        """Return whether the inner product with another vector vanishes."""
        return self.dot(other) == 0

    def normalized_by_first(self) -> "VectorBase":
        """Return the vector scaled so that its first nonzero entry is one.

        This is the exact substitute for normalizing to unit length, and it
        is what the library uses to compare eigenvectors and kernel bases.

        Example:
            >>> VectorBase([0, 2, 4]).normalized_by_first()
            VectorBase([0, 1, 2])
        """
        for entry in self._entries:
            if entry != 0:
                return self.scale(Fraction(1, 1) / entry)
        return self

    # Operators.

    def __add__(self, other: "VectorBase") -> "VectorBase":
        return self.add(other)

    def __sub__(self, other: "VectorBase") -> "VectorBase":
        return self.subtract(other)

    def __neg__(self) -> "VectorBase":
        return self.negate()

    def __mul__(self, factor: Any) -> "VectorBase":
        return self.scale(factor)

    def __rmul__(self, factor: Any) -> "VectorBase":
        return self.scale(factor)

    def __eq__(self, other: object) -> bool:
        if isinstance(other, VectorBase):
            return self._entries == other._entries
        if isinstance(other, Sequence):
            try:
                return self._entries == tuple(as_fraction(item) for item in other)
            except Exception:  # pragma: no cover - non numeric sequence
                return NotImplemented
        return NotImplemented

    def __hash__(self) -> int:
        return hash(self._entries)

    def to_latex(self) -> str:
        """Return the vector as a LaTeX column vector.

        Example:
            >>> VectorBase([1, "1/2"]).to_latex()
            '\\\\begin{pmatrix} 1 \\\\\\\\ \\\\frac{1}{2} \\\\end{pmatrix}'
        """
        from .rationals import fraction_to_latex

        body = r" \\ ".join(fraction_to_latex(entry) for entry in self._entries)
        return r"\begin{pmatrix} " + body + r" \end{pmatrix}"

    def __repr__(self) -> str:
        inner = ", ".join(fraction_to_text(entry) for entry in self._entries)
        return f"VectorBase([{inner}])"
