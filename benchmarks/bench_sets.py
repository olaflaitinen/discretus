# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

"""Benchmarks for the set theory package.

What is measured here, and why each measurement is worth its runtime:

    The set algebra, because it is the most frequently called code in the
    library and because its cost is linear in the total size of its
    arguments, which is a claim that a change could quietly break.

    The three set representations against one another, because the reference
    tells a reader to choose a bit set for a dense integer universe and a
    finite set for anything else, and that advice is only worth giving if the
    difference is real and measurable.

    The relation property tests, because they differ in cost from linear to
    quadratic and the reference states which is which. Transitivity is the
    expensive one, and a change that made symmetry quadratic would be
    invisible in a correctness test.

    The transitive closure, because Warshall's algorithm is cubic and a
    cubic routine is where an accidental extra loop shows up first.

    The poset machinery, because the cover relation is cubic and is cached,
    and because the cache is the difference between an interactive Hasse
    diagram and one that is not.

    The union find structure, because the near constant amortized cost it
    promises is what makes Kruskal's algorithm and connected component
    computation linear, and a regression here would slow down two other
    packages.

    Lazy enumeration, because the promise that a power set can be traversed
    without being materialized is a promise about memory that a time
    measurement can at least partially check: a routine that materializes
    first cannot produce its first element in constant time.

Every input is generated from a seed derived from the benchmark name, so a
measurement can be repeated exactly. The element types are varied
deliberately: several benchmarks use strings rather than integers, because
the library accepts any hashable value and a routine that is fast for
integers and slow for strings is worth detecting.
"""

from __future__ import annotations

from typing import Any, List, Tuple

from . import (
    benchmark,
    random_pairs,
    random_words,
    require,
    requires_all,
    seeded,
)

# ---------------------------------------------------------------------------
# The modules under measurement
# ---------------------------------------------------------------------------
# Each is resolved once at import time. A module that is not available yet
# makes its benchmarks report as skipped rather than failing the suite, which
# is what lets this file exist while the package is still being built out.

sets_module = require("discretus.sets", "FiniteSet", "BitSet", "Multiset")
operations_module = require(
    "discretus.sets.operations", "union", "intersection", "power_set"
)
relations_module = require("discretus.sets.relations", "Relation")
equivalence_module = require(
    "discretus.sets.equivalence",
    "EquivalenceRelation",
    "Partition",
    "UnionFind",
)
orders_module = require("discretus.sets.orders", "PartialOrder", "dilworth")
functions_module = require("discretus.sets.functions", "SetFunction")

#: A group name per subject, so that a contributor can measure one area.
GROUP = "sets"
GROUP_RELATIONS = "sets.relations"
GROUP_ORDERS = "sets.orders"
GROUP_EQUIVALENCE = "sets.equivalence"
GROUP_FUNCTIONS = "sets.functions"


# ---------------------------------------------------------------------------
# Input preparation
# ---------------------------------------------------------------------------
# Setup functions are not timed. They build the input for a size and return
# it, so that the timed call does nothing but the operation being measured.


def make_two_integer_sets(size: int) -> Tuple[Any, Any]:
    """Return two finite sets of integers that overlap in half their members.

    The overlap matters. Two disjoint sets make intersection trivial and two
    identical sets make difference trivial, and neither is representative of
    how the operations are used.
    """
    assert sets_module is not None
    half = size // 2
    left = sets_module.FiniteSet(range(size))
    right = sets_module.FiniteSet(range(half, size + half))
    return left, right


