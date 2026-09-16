# Group theory

This tutorial builds group theory from the axioms to Sylow theory, using the
library to make each abstraction concrete. Groups are the first place where
a student meets a structure defined purely by axioms, and the usual
difficulty is that the axioms feel remote from anything computable. They are
not, and this tutorial is an attempt to show that.

## The axioms

A group is a set with a binary operation that is closed and associative, has
an identity, and gives every element an inverse. The library checks all four
when a group is constructed, so an object of a group type satisfies the
axioms for its whole lifetime.

Start below the group level, to see what the axioms exclude.

```python
from discretus.core.operation import BinaryOperation

addition_mod_3 = BinaryOperation([0, 1, 2], lambda a, b: (a + b) % 3, symbol="+")
print(addition_mod_3.is_closed())
print(addition_mod_3.is_associative())
print(addition_mod_3.identity())
print(addition_mod_3.has_inverses())
print(addition_mod_3.is_group())
```

Four properties, checked independently. Now break each one in turn.

```python
subtraction = BinaryOperation([0, 1, 2], lambda a, b: (a - b) % 3, symbol="-")
print(subtraction.is_closed(), subtraction.is_associative())
print(subtraction.associativity_counterexample())

multiplication = BinaryOperation([0, 1, 2], lambda a, b: (a * b) % 3, symbol=".")
print(multiplication.identity(), multiplication.has_inverses())
print(multiplication.inverses())
```

Subtraction modulo three is closed and not associative, and the library
returns the triple that violates it rather than merely reporting a failure.
Multiplication modulo three has an identity and zero has no inverse, which
the inverse table shows. Neither is a group, and the reasons are different.

The hierarchy in the core layer names each stage.

```python
from discretus.core.algebraic_base import GroupBase, Magma, Monoid, Semigroup
from discretus import AxiomViolationError

print(Magma([0, 1, 2], lambda a, b: (a - b) % 3).satisfies_axioms())
try:
    Semigroup([0, 1, 2], lambda a, b: (a - b) % 3)
except AxiomViolationError as error:
    print("not a semigroup:", error)

print(Monoid([0, 1, 2, 3], lambda a, b: (a * b) % 4).identity())
print(GroupBase([0, 1, 2, 3], lambda a, b: (a + b) % 4).inverses())
```

A magma needs only closure, a semigroup adds associativity, a monoid adds an
identity, and a group adds inverses. Each class checks exactly what it adds.

## The families

Most groups a reader meets belong to a handful of families, and the library
constructs them directly.

```python
from discretus.algebra.groups import (
    AlternatingGroup, CyclicGroup, DihedralGroup, KleinGroup,
    QuaternionGroup, SymmetricGroup,
)

for group in (
    CyclicGroup(6), KleinGroup(), DihedralGroup(4),
    SymmetricGroup(3), AlternatingGroup(4), QuaternionGroup(),
):
    print(type(group).__name__, group.order(), group.is_abelian())
```

The cyclic group is the integers modulo $n$ under addition. The symmetric
group is all permutations of $n$ letters, and it has $n!$ elements. The
dihedral group is the symmetries of a regular polygon, with $2n$ elements,
$n$ rotations and $n$ reflections.

```python
d4 = DihedralGroup(4)
print(d4.elements())
print(d4.order())
print(d4.operate(("r", 1), ("s", 0)))
```

The Cayley table is the complete multiplication table, and for a group this
small it is the whole structure in one picture.

```python
print(CyclicGroup(4).cayley_table())
```

Reading a Cayley table teaches two things immediately. Every row and column
is a permutation of the elements, which is a necessary condition for a group
and is the Latin square property. And the table is symmetric about the
diagonal exactly when the group is abelian.

```python
print(CyclicGroup(4).operation.is_latin_square())
print(SymmetricGroup(3).is_abelian())
print(SymmetricGroup(3).operation.commutativity_counterexample())
```

The symmetric group on three letters is the smallest non abelian group, and
the counterexample is a pair of permutations that do not commute.

## Element orders

The order of an element is the least positive power that gives the identity.

```python
z12 = CyclicGroup(12)
print(z12.element_orders())
print(z12.element_order(8))
```

Every element order divides the group order, which is a corollary of
Lagrange's theorem and is the first non obvious fact in the subject.

