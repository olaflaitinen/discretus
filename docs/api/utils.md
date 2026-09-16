# `discretus.utils`

The utility package holds the cross cutting helpers that the domain packages
share but that are not themselves mathematical abstractions: timing,
memoization, bit manipulation, formatting, validation, iteration, comparison,
seeded randomness, a prime cache, progress reporting, and optional parallel
mapping.

The division of labour between this package and
[`discretus.core`](core.md) is worth stating, because both are shared
layers. The core layer holds the abstractions that model mathematics: what
an element is, what a relation is, what an exact matrix is. This package
holds the engineering helpers that any library of this kind would need
whether or not it computed mathematics.

Everything here is public and documented, because these helpers are useful
in a caller's own code and because pretending they are private would not
stop anyone from importing them.

## Module map

| Module | Responsibility |
| --- | --- |
| `timing` | Measuring elapsed time, for benchmarks and reports |
| `memoize` | Caching, with inspectable and clearable caches |
| `bit_tricks` | Bit level operations used by the set and subset machinery |
| `iterables` | Iteration helpers beyond those in the core layer |
| `comparison` | Approximate and exact comparison helpers |
| `formatting` | Number, table, and duration formatting |
| `hashing` | Convenience wrappers over the core hashing primitives |
| `math_utils` | Small numeric helpers that are not number theory |
| `primes_cache` | A shared, growable sieve |
| `progress` | Progress reporting for long enumerations |
| `random_utils` | Seeded random helpers above the core generator |
| `validation` | Higher level validators built on the core ones |
| `decorators` | Deprecation, complexity annotation, argument coercion |
| `parallel` | Optional parallel mapping over independent work |

## Timing

| Routine | Meaning |
| --- | --- |
| `Timer()` | A context manager measuring a block |
| `timed(function)` | A decorator recording each call's duration |
| `measure(function, *args, repeats=1)` | Time a call, returning the result and the timings |
| `format_duration(seconds)` | A human readable duration |

```python
from discretus.utils.timing import Timer, measure
from discretus.number_theory.factorization import factorize

with Timer() as timer:
    factorize(600_851_475_143)
print(timer.elapsed, timer.human)

result, timings = measure(factorize, 600_851_475_143, repeats=5)
print(result, min(timings), max(timings))
```

`measure` reports every repetition rather than an average, because the
minimum is the informative statistic for a deterministic computation and an
average hides the effect of a warm cache. The timers use the monotonic
performance counter, so a clock adjustment cannot produce a negative
duration.

## Memoization

| Routine | Meaning |
| --- | --- |
| `memoize(function)` | Unbounded cache on the arguments |
| `memoize_with_limit(size)` | A bounded cache, least recently used |
| `memoize_method(method)` | Per instance caching for a method |
| `clear_caches()` | Clear every cache this module created |
| `cache_statistics()` | Hits, misses, and size per cached function |

The caches are inspectable and clearable, which is what distinguishes them
from a bare dictionary inside a closure. A test can assert that a second
call was a hit, a benchmark can clear the caches between runs so that a
measurement is not contaminated, and a long running process can reclaim the
memory.

```python
from discretus.utils.memoize import cache_statistics, clear_caches, memoize


@memoize
def slow(n: int) -> int:
    return sum(range(n))


slow(10_000)
slow(10_000)
print(cache_statistics()["slow"])
clear_caches()
```

The sequences in [`discretus.combinatorics`](combinatorics.md) and
[`discretus.recurrences`](recurrences.md) are memoized through this module,
which is why computing the hundredth Catalan number after the ninety ninth
is free and why clearing the caches restores the cold cost.

## Bit tricks

| Routine | Meaning |
| --- | --- |
| `popcount(value)` | The number of one bits |
| `lowest_set_bit(value)`, `highest_set_bit(value)` | Bit positions |
| `set_bit`, `clear_bit`, `toggle_bit`, `test_bit` | Single bit edits |
| `iterate_bits(value)` | The positions of the one bits |
| `subsets_of_mask(mask)` | Every submask, in decreasing order |
| `gray_code(value)`, `inverse_gray_code(value)` | The Gray code bijection |
| `next_permutation_mask(mask)` | The next mask with the same popcount |
| `bit_reverse(value, width)` | Reversal within a fixed width |

These are the operations that make the bit set representation and the subset
enumerators fast. Two of them are worth knowing even outside the library.
`subsets_of_mask` enumerates every submask of a mask in a single loop, which
turns a subset sum over subsets into a linear pass; and
`next_permutation_mask` steps through the masks of a fixed popcount in
increasing order, which is how combinations are enumerated without
generating and filtering.

```python
from discretus.utils.bit_tricks import popcount, subsets_of_mask

assert popcount(0b1011) == 3
assert list(subsets_of_mask(0b101)) == [0b101, 0b100, 0b001, 0b000]
```

