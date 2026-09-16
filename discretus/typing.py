# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

"""Shared type aliases used across the library.

The aliases are deliberately structural and permissive. They document intent
at call sites without forcing a particular container on the caller, which
keeps the seven domain packages interoperable.
"""

from __future__ import annotations

from fractions import Fraction
from typing import (
    Any,
    Callable,
    Dict,
    FrozenSet,
    Hashable,
    Iterable,
    Iterator,
    List,
    Mapping,
    MutableMapping,
    Optional,
    Sequence,
    Set,
    Tuple,
    TypeVar,
    Union,
)

__all__ = [
    "T",
    "S",
    "K",
    "V",
    "Element",
    "Elements",
    "Pair",
    "Triple",
    "Number",
    "Exact",
    "Weight",
    "Scalar",
    "Vertex",
    "Edge",
    "WeightedEdge",
    "EdgeLike",
    "AdjacencyMap",
    "AdjacencySets",
    "Matrix",
    "MutableMatrix",
    "IntMatrix",
    "BoolMatrix",
    "VectorLike",
    "Assignment",
    "PartialAssignment",
    "Literal",
    "Clause",
    "CnfFormula",
    "Predicate",
    "BinaryOperation",
    "UnaryOperation",
    "Comparator",
    "KeyFunction",
    "Seed",
    "PairSet",
    "Partition",
    "StepList",
]

T = TypeVar("T")
S = TypeVar("S")
K = TypeVar("K", bound=Hashable)
V = TypeVar("V")

#: A member of a discrete structure. Elements must be hashable so that they
#: can live in sets and act as dictionary keys.
Element = Hashable
Elements = Iterable[Element]

Pair = Tuple[Element, Element]
Triple = Tuple[Element, Element, Element]

#: Any numeric value the library accepts as input.
Number = Union[int, float, Fraction]
#: Values for which the library guarantees exact arithmetic.
Exact = Union[int, Fraction]
#: An edge weight. Integers and fractions keep results exact.
Weight = Union[int, float, Fraction]
Scalar = Union[int, float, Fraction]

#: A graph vertex. Any hashable value may be used as a vertex label.
Vertex = Hashable
#: An unweighted edge as an ordered pair of endpoints.
Edge = Tuple[Vertex, Vertex]
#: A weighted edge as a triple of two endpoints and a weight.
WeightedEdge = Tuple[Vertex, Vertex, Weight]
#: Either edge shape, accepted by the bulk insertion helpers.
EdgeLike = Union[Edge, WeightedEdge]

#: Adjacency with weights, mapping each vertex to its neighbours.
AdjacencyMap = Dict[Vertex, Dict[Vertex, Weight]]
#: Adjacency without weights.
AdjacencySets = Dict[Vertex, Set[Vertex]]

Matrix = Sequence[Sequence[Scalar]]
MutableMatrix = List[List[Scalar]]
IntMatrix = List[List[int]]
BoolMatrix = List[List[bool]]
VectorLike = Sequence[Scalar]

#: A total truth assignment mapping every variable name to a truth value.
Assignment = Mapping[str, bool]
#: A partial truth assignment, where absent names are undecided.
PartialAssignment = MutableMapping[str, bool]

#: A signed integer literal in the DIMACS convention, where the sign is the
#: polarity and the magnitude is the one based variable index.
Literal = int
Clause = FrozenSet[Literal]
CnfFormula = Sequence[Clause]

Predicate = Callable[..., bool]
BinaryOperation = Callable[[Any, Any], Any]
UnaryOperation = Callable[[Any], Any]
Comparator = Callable[[Any, Any], bool]
KeyFunction = Callable[[Any], Any]

#: Seed for a randomized routine. ``None`` means nondeterministic.
Seed = Optional[int]

PairSet = FrozenSet[Pair]
Partition = FrozenSet[FrozenSet[Element]]

#: A recorded derivation produced by the step recorder.
StepList = List[Tuple[str, Any]]

#: Re-exported for convenience so that domain modules import one module.
Iterator = Iterator