```python
for group in (CyclicGroup(12), DihedralGroup(4), SymmetricGroup(4), QuaternionGroup()):
    order = group.order()
    orders = set(group.element_orders().values())
    print(type(group).__name__, order, sorted(orders), all(order % k == 0 for k in orders))
```

A cyclic group has an element whose order is the group order, and that is
what cyclic means.

```python
print(z12.is_cyclic(), z12.generators())
print(SymmetricGroup(3).is_cyclic())
```

The generators of the cyclic group of order twelve are exactly the residues
coprime to twelve, which is the connection to the Euler totient.

```python
from discretus.number_theory.functions import euler_totient

print(len(z12.generators()) == euler_totient(12))
```

## Subgroups and Lagrange's theorem

A subgroup is a subset that is a group under the same operation. Lagrange's
theorem says its order divides the group order, and the index counts the
cosets:

$$|H| \text{ divides } |G|, \qquad [G : H] = \frac{|G|}{|H|}.$$

```python
group = CyclicGroup(12)
subgroups = group.subgroups()
print([h.order() for h in subgroups])
print(all(group.order() % h.order() == 0 for h in subgroups))
```

The orders are exactly the divisors of twelve, which is a stronger statement
than Lagrange's theorem and is special to cyclic groups.

```python
print(sorted(h.order() for h in DihedralGroup(6).subgroups()))
```

The dihedral group of order twelve has subgroups of several orders, and not
every divisor need appear in a general group, which is where Sylow's
theorems come in below.

Cosets partition the group, which is the proof of Lagrange's theorem and is
visible directly.

```python
subgroup = group.generated_by([4])
print(subgroup.elements())
cosets = group.cosets(subgroup, side="left")
print(cosets)
print(len(cosets) * subgroup.order() == group.order())
flattened = sorted(element for coset in cosets for element in coset)
print(flattened == sorted(group.elements()))
```

Four cosets of a subgroup of order three in a group of order twelve, and
together they cover the group exactly once each. That is the whole proof.

A subgroup is normal when it is invariant under conjugation, and only then
does the set of cosets form a group.

```python
print(group.is_normal(subgroup))
print([h.order() for h in SymmetricGroup(3).normal_subgroups()])
quotient = group.quotient_group(subgroup)
print(quotient.order(), quotient.is_abelian())
```

Every subgroup of an abelian group is normal, so the cyclic example is
uninformative. The symmetric group on three letters has exactly three normal
subgroups, of orders one, three, and six, and the one of order three is the
alternating group.

## Morphisms

A homomorphism is a map that preserves the operation. The library verifies
that on construction.

```python
from discretus.algebra.groups import Homomorphism

source, target = CyclicGroup(12), CyclicGroup(4)
reduction = Homomorphism(source, target, lambda x: x % 4)
print(reduction.is_valid())
print(reduction.kernel().elements())
print(reduction.image())
```

The kernel is a normal subgroup and the image is a subgroup, and the first
isomorphism theorem says the quotient by the kernel is isomorphic to the
image. Check the orders, which is the counting half of the theorem.

```python
print(source.order() // reduction.kernel().order() == len(reduction.image()))
```

Isomorphism is the notion of two groups being the same up to renaming.

```python
from discretus.algebra.groups import DirectProduct, are_isomorphic

print(are_isomorphic(CyclicGroup(6), DirectProduct(CyclicGroup(2), CyclicGroup(3))))
print(are_isomorphic(CyclicGroup(4), KleinGroup()))
```

The first is the Chinese remainder theorem in group form: the cyclic group
of order six splits as a product because two and three are coprime. The
second is false, and the reason is instructive: both groups have order four,
and one has an element of order four while the other does not.

```python
print(sorted(CyclicGroup(4).element_orders().values()))
print(sorted(KleinGroup().element_orders().values()))
```

The multiset of element orders is an isomorphism invariant, and comparing
invariants is how a non isomorphism is usually shown.

## Group actions

A group acts on a set when each element permutes the set compatibly with the
operation. The orbit stabilizer theorem says

$$|G| = |\mathrm{Orb}(x)| \cdot |\mathrm{Stab}(x)|.$$