## Iteration and comparison

`iterables` adds the helpers that the core layer does not: `flatten`,
`partition_by`, `group_by`, `split_at`, `rotate`, `all_equal`,
`duplicates`, `roundrobin`, and `consume`. They complement rather than
duplicate `discretus.core.iterators`, which holds the ones the generators
depend on.

`comparison` holds the helpers for the few places where an exact comparison
is impossible: `approximately_equal`, `relative_error`, `is_close_to_zero`,
and `compare_with_tolerance`. Each takes a tolerance that defaults to the
configured one, and each documents that it is for floating point values
only. An exact routine never calls them, which is the invariant that keeps
the library's exactness claim true.

## Formatting

| Routine | Meaning |
| --- | --- |
| `format_number(value, digits=None)` | An integer or fraction, grouped for reading |
| `format_big_integer(value, head=20, tail=20)` | A large integer, abbreviated in the middle |
| `format_table(rows, header=None)` | A padded text table |
| `format_duration(seconds)` | A duration in readable units |
| `format_percentage(part, whole)` | A percentage, exactly computed |
| `truncate_text(text, width)` | Text with an ellipsis marker |

`format_big_integer` deserves a mention because this library produces
numbers that no one wants printed in full. The hundred thousandth Fibonacci
number has over twenty thousand digits, and abbreviating the middle while
keeping both ends is what makes it reportable.

```python
from discretus.recurrences.sequences import fibonacci
from discretus.utils.formatting import format_big_integer

print(format_big_integer(fibonacci(100_000)))
```

## The prime cache

| Routine | Meaning |
| --- | --- |
| `primes_below(limit)` | Every prime below a limit, from the shared sieve |
| `is_prime_cached(n)` | Membership, for values within the sieve |
| `nth_prime(index)` | The prime at an index, extending the sieve if needed |
| `extend_to(limit)` | Grow the sieve deliberately |
| `cache_limit()` | The current extent of the sieve |
| `clear_prime_cache()` | Reclaim the memory |

The cache grows when asked and never shrinks on its own, which is the right
policy for a process that factors many numbers and the wrong one for a long
lived service, so the explicit clear exists. The number theory package uses
it for trial division, which is why factoring a thousand numbers is much
faster than factoring one a thousand times over.

## Progress reporting

| Routine | Meaning |
| --- | --- |
| `progress(iterable, total=None, label=None)` | Wrap an iterable with reporting |
| `ProgressReporter(total, label)` | The reporter, for manual updates |
| `silent()` | A context manager disabling reporting |

Reporting is off unless a caller asks for it, and it writes to standard
error rather than standard output, so a program whose output is piped is
unaffected. It has no dependency: the implementation is a carriage return
and a rate estimate, which is enough for a long enumeration and avoids
adding a package for a progress bar.

```python
from discretus.combinatorics.generation import set_partitions
from discretus.utils.progress import progress
from discretus.combinatorics.sequences import bell

count = sum(1 for _ in progress(set_partitions(range(9)), total=bell(9)))
```

## Seeded randomness

`random_utils` sits above `discretus.core.random_base` and adds the
operations the generators and the benchmarks need: `random_subset`,
`random_partition`, `random_permutation`, `weighted_choice`,
`random_integers`, and `reproducible_seed`. Everything takes a seed and is
deterministic once given one.

`reproducible_seed(label)` derives a seed from a string through the
deterministic hash in the core layer, which is a small but genuinely useful
trick: a test or a benchmark can seed itself from its own name, so every
case has a distinct reproducible seed and nobody has to maintain a table of
magic numbers.

```python
from discretus.utils.random_utils import random_subset, reproducible_seed

seed = reproducible_seed("test_kruskal_matches_prim")
print(random_subset(range(10), seed=seed))
```

## Validation

`validation` builds on `discretus.validation` and adds the composite
validators the domains need: `validate_matrix`, `validate_square_matrix`,
`validate_graph_input`, `validate_probability_vector`,
`validate_partition`, and `validate_permutation`. Each raises the same
exception types as the core validators, so a caller catches one hierarchy.

```python
from discretus.utils.validation import validate_permutation

validate_permutation((2, 0, 1))            # accepted
validate_permutation((2, 0, 2))            # raises ValidationError
```

## Decorators

| Decorator | Meaning |
| --- | --- |
| `deprecated(replacement, removal)` | Emit a deprecation warning naming both |
| `complexity(expression)` | Record the complexity, for the reference and the benchmarks |
| `coerce_arguments(**converters)` | Convert arguments at the boundary |
| `validate_arguments(**validators)` | Check arguments at the boundary |
| `experimental(since)` | Mark an interface as not yet covered by the guarantee |

