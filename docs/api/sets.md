# `discretus.sets`

The set theory package provides the set types, the set algebra, binary and
n-ary relations, equivalence relations with their quotients, order theory,
and functions between finite sets.

It is the package most worth reading first, because a relation is the common
ancestor of an order, an equivalence, and a directed graph, and because the
conventions established here hold everywhere else in the library.

## Mathematical basis

A set is an unordered collection of distinct members. The fundamental
operations are defined by

$$A \cup B = \{ x : x \in A \lor x \in B \}, \qquad
A \cap B = \{ x : x \in A \land x \in B \},$$

$$A \setminus B = \{ x : x \in A \land x \notin B \}, \qquad
A \triangle B = (A \setminus B) \cup (B \setminus A),$$

and they satisfy the distributive laws in both directions together with the
De Morgan laws,

$$A \cap (B \cup C) = (A \cap B) \cup (A \cap C), \qquad
\overline{A \cup B} = \overline{A} \cap \overline{B}.$$

The library asserts these as property based tests rather than only claiming
them. The cardinality of a power set is $|\mathcal{P}(A)| = 2^{|A|}$ and of
a Cartesian product is $|A \times B| = |A|\,|B|$, and both are computed
exactly while the members can be enumerated lazily.

A binary relation $R \subseteq A \times A$ is reflexive when
$\forall a\,(a\,R\,a)$, symmetric when
$\forall a,b\,(a\,R\,b \Rightarrow b\,R\,a)$, antisymmetric when
$\forall a,b\,(a\,R\,b \land b\,R\,a \Rightarrow a = b)$, and transitive
when $\forall a,b,c\,(a\,R\,b \land b\,R\,c \Rightarrow a\,R\,c)$. A
relation that is reflexive, symmetric, and transitive is an equivalence and
partitions its ground set. One that is reflexive, antisymmetric, and
transitive is a partial order.

## Module map

| Subpackage or module | Responsibility |
| --- | --- |
| `finite_set` | The default immutable set type |
| `bit_set` | Compact representation for a dense integer universe |
| `multiset` | Counting semantics, members with multiplicity |
| `ordered_set` | Insertion ordered set |
| `interval_set` | Union of integer intervals |
| `sparse_set` | Sparse membership over a large universe |
| `lazy_set` | A set described by a predicate and a universe |
| `universal_set` | The complement aware universe |
| `frozen_set_ext` | Adapter that gives a built-in frozen set the interface |
| `operations` | The set algebra |
| `relations` | Binary and n-ary relations, properties, closures |
| `equivalence` | Equivalence relations, partitions, quotients, union find |
| `orders` | Preorders, partial and total orders, lattices, Hasse diagrams |
| `functions` | Functions between finite sets |

## Set types

### `FiniteSet(members=())`

The default set type: immutable, hashable, and therefore able to be a member
of another set, which is what makes a power set expressible directly.
Members may be any hashable value and are normalized on construction, so a
list becomes a tuple and a set becomes a frozen set.

| Method | Meaning |
| --- | --- |
| `members()` | Members in deterministic display order |
| `cardinality()`, `__len__` | Number of members |
| `contains(value)`, `__contains__` | Membership, O(1) average |
| `is_subset(other)`, `is_superset(other)` | Inclusion |
| `is_proper_subset(other)` | Strict inclusion |
| `is_disjoint(other)` | Empty intersection |
| `with_member(value)`, `without(value)` | Modified copies |
| `to_frozenset()`, `to_dict()`, `to_latex()` | Conversions |

```python
>>> from discretus.sets import FiniteSet
>>> a = FiniteSet({3, 1, 2, 1})
>>> a
{1, 2, 3}
>>> len(a), 2 in a, a.is_subset(FiniteSet(range(5)))
(3, True, True)
```

Set operators are available as well as named functions, and the named
functions are the documented interface because they read like the
mathematics.

### `BitSet(members=(), universe=None)`

A set of non negative integers held as a bit mask, which makes membership,
union, intersection, and difference single machine operations on each word.
Use it when the universe is dense and integer valued; use `FiniteSet` for
anything else. The interface is the same, so an algorithm written against
the abstract interface accepts either.

### `Multiset(members=())`

A set with multiplicities, which is what counting problems need. Adds
`multiplicity`, `distinct_count`, `most_common`, `total`, and the multiset
sum, difference, and intersection that respect multiplicity. Iteration
yields each member once per occurrence and `distinct()` yields it once.

