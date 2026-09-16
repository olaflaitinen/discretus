# `discretus.combinatorics`

The combinatorics package counts, generates, and enumerates. It computes the
classical counting functions and integer sequences exactly, it yields
combinatorial objects lazily so that spaces far too large to store can still
be traversed, and it maps those objects bijectively to indices so that a
space can be addressed without being enumerated.

## Mathematical basis

The number of ordered arrangements and of unordered selections of $k$
objects from $n$ are

$$P(n, k) = \frac{n!}{(n-k)!}, \qquad
\binom{n}{k} = \frac{n!}{k!\,(n-k)!},$$

and the binomial coefficients satisfy the Pascal identity and the
Vandermonde convolution,

$$\binom{n}{k} = \binom{n-1}{k-1} + \binom{n-1}{k}, \qquad
\binom{m+n}{r} = \sum_{k=0}^{r} \binom{m}{k}\binom{n}{r-k}.$$

Among the sequences the package computes, the Catalan, Bell, and Stirling
numbers of the second kind are

$$C_n = \frac{1}{n+1}\binom{2n}{n}, \qquad
B_n = \sum_{k=0}^{n} S(n, k), \qquad
S(n, k) = \frac{1}{k!}\sum_{j=0}^{k} (-1)^{j}\binom{k}{j}(k-j)^{n}.$$

The principle of inclusion and exclusion counts a union through its
intersections,

$$\left| \bigcup_{i=1}^{n} A_i \right|
= \sum_{\emptyset \neq S \subseteq \{1,\dots,n\}} (-1)^{|S|+1}
\left| \bigcap_{i \in S} A_i \right|.$$

Every one of these is computed with exact integer arithmetic, so a
coefficient with three hundred digits is simply an integer with three
hundred digits.

## Module map

| Subpackage | Responsibility |
| --- | --- |
| `counting` | Counting functions and identities |
| `sequences` | Classical integer sequences |
| `generation` | Lazy generators, ranking, and unranking |
| `generating_functions` | Formal power series, ordinary and exponential |
| `polya` | Cycle index polynomials, Burnside, Polya enumeration |
| `designs` | Block designs, Latin squares, Steiner systems, Ramsey |
| `probability` | Discrete distributions, expectation, urn models |

## Counting

| Routine | Counts | Complexity |
| --- | --- | --- |
| `factorial(n)` | Arrangements of n objects | O(n) multiplications |
| `falling_factorial(n, k)` | Ordered selections | O(k) |
| `rising_factorial(n, k)` | The rising analogue | O(k) |
| `permutations_count(n, k)` | Ordered selections of k from n | O(k) |
| `combinations_count(n, k)` | Unordered selections | O(min(k, n - k)) |
| `binomial(n, k)` | The binomial coefficient | O(min(k, n - k)) |
| `multinomial(parts)` | Arrangements of a multiset | O(total) |
| `multiset_permutations_count(counts)` | Distinct arrangements | O(total) |
| `multiset_combinations_count(counts, k)` | Selections with repetition | O(total times k) |
| `derangements(n)` | Permutations with no fixed point | O(n) |
| `pascal_row(n)` | One row of the triangle | O(n) |
| `pascal_triangle(n)` | The first n rows | O(n squared) |
| `inclusion_exclusion(sizes)` | The union size from intersection sizes | O(2 to the n) |
| `pigeonhole(items, boxes)` | The guaranteed minimum occupancy | O(1) |
| `twelvefold(n, k, ...)` | The twelvefold way, by injectivity and symmetry | Varies |

`binomial` iterates over the smaller of the two tails and divides as it
goes, so it never builds a factorial larger than the answer needs. That
matters: computing a coefficient as a ratio of three factorials for
arguments in the thousands wastes most of the work on digits that cancel.

```python
>>> from discretus.combinatorics.counting import binomial, derangements
>>> binomial(100, 50)
100891344545564193334812497256
>>> derangements(6)
265
```

The twelvefold way deserves a note, because it is the organizing idea of the
subject rather than one more routine. It classifies the ways of placing $n$
balls into $k$ boxes by whether the balls and boxes are distinguishable and
by whether the placement is arbitrary, injective, or surjective. The routine
takes those three choices as arguments and dispatches to the right counting
function, which makes the table in a textbook executable.

## Sequences

Every sequence is exact and memoized, so the terms of one call are available
to the next at no cost.

| Routine | Sequence |
| --- | --- |
| `bell(n)` | Set partitions of an n member set |
| `bernoulli(n)` | Bernoulli numbers, as exact rationals |
| `catalan(n)` | Balanced parenthesizations, binary trees, and much else |
| `composition_number(n)` | Compositions of n |
| `eulerian(n, k)` | Permutations with k descents |
| `fibonacci_like(n, first, second)` | Any two term linear recurrence |
| `lah(n, k)` | Lah numbers |
| `motzkin(n)` | Motzkin paths |
| `narayana(n, k)` | Narayana numbers |
| `partition_number(n)` | Integer partitions of n |
| `stirling_first(n, k)` | Permutations with k cycles, signless |
| `stirling_second(n, k)` | Set partitions into k blocks |