```python
from itertools import combinations

from discretus.algebra.groups import GroupAction, SymmetricGroup

group = SymmetricGroup(4)
points = [frozenset(c) for size in range(5) for c in combinations(range(4), size)]

action = GroupAction(
    group=group,
    points=points,
    action=lambda permutation, subset: frozenset(permutation[i] for i in subset),
)

for point in (frozenset(), frozenset({0}), frozenset({0, 1}), frozenset(range(4))):
    orbit = action.orbit(point)
    stabilizer = action.stabilizer(point)
    print(sorted(point), len(orbit), stabilizer.order(), len(orbit) * stabilizer.order())
```

Every product is twenty four, the order of the group. The orbits are the
subsets of a given size, which is the content of the action being the
natural one.

```python
print(sorted(len(orbit) for orbit in action.orbits()))
print(action.burnside_count(), len(action.orbits()))
```

Burnside's lemma counts the orbits as the average number of fixed points,

$$|X / G| = \frac{1}{|G|} \sum_{g \in G} |\mathrm{Fix}(g)|,$$

and the library computes both sides so that the identity can be checked.
This is the machinery behind counting up to symmetry, which the
combinatorics package uses.

```python
from discretus.algebra.groups import CyclicGroup
from discretus.combinatorics.polya import burnside, cycle_index

print(burnside(CyclicGroup(4), colours=2))
print(cycle_index(CyclicGroup(4), degree=4).to_text())
```

Six necklaces of four beads in two colours, up to rotation, which is a
counting answer obtained entirely from group theory.

## Conjugacy and the class equation

Conjugate elements are those related by conjugation, and the conjugacy
classes partition the group.

```python
s4 = SymmetricGroup(4)
classes = s4.conjugacy_classes()
print([len(cls) for cls in classes])
print(sum(len(cls) for cls in classes) == s4.order())
print(all(s4.order() % len(cls) == 0 for cls in classes))
```

In a symmetric group the conjugacy classes are the cycle types, which is one
of the cleanest facts in the subject, and the class sizes divide the group
order because each is an orbit of the conjugation action.

The centre is the set of elements that commute with everything, and it is a
normal subgroup.

```python
print(s4.center().elements())
print(CyclicGroup(6).center().order() == 6)
print(QuaternionGroup().center().elements())
```

A group is abelian exactly when its centre is the whole group, and the
quaternion group has a centre of order two, which is why it is non abelian
but close to it.

## Sylow theory

Sylow's theorems say which subgroup orders must occur. For a prime power
dividing the group order maximally, a subgroup of that order exists, all
such subgroups are conjugate, and their number is congruent to one modulo
the prime.

```python
group = SymmetricGroup(4)
print(group.order())

for prime in (2, 3):
    sylows = group.sylow_subgroups(prime)
    print(prime, len(sylows), [h.order() for h in sylows])
```

The order twenty four factors as eight times three, so the Sylow two
subgroups have order eight and the Sylow three subgroups have order three.
The counts satisfy the congruence, which is worth checking.

```python
for prime in (2, 3):
    count = len(group.sylow_subgroups(prime))
    print(prime, count, count % prime == 1 % prime)
```

Solvability and simplicity are the structural questions Sylow theory
supports.

```python
from discretus.algebra.groups import AlternatingGroup

for group in (CyclicGroup(6), SymmetricGroup(3), SymmetricGroup(4), AlternatingGroup(5)):
    print(type(group).__name__, group.order(), group.is_solvable(), group.is_simple())
```

The alternating group on five letters is simple and not solvable, which is
the fact behind the unsolvability of the general quintic, and it is the
smallest non abelian simple group.

## Cayley graphs

A group and a set of generators produce a graph, and every routine in the
graph package then applies.

```python
from discretus.graphs.properties import diameter
from discretus.graphs.traversal import connected_components

cayley = CyclicGroup(8).cayley_graph(generators=[1])
print(cayley.order(), cayley.size())
print(len(connected_components(cayley)), diameter(cayley))

two_generators = CyclicGroup(8).cayley_graph(generators=[1, 3])
print(two_generators.size(), diameter(two_generators))
```

The graph is connected exactly when the chosen elements generate the group,
and its diameter is the word length metric, that is the largest number of
generators needed to express an element. Adding a generator shortens it,
which is the whole idea behind expander constructions.