```python
>>> from discretus.sets import Multiset
>>> bag = Multiset("mississippi")
>>> bag.multiplicity("s"), bag.distinct_count(), len(bag)
(4, 4, 11)
>>> bag.most_common(2)
[('i', 4), ('s', 4)]
```

### `OrderedSet`, `IntervalSet`, `SparseSet`, `LazySet`, `UniversalSet`

`OrderedSet` preserves insertion order, which matters when a set describes a
sequence of choices. `IntervalSet` holds a union of integer intervals in
their endpoints, so a set of a billion consecutive integers costs two
integers. `SparseSet` is the complement case, a few members in a huge
universe. `LazySet` is described by a predicate over a universe and
materializes on demand. `UniversalSet` represents the universe itself and
makes complementation total, so that the complement of a finite set is a
well defined cofinite set rather than an error.

## The set algebra

Every routine in `discretus.sets.operations` returns a new object and
mutates nothing.

| Routine | Result | Complexity |
| --- | --- | --- |
| `union(*sets)` | Members of any argument | O(total size) |
| `intersection(*sets)` | Members of every argument | O(smallest size) |
| `difference(a, b)` | Members of `a` not in `b` | O(size of `a`) |
| `symmetric_difference(a, b)` | Members of exactly one | O(total size) |
| `complement(a, universe)` | Members of the universe not in `a` | O(universe) |
| `cartesian_product(*sets)` | Tuples, lazily | O(1) per tuple |
| `power_set(a)` | Subsets, lazily | O(1) per subset |
| `disjoint_union(*sets)` | Tagged union | O(total size) |
| `partition_ops` | Refinement, coarsening, products of partitions | Varies |
| `cover(family, target)` | Whether a family covers a set | O(total size) |
| `closure(seed, operation)` | Least closed superset | O(result size) |

The lazy routines are the ones whose output is exponential or quadratic in
the input. They return generators, so a search that stops early costs only
what it consumed, and the configured enumeration limit applies to the
materializing helpers rather than to the generators.

```python
>>> from discretus.sets import FiniteSet
>>> from discretus.sets.operations import power_set, union
>>> union(FiniteSet({1, 2}), FiniteSet({2, 3}))
{1, 2, 3}
>>> sum(1 for _ in power_set(FiniteSet(range(10))))
1024
```

## Relations

### `Relation(domain, pairs=(), infer_domain=False)`

A binary relation over a finite ground set, built on
`discretus.core.relation_base.RelationBase` and therefore sharing its
property tests and closures with the order and equivalence types.

| Group | Members |
| --- | --- |
| Access | `domain`, `pairs`, `holds`, `image_of`, `preimage_of`, `adjacency` |
| Properties | `is_reflexive`, `is_irreflexive`, `is_symmetric`, `is_antisymmetric`, `is_asymmetric`, `is_transitive`, `is_total`, `is_equivalence`, `is_partial_order`, `is_preorder`, `is_function`, `properties` |
| Algebra | `converse`, `complement`, `union`, `intersection`, `difference`, `compose` |
| Closures | `reflexive_closure`, `symmetric_closure`, `transitive_closure`, `equivalence_closure` |
| Views | `matrix`, `to_digraph`, `to_relation_matrix` |

```python
>>> from discretus.sets.relations import Relation
>>> r = Relation(domain={1, 2, 3}, pairs={(1, 2), (2, 3)})
>>> r.is_transitive()
False
>>> sorted(r.transitive_closure().pairs)
[(1, 2), (1, 3), (2, 3)]
```

The transitive closure is Warshall's algorithm, which runs in $O(n^3)$
boolean operations for a ground set of size $n$. The dedicated modules
`closure_reflexive`, `closure_symmetric`, `closure_transitive`, and
`warshall` expose the algorithms as free functions for readers who want the
algorithm without the object.

### `RelationMatrix` and `relation_graph`

`RelationMatrix` is the boolean matrix view, where composition is boolean
matrix multiplication and the transitive closure is the transitive closure
of the matrix. `relation_graph` produces the directed graph view, which is
the bridge to the graph package: the strongly connected components of that
graph are exactly the equivalence classes of the relation's mutual
reachability.

### `NaryRelation(arity, tuples=())`

A relation of arbitrary arity, with projection, selection, and natural join,
which is the relational algebra a database student meets in the same course.

### Property modules

`reflexive`, `irreflexive`, `symmetric`, `antisymmetric`, `asymmetric`,
`transitive`, and `properties` expose each test as a free function over a
pair set, for use without constructing a relation object.

## Equivalence relations

### `EquivalenceRelation`

