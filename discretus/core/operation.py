# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

"""Binary operations on a finite carrier set.

The class in this module is the computational heart of the algebra package.
A group, a ring, or a lattice is a carrier set plus one or two operations,
and every axiom those structures have to satisfy is checked here once.

The operation can be given either as a callable or as a table. A callable is
convenient for the classical families, for example addition modulo n, while
a table is convenient when a structure is defined by exhibiting its Cayley
table.
"""

from __future__ import annotations

from itertools import product
from typing import Any, Callable, Dict, Iterable, List, Optional, Sequence, Tuple

from ..exceptions import AxiomViolationError, DomainError, ValidationError
from ..typing import Element
from .comparators import sorted_elements
from .element import element_repr, normalize_element
from .repr_utils import format_table

__all__ = ["BinaryOperation", "operation_from_table"]


class BinaryOperation:
    """A closed binary operation on a finite carrier set.

    Args:
        carrier: The members the operation is defined on.
        function: A two argument callable returning a member.
        symbol: Notation used when the operation is printed.
        check_closure: Whether to verify closure on construction. The check
            costs one evaluation per ordered pair.

    Raises:
        AxiomViolationError: When ``check_closure`` is set and the operation
            leaves the carrier set.

    Example:
        >>> plus = BinaryOperation([0, 1, 2], lambda a, b: (a + b) % 3, symbol="+")
        >>> plus(2, 2)
        1
        >>> plus.is_associative(), plus.is_commutative()
        (True, True)
        >>> plus.identity()
        0
        >>> plus.inverse(1)
        2
    """

    def __init__(
        self,
        carrier: Iterable[Any],
        function: Callable[[Any, Any], Any],
        symbol: str = "*",
        check_closure: bool = True,
    ) -> None:
        self._carrier: Tuple[Element, ...] = tuple(
            sorted_elements({normalize_element(item) for item in carrier})
        )
        self._members = frozenset(self._carrier)
        self._function = function
        self._symbol = symbol
        self._cache: Dict[Tuple[Element, Element], Element] = {}
        if check_closure:
            self.verify_closure()

    @property
    def carrier(self) -> List[Element]:
        """Return the carrier set in deterministic order."""
        return list(self._carrier)

    @property
    def symbol(self) -> str:
        """Return the notation used when printing the operation."""
        return self._symbol

    def order(self) -> int:
        """Return the size of the carrier set."""
        return len(self._carrier)

    def apply(self, left: Any, right: Any) -> Element:
        """Return the result of the operation on two members.

        Raises:
            DomainError: When an argument is not a member of the carrier.
        """
        key = (left, right)
        if key in self._cache:
            return self._cache[key]
        if left not in self._members:
            raise DomainError(f"{left!r} is not a member of the carrier set")
        if right not in self._members:
            raise DomainError(f"{right!r} is not a member of the carrier set")
        value = normalize_element(self._function(left, right))
        self._cache[key] = value
        return value

    def __call__(self, left: Any, right: Any) -> Element:
        return self.apply(left, right)

    # Axioms.

    def verify_closure(self) -> None:
        """Raise when the operation leaves the carrier set.

        Complexity:
            O(n^2) evaluations for a carrier of size n.
        """
        for left, right in product(self._carrier, repeat=2):
            value = normalize_element(self._function(left, right))
            if value not in self._members:
                raise AxiomViolationError(
                    "closure",
                    f"{element_repr(left)} {self._symbol} {element_repr(right)} "
                    f"= {element_repr(value)} leaves the carrier set",
                )
            self._cache[(left, right)] = value

    def is_closed(self) -> bool:
        """Return whether every product of two members is a member."""
        try:
            self.verify_closure()
        except AxiomViolationError:
            return False
        return True

    def is_associative(self) -> bool:
        """Return whether the operation is associative.

        Complexity:
            O(n^3) evaluations for a carrier of size n.
        """
        return self.associativity_counterexample() is None

    def associativity_counterexample(
        self,
    ) -> Optional[Tuple[Element, Element, Element]]:
        """Return a triple that violates associativity, or ``None``.

        Example:
            >>> minus = BinaryOperation([0, 1, 2], lambda a, b: (a - b) % 3)
            >>> minus.associativity_counterexample() is not None
            True
        """
        for a, b, c in product(self._carrier, repeat=3):
            if self.apply(self.apply(a, b), c) != self.apply(a, self.apply(b, c)):
                return (a, b, c)
        return None

    def is_commutative(self) -> bool:
        """Return whether the operation is commutative.

        Complexity:
            O(n^2) evaluations for a carrier of size n.
        """
        return self.commutativity_counterexample() is None

    def commutativity_counterexample(self) -> Optional[Tuple[Element, Element]]:
        """Return a pair that violates commutativity, or ``None``."""
        items = self._carrier
        for index, left in enumerate(items):
            for right in items[index + 1 :]:
                if self.apply(left, right) != self.apply(right, left):
                    return (left, right)
        return None

    def is_idempotent(self) -> bool:
        """Return whether every member is its own product.

        Example:
            >>> meet = BinaryOperation([1, 2], min)
            >>> meet.is_idempotent()
            True
        """
        return all(self.apply(item, item) == item for item in self._carrier)

    def identity(self) -> Optional[Element]:
        """Return the two sided identity, or ``None`` when there is none.

        Complexity:
            O(n^2) evaluations for a carrier of size n.
        """
        for candidate in self._carrier:
            if all(
                self.apply(candidate, item) == item
                and self.apply(item, candidate) == item
                for item in self._carrier
            ):
                return candidate
        return None

    def require_identity(self) -> Element:
        """Return the identity, raising when the operation has none.

        Raises:
            AxiomViolationError: When no two sided identity exists.
        """
        found = self.identity()
        if found is None:
            raise AxiomViolationError("identity", "no two sided identity exists")
        return found

    def inverse(self, element: Any) -> Optional[Element]:
        """Return the inverse of a member, or ``None`` when it has none.

        Raises:
            AxiomViolationError: When the operation has no identity.
            DomainError: When the argument is not a member.
        """
        identity = self.require_identity()
        self.apply(element, identity)
        for candidate in self._carrier:
            if (
                self.apply(element, candidate) == identity
                and self.apply(candidate, element) == identity
            ):
                return candidate
        return None

    def inverses(self) -> Dict[Element, Optional[Element]]:
        """Return the inverse of every member, using ``None`` when absent."""
        return {item: self.inverse(item) for item in self._carrier}

    def has_inverses(self) -> bool:
        """Return whether every member has a two sided inverse."""
        if self.identity() is None:
            return False
        return all(self.inverse(item) is not None for item in self._carrier)

    def is_group(self) -> bool:
        """Return whether the carrier and operation form a group.

        Example:
            >>> BinaryOperation([0, 1, 2], lambda a, b: (a + b) % 3).is_group()
            True
            >>> BinaryOperation([0, 1, 2], lambda a, b: (a * b) % 3).is_group()
            False
        """
        return self.is_closed() and self.is_associative() and self.has_inverses()

    # Derived data.

    def table(self) -> Dict[Tuple[Element, Element], Element]:
        """Return the operation as a mapping from ordered pairs to results."""
        return {
            (left, right): self.apply(left, right)
            for left, right in product(self._carrier, repeat=2)
        }

    def rows(self) -> List[List[Element]]:
        """Return the Cayley table as a list of rows."""
        return [
            [self.apply(left, right) for right in self._carrier]
            for left in self._carrier
        ]

    def cayley_table(self) -> str:
        """Return the Cayley table rendered as text.

        Example:
            >>> print(BinaryOperation([0, 1], lambda a, b: (a + b) % 2, "+").cayley_table())
            + | 0 | 1
            --+---+--
            0 | 0 | 1
            1 | 1 | 0
        """
        header = [self._symbol, *self._carrier]
        body = [
            [left, *[self.apply(left, right) for right in self._carrier]]
            for left in self._carrier
        ]
        return format_table(body, header=header)

    def is_latin_square(self) -> bool:
        """Return whether every row and column is a permutation of the carrier.

        A finite operation with an identity is a group precisely when it is
        associative and its table is a Latin square, so the check is a cheap
        necessary condition.
        """
        expected = self._members
        for row in self.rows():
            if frozenset(row) != expected:
                return False
        for index in range(self.order()):
            column = [row[index] for row in self.rows()]
            if frozenset(column) != expected:
                return False
        return True

    def restricted(self, subset: Iterable[Any]) -> "BinaryOperation":
        """Return the operation restricted to a subset of the carrier.

        Raises:
            DomainError: When the subset is not contained in the carrier.
            AxiomViolationError: When the subset is not closed.
        """
        members = [normalize_element(item) for item in subset]
        outside = [item for item in members if item not in self._members]
        if outside:
            raise DomainError(f"not members of the carrier set: {outside!r}")
        return BinaryOperation(members, self._function, self._symbol)

    def __repr__(self) -> str:
        return f"BinaryOperation(order={self.order()}, symbol={self._symbol!r})"