def make_two_string_sets(size: int) -> Tuple[Any, Any]:
    """Return two finite sets of strings with a partial overlap.

    String members exercise the hashing and the display ordering rather than
    the integer fast paths, which is the comparison this pair is here for.
    """
    assert sets_module is not None
    words = random_words(size + size // 2, length=10, label="sets.strings")
    left = sets_module.FiniteSet(words[:size])
    right = sets_module.FiniteSet(words[size // 2 :])
    return left, right


def make_two_bit_sets(size: int) -> Tuple[Any, Any]:
    """Return two bit sets over a dense integer universe."""
    assert sets_module is not None
    half = size // 2
    return (
        sets_module.BitSet(range(size)),
        sets_module.BitSet(range(half, size + half)),
    )


def make_two_builtin_sets(size: int) -> Tuple[set, set]:
    """Return two built-in sets, as the reference point for the algebra.

    This is the honest comparison for the set operations: the library adds
    deterministic ordering, immutability, and normalization on top of the
    built-in type, and this benchmark is what makes the cost of that
    visible rather than assumed.
    """
    half = size // 2
    return set(range(size)), set(range(half, size + half))


def make_finite_set(size: int) -> Any:
    """Return one finite set of integers."""
    assert sets_module is not None
    return sets_module.FiniteSet(range(size))


def make_small_finite_set(size: int) -> Any:
    """Return a finite set small enough for an exponential enumeration.

    The size here is the exponent rather than the member count, because the
    enumerations that consume it are exponential and a linear size parameter
    would be misleading in the growth report.
    """
    assert sets_module is not None
    return sets_module.FiniteSet(range(size))


def make_sparse_relation(size: int) -> Any:
    """Return a relation with roughly two pairs per member.

    Sparse is the realistic case. A relation with a quadratic number of pairs
    is a different measurement, and it is taken separately below, because the
    property tests behave differently on the two.
    """
    assert relations_module is not None
    pairs = random_pairs(size * 2, size, label="sets.sparse_relation")
    return relations_module.Relation(domain=set(range(size)), pairs=set(pairs))


def make_dense_relation(size: int) -> Any:
    """Return a relation with a quadratic number of pairs.

    The size is deliberately smaller here, because the pair count grows as
    its square and the point is the shape rather than the scale.
    """
    assert relations_module is not None
    pairs = {(i, j) for i in range(size) for j in range(size) if (i + j) % 3}
    return relations_module.Relation(domain=set(range(size)), pairs=pairs)


def make_transitive_relation(size: int) -> Any:
    """Return a relation that is already transitive.

    A transitivity test that stops at the first violation is fast on a
    relation that violates it early and slow on one that does not. Measuring
    the transitive case is measuring the worst case, which is the number the
    reference should state.
    """
    assert relations_module is not None
    pairs = {(i, j) for i in range(size) for j in range(i + 1, size)}
    return relations_module.Relation(domain=set(range(size)), pairs=pairs)


def make_equivalence_pairs(size: int) -> Any:
    """Return the pairs of an equivalence with blocks of size five."""
    assert relations_module is not None
    pairs = {
        (i, j)
        for i in range(size)
        for j in range(size)
        if i // 5 == j // 5
    }
    return relations_module.Relation(domain=set(range(size)), pairs=pairs)


def make_divisibility_order(size: int) -> Any:
    """Return the divisibility order on the integers up to a bound.

    Divisibility is the standard example of a partial order that is not
    total, it has a rich cover relation, and its meet and join are the
    greatest common divisor and the least common multiple, so it exercises
    the lattice machinery rather than only the comparison.
    """
    assert orders_module is not None
    return orders_module.PartialOrder.from_relation(
        ground=set(range(1, size + 1)),
        leq=lambda x, y: y % x == 0,
    )


def make_subset_order(size: int) -> Any:
    """Return the subset order on the power set of a small ground set.

    The ground set is small because the poset has two to the size elements.
    This is the Boolean lattice, which is where the distributivity and
    complementation tests are exercised.
    """
    assert orders_module is not None and sets_module is not None
    ground = list(range(size))
    subsets = []
    for mask in range(1 << size):
        subsets.append(
            frozenset(value for index, value in enumerate(ground) if mask >> index & 1)
        )
    return orders_module.PartialOrder.from_relation(
        ground=set(subsets),
        leq=lambda x, y: x <= y,
    )


def make_union_find(size: int) -> Any:
    """Return a fresh disjoint set forest over a range."""
    assert equivalence_module is not None
    return equivalence_module.UnionFind(range(size))


def make_union_find_plan(size: int) -> Tuple[Any, List[Tuple[int, int]]]:
    """Return a forest and a reproducible sequence of unions to perform.

    The sequence is generated in advance so that the timed call does nothing
    but the unions, and so that two runs perform exactly the same merges.
    """
    assert equivalence_module is not None
    source = seeded("sets.union_find_plan")
    plan = [
        (source.randrange(size), source.randrange(size)) for _ in range(size * 2)
    ]
    return equivalence_module.UnionFind(range(size)), plan


def make_function(size: int) -> Any:
    """Return a function from a range to its residues modulo a small base."""
    assert functions_module is not None
    return functions_module.SetFunction(
        domain=set(range(size)),
        rule=lambda value: value % 97,
    )


# ---------------------------------------------------------------------------
# The set algebra
# ---------------------------------------------------------------------------


@benchmark(
    group=GROUP,
    sizes=[1_000, 10_000, 100_000, 1_000_000],
    complexity="O(total size)",
    setup=make_two_integer_sets,
    requires=requires_all(sets_module, operations_module),
    note="the most frequently called routine in the library",
)
def union_integers(payload: Tuple[Any, Any]) -> Any:
    """Union of two overlapping integer sets."""
    left, right = payload
    return operations_module.union(left, right)


@benchmark(
    group=GROUP,
    sizes=[1_000, 10_000, 100_000, 1_000_000],
    complexity="O(smallest size)",
    setup=make_two_integer_sets,
    requires=requires_all(sets_module, operations_module),
    note="iterates the smaller argument, so it should be cheaper than union",
)
def intersection_integers(payload: Tuple[Any, Any]) -> Any:
    """Intersection of two overlapping integer sets."""
    left, right = payload
    return operations_module.intersection(left, right)


@benchmark(
    group=GROUP,
    sizes=[1_000, 10_000, 100_000, 1_000_000],
    complexity="O(size of the first argument)",
    setup=make_two_integer_sets,
    requires=requires_all(sets_module, operations_module),
)
def difference_integers(payload: Tuple[Any, Any]) -> Any:
    """Difference of two overlapping integer sets."""
    left, right = payload
    return operations_module.difference(left, right)


@benchmark(
    group=GROUP,
    sizes=[1_000, 10_000, 100_000, 1_000_000],
    complexity="O(total size)",
    setup=make_two_integer_sets,
    requires=requires_all(sets_module, operations_module),
)
def symmetric_difference_integers(payload: Tuple[Any, Any]) -> Any:
    """Symmetric difference of two overlapping integer sets."""
    left, right = payload
    return operations_module.symmetric_difference(left, right)


@benchmark(
    group=GROUP,
    sizes=[1_000, 10_000, 100_000],
    complexity="O(total size)",
    setup=make_two_string_sets,
    requires=requires_all(sets_module, operations_module),
    note="the same operation over string members, for comparison",
)
def union_strings(payload: Tuple[Any, Any]) -> Any:
    """Union of two overlapping string sets."""
    left, right = payload
    return operations_module.union(left, right)


@benchmark(
    group=GROUP,
    sizes=[1_000, 10_000, 100_000, 1_000_000],
    complexity="O(total size)",
    setup=make_two_builtin_sets,
    requires=requires_all(sets_module, operations_module),
    note="the built-in operation, as the reference point for the two above",
)
def union_builtin(payload: Tuple[set, set]) -> set:
    """Union of two built-in sets, for comparison."""
    left, right = payload
    return left | right


@benchmark(
    group=GROUP,
    sizes=[1_000, 10_000, 100_000, 1_000_000],
    complexity="O(total size) with word level operations",
    setup=make_two_bit_sets,
    requires=requires_all(sets_module, operations_module),
    note="the representation the reference recommends for a dense universe",
)
def union_bit_sets(payload: Tuple[Any, Any]) -> Any:
    """Union of two bit sets over a dense integer universe."""
    left, right = payload
    return operations_module.union(left, right)


@benchmark(
    group=GROUP,
    sizes=[1_000, 10_000, 100_000, 1_000_000],
    complexity="O(total size) with word level operations",
    setup=make_two_bit_sets,
    requires=requires_all(sets_module, operations_module),
)
def intersection_bit_sets(payload: Tuple[Any, Any]) -> Any:
    """Intersection of two bit sets."""
    left, right = payload
    return operations_module.intersection(left, right)


@benchmark(
    group=GROUP,
    sizes=[10_000, 100_000, 1_000_000],
    complexity="O(1) average per test",
    setup=make_finite_set,
    requires=sets_module,
    note="the membership test, called inside almost every other routine",
)
def membership(collection: Any) -> int:
    """One thousand membership tests, half of them hits."""
    found = 0
    for value in range(0, 2_000, 2):
        if value in collection:
            found += 1
    return found


@benchmark(
    group=GROUP,
    sizes=[10_000, 100_000, 1_000_000],
    complexity="O(size)",
    setup=make_finite_set,
    requires=sets_module,
    note="construction, which normalizes and sorts the members",
)
def construction(collection: Any) -> Any:
    """Rebuild a finite set from the members of another."""
    return sets_module.FiniteSet(collection.members())


@benchmark(
    group=GROUP,
    sizes=[1_000, 10_000, 100_000],
    complexity="O(size) with the display ordering",
    setup=make_finite_set,
    requires=sets_module,
    note="the deterministic ordering, which is what makes output stable",
)
def ordering(collection: Any) -> List[Any]:
    """Produce the members in the universal display order."""
    return collection.members()


@benchmark(
    group=GROUP,
    sizes=[100, 1_000, 10_000],
    complexity="O(size of the first) subset tests",
    setup=make_two_integer_sets,
    requires=sets_module,
)
def subset_test(payload: Tuple[Any, Any]) -> bool:
    """Test inclusion between two overlapping sets."""
    left, right = payload
    return left.is_subset(right)


# ---------------------------------------------------------------------------
# Lazy enumeration
# ---------------------------------------------------------------------------


@benchmark(
    group=GROUP,
    sizes=[12, 16, 20],
    complexity="O(1) amortized per subset, 2 to the n subsets",
    setup=make_small_finite_set,
    requires=requires_all(sets_module, operations_module),
    note="the size is the exponent, so each step doubles the work",
)
def power_set_full(collection: Any) -> int:
    """Traverse the whole power set without materializing it."""
    return sum(1 for _ in operations_module.power_set(collection))


@benchmark(
    group=GROUP,
    sizes=[20, 200, 2_000],
    complexity="O(1) to produce the first subset",
    setup=make_small_finite_set,
    requires=requires_all(sets_module, operations_module),
    note=(
        "takes only the first ten subsets of a space with two to the size "
        "members; a routine that materialized first could not do this"
    ),
)
def power_set_prefix(collection: Any) -> int:
    """Take the first ten subsets of an astronomically large power set."""
    taken = 0
    for _ in operations_module.power_set(collection):
        taken += 1
        if taken == 10:
            break
    return taken


@benchmark(
    group=GROUP,
    sizes=[100, 300, 1_000],
    complexity="O(1) per tuple, |A| times |B| tuples",
    setup=make_two_integer_sets,
    requires=requires_all(sets_module, operations_module),
)
def cartesian_product_full(payload: Tuple[Any, Any]) -> int:
    """Traverse a Cartesian product."""
    left, right = payload
    return sum(1 for _ in operations_module.cartesian_product(left, right))


# ---------------------------------------------------------------------------
# Relations
# ---------------------------------------------------------------------------


@benchmark(
    group=GROUP_RELATIONS,
    sizes=[100, 1_000, 10_000],
    complexity="O(n) membership tests",
    setup=make_sparse_relation,
    requires=relations_module,
)
def is_reflexive_sparse(relation: Any) -> bool:
    """Test reflexivity on a sparse relation."""
    return relation.is_reflexive()


@benchmark(
    group=GROUP_RELATIONS,
    sizes=[100, 1_000, 10_000],
    complexity="O(|R|) membership tests",
    setup=make_sparse_relation,
    requires=relations_module,
)
def is_symmetric_sparse(relation: Any) -> bool:
    """Test symmetry on a sparse relation."""
    return relation.is_symmetric()


@benchmark(
    group=GROUP_RELATIONS,
    sizes=[100, 1_000, 10_000],
    complexity="O(|R| times n) membership tests",
    setup=make_sparse_relation,
    requires=relations_module,
    note="the expensive property test, and the one to watch",
)
def is_transitive_sparse(relation: Any) -> bool:
    """Test transitivity on a sparse relation."""
    return relation.is_transitive()


@benchmark(
    group=GROUP_RELATIONS,
    sizes=[50, 100, 200],
    complexity="O(|R| times n) membership tests",
    setup=make_transitive_relation,
    requires=relations_module,
    note="the worst case: the test cannot stop early because it never fails",
)
def is_transitive_worst_case(relation: Any) -> bool:
    """Test transitivity on a relation that is transitive."""
    return relation.is_transitive()


@benchmark(
    group=GROUP_RELATIONS,
    sizes=[50, 100, 200],
    complexity="O(n squared)",
    setup=make_dense_relation,
    requires=relations_module,
)
def properties_dense(relation: Any) -> dict:
    """Compute every property test at once on a dense relation."""
    return relation.properties()


@benchmark(
    group=GROUP_RELATIONS,
    sizes=[50, 100, 200, 400],
    complexity="O(n cubed) boolean operations",
    setup=make_sparse_relation,
    requires=relations_module,
    note="Warshall's algorithm, where an accidental extra loop would show",
)
def transitive_closure(relation: Any) -> Any:
    """Compute the transitive closure by Warshall's algorithm."""
    return relation.transitive_closure()


@benchmark(
    group=GROUP_RELATIONS,
    sizes=[100, 1_000, 10_000],
    complexity="O(n + |R|)",
    setup=make_sparse_relation,
    requires=relations_module,
)
def reflexive_closure(relation: Any) -> Any:
    """Compute the reflexive closure."""
    return relation.reflexive_closure()


@benchmark(
    group=GROUP_RELATIONS,
    sizes=[100, 1_000, 10_000],
    complexity="O(|R|)",
    setup=make_sparse_relation,
    requires=relations_module,
)
def symmetric_closure(relation: Any) -> Any:
    """Compute the symmetric closure."""
    return relation.symmetric_closure()


@benchmark(
    group=GROUP_RELATIONS,
    sizes=[100, 500, 1_000],
    complexity="O(|R| times |S|) in the worst case",
    setup=make_sparse_relation,
    requires=relations_module,
)
def composition(relation: Any) -> Any:
    """Compose a relation with itself."""
    return relation.compose(relation)


@benchmark(
    group=GROUP_RELATIONS,
    sizes=[100, 500, 1_000],
    complexity="O(n squared)",
    setup=make_sparse_relation,
    requires=relations_module,
    note="the matrix view, which composition and closure are defined through",
)
def relation_matrix(relation: Any) -> Any:
    """Build the adjacency matrix of a relation."""
    return relation.matrix()


# ---------------------------------------------------------------------------
# Equivalences and partitions
# ---------------------------------------------------------------------------


@benchmark(
    group=GROUP_EQUIVALENCE,
    sizes=[1_000, 10_000, 100_000],
    complexity="O(n) with a hash map",
    requires=equivalence_module,
)
def equivalence_from_kernel(size: int) -> Any:
    """Build an equivalence from a function whose equal values define it."""
    return equivalence_module.EquivalenceRelation.from_kernel(
        range(size), key=lambda value: value % 97
    )


@benchmark(
    group=GROUP_EQUIVALENCE,
    sizes=[100, 500, 1_000],
    complexity="O(n squared) to verify the axioms",
    setup=make_equivalence_pairs,
    requires=requires_all(relations_module, equivalence_module),
    note="construction from pairs verifies that the relation is an equivalence",
)
def equivalence_from_pairs(relation: Any) -> Any:
    """Build an equivalence from an explicit pair set."""
    return equivalence_module.EquivalenceRelation(
        domain=relation.domain, pairs=relation.pairs
    )


@benchmark(
    group=GROUP_EQUIVALENCE,
    sizes=[1_000, 10_000, 100_000],
    complexity="near O(1) amortized per operation",
    setup=make_union_find_plan,
    requires=equivalence_module,
    note=(
        "the structure Kruskal and connected components depend on, so a "
        "regression here slows two other packages"
    ),
)
def union_find_merge(payload: Tuple[Any, List[Tuple[int, int]]]) -> int:
    """Perform twice as many unions as there are members."""
    forest, plan = payload
    for left, right in plan:
        forest.union(left, right)
    return forest.count()


@benchmark(
    group=GROUP_EQUIVALENCE,
    sizes=[1_000, 10_000, 100_000],
    complexity="near O(1) amortized per query",
    setup=make_union_find,
    requires=equivalence_module,
    note="path compression is what makes the repeated find cheap",
)
def union_find_find(forest: Any) -> int:
    """Chain every member into one class and then query every root."""
    size = len(list(forest.groups()))
    for value in range(1, size):
        forest.union(value - 1, value)
    return sum(1 for value in range(size) if forest.find(value) is not None)


@benchmark(
    group=GROUP_EQUIVALENCE,
    sizes=[1_000, 10_000, 100_000],
    complexity="O(n)",
    requires=equivalence_module,
)
def partition_blocks(size: int) -> Any:
    """Build a partition and read its blocks."""
    relation = equivalence_module.EquivalenceRelation.from_kernel(
        range(size), key=lambda value: value % 101
    )
    return relation.classes()


# ---------------------------------------------------------------------------
# Orders and lattices
# ---------------------------------------------------------------------------


@benchmark(
    group=GROUP_ORDERS,
    sizes=[30, 60, 120],
    complexity="O(n squared) comparisons to build",
    requires=orders_module,
)
def order_construction(size: int) -> Any:
    """Build the divisibility order on a range."""
    return orders_module.PartialOrder.from_relation(
        ground=set(range(1, size + 1)),
        leq=lambda x, y: y % x == 0,
    )


@benchmark(
    group=GROUP_ORDERS,
    sizes=[30, 60, 120],
    complexity="O(n cubed) to remove the transitive edges",
    setup=make_divisibility_order,
    requires=orders_module,
    note="the cover relation, which every diagram and height query needs",
)
def cover_relation(order: Any) -> Any:
    """Compute the cover relation of a partial order."""
    return order.hasse_diagram()


@benchmark(
    group=GROUP_ORDERS,
    sizes=[30, 60, 120],
    complexity="O(1) after the cover relation is cached",
    setup=make_divisibility_order,
    requires=orders_module,
    note=(
        "the second query should be far cheaper than the first, which is the "
        "cache working; if the two are equal the cache has regressed"
    ),
)
def cover_relation_cached(order: Any) -> Any:
    """Compute the cover relation twice, measuring the cached second call."""
    order.hasse_diagram()
    return order.hasse_diagram()


@benchmark(
    group=GROUP_ORDERS,
    sizes=[30, 60, 120],
    complexity="O(n) with the cover relation available",
    setup=make_divisibility_order,
    requires=orders_module,
)
def extremal_elements(order: Any) -> Tuple[List[Any], List[Any]]:
    """Find the minimal and the maximal elements."""
    return order.minimal_elements(), order.maximal_elements()


@benchmark(
    group=GROUP_ORDERS,
    sizes=[30, 60, 120],
    complexity="O(n squared) meet and join queries",
    setup=make_divisibility_order,
    requires=orders_module,
    note="in this order the meet is the divisor and the join is the multiple",
)
def lattice_operations(order: Any) -> int:
    """Compute the meet and the join of every pair of a sample."""
    members = order.elements()[:40]
    count = 0
    for left in members:
        for right in members:
            order.meet(left, right)
            order.join(left, right)
            count += 1
    return count


@benchmark(
    group=GROUP_ORDERS,
    sizes=[30, 60, 120],
    complexity="O(n cubed)",
    setup=make_divisibility_order,
    requires=orders_module,
)
def is_lattice(order: Any) -> bool:
    """Decide whether a partial order is a lattice."""
    return order.is_lattice()


@benchmark(
    group=GROUP_ORDERS,
    sizes=[4, 6, 8],
    complexity="O(n cubed) on a poset of two to the size elements",
    setup=make_subset_order,
    requires=requires_all(sets_module, orders_module),
    note="the Boolean lattice, where distributivity is exercised",
)
def boolean_lattice_distributive(order: Any) -> bool:
    """Decide whether the subset order is distributive."""
    return order.is_distributive()


@benchmark(
    group=GROUP_ORDERS,
    sizes=[20, 40, 80],
    complexity="O(n cubed) for the width",
    setup=make_divisibility_order,
    requires=orders_module,
    note="the height is the longest chain and the width the largest antichain",
)
def height_and_width(order: Any) -> Tuple[int, int]:
    """Compute the height and the width of a partial order."""
    return order.height(), order.width()


@benchmark(
    group=GROUP_ORDERS,
    sizes=[8, 10, 12],
    complexity="O(1) amortized per extension, factorially many",
    setup=make_divisibility_order,
    requires=orders_module,
    note="takes the first hundred of a factorially large enumeration",
)
def linear_extensions_prefix(order: Any) -> int:
    """Take the first hundred linear extensions."""
    taken = 0
    for _ in order.linear_extensions():
        taken += 1
        if taken == 100:
            break
    return taken


# ---------------------------------------------------------------------------
# Functions
# ---------------------------------------------------------------------------


@benchmark(
    group=GROUP_FUNCTIONS,
    sizes=[1_000, 10_000, 100_000],
    complexity="O(n) to verify totality on construction",
    requires=functions_module,
)
def function_construction(size: int) -> Any:
    """Build a function from a rule over a range."""
    return functions_module.SetFunction(
        domain=set(range(size)),
        rule=lambda value: value % 97,
    )


@benchmark(
    group=GROUP_FUNCTIONS,
    sizes=[1_000, 10_000, 100_000],
    complexity="O(n) with a hash set",
    setup=make_function,
    requires=functions_module,
)
def injectivity_test(function: Any) -> bool:
    """Test whether a function is injective."""
    return function.is_injective()


@benchmark(
    group=GROUP_FUNCTIONS,
    sizes=[1_000, 10_000, 100_000],
    complexity="O(n)",
    setup=make_function,
    requires=functions_module,
)
def image_computation(function: Any) -> List[Any]:
    """Compute the image of a function."""
    return function.image()


@benchmark(
    group=GROUP_FUNCTIONS,
    sizes=[1_000, 10_000, 100_000],
    complexity="O(n)",
    setup=make_function,
    requires=functions_module,
)
def fiber_computation(function: Any) -> List[Any]:
    """Compute one fiber of a function."""
    return function.fiber(0)


@benchmark(
    group=GROUP_FUNCTIONS,
    sizes=[1_000, 10_000, 100_000],
    complexity="O(n)",
    setup=make_function,
    requires=functions_module,
)
def function_composition(function: Any) -> Any:
    """Compose a function with a second one defined on its image."""
    second = functions_module.SetFunction(
        domain=set(function.image()),
        rule=lambda value: value * 2,
    )
    return function.compose(second)


# ---------------------------------------------------------------------------
# Notes on reading these results
# ---------------------------------------------------------------------------
#
# The comparisons worth looking at, rather than the absolute numbers:
#
#   union_integers against union_builtin. The difference is the cost of the
#   library's guarantees: normalization on construction, immutability, and
#   deterministic ordering. It should be a modest constant factor. If it
#   grows with the size, something has become asymptotically worse.
#
#   union_integers against union_bit_sets on a dense universe. The bit set
#   should win by a large factor, which is what makes the advice in the
#   reference worth giving.
#
#   union_integers against union_strings. A large gap means the hashing or
#   the ordering of string members has become expensive, which would affect
#   every structure built over non integer members.
#
#   is_symmetric_sparse against is_transitive_sparse. The reference states
#   that the first is linear in the pair count and the second is the pair
#   count times the ground set. The growth ratios should show that.
#
#   is_transitive_sparse against is_transitive_worst_case. The second cannot
#   stop early, so it is the number the reference should quote.
#
#   cover_relation against cover_relation_cached. The second call should be
#   nearly free. If the two are equal, the cache has regressed and every
#   diagram and height query became cubic again.
#
#   power_set_full against power_set_prefix. The first grows as two to the
#   size and the second should be flat, because taking ten subsets of a
#   space with a million or a quadrillion members is the same work. A
#   power_set_prefix that grows with the size means the enumeration
#   materializes before it yields.