Constructed from pairs, from a kernel, or from a partition, and verified to
be an equivalence on construction.

| Method | Meaning |
| --- | --- |
| `classes()` | The equivalence classes |
| `class_of(element)` | The class containing a member |
| `representatives()` | One member per class, deterministically chosen |
| `quotient_set()` | The set of classes |
| `index()` | The number of classes |
| `is_refinement_of(other)` | Whether every class refines one of `other` |
| `to_partition()` | The induced partition |

```python
>>> from discretus.sets.equivalence import EquivalenceRelation
>>> mod3 = EquivalenceRelation.from_kernel(range(7), key=lambda n: n % 3)
>>> mod3.index(), mod3.class_of(4)
(3, {1, 4})
```

### `Partition(blocks)`

A partition of a ground set, with `blocks`, `block_of`, `is_refinement_of`,
`refine`, `coarsen`, `common_refinement`, and `to_equivalence`. The
partition lattice operations are the meet and join of the equivalence
lattice, which is why they live here rather than in the order package.

### `UnionFind(elements=())`

A disjoint set forest with path compression and union by rank, which gives
the near constant amortized cost that Kruskal's algorithm and connected
component computation depend on.

| Method | Meaning | Complexity |
| --- | --- | --- |
| `find(element)` | The representative of a member | Near O(1) amortized |
| `union(left, right)` | Merge two classes, returning whether it merged | Near O(1) amortized |
| `connected(left, right)` | Whether two members share a class | Near O(1) amortized |
| `groups()` | The classes | O(n) |
| `count()` | The number of classes | O(1) |

### `kernel`, `quotient_set`, `refinement`, `equivalence_class`

The free function forms of the same operations, for readers who prefer them.

## Order theory

### `Poset(ground, leq)` and `PartialOrder`

A partially ordered set, given by its comparison rule or by its pairs, and
verified to be reflexive, antisymmetric, and transitive on construction.

| Group | Members |
| --- | --- |
| Comparison | `leq`, `less`, `comparable`, `incomparable` |
| Extremes | `minimal_elements`, `maximal_elements`, `least_element`, `greatest_element` |
| Bounds | `upper_bounds`, `lower_bounds`, `supremum`, `infimum` |
| Lattice | `is_lattice`, `meet`, `join`, `is_distributive`, `is_modular` |
| Structure | `covers`, `hasse_diagram`, `height`, `width`, `chains`, `antichains` |
| Extensions | `linear_extensions`, `topological_extension` |
| Duality | `dual` |

```python
>>> from discretus.sets.orders import PartialOrder
>>> divides = PartialOrder.from_relation(
...     ground={1, 2, 3, 4, 6, 12},
...     leq=lambda x, y: y % x == 0,
... )
>>> divides.minimal_elements(), divides.maximal_elements()
([1], [12])
>>> divides.is_lattice(), divides.meet(4, 6), divides.join(4, 6)
(True, 2, 12)
```

The cover relation is the order with reflexivity and transitivity removed,
and the Hasse diagram is its graph. Drawing it is a visualization concern
and is handled by `discretus.viz.hasse_draw`, while the layout, meaning the
assignment of a rank to each member, is computed here in `hasse_layout`
because it is order theory rather than rendering.

### `TotalOrder`, `StrictOrder`, `Preorder`

The neighbouring structures. `TotalOrder` adds comparability of every pair
and therefore sorting. `StrictOrder` is the irreflexive form. `Preorder`
drops antisymmetry, and its quotient by mutual comparability is a partial
order, which the package computes.

### `Chain`, `Antichain`, `dilworth`

A chain is a totally ordered subset and an antichain is a pairwise
incomparable one. Dilworth's theorem states that the least number of chains
that cover a finite poset equals the size of its largest antichain, and the
module computes both sides, which makes the theorem checkable rather than
only quotable.

### `Lattice`, `BoundedLattice`, `DistributiveLattice`

The lattice hierarchy, each verifying the laws it adds. A lattice provides
meet and join for every pair; a bounded lattice adds a least and a greatest
element; a distributive lattice satisfies the distributive laws, which the
type checks on construction.

### `galois_connection`, `supremum_infimum`, `maximal_minimal`, `topological_extension`

Supporting modules: a Galois connection between two posets with its adjoint
pair, bounds computation as free functions, extreme element computation as
free functions, and the extension of a partial order to a total one, which
is topological sorting seen from the order side.

## Functions between sets

### `SetFunction(domain, codomain=None, mapping=None, rule=None)`

