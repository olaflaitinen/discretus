# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

"""Benchmarks for the combinatorics package.

This package is where the difference between counting, generating, and
ranking is measured rather than described. The reference tells a reader to
count when they need the size, to generate when they will examine the
members, and to rank when they need to address the space without traversing
it. Those three answers to the same question differ by many orders of
magnitude, and this file is where that claim is demonstrated.

What is measured, and why:

    The counting functions, because they are called constantly and because
    they operate on integers that grow: a binomial coefficient with a
    thousand digits is a thousand digit integer, and the cost of the
    arithmetic is part of the cost of the routine.

    The classical sequences, both cold and warm, because they memoize. A
    sequence whose hundredth term is free after its ninety ninth behaves
    very differently on a second call, and both numbers are worth having.

    The lazy generators, at a prefix and in full, because the promise that a
    generator can traverse a space too large to store is a promise that only
    a prefix measurement can check: producing the first ten objects of a
    space with a quadrillion members must cost the same as producing the
    first ten of a space with a million.

    Ranking and unranking, because they are what make a distributed
    enumeration, an exact uniform sample, and a compact encoding possible,
    and because the reference states two different complexities for the
    transparent and the tuned permutation ranking.

    Formal power series multiplication, because it is quadratic in the term
    count and is the operation an analytic combinatorics computation repeats.

    Polya enumeration, because its cost is the group order times the fixed
    point computation, which is a bound that only makes sense once measured
    against a real group.

Everything is exact. That is the point of the package, and it is also why
the integer sizes in the growth report matter: a factorial of ten thousand
is a thirty five thousand digit integer, and a routine that is linear in the
argument is not linear in the number of digits.
"""

from __future__ import annotations

from typing import Any, List, Tuple

from . import benchmark, require, requires_all, seeded

# ---------------------------------------------------------------------------
# The modules under measurement
# ---------------------------------------------------------------------------

counting_module = require(
    "discretus.combinatorics.counting", "factorial", "binomial", "multinomial"
)
sequences_module = require(
    "discretus.combinatorics.sequences", "catalan", "bell", "stirling_second"
)
generation_module = require(
    "discretus.combinatorics.generation",
    "permutations",
    "subsets",
    "permutation_rank",
)
series_module = require(
    "discretus.combinatorics.generating_functions", "OrdinaryGeneratingFunction"
)
polya_module = require("discretus.combinatorics.polya", "burnside", "cycle_index")
designs_module = require("discretus.combinatorics.designs", "LatinSquare")
probability_module = require(
    "discretus.combinatorics.probability", "DiscreteDistribution", "expectation"
)
groups_module = require("discretus.algebra.groups", "CyclicGroup", "SymmetricGroup")

GROUP_COUNTING = "combinatorics.counting"
GROUP_SEQUENCES = "combinatorics.sequences"
GROUP_GENERATION = "combinatorics.generation"
GROUP_RANKING = "combinatorics.ranking"
GROUP_SERIES = "combinatorics.series"
GROUP_POLYA = "combinatorics.polya"
GROUP_DESIGNS = "combinatorics.designs"
GROUP_PROBABILITY = "combinatorics.probability"

#: How many objects the prefix benchmarks take from a generator. Ten is
#: enough to pay the start up cost and few enough that the measurement is
#: independent of the size of the space, which is the property being tested.
PREFIX = 10


# ---------------------------------------------------------------------------
# Input preparation
# ---------------------------------------------------------------------------


def make_item_list(size: int) -> List[int]:
    """Return a list of distinct integers of the given length."""
    return list(range(size))


def make_shuffled_list(size: int) -> List[int]:
    """Return a reproducibly shuffled list, so the input is not sorted.

    A sorted input can be the best case for a generator that walks in
    lexicographic order, so the shuffled version is the honest one for
    anything that reads the input rather than only its length.
    """
    source = seeded(f"combinatorics.shuffled.{size}")
    items = list(range(size))
    source.shuffle(items)
    return items


def make_permutation(size: int) -> Tuple[int, ...]:
    """Return a reproducible permutation in one line notation."""
    source = seeded(f"combinatorics.permutation.{size}")
    items = list(range(size))
    source.shuffle(items)
    return tuple(items)


def make_rank_and_size(size: int) -> Tuple[int, int]:
    """Return a size and a rank in the middle of its permutation space.

    The rank is an exact integer with as many digits as the factorial has,
    which is the case that distinguishes an implementation using unbounded
    integers from one that does not.
    """
    if counting_module is None:
        return size, 0
    total = counting_module.factorial(size)
    return size, total // 2


