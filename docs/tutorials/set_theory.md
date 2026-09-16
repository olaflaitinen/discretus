# Set theory

This tutorial develops the set theory package in the order the subject is
usually taught: sets and their algebra, then relations and their properties,
then equivalences and partitions, then orders and lattices, and finally
functions. Each section states the mathematics and then computes with it.

It assumes the [getting started](getting_started.md) tutorial, or at least
its conventions: values do not mutate, output order is deterministic,
exponential enumerations are lazy, and conversions between representations
are named calls.

## Sets

A set is an unordered collection of distinct members. Two sets are equal
when they have the same members, which means a set is determined entirely by
its membership and nothing else.

```python
from discretus.sets import FiniteSet

a = FiniteSet({1, 2, 3})
b = FiniteSet([3, 2, 1, 1, 2])
print(a == b)
print(a)
```

The two are equal, because order and repetition in the construction do not
survive into the set. The printed form is sorted, which is a display choice
rather than a property of the set.

Membership, size, and the inclusion relations are the basic vocabulary.

```python
print(2 in a, 7 in a)
print(len(a), a.cardinality())
print(a.is_subset(FiniteSet({1, 2, 3, 4})))
print(a.is_proper_subset(FiniteSet({1, 2, 3})))
print(a.is_disjoint(FiniteSet({7, 8})))
```

Note the difference between the third and fourth lines. Every set is a
subset of itself and no set is a proper subset of itself, and that
distinction matters constantly in order theory later on.

The empty set is a set like any other, and it is a subset of everything.

```python
empty = FiniteSet()
print(len(empty), empty.is_subset(a), a.is_subset(empty))
```

The library treats the empty case as ordinary rather than exceptional, which
is a theme worth watching for: the empty sum is zero, the empty product is
one, the empty relation is vacuously transitive, and the power set of the
empty set has exactly one member.

## The set algebra

The four fundamental operations are defined by

$$A \cup B = \{ x : x \in A \lor x \in B \}, \qquad
A \cap B = \{ x : x \in A \land x \in B \},$$

$$A \setminus B = \{ x : x \in A \land x \notin B \}, \qquad
A \triangle B = (A \setminus B) \cup (B \setminus A).$$

```python
from discretus.sets.operations import difference, intersection, symmetric_difference, union

a, b = FiniteSet({1, 2, 3}), FiniteSet({2, 3, 4})
print(union(a, b))
print(intersection(a, b))
print(difference(a, b))
print(symmetric_difference(a, b))
```

The operations take any number of arguments where that makes sense, which is
more convenient than folding by hand and is also exactly how the
associativity of the operation appears in the interface.

```python
c = FiniteSet({3, 4, 5})
print(union(a, b, c) == union(union(a, b), c))
print(intersection(a, b, c))
```

Complementation needs a universe, because the complement of a set is only
meaningful relative to one. The library requires it rather than assuming
one, which is the explicitness convention again.

```python
from discretus.sets.operations import complement

universe = FiniteSet(range(6))
print(complement(a, universe))
```

Now the laws. The distributive laws hold in both directions and the De
Morgan laws connect complementation with the two binary operations:

$$A \cap (B \cup C) = (A \cap B) \cup (A \cap C), \qquad
\overline{A \cup B} = \overline{A} \cap \overline{B}.$$

```python
print(intersection(a, union(b, c)) == union(intersection(a, b), intersection(a, c)))
print(union(a, intersection(b, c)) == intersection(union(a, b), union(a, c)))
print(
    complement(union(a, b), universe)
    == intersection(complement(a, universe), complement(b, universe))
)
```

Three lines, three theorems, confirmed on one example. The library's test
suite does the same thing on randomized inputs with Hypothesis, which is the
difference between an example and a property.

## Power sets and products

The power set of a set is the set of all its subsets, and its size is
$|\mathcal{P}(A)| = 2^{|A|}$. The Cartesian product has size
$|A \times B| = |A|\,|B|$.

```python
from discretus.sets.operations import cartesian_product, power_set

print(2 ** len(a))
print(sorted(power_set(a), key=len))
print(len(a) * len(b))
print(list(cartesian_product(a, b))[:4])
```

Both are lazy, and here is why that matters:

```python
big = FiniteSet(range(40))
print(2 ** len(big))

for subset in power_set(big):
    if len(subset) == 3 and sum(subset) == 100:
        print("found", subset)
        break
```