```python
print(CyclicGroup(8).generated_by([2]).order())
print(len(connected_components(CyclicGroup(8).cayley_graph(generators=[2]))))
```

Two does not generate the group of order eight, so that Cayley graph is
disconnected, with one component per coset of the subgroup it does generate.

For a picture, the drawing takes the graph directly.

```python
from discretus.viz import graph_draw

print(graph_draw.draw(cayley, layout="circular", backend="ascii"))
```

## Permutations in detail

Permutation groups deserve their own section, because the symmetric group is
where most of group theory is done and because the two notations for a
permutation cause most of the confusion.

The library uses one line notation over zero based positions: a permutation
is a tuple whose entry at position $i$ is the image of $i$.

```python
from discretus.algebra.groups import PermutationGroup, SymmetricGroup

s4 = SymmetricGroup(4)
print(s4.elements()[:5])
print(s4.identity())
```

Cycle notation is the other convention, and the conversion is explicit in
both directions because a silent misreading between the two produces a
plausible wrong answer.

```python
print(s4.to_cycles((1, 0, 3, 2)))
print(s4.from_cycles([(0, 1), (2, 3)]))
print(s4.to_cycles((1, 2, 3, 0)))
```

The first is a product of two transpositions and the third is a single four
cycle. The cycle type, that is the multiset of cycle lengths, determines the
conjugacy class, which is the fact that makes the symmetric group's
structure so tractable.

```python
from collections import Counter

types = Counter(tuple(sorted(map(len, s4.to_cycles(p)))) for p in s4.elements())
print(dict(types))
print(len(types), len(s4.conjugacy_classes()))
```

Five cycle types and five conjugacy classes, and the counts of each match.
The cycle types of permutations of four letters are the partitions of four,
which connects this to the combinatorics package.

```python
from discretus.combinatorics.generation import integer_partitions

print(len(list(integer_partitions(4))))
```

The sign of a permutation is one for an even number of transpositions and
minus one for an odd number, and the even permutations form the alternating
group.

```python
from discretus.algebra.groups import AlternatingGroup

print(s4.sign((1, 0, 2, 3)), s4.sign((1, 2, 0, 3)))
a4 = AlternatingGroup(4)
print(a4.order(), s4.order() // 2)
print(s4.is_normal(a4))
```

The alternating group always has index two and is therefore normal, which is
why the sign is a homomorphism onto the group of order two.

A permutation group can also be given by generators, which is how a group of
symmetries is usually specified in practice.

```python
rotations = PermutationGroup([(1, 2, 3, 0)])
print(rotations.order(), rotations.is_cyclic())

square = PermutationGroup([(1, 2, 3, 0), (3, 2, 1, 0)])
print(square.order())
print(square.order() == 8)
```

The first generator is a four cycle and generates a cyclic group of order
four. Adding a reflection gives a group of order eight, which is the
dihedral group of the square realized as permutations of its corners.
Cayley's theorem says every finite group can be realized this way.

```python
from discretus.algebra.groups import DihedralGroup, are_isomorphic

print(are_isomorphic(square, DihedralGroup(4)))
```

## Reading an axiom failure

The library refuses to build a structure that fails its axioms, and the
error is designed to be actionable rather than merely negative. Learning to
read it saves time.

```python
from discretus import AxiomViolationError
from discretus.core.algebraic_base import GroupBase

# Not closed: the operation leaves the carrier.
try:
    GroupBase([0, 1, 2], lambda a, b: a + b, symbol="+")
except AxiomViolationError as error:
    print("1:", error.axiom, "|", error.detail)

# Not associative.
try:
    GroupBase([0, 1, 2], lambda a, b: (a - b) % 3, symbol="-")
except AxiomViolationError as error:
    print("2:", error.axiom, "|", error.detail)

# No identity.
try:
    GroupBase([1, 2], lambda a, b: 1, symbol="*")
except AxiomViolationError as error:
    print("3:", error.axiom, "|", error.detail)

# No inverse for one element.
try:
    GroupBase([0, 1, 2, 3], lambda a, b: (a * b) % 4, symbol=".")
except AxiomViolationError as error:
    print("4:", error.axiom, "|", error.detail)
```

