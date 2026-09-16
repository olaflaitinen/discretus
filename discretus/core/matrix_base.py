# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

"""Exact matrices over the rationals.

The matrix type is immutable, arithmetic is exact, and every operation that
would normally be phrased in floating point is phrased over the rationals
instead. The linear algebra package in
:mod:`discretus.algebra.linear` builds its factorizations on this base, and
the graph package uses it for adjacency and Laplacian computations.
"""

from __future__ import annotations

from fractions import Fraction
from typing import Any, Iterable, Iterator, List, Sequence, Tuple

from ..exceptions import DimensionError, DomainError, ValidationError
from .rationals import as_fraction, fraction_to_latex, fraction_to_text
from .repr_utils import format_table
from .vector_base import VectorBase

__all__ = ["MatrixBase"]


class MatrixBase:
    """An immutable matrix of exact rational entries.

    Args:
        rows: The rows of the matrix, each of the same length.

    Raises:
        ValidationError: When the rows do not all have the same length.

    Example:
        >>> a = MatrixBase([[1, 2], [3, 4]])
        >>> a.shape
        (2, 2)
        >>> a + a
        MatrixBase([[2, 4], [6, 8]])
        >>> a * a
        MatrixBase([[7, 10], [15, 22]])
        >>> a.transpose()
        MatrixBase([[1, 3], [2, 4]])
        >>> a.trace()
        Fraction(5, 1)
    """

    __slots__ = ("_rows",)

    def __init__(self, rows: Iterable[Iterable[Any]]) -> None:
        materialized = [tuple(as_fraction(entry) for entry in row) for row in rows]
        if materialized:
            width = len(materialized[0])
            if any(len(row) != width for row in materialized):
                raise ValidationError("every row must have the same length")
        self._rows: Tuple[Tuple[Fraction, ...], ...] = tuple(materialized)

    # Construction.

    @classmethod
    def zero(cls, rows: int, columns: int) -> "MatrixBase":
        """Return the zero matrix of the given shape.

        Example:
            >>> MatrixBase.zero(1, 2)
            MatrixBase([[0, 0]])
        """
        if rows < 0 or columns < 0:
            raise DomainError("dimensions must be non negative")
        return cls([[0] * columns for _ in range(rows)])

    @classmethod
    def identity(cls, size: int) -> "MatrixBase":
        """Return the identity matrix of the given size.

        Example:
            >>> MatrixBase.identity(2)
            MatrixBase([[1, 0], [0, 1]])
        """
        if size < 0:
            raise DomainError(f"size must be non negative, got {size}")
        return cls(
            [[1 if i == j else 0 for j in range(size)] for i in range(size)]
        )

    @classmethod
    def diagonal(cls, entries: Sequence[Any]) -> "MatrixBase":
        """Return a square matrix with the given diagonal.

        Example:
            >>> MatrixBase.diagonal([1, 2])
            MatrixBase([[1, 0], [0, 2]])
        """
        size = len(entries)
        return cls(
            [
                [entries[i] if i == j else 0 for j in range(size)]
                for i in range(size)
            ]
        )

    @classmethod
    def from_columns(cls, columns: Sequence[Sequence[Any]]) -> "MatrixBase":
        """Return the matrix whose columns are the given sequences."""
        if not columns:
            return cls([])
        height = len(columns[0])
        if any(len(column) != height for column in columns):
            raise ValidationError("every column must have the same length")
        return cls(
            [[column[index] for column in columns] for index in range(height)]
        )

    # Shape and access.

    @property
    def rows(self) -> List[List[Fraction]]:
        """Return the rows as a list of lists."""
        return [list(row) for row in self._rows]

    @property
    def shape(self) -> Tuple[int, int]:
        """Return the number of rows and columns."""
        if not self._rows:
            return (0, 0)
        return (len(self._rows), len(self._rows[0]))

    @property
    def row_count(self) -> int:
        """Return the number of rows."""
        return self.shape[0]

    @property
    def column_count(self) -> int:
        """Return the number of columns."""
        return self.shape[1]

    def is_square(self) -> bool:
        """Return whether the matrix has as many rows as columns."""
        rows, columns = self.shape
        return rows == columns

    def entry(self, row: int, column: int) -> Fraction:
        """Return one entry of the matrix.

        Raises:
            DomainError: When an index is out of range.
        """
        rows, columns = self.shape
        if not 0 <= row < rows or not 0 <= column < columns:
            raise DomainError(f"index ({row}, {column}) is out of range")
        return self._rows[row][column]

    def row(self, index: int) -> VectorBase:
        """Return one row as a vector."""
        if not 0 <= index < self.row_count:
            raise DomainError(f"row {index} is out of range")
        return VectorBase(self._rows[index])

    def column(self, index: int) -> VectorBase:
        """Return one column as a vector."""
        if not 0 <= index < self.column_count:
            raise DomainError(f"column {index} is out of range")
        return VectorBase(row[index] for row in self._rows)

    def with_entry(self, row: int, column: int, value: Any) -> "MatrixBase":
        """Return a copy with one entry replaced."""
        self.entry(row, column)
        updated = self.rows
        updated[row][column] = as_fraction(value)
        return MatrixBase(updated)

    def __getitem__(self, index: int) -> List[Fraction]:
        return list(self._rows[index])

    def __iter__(self) -> Iterator[List[Fraction]]:
        return iter(self.rows)

    # Arithmetic.

    def add(self, other: "MatrixBase") -> "MatrixBase":
        """Return the entrywise sum.

        Raises:
            DimensionError: When the shapes differ.
        """
        if self.shape != other.shape:
            raise DimensionError(
                f"cannot add matrices of shapes {self.shape} and {other.shape}"
            )
        return MatrixBase(
            [
                [a + b for a, b in zip(left, right)]
                for left, right in zip(self._rows, other._rows)
            ]
        )

    def subtract(self, other: "MatrixBase") -> "MatrixBase":
        """Return the entrywise difference."""
        return self.add(other.scale(-1))

    def scale(self, factor: Any) -> "MatrixBase":
        """Return the matrix multiplied by a scalar."""
        multiplier = as_fraction(factor)
        return MatrixBase([[entry * multiplier for entry in row] for row in self._rows])

    def multiply(self, other: "MatrixBase") -> "MatrixBase":
        """Return the matrix product.

        Raises:
            DimensionError: When the inner dimensions disagree.

        Complexity:
            O(n m p) exact multiplications for shapes n by m and m by p.
        """
        if self.column_count != other.row_count:
            raise DimensionError(
                f"cannot multiply shapes {self.shape} and {other.shape}"
            )
        other_columns = [other.column(index) for index in range(other.column_count)]
        return MatrixBase(
            [
                [VectorBase(row).dot(column) for column in other_columns]
                for row in self._rows
            ]
        )

    def apply(self, vector: VectorBase) -> VectorBase:
        """Return the image of a vector under the matrix.

        Raises:
            DimensionError: When the vector length does not match.
        """
        if vector.size != self.column_count:
            raise DimensionError(
                f"cannot apply shape {self.shape} to a vector of size {vector.size}"
            )
        return VectorBase(VectorBase(row).dot(vector) for row in self._rows)

    def power(self, exponent: int) -> "MatrixBase":
        """Return an integer power of a square matrix by repeated squaring.

        Args:
            exponent: A non negative integer.

        Raises:
            DomainError: When the matrix is not square or the exponent is
                negative.

        Complexity:
            O(n^3 log exponent) exact multiplications.

        Example:
            >>> MatrixBase([[1, 1], [1, 0]]).power(10)
            MatrixBase([[89, 55], [55, 34]])
        """
        if not self.is_square():
            raise DomainError("only a square matrix can be raised to a power")
        if exponent < 0:
            raise DomainError(f"exponent must be non negative, got {exponent}")
        result = MatrixBase.identity(self.row_count)
        base = self
        remaining = exponent
        while remaining:
            if remaining & 1:
                result = result.multiply(base)
            remaining >>= 1
            if remaining:
                base = base.multiply(base)
        return result

    def transpose(self) -> "MatrixBase":
        """Return the transpose."""
        rows, columns = self.shape
        return MatrixBase(
            [[self._rows[i][j] for i in range(rows)] for j in range(columns)]
        )

    def trace(self) -> Fraction:
        """Return the sum of the diagonal entries.

        Raises:
            DomainError: When the matrix is not square.
        """
        if not self.is_square():
            raise DomainError("only a square matrix has a trace")
        return sum((self._rows[i][i] for i in range(self.row_count)), Fraction(0))

    # Structure.

    def submatrix(self, skip_row: int, skip_column: int) -> "MatrixBase":
        """Return the matrix with one row and one column removed.

        Example:
            >>> MatrixBase([[1, 2], [3, 4]]).submatrix(0, 0)
            MatrixBase([[4]])
        """
        rows, columns = self.shape
        if not 0 <= skip_row < rows or not 0 <= skip_column < columns:
            raise DomainError("the row or column to skip is out of range")
        return MatrixBase(
            [
                [entry for index, entry in enumerate(row) if index != skip_column]
                for position, row in enumerate(self._rows)
                if position != skip_row
            ]
        )

    def swap_rows(self, first: int, second: int) -> "MatrixBase":
        """Return a copy with two rows exchanged."""
        updated = self.rows
        updated[first], updated[second] = updated[second], updated[first]
        return MatrixBase(updated)

    def scale_row(self, index: int, factor: Any) -> "MatrixBase":
        """Return a copy with one row multiplied by a scalar."""
        multiplier = as_fraction(factor)
        updated = self.rows
        updated[index] = [entry * multiplier for entry in updated[index]]
        return MatrixBase(updated)

    def add_row_multiple(self, target: int, source: int, factor: Any) -> "MatrixBase":
        """Return a copy with a multiple of one row added to another."""
        multiplier = as_fraction(factor)
        updated = self.rows
        updated[target] = [
            entry + multiplier * other
            for entry, other in zip(updated[target], updated[source])
        ]
        return MatrixBase(updated)

    def is_symmetric(self) -> bool:
        """Return whether the matrix equals its transpose."""
        return self.is_square() and self._rows == self.transpose()._rows

    def is_diagonal(self) -> bool:
        """Return whether every off diagonal entry is zero."""
        if not self.is_square():
            return False
        return all(
            entry == 0
            for i, row in enumerate(self._rows)
            for j, entry in enumerate(row)
            if i != j
        )

    def is_identity(self) -> bool:
        """Return whether the matrix is the identity."""
        return self.is_square() and self._rows == MatrixBase.identity(self.row_count)._rows

    # Operators and rendering.

    def __add__(self, other: "MatrixBase") -> "MatrixBase":
        return self.add(other)

    def __sub__(self, other: "MatrixBase") -> "MatrixBase":
        return self.subtract(other)

    def __neg__(self) -> "MatrixBase":
        return self.scale(-1)

    def __mul__(self, other: Any) -> Any:
        if isinstance(other, MatrixBase):
            return self.multiply(other)
        if isinstance(other, VectorBase):
            return self.apply(other)
        return self.scale(other)

    def __rmul__(self, other: Any) -> "MatrixBase":
        return self.scale(other)

    def __pow__(self, exponent: int) -> "MatrixBase":
        return self.power(exponent)

    def __eq__(self, other: object) -> bool:
        if isinstance(other, MatrixBase):
            return self._rows == other._rows
        return NotImplemented

    def __hash__(self) -> int:
        return hash(self._rows)

    def to_latex(self) -> str:
        """Return the matrix as a LaTeX ``pmatrix`` environment.

        Example:
            >>> MatrixBase([[1, 2]]).to_latex()
            '\\\\begin{pmatrix} 1 & 2 \\\\end{pmatrix}'
        """
        body = r" \\ ".join(
            " & ".join(fraction_to_latex(entry) for entry in row) for row in self._rows
        )
        return r"\begin{pmatrix} " + body + r" \end{pmatrix}"

    def to_text(self) -> str:
        """Return the matrix as an aligned text table.

        Example:
            >>> print(MatrixBase([[1, 20], [3, 4]]).to_text())
            1 | 20
            3 | 4
        """
        return format_table([[fraction_to_text(entry) for entry in row] for row in self._rows])

    def __repr__(self) -> str:
        inner = ", ".join(
            "[" + ", ".join(fraction_to_text(entry) for entry in row) + "]"
            for row in self._rows
        )
        return f"MatrixBase([{inner}])"