The power set of a forty member set has over a trillion members. The search
above finds what it needs in a fraction of a second, because the generator
produced only the subsets it was asked for. Materializing it would be
impossible, and the configured enumeration limit exists to catch an
accidental attempt.

## Relations

A binary relation on a ground set $A$ is a subset of $A \times A$, that is a
set of ordered pairs. The library requires the ground set as well as the
pairs, because the ground set changes what the properties mean.

```python
from discretus.sets.relations import Relation

r = Relation(domain={1, 2, 3}, pairs={(1, 2), (2, 3)})
print(r.domain)
print(sorted(r.pairs))
print(r.holds(1, 2), r.holds(2, 1))
```

The four properties that matter are defined by

$$\text{reflexive: } \forall a\,(a\,R\,a), \qquad
\text{symmetric: } \forall a,b\,(a\,R\,b \Rightarrow b\,R\,a),$$

$$\text{antisymmetric: } \forall a,b\,(a\,R\,b \land b\,R\,a \Rightarrow a=b),
\qquad
\text{transitive: } \forall a,b,c\,(a\,R\,b \land b\,R\,c \Rightarrow a\,R\,c).$$

```python
print(r.properties())
```

The relation above is antisymmetric and nothing else, which the dictionary
shows at a glance. Let us see why it is not transitive and fix it.

```python
print(r.holds(1, 2), r.holds(2, 3), r.holds(1, 3))
closed = r.transitive_closure()
print(sorted(closed.pairs))
print(closed.is_transitive())
```

The transitive closure is the least transitive relation containing the
original. The library computes it by Warshall's algorithm, which runs in
$O(n^3)$ boolean operations, and the reference states that.

The other two closures work the same way, and the equivalence closure is the
composition of all three.

```python
print(sorted(r.reflexive_closure().pairs))
print(sorted(r.symmetric_closure().pairs))
print(r.equivalence_closure().is_equivalence())
```

Relations compose, and composition is where the matrix view earns its place.

```python
first = Relation(domain={1, 2, 3}, pairs={(1, 2)})
second = Relation(domain={1, 2, 3}, pairs={(2, 3)})
print(sorted(first.compose(second).pairs))
print(first.matrix())
```

Composition of relations is boolean matrix multiplication, and the
transitive closure is the reflexive transitive closure of the matrix. Seeing
both representations makes the algorithm obvious rather than magical.

Two relations are worth constructing as exercises in the definitions.

```python
divisibility = Relation(
    domain=set(range(1, 13)),
    pairs={(x, y) for x in range(1, 13) for y in range(1, 13) if y % x == 0},
)
print(divisibility.properties())

strictly_less = Relation(
    domain=set(range(5)),
    pairs={(x, y) for x in range(5) for y in range(5) if x < y},
)
print(strictly_less.properties())
```

Divisibility is reflexive, antisymmetric, and transitive, so it is a partial
order. Strict inequality is irreflexive, asymmetric, and transitive, so it
is a strict order. The property dictionaries say exactly that, and the next
two sections build on both.

## Equivalence relations and partitions

A relation that is reflexive, symmetric, and transitive is an equivalence,
and it partitions its ground set into classes. That correspondence is a
bijection: every equivalence gives a partition and every partition gives an
equivalence.

```python
from discretus.sets.equivalence import EquivalenceRelation

mod3 = EquivalenceRelation.from_kernel(range(10), key=lambda n: n % 3)
print(mod3.classes())
print(mod3.class_of(7))
print(mod3.index())
print(mod3.representatives())
```

Building it from a kernel, that is from a function whose equal values define
the classes, is usually the most convenient construction. The alternatives
are from pairs and from an explicit partition.

```python
from discretus.sets.equivalence import Partition

partition = Partition([{0, 3, 6, 9}, {1, 4, 7}, {2, 5, 8}])
print(partition.to_equivalence() == mod3)
print(mod3.to_partition() == partition)
```

The quotient set is the set of classes, and it is a set of sets, which is
where the immutability of `FiniteSet` pays off again.

```python
print(mod3.quotient_set())
```

Partitions form a lattice under refinement, and the library computes the
refinement order.

```python
finer = Partition([{0, 3}, {6, 9}, {1, 4, 7}, {2, 5, 8}])
print(finer.is_refinement_of(partition))
print(partition.is_refinement_of(finer))
print(finer.common_refinement(partition) == finer)
```

The disjoint set forest is the efficient implementation of the same idea,
and it is what makes Kruskal's algorithm and connected component computation
near linear.