def make_combination_rank(size: int) -> Tuple[int, int, int]:
    """Return a ground size, a subset size, and a rank in the middle."""
    if counting_module is None:
        return size, size // 2, 0
    chosen = size // 2
    total = counting_module.binomial(size, chosen)
    return size, chosen, total // 2


def make_series(terms: int) -> Any:
    """Return an ordinary generating function with the given term count."""
    assert series_module is not None
    source = seeded(f"combinatorics.series.{terms}")
    coefficients = [source.randint(0, 100) for _ in range(terms)]
    return series_module.OrdinaryGeneratingFunction(coefficients)


def make_two_series(terms: int) -> Tuple[Any, Any]:
    """Return two generating functions of the same term count."""
    return make_series(terms), make_series(terms + 1)


def make_cyclic_group(order: int) -> Any:
    """Return a cyclic group of the given order, for the Polya benchmarks."""
    assert groups_module is not None
    return groups_module.CyclicGroup(order)


def make_symmetric_group(letters: int) -> Any:
    """Return a symmetric group on the given number of letters.

    The letter count is small because the group has its factorial as its
    order, which is the quantity the Polya cost is proportional to.
    """
    assert groups_module is not None
    return groups_module.SymmetricGroup(letters)


def make_latin_square(order: int) -> Any:
    """Return the cyclic Latin square of the given order."""
    assert designs_module is not None
    rows = [[(row + column) % order for column in range(order)] for row in range(order)]
    return designs_module.LatinSquare(rows)


def make_distribution(outcomes: int) -> Any:
    """Return a discrete distribution over the given number of outcomes."""
    assert probability_module is not None
    source = seeded(f"combinatorics.distribution.{outcomes}")
    weights = {index: source.randint(1, 100) for index in range(outcomes)}
    return probability_module.DiscreteDistribution(weights)


# ---------------------------------------------------------------------------
# Counting
# ---------------------------------------------------------------------------


@benchmark(
    group=GROUP_COUNTING,
    sizes=[1_000, 5_000, 20_000],
    complexity="O(n) multiplications on growing integers",
    requires=counting_module,
    note=(
        "linear in the argument and superlinear in the digits, because the "
        "product grows; the implied exponent should exceed one"
    ),
)
def factorial(size: int) -> int:
    """Compute a factorial exactly."""
    return counting_module.factorial(size)