The deprecation decorator implements the policy in the contributing guide: a
name that is going away keeps working, warns, and names both its replacement
and the release in which it will be removed. The test configuration turns
deprecation warnings into errors, so the library's own suite cannot quietly
depend on something it has deprecated.

```python
from discretus.utils.decorators import deprecated


@deprecated(replacement="new_name", removal="1.2.0")
def old_name(value: int) -> int:
    return new_name(value)
```

## Parallel mapping

| Routine | Meaning |
| --- | --- |
| `parallel_map(function, items, workers=None, chunk=None)` | Map over independent work |
| `is_available()` | Whether the platform supports the process pool |
| `sequential_map(function, items)` | The same interface, one process |

Parallelism is opt in and is suitable for a narrow case: many independent
calls whose arguments and results are cheap to move between processes, for
instance factoring a list of integers or running a solver on a family of
instances. It is not suitable for a single large graph algorithm, because
moving the graph costs more than the computation saves.

The interface is identical to the sequential one, so a program can switch
between them with a single name, and `sequential_map` exists precisely so
that a test can run the same code deterministically in one process.

```python
from discretus.number_theory.factorization import factorize
from discretus.utils.parallel import parallel_map

numbers = [600_851_475_143, 999_999_000_001, 123_456_789_017]
print(parallel_map(factorize, numbers, workers=3))
```

Results are returned in the order of the input regardless of completion
order, which is what keeps a parallel run reproducible.

## How these helpers read the configuration

Several helpers consult `discretus.config`, which means their behaviour can
be set once for a process rather than at every call site. Knowing which ones
do is useful, because it explains behaviour that would otherwise look like
inconsistency.

| Helper | Setting it reads | Effect |
| --- | --- | --- |
| `comparison.approximately_equal` | `tolerance` | The default tolerance |
| `random_utils`, `random_base` | `default_seed` | The seed when none is given |
| `progress.progress` | `explain` | Whether reporting is enabled by default |
| `validation.*` | `strict_validation` | Whether expensive checks run |
| `primes_cache.primes_below` | `max_enumeration` | The largest sieve permitted |
| `formatting.format_big_integer` | None | Always explicit |

The pattern is that a helper reads a setting only for its default, and an
explicit argument always wins. That keeps a library call predictable: a
caller who passes a seed gets that seed regardless of the configuration, and
a caller who passes nothing gets the configured behaviour.

```python
from discretus.config import config_scope
from discretus.utils.random_utils import random_subset

# The configured seed applies.
with config_scope(default_seed=7):
    first = random_subset(range(10))
    second = random_subset(range(10))
assert first == second

# An explicit seed overrides it.
with config_scope(default_seed=7):
    explicit = random_subset(range(10), seed=99)
assert explicit != first
```

## Core or utils

Both packages are shared layers, and a contributor adding a helper has to
decide which one it belongs in. The test is what the helper is about.

If it models mathematics, it belongs in `discretus.core`. An element, a
relation, an exact matrix, a binary operation, a group axiom, a modular
residue: these are the subject matter, and the domain packages build
directly on them.

If it is engineering, it belongs here. A timer, a cache, a progress
reporter, a formatter, a deprecation decorator: any library of this size
would need them whether or not it computed mathematics, and none of them
would appear in a textbook.

Two pairs look like duplication and are not.

`core.iterators` and `utils.iterables` both hold iteration helpers. The core
module holds the ones the combinatorial generators depend on, which is why
it lives in the layer those generators can import; the utility module holds
the general purpose remainder. The split follows the dependency rule rather
than a taxonomy of iteration.

`core.hashing` and `utils.hashing` both hash. The core module defines the
canonical encoding and the deterministic digest, which structures use for
their fingerprints; the utility module wraps them for convenience in a
caller's own code and adds nothing mathematical.

The same reasoning explains why `core.random_base` defines the seeded
generator while `random_utils` builds the higher level draws on top of it,
and why `discretus.validation` holds the primitive precondition checks while
`utils.validation` composes them into validators for matrices, graphs, and
permutations.

## Using these helpers in your own code

Nothing in this package is private, and three of the modules are worth
importing into a caller's own work.

The timing helpers are a small, dependency free alternative to writing
`time.perf_counter` by hand, and `format_duration` produces the units a
reader wants without a second thought about whether a number is in seconds
or milliseconds.

`reproducible_seed` solves a real problem in test suites: giving every case
a distinct, stable seed without maintaining a table of numbers. Deriving the
seed from the test's name means a new case cannot collide with an old one
and a renamed case gets a fresh seed, which is usually what is wanted.

`memoize` with its statistics and its clear is more useful during
development than the standard library cache, because the questions during
development are whether the cache is being hit and how large it has grown,
and both are one call away.