```python
>>> from discretus.combinatorics.sequences import bell, catalan, stirling_second
>>> [catalan(n) for n in range(8)]
[1, 1, 2, 5, 14, 42, 132, 429]
>>> bell(6), stirling_second(5, 2)
(203, 15)
```

Each routine is implemented through the recurrence that defines the
sequence, not through a closed form with floating point in it, because the
closed forms lose exactness at moderate arguments. The Bernoulli numbers are
returned as `Fraction` values for the same reason: they are not integers,
and rounding them would make the Euler Maclaurin formula useless.

## Generation, ranking, and unranking

The generators yield objects one at a time and hold only the current object,
so a space with billions of members can be traversed and a search that stops
early costs only what it consumed.

| Routine | Yields | Order |
| --- | --- | --- |
| `permutations(items)` | Every arrangement | Lexicographic |
| `permutations_of_length(items, k)` | Ordered selections | Lexicographic |
| `combinations(items, k)` | Unordered selections | Lexicographic |
| `subsets(items)` | Every subset | By size, then lexicographic |
| `subsets_gray_code(items)` | Every subset | Gray code, one change per step |
| `tuples(items, length)` | Cartesian powers | Lexicographic |
| `compositions(n, parts=None)` | Ordered sums | Lexicographic |
| `integer_partitions(n)` | Unordered sums | Reverse lexicographic |
| `set_partitions(items)` | Partitions of a set | Restricted growth strings |
| `necklaces(alphabet, length)` | Cyclic words up to rotation | Lexicographic |
| `lyndon_words(alphabet, length)` | Aperiodic necklace representatives | Lexicographic |

```python
>>> from discretus.combinatorics.generation import integer_partitions, subsets_gray_code
>>> list(subsets_gray_code([1, 2, 3]))
[(), (1,), (1, 2), (2,), (2, 3), (1, 2, 3), (1, 3), (3,)]
>>> list(integer_partitions(5))
[(5,), (4, 1), (3, 2), (3, 1, 1), (2, 2, 1), (2, 1, 1, 1), (1, 1, 1, 1, 1)]
```

The Gray code order is the one where consecutive subsets differ in exactly
one member, which is what makes it the right enumeration when each step has
a cost proportional to the change rather than to the whole object.

Ranking and unranking are inverse bijections between objects and indices in
a documented order. They make it possible to address a combinatorial space
directly, which is what a distributed enumeration, a random selection
without rejection, and a compact encoding all need.

```python
>>> from discretus.combinatorics.generation import (
...     combination_rank, combination_unrank, permutation_rank, permutation_unrank,
... )
>>> permutation_rank((2, 0, 1))
4
>>> permutation_unrank(3, 4)
(2, 0, 1)
>>> combination_unrank(5, 3, 7)
(1, 2, 4)
>>> combination_rank((1, 2, 4), 5)
7
```

Ranking a permutation of $n$ elements costs $O(n^2)$ in the transparent
implementation and $O(n \log n)$ in the tuned one, and both are shipped with
the tuned one validated against the transparent one. Unranking an object
whose index has hundreds of digits works, because the index is an unbounded
integer like everything else.

## Generating functions

A formal power series is a first class object, so the manipulations of
analytic combinatorics can be carried out and then evaluated.

| Routine or type | Meaning |
| --- | --- |
| `FormalPowerSeries(coefficients)` | A truncated or lazily extended series |
| `OrdinaryGeneratingFunction` | The ordinary form |
| `ExponentialGeneratingFunction` | The exponential form, with factorial weights |
| `add`, `multiply`, `scale` | Ring operations |
| `convolve(left, right)` | The coefficientwise convolution |
| `compose(outer, inner)` | Substitution of one series into another |
| `invert(series)` | The multiplicative inverse, when the constant term is a unit |
| `coefficient(series, n)` | Extraction of one coefficient |
| `coefficients(series, upto)` | The first several coefficients |

```python
>>> from discretus.combinatorics.generating_functions import (
...     OrdinaryGeneratingFunction as Ogf,
... )
>>> geometric = Ogf.geometric()          # 1 + x + x squared + ...
>>> squared = geometric * geometric
>>> squared.coefficients(5)
[1, 2, 3, 4, 5]
```

The example is the identity that the square of the geometric series has the
positive integers as its coefficients, which is the smallest useful
demonstration that the arithmetic is right. A series may be given by a rule
rather than a list, in which case it is extended lazily as far as a
coefficient is requested.

