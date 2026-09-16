"""The base class shared by every discrete structure in the library.

A structure is a finite carrier set together with whatever operations,
relations, or labels its domain adds. The base class fixes the parts that
must behave identically everywhere: a deterministic element order, size and
membership, equality by content, and a dictionary form for serialization.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Dict, Iterable, Iterator, List, Tuple

from ..exceptions import DomainError
from ..typing import Element
from .comparators import sorted_elements
from .element import normalize_elements
from .hashing import stable_hash
from .repr_utils import format_set

__all__ = ["Structure", "FiniteStructure"]


class Structure(ABC):
    """Abstract base class for a finite discrete structure.

    Subclasses provide :meth:`elements`. Everything else is derived, which
    keeps membership, ordering, printing, and hashing consistent across the
    seven domains.
    """

    @abstractmethod
    def elements(self) -> List[Element]:
        """Return the carrier set in deterministic order."""

    def order(self) -> int:
        """Return the number of members of the carrier set.

        The term matches the algebraic convention, where the order of a
        group is the size of its underlying set.
        """
        return len(self.elements())

    def cardinality(self) -> int:
        """Return the number of members. An alias of :meth:`order`."""
        return self.order()

    def is_empty(self) -> bool:
        """Return whether the carrier set has no members."""
        return self.order() == 0

    def contains(self, value: Any) -> bool:
        """Return whether a value is a member of the carrier set."""
        return value in self._member_set()

    def require_member(self, value: Any, name: str = "element") -> Element:
        """Return the value when it is a member, and raise otherwise.

        Raises:
            DomainError: When the value is not in the carrier set.
        """
        if not self.contains(value):
            raise DomainError(f"{name} {value!r} is not a member of {type(self).__name__}")
        return value

    def index_of(self, value: Any) -> int:
        """Return the position of a member in the deterministic order.

        Raises:
            DomainError: When the value is not in the carrier set.
        """
        try:
            return self.elements().index(value)
        except ValueError as exc:
            raise DomainError(f"{value!r} is not a member") from exc

    def _member_set(self) -> frozenset:
        """Return the carrier set as a frozen set, for fast membership."""
        return frozenset(self.elements())

    def to_dict(self) -> Dict[str, Any]:
        """Return a deterministic dictionary describing the structure."""
        return {"type": type(self).__name__, "elements": list(self.elements())}

    def signature(self) -> int:
        """Return a process independent fingerprint of the structure."""
        return stable_hash(self.to_dict())

    def __contains__(self, value: object) -> bool:
        return self.contains(value)

    def __iter__(self) -> Iterator[Element]:
        return iter(self.elements())

    def __len__(self) -> int:
        return self.order()

    def __eq__(self, other: object) -> bool:
        if isinstance(other, Structure):
            return type(self) is type(other) and self.to_dict() == other.to_dict()
        return NotImplemented

    def __hash__(self) -> int:
        return hash((type(self).__name__, tuple(self.elements())))

    def __repr__(self) -> str:
        return f"{type(self).__name__}(order={self.order()})"

    def __str__(self) -> str:
        return f"{type(self).__name__}{format_set(self.elements())}"


class FiniteStructure(Structure):
    """A structure whose carrier set is given explicitly at construction.

    Args:
        elements: The members of the carrier set. Duplicates are removed and
            the order is normalized so that two structures built from the
            same members compare equal.
        sort: Whether to sort the members into the universal total order.
            Pass ``False`` to preserve the order in which they were given,
            which matters for structures such as permutation groups where a
            natural indexing already exists.

    Example:
        >>> s = FiniteStructure([3, 1, 2, 1])
        >>> s.elements()
        [1, 2, 3]
        >>> s.order(), 2 in s
        (3, True)
        >>> FiniteStructure(["b", "a"], sort=False).elements()
        ['b', 'a']
    """

    def __init__(self, elements: Iterable[Any], sort: bool = True) -> None:
        normalized = normalize_elements(elements)
        unique: List[Element] = []
        seen = set()
        for item in normalized:
            if item not in seen:
                seen.add(item)
                unique.append(item)
        self._elements: Tuple[Element, ...] = tuple(
            sorted_elements(unique) if sort else unique
        )
        self._members = frozenset(self._elements)

    def elements(self) -> List[Element]:
        """Return the carrier set in its normalized order."""
        return list(self._elements)

    def _member_set(self) -> frozenset:
        return self._members
