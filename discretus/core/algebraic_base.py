"""Interfaces for algebraic structures with one or two operations.

The hierarchy follows the standard chain of successively stronger axioms::

    Magma           closure
    Semigroup       closure, associativity
    Monoid          closure, associativity, identity
    GroupBase       closure, associativity, identity, inverses
    RingBase        an abelian additive group and a multiplicative monoid

Each class verifies exactly the axioms it adds, so a subclass never repeats
a check its parent already performed. Verification happens on construction
by default, which means an object of one of these types is guaranteed to
satisfy its axioms for its whole lifetime.
"""

from __future__ import annotations

from typing import Any, Callable, Dict, Iterable, List, Optional, Tuple

from ..exceptions import AxiomViolationError, DomainError
from ..typing import Element
from .operation import BinaryOperation
from .structure import Structure

__all__ = ["Magma", "Semigroup", "Monoid", "GroupBase", "RingBase"]


class Magma(Structure):
    """A carrier set with one closed binary operation.

    Args:
        carrier: The members of the structure.
        operation: A two argument callable, or a
            :class:`~discretus.core.operation.BinaryOperation`.
        symbol: Notation used when the operation is printed.
        verify: Whether to check the axioms on construction.

    Example:
        >>> m = Magma([0, 1, 2], lambda a, b: (a + b) % 3, symbol="+")
        >>> m.operate(2, 2), m.order()
        (1, 3)
    """

    #: Name used in axiom violation messages.
    structure_name = "magma"

    def __init__(
        self,
        carrier: Iterable[Any],
        operation: Any,
        symbol: str = "*",
        verify: bool = True,
    ) -> None:
        if isinstance(operation, BinaryOperation):
            self._operation = operation
        else:
            self._operation = BinaryOperation(
                carrier, operation, symbol=symbol, check_closure=verify
            )
        if verify:
            self.verify_axioms()

    @property
    def operation(self) -> BinaryOperation:
        """Return the underlying binary operation."""
        return self._operation

    def elements(self) -> List[Element]:
        """Return the carrier set in deterministic order."""
        return self._operation.carrier

    def operate(self, left: Any, right: Any) -> Element:
        """Apply the operation to two members."""
        return self._operation.apply(left, right)

    def axioms(self) -> Tuple[str, ...]:
        """Return the names of the axioms this class guarantees."""
        return ("closure",)

    def verify_axioms(self) -> None:
        """Raise :class:`AxiomViolationError` when an axiom fails."""
        self._operation.verify_closure()

    def satisfies_axioms(self) -> bool:
        """Return whether the axioms hold, without raising."""
        try:
            self.verify_axioms()
        except AxiomViolationError:
            return False
        return True

    def is_commutative(self) -> bool:
        """Return whether the operation is commutative."""
        return self._operation.is_commutative()

    def is_abelian(self) -> bool:
        """Return whether the operation is commutative. An alias."""
        return self.is_commutative()

    def cayley_table(self) -> str:
        """Return the Cayley table of the operation rendered as text."""
        return self._operation.cayley_table()

    def to_dict(self) -> Dict[str, Any]:
        """Return a dictionary describing the structure."""
        return {
            "type": type(self).__name__,
            "elements": list(self.elements()),
            "table": self._operation.rows(),
            "symbol": self._operation.symbol,
        }

    def __repr__(self) -> str:
        return f"{type(self).__name__}(order={self.order()})"


class Semigroup(Magma):
    """A magma whose operation is associative.

    Example:
        >>> s = Semigroup([1, 2, 3], min)
        >>> s.satisfies_axioms()
        True
    """

    structure_name = "semigroup"

    def axioms(self) -> Tuple[str, ...]:
        return ("closure", "associativity")

    def verify_axioms(self) -> None:
        super().verify_axioms()
        counterexample = self._operation.associativity_counterexample()
        if counterexample is not None:
            a, b, c = counterexample
            raise AxiomViolationError(
                "associativity",
                f"({a!r} {self._operation.symbol} {b!r}) "
                f"{self._operation.symbol} {c!r} differs from "
                f"{a!r} {self._operation.symbol} ({b!r} "
                f"{self._operation.symbol} {c!r})",
            )

    def power(self, element: Any, exponent: int) -> Element:
        """Return the element combined with itself ``exponent`` times.

        The result is computed by repeated squaring, which needs
        ``O(log exponent)`` applications of the operation.

        Args:
            element: A member of the carrier set.
            exponent: A positive integer.

        Raises:
            DomainError: When the exponent is not positive.

        Example:
            >>> s = Semigroup([0, 1, 2], lambda a, b: (a + b) % 3, symbol="+")
            >>> s.power(2, 5)
            1
        """
        if exponent < 1:
            raise DomainError(f"exponent must be positive, got {exponent}")
        self.require_member(element)
        result: Optional[Element] = None
        base = element
        remaining = exponent
        while remaining:
            if remaining & 1:
                result = base if result is None else self.operate(result, base)
            remaining >>= 1
            if remaining:
                base = self.operate(base, base)
        assert result is not None
        return result