@benchmark(
    group=GROUP_COUNTING,
    sizes=[1_000, 10_000, 100_000],
    complexity="O(min(k, n - k))",
    requires=counting_module,
    note=(
        "iterates the smaller tail and divides as it goes, so it never "
        "builds a factorial larger than the answer needs"
    ),
)
def binomial_middle(size: int) -> int:
    """Compute the central binomial coefficient."""
    return counting_module.binomial(size, size // 2)


@benchmark(
    group=GROUP_COUNTING,
    sizes=[1_000, 10_000, 100_000],
    complexity="O(min(k, n - k))",
    requires=counting_module,
    note="a small tail, which should be far cheaper than the central one",
)
def binomial_edge(size: int) -> int:
    """Compute a binomial coefficient with a small second argument."""
    return counting_module.binomial(size, 5)


@benchmark(
    group=GROUP_COUNTING,
    sizes=[100, 500, 2_000],
    complexity="O(n squared)",
    requires=counting_module,
)
def pascal_triangle(rows: int) -> Any:
    """Build the first rows of Pascal's triangle."""
    return counting_module.pascal_triangle(rows)


@benchmark(
    group=GROUP_COUNTING,
    sizes=[100, 1_000, 5_000],
    complexity="O(total)",
    requires=counting_module,
)
def multinomial(parts: int) -> int:
    """Compute a multinomial coefficient over many parts."""
    return counting_module.multinomial([3] * parts)


@benchmark(
    group=GROUP_COUNTING,
    sizes=[1_000, 10_000, 50_000],
    complexity="O(n)",
    requires=counting_module,
)
def derangements(size: int) -> int:
    """Count the permutations with no fixed point."""
    return counting_module.derangements(size)


@benchmark(
    group=GROUP_COUNTING,
    sizes=[10, 15, 20],
    complexity="O(2 to the n)",
    requires=counting_module,
    note="inclusion and exclusion, exponential in the number of sets",
)
def inclusion_exclusion(sets: int) -> int:
    """Apply inclusion and exclusion over the given number of sets."""
    source = seeded(f"combinatorics.inclusion.{sets}")
    sizes = {
        frozenset(subset): source.randint(1, 100)
        for subset in _subsets_of(range(sets))
        if subset
    }
    return counting_module.inclusion_exclusion(sizes)


def _subsets_of(items: Any) -> Any:
    """Yield every subset of a small iterable, for the helper above."""
    items = list(items)
    for mask in range(1 << len(items)):
        yield tuple(value for index, value in enumerate(items) if mask >> index & 1)


# ---------------------------------------------------------------------------
# Sequences
# ---------------------------------------------------------------------------


@benchmark(
    group=GROUP_SEQUENCES,
    sizes=[100, 500, 2_000],
    complexity="O(n) with memoization",
    requires=sequences_module,
    note="the cold cost, measured on a fresh cache where possible",
)
def catalan(index: int) -> int:
    """Compute a Catalan number."""
    return sequences_module.catalan(index)


@benchmark(
    group=GROUP_SEQUENCES,
    sizes=[100, 500, 2_000],
    complexity="O(1) after the first call",
    requires=sequences_module,
    note=(
        "the same term requested a hundred times; the ratio against the "
        "benchmark above is what the memoization is worth"
    ),
)
def catalan_warm(index: int) -> int:
    """Compute the same Catalan number a hundred times."""
    total = 0
    for _ in range(100):
        total = sequences_module.catalan(index)
    return total


@benchmark(
    group=GROUP_SEQUENCES,
    sizes=[100, 300, 800],
    complexity="O(n squared) through the triangle",
    requires=sequences_module,
)
def bell(index: int) -> int:
    """Compute a Bell number."""
    return sequences_module.bell(index)


@benchmark(
    group=GROUP_SEQUENCES,
    sizes=[100, 300, 800],
    complexity="O(n k) through the recurrence",
    requires=sequences_module,
)
def stirling_second(index: int) -> int:
    """Compute a Stirling number of the second kind."""
    return sequences_module.stirling_second(index, index // 3)


@benchmark(
    group=GROUP_SEQUENCES,
    sizes=[100, 300, 800],
    complexity="O(n k)",
    requires=sequences_module,
)
def stirling_first(index: int) -> int:
    """Compute a Stirling number of the first kind."""
    return sequences_module.stirling_first(index, index // 3)


@benchmark(
    group=GROUP_SEQUENCES,
    sizes=[1_000, 5_000, 20_000],
    complexity="O(n to the 1.5) by the pentagonal recurrence",
    requires=sequences_module,
    note="the implied exponent should be near one and a half rather than two",
)
def partition_number(index: int) -> int:
    """Compute the number of integer partitions."""
    return sequences_module.partition_number(index)


@benchmark(
    group=GROUP_SEQUENCES,
    sizes=[100, 500, 2_000],
    complexity="O(n squared) exact rational arithmetic",
    requires=sequences_module,
    note="returned as exact fractions, because they are not integers",
)
def bernoulli(index: int) -> Any:
    """Compute a Bernoulli number exactly."""
    return sequences_module.bernoulli(index)


@benchmark(
    group=GROUP_SEQUENCES,
    sizes=[1_000, 10_000],
    complexity="O(n) per prefix",
    requires=sequences_module,
    note="the whole prefix rather than one term, which is the common use",
)
def catalan_prefix(count: int) -> List[int]:
    """Compute the first several Catalan numbers."""
    return [sequences_module.catalan(index) for index in range(count)]


# ---------------------------------------------------------------------------
# Generation
# ---------------------------------------------------------------------------


@benchmark(
    group=GROUP_GENERATION,
    sizes=[7, 8, 9],
    complexity="O(1) amortized per object, n factorial objects",
    setup=make_item_list,
    requires=generation_module,
    note="the size is the letter count, so each step multiplies the work",
)
def permutations_full(items: List[int]) -> int:
    """Traverse every permutation of a small list."""
    return sum(1 for _ in generation_module.permutations(items))


@benchmark(
    group=GROUP_GENERATION,
    sizes=[10, 100, 1_000, 10_000],
    complexity="O(1) to produce the first object",
    setup=make_item_list,
    requires=generation_module,
    note=(
        "takes ten permutations of a space with the factorial as its size; "
        "this must be flat in the size, which is what laziness means"
    ),
)
def permutations_prefix(items: List[int]) -> int:
    """Take the first few permutations of a very large space."""
    taken = 0
    for _ in generation_module.permutations(items):
        taken += 1
        if taken == PREFIX:
            break
    return taken


@benchmark(
    group=GROUP_GENERATION,
    sizes=[16, 18, 20],
    complexity="O(1) amortized per subset, 2 to the n subsets",
    setup=make_item_list,
    requires=generation_module,
)
def subsets_full(items: List[int]) -> int:
    """Traverse every subset of a list."""
    return sum(1 for _ in generation_module.subsets(items))


@benchmark(
    group=GROUP_GENERATION,
    sizes=[16, 18, 20],
    complexity="O(1) amortized per subset",
    setup=make_item_list,
    requires=generation_module,
    note=(
        "Gray code order, where consecutive subsets differ in one member, "
        "which is the right enumeration when each step costs the change"
    ),
)
def subsets_gray_code(items: List[int]) -> int:
    """Traverse every subset in Gray code order."""
    return sum(1 for _ in generation_module.subsets_gray_code(items))


@benchmark(
    group=GROUP_GENERATION,
    sizes=[18, 20, 22],
    complexity="O(1) amortized per selection",
    setup=make_item_list,
    requires=generation_module,
)
def combinations_full(items: List[int]) -> int:
    """Traverse every selection of half the items."""
    return sum(1 for _ in generation_module.combinations(items, len(items) // 2))


@benchmark(
    group=GROUP_GENERATION,
    sizes=[40, 60, 80],
    complexity="O(1) amortized per partition",
    requires=generation_module,
    note="the partitions of an integer, which grow subexponentially",
)
def integer_partitions(value: int) -> int:
    """Traverse every integer partition of a value."""
    return sum(1 for _ in generation_module.integer_partitions(value))


@benchmark(
    group=GROUP_GENERATION,
    sizes=[9, 10, 11],
    complexity="O(1) amortized per partition, Bell many partitions",
    setup=make_item_list,
    requires=generation_module,
)
def set_partitions(items: List[int]) -> int:
    """Traverse every partition of a set."""
    return sum(1 for _ in generation_module.set_partitions(items))


@benchmark(
    group=GROUP_GENERATION,
    sizes=[30, 60, 120],
    complexity="O(1) amortized per composition",
    requires=generation_module,
)
def compositions(value: int) -> int:
    """Take a prefix of the compositions of a value."""
    taken = 0
    for _ in generation_module.compositions(value):
        taken += 1
        if taken == 10_000:
            break
    return taken


@benchmark(
    group=GROUP_GENERATION,
    sizes=[8, 10, 12],
    complexity="O(1) amortized per necklace",
    requires=generation_module,
    note="counting up to rotation, which the Polya machinery counts directly",
)
def necklaces(length: int) -> int:
    """Traverse the binary necklaces of a length."""
    return sum(1 for _ in generation_module.necklaces([0, 1], length))


@benchmark(
    group=GROUP_GENERATION,
    sizes=[10, 14, 18],
    complexity="O(1) amortized per word",
    requires=generation_module,
)
def lyndon_words(length: int) -> int:
    """Traverse the binary Lyndon words of a length."""
    return sum(1 for _ in generation_module.lyndon_words([0, 1], length))


# ---------------------------------------------------------------------------
# Ranking and unranking
# ---------------------------------------------------------------------------


@benchmark(
    group=GROUP_RANKING,
    sizes=[100, 1_000, 5_000],
    complexity="O(n squared) transparent, O(n log n) tuned",
    setup=make_permutation,
    requires=generation_module,
    note=(
        "the implied exponent distinguishes the two implementations the "
        "reference describes"
    ),
)
def permutation_rank(permutation: Tuple[int, ...]) -> int:
    """Rank a permutation in lexicographic order."""
    return generation_module.permutation_rank(permutation)


@benchmark(
    group=GROUP_RANKING,
    sizes=[100, 1_000, 5_000],
    complexity="O(n squared) transparent, O(n log n) tuned",
    setup=make_rank_and_size,
    requires=requires_all(counting_module, generation_module),
    note=(
        "the rank is an integer with as many digits as the factorial, which "
        "is the case that needs unbounded arithmetic"
    ),
)
def permutation_unrank(payload: Tuple[int, int]) -> Tuple[int, ...]:
    """Recover the permutation at a rank in the middle of the space."""
    size, rank = payload
    return generation_module.permutation_unrank(size, rank)


@benchmark(
    group=GROUP_RANKING,
    sizes=[100, 1_000, 10_000],
    complexity="O(k) with cached binomials",
    setup=make_combination_rank,
    requires=requires_all(counting_module, generation_module),
)
def combination_unrank(payload: Tuple[int, int, int]) -> Tuple[int, ...]:
    """Recover the selection at a rank in the middle of the space."""
    size, chosen, rank = payload
    return generation_module.combination_unrank(size, chosen, rank)


@benchmark(
    group=GROUP_RANKING,
    sizes=[8, 9, 10],
    complexity="O(n) per object over n factorial objects",
    setup=make_item_list,
    requires=generation_module,
    note=(
        "the bijection checked in both directions over the whole space, "
        "which is what the test suite asserts"
    ),
)
def ranking_round_trip(items: List[int]) -> int:
    """Rank and unrank every permutation of a small list."""
    size = len(items)
    checked = 0
    for index, permutation in enumerate(generation_module.permutations(items)):
        if generation_module.permutation_rank(permutation) != index:
            raise AssertionError("ranking disagrees with the enumeration order")
        if generation_module.permutation_unrank(size, index) != permutation:
            raise AssertionError("unranking is not the inverse of ranking")
        checked += 1
    return checked


# ---------------------------------------------------------------------------
# Generating functions
# ---------------------------------------------------------------------------


@benchmark(
    group=GROUP_SERIES,
    sizes=[100, 500, 2_000],
    complexity="O(n)",
    setup=make_two_series,
    requires=series_module,
)
def series_add(payload: Tuple[Any, Any]) -> Any:
    """Add two formal power series."""
    left, right = payload
    return left + right


@benchmark(
    group=GROUP_SERIES,
    sizes=[100, 300, 900],
    complexity="O(n squared)",
    setup=make_two_series,
    requires=series_module,
    note="the operation an analytic combinatorics computation repeats",
)
def series_multiply(payload: Tuple[Any, Any]) -> Any:
    """Multiply two formal power series."""
    left, right = payload
    return left * right


@benchmark(
    group=GROUP_SERIES,
    sizes=[50, 100, 200],
    complexity="O(n squared) or worse",
    setup=make_two_series,
    requires=series_module,
)
def series_compose(payload: Tuple[Any, Any]) -> Any:
    """Substitute one series into another."""
    left, right = payload
    return series_module.compose(left, right)


@benchmark(
    group=GROUP_SERIES,
    sizes=[100, 500, 2_000],
    complexity="O(n squared)",
    setup=make_series,
    requires=series_module,
)
def series_invert(series: Any) -> Any:
    """Compute the multiplicative inverse of a series."""
    return series_module.invert(series)


@benchmark(
    group=GROUP_SERIES,
    sizes=[100, 1_000, 10_000],
    complexity="O(1) per coefficient once expanded",
    setup=make_series,
    requires=series_module,
)
def series_coefficients(series: Any) -> List[Any]:
    """Extract the first several coefficients of a series."""
    return series.coefficients(100)


# ---------------------------------------------------------------------------
# Polya enumeration
# ---------------------------------------------------------------------------


@benchmark(
    group=GROUP_POLYA,
    sizes=[8, 16, 32],
    complexity="O(group order) fixed point counts",
    setup=make_cyclic_group,
    requires=requires_all(groups_module, polya_module),
    note="counting necklaces up to rotation, which is Burnside's lemma",
)
def burnside_cyclic(group: Any) -> int:
    """Count the orbits of a cyclic group acting on colourings."""
    return polya_module.burnside(group, colours=3)


@benchmark(
    group=GROUP_POLYA,
    sizes=[4, 5, 6],
    complexity="O(group order), which is the factorial here",
    setup=make_symmetric_group,
    requires=requires_all(groups_module, polya_module),
    note="the group order grows factorially, which dominates the cost",
)
def burnside_symmetric(group: Any) -> int:
    """Count the orbits of a symmetric group acting on colourings."""
    return polya_module.burnside(group, colours=2)


@benchmark(
    group=GROUP_POLYA,
    sizes=[8, 16, 32],
    complexity="O(group order)",
    setup=make_cyclic_group,
    requires=requires_all(groups_module, polya_module),
)
def cycle_index(group: Any) -> Any:
    """Compute the cycle index polynomial of a permutation group."""
    return polya_module.cycle_index(group, degree=group.order())


# ---------------------------------------------------------------------------
# Designs and probability
# ---------------------------------------------------------------------------


@benchmark(
    group=GROUP_DESIGNS,
    sizes=[20, 50, 100],
    complexity="O(n squared) to verify the rows and columns",
    setup=make_latin_square,
    requires=designs_module,
)
def latin_square_validation(square: Any) -> bool:
    """Verify that a square is Latin."""
    return square.is_valid()


@benchmark(
    group=GROUP_DESIGNS,
    sizes=[10, 20, 40],
    complexity="O(n squared) per pair of squares",
    setup=make_latin_square,
    requires=designs_module,
)
def latin_square_orthogonality(square: Any) -> bool:
    """Test two Latin squares for orthogonality."""
    return designs_module.orthogonal(square, square)


@benchmark(
    group=GROUP_DESIGNS,
    sizes=[12, 16, 20],
    complexity="exponential in the ground set",
    setup=make_item_list,
    requires=designs_module,
    note="Sperner's theorem bounds the size of an antichain of subsets",
)
def sperner_family(items: List[int]) -> Any:
    """Build a maximal antichain of subsets."""
    return designs_module.sperner_family(items)


@benchmark(
    group=GROUP_PROBABILITY,
    sizes=[100, 1_000, 10_000],
    complexity="O(n) exact rational arithmetic",
    setup=make_distribution,
    requires=probability_module,
    note="exact fractions rather than floats, so a chain does not drift",
)
def expectation(distribution: Any) -> Any:
    """Compute the expected value of a distribution exactly."""
    return probability_module.expectation(distribution, value=lambda key: key)


@benchmark(
    group=GROUP_PROBABILITY,
    sizes=[100, 1_000, 10_000],
    complexity="O(n) exact rational arithmetic",
    setup=make_distribution,
    requires=probability_module,
)
def variance(distribution: Any) -> Any:
    """Compute the variance of a distribution exactly."""
    return probability_module.variance(distribution, value=lambda key: key)


@benchmark(
    group=GROUP_PROBABILITY,
    sizes=[20, 40, 52],
    complexity="O(min(k, n - k)) through the coefficients",
    requires=requires_all(counting_module, probability_module),
    note="the classical counting probability, exact as a fraction",
)
def counting_probability(size: int) -> Any:
    """Compute the probability of a five member selection."""
    favourable = counting_module.binomial(size // 2, 5)
    total = counting_module.binomial(size, 5)
    return probability_module.counting_probability(favourable, total)


# ---------------------------------------------------------------------------
# Notes on reading these results
# ---------------------------------------------------------------------------
#
# The comparisons worth looking at:
#
#   permutations_full against permutations_prefix. This is the central
#   measurement of the file. The first grows factorially and the second must
#   be flat in the size, because taking ten objects from a space of a
#   thousand factorial members is the same work as taking ten from a space
#   of ten factorial. A permutations_prefix that grows with the size means
#   the generator materializes before it yields, which would break the
#   promise the reference makes.
#
#   permutation_unrank against permutations_prefix at a large size. Both
#   address a space without traversing it, and unranking reaches a specific
#   object rather than the first one, which is what a distributed
#   enumeration and an exact uniform sample need.
#
#   catalan against catalan_warm. The ratio is what the memoization is
#   worth. A warm call should be a hundred lookups rather than a hundred
#   computations, so the second benchmark should not be a hundred times the
#   first.
#
#   binomial_middle against binomial_edge. The routine iterates the smaller
#   tail, so a coefficient with a small second argument should be far
#   cheaper at the same first argument. If the two are equal, the routine is
#   building factorials it does not need.
#
#   factorial growth. The implied exponent should exceed one, because the
#   argument count is linear while the integers being multiplied grow. A
#   routine that looked exactly linear here would be suspicious.
#
#   partition_number growth. The pentagonal recurrence gives roughly n to
#   the power one and a half, which the implied exponent should show. A
#   value near two means the implementation fell back to the quadratic
#   recurrence.
#
#   series_add against series_multiply. Linear against quadratic, on the
#   same input family, which is the pair that makes the cost of an analytic
#   combinatorics computation predictable.
#
#   burnside_cyclic against burnside_symmetric. Both are proportional to the
#   group order, and the symmetric group's order is the factorial, which is
#   why its sizes are so much smaller. The cost is the group rather than the
#   colouring.