## Polya enumeration

Counting up to symmetry is a different problem from counting, and it needs
group theory.

| Routine | Meaning |
| --- | --- |
| `cycle_index(group, degree)` | The cycle index polynomial of a permutation group |
| `burnside(group, colours)` | Orbit count by Burnside's lemma |
| `polya_enumerate(group, weights)` | The pattern inventory |

Burnside's lemma states that the number of orbits equals the average number
of fixed points of the group elements,

$$|X / G| = \frac{1}{|G|} \sum_{g \in G} |\mathrm{Fix}(g)|,$$

and the module computes both sides, so the identity can be checked rather
than assumed. The group argument comes from
[`discretus.algebra`](algebra.md), which is the clearest instance of the two
packages cooperating without importing one another: the group is passed in
as data.

```python
>>> from discretus.algebra.groups import CyclicGroup
>>> from discretus.combinatorics.polya import burnside
>>> burnside(CyclicGroup(4), colours=2)       # necklaces of four beads, two colours
6
```

## Designs

| Type or routine | Meaning |
| --- | --- |
| `BlockDesign(points, blocks)` | An incidence structure, with its parameters |
| `is_balanced(design)` | Whether every pair occurs in the same number of blocks |
| `LatinSquare(rows)` | A square with each symbol once per row and column |
| `is_reduced(square)`, `orthogonal(left, right)` | Latin square properties |
| `SteinerSystem(order, block_size)` | A Steiner system, when one exists |
| `sperner_family(items)` | An antichain of subsets, with Sperner's bound |
| `ramsey_number(s, t)` | Known values and bounds |

Ramsey numbers are a good illustration of the library's honesty about cost.
The exact values are known for very few cases, so the routine returns the
known value when it exists and otherwise returns the best known interval
together with its source, rather than either guessing or raising.

## Discrete probability

| Routine or type | Meaning |
| --- | --- |
| `DiscreteDistribution(weights)` | A distribution over a finite set, exact |
| `probability(event, distribution)` | The probability of a subset |
| `counting_probability(favourable, total)` | The classical ratio, exact |
| `expectation(distribution, value)` | The expected value, exact |
| `variance(distribution, value)` | The variance, exact |
| `urn_draw(urn, draws, replace)` | Urn model probabilities |

Probabilities are exact rationals rather than floats, so the probability of
a hand in a card game is a fraction whose denominator is the number of
hands, and a sequence of conditional probabilities multiplies without drift.

```python
>>> from discretus.combinatorics.probability import counting_probability
>>> from discretus.combinatorics.counting import binomial
>>> counting_probability(binomial(13, 5), binomial(52, 5))
Fraction(33, 66640)
```

## Choosing between counting, generating, and ranking

The package offers three ways to work with a combinatorial space, and
picking the right one is usually the whole of the performance question.

**Count** when you need the size and nothing else. A count is a closed form
or a short recurrence, so it is cheap regardless of how large the space is.
The number of ways to deal a bridge hand is a single multiplication of a few
dozen digits; enumerating the hands is not possible in any amount of time.

**Generate** when you need to examine the members and the space is small
enough that you will visit a useful fraction of it, or when you will stop
early. A search for the first object with a property is a generation
problem, and the laziness means the cost is proportional to how far the
search went rather than to the size of the space.

**Rank and unrank** when you need to address the space without traversing
it. Three situations call for it. Drawing a uniformly random member: draw a
random index below the count and unrank it, which is exact and needs no
rejection loop. Splitting work across processes: give each worker an index
range, and no coordination is needed because unranking is a pure function.
Storing a member compactly: an index is one integer, and a permutation of a
thousand elements is a thousand.

```python
from discretus.combinatorics.counting import combinations_count
from discretus.combinatorics.generation import combination_unrank
from discretus.core.random_base import SeededRandom

total = combinations_count(52, 5)
source = SeededRandom(2026)
hand = combination_unrank(52, 5, source.integer(0, total - 1))
print(total, hand)
```

The mistake this replaces is generating all members and then choosing one,
which is the natural first idea and is impossible here: there are over two
and a half million five card hands, and for a seven card hand there are over
a hundred and thirty million.

## Worked example: count, then verify by enumeration

The most useful habit in combinatorics is to count a small case twice, once
by the formula and once by brute force, because a wrong formula and a wrong
enumeration almost never agree. The package is designed to make that
comparison a two line assertion, and the test suite is full of them.