def operation_from_table(
    carrier: Sequence[Any],
    rows: Sequence[Sequence[Any]],
    symbol: str = "*",
) -> BinaryOperation:
    """Build an operation from an explicit Cayley table.

    Args:
        carrier: The members, in the order the table indexes them.
        rows: A square table where ``rows[i][j]`` is the product of the
            member at index ``i`` with the member at index ``j``.
        symbol: Notation used when the operation is printed.

    Returns:
        The corresponding :class:`BinaryOperation`.

    Raises:
        ValidationError: When the table is not square or its size does not
            match the carrier.

    Example:
        >>> op = operation_from_table([0, 1], [[0, 1], [1, 0]], symbol="+")
        >>> op(1, 1)
        0
    """
    size = len(carrier)
    if len(rows) != size or any(len(row) != size for row in rows):
        raise ValidationError(
            f"the table must be {size} by {size} to match the carrier set"
        )
    members = [normalize_element(item) for item in carrier]
    position = {item: index for index, item in enumerate(members)}
    lookup = {
        (members[i], members[j]): normalize_element(rows[i][j])
        for i in range(size)
        for j in range(size)
    }

    def function(left: Any, right: Any) -> Any:
        if left not in position or right not in position:
            raise DomainError(f"({left!r}, {right!r}) is outside the table")
        return lookup[(left, right)]

    return BinaryOperation(members, function, symbol)