Built on `discretus.core.function_base.FunctionBase`. Totality is verified
on construction, so an instance is a genuine function.

| Group | Members |
| --- | --- |
| Access | `domain`, `codomain`, `mapping`, `apply`, call syntax, `pairs` |
| Images | `image`, `image_of`, `preimage_of`, `fiber` |
| Properties | `is_injective`, `is_surjective`, `is_bijective`, `is_identity`, `is_constant`, `fixed_points` |
| Derived | `compose`, `inverse`, `restricted_to`, `extended_by` |

```python
>>> from discretus.sets.functions import SetFunction
>>> f = SetFunction(domain={1, 2, 3}, rule=lambda n: n % 2)
>>> f.image(), f.is_injective(), f.is_surjective()
([0, 1], False, True)
```

The predicate modules `injective`, `surjective`, and `bijective` expose the
tests as free functions, `image_preimage` exposes the image and preimage
computations, `inverse` constructs the inverse and raises `InfeasibleError`
with the reason when the function is not bijective, and `restriction`
restricts a function to a subset of its domain.

A function is also a relation, and the conversion is explicit in both
directions: a relation that passes `is_function` converts to a
`SetFunction`, and a `SetFunction` converts to its graph as a `Relation`.

## Interoperability

The set package is the hub of the library, and these conversions are the
documented bridges out of it.

| From | To | Call |
| --- | --- | --- |
| `Relation` | Directed graph | `relation.to_digraph()` |
| `Relation` | Boolean matrix | `relation.matrix()` |
| `PartialOrder` | Hasse diagram graph | `order.hasse_diagram()` |
| `PartialOrder` | Topological order | `order.topological_extension()` |
| `EquivalenceRelation` | Partition | `relation.to_partition()` |
| `Partition` | Equivalence relation | `partition.to_equivalence()` |
| `FiniteSet` | Built-in frozen set | `set.to_frozenset()` |
| `Poset` | Lattice, when it is one | `Lattice.from_poset(order)` |

Each is a named operation rather than an implicit coercion, which is the
explicitness principle the library applies throughout: a conversion that
changes how an object is interpreted should be visible in the source.

## Choosing a set type

Six set types are a lot to choose between, so the decision is worth stating
plainly. The interface is shared, so a wrong first choice costs a one line
change rather than a rewrite.

Use `FiniteSet` unless you have a reason not to. It accepts any hashable
member, it is immutable and therefore usable as a member of another set, and
its operations are the ones every other type is measured against.

Use `BitSet` when the members are non negative integers drawn from a dense
range and the sets are large. Union, intersection, and difference become
word level operations, which is a difference of an order of magnitude on a
universe of a few thousand. The saving disappears if the universe is sparse,
because the mask is as long as the largest member.

Use `Multiset` when a member can occur more than once and the count matters.
The temptation is to reach for a list instead, but a list gives up
membership testing in constant time and gives up the set operations
entirely.

Use `IntervalSet` when the members are consecutive runs of integers. A set
of a billion consecutive integers costs two integers rather than a billion,
and the operations work on the endpoints.

Use `OrderedSet` when the order of insertion is part of the meaning, for
instance a sequence of distinct choices or a deterministic worklist.

Use `LazySet` when the membership rule is cheap and the universe is large
enough that enumerating it would be wasteful, for instance the squares below
a bound.

## Worked example: checking the laws

The claim that the library asserts its algebraic laws rather than only
documenting them is easy to verify. The following is close to what the
property based suite does, with a fixed seed rather than a generator.

```python
from itertools import combinations

from discretus.core.random_base import SeededRandom
from discretus.sets import FiniteSet
from discretus.sets.operations import (
    complement,
    difference,
    intersection,
    symmetric_difference,
    union,
)

source = SeededRandom(2026)
universe = FiniteSet(range(12))


def sample_set() -> FiniteSet:
    size = source.integer(0, 12)
    return FiniteSet(source.sample(range(12), size))


for _ in range(200):
    a, b, c = sample_set(), sample_set(), sample_set()

    # Distributivity, in both directions.
    assert intersection(a, union(b, c)) == union(intersection(a, b), intersection(a, c))
    assert union(a, intersection(b, c)) == intersection(union(a, b), union(a, c))

    # De Morgan, relative to an explicit universe.
    assert complement(union(a, b), universe) == intersection(
        complement(a, universe), complement(b, universe)
    )
    assert complement(intersection(a, b), universe) == union(
        complement(a, universe), complement(b, universe)
    )

    # The symmetric difference is the union of the two differences.
    assert symmetric_difference(a, b) == union(difference(a, b), difference(b, a))

    # Inclusion and exclusion for two and three sets.
    assert len(union(a, b)) == len(a) + len(b) - len(intersection(a, b))
    triple = [a, b, c]
    inclusive = sum(len(s) for s in triple)
    inclusive -= sum(len(intersection(x, y)) for x, y in combinations(triple, 2))
    inclusive += len(intersection(a, b, c))
    assert len(union(a, b, c)) == inclusive

print("the laws hold on 200 randomized triples")
```