```python
from discretus.sets.equivalence import UnionFind

forest = UnionFind(range(10))
for value in range(10):
    forest.union(value, value % 3)
print(forest.count())
print(sorted(map(sorted, forest.groups())))
print(forest.connected(1, 4), forest.connected(1, 2))
```

## Partial orders

A relation that is reflexive, antisymmetric, and transitive is a partial
order. The library accepts either the pairs or a comparison rule, and the
rule is usually clearer.

```python
from discretus.sets.orders import PartialOrder

divides = PartialOrder.from_relation(
    ground={1, 2, 3, 4, 6, 12},
    leq=lambda x, y: y % x == 0,
)
print(divides.leq(2, 12), divides.leq(3, 4))
print(divides.comparable(2, 3), divides.incomparable(2, 3))
```

Two and three are incomparable, which is the whole difference between a
partial order and a total one. Now the extremal elements.

```python
print(divides.minimal_elements(), divides.maximal_elements())
print(divides.least_element(), divides.greatest_element())
```

A minimal element has nothing below it; a least element is below everything.
The distinction is invisible in this order, where one is both minimal and
least, and it becomes visible as soon as the least element is removed.

```python
without_one = PartialOrder.from_relation(
    ground={2, 3, 4, 6, 12},
    leq=lambda x, y: y % x == 0,
)
print(without_one.minimal_elements())
print(without_one.least_element())
```

Two minimal elements and no least element, exactly as the definitions
predict.

Bounds and the lattice structure come next.

$$\text{a lattice: every pair has a supremum and an infimum.}$$

```python
print(divides.upper_bounds(4, 6), divides.lower_bounds(4, 6))
print(divides.supremum(4, 6), divides.infimum(4, 6))
print(divides.is_lattice())
print(divides.meet(4, 6), divides.join(4, 6))
```

In the divisibility order the meet is the greatest common divisor and the
join is the least common multiple, which is the cleanest example of an
abstract structure having a concrete meaning. Verify it against the number
theory package:

```python
from discretus.number_theory.gcd import gcd, lcm

print(divides.meet(4, 6) == gcd(4, 6))
print(divides.join(4, 6) == lcm(4, 6))
```

Two packages, one theorem, and no imports between them.

The cover relation and the Hasse diagram are how a poset is drawn and
understood.

```python
print(divides.covers(2))
print(divides.hasse_diagram().edges())
print(divides.height(), divides.width())

from discretus.viz import hasse_draw

print(hasse_draw.draw(divides, backend="ascii"))
```

The height is the longest chain and the width is the largest antichain.
Dilworth's theorem relates the width to a chain decomposition: the least
number of chains covering the poset equals the width.

```python
from discretus.sets.orders import dilworth

chains = dilworth.chain_cover(divides)
print(len(chains), divides.width())
print(chains)
```

The two numbers agree, which is the theorem, and the library computes both
sides independently so that the agreement is evidence rather than a
tautology.

Finally, a linear extension is a total order compatible with the partial
one, which is topological sorting seen from the order side.

```python
extensions = list(divides.linear_extensions())
print(len(extensions))
print(extensions[0])
print(divides.topological_extension())
```

Every extension respects divisibility, so one always precedes two, and two
always precedes four. The enumeration is lazy because the number of
extensions grows factorially.

## Functions

A function assigns exactly one value to each member of its domain. The
library verifies that on construction, which means a `SetFunction` instance
is a genuine function rather than a candidate.

```python
from discretus.sets.functions import SetFunction

parity = SetFunction(domain={1, 2, 3, 4}, rule=lambda n: n % 2)
print(parity(3), parity.mapping)
print(parity.image())
print(parity.properties())
```

The properties dictionary reports injectivity, surjectivity, and
bijectivity. Parity is surjective onto its image and not injective, which
the fibers show directly.

```python
print(parity.fiber(0), parity.fiber(1))
print(parity.preimage_of([1]))
```

A codomain can be given explicitly, and that changes whether the function is
surjective, which is a subtlety worth seeing.

```python
into_five = SetFunction(domain={1, 2}, codomain={0, 1, 2, 3, 4}, rule=lambda n: n % 2)
print(into_five.is_surjective())
print(SetFunction(domain={1, 2}, rule=lambda n: n % 2).is_surjective())
```

Without an explicit codomain the library uses the image, so the function is
surjective by construction. With one, surjectivity is a real question. The
mathematics is the same; the interface makes the choice explicit.