```python
from discretus.utils.memoize import cache_statistics, memoize
from discretus.utils.timing import Timer
from discretus.utils.random_utils import reproducible_seed


@memoize
def expensive(n: int) -> int:
    return sum(i * i for i in range(n))


with Timer() as first:
    expensive(200_000)
with Timer() as second:
    expensive(200_000)

print(first.human, second.human)
print(cache_statistics()["expensive"])
print(reproducible_seed("my own experiment"))
```

## Worked example: benchmarking two implementations

The utility package exists mostly to serve the library, and the one place a
caller uses several of its modules together is when comparing two
implementations. The following compares the two greatest common divisor
routines, which is the smallest honest benchmark in the library, and it
illustrates the timing, memoization, randomness, and formatting helpers at
once.

```python
from discretus.number_theory.gcd import binary_gcd, gcd
from discretus.utils.formatting import format_duration, format_table
from discretus.utils.memoize import clear_caches
from discretus.utils.random_utils import random_integers, reproducible_seed
from discretus.utils.timing import measure

seed = reproducible_seed("gcd benchmark")
pairs = list(zip(random_integers(200, 1, 10 ** 12, seed=seed),
                 random_integers(200, 1, 10 ** 12, seed=seed + 1)))

rows = []
for name, routine in (("euclidean", gcd), ("binary", binary_gcd)):
    clear_caches()

    def run() -> int:
        return sum(routine(a, b) for a, b in pairs)

    total, timings = measure(run, repeats=5)
    rows.append([name, total, format_duration(min(timings))])

print(format_table(rows, header=["routine", "checksum", "best of five"]))
```

Four practices in that program are worth copying into any benchmark.

The seed comes from the benchmark's own name, so the inputs are fixed
without a magic number and two benchmarks never accidentally share them.

The caches are cleared before each candidate, because a warm cache would
make whichever routine ran second look faster, which is the most common way
a benchmark lies.

The result is checksummed and compared across candidates. Two
implementations of the same function must agree, and a benchmark that does
not check this can happily report that the wrong implementation is faster.
Adding `assert rows[0][1] == rows[1][1]` makes that explicit.

The minimum of several repetitions is reported rather than the mean. For a
deterministic computation the variation is noise from the machine, and the
minimum is the closest estimate of the true cost.

The comparison this program performs, incidentally, is the one the
documentation of `binary_gcd` describes: the binary algorithm replaces
division with shifting, which was an advantage on hardware without a
divider and is not an advantage in Python, where the division is implemented
in C and the shifting is not. Running it is more convincing than the
sentence.

## Errors

| Exception | Raised when |
| --- | --- |
| `ValidationError` | A validator's precondition fails |
| `DomainError` | A value is outside a valid range |
| `LimitExceededError` | A cache or enumeration bound is exceeded |
| `OptionalDependencyError` | A helper needing an optional package is used |

## Design notes

**Caches are inspectable.** A cache that cannot be examined or cleared is
untestable and unbounded in the worst way. Every cache in this package
reports its statistics and can be cleared.

**Nothing here is magic.** The decorators do one thing each and say so, the
timing helpers use the monotonic clock, and the progress reporter is a
carriage return. A utility package is where unexplained cleverness
accumulates, and the antidote is that every helper is small enough to read.

**Approximate comparison is quarantined.** The tolerance based helpers exist
in one module, they document that they are for floating point only, and no
exact routine calls them. That is how the exactness claim in the
documentation stays true.

**Parallelism is opt in and honest about its scope.** It helps for many
independent calls and hurts for one large structure, and the documentation
says which is which rather than presenting it as a general speedup.

## What is deliberately absent

A utility package tends to accumulate, so it is worth recording what was
considered and left out, and why.

There is no logging helper here. Logging is configured in
`discretus.logging_utils`, which attaches a null handler to the library
logger and offers one opt in configurator. Splitting it across two modules
would leave nobody sure which to call.

There is no configuration helper here. Configuration lives in
`discretus.config`, as a single immutable snapshot with a process wide setter
and a scoped context manager, and that is the whole interface.

There is no retry, no rate limiter, and no circuit breaker. The library
performs no input and output beyond reading and writing files on request,
and it makes no network calls, so the failures those helpers exist for
cannot occur.

There is no serialization helper here either. The dictionary and JSON
protocol lives in `discretus.core.serializable` and the formats live in
`discretus.io`, which is where a reader looks for them.

There is no plotting helper. Rendering is `discretus.viz`, behind its
registry and its optional dependencies.

## See also

- [`discretus.core`](core.md), for the mathematical abstractions and the
  primitives these helpers wrap.
- [`discretus.config`](../quickstart.md#configuration), for the settings
  several of these helpers consult.
- The contributing guide, for the deprecation policy the decorators
  implement.
