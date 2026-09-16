# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

"""The base class for functions between finite sets.

A function is a relation that assigns exactly one value of the codomain to
each element of the domain. The base class checks that requirement on
construction, so that an instance of this type is a genuine function, and it
implements the injectivity, surjectivity, image, and composition machinery
that the set theory package exposes.
"""

from __future__ import annotations

from typing import Any, Callable, Dict, Iterable, List, Optional, Set, Tuple

from ..exceptions import DomainError, InfeasibleError, NotAFunctionError
from ..typing import Element
from .comparators import sorted_elements
from .element import normalize_element
from .repr_utils import format_mapping, format_set
from .structure import Structure

__all__ = ["FunctionBase"]


class FunctionBase(Structure):
    """A total function between two finite sets.

    Args:
        domain: The set of arguments.
        codomain: The set the values are drawn from. Defaults to the image.
        mapping: A dictionary from each argument to its value.
        rule: A callable used to build the mapping instead of giving it.

    Raises:
        NotAFunctionError: When the mapping is not total on the domain.
        DomainError: When a value lies outside the codomain.

    Example:
        >>> f = FunctionBase(domain={1, 2, 3}, rule=lambda n: n % 2)
        >>> f(3), f.image()
        (1, [0, 1])
        >>> f.is_injective(), f.is_surjective()
        (False, True)
        >>> square = FunctionBase(domain={1, 2}, codomain={1, 4, 9}, rule=lambda n: n * n)
        >>> square.is_injective(), square.is_surjective()
        (True, False)
    """

    def __init__(
        self,
        domain: Iterable[Any],
        codomain: Optional[Iterable[Any]] = None,
        mapping: Optional[Dict[Any, Any]] = None,
        rule: Optional[Callable[[Any], Any]] = None,
    ) -> None:
        if mapping is None and rule is None:
            raise NotAFunctionError("either a mapping or a rule is required")
        if mapping is not None and rule is not None:
            raise NotAFunctionError("give either a mapping or a rule, not both")
        arguments = [normalize_element(item) for item in domain]
        unique_arguments = sorted_elements(set(arguments))
        table: Dict[Element, Element] = {}
        for argument in unique_arguments:
            if rule is not None:
                table[argument] = normalize_element(rule(argument))
            else:
                assert mapping is not None
                if argument not in mapping:
                    raise NotAFunctionError(
                        f"the mapping has no value for {argument!r}"
                    )
                table[argument] = normalize_element(mapping[argument])
        if mapping is not None:
            extra = [key for key in mapping if normalize_element(key) not in table]
            if extra:
                raise DomainError(
                    f"the mapping assigns values outside the domain: {extra!r}"
                )
        self._domain: Tuple[Element, ...] = tuple(unique_arguments)
        self._table = table
        if codomain is None:
            target = sorted_elements(set(table.values()))
        else:
            target = sorted_elements({normalize_element(item) for item in codomain})
            outside = [value for value in table.values() if value not in set(target)]
            if outside:
                raise DomainError(f"values outside the codomain: {outside!r}")
        self._codomain: Tuple[Element, ...] = tuple(target)

    # Access.

    def elements(self) -> List[Element]:
        """Return the domain in deterministic order."""
        return list(self._domain)

    @property
    def domain(self) -> List[Element]:
        """Return the domain in deterministic order."""
        return list(self._domain)

    @property
    def codomain(self) -> List[Element]:
        """Return the codomain in deterministic order."""
        return list(self._codomain)

    @property
    def mapping(self) -> Dict[Element, Element]:
        """Return a copy of the argument to value table."""
        return dict(self._table)

    def apply(self, argument: Any) -> Element:
        """Return the value at an argument.

        Raises:
            DomainError: When the argument is not in the domain.
        """
        value = normalize_element(argument)
        if value not in self._table:
            raise DomainError(f"{argument!r} is not in the domain")
        return self._table[value]

    def __call__(self, argument: Any) -> Element:
        return self.apply(argument)

    def pairs(self) -> List[Tuple[Element, Element]]:
        """Return the graph of the function as ordered pairs."""
        return [(argument, self._table[argument]) for argument in self._domain]

    # Properties.

    def image(self) -> List[Element]:
        """Return the set of attained values in deterministic order."""
        return sorted_elements(set(self._table.values()))

    def image_of(self, subset: Iterable[Any]) -> List[Element]:
        """Return the image of a subset of the domain.

        Example:
            >>> FunctionBase({1, 2, 3}, rule=lambda n: n % 2).image_of([2, 3])
            [0, 1]
        """
        return sorted_elements({self.apply(item) for item in subset})

    def preimage_of(self, subset: Iterable[Any]) -> List[Element]:
        """Return the arguments whose values lie in a subset of the codomain.

        Example:
            >>> FunctionBase({1, 2, 3}, rule=lambda n: n % 2).preimage_of([1])
            [1, 3]
        """
        targets = {normalize_element(item) for item in subset}
        return sorted_elements(
            argument
            for argument, value in self._table.items()
            if value in targets
        )

    def fiber(self, value: Any) -> List[Element]:
        """Return the arguments mapped to a single value."""
        return self.preimage_of([value])

    def is_injective(self) -> bool:
        """Return whether distinct arguments have distinct values.

        Complexity:
            O(n) with a hash set.
        """
        seen: Set[Element] = set()
        for value in self._table.values():
            if value in seen:
                return False
            seen.add(value)
        return True

    def is_surjective(self) -> bool:
        """Return whether every element of the codomain is attained."""
        return set(self._table.values()) == set(self._codomain)

    def is_bijective(self) -> bool:
        """Return whether the function is both injective and surjective."""
        return self.is_injective() and self.is_surjective()

    def is_identity(self) -> bool:
        """Return whether every argument is its own value."""
        return all(argument == value for argument, value in self._table.items())

    def is_constant(self) -> bool:
        """Return whether the function attains at most one value."""
        return len(set(self._table.values())) <= 1

    def fixed_points(self) -> List[Element]:
        """Return the arguments that are their own value.

        Example:
            >>> FunctionBase({0, 1, 2}, rule=lambda n: (n * n) % 3).fixed_points()
            [0, 1]
        """
        return sorted_elements(
            argument for argument, value in self._table.items() if argument == value
        )

    def properties(self) -> Dict[str, bool]:
        """Return the property tests as a dictionary."""
        return {
            "injective": self.is_injective(),
            "surjective": self.is_surjective(),
            "bijective": self.is_bijective(),
            "identity": self.is_identity(),
            "constant": self.is_constant(),
        }

    # Derived functions.

    def compose(self, other: "FunctionBase") -> "FunctionBase":
        """Return the composition that applies this function first.

        Raises:
            DomainError: When the image is not contained in the domain of
                the other function.

        Example:
            >>> double = FunctionBase({1, 2}, rule=lambda n: 2 * n)
            >>> succ = FunctionBase({2, 4}, rule=lambda n: n + 1)
            >>> double.compose(succ).mapping
            {1: 3, 2: 5}
        """
        outside = [value for value in self.image() if value not in set(other.domain)]
        if outside:
            raise DomainError(
                f"cannot compose: {outside!r} lie outside the second domain"
            )
        return FunctionBase(
            domain=self._domain,
            codomain=other.codomain,
            mapping={
                argument: other.apply(value) for argument, value in self._table.items()
            },
        )

    def inverse(self) -> "FunctionBase":
        """Return the inverse function.

        Raises:
            InfeasibleError: When the function is not bijective, in which
                case no inverse exists.

        Example:
            >>> FunctionBase({1, 2}, rule=lambda n: 2 * n).inverse().mapping
            {2: 1, 4: 2}
        """
        if not self.is_bijective():
            raise InfeasibleError(
                "only a bijective function has an inverse; this function is "
                f"{'not injective' if not self.is_injective() else 'not surjective'}"
            )
        return FunctionBase(
            domain=self._codomain,
            codomain=self._domain,
            mapping={value: argument for argument, value in self._table.items()},
        )

    def restricted_to(self, subset: Iterable[Any]) -> "FunctionBase":
        """Return the function restricted to a subset of the domain."""
        arguments = [normalize_element(item) for item in subset]
        outside = [item for item in arguments if item not in self._table]
        if outside:
            raise DomainError(f"not in the domain: {outside!r}")
        return FunctionBase(
            domain=arguments,
            codomain=self._codomain,
            mapping={argument: self._table[argument] for argument in arguments},
        )

    def to_dict(self) -> Dict[str, Any]:
        """Return a deterministic dictionary describing the function."""
        return {
            "type": type(self).__name__,
            "domain": list(self._domain),
            "codomain": list(self._codomain),
            "mapping": {argument: self._table[argument] for argument in self._domain},
        }

    def __eq__(self, other: object) -> bool:
        if isinstance(other, FunctionBase):
            return (
                self._table == other._table
                and set(self._codomain) == set(other._codomain)
            )
        return NotImplemented

    def __hash__(self) -> int:
        return hash((frozenset(self._table.items()), frozenset(self._codomain)))

    def __repr__(self) -> str:
        return (
            f"{type(self).__name__}(domain={format_set(self._domain)}, "
            f"mapping={format_mapping(self._table)})"
        )