Composition and inversion behave as the definitions require, and the errors
are informative when they do not apply.

```python
double = SetFunction(domain={1, 2}, rule=lambda n: 2 * n)
successor = SetFunction(domain={2, 4}, rule=lambda n: n + 1)
print(double.compose(successor).mapping)
print(double.inverse().mapping)

from discretus import InfeasibleError

try:
    parity.inverse()
except InfeasibleError as error:
    print("no inverse:", error)
```

A function is also a relation, and both conversions exist.

```python
print(sorted(parity.pairs()))
graph_relation = Relation(domain={1, 2, 3, 4}, pairs=set(parity.pairs()), infer_domain=True)
print(graph_relation.is_function())
```

## Multisets and bit sets

Two other set types are worth meeting, because they answer questions the
plain finite set cannot.

A multiset records multiplicities. It is what counting problems need, and it
is the right structure whenever the question is how many rather than
whether.

```python
from discretus.sets import Multiset

letters = Multiset("mississippi")
print(len(letters), letters.distinct_count())
print(letters.multiplicity("s"), letters.multiplicity("z"))
print(letters.most_common(2))
print(sorted(letters.distinct()))
```

The multiset operations respect multiplicity, which is where they differ
from the set operations and where the difference matters.

```python
first = Multiset("aab")
second = Multiset("abb")
print(first.union(second))              # maximum of the multiplicities
print(first.intersection(second))       # minimum of the multiplicities
print(first.sum(second))                # sum of the multiplicities
print(first.difference(second))         # truncated at zero
```

The union takes the maximum and the sum takes the total, and conflating them
is the usual error. A multiset union of two hands of cards tells you what
you could hold; a multiset sum tells you what you do hold after combining
them.

The number of distinct arrangements of a multiset is the multinomial
coefficient, which connects this to the combinatorics package.

```python
from discretus.combinatorics.counting import multinomial

counts = [letters.multiplicity(letter) for letter in sorted(letters.distinct())]
print(counts, multinomial(counts))
```

A bit set is the other specialization. When the members are non negative
integers from a dense range, holding the set as a bit mask makes the
operations word level rather than element level.

```python
from discretus.sets import BitSet

evens = BitSet(range(0, 100, 2))
multiples_of_three = BitSet(range(0, 100, 3))
print(len(evens), 42 in evens)

sixes = evens.intersection(multiples_of_three)
print(len(sixes), sorted(sixes)[:5])
```

The interface is the same as the finite set's, so an algorithm written
against one accepts the other. The choice is a performance decision, and the
rule is simple: dense integer members favour the bit set, and anything else
favours the finite set, because a mask is as long as its largest member.

## Why the ground set matters

One design decision in this package surprises people often enough to
deserve its own section: a relation carries its ground set, and the ground
set is part of the relation's identity.

The reason is that the properties depend on it. Consider the empty relation.

```python
from discretus.sets.relations import Relation

on_nothing = Relation(domain=set(), pairs=set())
on_three = Relation(domain={1, 2, 3}, pairs=set())

print(on_nothing.is_reflexive(), on_three.is_reflexive())
print(on_nothing.is_transitive(), on_three.is_transitive())
print(on_nothing == on_three)
```

Both are transitive, vacuously, because there are no two composable pairs to
check. Only the first is reflexive, because reflexivity requires a pair for
every member and the second has three members with no pairs. They are
therefore different relations even though their pair sets are both empty,
and the library reports them as different.

The same applies to complementation, which is entirely a function of the
ground set.

```python
small = Relation(domain={1, 2}, pairs={(1, 2)})
large = Relation(domain={1, 2, 3}, pairs={(1, 2)})
print(len(small.complement().pairs), len(large.complement().pairs))
```

Three pairs against eight, from the same single pair, because the ground set
square has four cells in one case and nine in the other.

When the pairs already mention every member you care about, the
`infer_domain` flag saves writing the ground set twice, and it is the right
choice for the common case.

```python
inferred = Relation(pairs={(1, 2), (2, 3)}, infer_domain=True)
print(inferred.domain)
```

## Putting it together

The following program uses every section above. It takes a set of integers,
builds the divisibility order on it, extracts the equivalence induced by
having the same number of divisors, and reports both structures.