Each error names the axiom and, where one exists, the counterexample. The
first reports the product that left the carrier, the second reports the
triple that broke associativity, and the fourth reports the element without
an inverse. That is the information needed to fix the structure or to
understand why it cannot be a group.

The verification costs cubic time in the carrier size, dominated by
associativity, and it can be skipped when a caller has already established
the axioms and is building many structures in a loop.

```python
from discretus.utils.timing import Timer

with Timer() as checked:
    GroupBase(list(range(24)), lambda a, b: (a + b) % 24, symbol="+")
with Timer() as unchecked:
    GroupBase(list(range(24)), lambda a, b: (a + b) % 24, symbol="+", verify=False)
print(checked.human, unchecked.human)
```

Skipping verification is a deliberate choice with a real cost: a structure
that silently fails its axioms produces wrong answers everywhere downstream,
and none of them will point back here. The default is to check.

## Exercises

1. Verify Lagrange's theorem for every group in the families above, and find
   a divisor of a group order for which no subgroup exists.
2. Show that the dihedral group of order eight and the quaternion group have
   the same element order multiset and are not isomorphic, by finding an
   invariant that distinguishes them.
3. Compute the subgroup lattice of the cyclic group of order twelve as a
   partial order under inclusion, and confirm it is a lattice.
4. Count the distinct colourings of the faces of a cube with three colours,
   up to rotation, using Burnside's lemma and the rotation group.
5. Verify the class equation for the symmetric group on four letters: the
   class sizes sum to the order and each divides it.
6. Build the Cayley graph of the symmetric group on three letters with two
   different generating sets and compare their diameters.

## From groups to rings and fields

Groups have one operation. Adding a second one, distributive over the first,
gives a ring, and the step is worth taking here because the tutorial has
already built everything it needs.

```python
from discretus.algebra.rings import Zmod

ring = Zmod(12)
print(ring.zero(), ring.one(), ring.characteristic())
print(ring.add(7, 8), ring.multiply(7, 8))
print(ring.additive_group().is_abelian())
```

The additive group of the ring is the cyclic group of order twelve, which is
the group the earlier sections used. The multiplicative structure is the new
part, and it is not a group, because not every element is invertible.

```python
print(ring.units())
print(ring.zero_divisors())
print(len(ring.units()) + len(ring.zero_divisors()) + 1 == ring.order())
```

Every nonzero element is a unit or a zero divisor, and that dichotomy is the
content of the last line. The units form a group, and it is the group whose
order is the Euler totient.

```python
from discretus.number_theory.functions import euler_totient

print(len(ring.units()) == euler_totient(12))
```

A ring in which every nonzero element is a unit is a field, and for the
integers modulo $n$ that happens exactly when $n$ is prime.

```python
from discretus.number_theory.primes import is_prime

for n in (7, 8, 11, 12):
    print(n, Zmod(n).is_field(), is_prime(n))
```

Finite fields exist for every prime power order and for no other order,
which is the theorem that makes coding theory and much of cryptography
possible.

```python
from discretus import InfeasibleError
from discretus.algebra.fields import GaloisField, PrimeField

print(PrimeField(7).order(), GaloisField(2, 3).order())
try:
    GaloisField(6, 1)
except InfeasibleError as error:
    print("no field of order six:", error)
```

The multiplicative group of a finite field is cyclic, which brings the
tutorial back to where it started: the structure of a finite field's units
is a cyclic group, and everything proved about cyclic groups applies to it.

```python
field = GaloisField(2, 3)
group = field.multiplicative_group()
print(len(group), field.order() - 1)
generator = field.primitive_element()
print(generator, field.element_order(generator) == field.order() - 1)
```

Eight elements, seven of them nonzero, and a generator whose order is seven.
A cyclic group of order seven, inside a field of order eight, built from a
polynomial over the field of two elements. That chain of constructions is
the reward for the axioms at the start of the tutorial.

## Where to go next

- The [algebra reference](../api/algebra.md) for rings, fields,
  polynomials, and exact linear algebra, which this tutorial did not reach.
- [Number theory](number_theory.md), where the unit groups of this tutorial
  come from.
- [Set theory](set_theory.md), for the lattices that subgroup structures
  form.
- The [graph reference](../api/graphs.md), for everything that can be done
  with a Cayley graph once it exists.
