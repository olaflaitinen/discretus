# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

"""The base class for binary relations.

A binary relation on a ground set is a set of ordered pairs. The base class
implements the property tests, the closures, and the matrix and graph views
once, so that the relation types in :mod:`discretus.sets.relations`, the
order types in :mod:`discretus.sets.orders`, and the equivalence machinery
all agree on what reflexivity, symmetry, and transitivity mean.
"""

from __future__ import annotations

from itertools import product
from typing import Any, Dict, FrozenSet, Iterable, List, Set, Tuple

from ..exceptions import DomainError
from ..typing import Element, Pair
from .comparators import sorted_elements
from .element import normalize_element
from .repr_utils import format_pairs, format_set
from .structure import Structure

__all__ = ["RelationBase"]


class RelationBase(Structure):
    """A binary relation over a finite ground set.

    Args:
        domain: The ground set the relation is defined on.
        pairs: The ordered pairs that stand in the relation.
        infer_domain: When true, endpoints appearing in the pairs are added
            to the ground set instead of being rejected.

    Raises:
        DomainError: When a pair mentions a value outside the ground set and
            ``infer_domain`` is false.

    Example:
        >>> r = RelationBase(domain={1, 2, 3}, pairs={(1, 2), (2, 3)})
        >>> r.holds(1, 2), r.holds(2, 1)
        (True, False)
        >>> r.is_transitive()
        False
        >>> sorted(r.transitive_closure().pairs)
        [(1, 2), (1, 3), (2, 3)]
    """

    def __init__(
        self,
        domain: Iterable[Any],
        pairs: Iterable[Tuple[Any, Any]] = (),
        infer_domain: bool = False,
    ) -> None:
        ground: Set[Element] = {normalize_element(item) for item in domain}
        normalized: Set[Pair] = set()
        for pair in pairs:
            if len(tuple(pair)) != 2:
                raise DomainError(f"{pair!r} is not an ordered pair")
            left, right = (normalize_element(part) for part in pair)
            if infer_domain:
                ground.update((left, right))
            else:
                for endpoint in (left, right):
                    if endpoint not in ground:
                        raise DomainError(
                            f"{endpoint!r} appears in a pair but is not in the "
                            "ground set"
                        )
            normalized.add((left, right))
        self._domain: Tuple[Element, ...] = tuple(sorted_elements(ground))
        self._members = frozenset(self._domain)
        self._pairs: FrozenSet[Pair] = frozenset(normalized)

    # Access.

    def elements(self) -> List[Element]:
        """Return the ground set in deterministic order."""
        return list(self._domain)

    @property
    def domain(self) -> List[Element]:
        """Return the ground set in deterministic order."""
        return list(self._domain)

    @property
    def pairs(self) -> FrozenSet[Pair]:
        """Return the ordered pairs of the relation."""
        return self._pairs

    def holds(self, left: Any, right: Any) -> bool:
        """Return whether an ordered pair stands in the relation."""
        return (normalize_element(left), normalize_element(right)) in self._pairs

    def image_of(self, element: Any) -> List[Element]:
        """Return the successors of an element.

        Example:
            >>> RelationBase({1, 2}, {(1, 2), (1, 1)}).image_of(1)
            [1, 2]
        """
        value = normalize_element(element)
        return sorted_elements(
            right for left, right in self._pairs if left == value
        )

    def preimage_of(self, element: Any) -> List[Element]:
        """Return the predecessors of an element."""
        value = normalize_element(element)
        return sorted_elements(left for left, right in self._pairs if right == value)

    def _rebuild(self, pairs: Iterable[Pair]) -> "RelationBase":
        """Return a relation of the same type over the same ground set."""
        return type(self)(self._domain, pairs)

    # Properties.

    def is_reflexive(self) -> bool:
        """Return whether every element is related to itself.

        Complexity:
            O(n) membership tests.
        """
        return all((item, item) in self._pairs for item in self._domain)

    def is_irreflexive(self) -> bool:
        """Return whether no element is related to itself."""
        return not any((item, item) in self._pairs for item in self._domain)

    def is_symmetric(self) -> bool:
        """Return whether the relation equals its converse.

        Complexity:
            O(|R|) membership tests.
        """
        return all((right, left) in self._pairs for left, right in self._pairs)

    def is_antisymmetric(self) -> bool:
        """Return whether related distinct elements are never mutually related."""
        return all(
            left == right or (right, left) not in self._pairs
            for left, right in self._pairs
        )

    def is_asymmetric(self) -> bool:
        """Return whether the relation is antisymmetric and irreflexive."""
        return self.is_irreflexive() and self.is_antisymmetric()

    def is_transitive(self) -> bool:
        """Return whether composition with itself adds nothing.

        Complexity:
            O(|R| * n) membership tests.
        """
        successors: Dict[Element, Set[Element]] = {item: set() for item in self._domain}
        for left, right in self._pairs:
            successors[left].add(right)
        for left, right in self._pairs:
            for far in successors[right]:
                if (left, far) not in self._pairs:
                    return False
        return True

    def is_total(self) -> bool:
        """Return whether every two distinct elements are comparable."""
        for left, right in product(self._domain, repeat=2):
            if left == right:
                continue
            if (left, right) not in self._pairs and (right, left) not in self._pairs:
                return False
        return True

    def is_equivalence(self) -> bool:
        """Return whether the relation is reflexive, symmetric, and transitive."""
        return self.is_reflexive() and self.is_symmetric() and self.is_transitive()

    def is_partial_order(self) -> bool:
        """Return whether the relation is reflexive, antisymmetric, transitive."""
        return self.is_reflexive() and self.is_antisymmetric() and self.is_transitive()

    def is_preorder(self) -> bool:
        """Return whether the relation is reflexive and transitive."""
        return self.is_reflexive() and self.is_transitive()

    def is_function(self) -> bool:
        """Return whether every element has exactly one successor."""
        seen: Set[Element] = set()
        for left, _ in self._pairs:
            if left in seen:
                return False
            seen.add(left)
        return len(seen) == len(self._domain)

    def properties(self) -> Dict[str, bool]:
        """Return every property test as a dictionary.

        Example:
            >>> RelationBase({1}, {(1, 1)}).properties()["reflexive"]
            True
        """
        return {
            "reflexive": self.is_reflexive(),
            "irreflexive": self.is_irreflexive(),
            "symmetric": self.is_symmetric(),
            "antisymmetric": self.is_antisymmetric(),
            "asymmetric": self.is_asymmetric(),
            "transitive": self.is_transitive(),
            "total": self.is_total(),
            "equivalence": self.is_equivalence(),
            "partial_order": self.is_partial_order(),
        }

    # Derived relations.

    def converse(self) -> "RelationBase":
        """Return the relation with every pair reversed.

        Example:
            >>> sorted(RelationBase({1, 2}, {(1, 2)}).converse().pairs)
            [(2, 1)]
        """
        return self._rebuild((right, left) for left, right in self._pairs)

    def complement(self) -> "RelationBase":
        """Return the pairs of the ground set square that are not related."""
        return self._rebuild(
            pair for pair in product(self._domain, repeat=2) if pair not in self._pairs
        )

    def union(self, other: "RelationBase") -> "RelationBase":
        """Return the union with another relation over the same ground set."""
        return self._rebuild(self._pairs | other.pairs)

    def intersection(self, other: "RelationBase") -> "RelationBase":
        """Return the intersection with another relation."""
        return self._rebuild(self._pairs & other.pairs)

    def difference(self, other: "RelationBase") -> "RelationBase":
        """Return the pairs present here and absent from another relation."""
        return self._rebuild(self._pairs - other.pairs)

    def compose(self, other: "RelationBase") -> "RelationBase":
        """Return the composition, applying this relation first.

        Complexity:
            O(|R| * |S|) in the worst case.

        Example:
            >>> first = RelationBase({1, 2, 3}, {(1, 2)})
            >>> second = RelationBase({1, 2, 3}, {(2, 3)})
            >>> sorted(first.compose(second).pairs)
            [(1, 3)]
        """
        successors: Dict[Element, Set[Element]] = {}
        for left, right in other.pairs:
            successors.setdefault(left, set()).add(right)
        composed = {
            (left, far)
            for left, middle in self._pairs
            for far in successors.get(middle, ())
        }
        return self._rebuild(composed)

    def reflexive_closure(self) -> "RelationBase":
        """Return the least reflexive relation containing this one."""
        return self._rebuild(
            self._pairs | {(item, item) for item in self._domain}
        )

    def symmetric_closure(self) -> "RelationBase":
        """Return the least symmetric relation containing this one."""
        return self._rebuild(
            self._pairs | {(right, left) for left, right in self._pairs}
        )

    def transitive_closure(self) -> "RelationBase":
        """Return the least transitive relation containing this one.

        The implementation is the Warshall algorithm over the adjacency
        matrix of the relation.

        Complexity:
            O(n^3) boolean operations for a ground set of size n.
        """
        index = {item: position for position, item in enumerate(self._domain)}
        size = len(self._domain)
        reachable = [[False] * size for _ in range(size)]
        for left, right in self._pairs:
            reachable[index[left]][index[right]] = True
        for middle in range(size):
            row_middle = reachable[middle]
            for start in range(size):
                if reachable[start][middle]:
                    row_start = reachable[start]
                    for end in range(size):
                        if row_middle[end]:
                            row_start[end] = True
        return self._rebuild(
            (self._domain[start], self._domain[end])
            for start in range(size)
            for end in range(size)
            if reachable[start][end]
        )

    def equivalence_closure(self) -> "RelationBase":
        """Return the least equivalence relation containing this one."""
        return self.reflexive_closure().symmetric_closure().transitive_closure()

    # Views.

    def matrix(self) -> List[List[int]]:
        """Return the adjacency matrix with rows and columns in element order.

        Example:
            >>> RelationBase({1, 2}, {(1, 2)}).matrix()
            [[0, 1], [0, 0]]
        """
        index = {item: position for position, item in enumerate(self._domain)}
        size = len(self._domain)
        grid = [[0] * size for _ in range(size)]
        for left, right in self._pairs:
            grid[index[left]][index[right]] = 1
        return grid

    def adjacency(self) -> Dict[Element, List[Element]]:
        """Return the relation as a mapping from elements to successors."""
        return {item: self.image_of(item) for item in self._domain}

    def to_dict(self) -> Dict[str, Any]:
        """Return a deterministic dictionary describing the relation."""
        return {
            "type": type(self).__name__,
            "domain": list(self._domain),
            "pairs": sorted_elements(self._pairs),
        }

    def __len__(self) -> int:
        return len(self._pairs)

    def __contains__(self, item: object) -> bool:
        if isinstance(item, tuple) and len(item) == 2:
            return self.holds(item[0], item[1])
        return item in self._members

    def __eq__(self, other: object) -> bool:
        if isinstance(other, RelationBase):
            return (
                self._members == other._members and self._pairs == other._pairs
            )
        return NotImplemented

    def __hash__(self) -> int:
        return hash((self._members, self._pairs))

    def __repr__(self) -> str:
        return (
            f"{type(self).__name__}(domain={format_set(self._domain)}, "
            f"pairs={format_pairs(self._pairs)})"
        )