```python
from itertools import permutations as raw_permutations

from discretus.combinatorics.counting import (
    binomial,
    derangements,
    multinomial,
    permutations_count,
)
from discretus.combinatorics.generation import (
    combinations,
    integer_partitions,
    set_partitions,
    subsets,
)
from discretus.combinatorics.sequences import bell, partition_number, stirling_second

items = list(range(6))

# Arrangements and selections against the generators.
assert permutations_count(6, 3) == sum(1 for _ in raw_permutations(items, 3))
assert binomial(6, 3) == sum(1 for _ in combinations(items, 3))
assert 2 ** 6 == sum(1 for _ in subsets(items))

# Set partitions against the Bell and Stirling numbers.
assert bell(6) == sum(1 for _ in set_partitions(items))
assert stirling_second(6, 3) == sum(
    1 for partition in set_partitions(items) if len(partition) == 3
)

# Integer partitions against the partition number.
assert partition_number(10) == sum(1 for _ in integer_partitions(10))

# Derangements against a direct count of fixed point free permutations.
assert derangements(6) == sum(
    1
    for arrangement in raw_permutations(items)
    if all(position != value for position, value in enumerate(arrangement))
)

# A multinomial against the distinct arrangements of a multiset.
word = "aabbc"
assert multinomial([2, 2, 1]) == len({"".join(p) for p in raw_permutations(word)})

print("every count agrees with its enumeration")
```

Each assertion pins a different identity, and together they exercise most of
the package. The pattern extends to anything new you add: compute the
quantity by the formula you believe, enumerate the same quantity for the
largest case you can afford, and assert that they match. When they do not,
the small case is small enough to inspect by hand, which is why the check
belongs at size six rather than at size sixty.

The same technique validates the ranking bijections in both directions, and
this is exactly what the suite asserts for them:

```python
from discretus.combinatorics.generation import (
    permutation_rank,
    permutation_unrank,
    permutations,
)

for index, arrangement in enumerate(permutations(range(5))):
    assert permutation_rank(arrangement) == index
    assert permutation_unrank(5, index) == arrangement
print("ranking is a bijection on all 120 permutations of five elements")
```

A bijection checked in one direction only is a common source of defects,
because an implementation can be self consistent and still disagree with the
documented order. Asserting both directions against the enumeration pins the
order as well as the inverse property.

## Complexity summary

| Routine | Complexity |
| --- | --- |
| `factorial(n)` | O(n) multiplications on growing integers |
| `binomial(n, k)` | O(min(k, n - k)) |
| `catalan(n)`, `bell(n)`, Stirling numbers | O(n) to O(n squared) with memoization |
| `partition_number(n)` | O(n to the 1.5) by the pentagonal recurrence |
| Permutation generation | O(1) amortized per object |
| Subset generation | O(1) amortized per object |
| Integer partition generation | O(1) amortized per partition |
| Set partition generation | O(1) amortized per partition |
| Permutation ranking | O(n squared) transparent, O(n log n) tuned |
| Combination ranking | O(k) with cached binomials |
| Series multiplication to n terms | O(n squared) |
| Inclusion and exclusion over n sets | O(2 to the n) |
| Burnside over a group of order g | O(g) fixed point counts |

## Errors

| Exception | Raised when |
| --- | --- |
| `DomainError` | A negative argument to a factorial, or k outside the range for a coefficient |
| `ValidationError` | A multiset count list contains a negative entry, or a rank is out of range |
| `LimitExceededError` | A generator's output was materialized beyond the configured limit |
| `InfeasibleError` | A design or a Steiner system with the requested parameters does not exist |

A rank outside the range of the space is a validation error rather than an
infeasible request, because the space is known in advance: unranking index
one million in a space of five thousand objects is a mistake in the caller.

## Design notes

**Counting and generating are separate.** `combinations_count` and
`combinations` answer different questions, and conflating them would force
either the count to enumerate or the enumeration to be counted first. Every
subpackage here keeps the two apart, and the names differ by the `_count`
suffix so that the choice is visible at the call site.

**Generators are lazy by default.** Returning a list would be friendlier for
small inputs and disastrous for large ones, and a library cannot know which
it has. The generators therefore yield, and the caller wraps in `list` when
the space is small, which is an explicit acknowledgment that it fits.

**The enumeration order is documented and stable.** Ranking is only
meaningful relative to an order, so the order is part of the interface
rather than an implementation detail, and it will not change within a major
version.

**Sequences are memoized without bound.** The argument space of these
sequences is small in practice, and the terms are reused, so the cache is
worth its memory. `discretus.core.lazy.memoized_recursion` provides it, and
the cache is inspectable, which is what makes the behaviour testable.

## See also

- [`discretus.sets`](sets.md), whose power sets, partitions, and products
  these routines count.
- [`discretus.algebra`](algebra.md), for the permutation groups that the
  Polya machinery consumes.
- [`discretus.recurrences`](recurrences.md), for solving the recurrences
  these sequences satisfy.
- [`discretus.number_theory`](number_theory.md), for the arithmetic
  functions that appear in the same identities.