```python
from discretus.number_theory.functions import divisor_count
from discretus.sets import FiniteSet
from discretus.sets.equivalence import EquivalenceRelation
from discretus.sets.orders import PartialOrder

ground = FiniteSet(range(1, 25))

order = PartialOrder.from_relation(
    ground=set(ground.members()),
    leq=lambda x, y: y % x == 0,
)
same_divisor_count = EquivalenceRelation.from_kernel(
    ground.members(), key=divisor_count
)

print("order:")
print("  minimal", order.minimal_elements())
print("  maximal", order.maximal_elements())
print("  height", order.height(), "width", order.width())
print("  lattice", order.is_lattice())

print("equivalence:")
for cls in same_divisor_count.classes():
    print(" ", divisor_count(min(cls)), sorted(cls))
```

The order is not a lattice on this ground set, because two elements can lack
a common multiple inside the range, and the report says so. The equivalence
groups the numbers by their divisor count, and the class with exactly two
divisors is the set of primes below twenty five, which is a nice check
against `primes_up_to`.

## Performance in this package

The set operations are cheap and two computations in this tutorial are not,
so it is worth knowing which is which before running any of it on a larger
input.

Membership, insertion, and the four binary operations are linear in the
total size of their arguments, and membership is constant on average. Those
never need thinking about.

The cover relation of a poset is cubic in the size of the ground set,
because computing it means removing every edge that transitivity implies.
Everything that needs the cover relation shares that cost, namely
`covers`, `hasse_diagram`, `height`, and `width`, and the result is cached
after the first call, so asking for all four costs one computation rather
than four.

```python
from discretus.sets.orders import PartialOrder
from discretus.utils.timing import Timer

order = PartialOrder.from_relation(
    ground=set(range(1, 61)),
    leq=lambda x, y: y % x == 0,
)

with Timer() as first:
    order.covers(1)
with Timer() as second:
    order.height()

print(first.human, second.human)
```

The second call is much faster than the first, which is the cache working.

Linear extensions are the expensive enumeration. Their number grows
factorially, so counting them all on a poset of thirty incomparable elements
is not possible in any amount of time. The enumeration is lazy, so taking
the first few is instant.

```python
from discretus.core.iterators import take

print(len(take(order.linear_extensions(), 3)))
```

The transitive closure is cubic, which is Warshall's algorithm, and the
transitivity test is cheaper because it stops at the first violation. If all
you need to know is whether a relation is transitive, do not compute the
closure and compare.

```python
from discretus.sets.relations import Relation

relation = Relation(
    domain=set(range(1, 61)),
    pairs={(x, y) for x in range(1, 61) for y in range(1, 61) if y % x == 0},
)

with Timer() as test:
    transitive = relation.is_transitive()
with Timer() as closure:
    relation.transitive_closure()

print(transitive, test.human, closure.human)
```

Finally, the enumeration limit. It applies when a lazy generator is
materialized, not when it is iterated, and the difference is the whole
reason the limit is usable.

```python
from discretus.config import config_scope
from discretus.sets import FiniteSet
from discretus.sets.operations import power_set

with config_scope(max_enumeration=1000):
    # Iterating is fine, however large the space.
    count = 0
    for subset in power_set(FiniteSet(range(30))):
        count += 1
        if count == 5:
            break
    print("iterated", count, "subsets of a space with", 2 ** 30)

    # Materializing is refused.
    try:
        list(power_set(FiniteSet(range(30))))
    except Exception as error:
        print(type(error).__name__)
```

## Exercises

1. Verify the inclusion and exclusion formula for three sets on random
   inputs, and then for four.
2. Show computationally that the subset relation on the power set of a three
   member set is a lattice, and identify its meet and join.
3. Build the equivalence induced by congruence modulo seven on the integers
   below fifty, and check that the classes all have the same size except
   possibly one.
4. Compute the transitive closure of a random relation twice, once with
   `transitive_closure` and once by repeatedly composing the relation with
   itself until it stops changing, and check that the results agree.
5. Find a poset on five elements whose height and width are both three, and
   draw its Hasse diagram.
6. Construct a function that is injective but not surjective, one that is
   surjective but not injective, and one that is both, each on a domain of
   three elements, and print their property dictionaries.

## Where to go next

- The [set theory reference](../api/sets.md) for the complete interface,
  including the bit set, multiset, and interval set types this tutorial did
  not use.
- [Graph algorithms](graph_algorithms.md), where the relations of this
  tutorial become graphs.
- [Group theory](group_theory.md), where the lattices of this tutorial
  reappear as subgroup lattices.
