# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

"""Structural protocols shared by the domain packages.

The protocols describe capabilities rather than inheritance. A class opts in
simply by implementing the methods, which keeps the domain packages free of
mandatory base classes while still allowing static checking and, where the
protocol is marked runtime checkable, dynamic feature detection.
"""

from __future__ import annotations

from typing import Any, Dict, Iterable, Iterator, List, Protocol, runtime_checkable

from .typing import Element, StepList, Vertex

__all__ = [
    "SupportsLatex",
    "SupportsSteps",
    "Serializable",
    "SupportsCardinality",
    "SetLike",
    "RelationLike",
    "GraphLike",
    "StructureLike",
    "Renderable",
]


@runtime_checkable
class SupportsLatex(Protocol):
    """An object that can render itself as a LaTeX fragment."""

    def to_latex(self) -> str:
        """Return a LaTeX representation without surrounding math delimiters."""


@runtime_checkable
class SupportsSteps(Protocol):
    """An object that can report the derivation that produced it."""

    def steps(self) -> StepList:
        """Return the recorded derivation as a list of labelled entries."""


@runtime_checkable
class Serializable(Protocol):
    """An object with a stable, deterministic dictionary representation."""

    def to_dict(self) -> Dict[str, Any]:
        """Return a JSON compatible dictionary describing the object."""

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Serializable":
        """Rebuild the object from the output of :meth:`to_dict`."""


@runtime_checkable
class SupportsCardinality(Protocol):
    """An object with a well defined finite size."""

    def cardinality(self) -> int:
        """Return the number of members."""


@runtime_checkable
class SetLike(Protocol):
    """The minimal interface the set algebra routines rely on."""

    def __contains__(self, item: object) -> bool: ...

    def __iter__(self) -> Iterator[Element]: ...

    def __len__(self) -> int: ...


@runtime_checkable
class RelationLike(Protocol):
    """A binary relation viewed as a set of ordered pairs over a ground set."""

    @property
    def domain(self) -> Iterable[Element]: ...

    @property
    def pairs(self) -> Iterable[Any]: ...

    def holds(self, left: Element, right: Element) -> bool:
        """Return whether the pair stands in the relation."""


@runtime_checkable
class GraphLike(Protocol):
    """The minimal interface the graph algorithms rely on."""

    @property
    def directed(self) -> bool: ...

    def vertices(self) -> List[Vertex]:
        """Return the vertices in deterministic order."""

    def neighbors(self, vertex: Vertex) -> List[Vertex]:
        """Return the out neighbours of a vertex in deterministic order."""

    def weight(self, source: Vertex, target: Vertex) -> Any:
        """Return the weight of an edge."""


@runtime_checkable
class StructureLike(Protocol):
    """An algebraic structure with a carrier set and at least one operation."""

    def elements(self) -> List[Element]:
        """Return the carrier set in deterministic order."""

    def order(self) -> int:
        """Return the size of the carrier set."""

    def operate(self, left: Element, right: Element) -> Element:
        """Apply the principal binary operation."""


@runtime_checkable
class Renderable(Protocol):
    """An object a visualization backend can draw."""

    def render_data(self) -> Dict[str, Any]:
        """Return a backend independent description of the drawing."""