Two things about this example generalize. The seed makes the run
reproducible, so a failure can be investigated rather than merely observed.
And the assertions are the mathematics transcribed, which is the form a
property based test should take: if the transcription is wrong the test is
wrong, and that is easier to review than an implementation.

## Performance notes

Membership, insertion, and removal on `FiniteSet` inherit the constant
average cost of the underlying hash set. The set operations are linear in
the total size of their arguments, and `intersection` is linear in the
smallest argument because it iterates that one.

Two costs are worth anticipating because they surprise people. The first is
the cover relation of a poset, which is cubic in the size of the ground set,
because it removes the transitive edges; it is cached after the first
computation, so `covers`, `hasse_diagram`, `height`, and `width` share the
work. The second is the linear extension count, which is the number of
topological orders and grows factorially; the enumeration is lazy, so
counting the first few is cheap and counting all of them for a large poset
is not.

The property tests differ in cost and it is worth knowing which. Reflexivity
and irreflexivity are linear in the ground set. Symmetry, antisymmetry, and
asymmetry are linear in the number of pairs. Transitivity is the number of
pairs times the ground set in the worst case, because it has to look at the
successors of each successor. Totality is quadratic in the ground set, since
it inspects every unordered pair.

## Design notes

Three decisions in this package are worth explaining, because each one could
have gone the other way and the reasons apply elsewhere in the library.

**Sets are immutable.** A mutable set cannot be a member of another set,
because its hash would change under mutation and corrupt whatever container
held it. Since a power set is a set of sets, and a partition is a set of
blocks, immutability is not a stylistic preference here but a requirement of
the mathematics the package models. The cost is that a modification returns
a copy, which the `with_member` and `without` names make visible.

**Order is imposed rather than inherited.** A set has no order, so the
library has to choose one for display and for the pairs it returns, and it
chooses a total order defined on the members rather than the iteration order
of the underlying container. That is what makes output identical between
processes despite hash randomization, and it is why members of mixed types
can be printed at all.

**A relation carries its ground set.** A relation is not merely a set of
pairs: the empty relation on a three member set is reflexive on no member
and is a different object from the empty relation on an empty set, and the
complement of a relation depends on the ground set entirely. Requiring the
ground set at construction makes those distinctions explicit, and
`infer_domain` exists for the common case where the pairs already mention
every member.

## Complexity summary

| Operation | Complexity |
| --- | --- |
| Membership in a hashed set | O(1) average |
| Membership in a bit set | O(1) |
| Union, intersection, difference | O(total size) |
| Power set enumeration | O(1) per subset, $2^n$ subsets |
| Cartesian product enumeration | O(1) per tuple |
| Relation property test | O(n) to O(n squared), by property |
| Transitive closure by Warshall | O(n cubed) |
| Union find operation | Near O(1) amortized |
| Cover relation of a poset | O(n cubed) |
| Linear extension enumeration | O(1) per extension |
| Lattice meet or join | O(n) with the cover relation cached |

## Errors

| Exception | Raised when |
| --- | --- |
| `ValidationError` | A member is unhashable, or a pair is not a pair |
| `DomainError` | A pair mentions a value outside the ground set, or a member is outside the domain |
| `AxiomViolationError` | A candidate order or equivalence fails its axioms |
| `NotAFunctionError` | A relation used as a function is not total or not single valued |
| `InfeasibleError` | An inverse, a least element, or a meet does not exist |
| `LimitExceededError` | A power set or product was materialized beyond the configured limit |

## See also

- The [set theory tutorial](../tutorials/set_theory.md), which develops this
  material slowly with the mathematics alongside.
- [`discretus.core`](core.md), for the relation and function bases and the
  universal order.
- [`discretus.graphs`](graphs.md), which consumes the relation and Hasse
  diagram conversions.
- [`discretus.combinatorics`](combinatorics.md), for counting the objects
  this package enumerates.
- [`discretus.viz`](viz.md), for drawing Hasse diagrams, lattices, and Venn
  diagrams.