class Monoid(Semigroup):
    """A semigroup with a two sided identity.

    Example:
        >>> m = Monoid([0, 1, 2, 3], lambda a, b: (a * b) % 4, symbol=".")
        >>> m.identity()
        1
        >>> m.power(3, 0)
        1
    """

    structure_name = "monoid"

    def axioms(self) -> Tuple[str, ...]:
        return ("closure", "associativity", "identity")

    def verify_axioms(self) -> None:
        super().verify_axioms()
        self._operation.require_identity()

    def identity(self) -> Element:
        """Return the identity member."""
        return self._operation.require_identity()

    def power(self, element: Any, exponent: int) -> Element:
        """Return the element combined with itself ``exponent`` times.

        Unlike the semigroup version the exponent may be zero, which yields
        the identity.

        Raises:
            DomainError: When the exponent is negative.
        """
        if exponent < 0:
            raise DomainError(f"exponent must be non negative, got {exponent}")
        if exponent == 0:
            self.require_member(element)
            return self.identity()
        return super().power(element, exponent)

    def units(self) -> List[Element]:
        """Return the members that have a two sided inverse.

        Example:
            >>> Monoid([0, 1, 2, 3], lambda a, b: (a * b) % 4, symbol=".").units()
            [1, 3]
        """
        return [
            item
            for item in self.elements()
            if self._operation.inverse(item) is not None
        ]

    def is_idempotent_monoid(self) -> bool:
        """Return whether every member is its own product."""
        return self._operation.is_idempotent()


class GroupBase(Monoid):
    """A monoid in which every member has a two sided inverse.

    The class implements the group behaviour that does not depend on how the
    group was presented. The concrete families in
    :mod:`discretus.algebra.groups` build on it.

    Example:
        >>> g = GroupBase([0, 1, 2, 3], lambda a, b: (a + b) % 4, symbol="+")
        >>> g.inverse(1), g.element_order(1), g.is_abelian()
        (3, 4, True)
    """

    structure_name = "group"

    def axioms(self) -> Tuple[str, ...]:
        return ("closure", "associativity", "identity", "inverses")

    def verify_axioms(self) -> None:
        super().verify_axioms()
        for item in self.elements():
            if self._operation.inverse(item) is None:
                raise AxiomViolationError(
                    "inverses", f"{item!r} has no two sided inverse"
                )

    def inverse(self, element: Any) -> Element:
        """Return the inverse of a member."""
        self.require_member(element)
        found = self._operation.inverse(element)
        if found is None:  # pragma: no cover - prevented by verify_axioms
            raise AxiomViolationError("inverses", f"{element!r} has no inverse")
        return found

    def power(self, element: Any, exponent: int) -> Element:
        """Return an integer power of a member, allowing negative exponents.

        Example:
            >>> g = GroupBase([0, 1, 2, 3], lambda a, b: (a + b) % 4, symbol="+")
            >>> g.power(1, -1), g.power(1, 6)
            (3, 2)
        """
        if exponent < 0:
            return super().power(self.inverse(element), -exponent)
        return super().power(element, exponent)

    def element_order(self, element: Any) -> int:
        """Return the least positive ``k`` with ``element ** k`` the identity.

        Complexity:
            O(n) applications of the operation for a group of order n.
        """
        self.require_member(element)
        identity = self.identity()
        current = element
        order = 1
        while current != identity:
            current = self.operate(current, element)
            order += 1
            if order > self.order():  # pragma: no cover - guards a broken table
                raise AxiomViolationError("inverses", "element has no finite order")
        return order

    def element_orders(self) -> Dict[Element, int]:
        """Return the order of every member."""
        return {item: self.element_order(item) for item in self.elements()}

    def commutator(self, left: Any, right: Any) -> Element:
        """Return the commutator of two members.

        The commutator is the product of the inverses of both members with
        both members, and it is the identity precisely when they commute.
        """
        return self.operate(
            self.operate(self.inverse(left), self.inverse(right)),
            self.operate(left, right),
        )


class RingBase(Structure):
    """A carrier set with an abelian additive group and a multiplicative monoid.

    Args:
        carrier: The members of the ring.
        addition: The additive operation.
        multiplication: The multiplicative operation.
        verify: Whether to check the axioms on construction, including
            distributivity.

    Example:
        >>> r = RingBase([0, 1, 2, 3], lambda a, b: (a + b) % 4, lambda a, b: (a * b) % 4)
        >>> r.zero(), r.one(), r.is_commutative()
        (0, 1, True)
        >>> r.negate(3), r.multiply(2, 3)
        (1, 2)
    """

    structure_name = "ring"

    def __init__(
        self,
        carrier: Iterable[Any],
        addition: Callable[[Any, Any], Any],
        multiplication: Callable[[Any, Any], Any],
        verify: bool = True,
    ) -> None:
        members = list(carrier)
        self._additive = GroupBase(members, addition, symbol="+", verify=verify)
        self._multiplicative = Monoid(members, multiplication, symbol=".", verify=verify)
        if verify:
            self.verify_axioms()

    @property
    def additive_group(self) -> GroupBase:
        """Return the additive group of the ring."""
        return self._additive

    @property
    def multiplicative_monoid(self) -> Monoid:
        """Return the multiplicative monoid of the ring."""
        return self._multiplicative

    def elements(self) -> List[Element]:
        """Return the carrier set in deterministic order."""
        return self._additive.elements()

    def add(self, left: Any, right: Any) -> Element:
        """Return the sum of two members."""
        return self._additive.operate(left, right)

    def multiply(self, left: Any, right: Any) -> Element:
        """Return the product of two members."""
        return self._multiplicative.operate(left, right)

    def zero(self) -> Element:
        """Return the additive identity."""
        return self._additive.identity()

    def one(self) -> Element:
        """Return the multiplicative identity."""
        return self._multiplicative.identity()

    def negate(self, element: Any) -> Element:
        """Return the additive inverse of a member."""
        return self._additive.inverse(element)

    def subtract(self, left: Any, right: Any) -> Element:
        """Return the difference of two members."""
        return self.add(left, self.negate(right))

    def is_commutative(self) -> bool:
        """Return whether multiplication is commutative."""
        return self._multiplicative.is_commutative()

    def axioms(self) -> Tuple[str, ...]:
        """Return the names of the axioms this class guarantees."""
        return (
            "additive abelian group",
            "multiplicative monoid",
            "distributivity",
        )

    def verify_axioms(self) -> None:
        """Raise when the ring axioms fail.

        Complexity:
            O(n^3) operation evaluations for a carrier of size n, dominated
            by associativity and distributivity.
        """
        if not self._additive.is_commutative():
            raise AxiomViolationError("additive commutativity")
        for a in self.elements():
            for b in self.elements():
                for c in self.elements():
                    left = self.multiply(a, self.add(b, c))
                    right = self.add(self.multiply(a, b), self.multiply(a, c))
                    if left != right:
                        raise AxiomViolationError(
                            "left distributivity",
                            f"a={a!r}, b={b!r}, c={c!r}",
                        )
                    left = self.multiply(self.add(b, c), a)
                    right = self.add(self.multiply(b, a), self.multiply(c, a))
                    if left != right:
                        raise AxiomViolationError(
                            "right distributivity",
                            f"a={a!r}, b={b!r}, c={c!r}",
                        )

    def satisfies_axioms(self) -> bool:
        """Return whether the ring axioms hold, without raising."""
        try:
            self.verify_axioms()
        except AxiomViolationError:
            return False
        return True

    def to_dict(self) -> Dict[str, Any]:
        """Return a dictionary describing the ring."""
        return {
            "type": type(self).__name__,
            "elements": list(self.elements()),
            "addition": self._additive.operation.rows(),
            "multiplication": self._multiplicative.operation.rows(),
        }
